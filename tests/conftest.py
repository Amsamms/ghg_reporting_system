"""
Pytest Configuration and Shared Fixtures

This module provides shared fixtures and configuration for all tests
in the GHG Reporting System test suite.
"""

import pytest
import tempfile
import os
import sys
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
import random

# Add src directory to path for imports
TEST_DIR = Path(__file__).parent
ROOT_DIR = TEST_DIR.parent
SRC_DIR = ROOT_DIR / 'src'
sys.path.insert(0, str(SRC_DIR))

@pytest.fixture(scope="session")
def test_data_dir():
    """Provide test data directory path"""
    data_dir = TEST_DIR / 'test_data'
    data_dir.mkdir(exist_ok=True)
    return data_dir

@pytest.fixture(scope="session")
def temp_output_dir():
    """Provide temporary output directory for test results"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)

@pytest.fixture
def mock_company_info():
    """Provide mock company information"""
    return {
        'name': 'TestCorp Petroleum',
        'reporting_year': 2024,
        'report_date': datetime.now().strftime('%Y-%m-%d'),
        'facilities': ['Test Refinery A', 'Test Platform B', 'Test Distribution C', 'Test Storage D']
    }

@pytest.fixture
def sample_scope1_data():
    """Generate sample Scope 1 emissions data"""
    sources = [
        'Combustion - Natural Gas', 'Combustion - Fuel Oil', 'Combustion - Diesel',
        'Process Emissions - Refining', 'Fugitive - Equipment Leaks', 'Fugitive - Venting',
        'Mobile Combustion - Fleet', 'Flaring', 'Process Venting'
    ]

    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
             'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    data = []
    for source in sources:
        monthly_values = [random.uniform(800, 2500) for _ in months]
        annual_total = sum(monthly_values)
        data.append({
            'Source': source,
            'Annual_Total': annual_total,
            'Percentage': 0,  # Will be calculated
            **dict(zip(months, monthly_values))
        })

    return data

@pytest.fixture
def sample_scope2_data():
    """Generate sample Scope 2 emissions data"""
    sources = ['Purchased Electricity', 'Purchased Steam', 'Purchased Heat/Cooling']
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
             'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    data = []
    for source in sources:
        monthly_values = [random.uniform(300, 1200) for _ in months]
        annual_total = sum(monthly_values)
        data.append({
            'Source': source,
            'Annual_Total': annual_total,
            'Percentage': 0,
            **dict(zip(months, monthly_values))
        })

    return data

@pytest.fixture
def sample_scope3_data():
    """Generate sample Scope 3 emissions data"""
    sources = [
        'Purchased Goods/Services', 'Capital Goods', 'Fuel/Energy Activities',
        'Transportation - Upstream', 'Waste Generated', 'Business Travel',
        'Employee Commuting', 'Transportation - Downstream', 'Processing of Products',
        'Use of Sold Products', 'End-of-life Products', 'Leased Assets'
    ]

    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
             'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    data = []
    for source in sources:
        monthly_values = [random.uniform(100, 800) for _ in months]
        annual_total = sum(monthly_values)
        data.append({
            'Source': source,
            'Annual_Total': annual_total,
            'Percentage': 0,
            **dict(zip(months, monthly_values))
        })

    return data

@pytest.fixture
def sample_energy_data():
    """Generate sample energy consumption data"""
    energy_sources = [
        'Natural Gas (MWh)', 'Electricity (MWh)', 'Steam (MWh)',
        'Fuel Oil (MWh)', 'Diesel (MWh)', 'Gasoline (MWh)'
    ]

    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
             'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    data = []
    for source in energy_sources:
        monthly_values = [random.uniform(5000, 15000) for _ in months]
        data.append({
            'Energy_Source': source,
            'Annual_Total': sum(monthly_values),
            'Emission_Factor': random.uniform(0.2, 0.8),
            **dict(zip(months, monthly_values))
        })

    return data

@pytest.fixture
def sample_facility_data(mock_company_info):
    """Generate sample facility data"""
    data = []
    for facility in mock_company_info['facilities']:
        data.append({
            'Facility': facility,
            'Scope_1': random.uniform(8000, 25000),
            'Scope_2': random.uniform(3000, 12000),
            'Scope_3': random.uniform(5000, 18000),
            'Energy_Intensity': random.uniform(2.5, 8.0),
            'Production': random.uniform(50000, 200000)
        })

    return data

@pytest.fixture
def sample_targets_data():
    """Generate sample targets and performance data"""
    return [
        {'Metric': 'Total GHG Reduction Target (%)', 'Target_2024': 5, 'Actual_2024': 3.2, 'Target_2025': 10, 'Status': 'On Track'},
        {'Metric': 'Scope 1 Reduction (%)', 'Target_2024': 3, 'Actual_2024': 2.1, 'Target_2025': 7, 'Status': 'Needs Improvement'},
        {'Metric': 'Energy Intensity Reduction (%)', 'Target_2024': 4, 'Actual_2024': 4.5, 'Target_2025': 8, 'Status': 'Exceeded'},
        {'Metric': 'Renewable Energy Usage (%)', 'Target_2024': 15, 'Actual_2024': 12, 'Target_2025': 25, 'Status': 'On Track'},
        {'Metric': 'Carbon Capture Implementation', 'Target_2024': 2, 'Actual_2024': 1, 'Target_2025': 4, 'Status': 'Delayed'}
    ]

@pytest.fixture
def valid_excel_file(test_data_dir, sample_scope1_data, sample_scope2_data,
                     sample_scope3_data, sample_energy_data, sample_facility_data,
                     sample_targets_data, mock_company_info):
    """Create a valid Excel file for testing"""
    file_path = test_data_dir / 'test_ghg_data.xlsx'

    with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
        # Dashboard sheet
        summary_data = pd.DataFrame([
            ['Company Name', mock_company_info['name']],
            ['Reporting Year', mock_company_info['reporting_year']],
            ['Report Date', mock_company_info['report_date']],
            ['Total Facilities', len(mock_company_info['facilities'])]
        ])
        summary_data.to_excel(writer, sheet_name='Dashboard', index=False, header=False)

        # Emissions sheets
        pd.DataFrame(sample_scope1_data).to_excel(writer, sheet_name='Scope 1 Emissions', index=False)
        pd.DataFrame(sample_scope2_data).to_excel(writer, sheet_name='Scope 2 Emissions', index=False)
        pd.DataFrame(sample_scope3_data).to_excel(writer, sheet_name='Scope 3 Emissions', index=False)

        # Energy and facility sheets
        pd.DataFrame(sample_energy_data).to_excel(writer, sheet_name='Energy Consumption', index=False)
        pd.DataFrame(sample_facility_data).to_excel(writer, sheet_name='Facility Breakdown', index=False)
        pd.DataFrame(sample_targets_data).to_excel(writer, sheet_name='Targets & Performance', index=False)

    return file_path

@pytest.fixture
def invalid_excel_file(test_data_dir):
    """Create an invalid Excel file for testing error handling"""
    file_path = test_data_dir / 'invalid_ghg_data.xlsx'

    # Create Excel with missing required columns
    with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
        # Invalid scope data - missing required columns
        invalid_data = pd.DataFrame({
            'Wrong_Column': [1, 2, 3],
            'Another_Wrong': ['a', 'b', 'c']
        })
        invalid_data.to_excel(writer, sheet_name='Scope 1 Emissions', index=False)

    return file_path

@pytest.fixture
def empty_excel_file(test_data_dir):
    """Create an empty Excel file for testing"""
    file_path = test_data_dir / 'empty_ghg_data.xlsx'

    with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
        # Empty DataFrame
        pd.DataFrame().to_excel(writer, sheet_name='Empty', index=False)

    return file_path

@pytest.fixture
def large_dataset_excel_file(test_data_dir):
    """Create a large Excel file for performance testing"""
    file_path = test_data_dir / 'large_ghg_data.xlsx'

    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
             'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    # Generate large datasets
    large_scope1_data = []
    for i in range(100):  # 100 sources
        monthly_values = [random.uniform(800, 2500) for _ in months]
        large_scope1_data.append({
            'Source': f'Source_{i}',
            'Annual_Total': sum(monthly_values),
            'Percentage': random.uniform(0, 10),
            **dict(zip(months, monthly_values))
        })

    with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
        pd.DataFrame(large_scope1_data).to_excel(writer, sheet_name='Scope 1 Emissions', index=False)
        # Add minimal other sheets to avoid errors
        pd.DataFrame([{'Source': 'Test', 'Annual_Total': 1000}]).to_excel(writer, sheet_name='Scope 2 Emissions', index=False)
        pd.DataFrame([{'Source': 'Test', 'Annual_Total': 1000}]).to_excel(writer, sheet_name='Scope 3 Emissions', index=False)

    return file_path

@pytest.fixture(autouse=True)
def setup_test_environment():
    """Set up test environment before each test"""
    # Set random seed for reproducible tests
    random.seed(42)
    np.random.seed(42)

    # Ensure clean state
    yield

    # Cleanup after test if needed

# Custom markers for test categorization
def pytest_configure(config):
    """Configure custom markers"""
    config.addinivalue_line("markers", "unit: Unit tests for individual modules")
    config.addinivalue_line("markers", "integration: Integration tests for workflows")
    config.addinivalue_line("markers", "performance: Performance tests for large datasets")
    config.addinivalue_line("markers", "error_handling: Error handling and edge case tests")
    config.addinivalue_line("markers", "slow: Tests that take longer to run")