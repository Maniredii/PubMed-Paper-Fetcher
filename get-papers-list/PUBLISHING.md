# Publishing to Test PyPI

This document provides instructions for publishing the `get-papers-list` package to Test PyPI.

## Prerequisites

1. **Create Test PyPI Account**: Register at https://test.pypi.org/account/register/
2. **Install Poetry** (recommended) or use pip with build tools

## Method 1: Using Poetry (Recommended)

### Install Poetry
```bash
# On Windows (PowerShell)
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -

# On macOS/Linux
curl -sSL https://install.python-poetry.org | python3 -
```

### Configure Test PyPI
```bash
poetry config repositories.test-pypi https://test.pypi.org/legacy/
poetry config pypi-token.test-pypi <your-test-pypi-token>
```

### Build and Publish
```bash
# Build the package
poetry build

# Publish to Test PyPI
poetry publish -r test-pypi
```

## Method 2: Using pip and build tools

### Install Build Tools
```bash
pip install build twine
```

### Build the Package
```bash
# Build the package
python -m build
```

### Upload to Test PyPI
```bash
# Upload using twine
python -m twine upload --repository testpypi dist/*
```

## Installation from Test PyPI

Once published, users can install the package from Test PyPI:

```bash
# Install from Test PyPI
pip install --index-url https://test.pypi.org/simple/ get-papers-list

# Or with Poetry
poetry add --source test-pypi get-papers-list
```

## Testing the Published Package

After installation, test the package:

```bash
# Test the CLI command
get-papers-list "cancer therapy" --max-results 5

# Test help
get-papers-list --help
```

## Notes

- Test PyPI is for testing purposes only
- Packages on Test PyPI may be deleted periodically
- For production release, use the main PyPI (https://pypi.org/)
- Make sure to increment the version number in `pyproject.toml` for each release

## Version Management

Update the version in `pyproject.toml` before publishing:

```toml
[tool.poetry]
name = "get-papers-list"
version = "0.1.1"  # Increment this for each release
```

## Troubleshooting

### Common Issues

1. **Package name already exists**: Choose a unique name or add a suffix
2. **Authentication errors**: Ensure your API token is correctly configured
3. **Build errors**: Check that all dependencies are properly specified

### Getting API Tokens

1. Go to https://test.pypi.org/manage/account/token/
2. Create a new API token
3. Use the token in your configuration (starts with `pypi-`)
