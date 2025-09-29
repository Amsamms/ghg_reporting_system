# GHG Reporting System Test Suite

This directory contains comprehensive tests for the GHG Reporting System, ensuring 100% error-free operation across all modules and scenarios.

## 🧪 Test Structure

### Test Categories

- **Unit Tests** (`test_*.py`) - Individual module functionality
- **Integration Tests** (`test_integration.py`) - End-to-end workflows
- **Data Validation Tests** (`test_data_validation.py`) - Excel file processing
- **Chart Generation Tests** (`test_chart_generation.py`) - Visualization components
- **Performance Tests** (`test_performance.py`) - Large dataset handling
- **GUI Tests** (`test_gui_interface.py`) - User interface functionality

### Test Markers

Tests are categorized using pytest markers:

- `@pytest.mark.unit` - Unit tests for individual modules
- `@pytest.mark.integration` - Integration tests for workflows
- `@pytest.mark.performance` - Performance tests for large datasets
- `@pytest.mark.error_handling` - Error handling and edge case tests
- `@pytest.mark.slow` - Tests that take longer to run

## 🚀 Quick Start

### Install Dependencies

```bash
# Install test dependencies
pip install -r tests/requirements-test.txt

# Or use make
make install-deps
```

### Run All Tests

```bash
# Using the test runner
python tests/run_tests.py --all -v

# Using make
make test

# Using pytest directly
pytest tests/ -v
```

## 📋 Running Specific Test Categories

### Unit Tests Only
```bash
python tests/run_tests.py --unit -v
make test-unit
```

### Integration Tests Only
```bash
python tests/run_tests.py --integration -v
make test-integration
```

### Performance Tests Only
```bash
python tests/run_tests.py --performance -v
make test-performance
```

### Fast Tests (Excluding Slow)
```bash
python tests/run_tests.py --fast -v
make test-fast
```

## 📊 Coverage Reports

### Generate Coverage Report
```bash
python tests/run_tests.py --coverage -v
make test-coverage
```

### HTML Reports
```bash
python tests/run_tests.py --html-report
make test-html
```

Reports are generated in `test_reports/` directory.

## 🔧 Test Configuration

### pytest.ini
Contains pytest configuration including:
- Test discovery patterns
- Coverage settings
- Markers definition
- Warning filters

### conftest.py
Provides shared fixtures:
- `valid_excel_file` - Valid test Excel file
- `invalid_excel_file` - Invalid test Excel file
- `large_dataset_excel_file` - Large dataset for performance testing
- `mock_company_info` - Mock company data
- Sample data generators for all scopes

## 📁 Test Files Overview

### Core Module Tests

| Test File | Purpose | Coverage |
|-----------|---------|----------|
| `test_excel_generator.py` | Excel template generation | Data generation, file creation, formatting |
| `test_report_generator.py` | Data processing and charts | Data loading, statistics, chart generation |
| `test_pdf_report.py` | PDF report generation | PDF creation, chart integration, styling |
| `test_html_report.py` | HTML report generation | Template rendering, interactivity |
| `test_gui_interface.py` | GUI functionality | User interactions, threading, file handling |

### Specialized Tests

| Test File | Purpose | Coverage |
|-----------|---------|----------|
| `test_integration.py` | End-to-end workflows | Complete system integration |
| `test_data_validation.py` | Data integrity | Excel validation, data consistency |
| `test_chart_generation.py` | Visualization quality | Chart structure, data accuracy |
| `test_performance.py` | System performance | Large datasets, memory usage, timing |

## 🎯 Test Scenarios Covered

### Data Validation
- ✅ Valid Excel file structure
- ✅ Required columns validation
- ✅ Data type validation
- ✅ Monthly data consistency
- ✅ Percentage calculations
- ✅ Boundary value testing
- ✅ Special character handling
- ✅ Large number processing

### Error Handling
- ✅ Missing files
- ✅ Corrupted Excel files
- ✅ Invalid data formats
- ✅ Empty datasets
- ✅ Network failures
- ✅ Permission errors
- ✅ Memory constraints

### Performance Testing
- ✅ Large dataset processing (1000+ sources)
- ✅ Memory usage monitoring
- ✅ Concurrent operations
- ✅ File I/O performance
- ✅ Chart generation timing
- ✅ Report generation efficiency

### Chart Generation
- ✅ Scope comparison charts
- ✅ Monthly trend analysis
- ✅ Sankey flow diagrams
- ✅ Facility breakdowns
- ✅ Energy consumption charts
- ✅ Data consistency validation
- ✅ Visual styling verification

## 🏃‍♂️ Running Tests

### Command Line Options

```bash
# Test runner options
python tests/run_tests.py [OPTIONS]

Options:
  --all                    Run all tests
  --unit                   Run unit tests only
  --integration            Run integration tests only
  --performance            Run performance tests only
  --error-handling         Run error handling tests only
  --fast                   Run fast tests only
  --file TEST_FILE         Run specific test file
  -v, --verbose            Verbose output
  --coverage               Generate coverage report
  --parallel               Run tests in parallel
  --html-report            Generate HTML report
  --lint                   Run code quality checks
  --check-coverage         Check coverage requirements
```

### Make Commands

```bash
make test              # Run all tests
make test-unit         # Unit tests only
make test-integration  # Integration tests only
make test-performance  # Performance tests only
make test-coverage     # Tests with coverage
make test-html         # Generate HTML reports
make lint              # Code quality checks
make clean             # Clean test artifacts
```

## 📈 Performance Benchmarks

The test suite includes performance benchmarks for:

- **Excel Generation**: < 30 seconds
- **Data Loading**: < 30 seconds for large datasets
- **Chart Generation**: < 15 seconds per chart
- **HTML Report**: < 45 seconds
- **Memory Usage**: < 500MB increase for large datasets
- **Full Workflow**: < 120 seconds complete pipeline

## 🐛 Debugging Tests

### Running Specific Tests
```bash
# Run single test method
pytest tests/test_excel_generator.py::TestGHGExcelGenerator::test_initialization -v

# Run specific test file
python tests/run_tests.py --file test_excel_generator.py -v

# Run with debug output
pytest tests/ -v -s --tb=long
```

### Test Data
Test data is automatically generated and cleaned up. Temporary files are created in:
- `tests/test_data/` - Persistent test files
- System temp directory - Temporary files during test execution

## 🔍 Code Quality

### Coverage Requirements
- Minimum coverage: 80%
- Target coverage: 90%+
- Critical modules: 95%+

### Quality Checks
```bash
# Run all quality checks
make lint

# Check coverage requirements
make coverage-check
```

## 🚀 Continuous Integration

For CI/CD pipelines:

```bash
# Complete CI test suite
make ci-test

# Includes:
# - All tests
# - Coverage requirements
# - Parallel execution
# - Quality checks
```

## 📝 Contributing Tests

### Adding New Tests

1. **Follow naming convention**: `test_*.py`
2. **Use appropriate markers**: `@pytest.mark.unit`, etc.
3. **Include docstrings**: Describe test purpose
4. **Add to conftest.py**: If creating shared fixtures
5. **Update documentation**: Add to this README

### Test Guidelines

- **Arrange-Act-Assert** pattern
- **Descriptive test names** explaining what is tested
- **Independent tests** - no dependencies between tests
- **Clean fixtures** - proper setup and teardown
- **Error scenarios** - test both success and failure cases
- **Performance considerations** - mark slow tests appropriately

## 🔧 Troubleshooting

### Common Issues

1. **Module import errors**
   - Ensure PYTHONPATH includes src directory
   - Run from project root directory

2. **GUI tests failing**
   - Tests may be skipped in headless environments
   - Use `@pytest.mark.gui` marker

3. **Performance tests timing out**
   - Adjust timeout settings in pytest.ini
   - Check system resources

4. **Coverage not reaching target**
   - Review coverage report in htmlcov/
   - Add tests for uncovered lines

### Getting Help

- Check test output for detailed error messages
- Review coverage reports for missing tests
- Use `-v` flag for verbose output
- Check the GitHub repository for known issues

## 📊 Test Results

Example test execution summary:

```
==================== test session starts ====================
platform linux -- Python 3.9.0
collected 150 items

tests/test_excel_generator.py ................... [ 12%]
tests/test_report_generator.py .................. [ 24%]
tests/test_pdf_report.py ........................ [ 36%]
tests/test_html_report.py ....................... [ 48%]
tests/test_gui_interface.py ..................... [ 60%]
tests/test_integration.py ....................... [ 72%]
tests/test_data_validation.py ................... [ 84%]
tests/test_chart_generation.py .................. [ 92%]
tests/test_performance.py ....................... [100%]

==================== 150 passed in 45.2s ====================

Coverage Report:
Name                    Stmts   Miss  Cover
-------------------------------------------
src/excel_generator.py    156      8    95%
src/report_generator.py   234     12    95%
src/pdf_report.py         187      9    95%
src/html_report.py        124      6    95%
src/gui_interface.py      198     15    92%
-------------------------------------------
TOTAL                     899     50    94%
```

## 🎉 Success Criteria

The test suite ensures:

- ✅ **100% functionality coverage** - All features tested
- ✅ **Error-free operation** - Comprehensive error handling
- ✅ **Performance validation** - Meets performance requirements
- ✅ **Data integrity** - Accurate calculations and processing
- ✅ **User experience** - GUI and workflow testing
- ✅ **Scalability** - Large dataset handling
- ✅ **Reliability** - Consistent results across runs