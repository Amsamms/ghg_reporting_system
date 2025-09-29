"""
Performance Tests for GHG Reporting System

This module contains comprehensive performance tests to ensure
the system handles large datasets and operates efficiently.
"""

import pytest
import time
import tempfile
import pandas as pd
import numpy as np
from pathlib import Path
import threading
import concurrent.futures
import psutil
import os

from excel_generator import GHGExcelGenerator
from report_generator import GHGReportGenerator
from html_report import HTMLReportGenerator


class TestPerformance:
    """Performance test suite for the GHG reporting system"""

    @pytest.fixture
    def large_excel_generator(self):
        """Create Excel generator for performance testing"""
        return GHGExcelGenerator()

    @pytest.mark.performance
    def test_excel_generation_performance(self, large_excel_generator, temp_output_dir):
        """Test Excel generation performance"""
        start_time = time.time()

        excel_file = temp_output_dir / 'performance_excel.xlsx'
        result = large_excel_generator.create_excel_template(str(excel_file))

        end_time = time.time()
        generation_time = end_time - start_time

        assert result == str(excel_file)
        assert excel_file.exists()
        assert generation_time < 30.0, f"Excel generation took {generation_time:.2f}s, expected < 30.0s"

    @pytest.mark.performance
    def test_large_dataset_processing(self, temp_output_dir):
        """Test processing of large datasets"""
        # Create large dataset (1000 emission sources)
        excel_file = temp_output_dir / 'large_performance_test.xlsx'

        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

        # Generate 1000 Scope 1 sources
        large_scope1_data = []
        for i in range(1000):
            monthly_values = [np.random.uniform(100, 500) for _ in months]
            large_scope1_data.append({
                'Source': f'Large Performance Source {i+1}',
                'Annual_Total': sum(monthly_values),
                'Percentage': 0.1,
                **dict(zip(months, monthly_values))
            })

        # Create Excel file
        start_creation = time.time()
        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            pd.DataFrame(large_scope1_data).to_excel(writer, sheet_name='Scope 1 Emissions', index=False)
            # Add minimal other sheets
            pd.DataFrame([{'Source': 'Test', 'Annual_Total': 1000}]).to_excel(writer, sheet_name='Scope 2 Emissions', index=False)
            pd.DataFrame([{'Source': 'Test', 'Annual_Total': 1000}]).to_excel(writer, sheet_name='Scope 3 Emissions', index=False)
        end_creation = time.time()

        creation_time = end_creation - start_creation
        assert creation_time < 60.0, f"Large Excel creation took {creation_time:.2f}s, expected < 60.0s"

        # Test data loading performance
        start_loading = time.time()
        report_gen = GHGReportGenerator(str(excel_file))
        end_loading = time.time()

        loading_time = end_loading - start_loading
        assert report_gen.data is not None
        assert len(report_gen.data['Scope 1 Emissions']) == 1000
        assert loading_time < 30.0, f"Large dataset loading took {loading_time:.2f}s, expected < 30.0s"

        # Test statistics generation performance
        start_stats = time.time()
        stats = report_gen.get_summary_statistics()
        end_stats = time.time()

        stats_time = end_stats - start_stats
        assert stats['total_emissions'] > 0
        assert stats_time < 10.0, f"Statistics generation took {stats_time:.2f}s, expected < 10.0s"

    @pytest.mark.performance
    def test_chart_generation_performance_large_data(self, large_dataset_excel_file):
        """Test chart generation performance with large datasets"""
        report_gen = GHGReportGenerator(str(large_dataset_excel_file))

        chart_methods = [
            'create_scope_comparison_chart',
            'create_monthly_trend_chart',
            'create_sankey_diagram',
            'create_facility_breakdown_chart',
            'create_energy_consumption_chart'
        ]

        total_start_time = time.time()

        for method_name in chart_methods:
            start_time = time.time()
            chart = getattr(report_gen, method_name)()
            end_time = time.time()

            generation_time = end_time - start_time
            assert generation_time < 20.0, f"{method_name} took {generation_time:.2f}s, expected < 20.0s"

        total_end_time = time.time()
        total_time = total_end_time - total_start_time
        assert total_time < 60.0, f"All charts generation took {total_time:.2f}s, expected < 60.0s"

    @pytest.mark.performance
    def test_html_report_generation_performance(self, large_dataset_excel_file):
        """Test HTML report generation performance"""
        report_gen = GHGReportGenerator(str(large_dataset_excel_file))
        html_gen = HTMLReportGenerator(report_gen)

        with tempfile.TemporaryDirectory() as temp_dir:
            html_file = Path(temp_dir) / 'performance_report.html'

            start_time = time.time()
            success = html_gen.generate_html_report(str(html_file))
            end_time = time.time()

            generation_time = end_time - start_time

            assert success is True
            assert html_file.exists()
            assert generation_time < 45.0, f"HTML generation took {generation_time:.2f}s, expected < 45.0s"

            # Check file size is reasonable
            file_size = html_file.stat().st_size
            assert file_size > 1000, "HTML file should have substantial content"
            assert file_size < 50 * 1024 * 1024, "HTML file should not be excessively large"

    @pytest.mark.performance
    def test_memory_usage_large_dataset(self, large_dataset_excel_file):
        """Test memory usage with large datasets"""
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Load large dataset
        report_gen = GHGReportGenerator(str(large_dataset_excel_file))
        after_loading_memory = process.memory_info().rss / 1024 / 1024

        # Generate statistics and charts
        stats = report_gen.get_summary_statistics()
        scope_chart = report_gen.create_scope_comparison_chart()
        monthly_chart = report_gen.create_monthly_trend_chart()

        final_memory = process.memory_info().rss / 1024 / 1024

        memory_increase = final_memory - initial_memory

        # Memory increase should be reasonable (less than 500MB for test data)
        assert memory_increase < 500, f"Memory usage increased by {memory_increase:.1f}MB, expected < 500MB"

    @pytest.mark.performance
    def test_concurrent_chart_generation(self, valid_excel_file):
        """Test concurrent chart generation performance"""
        report_gen = GHGReportGenerator(str(valid_excel_file))

        chart_methods = [
            'create_scope_comparison_chart',
            'create_monthly_trend_chart',
            'create_sankey_diagram',
            'create_facility_breakdown_chart',
            'create_energy_consumption_chart'
        ]

        def generate_chart(method_name):
            start_time = time.time()
            chart = getattr(report_gen, method_name)()
            end_time = time.time()
            return method_name, chart, end_time - start_time

        # Test concurrent execution
        start_concurrent = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            future_to_method = {
                executor.submit(generate_chart, method): method
                for method in chart_methods
            }

            results = {}
            for future in concurrent.futures.as_completed(future_to_method, timeout=60):
                method_name, chart, generation_time = future.result()
                results[method_name] = (chart, generation_time)

        end_concurrent = time.time()
        concurrent_time = end_concurrent - start_concurrent

        # Concurrent generation should be faster than sequential
        assert concurrent_time < 30.0, f"Concurrent generation took {concurrent_time:.2f}s, expected < 30.0s"

        # All charts should be generated
        assert len(results) == len(chart_methods)

    @pytest.mark.performance
    def test_memory_leak_prevention(self, valid_excel_file):
        """Test that repeated operations don't cause memory leaks"""
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024

        # Perform operations multiple times
        for i in range(10):
            report_gen = GHGReportGenerator(str(valid_excel_file))
            stats = report_gen.get_summary_statistics()
            chart = report_gen.create_scope_comparison_chart()

            # Force garbage collection
            import gc
            gc.collect()

            current_memory = process.memory_info().rss / 1024 / 1024
            memory_increase = current_memory - initial_memory

            # Memory should not continuously increase
            if i > 5:  # Allow some initial increase
                assert memory_increase < 100, f"Iteration {i}: Memory increased by {memory_increase:.1f}MB, possible leak"

    @pytest.mark.performance
    def test_file_io_performance(self, temp_output_dir):
        """Test file I/O performance"""
        # Test Excel file creation performance
        excel_file = temp_output_dir / 'io_performance_test.xlsx'

        # Create medium-sized dataset
        scope1_data = []
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

        for i in range(100):
            monthly_values = [np.random.uniform(100, 1000) for _ in months]
            scope1_data.append({
                'Source': f'IO Test Source {i+1}',
                'Annual_Total': sum(monthly_values),
                'Percentage': 1.0,
                **dict(zip(months, monthly_values))
            })

        # Test write performance
        start_write = time.time()
        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            pd.DataFrame(scope1_data).to_excel(writer, sheet_name='Scope 1 Emissions', index=False)
        end_write = time.time()

        write_time = end_write - start_write
        assert write_time < 15.0, f"Excel write took {write_time:.2f}s, expected < 15.0s"

        # Test read performance
        start_read = time.time()
        report_gen = GHGReportGenerator(str(excel_file))
        end_read = time.time()

        read_time = end_read - start_read
        assert read_time < 10.0, f"Excel read took {read_time:.2f}s, expected < 10.0s"
        assert report_gen.data is not None

    @pytest.mark.performance
    def test_cpu_usage_monitoring(self, valid_excel_file):
        """Test CPU usage during intensive operations"""
        process = psutil.Process(os.getpid())

        # Monitor CPU usage during chart generation
        cpu_percent_before = process.cpu_percent()

        start_time = time.time()
        report_gen = GHGReportGenerator(str(valid_excel_file))

        # Generate multiple charts
        charts = [
            report_gen.create_scope_comparison_chart(),
            report_gen.create_monthly_trend_chart(),
            report_gen.create_sankey_diagram(),
            report_gen.create_facility_breakdown_chart(),
            report_gen.create_energy_consumption_chart()
        ]

        end_time = time.time()
        cpu_percent_after = process.cpu_percent()

        processing_time = end_time - start_time

        # Should complete efficiently
        assert processing_time < 45.0, f"Chart generation took {processing_time:.2f}s, expected < 45.0s"

        # CPU usage should be reasonable (this is a rough check)
        # Note: CPU percent can be > 100% on multi-core systems
        assert cpu_percent_after < 500, f"CPU usage too high: {cpu_percent_after}%"

    @pytest.mark.performance
    def test_scalability_with_facilities(self, temp_output_dir):
        """Test scalability with increasing number of facilities"""
        facility_counts = [5, 10, 25, 50]
        processing_times = []

        for facility_count in facility_counts:
            excel_file = temp_output_dir / f'scalability_{facility_count}_facilities.xlsx'

            # Create data with varying facility counts
            facility_data = []
            for i in range(facility_count):
                facility_data.append({
                    'Facility': f'Scalability Facility {i+1}',
                    'Scope_1': np.random.uniform(5000, 15000),
                    'Scope_2': np.random.uniform(2000, 8000),
                    'Scope_3': np.random.uniform(3000, 10000),
                    'Energy_Intensity': np.random.uniform(2.0, 6.0),
                    'Production': np.random.uniform(50000, 150000)
                })

            # Create Excel file
            with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
                pd.DataFrame([{'Source': 'Test', 'Annual_Total': 10000}]).to_excel(writer, sheet_name='Scope 1 Emissions', index=False)
                pd.DataFrame([{'Source': 'Test', 'Annual_Total': 5000}]).to_excel(writer, sheet_name='Scope 2 Emissions', index=False)
                pd.DataFrame([{'Source': 'Test', 'Annual_Total': 3000}]).to_excel(writer, sheet_name='Scope 3 Emissions', index=False)
                pd.DataFrame(facility_data).to_excel(writer, sheet_name='Facility Breakdown', index=False)

            # Test processing time
            start_time = time.time()
            report_gen = GHGReportGenerator(str(excel_file))
            facility_chart = report_gen.create_facility_breakdown_chart()
            end_time = time.time()

            processing_time = end_time - start_time
            processing_times.append(processing_time)

        # Processing time should scale reasonably
        # Time for 50 facilities should not be more than 10x time for 5 facilities
        if len(processing_times) >= 2:
            time_ratio = processing_times[-1] / processing_times[0]
            assert time_ratio < 10, f"Poor scalability: {time_ratio:.1f}x increase for {facility_counts[-1]/facility_counts[0]:.1f}x data"

    @pytest.mark.performance
    def test_recommendation_generation_performance(self, large_dataset_excel_file):
        """Test performance of recommendation generation"""
        report_gen = GHGReportGenerator(str(large_dataset_excel_file))

        start_time = time.time()
        recommendations = report_gen.generate_recommendations()
        end_time = time.time()

        generation_time = end_time - start_time

        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        assert generation_time < 5.0, f"Recommendation generation took {generation_time:.2f}s, expected < 5.0s"

    @pytest.mark.performance
    def test_full_workflow_performance_benchmark(self, temp_output_dir):
        """Comprehensive performance benchmark of full workflow"""
        benchmark_results = {}

        # Step 1: Excel Generation
        start_time = time.time()
        generator = GHGExcelGenerator()
        excel_file = temp_output_dir / 'benchmark_test.xlsx'
        generator.create_excel_template(str(excel_file))
        benchmark_results['excel_generation'] = time.time() - start_time

        # Step 2: Data Loading
        start_time = time.time()
        report_gen = GHGReportGenerator(str(excel_file))
        benchmark_results['data_loading'] = time.time() - start_time

        # Step 3: Statistics Generation
        start_time = time.time()
        stats = report_gen.get_summary_statistics()
        benchmark_results['statistics'] = time.time() - start_time

        # Step 4: Chart Generation
        start_time = time.time()
        charts = [
            report_gen.create_scope_comparison_chart(),
            report_gen.create_monthly_trend_chart(),
            report_gen.create_sankey_diagram(),
            report_gen.create_facility_breakdown_chart(),
            report_gen.create_energy_consumption_chart()
        ]
        benchmark_results['charts'] = time.time() - start_time

        # Step 5: Recommendations
        start_time = time.time()
        recommendations = report_gen.generate_recommendations()
        benchmark_results['recommendations'] = time.time() - start_time

        # Step 6: HTML Report
        start_time = time.time()
        html_gen = HTMLReportGenerator(report_gen)
        html_file = temp_output_dir / 'benchmark_report.html'
        html_gen.generate_html_report(str(html_file))
        benchmark_results['html_generation'] = time.time() - start_time

        # Validate benchmark results
        total_time = sum(benchmark_results.values())
        assert total_time < 120.0, f"Full workflow took {total_time:.2f}s, expected < 120.0s"

        # Individual component benchmarks
        assert benchmark_results['excel_generation'] < 20.0
        assert benchmark_results['data_loading'] < 10.0
        assert benchmark_results['statistics'] < 5.0
        assert benchmark_results['charts'] < 30.0
        assert benchmark_results['recommendations'] < 5.0
        assert benchmark_results['html_generation'] < 30.0

        print(f"\nPerformance Benchmark Results:")
        for step, duration in benchmark_results.items():
            print(f"  {step}: {duration:.2f}s")
        print(f"  Total: {total_time:.2f}s")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])