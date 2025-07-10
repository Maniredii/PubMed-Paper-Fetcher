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
        # Initialize components
        fetcher = PubMedFetcher(email=email)
        parser = PubMedParser()
        filter_obj = AffiliationFilter(debug=debug)
        exporter = CSVExporter(debug=debug)
        
        # Step 1: Search PubMed
        search_results[search_id]['progress'] = 'Searching PubMed...'
        pubmed_ids = fetcher.search_papers(query, max_results)
        
        if not pubmed_ids:
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
        xml_responses = fetcher.fetch_papers_batch(pubmed_ids)
        
        # Step 3: Parse papers
        search_results[search_id]['progress'] = 'Parsing paper data...'
        all_papers = []
        for xml_response in xml_responses:
            papers = parser.parse_papers(xml_response)
            all_papers.extend(papers)
        
        # Step 4: Filter for industry authors
        search_results[search_id]['progress'] = 'Filtering for industry authors...'
        papers_with_industry = filter_obj.filter_papers_with_industry_authors(all_papers)
        
        # Step 5: Prepare results
        search_results[search_id]['progress'] = 'Preparing results...'
        
        # Convert papers to JSON-serializable format
        results_data = []
        total_industry_authors = 0
        
        for paper in papers_with_industry:
            industry_authors = filter_obj.identify_industry_authors(paper.authors)
            companies = filter_obj.get_company_affiliations(industry_authors)
            total_industry_authors += len(industry_authors)
            
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
