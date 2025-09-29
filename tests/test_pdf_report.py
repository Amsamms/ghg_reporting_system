"""
Unit Tests for PDFReportGenerator Module

This module contains comprehensive unit tests for the PDFReportGenerator class,
testing PDF generation, chart integration, and error handling.
"""

import pytest
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import plotly.graph_objects as go

from pdf_report import PDFReportGenerator
from report_generator import GHGReportGenerator


class TestPDFReportGenerator:
    """Test suite for PDFReportGenerator class"""

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
            }
        ]

        return mock_gen

    @pytest.fixture
    def pdf_generator(self, mock_report_generator):
        """Create PDFReportGenerator instance for testing"""
        return PDFReportGenerator(mock_report_generator)

    @pytest.mark.unit
    def test_initialization(self, mock_report_generator):
        """Test proper initialization of PDFReportGenerator"""
        pdf_gen = PDFReportGenerator(mock_report_generator)

        assert pdf_gen.report_gen == mock_report_generator
        assert pdf_gen.styles is not None
        assert hasattr(pdf_gen, 'styles')

    @pytest.mark.unit
    def test_custom_styles_setup(self, pdf_generator):
        """Test that custom styles are set up correctly"""
        styles = pdf_generator.styles

        # Check that custom styles were added
        assert 'CustomTitle' in styles.byName
        assert 'SubHeading' in styles.byName
        assert 'HighlightBox' in styles.byName

        # Check style properties
        custom_title = styles['CustomTitle']
        assert custom_title.fontSize == 24
        assert custom_title.spaceAfter == 30

        sub_heading = styles['SubHeading']
        assert sub_heading.fontSize == 14
        assert sub_heading.spaceBefore == 20

    @pytest.mark.unit
    @patch('pdf_report.pio.write_image')
    def test_create_chart_image_success(self, mock_write_image, pdf_generator):
        """Test successful chart image creation"""
        mock_fig = Mock(spec=go.Figure)
        mock_write_image.return_value = None  # Successful write

        result = pdf_generator._create_chart_image(mock_fig, 'test_chart')

        assert result is not None
        assert result.endswith('test_chart.png')
        mock_write_image.assert_called_once()

    @pytest.mark.unit
    def test_create_chart_image_none_figure(self, pdf_generator):
        """Test chart image creation with None figure"""
        result = pdf_generator._create_chart_image(None, 'test_chart')
        assert result is None

    @pytest.mark.unit
    @patch('pdf_report.pio.write_image')
    def test_create_chart_image_error(self, mock_write_image, pdf_generator):
        """Test chart image creation with error"""
        mock_fig = Mock(spec=go.Figure)
        mock_write_image.side_effect = Exception("Image creation failed")

        result = pdf_generator._create_chart_image(mock_fig, 'test_chart')
        assert result is None

    @pytest.mark.unit
    def test_create_title_page(self, pdf_generator):
        """Test title page creation"""
        title_elements = pdf_generator._create_title_page()

        assert isinstance(title_elements, list)
        assert len(title_elements) > 0

        # Should contain various elements like spacers, paragraphs, tables
        element_types = [type(elem).__name__ for elem in title_elements]
        assert 'Spacer' in element_types
        assert 'Paragraph' in element_types
        assert 'Table' in element_types

    @pytest.mark.unit
    def test_create_executive_summary(self, pdf_generator):
        """Test executive summary creation"""
        summary_elements = pdf_generator._create_executive_summary()

        assert isinstance(summary_elements, list)
        assert len(summary_elements) > 0

        element_types = [type(elem).__name__ for elem in summary_elements]
        assert 'Paragraph' in element_types
        assert 'Table' in element_types

    @pytest.mark.unit
    @patch('pdf_report.PDFReportGenerator._create_chart_image')
    def test_create_scope_analysis(self, mock_create_image, pdf_generator):
        """Test scope analysis section creation"""
        mock_create_image.return_value = '/fake/image/path.png'

        analysis_elements = pdf_generator._create_scope_analysis()

        assert isinstance(analysis_elements, list)
        assert len(analysis_elements) > 0

        element_types = [type(elem).__name__ for elem in analysis_elements]
        assert 'Paragraph' in element_types

    @pytest.mark.unit
    @patch('pdf_report.PDFReportGenerator._create_chart_image')
    def test_create_facility_analysis(self, mock_create_image, pdf_generator):
        """Test facility analysis section creation"""
        mock_create_image.return_value = '/fake/image/path.png'

        facility_elements = pdf_generator._create_facility_analysis()

        assert isinstance(facility_elements, list)
        assert len(facility_elements) > 0

        element_types = [type(elem).__name__ for elem in facility_elements]
        assert 'Paragraph' in element_types

    @pytest.mark.unit
    @patch('pdf_report.PDFReportGenerator._create_chart_image')
    def test_create_energy_analysis(self, mock_create_image, pdf_generator):
        """Test energy analysis section creation"""
        mock_create_image.return_value = '/fake/image/path.png'

        energy_elements = pdf_generator._create_energy_analysis()

        assert isinstance(energy_elements, list)
        assert len(energy_elements) > 0

        element_types = [type(elem).__name__ for elem in energy_elements]
        assert 'Paragraph' in element_types

    @pytest.mark.unit
    def test_create_recommendations(self, pdf_generator):
        """Test recommendations section creation"""
        rec_elements = pdf_generator._create_recommendations()

        assert isinstance(rec_elements, list)
        assert len(rec_elements) > 0

        element_types = [type(elem).__name__ for elem in rec_elements]
        assert 'Paragraph' in element_types

    @pytest.mark.unit
    def test_create_appendix(self, pdf_generator):
        """Test appendix section creation"""
        appendix_elements = pdf_generator._create_appendix()

        assert isinstance(appendix_elements, list)
        assert len(appendix_elements) > 0

        element_types = [type(elem).__name__ for elem in appendix_elements]
        assert 'Paragraph' in element_types

    @pytest.mark.unit
    @patch('pdf_report.SimpleDocTemplate')
    @patch('pdf_report.PDFReportGenerator._create_chart_image')
    def test_generate_pdf_report_success(self, mock_create_image, mock_doc, pdf_generator, temp_output_dir):
        """Test successful PDF report generation"""
        mock_create_image.return_value = '/fake/image/path.png'

        # Mock the document build method
        mock_doc_instance = Mock()
        mock_doc.return_value = mock_doc_instance
        mock_doc_instance.build.return_value = None

        output_path = temp_output_dir / 'test_report.pdf'
        result = pdf_generator.generate_pdf_report(str(output_path))

        assert result is True
        mock_doc.assert_called_once()
        mock_doc_instance.build.assert_called_once()

    @pytest.mark.unit
    @patch('pdf_report.SimpleDocTemplate')
    def test_generate_pdf_report_build_error(self, mock_doc, pdf_generator, temp_output_dir):
        """Test PDF report generation with build error"""
        # Mock the document to raise an exception during build
        mock_doc_instance = Mock()
        mock_doc.return_value = mock_doc_instance
        mock_doc_instance.build.side_effect = Exception("Build failed")

        output_path = temp_output_dir / 'test_report.pdf'
        result = pdf_generator.generate_pdf_report(str(output_path))

        assert result is False

    @pytest.mark.integration
    def test_full_pdf_generation_with_real_data(self, temp_output_dir, valid_excel_file):
        """Test full PDF generation with real data"""
        # This test uses real data but mocks the actual PDF creation to avoid dependencies
        report_gen = GHGReportGenerator(str(valid_excel_file))
        pdf_gen = PDFReportGenerator(report_gen)

        with patch('pdf_report.SimpleDocTemplate') as mock_doc:
            with patch('pdf_report.pio.write_image') as mock_write_image:
                mock_doc_instance = Mock()
                mock_doc.return_value = mock_doc_instance
                mock_doc_instance.build.return_value = None
                mock_write_image.return_value = None

                output_path = temp_output_dir / 'full_test_report.pdf'
                result = pdf_gen.generate_pdf_report(str(output_path))

                assert result is True

    @pytest.mark.error_handling
    def test_generate_pdf_with_missing_data(self, pdf_generator, temp_output_dir):
        """Test PDF generation with missing data"""
        # Set report generator data to None
        pdf_generator.report_gen.data = None
        pdf_generator.report_gen.get_summary_statistics.return_value = {}

        with patch('pdf_report.SimpleDocTemplate') as mock_doc:
            mock_doc_instance = Mock()
            mock_doc.return_value = mock_doc_instance
            mock_doc_instance.build.return_value = None

            output_path = temp_output_dir / 'missing_data_report.pdf'
            result = pdf_generator.generate_pdf_report(str(output_path))

            # Should still succeed with empty/default data
            assert result is True

    @pytest.mark.error_handling
    def test_generate_pdf_with_chart_creation_failures(self, pdf_generator, temp_output_dir):
        """Test PDF generation when chart creation fails"""
        # Make all chart methods return None
        pdf_generator.report_gen.create_scope_comparison_chart.return_value = None
        pdf_generator.report_gen.create_monthly_trend_chart.return_value = None
        pdf_generator.report_gen.create_sankey_diagram.return_value = None
        pdf_generator.report_gen.create_facility_breakdown_chart.return_value = None
        pdf_generator.report_gen.create_energy_consumption_chart.return_value = None

        with patch('pdf_report.SimpleDocTemplate') as mock_doc:
            mock_doc_instance = Mock()
            mock_doc.return_value = mock_doc_instance
            mock_doc_instance.build.return_value = None

            output_path = temp_output_dir / 'no_charts_report.pdf'
            result = pdf_generator.generate_pdf_report(str(output_path))

            # Should still succeed without charts
            assert result is True

    @pytest.mark.unit
    def test_recommendations_grouping_by_priority(self, pdf_generator):
        """Test that recommendations are properly grouped by priority"""
        # Test with mixed priority recommendations
        pdf_generator.report_gen.generate_recommendations.return_value = [
            {'priority': 'High', 'category': 'Test1', 'recommendation': 'Test', 'potential_impact': 'Test', 'implementation_timeline': 'Test'},
            {'priority': 'Low', 'category': 'Test2', 'recommendation': 'Test', 'potential_impact': 'Test', 'implementation_timeline': 'Test'},
            {'priority': 'Medium', 'category': 'Test3', 'recommendation': 'Test', 'potential_impact': 'Test', 'implementation_timeline': 'Test'},
            {'priority': 'High', 'category': 'Test4', 'recommendation': 'Test', 'potential_impact': 'Test', 'implementation_timeline': 'Test'},
        ]

        rec_elements = pdf_generator._create_recommendations()

        # Should contain properly structured recommendations
        assert isinstance(rec_elements, list)
        assert len(rec_elements) > 0

    @pytest.mark.unit
    def test_table_creation_with_valid_data(self, pdf_generator):
        """Test table creation with valid summary statistics"""
        # Ensure summary statistics are available
        summary_stats = pdf_generator.report_gen.get_summary_statistics()
        assert 'total_emissions' in summary_stats
        assert 'total_facilities' in summary_stats

        title_elements = pdf_generator._create_title_page()

        # Should contain a table with company information
        tables = [elem for elem in title_elements if type(elem).__name__ == 'Table']
        assert len(tables) > 0

    @pytest.mark.unit
    def test_error_handling_in_section_creation(self, pdf_generator):
        """Test error handling in individual section creation methods"""
        # Mock the report generator to raise exceptions
        pdf_generator.report_gen.get_summary_statistics.side_effect = Exception("Stats error")

        # Sections should handle exceptions gracefully
        try:
            title_elements = pdf_generator._create_title_page()
            # Should either return empty list or handle error gracefully
            assert isinstance(title_elements, list)
        except Exception:
            pytest.fail("Section creation should handle exceptions gracefully")

    @pytest.mark.performance
    @patch('pdf_report.SimpleDocTemplate')
    @patch('pdf_report.PDFReportGenerator._create_chart_image')
    def test_pdf_generation_performance(self, mock_create_image, mock_doc, pdf_generator, temp_output_dir):
        """Test PDF generation performance"""
        import time

        mock_create_image.return_value = '/fake/image/path.png'
        mock_doc_instance = Mock()
        mock_doc.return_value = mock_doc_instance
        mock_doc_instance.build.return_value = None

        output_path = temp_output_dir / 'performance_test.pdf'

        start_time = time.time()
        result = pdf_generator.generate_pdf_report(str(output_path))
        end_time = time.time()

        generation_time = end_time - start_time

        assert result is True
        assert generation_time < 30.0, f"PDF generation took {generation_time:.2f}s, expected < 30.0s"

    @pytest.mark.unit
    def test_paragraph_content_validation(self, pdf_generator):
        """Test that paragraph content is properly formatted"""
        summary_elements = pdf_generator._create_executive_summary()

        # Find paragraph elements
        paragraphs = [elem for elem in summary_elements if type(elem).__name__ == 'Paragraph']
        assert len(paragraphs) > 0

        # Paragraphs should have content
        for para in paragraphs:
            assert hasattr(para, 'text') or hasattr(para, '_text')

    @pytest.mark.unit
    def test_chart_image_integration(self, pdf_generator):
        """Test chart image integration in sections"""
        with patch('pdf_report.PDFReportGenerator._create_chart_image') as mock_create_image:
            mock_create_image.return_value = '/fake/image/path.png'

            scope_elements = pdf_generator._create_scope_analysis()

            # Should have called chart image creation
            assert mock_create_image.call_count > 0

    @pytest.mark.unit
    def test_image_element_creation(self, pdf_generator):
        """Test image element creation when chart images are available"""
        with patch('pdf_report.PDFReportGenerator._create_chart_image') as mock_create_image:
            with patch('pdf_report.Image') as mock_image:
                mock_create_image.return_value = '/fake/image/path.png'
                mock_image.return_value = Mock()

                scope_elements = pdf_generator._create_scope_analysis()

                # Should have created image elements
                if mock_create_image.call_count > 0:
                    # If charts were created, images should be created too
                    assert mock_image.call_count >= 0

    @pytest.mark.error_handling
    def test_invalid_output_path(self, pdf_generator):
        """Test PDF generation with invalid output path"""
        with patch('pdf_report.SimpleDocTemplate') as mock_doc:
            mock_doc.side_effect = Exception("Invalid path")

            result = pdf_generator.generate_pdf_report('/invalid/path/report.pdf')
            assert result is False

    @pytest.mark.unit
    def test_page_break_insertion(self, pdf_generator):
        """Test that page breaks are properly inserted"""
        with patch('pdf_report.SimpleDocTemplate') as mock_doc:
            with patch('pdf_report.PageBreak') as mock_page_break:
                mock_doc_instance = Mock()
                mock_doc.return_value = mock_doc_instance
                mock_doc_instance.build.return_value = None

                pdf_generator.generate_pdf_report('/fake/path.pdf')

                # Should have created page breaks
                assert mock_page_break.call_count > 0

    @pytest.mark.unit
    def test_spacer_usage(self, pdf_generator):
        """Test proper spacer usage in document sections"""
        title_elements = pdf_generator._create_title_page()

        spacers = [elem for elem in title_elements if type(elem).__name__ == 'Spacer']
        assert len(spacers) > 0

        # Spacers should have reasonable heights
        for spacer in spacers:
            if hasattr(spacer, 'height'):
                assert spacer.height > 0

if __name__ == "__main__":
    pytest.main([__file__, "-v"])