# PDF Generation Setup

The GHG Reporting System uses `wkhtmltopdf` to convert the beautiful HTML reports to PDF format.

## Requirements

### System Dependency: wkhtmltopdf

The PDF generation requires `wkhtmltopdf` to be installed on your system.

#### Installation Instructions

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y wkhtmltopdf
```

**macOS:**
```bash
brew install wkhtmltopdf
```

**Windows:**
Download and install from: https://wkhtmltopdf.org/downloads.html

### Python Dependencies

All Python dependencies are listed in `requirements.txt` and can be installed with:

```bash
pip install -r requirements.txt
```

## How It Works

1. The system generates a beautiful HTML report with interactive charts
2. The HTML is converted to PDF using `wkhtmltopdf` via `pdfkit`
3. Special print CSS rules ensure proper page breaks and formatting
4. Charts are embedded directly in the PDF

## Features

- ✅ Identical styling to HTML report
- ✅ All charts embedded in PDF
- ✅ Proper page breaks (no split charts)
- ✅ Company logo included
- ✅ Custom introduction and conclusion text
- ✅ Professional pagination

## Streamlit Cloud Deployment

For Streamlit Cloud deployment, add this to `packages.txt`:
```
wkhtmltopdf
```

This ensures `wkhtmltopdf` is installed on the cloud server.
