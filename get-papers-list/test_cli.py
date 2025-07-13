#!/usr/bin/env python3
"""
Integration tests for the command-line interface.
Validates CLI functionality and user interaction.
"""

import subprocess
import sys
import os
import tempfile
import time
from pathlib import Path


def run_command(cmd, timeout=30):
    """Run a command and return result."""
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            capture_output=True, 
            text=True, 
            timeout=timeout,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Command timed out"


def test_help_option():
    """Test --help option."""
    print("Testing --help option...")
    
    # Test both -h and --help
    for help_flag in ["-h", "--help"]:
        returncode, stdout, stderr = run_command(f"python cli.py {help_flag}")
        
        if returncode != 0:
            print(f"[FAIL] Help option {help_flag} failed")
            return False
        
        if "Usage:" not in stdout or "Options:" not in stdout:
            print(f"[FAIL] Help output missing required sections for {help_flag}")
            return False
    
    print("[PASS] Help option works correctly")
    return True


def test_required_arguments():
    """Test that query argument is required."""
    print("Testing required arguments...")
    
    returncode, stdout, stderr = run_command("python cli.py")
    
    if returncode == 0:
        print("[FAIL] CLI should fail when no query provided")
        return False

    if "Missing argument" not in stdout and "Missing argument" not in stderr:
        print("[FAIL] Missing proper error message for missing query")
        return False

    print("[PASS] Required arguments validation works")
    return True


def test_basic_functionality():
    """Test basic CLI functionality with a simple query."""
    print("Testing basic functionality...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        output_file = os.path.join(temp_dir, "test_output.csv")
        
        # Test with file output
        cmd = f'python cli.py "test" --max-results 1 --file "{output_file}"'
        returncode, stdout, stderr = run_command(cmd, timeout=60)
        
        if returncode != 0:
            print(f"[FAIL] Basic functionality test failed: {stderr}")
            return False

        # Check if output mentions the process
        if "PubMed Paper Finder" not in stdout:
            print("[FAIL] Missing expected output format")
            return False

    print("[PASS] Basic functionality works")
    return True


def test_console_output():
    """Test console output when no file specified."""
    print("Testing console output...")
    
    cmd = 'python cli.py "test" --max-results 1'
    returncode, stdout, stderr = run_command(cmd, timeout=60)
    
    if returncode != 0:
        print(f"[FAIL] Console output test failed: {stderr}")
        return False

    if "Output: Console" not in stdout:
        print("[FAIL] Console output not properly indicated")
        return False

    print("[PASS] Console output works")
    return True


def test_debug_mode():
    """Test debug mode functionality."""
    print("Testing debug mode...")
    
    cmd = 'python cli.py "test" --debug --max-results 1'
    returncode, stdout, stderr = run_command(cmd, timeout=60)
    
    if returncode != 0:
        print(f"[FAIL] Debug mode test failed: {stderr}")
        return False

    if "Debug mode enabled" not in stdout:
        print("[FAIL] Debug mode not properly indicated")
        return False

    print("[PASS] Debug mode works")
    return True


def test_all_options():
    """Test CLI with all options."""
    print("Testing all CLI options...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        output_file = os.path.join(temp_dir, "full_test.csv")
        
        cmd = f'python cli.py "test" --file "{output_file}" --max-results 2 --debug --email "test@example.com" --detailed'
        returncode, stdout, stderr = run_command(cmd, timeout=60)
        
        if returncode != 0:
            print(f"[FAIL] Full options test failed: {stderr}")
            return False

        # Check for expected output elements
        expected_elements = [
            "PubMed Paper Finder",
            "Query: test",
            "Max results: 2",
            "Debug mode enabled"
        ]

        for element in expected_elements:
            if element not in stdout:
                print(f"[FAIL] Missing expected element: {element}")
                return False

    print("[PASS] All options work correctly")
    return True


def test_error_handling():
    """Test error handling with invalid inputs."""
    print("Testing error handling...")
    
    # Test with very long nonsense query that should return no results
    cmd = 'python cli.py "xyznonexistentquery12345abcdef" --max-results 1'
    returncode, stdout, stderr = run_command(cmd, timeout=60)
    
    # Should complete successfully even with no results
    if returncode not in [0, 1]:  # Allow exit code 1 for no results
        print(f"[FAIL] Error handling test failed unexpectedly: {stderr}")
        return False

    print("[PASS] Error handling works")
    return True


def main():
    """Run all CLI tests."""
    print("=" * 60)
    print("CLI AUTOMATED TESTING SUITE")
    print("=" * 60)
    
    tests = [
        test_help_option,
        test_required_arguments,
        test_basic_functionality,
        test_console_output,
        test_debug_mode,
        test_all_options,
        test_error_handling
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                print(f"[FAIL] Test {test.__name__} failed")
        except Exception as e:
            print(f"[FAIL] Test {test.__name__} crashed: {e}")

        print("-" * 40)

    print(f"\nTEST RESULTS: {passed}/{total} tests passed")

    if passed == total:
        print("[SUCCESS] ALL TESTS PASSED - CLI is ready for automated evaluation!")
        return 0
    else:
        print("[FAIL] Some tests failed - please fix issues before submission")
        return 1


if __name__ == "__main__":
    sys.exit(main())
