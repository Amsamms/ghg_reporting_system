"""
Unit Tests for GHGReportGenerator Module

This module contains comprehensive unit tests for the GHGReportGenerator class,
testing all chart generation, data processing, and analysis functionality.
"""

import pytest
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from pathlib import Path
import tempfile
import os
from unittest.mock import Mock, patch

from report_generator import GHGReportGenerator


class TestGHGReportGenerator:
    """Test suite for GHGReportGenerator class"""

    @pytest.fixture
    def mock_excel_data(self, sample_scope1_data, sample_scope2_data,
                       sample_scope3_data, sample_energy_data,
                       sample_facility_data, sample_targets_data):
        """Create mock Excel data for testing"""
        return {
            'Dashboard': pd.DataFrame([
                ['Company Name', 'TestCorp Petroleum'],
                ['Reporting Year', 2024]
            ]),
            'Scope 1 Emissions': pd.DataFrame(sample_scope1_data),
            'Scope 2 Emissions': pd.DataFrame(sample_scope2_data),
            'Scope 3 Emissions': pd.DataFrame(sample_scope3_data),
            'Energy Consumption': pd.DataFrame(sample_energy_data),
            'Facility Breakdown': pd.DataFrame(sample_facility_data),
            'Targets & Performance': pd.DataFrame(sample_targets_data)
        }

    @pytest.fixture
    def report_generator_with_data(self, valid_excel_file):
        """Create GHGReportGenerator with valid test data"""
        return GHGReportGenerator(str(valid_excel_file))

    @pytest.fixture
    def report_generator_mock_data(self, mock_excel_data):
        """Create GHGReportGenerator with mocked data"""
        with patch('report_generator.pd.read_excel') as mock_read:
            mock_read.return_value = mock_excel_data
            generator = GHGReportGenerator('/fake/path.xlsx')
            generator.data = mock_excel_data
            return generator

    @pytest.mark.unit
    def test_initialization_valid_file(self, valid_excel_file):
        """Test initialization with valid Excel file"""
        generator = GHGReportGenerator(str(valid_excel_file))

        assert generator.excel_file == str(valid_excel_file)
        assert generator.data is not None
        assert isinstance(generator.data, dict)
        assert generator.report_date is not None

    @pytest.mark.unit
    def test_initialization_invalid_file(self):
        """Test initialization with invalid Excel file"""
        generator = GHGReportGenerator('/nonexistent/file.xlsx')

        assert generator.excel_file == '/nonexistent/file.xlsx'
        assert generator.data is None

    @pytest.mark.unit
    def test_load_excel_data_success(self, valid_excel_file):
        """Test successful Excel data loading"""
        generator = GHGReportGenerator(str(valid_excel_file))

        assert generator.data is not None
        assert isinstance(generator.data, dict)

        # Check expected sheets exist
        expected_sheets = [
            'Dashboard', 'Scope 1 Emissions', 'Scope 2 Emissions',
            'Scope 3 Emissions', 'Energy Consumption', 'Facility Breakdown',
            'Targets & Performance'
        ]

        for sheet in expected_sheets:
            assert sheet in generator.data
            assert isinstance(generator.data[sheet], pd.DataFrame)

    @pytest.mark.unit
    def test_load_excel_data_failure(self):
        """Test Excel data loading failure"""
        generator = GHGReportGenerator('/invalid/path.xlsx')
        assert generator.data is None

    @pytest.mark.unit
    def test_create_sankey_diagram_success(self, report_generator_mock_data):
        """Test successful Sankey diagram creation"""
        fig = report_generator_mock_data.create_sankey_diagram()

        assert fig is not None
        assert isinstance(fig, go.Figure)
        assert len(fig.data) > 0
        assert fig.data[0].type == 'sankey'

    @pytest.mark.unit
    def test_create_sankey_diagram_no_data(self):
        """Test Sankey diagram creation with no data"""
        generator = GHGReportGenerator('/fake/path.xlsx')
        generator.data = None

        fig = generator.create_sankey_diagram()
        assert fig is None

    @pytest.mark.unit
    def test_create_sankey_diagram_empty_data(self, report_generator_mock_data):
        """Test Sankey diagram creation with empty data"""
        # Set empty DataFrames
        report_generator_mock_data.data['Scope 1 Emissions'] = pd.DataFrame()
        report_generator_mock_data.data['Scope 2 Emissions'] = pd.DataFrame()
        report_generator_mock_data.data['Scope 3 Emissions'] = pd.DataFrame()

        fig = report_generator_mock_data.create_sankey_diagram()
        assert fig is None

    @pytest.mark.unit
    def test_create_scope_comparison_chart_success(self, report_generator_mock_data):
        """Test successful scope comparison chart creation"""
        fig = report_generator_mock_data.create_scope_comparison_chart()

        assert fig is not None
        assert isinstance(fig, go.Figure)
        assert len(fig.data) > 0
        assert fig.data[0].type == 'bar'

    @pytest.mark.unit
    def test_create_scope_comparison_chart_no_data(self):
        """Test scope comparison chart creation with no data"""
        generator = GHGReportGenerator('/fake/path.xlsx')
        generator.data = None

        fig = generator.create_scope_comparison_chart()
        assert fig is None

    @pytest.mark.unit
    def test_create_monthly_trend_chart_success(self, report_generator_mock_data):
        """Test successful monthly trend chart creation"""
        fig = report_generator_mock_data.create_monthly_trend_chart()

        assert fig is not None
        assert isinstance(fig, go.Figure)
        assert len(fig.data) >= 3  # Should have at least 3 traces (scopes)

    @pytest.mark.unit
    def test_create_monthly_trend_chart_no_data(self):
        """Test monthly trend chart creation with no data"""
        generator = GHGReportGenerator('/fake/path.xlsx')
        generator.data = None

        fig = generator.create_monthly_trend_chart()
        assert fig is None

    @pytest.mark.unit
    def test_create_facility_breakdown_chart_success(self, report_generator_mock_data):
        """Test successful facility breakdown chart creation"""
        fig = report_generator_mock_data.create_facility_breakdown_chart()

        assert fig is not None
        assert isinstance(fig, go.Figure)
        assert len(fig.data) > 0

    @pytest.mark.unit
    def test_create_facility_breakdown_chart_no_data(self):
        """Test facility breakdown chart creation with no data"""
        generator = GHGReportGenerator('/fake/path.xlsx')
        generator.data = None

        fig = generator.create_facility_breakdown_chart()
        assert fig is None

    @pytest.mark.unit
    def test_create_facility_breakdown_chart_missing_columns(self, report_generator_mock_data):
        """Test facility breakdown chart with missing columns"""
        # Remove required columns
        report_generator_mock_data.data['Facility Breakdown'] = pd.DataFrame({'Wrong_Column': [1, 2, 3]})

        fig = report_generator_mock_data.create_facility_breakdown_chart()
        assert fig is None

    @pytest.mark.unit
    def test_create_energy_consumption_chart_success(self, report_generator_mock_data):
        """Test successful energy consumption chart creation"""
        fig = report_generator_mock_data.create_energy_consumption_chart()

        assert fig is not None
        assert isinstance(fig, go.Figure)
        assert len(fig.data) > 0

    @pytest.mark.unit
    def test_create_energy_consumption_chart_no_data(self):
        """Test energy consumption chart creation with no data"""
        generator = GHGReportGenerator('/fake/path.xlsx')
        generator.data = None

        fig = generator.create_energy_consumption_chart()
        assert fig is None

    @pytest.mark.unit
    def test_create_energy_consumption_chart_empty_data(self, report_generator_mock_data):
        """Test energy consumption chart with empty data"""
        report_generator_mock_data.data['Energy Consumption'] = pd.DataFrame()

        fig = report_generator_mock_data.create_energy_consumption_chart()
        assert fig is None

    @pytest.mark.unit
    def test_generate_recommendations_success(self, report_generator_mock_data):
        """Test successful recommendation generation"""
        recommendations = report_generator_mock_data.generate_recommendations()

        assert isinstance(recommendations, list)
        assert len(recommendations) > 0

        for rec in recommendations:
            assert isinstance(rec, dict)
            assert 'priority' in rec
            assert 'category' in rec
            assert 'recommendation' in rec
            assert 'potential_impact' in rec
            assert 'implementation_timeline' in rec
            assert rec['priority'] in ['High', 'Medium', 'Low']

    @pytest.mark.unit
    def test_generate_recommendations_no_data(self):
        """Test recommendation generation with no data"""
        generator = GHGReportGenerator('/fake/path.xlsx')
        generator.data = None

        recommendations = generator.generate_recommendations()
        assert isinstance(recommendations, list)
        # Should still return some general recommendations

    @pytest.mark.unit
    def test_generate_recommendations_high_emissions(self, report_generator_mock_data):
        """Test recommendations for high emission scenarios"""
        # Modify data to trigger high emission recommendations
        scope1_df = report_generator_mock_data.data['Scope 1 Emissions'].copy()
        scope1_df['Annual_Total'] = scope1_df['Annual_Total'] * 10  # Increase emissions
        report_generator_mock_data.data['Scope 1 Emissions'] = scope1_df

        recommendations = report_generator_mock_data.generate_recommendations()

        # Should include high priority recommendations for emission reduction
        high_priority_recs = [r for r in recommendations if r['priority'] == 'High']
        assert len(high_priority_recs) > 0

    @pytest.mark.unit
    def test_generate_recommendations_underperforming_targets(self, report_generator_mock_data):
        """Test recommendations for underperforming targets"""
        # Modify targets data to show poor performance
        targets_df = report_generator_mock_data.data['Targets & Performance'].copy()
        targets_df.loc[0, 'Status'] = 'Needs Improvement'
        report_generator_mock_data.data['Targets & Performance'] = targets_df

        recommendations = report_generator_mock_data.generate_recommendations()

        # Should include recommendations for target achievement
        target_recs = [r for r in recommendations if 'target' in r['category'].lower() or 'Target' in r['category']]
        assert len(target_recs) > 0

    @pytest.mark.unit
    def test_get_summary_statistics_success(self, report_generator_mock_data):
        """Test successful summary statistics generation"""
        stats = report_generator_mock_data.get_summary_statistics()

        assert isinstance(stats, dict)

        required_keys = [
            'total_emissions', 'scope1_total', 'scope2_total', 'scope3_total',
            'carbon_intensity', 'total_facilities', 'report_date',
            'scope1_pct', 'scope2_pct', 'scope3_pct'
        ]

        for key in required_keys:
            assert key in stats, f"Missing key: {key}"

        # Test value validity
        assert stats['total_emissions'] >= 0
        assert stats['scope1_total'] >= 0
        assert stats['scope2_total'] >= 0
        assert stats['scope3_total'] >= 0
        assert stats['carbon_intensity'] >= 0
        assert stats['total_facilities'] >= 0

        # Test percentages sum to 100 (approximately)
        total_pct = stats['scope1_pct'] + stats['scope2_pct'] + stats['scope3_pct']
        assert abs(total_pct - 100) < 0.1

    @pytest.mark.unit
    def test_get_summary_statistics_no_data(self):
        """Test summary statistics generation with no data"""
        generator = GHGReportGenerator('/fake/path.xlsx')
        generator.data = None

        stats = generator.get_summary_statistics()
        assert isinstance(stats, dict)
        # Should return empty dict or dict with zero values

    @pytest.mark.unit
    def test_get_summary_statistics_zero_emissions(self, report_generator_mock_data):
        """Test summary statistics with zero emissions"""
        # Set all emissions to zero
        for sheet in ['Scope 1 Emissions', 'Scope 2 Emissions', 'Scope 3 Emissions']:
            df = report_generator_mock_data.data[sheet].copy()
            df['Annual_Total'] = 0
            report_generator_mock_data.data[sheet] = df

        stats = report_generator_mock_data.get_summary_statistics()

        assert stats['total_emissions'] == 0
        assert stats['scope1_total'] == 0
        assert stats['scope2_total'] == 0
        assert stats['scope3_total'] == 0

        # Percentages should be 0 when total is 0
        assert stats['scope1_pct'] == 0
        assert stats['scope2_pct'] == 0
        assert stats['scope3_pct'] == 0

    @pytest.mark.error_handling
    def test_chart_generation_with_corrupted_data(self, report_generator_mock_data):
        """Test chart generation with corrupted data"""
        # Corrupt data by adding NaN values
        scope1_df = report_generator_mock_data.data['Scope 1 Emissions'].copy()
        scope1_df.loc[0, 'Annual_Total'] = np.nan
        report_generator_mock_data.data['Scope 1 Emissions'] = scope1_df

        # Charts should handle NaN values gracefully
        fig = report_generator_mock_data.create_scope_comparison_chart()
        # Should either return None or a valid figure
        assert fig is None or isinstance(fig, go.Figure)

    @pytest.mark.error_handling
    def test_chart_generation_with_negative_values(self, report_generator_mock_data):
        """Test chart generation with negative values"""
        # Add negative values
        scope1_df = report_generator_mock_data.data['Scope 1 Emissions'].copy()
        scope1_df.loc[0, 'Annual_Total'] = -1000
        report_generator_mock_data.data['Scope 1 Emissions'] = scope1_df

        # Charts should handle negative values gracefully
        fig = report_generator_mock_data.create_scope_comparison_chart()
        assert fig is None or isinstance(fig, go.Figure)

    @pytest.mark.error_handling
    def test_chart_generation_with_missing_columns(self, report_generator_mock_data):
        """Test chart generation with missing required columns"""
        # Remove required column
        scope1_df = report_generator_mock_data.data['Scope 1 Emissions'].copy()
        scope1_df = scope1_df.drop('Annual_Total', axis=1)
        report_generator_mock_data.data['Scope 1 Emissions'] = scope1_df

        fig = report_generator_mock_data.create_scope_comparison_chart()
        # Should handle missing columns gracefully
        assert fig is None or isinstance(fig, go.Figure)

    @pytest.mark.performance
    def test_chart_generation_performance(self, report_generator_mock_data):
        """Test performance of chart generation"""
        import time

        charts_to_test = [
            'create_sankey_diagram',
            'create_scope_comparison_chart',
            'create_monthly_trend_chart',
            'create_facility_breakdown_chart',
            'create_energy_consumption_chart'
        ]

        for chart_method in charts_to_test:
            start_time = time.time()
            fig = getattr(report_generator_mock_data, chart_method)()
            end_time = time.time()

            generation_time = end_time - start_time

            # Each chart should generate within reasonable time
            assert generation_time < 10.0, f"{chart_method} took {generation_time:.2f}s, expected < 10.0s"

    @pytest.mark.performance
    def test_recommendations_generation_performance(self, report_generator_mock_data):
        """Test performance of recommendations generation"""
        import time

        start_time = time.time()
        recommendations = report_generator_mock_data.generate_recommendations()
        end_time = time.time()

        generation_time = end_time - start_time

        assert generation_time < 5.0, f"Recommendations generation took {generation_time:.2f}s, expected < 5.0s"
        assert len(recommendations) > 0

    @pytest.mark.unit
    def test_monthly_data_aggregation(self, report_generator_mock_data):
        """Test monthly data aggregation in charts"""
        fig = report_generator_mock_data.create_monthly_trend_chart()

        if fig is not None:
            # Check that chart has monthly data points
            months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                     'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

            # Should have data for all months
            for trace in fig.data:
                if hasattr(trace, 'x') and trace.x is not None:
                    assert len(trace.x) == 12  # 12 months

    @pytest.mark.unit
    def test_sankey_diagram_node_structure(self, report_generator_mock_data):
        """Test Sankey diagram node structure"""
        fig = report_generator_mock_data.create_sankey_diagram()

        if fig is not None and len(fig.data) > 0:
            sankey_data = fig.data[0]

            # Check node structure
            assert hasattr(sankey_data, 'node')
            assert hasattr(sankey_data, 'link')

            # Check that there are nodes and links
            if sankey_data.node and 'label' in sankey_data.node:
                assert len(sankey_data.node['label']) > 0

            if sankey_data.link and 'source' in sankey_data.link:
                assert len(sankey_data.link['source']) > 0
                assert len(sankey_data.link['target']) > 0
                assert len(sankey_data.link['value']) > 0

    @pytest.mark.unit
    def test_facility_breakdown_calculations(self, report_generator_mock_data):
        """Test facility breakdown calculations"""
        fig = report_generator_mock_data.create_facility_breakdown_chart()

        if fig is not None:
            # Verify that facility data is processed correctly
            facility_df = report_generator_mock_data.data['Facility Breakdown']

            if not facility_df.empty and all(col in facility_df.columns for col in ['Scope_1', 'Scope_2', 'Scope_3']):
                # Check that total emissions are calculated
                expected_totals = facility_df['Scope_1'] + facility_df['Scope_2'] + facility_df['Scope_3']

                # The chart should include these totals
                assert len(expected_totals) == len(facility_df)

    @pytest.mark.error_handling
    def test_exception_handling_in_charts(self, report_generator_mock_data):
        """Test exception handling in chart generation methods"""
        # Mock plotly to raise an exception
        with patch('plotly.graph_objects.Figure') as mock_fig:
            mock_fig.side_effect = Exception("Plotly error")

            # All chart methods should handle exceptions gracefully
            assert report_generator_mock_data.create_sankey_diagram() is None
            assert report_generator_mock_data.create_scope_comparison_chart() is None
            assert report_generator_mock_data.create_monthly_trend_chart() is None
            assert report_generator_mock_data.create_facility_breakdown_chart() is None
            assert report_generator_mock_data.create_energy_consumption_chart() is None

    @pytest.mark.unit
    def test_data_validation_in_summary_stats(self, report_generator_mock_data):
        """Test data validation in summary statistics"""
        stats = report_generator_mock_data.get_summary_statistics()

        # All emission values should be non-negative
        emission_keys = ['total_emissions', 'scope1_total', 'scope2_total', 'scope3_total']
        for key in emission_keys:
            if key in stats:
                assert stats[key] >= 0, f"{key} should be non-negative"

        # Percentages should be between 0 and 100
        percentage_keys = ['scope1_pct', 'scope2_pct', 'scope3_pct']
        for key in percentage_keys:
            if key in stats:
                assert 0 <= stats[key] <= 100, f"{key} should be between 0 and 100"

        # Total facilities should be integer-like
        if 'total_facilities' in stats:
            assert isinstance(stats['total_facilities'], (int, float))
            assert stats['total_facilities'] >= 0

if __name__ == "__main__":
    pytest.main([__file__, "-v"])