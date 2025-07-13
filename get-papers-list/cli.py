#!/usr/bin/env python3
"""
CLI interface for the PubMed paper finder tool.
"""

import typer
from typing import Optional
from rich.console import Console
from rich.table import Table
import sys
import os

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from paper_finder.fetch import PubMedFetcher
from paper_finder.parser import PubMedParser
from paper_finder.filter import AffiliationFilter
from paper_finder.output import CSVExporter

console = Console()


def search_papers(
    query: Optional[str] = typer.Argument(None, help="Search query for PubMed"),
    file: Optional[str] = typer.Option(
        None,
        "--file",
        "-f",
        help="Output CSV file path (default: results.csv)"
    ),
    help_flag: bool = typer.Option(
        False,
        "--help",
        "-h",
        help="Show this message and exit"
    ),
    max_results: int = typer.Option(
        20, 
        "--max-results", 
        "-n", 
        help="Maximum number of papers to retrieve"
    ),
    debug: bool = typer.Option(
        False, 
        "--debug", 
        "-d", 
        help="Enable debug output"
    ),
    email: Optional[str] = typer.Option(
        None,
        "--email",
        "-e",
        help="Your email address (recommended by NCBI)"
    ),
    detailed: bool = typer.Option(
        False,
        "--detailed",
        help="Export detailed report with individual author rows"
    )
):
    """
    Search PubMed for research papers and filter for those with non-academic authors.
    
    This tool searches PubMed using the provided query, identifies papers with authors
    from industry/commercial organizations, and exports the results to CSV.
    
    Example usage:
    
        get-papers-list "cancer therapy" --file output.csv --debug
        
        get-papers-list "machine learning drug discovery" --max-results 50
    """
    
    # Handle help flag
    if help_flag:
        console.print(__doc__ or "PubMed Paper Finder - Find research papers with non-academic authors")
        console.print("\nUsage: get-papers-list [OPTIONS] QUERY")
        console.print("\nOptions:")
        console.print("  -h, --help     Show this message and exit")
        console.print("  -d, --debug    Enable debug output")
        console.print("  -f, --file     Output CSV file path")
        console.print("  -e, --email    Your email address (recommended by NCBI)")
        console.print("  --detailed     Export detailed report with individual author rows")
        console.print("  --max-results  Maximum number of papers to retrieve [default: 20]")
        console.print("\nExample:")
        console.print('  get-papers-list "cancer therapy" --file output.csv --debug')
        raise typer.Exit(0)

    # Validate query is provided when not showing help
    if not query:
        console.print("[red]Error: Missing argument 'QUERY'.[/red]")
        console.print("Use -h or --help for usage information.")
        raise typer.Exit(1)

    # Check if output should go to console or file
    output_to_console = file is None
    
    console.print(f"[bold blue]PubMed Paper Finder[/bold blue]")
    console.print(f"Query: [green]{query}[/green]")
    console.print(f"Max results: [yellow]{max_results}[/yellow]")
    if output_to_console:
        console.print("Output: [cyan]Console[/cyan]")
    else:
        console.print(f"Output file: [cyan]{file}[/cyan]")
    
    if debug:
        console.print("[yellow]Debug mode enabled[/yellow]")
    
    try:
        # Initialize components
        fetcher = PubMedFetcher(email=email)
        parser = PubMedParser()
        filter_obj = AffiliationFilter(debug=debug)
        exporter = CSVExporter(debug=debug)
        
        # Step 1: Search PubMed
        console.print("Searching PubMed...")

        if debug:
            console.print(f"[dim]Searching PubMed with query: {query}[/dim]")

        pubmed_ids = fetcher.search_papers(query, max_results)
        console.print(f"Found {len(pubmed_ids)} papers")

        if not pubmed_ids:
            console.print("[red]No papers found for the given query.[/red]")
            raise typer.Exit(1)

        if debug:
            console.print(f"[dim]Found PubMed IDs: {pubmed_ids[:5]}{'...' if len(pubmed_ids) > 5 else ''}[/dim]")

        # Step 2: Fetch paper details
        console.print("Fetching paper details...")

        xml_responses = fetcher.fetch_papers_batch(pubmed_ids)
        console.print("Parsing paper data...")

        # Step 3: Parse papers
        all_papers = []
        for xml_response in xml_responses:
            papers = parser.parse_papers(xml_response)
            all_papers.extend(papers)

        console.print(f"Parsed {len(all_papers)} papers")

        if debug:
            console.print(f"[dim]Successfully parsed {len(all_papers)} papers[/dim]")

        # Step 4: Filter for industry authors
        console.print("Filtering for industry authors...")

        papers_with_industry = filter_obj.filter_papers_with_industry_authors(all_papers)
        console.print(f"Found {len(papers_with_industry)} papers with industry authors")

        # Step 5: Export results
        console.print("Exporting results...")

        if all_papers:
            if output_to_console:
                # Show all papers, highlighting those with industry authors
                exporter.print_all_papers_to_console(all_papers, papers_with_industry)
            else:
                # Export all papers with industry author indicators
                exporter.export_all_papers(all_papers, papers_with_industry, file)

                if detailed:
                    exporter.export_detailed_report(papers_with_industry, file)

            console.print("Export complete")
        else:
            console.print("No papers to export")
        
        # Display results summary
        console.print("\n" + "="*50)
        exporter.print_summary(all_papers)
        
        if papers_with_industry:
            if output_to_console:
                console.print(f"\n[green]✓ Results displayed above[/green]")
            else:
                console.print(f"\n[green]✓ Results exported to: {file}[/green]")

                if detailed:
                    detailed_file = os.path.splitext(file)[0] + "_detailed.csv"
                    console.print(f"[green]✓ Detailed report exported to: {detailed_file}[/green]")

            # Show preview of results (only if not already printed to console)
            if not output_to_console:
                _show_results_preview(papers_with_industry, filter_obj)
        else:
            console.print(f"\n[yellow]No papers with industry authors found for query: {query}[/yellow]")
            console.print("[dim]Try a different search query or check the filtering criteria.[/dim]")
    
    except KeyboardInterrupt:
        console.print("\n[red]Operation cancelled by user.[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        if debug:
            import traceback
            console.print(f"[dim]{traceback.format_exc()}[/dim]")
        raise typer.Exit(1)


def _show_results_preview(papers, filter_obj):
    """Show a preview of the results in a table."""
    console.print("\n[bold]Preview of Results:[/bold]")
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("PubMed ID", style="cyan")
    table.add_column("Title", style="white", max_width=50)
    table.add_column("Industry Authors", style="green")
    table.add_column("Publication Date", style="yellow")
    
    # Show first 5 papers
    for paper in papers[:5]:
        industry_authors = filter_obj.identify_industry_authors(paper.authors)
        author_names = [f"{a.last_name}, {a.first_name or a.initials}" for a in industry_authors]
        
        table.add_row(
            paper.pubmed_id,
            paper.title[:47] + "..." if len(paper.title) > 50 else paper.title,
            "; ".join(author_names[:2]) + ("..." if len(author_names) > 2 else ""),
            paper.publication_date
        )
    
    console.print(table)
    
    if len(papers) > 5:
        console.print(f"[dim]... and {len(papers) - 5} more papers[/dim]")


def main():
    """Entry point for Poetry script."""
    typer.run(search_papers)


if __name__ == "__main__":
    main()
