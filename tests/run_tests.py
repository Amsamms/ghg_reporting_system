#!/usr/bin/env python3
"""
Test Runner for GHG Reporting System

This script provides various options for running the comprehensive test suite
with different configurations and reporting options.
"""

import sys
import os
import argparse
import subprocess
import time
from pathlib import Path


def setup_environment():
    """Setup test environment and paths"""
    # Add src directory to Python path
    test_dir = Path(__file__).parent
    root_dir = test_dir.parent
    src_dir = root_dir / 'src'

    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))

    # Set environment variables
    os.environ['PYTHONPATH'] = str(src_dir)
    return test_dir, root_dir


def run_command(cmd, description=""):
    """Run a command and return the result"""
    print(f"\n{'='*60}")
    print(f"Running: {description or ' '.join(cmd)}")
    print(f"{'='*60}")

    start_time = time.time()
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        end_time = time.time()

        print(f"✅ Completed successfully in {end_time - start_time:.2f} seconds")
        if result.stdout:
            print(result.stdout)
        return True, result
    except subprocess.CalledProcessError as e:
        end_time = time.time()
        print(f"❌ Failed after {end_time - start_time:.2f} seconds")
        print(f"Exit code: {e.returncode}")
        if e.stdout:
            print("STDOUT:")
            print(e.stdout)
        if e.stderr:
            print("STDERR:")
            print(e.stderr)
        return False, e


def run_unit_tests(test_dir, verbose=False, coverage=False):
    """Run unit tests"""
    cmd = ['python', '-m', 'pytest', str(test_dir), '-m', 'unit']

    if verbose:
        cmd.append('-v')
    if coverage:
        cmd.extend(['--cov=src', '--cov-report=term-missing'])

    return run_command(cmd, "Unit Tests")


def run_integration_tests(test_dir, verbose=False):
    """Run integration tests"""
    cmd = ['python', '-m', 'pytest', str(test_dir), '-m', 'integration']

    if verbose:
        cmd.append('-v')

    return run_command(cmd, "Integration Tests")


def run_performance_tests(test_dir, verbose=False):
    """Run performance tests"""
    cmd = ['python', '-m', 'pytest', str(test_dir), '-m', 'performance']

    if verbose:
        cmd.append('-v')

    return run_command(cmd, "Performance Tests")


def run_error_handling_tests(test_dir, verbose=False):
    """Run error handling tests"""
    cmd = ['python', '-m', 'pytest', str(test_dir), '-m', 'error_handling']

    if verbose:
        cmd.append('-v')

    return run_command(cmd, "Error Handling Tests")


def run_all_tests(test_dir, verbose=False, coverage=False, parallel=False):
    """Run all tests"""
    cmd = ['python', '-m', 'pytest', str(test_dir)]

    if verbose:
        cmd.append('-v')
    if coverage:
        cmd.extend(['--cov=src', '--cov-report=html', '--cov-report=term-missing'])
    if parallel:
        cmd.extend(['-n', 'auto'])

    return run_command(cmd, "All Tests")


def run_specific_test_file(test_dir, test_file, verbose=False):
    """Run specific test file"""
    test_path = test_dir / test_file
    if not test_path.exists():
        print(f"❌ Test file not found: {test_path}")
        return False, None

    cmd = ['python', '-m', 'pytest', str(test_path)]

    if verbose:
        cmd.append('-v')

    return run_command(cmd, f"Test file: {test_file}")


def run_tests_with_html_report(test_dir, output_dir):
    """Run tests and generate HTML report"""
    cmd = [
        'python', '-m', 'pytest', str(test_dir),
        '--html', str(output_dir / 'test_report.html'),
        '--self-contained-html',
        '--cov=src',
        '--cov-report=html:' + str(output_dir / 'coverage_html')
    ]

    return run_command(cmd, "Tests with HTML Report")


def check_test_coverage(test_dir):
    """Check test coverage"""
    cmd = [
        'python', '-m', 'pytest', str(test_dir),
        '--cov=src',
        '--cov-report=term-missing',
        '--cov-fail-under=80'
    ]

    return run_command(cmd, "Coverage Check")


def run_fast_tests(test_dir):
    """Run only fast tests (exclude slow marker)"""
    cmd = ['python', '-m', 'pytest', str(test_dir), '-m', 'not slow']

    return run_command(cmd, "Fast Tests Only")


def lint_and_format_check(root_dir):
    """Run linting and format checks"""
    print("\n🔍 Running code quality checks...")

    # Check if flake8 is available
    try:
        cmd = ['flake8', str(root_dir / 'src'), '--max-line-length=100']
        success, result = run_command(cmd, "Flake8 Linting")
        if not success:
            print("ℹ️  Install flake8 for code linting: pip install flake8")
    except FileNotFoundError:
        print("ℹ️  Flake8 not found. Install with: pip install flake8")


def main():
    """Main test runner function"""
    parser = argparse.ArgumentParser(
        description="GHG Reporting System Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_tests.py --all                    # Run all tests
  python run_tests.py --unit -v                # Run unit tests with verbose output
  python run_tests.py --integration            # Run integration tests
  python run_tests.py --performance            # Run performance tests
  python run_tests.py --coverage               # Run with coverage report
  python run_tests.py --file test_excel_generator.py  # Run specific test file
  python run_tests.py --fast                   # Run only fast tests
  python run_tests.py --html-report            # Generate HTML report
        """
    )

    # Test selection options
    test_group = parser.add_mutually_exclusive_group()
    test_group.add_argument('--all', action='store_true',
                           help='Run all tests')
    test_group.add_argument('--unit', action='store_true',
                           help='Run unit tests only')
    test_group.add_argument('--integration', action='store_true',
                           help='Run integration tests only')
    test_group.add_argument('--performance', action='store_true',
                           help='Run performance tests only')
    test_group.add_argument('--error-handling', action='store_true',
                           help='Run error handling tests only')
    test_group.add_argument('--fast', action='store_true',
                           help='Run fast tests only (exclude slow tests)')
    test_group.add_argument('--file', type=str,
                           help='Run specific test file')

    # Output options
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Verbose output')
    parser.add_argument('--coverage', action='store_true',
                       help='Generate coverage report')
    parser.add_argument('--parallel', action='store_true',
                       help='Run tests in parallel')
    parser.add_argument('--html-report', action='store_true',
                       help='Generate HTML test report')
    parser.add_argument('--output-dir', type=str, default='test_reports',
                       help='Output directory for reports')

    # Quality checks
    parser.add_argument('--lint', action='store_true',
                       help='Run code quality checks')
    parser.add_argument('--check-coverage', action='store_true',
                       help='Check coverage requirements')

    args = parser.parse_args()

    # Setup environment
    test_dir, root_dir = setup_environment()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)

    print("🧪 GHG Reporting System Test Runner")
    print(f"Test directory: {test_dir}")
    print(f"Root directory: {root_dir}")

    # Default to running all tests if no specific option is provided
    if not any([args.all, args.unit, args.integration, args.performance,
                args.error_handling, args.fast, args.file]):
        args.all = True

    success = True

    # Run linting if requested
    if args.lint:
        lint_and_format_check(root_dir)

    # Run appropriate tests
    if args.all:
        success, _ = run_all_tests(test_dir, args.verbose, args.coverage, args.parallel)
    elif args.unit:
        success, _ = run_unit_tests(test_dir, args.verbose, args.coverage)
    elif args.integration:
        success, _ = run_integration_tests(test_dir, args.verbose)
    elif args.performance:
        success, _ = run_performance_tests(test_dir, args.verbose)
    elif args.error_handling:
        success, _ = run_error_handling_tests(test_dir, args.verbose)
    elif args.fast:
        success, _ = run_fast_tests(test_dir)
    elif args.file:
        success, _ = run_specific_test_file(test_dir, args.file, args.verbose)

    # Generate HTML report if requested
    if args.html_report:
        print("\n📊 Generating HTML reports...")
        run_tests_with_html_report(test_dir, output_dir)
        print(f"📁 Reports saved to: {output_dir}")

    # Check coverage if requested
    if args.check_coverage:
        coverage_success, _ = check_test_coverage(test_dir)
        success = success and coverage_success

    # Final summary
    print(f"\n{'='*60}")
    if success:
        print("✅ All tests completed successfully!")
    else:
        print("❌ Some tests failed. Check output above for details.")
    print(f"{'='*60}")

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()