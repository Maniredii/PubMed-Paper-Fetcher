# 🔬 PubMed Paper Finder - User Guide

## 🚀 Quick Start

### Option 1: Interactive Mode (Recommended for Beginners)
1. **Install dependencies**: Double-click `setup.bat` or run `pip install -r requirements.txt`
2. **Run the app**: Double-click `simple_run.py` or run `python simple_run.py`
3. **Follow the prompts**: Enter your search query and options
4. **Get results**: The app will create a CSV file with your results

### Option 2: Command Line Mode
```bash
# Basic usage
python cli.py main "cancer therapy"

# With options
python cli.py main "biotech drug discovery" --max-results 20 --debug --file my_results.csv
```

### Option 3: Windows Batch File
1. Double-click `run_app.bat`
2. Follow the prompts

## 📋 What You'll Get

The application creates a CSV file with these columns:
- **PubmedID**: Unique identifier for the paper
- **Title**: Paper title
- **Publication Date**: When it was published
- **Non-academic Author(s)**: Names of industry authors found
- **Company Affiliation(s)**: Company names
- **Corresponding Author Email**: Contact email
- **Journal**: Journal name
- **Total Authors**: Total number of authors
- **Industry Authors Count**: Number of industry authors

## 🎯 Best Search Queries

### High Success Rate Queries:
- `"pharmaceutical clinical trial"`
- `"biotech drug discovery"`
- `"Pfizer OR Roche OR Novartis"`
- `"industry collaboration research"`
- `"commercial sponsor clinical"`

### Company-Specific Searches:
- `"GSK pharmaceutical"`
- `"Merck drug development"`
- `"Johnson Johnson research"`

## 🔧 Troubleshooting

### No Results Found?
- Try broader search terms
- Increase max results (try 50-100)
- Use company names in your search
- Try different pharmaceutical terms

### Installation Issues?
- Make sure Python 3.9+ is installed
- Run `pip install --upgrade pip` first
- Try `pip install requests typer pandas lxml rich` manually

### Application Errors?
- Check your internet connection
- Try adding your email with `--email your@email.com`
- Use debug mode to see what's happening

## 📊 Understanding the Results

### Industry Author Detection
The app uses smart algorithms to identify industry authors by:
- **Email domains**: `.com` domains vs `.edu` academic domains
- **Affiliation keywords**: "Inc", "Ltd", "Corp", "Pharma", "Biotech"
- **Company names**: Known pharmaceutical and biotech companies

### Scoring System
- Authors get scores from -1 (definitely academic) to +1 (definitely industry)
- Threshold is 0.5 - authors above this are classified as industry
- Email domains have 70% weight, affiliation text has 30% weight

## 📁 Output Files

### Standard Output: `results.csv`
- One row per paper with industry authors
- Summary information for each paper

### Detailed Output: `results_detailed.csv` (with --detailed flag)
- One row per industry author
- Includes full affiliation text and abstracts

## 🎯 Example Successful Run

```
Query: "pharmaceutical clinical trial"
Results: 2 papers found with 4 industry authors
Companies: GSK, Ashfield MedComms
Output: pharma_trial.csv
```

## 💡 Tips for Better Results

1. **Use specific industry terms**: "pharmaceutical", "biotech", "clinical trial"
2. **Include company names**: Add known pharma companies to your search
3. **Try different result limits**: Start with 15-20, increase if needed
4. **Use debug mode**: See exactly how authors are being classified
5. **Check recent papers**: Industry collaborations are more common in recent research

## 🆘 Need Help?

1. **Check the README.md** for detailed technical information
2. **Use debug mode** (`--debug`) to see what's happening
3. **Try the interactive mode** (`simple_run.py`) for guided usage
4. **Check your CSV output** even if no results are shown - sometimes papers are found but don't meet the threshold
