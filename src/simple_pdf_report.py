import pdfkit
import tempfile
import os
from datetime import datetime
from report_generator import GHGReportGenerator
from html_report import HTMLReportGenerator

class SimplePDFReportGenerator:
    def __init__(self, report_generator):
        self.report_gen = report_generator
        self.html_gen = HTMLReportGenerator(report_generator)

    def generate_simple_pdf_report(self, output_path, use_ai=False):
        """Generate PDF report from HTML template using pdfkit

        Args:
            output_path: Path to save PDF file
            use_ai: If True, use AI-generated recommendations

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Create temporary HTML file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as tmp_html:
                tmp_html_path = tmp_html.name

            # Generate HTML report first
            if not self.html_gen.generate_html_report(tmp_html_path, facility_filter=None, use_ai=use_ai):
                print("Failed to generate HTML template")
                return False

            # Read HTML content
            with open(tmp_html_path, 'r', encoding='utf-8') as f:
                html_content = f.read()

            # Configure pdfkit options for better PDF output
            # For landscape A4: ~297mm width × 210mm height
            # Set viewport width to match landscape dimensions
            options = {
                'page-size': 'A4',
                'orientation': 'Landscape',
                'margin-top': '0.5in',
                'margin-right': '0.5in',
                'margin-bottom': '0.5in',
                'margin-left': '0.5in',
                'encoding': 'UTF-8',
                'no-outline': None,
                'enable-local-file-access': None,
                'print-media-type': None,
                'javascript-delay': 1000,
                'no-stop-slow-scripts': None,
                'debug-javascript': None,
                'load-error-handling': 'ignore',
                'load-media-error-handling': 'ignore',
                'viewport-size': '1920x1080',  # Wider viewport for landscape
                'zoom': 1.0
            }

            # Generate PDF from HTML
            pdfkit.from_file(tmp_html_path, output_path, options=options)

            # Clean up temporary HTML file
            os.unlink(tmp_html_path)

            print(f"PDF report generated successfully: {output_path}")
            return True

        except Exception as e:
            print(f"Error generating PDF report: {e}")
            import traceback
            traceback.print_exc()

            # Clean up if exists
            if 'tmp_html_path' in locals() and os.path.exists(tmp_html_path):
                os.unlink(tmp_html_path)

            return False
