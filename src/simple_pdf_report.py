from playwright.sync_api import sync_playwright
import tempfile
import os
import subprocess
from datetime import datetime
from report_generator import GHGReportGenerator
from html_report import HTMLReportGenerator

# Auto-install Playwright browsers on first run (for Streamlit Cloud)
def ensure_playwright_browsers():
    """Install Playwright browsers if not already installed"""
    try:
        import sys
        import pathlib

        # Check if chromium is already installed
        playwright_cache = pathlib.Path.home() / ".cache" / "ms-playwright"
        if playwright_cache.exists() and list(playwright_cache.glob("chromium*")):
            # Browsers already installed, skip
            return

        print("Installing Playwright browsers (first run only)...")
        # Run playwright install command with dependencies
        result = subprocess.run(
            [sys.executable, "-m", "playwright", "install", "--with-deps", "chromium"],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        if result.returncode == 0:
            print("✓ Playwright browsers installed successfully")
        else:
            print(f"Playwright install output: {result.stdout}")
            print(f"Playwright install errors: {result.stderr}")
    except Exception as e:
        print(f"Error installing Playwright browsers: {e}")

# Install browsers on module import (only once)
ensure_playwright_browsers()

class SimplePDFReportGenerator:
    def __init__(self, report_generator):
        self.report_gen = report_generator
        self.html_gen = HTMLReportGenerator(report_generator)

    def generate_simple_pdf_report(self, output_path, use_ai=False):
        """Generate PDF report from HTML template using Playwright

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

            # Use Playwright to convert HTML to PDF
            with sync_playwright() as p:
                # Launch Chromium browser
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()

                # Load the HTML file
                page.goto(f'file://{tmp_html_path}')

                # Wait for charts to render (Plotly needs time)
                page.wait_for_timeout(2000)

                # Generate PDF with Chromium
                page.pdf(
                    path=output_path,
                    format='A4',
                    landscape=True,
                    print_background=True,
                    margin={
                        'top': '0.5in',
                        'right': '0.5in',
                        'bottom': '0.5in',
                        'left': '0.5in'
                    }
                )

                browser.close()

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
