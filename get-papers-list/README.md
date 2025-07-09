# PubMed Paper Finder

A command-line tool to search PubMed for research papers and identify those with non-academic (industry/commercial) authors. This tool helps researchers and analysts find papers where industry professionals have contributed to academic research.

## Features

- 🔍 Search PubMed using natural language queries
- 🏢 Identify papers with industry/commercial authors using intelligent heuristics
- 📊 Export results to CSV format with detailed author information
- 🎯 Filter out purely academic papers to focus on industry collaboration
- 🐛 Debug mode for troubleshooting and understanding the filtering process
- 📈 Rich CLI interface with progress indicators and result previews

## Installation

### Prerequisites

- Python 3.9 or higher
- pip package manager

### Install Dependencies

```bash
# Clone or download the project
cd get-papers-list

# Install required packages
pip install requests typer pandas lxml rich

# Or if you have Poetry installed:
poetry install
```

## Usage

### Basic Usage

```bash
# Search for papers about cancer therapy
python cli.py "cancer therapy"

# Search with custom output file
python cli.py "machine learning drug discovery" --file ml_papers.csv

# Search with more results
python cli.py "CRISPR gene editing" --max-results 50

# Enable debug mode to see filtering details
python cli.py "immunotherapy" --debug
```

### Advanced Options

```bash
# Full command with all options
python cli.py "artificial intelligence healthcare" \
    --file ai_healthcare.csv \
    --max-results 100 \
    --debug \
    --email your.email@example.com \
    --detailed
```

### Command Line Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--file` | `-f` | Output CSV file path | `results.csv` |
| `--max-results` | `-n` | Maximum papers to retrieve | `20` |
| `--debug` | `-d` | Enable debug output | `False` |
| `--email` | `-e` | Your email (recommended by NCBI) | `None` |
| `--detailed` | | Export detailed report with individual author rows | `False` |
| `--help` | | Show help message | |

## Output Format

### Standard CSV Output

The tool generates a CSV file with the following columns:

| Column | Description |
|--------|-------------|
| `PubmedID` | Unique PubMed identifier |
| `Title` | Paper title |
| `Publication Date` | Publication date (YYYY-MM-DD) |
| `Non-academic Author(s)` | Names of identified industry authors |
| `Company Affiliation(s)` | Company/organization names |
| `Corresponding Author Email` | Email of corresponding author |
| `Journal` | Journal name |
| `Total Authors` | Total number of authors |
| `Industry Authors Count` | Number of industry authors identified |

### Detailed Report

When using `--detailed`, an additional CSV file is created with one row per industry author, including:

- Individual author details (name, email, full affiliation)
- Paper abstract (truncated)
- Complete affiliation text

## Filtering Heuristics

The tool uses sophisticated heuristics to identify non-academic authors:

### Academic Institution Keywords (Excluded)

- university, college, institute, school
- laboratory, lab, research center
- medical center, hospital, clinic
- department, faculty, academy

### Industry/Commercial Keywords (Included)

- pharma, pharmaceutical, biotech, biotechnology
- therapeutics, inc, incorporated, ltd, limited
- llc, corp, corporation, company
- gmbh, ag, sa, plc
- biosciences, life sciences, r&d

### Email Domain Analysis

- **Academic domains**: `.edu`, `.ac.`, university domains → Excluded
- **Commercial domains**: `.com`, `.biz` → Included
- **Ambiguous domains**: `.org` → Evaluated with other criteria

### Scoring Algorithm

The tool combines multiple signals:

1. **Email domain score** (70% weight): More reliable indicator
2. **Affiliation text score** (30% weight): Keyword-based analysis
3. **Threshold**: Authors with combined score > 0.5 are classified as industry

## Examples

### Example 1: Basic Search

```bash
python cli.py "cancer immunotherapy"
```

**Output**: `results.csv` with papers containing industry authors working on cancer immunotherapy.

### Example 2: Pharmaceutical Research

```bash
python cli.py "drug discovery machine learning" --max-results 50 --file pharma_ai.csv
```

**Output**: Up to 50 papers about AI in drug discovery, filtered for industry collaboration.

### Example 3: Debug Mode

```bash
python cli.py "CRISPR therapeutics" --debug
```

**Output**: Detailed console output showing how each author is classified.

## API Information

This tool uses the NCBI E-utilities API:

- **Search API**: `esearch.fcgi` - Find PubMed IDs matching query
- **Fetch API**: `efetch.fcgi` - Retrieve detailed paper information
- **Rate Limiting**: Built-in delays to respect NCBI guidelines
- **Batch Processing**: Handles large result sets efficiently

### API Endpoints

- Base URL: `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/`
- Search: `esearch.fcgi?db=pubmed&term={query}&retmode=json`
- Fetch: `efetch.fcgi?db=pubmed&id={ids}&retmode=xml`

## Testing

### Manual Testing

1. **Test basic functionality**:
   ```bash
   python cli.py "cancer therapy" --max-results 5 --debug
   ```

2. **Test with known industry terms**:
   ```bash
   python cli.py "Pfizer OR Roche OR Novartis" --debug
   ```

3. **Test error handling**:
   ```bash
   python cli.py "nonexistentterms12345" --debug
   ```

### Validation

- Check that output CSV contains expected columns
- Verify that identified authors actually have industry affiliations
- Ensure publication dates are properly formatted
- Confirm email addresses are valid when present

## Troubleshooting

### Common Issues

1. **No results found**:
   - Try broader search terms
   - Increase `--max-results`
   - Check spelling of query terms

2. **Too many academic papers**:
   - Add industry-specific terms to query
   - Use company names in search
   - Try terms like "pharmaceutical", "biotech", "clinical trial"

3. **API errors**:
   - Check internet connection
   - Verify NCBI services are operational
   - Add `--email` parameter (recommended by NCBI)

### Debug Mode

Use `--debug` to see:
- PubMed IDs found
- Author classification details
- Affiliation scoring
- API response information

## Contributing

To extend or modify the tool:

1. **Add new filtering keywords**: Edit `ACADEMIC_KEYWORDS` and `INDUSTRY_KEYWORDS` in `paper_finder/filter.py`
2. **Modify scoring algorithm**: Update `_score_affiliation_text()` and `_score_email_domain()` methods
3. **Add new output formats**: Extend `paper_finder/output.py`
4. **Improve parsing**: Enhance XML parsing in `paper_finder/parser.py`

## License

This project is open source. Please respect NCBI's terms of service when using their APIs.

## Acknowledgments

- NCBI for providing the PubMed E-utilities API
- The scientific community for making research data accessible
