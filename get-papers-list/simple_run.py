#!/usr/bin/env python3
"""
Simple interactive runner for the PubMed Paper Finder.
Run this script directly without command line arguments.
"""

import sys
import os
from datetime import datetime

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from paper_finder.fetch import PubMedFetcher
from paper_finder.parser import PubMedParser
from paper_finder.filter import AffiliationFilter
from paper_finder.output import CSVExporter


def main():
    print("=" * 60)
    print("🔬 PubMed Paper Finder - Interactive Mode")
    print("=" * 60)
    print()
    print("This tool searches PubMed for research papers with industry authors.")
    print()
    
    # Get user input
    print("📝 Enter your search query:")
    print("Examples:")
    print("  - 'cancer therapy'")
    print("  - 'biotech drug discovery'")
    print("  - 'pharmaceutical clinical trial'")
    print("  - 'Pfizer OR Roche OR Novartis'")
    print()
    
    query = input("🔍 Search query: ").strip()
    
    if not query:
        print("❌ No query entered. Exiting.")
        return
    
    print()
    max_results = input("📊 Maximum results (default 15): ").strip()
    if not max_results:
        max_results = 15
    else:
        try:
            max_results = int(max_results)
        except ValueError:
            max_results = 15
    
    print()
    email = input("📧 Your email (optional, recommended by NCBI): ").strip()
    if not email:
        email = None
    
    print()
    debug = input("🐛 Enable debug mode? (y/n, default n): ").strip().lower()
    debug = debug in ['y', 'yes', '1', 'true']
    
    # Generate output filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"results_{timestamp}.csv"
    
    print()
    print("=" * 60)
    print(f"🚀 Starting search...")
    print(f"📝 Query: {query}")
    print(f"📊 Max results: {max_results}")
    print(f"📁 Output file: {output_file}")
    print(f"🐛 Debug mode: {'ON' if debug else 'OFF'}")
    print("=" * 60)
    print()
    
    try:
        # Initialize components
        fetcher = PubMedFetcher(email=email)
        parser = PubMedParser()
        filter_obj = AffiliationFilter(debug=debug)
        exporter = CSVExporter(debug=debug)
        
        # Step 1: Search PubMed
        print("🔍 Searching PubMed...")
        pubmed_ids = fetcher.search_papers(query, max_results)
        
        if not pubmed_ids:
            print("❌ No papers found for the given query.")
            return
        
        print(f"✅ Found {len(pubmed_ids)} papers")
        if debug:
            print(f"   PubMed IDs: {pubmed_ids[:5]}{'...' if len(pubmed_ids) > 5 else ''}")
        
        # Step 2: Fetch paper details
        print("📄 Fetching paper details...")
        xml_responses = fetcher.fetch_papers_batch(pubmed_ids)
        
        # Step 3: Parse papers
        print("🔬 Parsing paper data...")
        all_papers = []
        for xml_response in xml_responses:
            papers = parser.parse_papers(xml_response)
            all_papers.extend(papers)
        
        print(f"✅ Successfully parsed {len(all_papers)} papers")
        
        # Step 4: Filter for industry authors
        print("🏢 Filtering for industry authors...")
        papers_with_industry = filter_obj.filter_papers_with_industry_authors(all_papers)
        
        print(f"✅ Found {len(papers_with_industry)} papers with industry authors")
        
        # Step 5: Export results
        print("💾 Exporting results...")
        if papers_with_industry:
            exporter.export_papers(papers_with_industry, output_file)
            print(f"✅ Results exported to: {output_file}")
        else:
            print("ℹ️  No papers with industry authors found.")
        
        # Display summary
        print()
        print("=" * 60)
        exporter.print_summary(all_papers)
        print("=" * 60)
        
        if papers_with_industry:
            print()
            print("📋 Preview of first few results:")
            for i, paper in enumerate(papers_with_industry[:3], 1):
                industry_authors = filter_obj.identify_industry_authors(paper.authors)
                companies = filter_obj.get_company_affiliations(industry_authors)
                
                print(f"\n{i}. Paper ID: {paper.pubmed_id}")
                print(f"   Title: {paper.title[:80]}{'...' if len(paper.title) > 80 else ''}")
                print(f"   Industry Authors: {len(industry_authors)}")
                print(f"   Companies: {', '.join(companies[:2])}{'...' if len(companies) > 2 else ''}")
                print(f"   Publication Date: {paper.publication_date}")
        
        print()
        print("🎉 Search completed successfully!")
        
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        if debug:
            import traceback
            print(f"Debug traceback:\n{traceback.format_exc()}")


if __name__ == "__main__":
    main()
    print("\nPress Enter to exit...")
    input()
