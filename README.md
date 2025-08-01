# 🧬 AI-Enhanced PubMed Research Discovery Platform

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.3+-green.svg)](https://flask.palletsprojects.com)
[![Groq](https://img.shields.io/badge/Groq-LLM-orange.svg)](https://groq.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **Intelligent biomedical research discovery with AI-powered insights and industry collaboration analysis**

## 🚀 Features

### 🔍 **Smart Search Capabilities**
- **AI-Enhanced Queries**: Automatically improve search terms using Groq LLM
- **Industry Focus**: Specifically targets papers with industry-academic collaborations
- **Real-time Results**: Fast, responsive search with progress tracking
- **Advanced Filtering**: Filter by industry involvement, publication date, and more

### 🧠 **AI-Powered Analysis**
- **Research Summarization**: Automatic paper summaries and key findings extraction
- **Trend Analysis**: Identify emerging research themes and collaboration patterns
- **Industry Detection**: Smart algorithm to identify pharmaceutical, biotech, and other industry authors
- **Insight Generation**: Comprehensive analysis of research significance and impact

### 💻 **Modern Web Interface**
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile
- **Interactive UI**: Real-time updates, smooth animations, and intuitive navigation
- **Export Functionality**: Download results as CSV for further analysis
- **Pagination**: Efficient handling of large result sets

### 📊 **Data Management**
- **PubMed Integration**: Direct access to 35+ million biomedical citations
- **Structured Output**: Organized data with author affiliations and company information
- **Performance Optimization**: Intelligent caching and batch processing

## 🛠️ Installation

### Prerequisites
- Python 3.10 or higher
- pip package manager
- Internet connection for API access
- Groq API key (free at [console.groq.com](https://console.groq.com))

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/ai-pubmed-discovery.git
   cd ai-pubmed-discovery
   ```

2. **Install dependencies**
   ```bash
   pip install flask flask-cors groq pandas requests beautifulsoup4
   ```

3. **Configure environment variables**
   ```bash
   # Copy the example environment file
   cp .env.example .env

   # Edit .env and add your actual Groq API key
   # Get your free API key from: https://console.groq.com
   GROQ_API_KEY=your-actual-groq-api-key-here
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the application**
   Open your browser and go to: `http://localhost:5000`

## 📖 Usage Guide

### Basic Search
1. Enter your research query (e.g., "diabetes treatment", "cancer immunotherapy")
2. Optionally provide your email (recommended by NCBI for API usage)
3. Click **"Search Papers"** to start the search

### AI Enhancement
1. Enter your query
2. Click **"AI Enhance"** to improve the search terms automatically
3. Review the enhanced query and proceed with the search

### Analyzing Results
1. After search completion, view the summary statistics
2. Click **"Analyze Research Trends"** for AI-powered trend analysis
3. Browse through papers with automatic industry detection
4. View AI-generated insights for papers with industry collaborations

### Exporting Data
1. Complete a search
2. Click the **"Download CSV"** button
3. Get a comprehensive spreadsheet with all paper details

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
**use groq for llm**
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

## Web Interface Features

The web application provides an intuitive interface with the following features:

### Search Options
- **Flexible paper count**: Choose from 5, 10, 15, 20, 25, 50, or 100 papers
- **Real-time progress**: Live updates during search and processing
- **Debug mode**: Optional detailed logging for troubleshooting

### Results Display
- **Comprehensive statistics**: Shows papers requested, found, with industry authors, and displayed
- **Industry author highlighting**: Clear badges for industry authors and companies
- **Direct PubMed links**: Click paper titles to view on PubMed
- **CSV download**: Export results for further analysis

### Smart Filtering
- **Only relevant papers shown**: Displays only papers with identified industry authors
- **Exact counts**: Shows precise numbers of papers at each stage
- **Company identification**: Highlights pharmaceutical and biotech companies

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
