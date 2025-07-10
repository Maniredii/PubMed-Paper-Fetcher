# Setup Guide - Code Organization and Environment

This guide ensures the project meets all PDF requirements for Code Organization and Environment.

## Requirements Status

### ✅ Version Control - Git
- **Status**: ✅ Git repository initialized
- **Missing**: ❌ GitHub hosting

### ✅ Dependencies and Setup - Poetry  
- **Status**: ✅ pyproject.toml configured
- **Missing**: ❌ Poetry installation verification

### ✅ Execution - get-papers-list command
- **Status**: ✅ Script entry point configured
- **Missing**: ❌ Poetry execution verification

## Setup Instructions

### 1. Install Poetry

#### Windows (PowerShell)
```powershell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
```

#### macOS/Linux
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

#### Alternative: pip install
```bash
pip install poetry
```

### 2. Install Dependencies
```bash
cd get-papers-list
poetry install
```

### 3. Test Executable Command
```bash
# Test the get-papers-list command
poetry run get-papers-list --help

# Test with a query
poetry run get-papers-list "cancer therapy" --max-results 5
```

### 4. GitHub Hosting

#### Create GitHub Repository
1. Go to https://github.com/new
2. Create repository named `get-papers-list`
3. Don't initialize with README (we have one)

#### Push to GitHub
```bash
# Add remote origin
git remote add origin https://github.com/YOUR_USERNAME/get-papers-list.git

# Add all files
git add .

# Initial commit
git commit -m "Initial commit: PubMed paper finder with industry author filtering"

# Push to GitHub
git push -u origin main
```

## Alternative Setup (Without Poetry)

If Poetry is not available, you can still run the project:

### Install Dependencies with pip
```bash
pip install requests typer pandas lxml rich
```

### Run Directly
```bash
python cli.py "cancer therapy" --max-results 5
```

### Create Executable Script (Windows)
Create `get-papers-list.bat`:
```batch
@echo off
python "%~dp0cli.py" %*
```

### Create Executable Script (Unix/Linux/macOS)
Create `get-papers-list` (no extension):
```bash
#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cli import main
if __name__ == "__main__":
    main()
```

Make it executable:
```bash
chmod +x get-papers-list
```

## Verification Checklist

- [ ] Poetry installed and working
- [ ] `poetry install` completes successfully
- [ ] `poetry run get-papers-list --help` shows usage
- [ ] `poetry run get-papers-list "test" --max-results 1` runs successfully
- [ ] Git repository has initial commit
- [ ] Code pushed to GitHub repository
- [ ] GitHub repository is public and accessible

## Project Structure Verification

The project should have this structure:
```
get-papers-list/
├── .git/                 # Git repository
├── .gitignore           # Git ignore file
├── pyproject.toml       # Poetry configuration
├── README.md            # Documentation
├── cli.py               # CLI interface
├── paper_finder/        # Library module
│   ├── __init__.py
│   ├── fetch.py
│   ├── parser.py
│   ├── filter.py
│   └── output.py
└── SETUP_GUIDE.md       # This file
```

## Troubleshooting

### Poetry Installation Issues
- Ensure Python 3.9+ is installed
- Try alternative installation methods
- Check PATH environment variable

### Git/GitHub Issues
- Ensure Git is installed and configured
- Set up SSH keys or use HTTPS authentication
- Check repository permissions

### Dependency Issues
- Verify Python version compatibility
- Try installing dependencies individually
- Check for conflicting packages
