"""
Integration Tests for GHG Reporting System

This module contains comprehensive integration tests that verify
the complete workflow from Excel generation to report creation.
"""

import pytest
import os
import tempfile
from pathlib import Path
import pandas as pd
from datetime import datetime
import time

from excel_generator import GHGExcelGenerator
from report_generator import GHGReportGenerator
from pdf_report import PDFReportGenerator
from html_report import HTMLReportGenerator


class TestGHGSystemIntegration:
    """Integration test suite for the complete GHG reporting system"""

    @pytest.fixture(scope="class")
    def temp_workspace(self):
        """Create temporary workspace for integration tests"""
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            yield workspace

    @pytest.fixture
    def excel_generator(self):
        """Create Excel generator for integration tests"""
        return GHGExcelGenerator()

    @pytest.mark.integration
    def test_complete_workflow_excel_to_reports(self, excel_generator, temp_workspace):
        """Test complete workflow from Excel generation to report creation"""
        # Step 1: Generate Excel template
        excel_file = temp_workspace / 'integration_test.xlsx'
        result_file = excel_generator.create_excel_template(str(excel_file))

        assert result_file == str(excel_file)
        assert excel_file.exists()
        assert excel_file.stat().st_size > 0

        # Step 2: Load data with report generator
        report_gen = GHGReportGenerator(str(excel_file))

        assert report_gen.data is not None
        assert isinstance(report_gen.data, dict)
        assert len(report_gen.data) > 0

        # Step 3: Generate summary statistics
        stats = report_gen.get_summary_statistics()

        assert isinstance(stats, dict)
        assert 'total_emissions' in stats
        assert stats['total_emissions'] > 0

        # Step 4: Generate charts
        scope_chart = report_gen.create_scope_comparison_chart()
        trend_chart = report_gen.create_monthly_trend_chart()
        sankey_chart = report_gen.create_sankey_diagram()
        facility_chart = report_gen.create_facility_breakdown_chart()
        energy_chart = report_gen.create_energy_consumption_chart()

        # At least some charts should be created
        charts_created = sum(1 for chart in [scope_chart, trend_chart, sankey_chart, facility_chart, energy_chart] if chart is not None)
        assert charts_created >= 3, f"Only {charts_created} charts created, expected at least 3"

        # Step 5: Generate recommendations
        recommendations = report_gen.generate_recommendations()

        assert isinstance(recommendations, list)
        assert len(recommendations) > 0

        # Step 6: Generate PDF report
        pdf_gen = PDFReportGenerator(report_gen)
        pdf_file = temp_workspace / 'integration_report.pdf'

        # Mock PDF generation to avoid external dependencies
        with pytest.mock.patch('pdf_report.SimpleDocTemplate') as mock_doc:
            with pytest.mock.patch('pdf_report.pio.write_image') as mock_write:
                mock_doc_instance = pytest.mock.Mock()
                mock_doc.return_value = mock_doc_instance
                mock_doc_instance.build.return_value = None
                mock_write.return_value = None

                pdf_success = pdf_gen.generate_pdf_report(str(pdf_file))
                assert pdf_success is True

        # Step 7: Generate HTML report
        html_gen = HTMLReportGenerator(report_gen)
        html_file = temp_workspace / 'integration_report.html'

        html_success = html_gen.generate_html_report(str(html_file))

        assert html_success is True
        assert html_file.exists()

        # Verify HTML content
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
            assert '<!DOCTYPE html>' in html_content
            assert 'GHG Emissions Report' in html_content
            assert str(int(stats['total_emissions'])) in html_content

    @pytest.mark.integration
    def test_workflow_with_custom_data(self, temp_workspace):
        """Test workflow with custom Excel data"""
        # Create custom Excel file
        excel_file = temp_workspace / 'custom_test.xlsx'

        custom_scope1_data = [
            {
                'Source': 'Custom Source 1',
                'Annual_Total': 10000,
                'Percentage': 50,
                'Jan': 800, 'Feb': 850, 'Mar': 900, 'Apr': 920,
                'May': 950, 'Jun': 980, 'Jul': 1000, 'Aug': 1020,
                'Sep': 900, 'Oct': 850, 'Nov': 820, 'Dec': 800
            },
            {
                'Source': 'Custom Source 2',
                'Annual_Total': 10000,
                'Percentage': 50,
                'Jan': 800, 'Feb': 850, 'Mar': 900, 'Apr': 920,
                'May': 950, 'Jun': 980, 'Jul': 1000, 'Aug': 1020,
                'Sep': 900, 'Oct': 850, 'Nov': 820, 'Dec': 800
            }
        ]

        custom_scope2_data = [
            {
                'Source': 'Custom Electricity',
                'Annual_Total': 5000,
                'Percentage': 100,
                'Jan': 400, 'Feb': 420, 'Mar': 450, 'Apr': 460,
                'May': 470, 'Jun': 480, 'Jul': 500, 'Aug': 510,
                'Sep': 450, 'Oct': 420, 'Nov': 410, 'Dec': 400
            }
        ]

        custom_scope3_data = [
            {
                'Source': 'Custom Transport',
                'Annual_Total': 3000,
                'Percentage': 100,
                'Jan': 240, 'Feb': 250, 'Mar': 270, 'Apr': 280,
                'May': 290, 'Jun': 300, 'Jul': 310, 'Aug': 320,
                'Sep': 270, 'Oct': 250, 'Nov': 240, 'Dec': 230
            }
        ]

        # Create Excel file with custom data
        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            pd.DataFrame(custom_scope1_data).to_excel(writer, sheet_name='Scope 1 Emissions', index=False)
            pd.DataFrame(custom_scope2_data).to_excel(writer, sheet_name='Scope 2 Emissions', index=False)
            pd.DataFrame(custom_scope3_data).to_excel(writer, sheet_name='Scope 3 Emissions', index=False)

            # Add facility data
            facility_data = [
                {'Facility': 'Test Facility', 'Scope_1': 20000, 'Scope_2': 5000, 'Scope_3': 3000,
                 'Energy_Intensity': 5.0, 'Production': 100000}
            ]
            pd.DataFrame(facility_data).to_excel(writer, sheet_name='Facility Breakdown', index=False)

        # Test workflow with custom data
        report_gen = GHGReportGenerator(str(excel_file))

        assert report_gen.data is not None

        # Verify data was loaded correctly
        assert 'Scope 1 Emissions' in report_gen.data
        assert len(report_gen.data['Scope 1 Emissions']) == 2
        assert report_gen.data['Scope 1 Emissions']['Source'].iloc[0] == 'Custom Source 1'

        # Generate statistics
        stats = report_gen.get_summary_statistics()
        expected_total = 20000 + 5000 + 3000  # Sum of all scopes
        assert abs(stats['total_emissions'] - expected_total) < 1

        # Generate reports
        html_gen = HTMLReportGenerator(report_gen)
        html_file = temp_workspace / 'custom_report.html'

        success = html_gen.generate_html_report(str(html_file))
        assert success is True

    @pytest.mark.integration
    def test_workflow_with_missing_sheets(self, temp_workspace):
        """Test workflow with incomplete Excel data"""
        excel_file = temp_workspace / 'incomplete_test.xlsx'

        # Create Excel with only Scope 1 data
        scope1_data = [
            {
                'Source': 'Only Source',
                'Annual_Total': 15000,
                'Percentage': 100,
                'Jan': 1200, 'Feb': 1250, 'Mar': 1300, 'Apr': 1320,
                'May': 1350, 'Jun': 1380, 'Jul': 1400, 'Aug': 1420,
                'Sep': 1300, 'Oct': 1250, 'Nov': 1220, 'Dec': 1200
            }
        ]

        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            pd.DataFrame(scope1_data).to_excel(writer, sheet_name='Scope 1 Emissions', index=False)

        # Should handle missing sheets gracefully
        report_gen = GHGReportGenerator(str(excel_file))

        assert report_gen.data is not None
        assert 'Scope 1 Emissions' in report_gen.data

        # Generate statistics (should handle missing scopes)
        stats = report_gen.get_summary_statistics()
        assert stats['scope1_total'] == 15000
        assert stats['scope2_total'] == 0
        assert stats['scope3_total'] == 0

        # Charts should handle missing data gracefully
        scope_chart = report_gen.create_scope_comparison_chart()
        assert scope_chart is not None  # Should still create chart with available data

    @pytest.mark.integration
    def test_performance_full_workflow(self, excel_generator, temp_workspace):
        """Test performance of complete workflow"""
        start_time = time.time()

        # Generate Excel
        excel_file = temp_workspace / 'performance_test.xlsx'
        excel_generator.create_excel_template(str(excel_file))

        # Load and process data
        report_gen = GHGReportGenerator(str(excel_file))
        stats = report_gen.get_summary_statistics()
        recommendations = report_gen.generate_recommendations()

        # Generate all charts
        charts = [
            report_gen.create_scope_comparison_chart(),
            report_gen.create_monthly_trend_chart(),
            report_gen.create_sankey_diagram(),
            report_gen.create_facility_breakdown_chart(),
            report_gen.create_energy_consumption_chart()
        ]

        # Generate HTML report
        html_gen = HTMLReportGenerator(report_gen)
        html_file = temp_workspace / 'performance_report.html'
        html_gen.generate_html_report(str(html_file))

        end_time = time.time()
        total_time = end_time - start_time

        # Complete workflow should finish within reasonable time
        assert total_time < 60.0, f"Complete workflow took {total_time:.2f}s, expected < 60.0s"

        # Verify all components worked
        assert excel_file.exists()
        assert html_file.exists()
        assert stats['total_emissions'] > 0
        assert len(recommendations) > 0
        assert any(chart is not None for chart in charts)

    @pytest.mark.integration
    def test_data_consistency_across_modules(self, excel_generator, temp_workspace):
        """Test data consistency across different modules"""
        # Generate Excel data
        excel_file = temp_workspace / 'consistency_test.xlsx'
        excel_generator.create_excel_template(str(excel_file))

        # Load data and verify consistency
        report_gen = GHGReportGenerator(str(excel_file))

        # Get raw data from Excel
        excel_data = pd.read_excel(excel_file, sheet_name=None)

        # Compare with processed data
        scope1_excel = excel_data['Scope 1 Emissions']
        scope1_processed = report_gen.data['Scope 1 Emissions']

        # Data should be consistent
        assert len(scope1_excel) == len(scope1_processed)
        assert list(scope1_excel.columns) == list(scope1_processed.columns)

        # Totals should match
        excel_total = scope1_excel['Annual_Total'].sum()
        processed_total = scope1_processed['Annual_Total'].sum()
        assert abs(excel_total - processed_total) < 0.01

        # Summary statistics should be consistent with raw data
        stats = report_gen.get_summary_statistics()
        scope1_total_from_stats = stats['scope1_total']
        assert abs(excel_total - scope1_total_from_stats) < 0.01

    @pytest.mark.integration
    def test_error_recovery_workflow(self, temp_workspace):
        """Test workflow error recovery capabilities"""
        # Create invalid Excel file
        invalid_file = temp_workspace / 'invalid_test.xlsx'

        # Create Excel with wrong column names
        bad_data = pd.DataFrame({
            'Wrong_Column': [1, 2, 3],
            'Another_Wrong': ['a', 'b', 'c']
        })

        with pd.ExcelWriter(invalid_file, engine='openpyxl') as writer:
            bad_data.to_excel(writer, sheet_name='Scope 1 Emissions', index=False)

        # System should handle invalid data gracefully
        report_gen = GHGReportGenerator(str(invalid_file))

        # Should not crash, might return empty/default data
        stats = report_gen.get_summary_statistics()
        assert isinstance(stats, dict)

        # Charts should handle invalid data
        scope_chart = report_gen.create_scope_comparison_chart()
        # Should either return None or handle gracefully

        # Report generation should not crash
        html_gen = HTMLReportGenerator(report_gen)
        html_file = temp_workspace / 'error_recovery_report.html'

        try:
            success = html_gen.generate_html_report(str(html_file))
            # Should either succeed with default data or fail gracefully
            assert isinstance(success, bool)
        except Exception as e:
            # If it fails, it should be a handled exception
            assert "template" in str(e).lower() or "data" in str(e).lower()

    @pytest.mark.integration
    def test_concurrent_workflow_execution(self, excel_generator, temp_workspace):
        """Test concurrent execution of workflow components"""
        import threading
        import concurrent.futures

        # Generate Excel file
        excel_file = temp_workspace / 'concurrent_test.xlsx'
        excel_generator.create_excel_template(str(excel_file))

        # Load data
        report_gen = GHGReportGenerator(str(excel_file))

        def generate_chart(chart_method):
            """Generate a chart safely"""
            try:
                return getattr(report_gen, chart_method)()
            except Exception as e:
                return None

        # Test concurrent chart generation
        chart_methods = [
            'create_scope_comparison_chart',
            'create_monthly_trend_chart',
            'create_sankey_diagram',
            'create_facility_breakdown_chart',
            'create_energy_consumption_chart'
        ]

        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            future_to_chart = {
                executor.submit(generate_chart, method): method
                for method in chart_methods
            }

            results = {}
            for future in concurrent.futures.as_completed(future_to_chart):
                method = future_to_chart[future]
                try:
                    result = future.result(timeout=30)
                    results[method] = result
                except Exception as e:
                    results[method] = None

        # At least some charts should be generated successfully
        successful_charts = sum(1 for result in results.values() if result is not None)
        assert successful_charts >= 2, f"Only {successful_charts} charts generated concurrently"

    @pytest.mark.integration
    def test_large_dataset_workflow(self, temp_workspace):
        """Test workflow with large dataset"""
        excel_file = temp_workspace / 'large_dataset_test.xlsx'

        # Generate large dataset
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

        # Create large Scope 1 data (50 sources)
        large_scope1_data = []
        for i in range(50):
            monthly_values = [1000 + i * 10 + j * 5 for j in range(12)]
            large_scope1_data.append({
                'Source': f'Large Source {i+1}',
                'Annual_Total': sum(monthly_values),
                'Percentage': 2.0,  # Will be recalculated
                **dict(zip(months, monthly_values))
            })

        # Create corresponding facility data
        large_facility_data = []
        for i in range(20):
            large_facility_data.append({
                'Facility': f'Large Facility {i+1}',
                'Scope_1': 10000 + i * 500,
                'Scope_2': 5000 + i * 200,
                'Scope_3': 3000 + i * 100,
                'Energy_Intensity': 3.0 + i * 0.1,
                'Production': 100000 + i * 5000
            })

        # Create Excel file
        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            pd.DataFrame(large_scope1_data).to_excel(writer, sheet_name='Scope 1 Emissions', index=False)
            pd.DataFrame([{'Source': 'Large Electricity', 'Annual_Total': 50000}]).to_excel(writer, sheet_name='Scope 2 Emissions', index=False)
            pd.DataFrame([{'Source': 'Large Transport', 'Annual_Total': 30000}]).to_excel(writer, sheet_name='Scope 3 Emissions', index=False)
            pd.DataFrame(large_facility_data).to_excel(writer, sheet_name='Facility Breakdown', index=False)

        # Test workflow with large dataset
        start_time = time.time()

        report_gen = GHGReportGenerator(str(excel_file))
        assert report_gen.data is not None

        # Verify large dataset was loaded
        assert len(report_gen.data['Scope 1 Emissions']) == 50
        assert len(report_gen.data['Facility Breakdown']) == 20

        # Generate statistics
        stats = report_gen.get_summary_statistics()
        assert stats['total_emissions'] > 100000  # Should be large

        # Generate charts (should handle large data)
        scope_chart = report_gen.create_scope_comparison_chart()
        facility_chart = report_gen.create_facility_breakdown_chart()

        # Generate report
        html_gen = HTMLReportGenerator(report_gen)
        html_file = temp_workspace / 'large_dataset_report.html'
        success = html_gen.generate_html_report(str(html_file))

        end_time = time.time()
        processing_time = end_time - start_time

        # Should complete within reasonable time even with large dataset
        assert processing_time < 120.0, f"Large dataset processing took {processing_time:.2f}s, expected < 120.0s"
        assert success is True
        assert html_file.exists()

    @pytest.mark.integration
    def test_report_content_accuracy(self, excel_generator, temp_workspace):
        """Test accuracy of generated report content"""
        # Generate Excel with known data
        excel_file = temp_workspace / 'accuracy_test.xlsx'
        excel_generator.create_excel_template(str(excel_file))

        # Load and process
        report_gen = GHGReportGenerator(str(excel_file))
        stats = report_gen.get_summary_statistics()

        # Generate HTML report
        html_gen = HTMLReportGenerator(report_gen)
        html_file = temp_workspace / 'accuracy_report.html'
        html_gen.generate_html_report(str(html_file))

        # Verify report content accuracy
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()

        # Check that statistics are properly reflected in HTML
        assert str(int(stats['total_emissions'])) in html_content
        assert str(int(stats['scope1_total'])) in html_content
        assert str(int(stats['scope2_total'])) in html_content
        assert str(int(stats['scope3_total'])) in html_content

        # Check that percentages are reasonable
        assert f"{stats['scope1_pct']:.1f}" in html_content

        # Check for report generation date
        current_year = datetime.now().year
        assert str(current_year) in html_content

if __name__ == "__main__":
    pytest.main([__file__, "-v"])