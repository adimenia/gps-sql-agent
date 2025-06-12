#!/usr/bin/env python3
"""Test runner script with various testing scenarios."""

import subprocess
import sys
import argparse


def run_command(command):
    """Run a command and return the result."""
    print(f"Running: {' '.join(command)}")
    result = subprocess.run(command, capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    return result.returncode == 0


def run_unit_tests():
    """Run only unit tests."""
    return run_command(["python3", "-m", "pytest", "tests/unit/", "-v", "-m", "unit"])


def run_integration_tests():
    """Run only integration tests."""
    return run_command(["python3", "-m", "pytest", "tests/integration/", "-v", "-m", "integration"])


def run_etl_tests():
    """Run only ETL-related tests."""
    return run_command(["python3", "-m", "pytest", "-v", "-m", "etl"])


def run_all_tests():
    """Run all tests."""
    return run_command(["python3", "-m", "pytest", "tests/", "-v"])


def run_coverage_tests():
    """Run tests with coverage report."""
    return run_command([
        "python3", "-m", "pytest", "tests/", 
        "--cov=app", 
        "--cov-report=html", 
        "--cov-report=term-missing"
    ])


def run_fast_tests():
    """Run fast tests only (exclude slow tests)."""
    return run_command(["python3", "-m", "pytest", "tests/", "-v", "-m", "not slow"])


def run_specific_test(test_path):
    """Run a specific test file or test function."""
    return run_command(["python3", "-m", "pytest", test_path, "-v"])


def lint_code():
    """Run code linting."""
    print("Running flake8...")
    flake8_success = run_command(["flake8", "app/", "tests/"])
    
    print("Running black check...")
    black_success = run_command(["black", "--check", "app/", "tests/"])
    
    print("Running isort check...")
    isort_success = run_command(["isort", "--check-only", "app/", "tests/"])
    
    return flake8_success and black_success and isort_success


def format_code():
    """Format code with black and isort."""
    print("Formatting code with black...")
    black_success = run_command(["black", "app/", "tests/"])
    
    print("Sorting imports with isort...")
    isort_success = run_command(["isort", "app/", "tests/"])
    
    return black_success and isort_success


def main():
    parser = argparse.ArgumentParser(description="Test runner for Sports Analytics Platform")
    parser.add_argument("--unit", action="store_true", help="Run unit tests only")
    parser.add_argument("--integration", action="store_true", help="Run integration tests only")
    parser.add_argument("--etl", action="store_true", help="Run ETL tests only")
    parser.add_argument("--coverage", action="store_true", help="Run tests with coverage")
    parser.add_argument("--fast", action="store_true", help="Run fast tests only")
    parser.add_argument("--lint", action="store_true", help="Run code linting")
    parser.add_argument("--format", action="store_true", help="Format code")
    parser.add_argument("--test", type=str, help="Run specific test file or function")
    
    args = parser.parse_args()
    
    success = True
    
    if args.unit:
        success = run_unit_tests()
    elif args.integration:
        success = run_integration_tests()
    elif args.etl:
        success = run_etl_tests()
    elif args.coverage:
        success = run_coverage_tests()
    elif args.fast:
        success = run_fast_tests()
    elif args.lint:
        success = lint_code()
    elif args.format:
        success = format_code()
    elif args.test:
        success = run_specific_test(args.test)
    else:
        # Run all tests by default
        success = run_all_tests()
    
    if not success:
        print("❌ Tests failed!")
        sys.exit(1)
    else:
        print("✅ All tests passed!")


if __name__ == "__main__":
    main()