"""
PDF export using WeasyPrint.
Converts HTML report to PDF format.
"""

from pathlib import Path
from typing import Dict, Any
from .export_html import export_html_report


def export_pdf_report(
    context: Dict[str, Any],
    output_path: Path,
) -> Path:
    """
    Export PDF report from context.

    Args:
        context: Report context dictionary
        output_path: Output PDF file path

    Returns:
        Path to generated PDF file
    """

    try:
        from weasyprint import HTML, CSS
    except ImportError:
        raise ImportError(
            "WeasyPrint is required for PDF generation. "
            "Install with: pip install weasyprint"
        )

    # First generate HTML
    html_path = output_path.with_suffix('.html')
    export_html_report(context, html_path)

    # Convert HTML to PDF
    html = HTML(filename=str(html_path))

    # Additional CSS for print
    print_css = CSS(string="""
        @page {
            size: A4;
            margin: 2cm;
        }

        body {
            font-size: 10pt;
        }

        h1 {
            font-size: 18pt;
        }

        h2 {
            font-size: 14pt;
            page-break-after: avoid;
        }

        h3 {
            font-size: 12pt;
        }

        table {
            page-break-inside: avoid;
        }

        .chart-container {
            page-break-inside: avoid;
        }

        section {
            page-break-inside: avoid;
        }
    """)

    # Generate PDF
    html.write_pdf(output_path, stylesheets=[print_css])

    # Optionally clean up HTML
    # html_path.unlink()

    return output_path


def export_pdf_simple(
    context: Dict[str, Any],
    output_path: Path,
) -> Path:
    """
    Simple PDF export without complex charts (for environments without full dependencies).

    Args:
        context: Report context
        output_path: Output path

    Returns:
        Path to PDF
    """

    try:
        from reportlab.lib.pagesizes import A4, letter
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
        from reportlab.lib import colors
    except ImportError:
        raise ImportError(
            "ReportLab is required. Install with: pip install reportlab"
        )

    # Create PDF
    doc = SimpleDocTemplate(str(output_path), pagesize=A4)
    story = []
    styles = getSampleStyleSheet()

    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2c5f2d'),
        spaceAfter=30,
        alignment=1,  # Center
    )

    story.append(Paragraph(context['organization']['name'], title_style))
    story.append(Paragraph("GHG Inventory Report", styles['Title']))
    story.append(Paragraph(
        f"Reporting Period: {context['period_start']} to {context['period_end']}",
        styles['Normal']
    ))
    story.append(Spacer(1, 0.5*inch))

    # Executive Summary
    story.append(Paragraph("Executive Summary", styles['Heading2']))

    summary_data = [
        ['Metric', 'Value'],
        ['Total Emissions (tCO₂e)', f"{context['summary']['total_co2e_tonnes']:,.2f}"],
        ['Scope 1 (%)', f"{context['summary']['scope_1_pct']:.1f}%"],
        ['Scope 2 (%)', f"{context['summary']['scope_2_pct']:.1f}%"],
        ['Scope 3 (%)', f"{context['summary']['scope_3_pct']:.1f}%"],
    ]

    table = Table(summary_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5f2d')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    story.append(table)
    story.append(PageBreak())

    # Build PDF
    doc.build(story)

    return output_path
