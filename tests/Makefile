# Makefile for GHG Reporting System Tests
# Provides convenient commands for running tests and quality checks

.PHONY: help test test-unit test-integration test-performance test-coverage test-fast test-html clean lint install-deps

# Default target
help:
	@echo "GHG Reporting System Test Commands"
	@echo "=================================="
	@echo ""
	@echo "Test Commands:"
	@echo "  make test              - Run all tests"
	@echo "  make test-unit         - Run unit tests only"
	@echo "  make test-integration  - Run integration tests only"
	@echo "  make test-performance  - Run performance tests only"
	@echo "  make test-fast         - Run fast tests only (exclude slow tests)"
	@echo "  make test-coverage     - Run tests with coverage report"
	@echo "  make test-html         - Generate HTML test report"
	@echo ""
	@echo "Quality Commands:"
	@echo "  make lint              - Run code quality checks"
	@echo "  make coverage-check    - Check coverage requirements"
	@echo ""
	@echo "Setup Commands:"
	@echo "  make install-deps      - Install test dependencies"
	@echo "  make clean             - Clean test artifacts"
	@echo ""

# Test commands
test:
	@echo "Running all tests..."
	python tests/run_tests.py --all -v

test-unit:
	@echo "Running unit tests..."
	python tests/run_tests.py --unit -v

test-integration:
	@echo "Running integration tests..."
	python tests/run_tests.py --integration -v

test-performance:
	@echo "Running performance tests..."
	python tests/run_tests.py --performance -v

test-fast:
	@echo "Running fast tests..."
	python tests/run_tests.py --fast -v

test-coverage:
	@echo "Running tests with coverage..."
	python tests/run_tests.py --all --coverage -v

test-html:
	@echo "Generating HTML test report..."
	python tests/run_tests.py --all --html-report --coverage

coverage-check:
	@echo "Checking coverage requirements..."
	python tests/run_tests.py --check-coverage

# Quality commands
lint:
	@echo "Running code quality checks..."
	python tests/run_tests.py --lint

# Setup commands
install-deps:
	@echo "Installing test dependencies..."
	pip install -r tests/requirements-test.txt

# Specific test files
test-excel:
	python tests/run_tests.py --file test_excel_generator.py -v

test-report:
	python tests/run_tests.py --file test_report_generator.py -v

test-pdf:
	python tests/run_tests.py --file test_pdf_report.py -v

test-html-gen:
	python tests/run_tests.py --file test_html_report.py -v

test-gui:
	python tests/run_tests.py --file test_gui_interface.py -v

test-data:
	python tests/run_tests.py --file test_data_validation.py -v

test-charts:
	python tests/run_tests.py --file test_chart_generation.py -v

# Clean artifacts
clean:
	@echo "Cleaning test artifacts..."
	rm -rf tests/__pycache__/
	rm -rf tests/.pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf test_reports/
	rm -rf tests/test_data/*.xlsx
	rm -rf tests/test_data/*.html
	rm -rf tests/test_data/*.pdf
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} +

# Development commands
dev-test:
	@echo "Running development tests (fast, with coverage)..."
	python tests/run_tests.py --fast --coverage -v

ci-test:
	@echo "Running CI tests (all tests, strict)..."
	python tests/run_tests.py --all --coverage --check-coverage --parallel

# Benchmarking
benchmark:
	@echo "Running performance benchmarks..."
	python tests/run_tests.py --performance -v

# Documentation
test-docs:
	@echo "Testing documentation examples..."
	# Add documentation testing if needed

# Parallel testing
test-parallel:
	@echo "Running tests in parallel..."
	python tests/run_tests.py --all --parallel -v