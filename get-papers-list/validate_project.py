#!/usr/bin/env python3
"""
Project validation and quality assurance script.
Checks project structure, dependencies, and functionality.
"""

import os
import sys
import subprocess
import importlib.util
from pathlib import Path


def check_file_exists(filepath, description):
    """Check if a file exists."""
    if os.path.exists(filepath):
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description} MISSING: {filepath}")
        return False


def check_directory_structure():
    """Validate project directory structure."""
    print("\n📁 CHECKING PROJECT STRUCTURE")
    print("=" * 50)
    
    required_files = [
        ("pyproject.toml", "Poetry configuration"),
        ("cli.py", "CLI interface"),
        ("README.md", "Documentation"),
        ("paper_finder/__init__.py", "Library package"),
        ("paper_finder/fetch.py", "PubMed fetcher"),
        ("paper_finder/parser.py", "XML parser"),
        ("paper_finder/filter.py", "Author filter"),
        ("paper_finder/output.py", "CSV exporter"),
        ("test_paper_finder.py", "Unit tests"),
        ("test_cli.py", "CLI tests")
    ]
    
    all_exist = True
    for filepath, description in required_files:
        if not check_file_exists(filepath, description):
            all_exist = False
    
    return all_exist


def check_poetry_configuration():
    """Check Poetry configuration."""
    print("\n🔧 CHECKING POETRY CONFIGURATION")
    print("=" * 50)
    
    try:
        import toml
    except ImportError:
        print("❌ toml package not available for validation")
        return False
    
    try:
        with open("pyproject.toml", "r") as f:
            config = toml.load(f)
        
        # Check required sections
        checks = [
            ("tool.poetry.name", "Project name"),
            ("tool.poetry.dependencies", "Dependencies"),
            ("tool.poetry.scripts", "Script entry points"),
            ("build-system", "Build system")
        ]
        
        all_good = True
        for key_path, description in checks:
            keys = key_path.split(".")
            current = config
            
            try:
                for key in keys:
                    current = current[key]
                print(f"✅ {description}: Found")
            except KeyError:
                print(f"❌ {description}: Missing {key_path}")
                all_good = False
        
        # Check specific requirements
        if "get-papers-list" in config.get("tool", {}).get("poetry", {}).get("scripts", {}):
            print("✅ get-papers-list command configured")
        else:
            print("❌ get-papers-list command not configured")
            all_good = False
        
        return all_good
        
    except Exception as e:
        print(f"❌ Error reading pyproject.toml: {e}")
        return False


def check_imports():
    """Check that all modules can be imported."""
    print("\n📦 CHECKING MODULE IMPORTS")
    print("=" * 50)
    
    modules_to_test = [
        "paper_finder.fetch",
        "paper_finder.parser", 
        "paper_finder.filter",
        "paper_finder.output"
    ]
    
    all_imported = True
    for module_name in modules_to_test:
        try:
            spec = importlib.util.spec_from_file_location(
                module_name, 
                module_name.replace(".", "/") + ".py"
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            print(f"✅ {module_name}: Import successful")
        except Exception as e:
            print(f"❌ {module_name}: Import failed - {e}")
            all_imported = False
    
    return all_imported


def check_cli_functionality():
    """Test basic CLI functionality."""
    print("\n🖥️  CHECKING CLI FUNCTIONALITY")
    print("=" * 50)
    
    try:
        # Test help option
        result = subprocess.run(
            [sys.executable, "cli.py", "--help"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0 and "Usage:" in result.stdout:
            print("✅ CLI help option works")
            return True
        else:
            print(f"❌ CLI help failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ CLI test failed: {e}")
        return False


def check_csv_output_format():
    """Validate CSV output format matches requirements."""
    print("\n📊 CHECKING CSV OUTPUT FORMAT")
    print("=" * 50)
    
    required_columns = [
        "PubmedID",
        "Title", 
        "Publication Date",
        "Non-academic Author(s)",
        "Company Affiliation(s)",
        "Corresponding Author Email"
    ]
    
    try:
        # Import the output module to check column structure
        sys.path.insert(0, ".")
        from paper_finder.output import CSVExporter
        from paper_finder.parser import Paper, Author
        
        # Create test data
        authors = [Author("Test", "Author", "T", "Test Company Inc.", "test@company.com")]
        papers = [Paper("12345", "Test Paper", "2024-01-01", authors)]
        
        exporter = CSVExporter()
        row_data = exporter._prepare_paper_row(papers[0], authors)
        
        # Check if all required columns are present
        missing_columns = []
        for col in required_columns:
            if col not in row_data:
                missing_columns.append(col)
        
        if not missing_columns:
            print("✅ All required CSV columns present")
            return True
        else:
            print(f"❌ Missing CSV columns: {missing_columns}")
            return False
            
    except Exception as e:
        print(f"❌ CSV format check failed: {e}")
        return False


def run_tests():
    """Run the test suite."""
    print("\n🧪 RUNNING TEST SUITE")
    print("=" * 50)
    
    try:
        # Run unit tests
        result = subprocess.run(
            [sys.executable, "test_paper_finder.py"],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            print("✅ Unit tests passed")
            unit_tests_ok = True
        else:
            print(f"❌ Unit tests failed: {result.stderr}")
            unit_tests_ok = False
        
        # Run CLI tests
        result = subprocess.run(
            [sys.executable, "test_cli.py"],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0:
            print("✅ CLI tests passed")
            cli_tests_ok = True
        else:
            print(f"❌ CLI tests failed: {result.stderr}")
            cli_tests_ok = False
        
        return unit_tests_ok and cli_tests_ok
        
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        return False


def main():
    """Run complete project validation."""
    print("🎯 PROJECT VALIDATION FOR AUTOMATED EVALUATION")
    print("=" * 60)
    
    # Change to project directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    checks = [
        ("Directory Structure", check_directory_structure),
        ("Poetry Configuration", check_poetry_configuration),
        ("Module Imports", check_imports),
        ("CLI Functionality", check_cli_functionality),
        ("CSV Output Format", check_csv_output_format),
        ("Test Suite", run_tests)
    ]
    
    passed = 0
    total = len(checks)
    
    for check_name, check_func in checks:
        try:
            if check_func():
                passed += 1
            print()  # Add spacing
        except Exception as e:
            print(f"❌ {check_name} check crashed: {e}")
            print()
    
    print("=" * 60)
    print(f"VALIDATION RESULTS: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 PROJECT IS READY FOR AUTOMATED EVALUATION!")
        print("✅ All requirements satisfied")
        return 0
    else:
        print("❌ Project needs fixes before submission")
        print(f"   {total - passed} issues need to be resolved")
        return 1


if __name__ == "__main__":
    sys.exit(main())
