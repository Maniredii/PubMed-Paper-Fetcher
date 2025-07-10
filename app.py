#!/usr/bin/env python3
"""
Flask web application for PubMed Paper Finder.
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

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from paper_finder.fetch import PubMedFetcher
from paper_finder.parser import PubMedParser
from paper_finder.filter import AffiliationFilter
from paper_finder.output import CSVExporter

app = Flask(__name__)
CORS(app)

# Global variable to store search results
search_results = {}

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
        max_results = int(data.get('max_results', 15))
        email = data.get('email', '').strip() or None
        debug = data.get('debug', False)
        
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
            args=(search_id, query, max_results, email, debug)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({'search_id': search_id})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def perform_search(search_id, query, max_results, email, debug):
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
        print(f"DEBUG: Searching PubMed with query: {query}, max_results: {max_results}")
        pubmed_ids = fetcher.search_papers(query, max_results)
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
        xml_responses = fetcher.fetch_papers_batch(pubmed_ids)
        print(f"DEBUG: Got {len(xml_responses)} XML responses")

        # Step 3: Parse papers
        search_results[search_id]['progress'] = 'Parsing paper data...'
        all_papers = []
        for i, xml_response in enumerate(xml_responses):
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

        print(f"DEBUG: Found {len(papers_with_industry)} papers with industry authors out of {len(all_papers)} total")
        
        # Step 5: Prepare results
        search_results[search_id]['progress'] = 'Preparing results...'
        print(f"DEBUG: Preparing results for {len(all_papers)} papers")

        # Convert ALL papers to JSON-serializable format (not just those with industry authors)
        results_data = []
        total_industry_authors = 0

        for i, paper in enumerate(all_papers):
            print(f"DEBUG: Processing paper {i+1}: {paper.pubmed_id}")
            industry_authors = filter_obj.identify_industry_authors(paper.authors)
            companies = filter_obj.get_company_affiliations(industry_authors)
            total_industry_authors += len(industry_authors)
            print(f"DEBUG: Paper {paper.pubmed_id} has {len(industry_authors)} industry authors")
            
            paper_data = {
                'pubmed_id': paper.pubmed_id,
                'title': paper.title,
                'publication_date': paper.publication_date,
                'journal': paper.journal,
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
                'industry_authors_count': len(industry_authors)
            }
            results_data.append(paper_data)
        
        # Create summary
        summary = {
            'total_papers': len(all_papers),
            'papers_with_industry': len(papers_with_industry),
            'total_industry_authors': total_industry_authors,
            'papers_shown': len(results_data),  # All papers are now shown
            'query': query,
            'timestamp': datetime.now().isoformat()
        }
        
        # Store final results
        search_results[search_id] = {
            'status': 'completed',
            'progress': 'Search completed successfully!',
            'results': {
                'papers': results_data,
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
        
        # Convert results back to Paper objects for CSV export
        # This is a simplified approach - in a real app you'd store the original objects
        csv_data = []
        for paper_data in result['results']['papers']:
            row = {
                'PubmedID': paper_data['pubmed_id'],
                'Title': paper_data['title'],
                'Publication Date': paper_data['publication_date'],
                'Non-academic Author(s)': '; '.join([author['name'] for author in paper_data['industry_authors']]),
                'Company Affiliation(s)': '; '.join(paper_data['companies']),
                'Corresponding Author Email': paper_data['corresponding_email'] or '',
                'Journal': paper_data['journal'],
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
