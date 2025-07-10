"""
CSV output module for exporting filtered paper results.
"""

import pandas as pd
from typing import List, Optional
import os
from .parser import Paper, Author
from .filter import AffiliationFilter


class CSVExporter:
    """Handles exporting paper data to CSV format."""
    
    def __init__(self, debug: bool = False):
        """
        Initialize CSV exporter.
        
        Args:
            debug: Whether to print debug information
        """
        self.debug = debug
        self.filter = AffiliationFilter(debug=debug)
    
    def export_papers(self, papers: List[Paper], output_file: str) -> None:
        """
        Export papers to CSV file.
        
        Args:
            papers: List of Paper objects to export
            output_file: Path to output CSV file
        """
        if not papers:
            print("No papers to export.")
            return
        
        # Prepare data for CSV
        csv_data = []
        
        for paper in papers:
            # Identify industry authors for this paper
            industry_authors = self.filter.identify_industry_authors(paper.authors)
            
            if industry_authors:  # Only include papers with industry authors
                row_data = self._prepare_paper_row(paper, industry_authors)
                csv_data.append(row_data)
        
        if not csv_data:
            print("No papers with industry authors found.")
            return
        
        # Create DataFrame and export
        df = pd.DataFrame(csv_data)
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_file) if os.path.dirname(output_file) else '.', exist_ok=True)
        
        # Export to CSV
        df.to_csv(output_file, index=False, encoding='utf-8')
        
        if self.debug:
            print(f"Exported {len(csv_data)} papers to {output_file}")
            print(f"Columns: {list(df.columns)}")
    
    def _prepare_paper_row(self, paper: Paper, industry_authors: List[Author]) -> dict:
        """
        Prepare a single row of data for CSV export.
        
        Args:
            paper: Paper object
            industry_authors: List of industry-affiliated authors
            
        Returns:
            Dictionary containing row data
        """
        # Format non-academic authors
        non_academic_authors = self._format_authors(industry_authors)
        
        # Get company affiliations
        company_affiliations = self.filter.get_company_affiliations(industry_authors)
        company_affiliations_str = "; ".join(company_affiliations)
        
        # Get corresponding author email
        corresponding_email = paper.corresponding_author_email or ""
        
        return {
            "PubmedID": paper.pubmed_id,
            "Title": paper.title,
            "Publication Date": paper.publication_date,
            "Non-academic Author(s)": non_academic_authors,
            "Company Affiliation(s)": company_affiliations_str,
            "Corresponding Author Email": corresponding_email,
            "Journal": paper.journal,
            "Total Authors": len(paper.authors),
            "Industry Authors Count": len(industry_authors)
        }
    
    def _format_authors(self, authors: List[Author]) -> str:
        """
        Format author list for CSV output.
        
        Args:
            authors: List of Author objects
            
        Returns:
            Formatted string of author names
        """
        author_names = []
        
        for author in authors:
            # Format: "Last, First" or "Last, Initials" if no first name
            if author.first_name:
                name = f"{author.last_name}, {author.first_name}"
            elif author.initials:
                name = f"{author.last_name}, {author.initials}"
            else:
                name = author.last_name
            
            author_names.append(name)
        
        return "; ".join(author_names)

    def print_to_console(self, papers: List[Paper]) -> None:
        """
        Print papers to console in CSV format.

        Args:
            papers: List of Paper objects to print
        """
        if not papers:
            print("No papers to display.")
            return

        # Prepare data for console output
        csv_data = []

        for paper in papers:
            # Identify industry authors for this paper
            industry_authors = self.filter.identify_industry_authors(paper.authors)

            if industry_authors:  # Only include papers with industry authors
                row_data = self._prepare_paper_row(paper, industry_authors)
                csv_data.append(row_data)

        if not csv_data:
            print("No papers with industry authors found.")
            return

        # Create DataFrame and print to console
        df = pd.DataFrame(csv_data)

        # Print CSV header and data
        print("\n" + "="*80)
        print("RESULTS (CSV FORMAT)")
        print("="*80)
        print(df.to_csv(index=False, encoding='utf-8'))

        if self.debug:
            print(f"Displayed {len(csv_data)} papers to console")

    def print_summary(self, papers: List[Paper]) -> None:
        """
        Print a summary of the results.
        
        Args:
            papers: List of Paper objects
        """
        total_papers = len(papers)
        papers_with_industry = 0
        total_industry_authors = 0
        
        for paper in papers:
            industry_authors = self.filter.identify_industry_authors(paper.authors)
            if industry_authors:
                papers_with_industry += 1
                total_industry_authors += len(industry_authors)
        
        print(f"\n=== SUMMARY ===")
        print(f"Total papers found: {total_papers}")
        print(f"Papers with industry authors: {papers_with_industry}")
        print(f"Total industry authors identified: {total_industry_authors}")
        
        if papers_with_industry > 0:
            avg_industry_authors = total_industry_authors / papers_with_industry
            print(f"Average industry authors per relevant paper: {avg_industry_authors:.1f}")
    
    def export_detailed_report(self, papers: List[Paper], output_file: str) -> None:
        """
        Export a detailed report with additional information.
        
        Args:
            papers: List of Paper objects
            output_file: Path to output file
        """
        detailed_data = []
        
        for paper in papers:
            industry_authors = self.filter.identify_industry_authors(paper.authors)
            
            if industry_authors:
                for author in industry_authors:
                    row = {
                        "PubmedID": paper.pubmed_id,
                        "Title": paper.title,
                        "Publication Date": paper.publication_date,
                        "Journal": paper.journal,
                        "Author Last Name": author.last_name,
                        "Author First Name": author.first_name,
                        "Author Initials": author.initials,
                        "Author Email": author.email or "",
                        "Author Affiliation": author.affiliation,
                        "Corresponding Author Email": paper.corresponding_author_email or "",
                        "Abstract": paper.abstract[:500] + "..." if len(paper.abstract) > 500 else paper.abstract
                    }
                    detailed_data.append(row)
        
        if detailed_data:
            df = pd.DataFrame(detailed_data)
            
            # Create detailed report filename
            base_name = os.path.splitext(output_file)[0]
            detailed_file = f"{base_name}_detailed.csv"
            
            df.to_csv(detailed_file, index=False, encoding='utf-8')
            
            if self.debug:
                print(f"Exported detailed report to {detailed_file}")
        else:
            print("No detailed data to export.")
