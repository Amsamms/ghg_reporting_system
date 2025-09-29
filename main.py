#!/usr/bin/env python3
"""
GHG Reporting System Main Launcher
Professional GHG Report Generator for Petroleum Companies

This script launches the GHG Reporting System GUI and can also be used
to generate reports from command line.

Author: Advanced GHG Reporting System
Version: 1.0
"""

import sys
import os
import argparse
from pathlib import Path

# Add src directory to path
current_dir = Path(__file__).parent
src_dir = current_dir / 'src'
sys.path.insert(0, str(src_dir))

def launch_gui():
    """Launch the GUI interface"""
    try:
        from gui_interface import main as gui_main
        gui_main()
    except ImportError as e:
        print(f"Error importing GUI modules: {e}")
        print("Please ensure all required packages are installed.")
        return False
    except Exception as e:
        print(f"Error launching GUI: {e}")
        return False
    return True

def generate_reports_cli(excel_file, output_dir, report_types):
    """Generate reports from command line"""
    try:
        from report_generator import GHGReportGenerator
        from pdf_report import PDFReportGenerator
        from html_report import HTMLReportGenerator
        from datetime import datetime

        print(f"Loading Excel file: {excel_file}")
        report_gen = GHGReportGenerator(excel_file)

        if not report_gen.data:
            print("Error: Failed to load Excel data")
            return False

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # Generate PDF report
        if 'pdf' in report_types:
            print("Generating PDF report...")
            pdf_generator = PDFReportGenerator(report_gen)
            pdf_path = os.path.join(output_dir, f"GHG_Report_{timestamp}.pdf")

            if pdf_generator.generate_pdf_report(pdf_path):
                print(f"✅ PDF report generated: {pdf_path}")
            else:
                print("❌ PDF report generation failed")

        # Generate HTML report
        if 'html' in report_types:
            print("Generating HTML report...")
            html_generator = HTMLReportGenerator(report_gen)
            html_path = os.path.join(output_dir, f"GHG_Report_{timestamp}.html")

            if html_generator.generate_html_report(html_path):
                print(f"✅ HTML report generated: {html_path}")
            else:
                print("❌ HTML report generation failed")

        return True

    except ImportError as e:
        print(f"Error importing modules: {e}")
        return False
    except Exception as e:
        print(f"Error generating reports: {e}")
        return False

def create_sample_data():
    """Create sample Excel data file"""
    try:
        from excel_generator import GHGExcelGenerator

        print("Creating sample Excel template...")
        generator = GHGExcelGenerator()
        template_path = current_dir / 'data' / 'sample_ghg_data.xlsx'

        # Ensure data directory exists
        template_path.parent.mkdir(exist_ok=True)

        generator.create_excel_template(str(template_path))
        print(f"✅ Sample data created: {template_path}")
        return True

    except Exception as e:
        print(f"Error creating sample data: {e}")
        return False

def main():
    """Main function with command line argument parsing"""
    parser = argparse.ArgumentParser(
        description="GHG Reporting System - Professional GHG Report Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                                    # Launch GUI
  python main.py --cli --excel data.xlsx --output reports/  # CLI mode
  python main.py --sample                          # Create sample data
  python main.py --cli --excel data.xlsx --output reports/ --types pdf html
        """
    )

    parser.add_argument('--cli', action='store_true',
                       help='Run in command line mode (no GUI)')

    parser.add_argument('--excel', type=str,
                       help='Path to Excel file with GHG data')

    parser.add_argument('--output', type=str,
                       help='Output directory for generated reports')

    parser.add_argument('--types', nargs='+', choices=['pdf', 'html'],
                       default=['pdf', 'html'],
                       help='Types of reports to generate (default: both)')

    parser.add_argument('--sample', action='store_true',
                       help='Create sample Excel data file')

    parser.add_argument('--version', action='version',
                       version='GHG Reporting System v1.0')

    args = parser.parse_args()

    print("🌱 GHG Reporting System v1.0")
    print("Professional GHG Report Generator for Petroleum Companies")
    print("=" * 60)

    # Create sample data
    if args.sample:
        if create_sample_data():
            print("\n✅ Sample data file created successfully!")
            print("You can now use this file as input for report generation.")
        else:
            print("\n❌ Failed to create sample data file")
        return

    # Command line mode
    if args.cli:
        if not args.excel:
            print("Error: --excel argument is required in CLI mode")
            return

        if not args.output:
            print("Error: --output argument is required in CLI mode")
            return

        if not os.path.exists(args.excel):
            print(f"Error: Excel file not found: {args.excel}")
            return

        if not os.path.exists(args.output):
            print(f"Creating output directory: {args.output}")
            os.makedirs(args.output, exist_ok=True)

        print(f"Excel file: {args.excel}")
        print(f"Output directory: {args.output}")
        print(f"Report types: {', '.join(args.types)}")
        print("-" * 40)

        if generate_reports_cli(args.excel, args.output, args.types):
            print("\n✅ All reports generated successfully!")
        else:
            print("\n❌ Report generation failed")
        return

    # GUI mode (default)
    print("Launching GUI interface...")
    if not launch_gui():
        print("\n❌ Failed to launch GUI")
        print("Try using --cli mode or check your Python environment")

if __name__ == "__main__":
    main()