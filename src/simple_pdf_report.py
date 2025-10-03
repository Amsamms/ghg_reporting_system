from weasyprint import HTML
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
        """Generate PDF report from HTML template using WeasyPrint

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

            # Generate HTML report first (with pdf_mode=True for static charts)
            if not self.html_gen.generate_html_report(tmp_html_path, facility_filter=None, use_ai=use_ai, pdf_mode=True):
                print("Failed to generate HTML template")
                return False

            # Convert HTML to PDF using WeasyPrint
            HTML(filename=tmp_html_path).write_pdf(output_path)

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
