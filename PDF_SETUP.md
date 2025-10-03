# PDF Generation Setup

The GHG Reporting System uses **Playwright** with **Chromium** to convert the beautiful HTML reports to PDF format.

## Why Playwright?

✅ **Perfect Rendering** - Uses real Chromium browser (same as Chrome)
✅ **CSS Grid Support** - Full support for modern CSS
✅ **Chart Quality** - Plotly charts render perfectly
✅ **No Manual Fixes** - Respects all CSS page-break rules
✅ **Exact Match** - PDF looks identical to browser print preview

## Requirements

### Python Dependencies

All dependencies are in `requirements.txt`:

```bash
pip install -r requirements.txt
```

### Install Playwright Browsers

After installing the package, install Chromium:

```bash
playwright install chromium
```

Or with dependencies:

```bash
playwright install --with-deps chromium
```

## How It Works

1. Generate beautiful HTML report with interactive charts
2. Launch headless Chromium browser via Playwright
3. Load HTML and wait for charts to render (2 seconds)
4. Convert to PDF using Chromium's native print function
5. All CSS Grid, Flexbox, gradients preserved perfectly

## Features

- ✅ Identical styling to HTML report
- ✅ All charts embedded perfectly (no quality loss)
- ✅ Proper page breaks (respects CSS page-break-inside: avoid)
- ✅ Company logo included
- ✅ Custom introduction and conclusion text
- ✅ KPI cards display in grid layout (3 per row)
- ✅ Landscape orientation for better data visualization
- ✅ Smaller file size (1.5 MB vs 3.5 MB)

## Streamlit Cloud Deployment

The system is configured for Streamlit Cloud:

1. **packages.txt** - System dependencies for Chromium
2. **.streamlit/packages.txt** - Post-install script for Playwright browsers
3. **requirements.txt** - Python packages including Playwright

Playwright browsers will be installed automatically during deployment.

## Local Testing

```python
from excel_generator import GHGExcelGenerator
from report_generator import GHGReportGenerator
from simple_pdf_report import SimplePDFReportGenerator

# Generate sample data
excel_gen = GHGExcelGenerator()
excel_gen.create_excel_template('sample.xlsx')

# Load data
report_gen = GHGReportGenerator('sample.xlsx')

# Generate PDF
pdf_gen = SimplePDFReportGenerator(report_gen)
pdf_gen.generate_simple_pdf_report('output.pdf')
```

## Troubleshooting

If Playwright browsers are not installed:
```bash
playwright install chromium
```

If you get errors about missing dependencies on Linux:
```bash
playwright install --with-deps chromium
```

## Comparison: Playwright vs wkhtmltopdf

| Feature | wkhtmltopdf | Playwright |
|---------|-------------|------------|
| CSS Grid | ❌ Broken | ✅ Perfect |
| CSS Flexbox | ⚠️ Partial | ✅ Perfect |
| Modern CSS | ❌ Limited | ✅ Full Support |
| Chart Quality | ⚠️ Poor | ✅ Perfect |
| Page Breaks | ⚠️ Partial | ✅ Perfect |
| File Size | 3.5+ MB | ~1.5 MB |
| Browser Engine | Old WebKit | Chromium (Chrome) |
