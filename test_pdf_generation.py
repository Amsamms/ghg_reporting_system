#!/usr/bin/env python3
"""Test script for PDF generation with static Plotly charts"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from excel_generator import GHGExcelGenerator
from report_generator import GHGReportGenerator
from simple_pdf_report import SimplePDFReportGenerator

def test_pdf_generation():
    """Test PDF generation with Kaleido + WeasyPrint"""

    print("=" * 60)
    print("Testing PDF Generation with Static Plotly Charts")
    print("=" * 60)

    # Step 1: Generate sample Excel template
    print("\n[1/4] Generating sample Excel template...")
    excel_gen = GHGExcelGenerator()
    sample_file = 'test_sample.xlsx'

    if excel_gen.create_excel_template(sample_file):
        print(f"✓ Sample Excel created: {sample_file}")
    else:
        print("✗ Failed to create sample Excel")
        return False

    # Step 2: Load data from Excel
    print("\n[2/4] Loading data from Excel...")
    try:
        report_gen = GHGReportGenerator(sample_file)
        print("✓ Data loaded successfully")
    except Exception as e:
        print(f"✗ Failed to load data: {e}")
        return False

    # Step 3: Generate PDF
    print("\n[3/4] Generating PDF with static charts (Kaleido + WeasyPrint)...")
    pdf_gen = SimplePDFReportGenerator(report_gen)
    output_pdf = 'test_output.pdf'

    try:
        if pdf_gen.generate_simple_pdf_report(output_pdf, use_ai=False):
            print(f"✓ PDF generated successfully: {output_pdf}")
        else:
            print("✗ Failed to generate PDF")
            return False
    except Exception as e:
        print(f"✗ Error during PDF generation: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Step 4: Verify PDF file exists and has content
    print("\n[4/4] Verifying PDF file...")
    if os.path.exists(output_pdf):
        file_size = os.path.getsize(output_pdf)
        print(f"✓ PDF file exists")
        print(f"  File size: {file_size:,} bytes ({file_size/1024:.1f} KB)")

        if file_size > 10000:  # At least 10 KB
            print("✓ PDF appears to have content")
        else:
            print("⚠ Warning: PDF file seems too small")
            return False
    else:
        print("✗ PDF file not found")
        return False

    print("\n" + "=" * 60)
    print("✓ ALL TESTS PASSED!")
    print("=" * 60)
    print(f"\nGenerated files:")
    print(f"  - {sample_file} (sample data)")
    print(f"  - {output_pdf} (PDF report)")
    print("\nYou can open the PDF to verify charts are displayed correctly.")

    return True

if __name__ == '__main__':
    success = test_pdf_generation()
    sys.exit(0 if success else 1)
