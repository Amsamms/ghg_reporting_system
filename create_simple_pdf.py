#!/usr/bin/env python3
"""
Create a simple PDF report that will definitely open in Windows
"""
import sys
import os

# Add src directory to path
current_dir = os.path.dirname(__file__)
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

from report_generator import GHGReportGenerator
from simple_pdf_report import SimplePDFReportGenerator
from datetime import datetime

def create_simple_pdf():
    """Create a simple PDF that will open properly"""
    excel_file = "data/sample_ghg_data.xlsx"

    if not os.path.exists(excel_file):
        print("❌ Excel file not found. Please run 'python main.py --sample' first.")
        return False

    print("📄 Creating simple PDF report...")

    # Create report generator
    report_gen = GHGReportGenerator(excel_file)

    if not report_gen.data:
        print("❌ Failed to load Excel data")
        return False

    # Create simple PDF generator
    simple_pdf = SimplePDFReportGenerator(report_gen)

    # Generate output filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    pdf_path = f"reports/Simple_GHG_Report_{timestamp}.pdf"

    # Ensure reports directory exists
    os.makedirs("reports", exist_ok=True)

    # Generate PDF
    if simple_pdf.generate_simple_pdf_report(pdf_path):
        print(f"✅ Simple PDF report created: {pdf_path}")
        print(f"📁 Full path: {os.path.abspath(pdf_path)}")
        return True
    else:
        print("❌ Failed to create PDF report")
        return False

if __name__ == "__main__":
    create_simple_pdf()