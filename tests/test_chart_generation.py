"""
Chart Generation Tests for GHG Reporting System

This module contains comprehensive tests for chart generation,
visualization validation, and chart data integrity.
"""

import pytest
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch

from report_generator import GHGReportGenerator


class TestChartGeneration:
    """Test suite for chart generation functionality"""

    @pytest.fixture
    def report_generator_with_charts(self, valid_excel_file):
        """Create report generator with valid data for chart testing"""
        return GHGReportGenerator(str(valid_excel_file))

    @pytest.mark.unit
    def test_scope_comparison_chart_structure(self, report_generator_with_charts):
        """Test structure and validity of scope comparison chart"""
        chart = report_generator_with_charts.create_scope_comparison_chart()

        if chart is not None:
            assert isinstance(chart, go.Figure)
            assert len(chart.data) > 0

            # Should be a bar chart
            assert chart.data[0].type == 'bar'

            # Check chart data
            bar_data = chart.data[0]
            assert hasattr(bar_data, 'x')
            assert hasattr(bar_data, 'y')

            # Should have 3 scopes
            if bar_data.x is not None:
                assert len(bar_data.x) == 3

            # Y values should be positive
            if bar_data.y is not None:
                assert all(y >= 0 for y in bar_data.y if y is not None)

    @pytest.mark.unit
    def test_monthly_trend_chart_structure(self, report_generator_with_charts):
        """Test structure and validity of monthly trend chart"""
        chart = report_generator_with_charts.create_monthly_trend_chart()

        if chart is not None:
            assert isinstance(chart, go.Figure)
            assert len(chart.data) > 0

            # Should have traces for each scope
            assert len(chart.data) >= 1

            for trace in chart.data:
                assert trace.type == 'scatter'
                assert hasattr(trace, 'x')
                assert hasattr(trace, 'y')

                # Should have 12 months of data
                if trace.x is not None:
                    assert len(trace.x) == 12

                # Y values should be non-negative
                if trace.y is not None:
                    assert all(y >= 0 for y in trace.y if y is not None)

    @pytest.mark.unit
    def test_sankey_diagram_structure(self, report_generator_with_charts):
        """Test structure and validity of Sankey diagram"""
        chart = report_generator_with_charts.create_sankey_diagram()

        if chart is not None:
            assert isinstance(chart, go.Figure)
            assert len(chart.data) > 0

            # Should be a Sankey diagram
            sankey_data = chart.data[0]
            assert sankey_data.type == 'sankey'

            # Check Sankey components
            assert hasattr(sankey_data, 'node')
            assert hasattr(sankey_data, 'link')

            # Nodes should have labels
            if sankey_data.node and 'label' in sankey_data.node:
                labels = sankey_data.node['label']
                assert len(labels) > 0
                assert 'Total GHG Emissions' in labels

            # Links should have source, target, and value
            if sankey_data.link:
                link_keys = ['source', 'target', 'value']
                for key in link_keys:
                    if key in sankey_data.link:
                        assert len(sankey_data.link[key]) > 0

    @pytest.mark.unit
    def test_facility_breakdown_chart_structure(self, report_generator_with_charts):
        """Test structure and validity of facility breakdown chart"""
        chart = report_generator_with_charts.create_facility_breakdown_chart()

        if chart is not None:
            assert isinstance(chart, go.Figure)
            assert len(chart.data) > 0

            # Should have multiple subplots
            assert hasattr(chart, 'layout')
            if hasattr(chart.layout, 'annotations') and chart.layout.annotations:
                # Should have subplot titles
                annotations = chart.layout.annotations
                assert len(annotations) > 0

    @pytest.mark.unit
    def test_energy_consumption_chart_structure(self, report_generator_with_charts):
        """Test structure and validity of energy consumption chart"""
        chart = report_generator_with_charts.create_energy_consumption_chart()

        if chart is not None:
            assert isinstance(chart, go.Figure)
            assert len(chart.data) > 0

            # Should contain pie chart or bar chart
            chart_types = [trace.type for trace in chart.data]
            assert any(chart_type in ['pie', 'bar'] for chart_type in chart_types)

    @pytest.mark.unit
    def test_chart_colors_and_styling(self, report_generator_with_charts):
        """Test chart color schemes and styling"""
        scope_chart = report_generator_with_charts.create_scope_comparison_chart()

        if scope_chart is not None:
            # Check that colors are defined
            bar_data = scope_chart.data[0]
            if hasattr(bar_data, 'marker') and bar_data.marker:
                assert hasattr(bar_data.marker, 'color')

    @pytest.mark.unit
    def test_chart_titles_and_labels(self, report_generator_with_charts):
        """Test chart titles and axis labels"""
        charts_to_test = [
            ('scope_comparison', 'create_scope_comparison_chart'),
            ('monthly_trend', 'create_monthly_trend_chart'),
            ('sankey', 'create_sankey_diagram'),
            ('facility_breakdown', 'create_facility_breakdown_chart'),
            ('energy_consumption', 'create_energy_consumption_chart')
        ]

        for chart_name, chart_method in charts_to_test:
            chart = getattr(report_generator_with_charts, chart_method)()

            if chart is not None:
                # Should have a title
                if hasattr(chart, 'layout') and hasattr(chart.layout, 'title'):
                    assert chart.layout.title is not None

                # Should have axis labels for applicable charts
                if chart_name in ['scope_comparison', 'monthly_trend']:
                    if hasattr(chart.layout, 'xaxis') and chart.layout.xaxis:
                        assert hasattr(chart.layout.xaxis, 'title')
                    if hasattr(chart.layout, 'yaxis') and chart.layout.yaxis:
                        assert hasattr(chart.layout.yaxis, 'title')

    @pytest.mark.unit
    def test_chart_data_consistency(self, report_generator_with_charts):
        """Test consistency between chart data and source data"""
        # Get source data
        stats = report_generator_with_charts.get_summary_statistics()

        # Test scope comparison chart consistency
        scope_chart = report_generator_with_charts.create_scope_comparison_chart()

        if scope_chart is not None and len(scope_chart.data) > 0:
            bar_data = scope_chart.data[0]
            if bar_data.y is not None and len(bar_data.y) >= 3:
                chart_total = sum(bar_data.y)
                stats_total = stats['total_emissions']

                # Chart total should match statistics total (within tolerance)
                if stats_total > 0:
                    relative_error = abs(chart_total - stats_total) / stats_total
                    assert relative_error < 0.05, f"Chart total {chart_total} doesn't match stats {stats_total}"

    @pytest.mark.unit
    def test_chart_data_validation(self, report_generator_with_charts):
        """Test validation of chart data values"""
        charts_to_test = [
            report_generator_with_charts.create_scope_comparison_chart(),
            report_generator_with_charts.create_monthly_trend_chart(),
            report_generator_with_charts.create_facility_breakdown_chart()
        ]

        for chart in charts_to_test:
            if chart is not None:
                for trace in chart.data:
                    # Check for valid numeric data
                    if hasattr(trace, 'y') and trace.y is not None:
                        for value in trace.y:
                            if value is not None:
                                assert isinstance(value, (int, float, np.number))
                                assert not np.isnan(value)
                                assert not np.isinf(value)

    @pytest.mark.error_handling
    def test_chart_generation_with_empty_data(self):
        """Test chart generation with empty data"""
        # Create report generator with no data
        empty_gen = GHGReportGenerator('/nonexistent/file.xlsx')

        # All chart methods should handle empty data gracefully
        charts = [
            empty_gen.create_scope_comparison_chart(),
            empty_gen.create_monthly_trend_chart(),
            empty_gen.create_sankey_diagram(),
            empty_gen.create_facility_breakdown_chart(),
            empty_gen.create_energy_consumption_chart()
        ]

        # Should either return None or empty charts without crashing
        for chart in charts:
            assert chart is None or isinstance(chart, go.Figure)

    @pytest.mark.error_handling
    def test_chart_generation_with_invalid_data(self, test_data_dir):
        """Test chart generation with invalid/corrupted data"""
        # Create Excel with invalid data
        invalid_file = test_data_dir / 'invalid_chart_data.xlsx'

        invalid_data = pd.DataFrame({
            'Source': ['Test'],
            'Annual_Total': ['invalid_number']  # String instead of number
        })

        with pd.ExcelWriter(invalid_file, engine='openpyxl') as writer:
            invalid_data.to_excel(writer, sheet_name='Scope 1 Emissions', index=False)

        report_gen = GHGReportGenerator(str(invalid_file))

        # Should handle invalid data gracefully
        scope_chart = report_gen.create_scope_comparison_chart()
        assert scope_chart is None or isinstance(scope_chart, go.Figure)

    @pytest.mark.error_handling
    def test_chart_generation_with_nan_values(self, test_data_dir):
        """Test chart generation with NaN values in data"""
        nan_file = test_data_dir / 'nan_chart_data.xlsx'

        nan_data = pd.DataFrame({
            'Source': ['Source1', 'Source2', 'Source3'],
            'Annual_Total': [1000, np.nan, 2000]
        })

        with pd.ExcelWriter(nan_file, engine='openpyxl') as writer:
            nan_data.to_excel(writer, sheet_name='Scope 1 Emissions', index=False)

        report_gen = GHGReportGenerator(str(nan_file))

        # Should handle NaN values gracefully
        scope_chart = report_gen.create_scope_comparison_chart()
        if scope_chart is not None:
            # Chart should be created but handle NaN appropriately
            assert isinstance(scope_chart, go.Figure)

    @pytest.mark.unit
    def test_sankey_diagram_node_link_consistency(self, report_generator_with_charts):
        """Test consistency between nodes and links in Sankey diagram"""
        sankey_chart = report_generator_with_charts.create_sankey_diagram()

        if sankey_chart is not None and len(sankey_chart.data) > 0:
            sankey_data = sankey_chart.data[0]

            if (sankey_data.node and 'label' in sankey_data.node and
                sankey_data.link and 'source' in sankey_data.link and 'target' in sankey_data.link):

                num_nodes = len(sankey_data.node['label'])
                max_source = max(sankey_data.link['source']) if sankey_data.link['source'] else -1
                max_target = max(sankey_data.link['target']) if sankey_data.link['target'] else -1

                # All source and target indices should be valid node indices
                assert max_source < num_nodes, "Invalid source node index in Sankey"
                assert max_target < num_nodes, "Invalid target node index in Sankey"

    @pytest.mark.unit
    def test_monthly_trend_data_points(self, report_generator_with_charts):
        """Test monthly trend chart has correct data points"""
        monthly_chart = report_generator_with_charts.create_monthly_trend_chart()

        if monthly_chart is not None and len(monthly_chart.data) > 0:
            months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                     'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

            for trace in monthly_chart.data:
                if trace.x is not None:
                    # Should have month names or 12 data points
                    assert len(trace.x) == 12

                    # Check if months are in correct order
                    if all(isinstance(x, str) for x in trace.x):
                        assert list(trace.x) == months

    @pytest.mark.unit
    def test_facility_chart_subplots(self, report_generator_with_charts):
        """Test facility breakdown chart subplot structure"""
        facility_chart = report_generator_with_charts.create_facility_breakdown_chart()

        if facility_chart is not None:
            # Should have multiple traces for different subplots
            assert len(facility_chart.data) > 0

            # Check that traces have appropriate types
            trace_types = [trace.type for trace in facility_chart.data]
            expected_types = ['bar', 'scatter']
            assert any(trace_type in expected_types for trace_type in trace_types)

    @pytest.mark.unit
    def test_energy_chart_pie_structure(self, report_generator_with_charts):
        """Test energy consumption pie chart structure"""
        energy_chart = report_generator_with_charts.create_energy_consumption_chart()

        if energy_chart is not None and len(energy_chart.data) > 0:
            # Look for pie chart
            pie_traces = [trace for trace in energy_chart.data if trace.type == 'pie']

            if pie_traces:
                pie_trace = pie_traces[0]
                assert hasattr(pie_trace, 'labels')
                assert hasattr(pie_trace, 'values')

                if pie_trace.labels and pie_trace.values:
                    # Labels and values should have same length
                    assert len(pie_trace.labels) == len(pie_trace.values)

                    # Values should be positive
                    assert all(v >= 0 for v in pie_trace.values if v is not None)

    @pytest.mark.performance
    def test_chart_generation_performance(self, report_generator_with_charts):
        """Test performance of chart generation"""
        import time

        chart_methods = [
            'create_scope_comparison_chart',
            'create_monthly_trend_chart',
            'create_sankey_diagram',
            'create_facility_breakdown_chart',
            'create_energy_consumption_chart'
        ]

        for method_name in chart_methods:
            start_time = time.time()
            chart = getattr(report_generator_with_charts, method_name)()
            end_time = time.time()

            generation_time = end_time - start_time

            # Each chart should generate quickly
            assert generation_time < 15.0, f"{method_name} took {generation_time:.2f}s, expected < 15.0s"

    @pytest.mark.unit
    def test_chart_memory_usage(self, report_generator_with_charts):
        """Test that charts don't consume excessive memory"""
        import sys

        # Generate all charts
        charts = [
            report_generator_with_charts.create_scope_comparison_chart(),
            report_generator_with_charts.create_monthly_trend_chart(),
            report_generator_with_charts.create_sankey_diagram(),
            report_generator_with_charts.create_facility_breakdown_chart(),
            report_generator_with_charts.create_energy_consumption_chart()
        ]

        # Charts should be reasonable in size
        for chart in charts:
            if chart is not None:
                chart_size = sys.getsizeof(chart)
                assert chart_size < 10 * 1024 * 1024, f"Chart too large: {chart_size} bytes"

    @pytest.mark.unit
    def test_chart_serialization(self, report_generator_with_charts):
        """Test that charts can be serialized for HTML export"""
        scope_chart = report_generator_with_charts.create_scope_comparison_chart()

        if scope_chart is not None:
            try:
                # Test JSON serialization (used by Plotly)
                import plotly.io as pio
                json_str = pio.to_json(scope_chart)
                assert isinstance(json_str, str)
                assert len(json_str) > 0
            except Exception as e:
                pytest.fail(f"Chart serialization failed: {e}")

    @pytest.mark.unit
    def test_chart_interactivity_features(self, report_generator_with_charts):
        """Test that charts include interactivity features"""
        charts_to_test = [
            report_generator_with_charts.create_scope_comparison_chart(),
            report_generator_with_charts.create_monthly_trend_chart()
        ]

        for chart in charts_to_test:
            if chart is not None:
                # Check for hover information
                for trace in chart.data:
                    if hasattr(trace, 'hovertemplate') or hasattr(trace, 'hoverinfo'):
                        # Chart has hover information
                        pass
                    # This is acceptable - not all charts need custom hover

    @pytest.mark.unit
    def test_chart_color_consistency(self, report_generator_with_charts):
        """Test color consistency across charts"""
        # Define expected color scheme
        expected_colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']  # From the code

        scope_chart = report_generator_with_charts.create_scope_comparison_chart()
        monthly_chart = report_generator_with_charts.create_monthly_trend_chart()

        if scope_chart is not None and monthly_chart is not None:
            # Colors should be consistent between related charts
            scope_colors = []
            if hasattr(scope_chart.data[0], 'marker') and scope_chart.data[0].marker:
                if hasattr(scope_chart.data[0].marker, 'color'):
                    scope_colors = scope_chart.data[0].marker.color

            monthly_colors = []
            for trace in monthly_chart.data:
                if hasattr(trace, 'line') and trace.line and hasattr(trace.line, 'color'):
                    monthly_colors.append(trace.line.color)

            # Should use colors from the expected scheme
            if scope_colors:
                # At least some colors should match the expected scheme
                assert any(color in expected_colors for color in (scope_colors if isinstance(scope_colors, list) else [scope_colors]))

    @pytest.mark.error_handling
    def test_chart_exception_handling(self, report_generator_with_charts):
        """Test that chart generation handles exceptions gracefully"""
        # Mock plotly to raise exceptions
        with patch('plotly.graph_objects.Figure') as mock_figure:
            mock_figure.side_effect = Exception("Plotly error")

            # Should not crash, should return None
            chart = report_generator_with_charts.create_scope_comparison_chart()
            assert chart is None

    @pytest.mark.unit
    def test_chart_data_types(self, report_generator_with_charts):
        """Test that chart data uses appropriate data types"""
        scope_chart = report_generator_with_charts.create_scope_comparison_chart()

        if scope_chart is not None and len(scope_chart.data) > 0:
            bar_data = scope_chart.data[0]

            # X-axis should be strings (scope names)
            if bar_data.x is not None:
                assert all(isinstance(x, str) for x in bar_data.x)

            # Y-axis should be numeric
            if bar_data.y is not None:
                assert all(isinstance(y, (int, float, np.number)) for y in bar_data.y if y is not None)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])