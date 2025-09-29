"""
Unit Tests for HTMLReportGenerator Module

This module contains comprehensive unit tests for the HTMLReportGenerator class,
testing HTML generation, template rendering, and error handling.
"""

import pytest
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import plotly.graph_objects as go
from jinja2 import Template

from html_report import HTMLReportGenerator
from report_generator import GHGReportGenerator


class TestHTMLReportGenerator:
    """Test suite for HTMLReportGenerator class"""

    @pytest.fixture
    def mock_report_generator(self, mock_excel_data):
        """Create mock report generator for testing"""
        mock_gen = Mock(spec=GHGReportGenerator)
        mock_gen.data = mock_excel_data
        mock_gen.get_summary_statistics.return_value = {
            'total_emissions': 50000,
            'scope1_total': 20000,
            'scope2_total': 15000,
            'scope3_total': 15000,
            'scope1_pct': 40.0,
            'scope2_pct': 30.0,
            'scope3_pct': 30.0,
            'carbon_intensity': 0.25,
            'total_facilities': 4,
            'report_date': '2024-01-01 12:00:00'
        }

        # Mock chart creation methods
        mock_chart = Mock(spec=go.Figure)
        mock_gen.create_scope_comparison_chart.return_value = mock_chart
        mock_gen.create_monthly_trend_chart.return_value = mock_chart
        mock_gen.create_sankey_diagram.return_value = mock_chart
        mock_gen.create_facility_breakdown_chart.return_value = mock_chart
        mock_gen.create_energy_consumption_chart.return_value = mock_chart

        mock_gen.generate_recommendations.return_value = [
            {
                'priority': 'High',
                'category': 'Emission Reduction',
                'recommendation': 'Implement energy efficiency measures',
                'potential_impact': 'Up to 15% reduction',
                'implementation_timeline': '6-12 months'
            },
            {
                'priority': 'Medium',
                'category': 'Technology',
                'recommendation': 'Consider renewable energy',
                'potential_impact': 'Up to 20% reduction',
                'implementation_timeline': '12-18 months'
            },
            {
                'priority': 'Low',
                'category': 'Monitoring',
                'recommendation': 'Enhanced monitoring systems',
                'potential_impact': 'Improved data accuracy',
                'implementation_timeline': '3-6 months'
            }
        ]

        return mock_gen

    @pytest.fixture
    def html_generator(self, mock_report_generator):
        """Create HTMLReportGenerator instance for testing"""
        return HTMLReportGenerator(mock_report_generator)

    @pytest.mark.unit
    def test_initialization(self, mock_report_generator):
        """Test proper initialization of HTMLReportGenerator"""
        html_gen = HTMLReportGenerator(mock_report_generator)

        assert html_gen.report_gen == mock_report_generator

    @pytest.mark.unit
    @patch('html_report.plotly.io.to_html')
    def test_generate_all_charts_success(self, mock_to_html, html_generator):
        """Test successful chart generation for HTML"""
        mock_to_html.return_value = '<div>Mock Chart HTML</div>'

        charts = html_generator._generate_all_charts()

        assert isinstance(charts, dict)
        expected_chart_keys = [
            'scope_comparison', 'monthly_trend', 'sankey',
            'facility_breakdown', 'energy_consumption'
        ]

        for key in expected_chart_keys:
            if key in charts:
                assert charts[key] == '<div>Mock Chart HTML</div>'

        # Should have called chart generation methods
        html_generator.report_gen.create_scope_comparison_chart.assert_called_once()
        html_generator.report_gen.create_monthly_trend_chart.assert_called_once()
        html_generator.report_gen.create_sankey_diagram.assert_called_once()
        html_generator.report_gen.create_facility_breakdown_chart.assert_called_once()
        html_generator.report_gen.create_energy_consumption_chart.assert_called_once()

    @pytest.mark.unit
    @patch('html_report.plotly.io.to_html')
    def test_generate_all_charts_with_none_charts(self, mock_to_html, html_generator):
        """Test chart generation when some charts return None"""
        # Make some chart methods return None
        html_generator.report_gen.create_scope_comparison_chart.return_value = None
        html_generator.report_gen.create_sankey_diagram.return_value = None

        mock_to_html.return_value = '<div>Mock Chart HTML</div>'

        charts = html_generator._generate_all_charts()

        assert isinstance(charts, dict)

        # Should not contain charts that returned None
        assert 'scope_comparison' not in charts or charts['scope_comparison'] is None
        assert 'sankey' not in charts or charts['sankey'] is None

        # Should contain charts that were successful
        if html_generator.report_gen.create_monthly_trend_chart.return_value:
            assert 'monthly_trend' in charts

    @pytest.mark.unit
    @patch('html_report.plotly.io.to_html')
    def test_generate_all_charts_plotly_error(self, mock_to_html, html_generator):
        """Test chart generation when Plotly conversion fails"""
        mock_to_html.side_effect = Exception("Plotly conversion failed")

        charts = html_generator._generate_all_charts()

        # Should handle errors gracefully
        assert isinstance(charts, dict)

    @pytest.mark.unit
    def test_create_html_template(self, html_generator):
        """Test HTML template creation"""
        template_html = html_generator._create_html_template()

        assert isinstance(template_html, str)
        assert len(template_html) > 0

        # Check that template contains expected sections
        assert '<!DOCTYPE html>' in template_html
        assert '<html' in template_html
        assert '<head>' in template_html
        assert '<body>' in template_html
        assert '</html>' in template_html

        # Check for key sections
        assert 'Executive Overview' in template_html
        assert 'Scope-wise Emission Analysis' in template_html
        assert 'Facility Performance Analysis' in template_html
        assert 'Energy Consumption' in template_html
        assert 'Strategic Recommendations' in template_html
        assert 'Methodology' in template_html

        # Check for CSS styling
        assert '<style>' in template_html
        assert '</style>' in template_html

        # Check for JavaScript
        assert '<script>' in template_html
        assert '</script>' in template_html

    @pytest.mark.unit
    def test_html_template_jinja_syntax(self, html_generator):
        """Test that HTML template contains valid Jinja2 syntax"""
        template_html = html_generator._create_html_template()

        # Should contain Jinja2 template variables
        assert '{{' in template_html and '}}' in template_html
        assert '{%' in template_html and '%}' in template_html

        # Check for expected template variables
        assert '{{ report_date }}' in template_html
        assert '{{ summary_stats.total_emissions }}' in template_html
        assert '{{ charts.scope_comparison | safe }}' in template_html

        # Test that it's valid Jinja2 template
        try:
            template = Template(template_html)
            # Should not raise exception
        except Exception as e:
            pytest.fail(f"Invalid Jinja2 template: {e}")

    @pytest.mark.unit
    @patch('html_report.plotly.io.to_html')
    @patch('builtins.open', create=True)
    def test_generate_html_report_success(self, mock_open, mock_to_html, html_generator, temp_output_dir):
        """Test successful HTML report generation"""
        mock_to_html.return_value = '<div>Mock Chart HTML</div>'

        # Mock file writing
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        output_path = temp_output_dir / 'test_report.html'
        result = html_generator.generate_html_report(str(output_path))

        assert result is True
        mock_open.assert_called_once_with(str(output_path), 'w', encoding='utf-8')
        mock_file.write.assert_called_once()

    @pytest.mark.unit
    @patch('html_report.plotly.io.to_html')
    @patch('builtins.open', create=True)
    def test_generate_html_report_file_error(self, mock_open, mock_to_html, html_generator, temp_output_dir):
        """Test HTML report generation with file writing error"""
        mock_to_html.return_value = '<div>Mock Chart HTML</div>'
        mock_open.side_effect = IOError("Cannot write file")

        output_path = temp_output_dir / 'test_report.html'
        result = html_generator.generate_html_report(str(output_path))

        assert result is False

    @pytest.mark.unit
    @patch('html_report.plotly.io.to_html')
    @patch('builtins.open', create=True)
    def test_generate_html_report_template_error(self, mock_open, mock_to_html, html_generator, temp_output_dir):
        """Test HTML report generation with template rendering error"""
        mock_to_html.return_value = '<div>Mock Chart HTML</div>'

        # Mock template rendering to fail
        with patch('html_report.Template') as mock_template:
            mock_template.side_effect = Exception("Template error")

            output_path = temp_output_dir / 'test_report.html'
            result = html_generator.generate_html_report(str(output_path))

            assert result is False

    @pytest.mark.unit
    def test_html_template_responsive_design(self, html_generator):
        """Test that HTML template includes responsive design elements"""
        template_html = html_generator._create_html_template()

        # Check for responsive design elements
        assert 'viewport' in template_html
        assert 'width=device-width' in template_html
        assert '@media' in template_html
        assert 'flex' in template_html or 'grid' in template_html

    @pytest.mark.unit
    def test_html_template_accessibility(self, html_generator):
        """Test that HTML template includes accessibility features"""
        template_html = html_generator._create_html_template()

        # Check for accessibility features
        assert 'alt=' in template_html or 'aria-' in template_html
        assert 'lang=' in template_html

    @pytest.mark.unit
    def test_html_template_navigation(self, html_generator):
        """Test that HTML template includes proper navigation"""
        template_html = html_generator._create_html_template()

        # Check for navigation elements
        assert '<nav' in template_html
        assert 'href="#' in template_html
        assert 'scroll' in template_html  # For smooth scrolling

    @pytest.mark.unit
    def test_html_template_chart_containers(self, html_generator):
        """Test that HTML template includes proper chart containers"""
        template_html = html_generator._create_html_template()

        # Check for chart container divs
        assert 'chart-container' in template_html
        assert 'charts.scope_comparison' in template_html
        assert 'charts.monthly_trend' in template_html
        assert 'charts.sankey' in template_html
        assert 'charts.facility_breakdown' in template_html
        assert 'charts.energy_consumption' in template_html

    @pytest.mark.unit
    def test_html_template_kpi_cards(self, html_generator):
        """Test that HTML template includes KPI cards"""
        template_html = html_generator._create_html_template()

        # Check for KPI card elements
        assert 'kpi-card' in template_html
        assert 'total_emissions' in template_html
        assert 'scope1_total' in template_html
        assert 'scope2_total' in template_html
        assert 'scope3_total' in template_html
        assert 'carbon_intensity' in template_html

    @pytest.mark.unit
    def test_html_template_recommendations(self, html_generator):
        """Test that HTML template includes recommendations section"""
        template_html = html_generator._create_html_template()

        # Check for recommendations elements
        assert 'recommendation-card' in template_html
        assert 'priority' in template_html
        assert 'for rec in recommendations' in template_html
        assert 'rec.category' in template_html
        assert 'rec.recommendation' in template_html

    @pytest.mark.integration
    @patch('html_report.plotly.io.to_html')
    def test_full_html_generation_with_real_data(self, mock_to_html, temp_output_dir, valid_excel_file):
        """Test full HTML generation with real data"""
        mock_to_html.return_value = '<div>Real Chart HTML</div>'

        report_gen = GHGReportGenerator(str(valid_excel_file))
        html_gen = HTMLReportGenerator(report_gen)

        output_path = temp_output_dir / 'full_test_report.html'
        result = html_gen.generate_html_report(str(output_path))

        assert result is True
        assert output_path.exists()

        # Check file content
        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()
            assert '<!DOCTYPE html>' in content
            assert 'GHG Emissions Report' in content

    @pytest.mark.error_handling
    def test_generate_html_with_missing_data(self, html_generator, temp_output_dir):
        """Test HTML generation with missing data"""
        # Set report generator data to None
        html_generator.report_gen.data = None
        html_generator.report_gen.get_summary_statistics.return_value = {}
        html_generator.report_gen.generate_recommendations.return_value = []

        with patch('html_report.plotly.io.to_html') as mock_to_html:
            with patch('builtins.open', create=True) as mock_open:
                mock_to_html.return_value = '<div>Empty Chart HTML</div>'
                mock_file = MagicMock()
                mock_open.return_value.__enter__.return_value = mock_file

                output_path = temp_output_dir / 'missing_data_report.html'
                result = html_generator.generate_html_report(str(output_path))

                # Should still succeed with empty/default data
                assert result is True

    @pytest.mark.error_handling
    def test_generate_html_with_chart_failures(self, html_generator, temp_output_dir):
        """Test HTML generation when all charts fail"""
        # Make all chart methods return None
        html_generator.report_gen.create_scope_comparison_chart.return_value = None
        html_generator.report_gen.create_monthly_trend_chart.return_value = None
        html_generator.report_gen.create_sankey_diagram.return_value = None
        html_generator.report_gen.create_facility_breakdown_chart.return_value = None
        html_generator.report_gen.create_energy_consumption_chart.return_value = None

        with patch('builtins.open', create=True) as mock_open:
            mock_file = MagicMock()
            mock_open.return_value.__enter__.return_value = mock_file

            output_path = temp_output_dir / 'no_charts_report.html'
            result = html_generator.generate_html_report(str(output_path))

            # Should still succeed without charts
            assert result is True

    @pytest.mark.performance
    @patch('html_report.plotly.io.to_html')
    @patch('builtins.open', create=True)
    def test_html_generation_performance(self, mock_open, mock_to_html, html_generator, temp_output_dir):
        """Test HTML generation performance"""
        import time

        mock_to_html.return_value = '<div>Performance Chart HTML</div>'
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        output_path = temp_output_dir / 'performance_test.html'

        start_time = time.time()
        result = html_generator.generate_html_report(str(output_path))
        end_time = time.time()

        generation_time = end_time - start_time

        assert result is True
        assert generation_time < 15.0, f"HTML generation took {generation_time:.2f}s, expected < 15.0s"

    @pytest.mark.unit
    def test_chart_div_ids(self, html_generator):
        """Test that charts have proper div IDs"""
        with patch('html_report.plotly.io.to_html') as mock_to_html:
            mock_to_html.return_value = '<div>Chart HTML</div>'

            html_generator._generate_all_charts()

            # Check that to_html was called with proper div_id parameters
            calls = mock_to_html.call_args_list
            expected_div_ids = [
                'scope-comparison-chart',
                'monthly-trend-chart',
                'sankey-chart',
                'facility-chart',
                'energy-chart'
            ]

            called_div_ids = []
            for call in calls:
                if 'div_id' in call[1]:
                    called_div_ids.append(call[1]['div_id'])

            # At least some of the expected div IDs should be used
            assert any(div_id in called_div_ids for div_id in expected_div_ids)

    @pytest.mark.unit
    def test_plotly_js_inclusion(self, html_generator):
        """Test that Plotly.js is properly included"""
        template_html = html_generator._create_html_template()

        # Should include Plotly.js from CDN
        assert 'plotly' in template_html.lower()
        assert 'cdn' in template_html.lower() or 'script' in template_html.lower()

    @pytest.mark.unit
    def test_css_styling_completeness(self, html_generator):
        """Test that CSS styling is comprehensive"""
        template_html = html_generator._create_html_template()

        # Check for key CSS classes
        css_classes = [
            'container', 'header', 'nav', 'content', 'section',
            'kpi-grid', 'kpi-card', 'chart-container', 'recommendations',
            'recommendation-card', 'footer'
        ]

        for css_class in css_classes:
            assert f'.{css_class}' in template_html or f'class="{css_class}"' in template_html

    @pytest.mark.unit
    def test_javascript_functionality(self, html_generator):
        """Test that JavaScript functionality is included"""
        template_html = html_generator._create_html_template()

        # Check for JavaScript features
        js_features = [
            'addEventListener', 'scrollIntoView', 'smooth',
            'pageYOffset', 'scrollTo'
        ]

        for feature in js_features:
            assert feature in template_html

    @pytest.mark.unit
    def test_template_variable_formatting(self, html_generator):
        """Test that template variables are properly formatted"""
        template_html = html_generator._create_html_template()

        # Check for number formatting
        assert '"{:,.0f}".format' in template_html
        assert '"{:.1f}".format' in template_html
        assert '"{:.4f}".format' in template_html

    @pytest.mark.unit
    def test_recommendation_priority_styling(self, html_generator):
        """Test that recommendation priority styling is implemented"""
        template_html = html_generator._create_html_template()

        # Check for priority-based styling
        assert 'high-priority' in template_html
        assert 'medium-priority' in template_html
        assert 'low-priority' in template_html

        # Check for priority color coding
        assert '#e74c3c' in template_html  # Red for high
        assert '#f39c12' in template_html  # Orange for medium
        assert '#27ae60' in template_html  # Green for low

    @pytest.mark.unit
    def test_font_awesome_icons(self, html_generator):
        """Test that Font Awesome icons are properly included"""
        template_html = html_generator._create_html_template()

        # Check for Font Awesome inclusion
        assert 'font-awesome' in template_html
        assert 'fas fa-' in template_html

        # Check for specific icons
        icons = ['fa-leaf', 'fa-chart-line', 'fa-industry', 'fa-bolt', 'fa-lightbulb']
        for icon in icons:
            assert icon in template_html

    @pytest.mark.error_handling
    def test_invalid_template_data(self, html_generator, temp_output_dir):
        """Test handling of invalid template data"""
        # Provide invalid data to template
        html_generator.report_gen.get_summary_statistics.return_value = None

        with patch('builtins.open', create=True) as mock_open:
            mock_file = MagicMock()
            mock_open.return_value.__enter__.return_value = mock_file

            output_path = temp_output_dir / 'invalid_data_report.html'

            # Should handle None data gracefully
            try:
                result = html_generator.generate_html_report(str(output_path))
                # Should either succeed with default values or fail gracefully
                assert isinstance(result, bool)
            except Exception as e:
                # If it fails, it should be a handled exception
                assert "template" in str(e).lower() or "data" in str(e).lower()

if __name__ == "__main__":
    pytest.main([__file__, "-v"])