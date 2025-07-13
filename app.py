#!/usr/bin/env python3
"""
Flask web application for PubMed Paper Finder.
By Manideep Reddy Eevuri
"""

from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import os
import sys
import json
import traceback
from datetime import datetime
import threading
import time

# Add the get-papers-list directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'get-papers-list'))

from paper_finder.fetch import PubMedFetcher
from paper_finder.parser import PubMedParser
from paper_finder.filter import AffiliationFilter
from paper_finder.output import CSVExporter
from llm_service import GroqLLMService

app = Flask(__name__)
CORS(app)

# Initialize LLM service with Groq API
GROQ_API_KEY = os.getenv('GROQ_API_KEY', 'your-groq-api-key-here')
llm_service = GroqLLMService(api_key=GROQ_API_KEY)

# Global variable to store search results
search_results = {}

def enhance_search_query(original_query):
    """
    Enhance the search query to be more focused on industry collaborations.
    """
    # Industry-focused terms to add
    industry_terms = [
        "industry collaboration",
        "pharmaceutical company",
        "biotech",
        "clinical trial",
        "drug development",
        "corporate research",
        "commercial research"
    ]

    # Check if query already contains industry terms
    query_lower = original_query.lower()
    has_industry_terms = any(term in query_lower for term in [
        'pharma', 'biotech', 'company', 'corp', 'inc', 'ltd',
        'clinical trial', 'drug', 'therapeutic', 'industry'
    ])

    # If no industry terms, enhance the query
    if not has_industry_terms:
        # Add industry collaboration terms
        enhanced = f"({original_query}) AND (industry[Affiliation] OR pharmaceutical[Affiliation] OR biotech[Affiliation] OR company[Affiliation] OR corp[Affiliation] OR clinical trial OR drug development)"
        return enhanced
    else:
        # Query already has industry focus, just return original
        return original_query

def get_optimal_search_limit(query):
    """Determine optimal search limit based on query specificity for faster results."""
    query_lower = query.lower()

    # If query contains specific company names, search more papers
    company_names = ['pfizer', 'roche', 'novartis', 'gsk', 'merck', 'iqvia', 'covance', 'moderna', 'biontech']
    if any(company in query_lower for company in company_names):
        return 150  # More papers for specific company searches

    # If query is very specific, search fewer papers for faster results
    specific_terms = ['clinical trial', 'drug development', 'pharmaceutical', 'biotech']
    if any(term in query_lower for term in specific_terms):
        return 100

    # Default for general searches - optimized for speed
    return 75

@app.route('/')
def index():
    """Main page of the web application."""
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search_papers():
    """API endpoint to search for papers."""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        email = data.get('email', '').strip() or None
        debug = data.get('debug', False)
        page = int(data.get('page', 1))
        page_size = int(data.get('page_size', 15))
        search_limit = data.get('search_limit', 'fast')  # fast, balanced, comprehensive
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        # Generate unique search ID
        search_id = f"search_{int(time.time())}"
        
        # Initialize search results
        search_results[search_id] = {
            'status': 'running',
            'progress': 'Starting search...',
            'results': None,
            'error': None
        }
        
        # Start search in background thread
        thread = threading.Thread(
            target=perform_search,
            args=(search_id, query, email, debug, page, page_size, search_limit)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({'search_id': search_id})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def perform_search(search_id, query, email, debug, page=1, page_size=15, search_limit='fast'):
    """Perform the actual search in a background thread."""
    try:
        print(f"DEBUG: Starting search for query: {query}")

        # Initialize components
        fetcher = PubMedFetcher(email=email)
        parser = PubMedParser()
        filter_obj = AffiliationFilter(debug=True)  # Always enable debug for web app
        exporter = CSVExporter(debug=True)

        # Step 1: Search PubMed
        search_results[search_id]['progress'] = 'Searching PubMed...'

        # Enhance query to be more industry-focused
        enhanced_query = enhance_search_query(query)
        print(f"DEBUG: Original query: {query}")
        print(f"DEBUG: Enhanced query: {enhanced_query}")
        # Get search limit based on user preference and query
        if search_limit == 'comprehensive':
            max_results = 250
        elif search_limit == 'balanced':
            max_results = get_optimal_search_limit(query)
        else:  # fast
            max_results = min(75, get_optimal_search_limit(query))

        print(f"DEBUG: Searching PubMed with enhanced query (limit: {max_results}, mode: {search_limit})")
        # Search with user-selected performance mode
        pubmed_ids = fetcher.search_papers(enhanced_query, max_results=max_results)
        print(f"DEBUG: Found {len(pubmed_ids)} PubMed IDs: {pubmed_ids[:5]}")

        if not pubmed_ids:
            print("DEBUG: No PubMed IDs found")
            search_results[search_id] = {
                'status': 'completed',
                'progress': 'No papers found',
                'results': {
                    'papers': [],
                    'summary': {
                        'total_papers': 0,
                        'papers_with_industry': 0,
                        'total_industry_authors': 0
                    }
                },
                'error': None
            }
            return
        
        # Step 2: Fetch paper details
        search_results[search_id]['progress'] = f'Found {len(pubmed_ids)} papers. Fetching details...'
        print(f"DEBUG: Fetching details for {len(pubmed_ids)} papers")

        # Use smaller batch size for faster initial response
        xml_responses = fetcher.fetch_papers_batch(pubmed_ids, batch_size=50)
        print(f"DEBUG: Got {len(xml_responses)} XML responses")

        # Step 3: Parse papers
        search_results[search_id]['progress'] = 'Parsing paper data...'
        all_papers = []
        for i, xml_response in enumerate(xml_responses):
            search_results[search_id]['progress'] = f'Parsing papers... ({i+1}/{len(xml_responses)} batches)'
            print(f"DEBUG: Parsing XML response {i+1}/{len(xml_responses)}")
            papers = parser.parse_papers(xml_response)
            print(f"DEBUG: Parsed {len(papers)} papers from response {i+1}")
            all_papers.extend(papers)

        print(f"DEBUG: Total papers parsed: {len(all_papers)}")

        # Step 4: Filter for industry authors
        search_results[search_id]['progress'] = 'Filtering for industry authors...'
        print(f"DEBUG: Filtering {len(all_papers)} papers for industry authors")

        # Process all papers and identify which have industry authors
        papers_with_industry = []
        all_papers_data = []

        for i, paper in enumerate(all_papers):
            if i % 10 == 0:  # Update progress every 10 papers
                search_results[search_id]['progress'] = f'Analyzing authors... ({i+1}/{len(all_papers)} papers)'
            print(f"DEBUG: Analyzing paper {i+1}/{len(all_papers)}: {paper.pubmed_id}")
            industry_authors = filter_obj.identify_industry_authors(paper.authors)

            if industry_authors:
                papers_with_industry.append(paper)
                print(f"DEBUG: ✅ Paper {paper.pubmed_id} has {len(industry_authors)} industry authors")
            else:
                print(f"DEBUG: ❌ Paper {paper.pubmed_id} has NO industry authors")
                # Let's see why - check first few authors
                for j, author in enumerate(paper.authors[:3]):  # Check first 3 authors
                    is_industry = filter_obj.is_industry_affiliation(author)
                    print(f"DEBUG:   Author {j+1}: {author.first_name} {author.last_name} - Industry: {is_industry}")
                    if author.affiliation:
                        print(f"DEBUG:     Affiliation: {author.affiliation[:100]}...")
                    if author.email:
                        print(f"DEBUG:     Email: {author.email}")

        print(f"DEBUG: Found {len(papers_with_industry)} papers with industry authors out of {len(all_papers)} total")
        
        # Step 5: Prepare results
        search_results[search_id]['progress'] = 'Preparing results...'
        print(f"DEBUG: Preparing results for {len(all_papers)} papers")

        # Convert ALL papers to JSON-serializable format
        results_data = []
        total_industry_authors = 0

        for i, paper in enumerate(all_papers):
            print(f"DEBUG: Processing paper {i+1}: {paper.pubmed_id}")
            industry_authors = filter_obj.identify_industry_authors(paper.authors)
            companies = filter_obj.get_company_affiliations(industry_authors)
            has_industry = len(industry_authors) > 0
            total_industry_authors += len(industry_authors)
            print(f"DEBUG: Paper {paper.pubmed_id} has {len(industry_authors)} industry authors")

            # Generate LLM insights for papers with industry authors
            llm_insights = None
            if has_industry and i < 10:  # Limit LLM analysis to first 10 industry papers for speed
                try:
                    print(f"DEBUG: Generating LLM insights for paper {paper.pubmed_id}")
                    author_names = [f"{author.last_name}, {author.first_name or author.initials}"
                                  for author in paper.authors[:5]]  # First 5 authors
                    llm_insights = llm_service.summarize_paper(
                        title=paper.title,
                        abstract=getattr(paper, 'abstract', None),
                        authors=author_names
                    )
                except Exception as e:
                    print(f"DEBUG: LLM analysis failed for paper {paper.pubmed_id}: {e}")
                    llm_insights = None

            paper_data = {
                'pubmed_id': paper.pubmed_id,
                'title': paper.title,
                'publication_date': paper.publication_date,
                'journal': paper.journal,
                'has_industry_authors': has_industry,
                'industry_authors': [
                    {
                        'name': f"{author.last_name}, {author.first_name or author.initials}",
                        'affiliation': author.affiliation,
                        'email': author.email
                    }
                    for author in industry_authors
                ],
                'companies': companies,
                'corresponding_email': paper.corresponding_author_email,
                'total_authors': len(paper.authors),
                'industry_authors_count': len(industry_authors),
                'llm_insights': llm_insights  # Add LLM insights
            }
            results_data.append(paper_data)

        # Apply pagination to results
        total_results = len(results_data)
        total_pages = max(1, (total_results + page_size - 1) // page_size)  # Ceiling division
        start_index = (page - 1) * page_size
        end_index = min(start_index + page_size, total_results)
        paginated_results = results_data[start_index:end_index]

        print(f"DEBUG: Pagination - Page {page} of {total_pages}, showing {len(paginated_results)} papers")

        # Create summary with pagination info
        summary = {
            'total_papers': len(all_papers),
            'papers_with_industry': len(papers_with_industry),
            'total_industry_authors': total_industry_authors,
            'total_results': total_results,
            'current_page': page,
            'page_size': page_size,
            'total_pages': total_pages,
            'start_index': start_index + 1,  # 1-based for display
            'end_index': end_index,
            'has_previous': page > 1,
            'has_next': page < total_pages,
            'query': query,
            'enhanced_query': enhanced_query,
            'timestamp': datetime.now().isoformat()
        }
        
        # Store final results with pagination
        search_results[search_id] = {
            'status': 'completed',
            'progress': 'Search completed successfully!',
            'results': {
                'papers': paginated_results,
                'all_papers': results_data,  # Store all papers for pagination
                'summary': summary
            },
            'error': None
        }
        
    except Exception as e:
        search_results[search_id] = {
            'status': 'error',
            'progress': 'Search failed',
            'results': None,
            'error': str(e)
        }

@app.route('/status/<search_id>')
def get_search_status(search_id):
    """Get the status of a search."""
    if search_id not in search_results:
        return jsonify({'error': 'Search not found'}), 404
    
    return jsonify(search_results[search_id])

@app.route('/paginate/<search_id>', methods=['POST'])
def paginate_results(search_id):
    """Get a specific page of results without re-searching."""
    try:
        if search_id not in search_results:
            return jsonify({'error': 'Search not found'}), 404

        result = search_results[search_id]
        if result['status'] != 'completed' or not result['results']:
            return jsonify({'error': 'No results available'}), 404

        data = request.get_json()
        page = int(data.get('page', 1))
        page_size = int(data.get('page_size', 15))

        # Get all papers from stored results
        all_papers = result['results']['all_papers']

        # Apply pagination
        total_results = len(all_papers)
        total_pages = max(1, (total_results + page_size - 1) // page_size)
        start_index = (page - 1) * page_size
        end_index = min(start_index + page_size, total_results)
        paginated_results = all_papers[start_index:end_index]

        # Update summary with new pagination info
        summary = result['results']['summary'].copy()
        summary.update({
            'current_page': page,
            'page_size': page_size,
            'total_pages': total_pages,
            'start_index': start_index + 1,
            'end_index': end_index,
            'has_previous': page > 1,
            'has_next': page < total_pages,
        })

        return jsonify({
            'papers': paginated_results,
            'summary': summary
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<search_id>')
def download_results(search_id):
    """Download search results as CSV."""
    try:
        if search_id not in search_results:
            return jsonify({'error': 'Search not found'}), 404
        
        result = search_results[search_id]
        if result['status'] != 'completed' or not result['results']:
            return jsonify({'error': 'No results available'}), 400
        
        # Create CSV file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"pubmed_results_{timestamp}.csv"
        filepath = os.path.join(os.getcwd(), filename)
        
        # Convert results to CSV format (all papers, not just current page)
        csv_data = []
        all_papers = result['results'].get('all_papers', result['results']['papers'])
        for paper_data in all_papers:
            # Include all papers with industry status indicator
            row = {
                'PubmedID': paper_data['pubmed_id'],
                'Title': paper_data['title'],
                'Publication Date': paper_data['publication_date'],
                'Journal': paper_data['journal'],
                'Has Industry Authors': 'Yes' if paper_data['has_industry_authors'] else 'No',
                'Industry Authors': '; '.join([author['name'] for author in paper_data['industry_authors']]),
                'Companies': '; '.join(paper_data['companies']),
                'Corresponding Author Email': paper_data['corresponding_email'] or '',
                'Total Authors': paper_data['total_authors'],
                'Industry Authors Count': paper_data['industry_authors_count']
            }
            csv_data.append(row)
        
        # Create DataFrame and save
        import pandas as pd
        df = pd.DataFrame(csv_data)
        df.to_csv(filepath, index=False, encoding='utf-8')
        
        return send_file(filepath, as_attachment=True, download_name=filename)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/analyze-trends/<search_id>')
def analyze_trends(search_id):
    """Generate research trend analysis using LLM."""
    try:
        if search_id not in search_results:
            return jsonify({'error': 'Search not found'}), 404

        result = search_results[search_id]
        if result['status'] != 'completed' or not result['results']:
            return jsonify({'error': 'No results available'}), 404

        # Get all papers for trend analysis
        all_papers = result['results'].get('all_papers', result['results']['papers'])

        # Generate trend analysis
        trends = llm_service.analyze_research_trends(all_papers)

        return jsonify({
            'trends': trends,
            'analyzed_papers': len(all_papers),
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/enhance-query', methods=['POST'])
def enhance_query():
    """Enhance search query using LLM."""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()

        if not query:
            return jsonify({'error': 'Query is required'}), 400

        # Get enhanced query suggestions
        enhanced = llm_service.enhance_search_query(query)

        return jsonify({
            'original_query': query,
            'enhanced': enhanced,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/paper-insights/<search_id>/<pubmed_id>')
def get_paper_insights(search_id, pubmed_id):
    """Get detailed LLM insights for a specific paper."""
    try:
        if search_id not in search_results:
            return jsonify({'error': 'Search not found'}), 404

        result = search_results[search_id]
        if result['status'] != 'completed' or not result['results']:
            return jsonify({'error': 'No results available'}), 404

        # Find the specific paper
        all_papers = result['results'].get('all_papers', result['results']['papers'])
        paper_data = None
        for paper in all_papers:
            if paper['pubmed_id'] == pubmed_id:
                paper_data = paper
                break

        if not paper_data:
            return jsonify({'error': 'Paper not found'}), 404

        # Generate detailed insights
        insights = llm_service.generate_research_insights(paper_data)

        return jsonify({
            'paper_id': pubmed_id,
            'insights': insights,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    print("🚀 Starting PubMed Paper Finder Web Application...")
    print("📱 Open your browser and go to: http://localhost:5000")
    print("🛑 Press Ctrl+C to stop the server")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
