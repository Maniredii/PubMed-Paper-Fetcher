# PubMed Paper Finder

A command-line tool to search PubMed for research papers and identify those with authors from pharmaceutical or biotech companies. This tool helps researchers and analysts quickly find industry-sponsored research in their field of interest.

## Project Overview

This project was developed as part of a backend engineering assessment. The goal was to create a robust, well-documented tool that can:

- Search PubMed using any valid query syntax
- Identify papers with non-academic (industry) authors
- Export results in a structured CSV format
- Provide both file output and console display options

## Quick Start

```bash
# Clone and run in 3 commands
git clone https://github.com/Maniredii/Aganitha-Test.git
cd Aganitha-Test/get-papers-list
pip install -r requirements.txt

# Run your first search
python cli.py "cancer therapy" --max-results 5
```

## How the Code is Organized

The project follows a modular architecture with clear separation between the core library and command-line interface:

```
get-papers-list/
├── cli.py                   # Command-line interface (main entry point)
├── paper_finder/            # Core library module
│   ├── __init__.py         # Package initialization
│   ├── fetch.py            # PubMed API interaction and data fetching
│   ├── parser.py           # XML parsing and data structure definitions
│   ├── filter.py           # Author affiliation filtering and scoring
│   └── output.py           # CSV export and console output formatting
├── pyproject.toml          # Poetry configuration and dependencies
├── test_paper_finder.py    # Unit tests for core functionality
├── test_cli.py             # CLI integration tests
└── validate_project.py     # Project validation script
```

### Module Responsibilities

- **`cli.py`**: Main entry point providing the command-line interface using Typer framework
- **`fetch.py`**: Handles all PubMed API interactions, including search and data retrieval
- **`parser.py`**: Parses XML responses from PubMed and creates structured data objects
- **`filter.py`**: Implements heuristic algorithms to identify industry vs academic authors
- **`output.py`**: Manages CSV export and console output formatting

### Design Philosophy

The code is organized around these principles:
- **Separation of Concerns**: Each module has a single, well-defined responsibility
- **Modularity**: The core library can be used independently of the CLI
- **Type Safety**: Comprehensive type hints throughout for better maintainability
- **Error Handling**: Robust error handling at each layer
- **Testability**: Modular design enables comprehensive unit testing

## Installation and Setup

### Prerequisites

- Python 3.9 or higher
- Git (for cloning the repository)
- Internet connection for PubMed API access

### Step 1: Clone the Repository

```bash
# Clone the repository
git clone https://github.com/Maniredii/Aganitha-Test.git

# Navigate to the project directory
cd Aganitha-Test/get-papers-list
```

### Step 2: Install Dependencies

#### Option A: Using Poetry (Recommended)

1. **Install Poetry** (if not already installed):
   ```bash
   # Windows (PowerShell)
   (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -

   # macOS/Linux
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. **Install Dependencies**:
   ```bash
   poetry install
   ```

3. **Run the Tool**:
   ```bash
   poetry run get-papers-list "your search query"
   ```

#### Option B: Using pip

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Tool**:
   ```bash
   python cli.py "your search query"
   ```

### Step 3: Verify Installation

Test that everything is working correctly:

```bash
# Test help command
python cli.py --help

# Test with a simple query
python cli.py "cancer therapy" --max-results 5
```

## Usage Examples

### Basic Usage

```bash
# After cloning and installing dependencies:
cd Aganitha-Test/get-papers-list

# Search for papers about cancer therapy
python cli.py "cancer therapy"

# Search with specific company name
python cli.py "Pfizer AND drug development"

# Limit results and save to file
python cli.py "immunotherapy" --max-results 10 --file results.csv
```

### Command-line Options

- `-h, --help`: Show help message and exit
- `-f, --file FILE`: Save results to CSV file (default: display in console)
- `-d, --debug`: Enable debug output for troubleshooting
- `--max-results N`: Maximum number of papers to retrieve (default: 20)
- `-e, --email EMAIL`: Your email address (recommended by NCBI)
- `--detailed`: Export detailed report with individual author rows

### Advanced Examples

```bash
# Debug mode with detailed output
python cli.py "biotech AND clinical trial" --debug --detailed

# Large dataset export
python cli.py "pharmaceutical research" --max-results 100 --file pharma_research.csv

# Console output for quick review
python cli.py "drug discovery" --max-results 5
```

## Output Format

The tool generates CSV files with the following columns:

| Column | Description |
|--------|-------------|
| PubmedID | Unique PubMed identifier |
| Title | Paper title |
| Publication Date | Date of publication |
| Non-academic Author(s) | Names of industry-affiliated authors |
| Company Affiliation(s) | Company names identified |
| Corresponding Author Email | Contact email of corresponding author |
| Journal | Publication journal |
| Total Authors | Total number of authors |
| Industry Authors Count | Number of industry authors identified |

## Author Classification Algorithm

The tool uses sophisticated heuristics to identify non-academic authors:

### Email Domain Analysis
- Academic domains: `.edu`, `.ac.uk`, `.uni-*`
- Industry domains: `.com`, `.biz`, company-specific domains

### Affiliation Text Analysis
- **Academic keywords**: university, college, institute, department, school
- **Industry keywords**: inc, ltd, corp, pharmaceutical, biotech, therapeutics
- **Known companies**: Pfizer, Roche, Novartis, Merck, GSK, and 20+ others

### Scoring Algorithm
- Combines email and affiliation analysis
- Weighted scoring based on keyword frequency
- Threshold-based classification with configurable sensitivity

## Tools and Libraries Used

This project was built using modern Python development tools and libraries:

### Core Dependencies
- **[Requests](https://docs.python-requests.org/)**: HTTP library for PubMed API calls
- **[Typer](https://typer.tiangolo.com/)**: Modern CLI framework for Python
- **[Pandas](https://pandas.pydata.org/)**: Data manipulation and CSV export
- **[lxml](https://lxml.de/)**: Fast XML parsing for PubMed responses
- **[Rich](https://rich.readthedocs.io/)**: Rich text and beautiful formatting

### Development Tools
- **[Poetry](https://python-poetry.org/)**: Dependency management and packaging
- **Python 3.9+**: Core programming language
- **Git**: Version control
- **pytest**: Testing framework (for development dependencies)

### External APIs
- **[NCBI E-utilities](https://www.ncbi.nlm.nih.gov/books/NBK25497/)**: PubMed search and retrieval API

### Development Process
The project was developed using standard software engineering practices:
- Test-driven development with comprehensive unit tests
- Modular architecture for maintainability
- Type hints for code clarity and IDE support
- Comprehensive documentation and examples
- Git version control with meaningful commit messages

## Testing

The project includes comprehensive tests to ensure reliability:

```bash
# Navigate to project directory first
cd Aganitha-Test/get-papers-list

# Run unit tests
python test_paper_finder.py

# Run CLI tests
python test_cli.py

# Run complete validation
python validate_project.py
```

## Troubleshooting

### Common Issues

**Issue**: `ModuleNotFoundError` when running the tool
**Solution**: Make sure you're in the correct directory and dependencies are installed:
```bash
cd Aganitha-Test/get-papers-list
pip install -r requirements.txt
```

**Issue**: `git clone` fails
**Solution**: Ensure Git is installed and you have internet access:
```bash
git --version  # Should show Git version
```

**Issue**: Python version compatibility
**Solution**: Check your Python version (requires 3.9+):
```bash
python --version  # Should be 3.9 or higher
```

**Issue**: API rate limiting or timeouts
**Solution**: The tool includes built-in rate limiting, but for large queries, consider:
- Using smaller `--max-results` values
- Adding your email with `--email your@email.com`
- Running queries during off-peak hours

## Contributing

This project follows standard Python development practices:
- PEP 8 style guidelines
- Type hints for all functions
- Comprehensive docstrings
- Unit tests for all modules
- Clear commit messages

## License

This project is available under the MIT License.

## Acknowledgments

- NCBI for providing the PubMed E-utilities API
- The Python community for excellent libraries and tools
- The scientific community for making research data accessible
