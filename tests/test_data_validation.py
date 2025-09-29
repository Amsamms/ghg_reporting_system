"""
Data Validation Tests for GHG Reporting System

This module contains comprehensive tests for data validation,
Excel file processing, and data integrity checks.
"""

import pytest
import pandas as pd
import numpy as np
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

from report_generator import GHGReportGenerator
from excel_generator import GHGExcelGenerator


class TestDataValidation:
    """Test suite for data validation and processing"""

    @pytest.mark.unit
    def test_valid_excel_structure_validation(self, valid_excel_file):
        """Test validation of properly structured Excel file"""
        report_gen = GHGReportGenerator(str(valid_excel_file))

        assert report_gen.data is not None

        # Check required sheets exist
        required_sheets = [
            'Scope 1 Emissions', 'Scope 2 Emissions', 'Scope 3 Emissions',
            'Energy Consumption', 'Facility Breakdown'
        ]

        for sheet in required_sheets:
            assert sheet in report_gen.data, f"Missing required sheet: {sheet}"
            assert not report_gen.data[sheet].empty, f"Empty sheet: {sheet}"

    @pytest.mark.unit
    def test_required_columns_validation(self, valid_excel_file):
        """Test validation of required columns in each sheet"""
        report_gen = GHGReportGenerator(str(valid_excel_file))

        # Scope 1, 2, 3 emissions should have these columns
        emission_required_cols = ['Source', 'Annual_Total']
        for scope in ['Scope 1 Emissions', 'Scope 2 Emissions', 'Scope 3 Emissions']:
            if scope in report_gen.data:
                df = report_gen.data[scope]
                for col in emission_required_cols:
                    assert col in df.columns, f"Missing column {col} in {scope}"

        # Energy consumption required columns
        if 'Energy Consumption' in report_gen.data:
            energy_df = report_gen.data['Energy Consumption']
            energy_required_cols = ['Energy_Source', 'Annual_Total']
            for col in energy_required_cols:
                assert col in energy_df.columns, f"Missing column {col} in Energy Consumption"

        # Facility breakdown required columns
        if 'Facility Breakdown' in report_gen.data:
            facility_df = report_gen.data['Facility Breakdown']
            facility_required_cols = ['Facility', 'Scope_1', 'Scope_2', 'Scope_3']
            for col in facility_required_cols:
                assert col in facility_df.columns, f"Missing column {col} in Facility Breakdown"

    @pytest.mark.unit
    def test_data_type_validation(self, valid_excel_file):
        """Test validation of data types in Excel sheets"""
        report_gen = GHGReportGenerator(str(valid_excel_file))

        # Check that Annual_Total columns contain numeric data
        for scope in ['Scope 1 Emissions', 'Scope 2 Emissions', 'Scope 3 Emissions']:
            if scope in report_gen.data and 'Annual_Total' in report_gen.data[scope].columns:
                df = report_gen.data[scope]

                # Should be numeric
                assert df['Annual_Total'].dtype in [np.float64, np.int64, np.float32, np.int32], \
                    f"Annual_Total in {scope} should be numeric"

                # Should not contain NaN values (or very few)
                nan_count = df['Annual_Total'].isna().sum()
                assert nan_count == 0, f"Annual_Total in {scope} contains {nan_count} NaN values"

    @pytest.mark.unit
    def test_numerical_data_validation(self, valid_excel_file):
        """Test validation of numerical data ranges and consistency"""
        report_gen = GHGReportGenerator(str(valid_excel_file))

        # Check for negative emissions (should be rare/zero)
        for scope in ['Scope 1 Emissions', 'Scope 2 Emissions', 'Scope 3 Emissions']:
            if scope in report_gen.data and 'Annual_Total' in report_gen.data[scope].columns:
                df = report_gen.data[scope]
                negative_count = (df['Annual_Total'] < 0).sum()
                assert negative_count == 0, f"{scope} contains {negative_count} negative emission values"

        # Check for unreasonably large values (basic sanity check)
        for scope in ['Scope 1 Emissions', 'Scope 2 Emissions', 'Scope 3 Emissions']:
            if scope in report_gen.data and 'Annual_Total' in report_gen.data[scope].columns:
                df = report_gen.data[scope]
                max_value = df['Annual_Total'].max()
                assert max_value < 1e9, f"{scope} contains unreasonably large value: {max_value}"

    @pytest.mark.unit
    def test_monthly_data_consistency(self, valid_excel_file):
        """Test consistency between monthly data and annual totals"""
        report_gen = GHGReportGenerator(str(valid_excel_file))

        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

        for scope in ['Scope 1 Emissions', 'Scope 2 Emissions', 'Scope 3 Emissions']:
            if scope in report_gen.data:
                df = report_gen.data[scope]

                # Check if monthly columns exist
                monthly_cols_exist = all(month in df.columns for month in months)
                if monthly_cols_exist and 'Annual_Total' in df.columns:

                    for idx, row in df.iterrows():
                        monthly_sum = sum(row[month] for month in months if pd.notna(row[month]))
                        annual_total = row['Annual_Total']

                        if pd.notna(annual_total) and annual_total > 0:
                            # Allow small discrepancies due to rounding
                            relative_error = abs(monthly_sum - annual_total) / annual_total
                            assert relative_error < 0.01, \
                                f"{scope} row {idx}: Monthly sum {monthly_sum} != Annual total {annual_total}"

    @pytest.mark.unit
    def test_percentage_data_validation(self, valid_excel_file):
        """Test validation of percentage data"""
        report_gen = GHGReportGenerator(str(valid_excel_file))

        for scope in ['Scope 1 Emissions', 'Scope 2 Emissions', 'Scope 3 Emissions']:
            if scope in report_gen.data and 'Percentage' in report_gen.data[scope].columns:
                df = report_gen.data[scope]
                percentages = df['Percentage']

                # Percentages should be between 0 and 100
                assert (percentages >= 0).all(), f"{scope} contains negative percentages"
                assert (percentages <= 100).all(), f"{scope} contains percentages > 100"

                # Sum of percentages should be approximately 100 (within scope)
                total_percentage = percentages.sum()
                assert abs(total_percentage - 100) < 5, \
                    f"{scope} percentages sum to {total_percentage}, expected ~100"

    @pytest.mark.error_handling
    def test_missing_file_handling(self):
        """Test handling of missing Excel files"""
        report_gen = GHGReportGenerator('/nonexistent/file.xlsx')
        assert report_gen.data is None

    @pytest.mark.error_handling
    def test_corrupted_excel_file_handling(self, test_data_dir):
        """Test handling of corrupted Excel files"""
        # Create a fake corrupted Excel file
        corrupted_file = test_data_dir / 'corrupted.xlsx'
        with open(corrupted_file, 'w') as f:
            f.write("This is not a valid Excel file")

        report_gen = GHGReportGenerator(str(corrupted_file))
        assert report_gen.data is None

    @pytest.mark.error_handling
    def test_missing_sheets_handling(self, test_data_dir):
        """Test handling of Excel files with missing sheets"""
        excel_file = test_data_dir / 'missing_sheets.xlsx'

        # Create Excel with only one sheet
        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            pd.DataFrame({'Source': ['Test'], 'Annual_Total': [1000]}).to_excel(
                writer, sheet_name='Scope 1 Emissions', index=False)

        report_gen = GHGReportGenerator(str(excel_file))

        # Should load successfully but have limited data
        assert report_gen.data is not None
        assert 'Scope 1 Emissions' in report_gen.data
        assert 'Scope 2 Emissions' not in report_gen.data or report_gen.data['Scope 2 Emissions'].empty

    @pytest.mark.error_handling
    def test_missing_columns_handling(self, test_data_dir):
        """Test handling of sheets with missing required columns"""
        excel_file = test_data_dir / 'missing_columns.xlsx'

        # Create Excel with wrong column names
        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            pd.DataFrame({
                'Wrong_Column': ['Test1', 'Test2'],
                'Another_Wrong': [1000, 2000]
            }).to_excel(writer, sheet_name='Scope 1 Emissions', index=False)

        report_gen = GHGReportGenerator(str(excel_file))

        # Should handle gracefully
        stats = report_gen.get_summary_statistics()
        assert isinstance(stats, dict)

    @pytest.mark.unit
    def test_empty_data_handling(self, test_data_dir):
        """Test handling of empty Excel sheets"""
        excel_file = test_data_dir / 'empty_data.xlsx'

        # Create Excel with empty sheets
        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            pd.DataFrame().to_excel(writer, sheet_name='Scope 1 Emissions', index=False)
            pd.DataFrame().to_excel(writer, sheet_name='Scope 2 Emissions', index=False)

        report_gen = GHGReportGenerator(str(excel_file))

        # Should handle empty data gracefully
        stats = report_gen.get_summary_statistics()
        assert stats['total_emissions'] == 0
        assert stats['scope1_total'] == 0

    @pytest.mark.unit
    def test_special_character_handling(self, test_data_dir):
        """Test handling of special characters in data"""
        excel_file = test_data_dir / 'special_chars.xlsx'

        # Create data with special characters
        special_data = [
            {
                'Source': 'Test Source with "quotes" & symbols',
                'Annual_Total': 1000,
                'Jan': 100, 'Feb': 100, 'Mar': 100, 'Apr': 100,
                'May': 100, 'Jun': 100, 'Jul': 100, 'Aug': 100,
                'Sep': 100, 'Oct': 100, 'Nov': 100, 'Dec': 100
            },
            {
                'Source': 'Source with émissions spéciaux çharacters',
                'Annual_Total': 2000,
                'Jan': 200, 'Feb': 200, 'Mar': 200, 'Apr': 200,
                'May': 200, 'Jun': 200, 'Jul': 200, 'Aug': 200,
                'Sep': 200, 'Oct': 200, 'Nov': 200, 'Dec': 200
            }
        ]

        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            pd.DataFrame(special_data).to_excel(writer, sheet_name='Scope 1 Emissions', index=False)

        report_gen = GHGReportGenerator(str(excel_file))

        assert report_gen.data is not None
        assert len(report_gen.data['Scope 1 Emissions']) == 2

        # Should handle special characters in reports
        html_gen_module = pytest.importorskip('html_report')
        html_gen = html_gen_module.HTMLReportGenerator(report_gen)

        with tempfile.TemporaryDirectory() as temp_dir:
            html_file = Path(temp_dir) / 'special_chars_report.html'
            success = html_gen.generate_html_report(str(html_file))
            assert success is True

    @pytest.mark.unit
    def test_large_numbers_handling(self, test_data_dir):
        """Test handling of very large emission numbers"""
        excel_file = test_data_dir / 'large_numbers.xlsx'

        # Create data with large numbers
        large_data = [
            {
                'Source': 'Very Large Source',
                'Annual_Total': 1e6,  # 1 million
                'Jan': 1e5, 'Feb': 1e5, 'Mar': 1e5, 'Apr': 1e5,
                'May': 1e5, 'Jun': 1e5, 'Jul': 1e5, 'Aug': 1e5,
                'Sep': 1e5, 'Oct': 1e5, 'Nov': 1e5, 'Dec': 1e5
            }
        ]

        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            pd.DataFrame(large_data).to_excel(writer, sheet_name='Scope 1 Emissions', index=False)

        report_gen = GHGReportGenerator(str(excel_file))

        assert report_gen.data is not None
        stats = report_gen.get_summary_statistics()
        assert stats['scope1_total'] == 1e6

    @pytest.mark.unit
    def test_decimal_precision_handling(self, test_data_dir):
        """Test handling of decimal precision in data"""
        excel_file = test_data_dir / 'decimal_precision.xlsx'

        # Create data with high decimal precision
        precision_data = [
            {
                'Source': 'Precise Source',
                'Annual_Total': 1234.56789,
                'Jan': 102.88065, 'Feb': 102.88065, 'Mar': 102.88065, 'Apr': 102.88065,
                'May': 102.88065, 'Jun': 102.88065, 'Jul': 102.88065, 'Aug': 102.88065,
                'Sep': 102.88065, 'Oct': 102.88065, 'Nov': 102.88065, 'Dec': 102.88065
            }
        ]

        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            pd.DataFrame(precision_data).to_excel(writer, sheet_name='Scope 1 Emissions', index=False)

        report_gen = GHGReportGenerator(str(excel_file))

        assert report_gen.data is not None
        # Should preserve reasonable precision
        actual_total = report_gen.data['Scope 1 Emissions']['Annual_Total'].iloc[0]
        assert abs(actual_total - 1234.56789) < 0.01

    @pytest.mark.unit
    def test_data_boundary_values(self, test_data_dir):
        """Test handling of boundary values (zero, very small numbers)"""
        excel_file = test_data_dir / 'boundary_values.xlsx'

        boundary_data = [
            {
                'Source': 'Zero Source',
                'Annual_Total': 0,
                'Jan': 0, 'Feb': 0, 'Mar': 0, 'Apr': 0,
                'May': 0, 'Jun': 0, 'Jul': 0, 'Aug': 0,
                'Sep': 0, 'Oct': 0, 'Nov': 0, 'Dec': 0
            },
            {
                'Source': 'Very Small Source',
                'Annual_Total': 0.001,
                'Jan': 0.00008333, 'Feb': 0.00008333, 'Mar': 0.00008333, 'Apr': 0.00008333,
                'May': 0.00008333, 'Jun': 0.00008333, 'Jul': 0.00008333, 'Aug': 0.00008333,
                'Sep': 0.00008333, 'Oct': 0.00008333, 'Nov': 0.00008333, 'Dec': 0.00008333
            }
        ]

        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            pd.DataFrame(boundary_data).to_excel(writer, sheet_name='Scope 1 Emissions', index=False)

        report_gen = GHGReportGenerator(str(excel_file))

        assert report_gen.data is not None
        stats = report_gen.get_summary_statistics()

        # Should handle zero and very small values
        assert stats['scope1_total'] == 0.001
        assert stats['total_emissions'] == 0.001

    @pytest.mark.unit
    def test_facility_data_validation(self, valid_excel_file):
        """Test validation of facility-specific data"""
        report_gen = GHGReportGenerator(str(valid_excel_file))

        if 'Facility Breakdown' in report_gen.data:
            facility_df = report_gen.data['Facility Breakdown']

            # Check facility names are unique
            facility_names = facility_df['Facility'].tolist()
            assert len(facility_names) == len(set(facility_names)), "Facility names should be unique"

            # Check that facility totals are consistent
            if all(col in facility_df.columns for col in ['Scope_1', 'Scope_2', 'Scope_3']):
                for idx, row in facility_df.iterrows():
                    # All scope values should be non-negative
                    assert row['Scope_1'] >= 0, f"Facility {row['Facility']} has negative Scope 1"
                    assert row['Scope_2'] >= 0, f"Facility {row['Facility']} has negative Scope 2"
                    assert row['Scope_3'] >= 0, f"Facility {row['Facility']} has negative Scope 3"

    @pytest.mark.unit
    def test_energy_data_validation(self, valid_excel_file):
        """Test validation of energy consumption data"""
        report_gen = GHGReportGenerator(str(valid_excel_file))

        if 'Energy Consumption' in report_gen.data:
            energy_df = report_gen.data['Energy Consumption']

            # Check energy source names
            if 'Energy_Source' in energy_df.columns:
                energy_sources = energy_df['Energy_Source'].tolist()

                # Should contain recognizable energy types
                energy_keywords = ['gas', 'electric', 'steam', 'fuel', 'diesel', 'gasoline']
                has_energy_keyword = any(
                    any(keyword.lower() in source.lower() for keyword in energy_keywords)
                    for source in energy_sources
                )
                assert has_energy_keyword, "Energy sources should contain recognizable energy types"

            # Check emission factors if present
            if 'Emission_Factor' in energy_df.columns:
                emission_factors = energy_df['Emission_Factor']

                # Emission factors should be reasonable (0-1 range typically)
                assert (emission_factors >= 0).all(), "Emission factors should be non-negative"
                assert (emission_factors <= 10).all(), "Emission factors should be reasonable (≤10)"

    @pytest.mark.performance
    def test_large_dataset_validation_performance(self, large_dataset_excel_file):
        """Test validation performance with large datasets"""
        import time

        start_time = time.time()
        report_gen = GHGReportGenerator(str(large_dataset_excel_file))
        stats = report_gen.get_summary_statistics()
        end_time = time.time()

        processing_time = end_time - start_time

        # Should process large dataset within reasonable time
        assert processing_time < 30.0, f"Large dataset validation took {processing_time:.2f}s, expected < 30.0s"
        assert report_gen.data is not None
        assert stats['total_emissions'] > 0

if __name__ == "__main__":
    pytest.main([__file__, "-v"])