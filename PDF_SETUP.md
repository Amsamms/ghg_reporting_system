# PDF Generation Setup

The GHG Reporting System uses **WeasyPrint** to convert HTML reports to PDF format.

## Why WeasyPrint?

✅ **Pure Python** - No browser dependencies, easier deployment
✅ **Works on Streamlit Cloud** - Confirmed working with simple setup
✅ **Good CSS Support** - Handles most modern CSS (Grid, Flexbox, gradients)
✅ **Small File Size** - ~180 KB PDFs (vs 3.5 MB with wkhtmltopdf)
✅ **Fast** - Quick conversion without browser overhead
✅ **Reliable** - No browser installation issues

## Requirements

### Python Dependencies

All dependencies are in `requirements.txt`:

```bash
pip install -r requirements.txt
```

### System Dependencies (Streamlit Cloud)

For Streamlit Cloud deployment, add "weasyprint" to `packages.txt`:

```
weasyprint
```

This installs the necessary system libraries (Pango, Cairo, etc.).

## How It Works

1. Generate beautiful HTML report with Plotly charts (as static images)
2. Use WeasyPrint to convert HTML to PDF
3. All CSS styling, gradients, layouts preserved
4. Page breaks respected (`page-break-inside: avoid`)

## Features

- ✅ Identical styling to HTML report
- ✅ All charts embedded as images
- ✅ Proper page breaks (CSS page-break rules)
- ✅ Company logo included
- ✅ Custom introduction and conclusion text
- ✅ Landscape orientation for better data visualization
- ✅ Small file size (~180 KB)
- ✅ Fast generation

## Streamlit Cloud Deployment

The system is configured for Streamlit Cloud:

1. **packages.txt** - System package: `weasyprint`
2. **requirements.txt** - Python package: `weasyprint==66.0`

WeasyPrint will work automatically on deployment.

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

## Comparison: PDF Generation Libraries

| Feature | wkhtmltopdf | Playwright | WeasyPrint |
|---------|-------------|------------|------------|
| Deployment | ❌ Complex | ❌ Very Complex | ✅ Simple |
| CSS Grid | ❌ Broken | ✅ Perfect | ✅ Good |
| CSS Flexbox | ⚠️ Partial | ✅ Perfect | ✅ Good |
| File Size | 3.5+ MB | ~1.5 MB | ~180 KB |
| Speed | Medium | Slow | Fast |
| Dependencies | System binary | Browser + System | Python only |
| Streamlit Cloud | ⚠️ Works | ❌ Fails | ✅ Works |

## Troubleshooting

If you get errors on Streamlit Cloud:
1. Ensure `weasyprint` is in `packages.txt`
2. Ensure `weasyprint==66.0` is in `requirements.txt`
3. Redeploy the app

## Limitations

- **No JavaScript**: Charts must be static images (Plotly renders as static in HTML)
- **Limited CSS3**: Some advanced CSS features may not work
- **Font limitations**: System fonts only

These limitations don't affect our use case since we use static Plotly charts embedded in HTML.
