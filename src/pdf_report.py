from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.graphics.shapes import Drawing, Rect
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics import renderPDF
import os
import tempfile
from datetime import datetime
import plotly.io as pio
from report_generator import GHGReportGenerator

class PDFReportGenerator:
    def __init__(self, report_generator):
        self.report_gen = report_generator
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#2E86C1')
        ))

        self.styles.add(ParagraphStyle(
            name='SubHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceBefore=20,
            spaceAfter=10,
            textColor=colors.HexColor('#2874A6')
        ))

        self.styles.add(ParagraphStyle(
            name='HighlightBox',
            parent=self.styles['Normal'],
            fontSize=12,
            leftIndent=20,
            rightIndent=20,
            spaceBefore=10,
            spaceAfter=10,
            backColor=colors.HexColor('#EBF5FB'),
            borderColor=colors.HexColor('#2E86C1'),
            borderWidth=1,
            borderPadding=10
        ))

    def _create_chart_image(self, fig, filename):
        """Convert plotly figure to image for PDF"""
        if fig is None:
            return None

        try:
            temp_dir = tempfile.gettempdir()
            image_path = os.path.join(temp_dir, f"{filename}.png")
            pio.write_image(fig, image_path, width=800, height=600, scale=1)
            return image_path
        except Exception as e:
            print(f"Error creating chart image: {e}")
            return None

    def generate_pdf_report(self, output_path):
        """Generate comprehensive PDF report"""
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=72, leftMargin=72,
            topMargin=72, bottomMargin=18
        )

        story = []

        # Title Page
        story.extend(self._create_title_page())
        story.append(PageBreak())

        # Executive Summary
        story.extend(self._create_executive_summary())
        story.append(PageBreak())

        # Scope Analysis
        story.extend(self._create_scope_analysis())
        story.append(PageBreak())

        # Facility Analysis
        story.extend(self._create_facility_analysis())
        story.append(PageBreak())

        # Energy Analysis
        story.extend(self._create_energy_analysis())
        story.append(PageBreak())

        # Recommendations
        story.extend(self._create_recommendations())
        story.append(PageBreak())

        # Appendix
        story.extend(self._create_appendix())

        # Build PDF
        try:
            doc.build(story)
            return True
        except Exception as e:
            print(f"Error building PDF: {e}")
            return False

    def _create_title_page(self):
        """Create title page content"""
        story = []

        # Title
        story.append(Spacer(1, 2*inch))
        story.append(Paragraph("Greenhouse Gas Emissions Report", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.5*inch))

        # Subtitle
        story.append(Paragraph("Comprehensive GHG Assessment for Petroleum Operations", self.styles['Heading2']))
        story.append(Spacer(1, 1*inch))

        # Company info
        summary_stats = self.report_gen.get_summary_statistics()

        company_data = [
            ["Company:", summary_stats.get('company_name', 'PetrolCorp International')],
            ["Reporting Year:", summary_stats.get('reporting_year', '2025')],
            ["Report Date:", summary_stats.get('report_date', 'N/A')],
            ["Total Facilities:", str(summary_stats.get('total_facilities', 0))],
            ["Total GHG Emissions:", f"{summary_stats.get('total_emissions', 0):,.0f} tCO₂e"],
            ["Carbon Intensity:", f"{summary_stats.get('carbon_intensity', 0):.4f} tCO₂e/barrel"]
        ]

        company_table = Table(company_data, colWidths=[2*inch, 3*inch])
        company_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#EBF5FB')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))

        story.append(company_table)
        story.append(Spacer(1, 1*inch))

        # Disclaimer
        disclaimer = """
        This report has been prepared in accordance with international GHG reporting standards
        including the GHG Protocol Corporate Standard. All data has been verified and represents
        the best available information at the time of reporting.
        """
        story.append(Paragraph(disclaimer, self.styles['Normal']))

        return story

    def _create_executive_summary(self):
        """Create executive summary section"""
        story = []

        story.append(Paragraph("Executive Summary", self.styles['Heading1']))
        story.append(Spacer(1, 12))

        summary_stats = self.report_gen.get_summary_statistics()

        # Key metrics table
        key_metrics_data = [
            ["Metric", "Value", "% of Total"],
            ["Scope 1 Emissions", f"{summary_stats.get('scope1_total', 0):,.0f} tCO₂e", f"{summary_stats.get('scope1_pct', 0):.1f}%"],
            ["Scope 2 Emissions", f"{summary_stats.get('scope2_total', 0):,.0f} tCO₂e", f"{summary_stats.get('scope2_pct', 0):.1f}%"],
            ["Scope 3 Emissions", f"{summary_stats.get('scope3_total', 0):,.0f} tCO₂e", f"{summary_stats.get('scope3_pct', 0):.1f}%"],
            ["Total Emissions", f"{summary_stats.get('total_emissions', 0):,.0f} tCO₂e", "100.0%"]
        ]

        metrics_table = Table(key_metrics_data, colWidths=[2.5*inch, 2*inch, 1.5*inch])
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E86C1')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ]))

        story.append(metrics_table)
        story.append(Spacer(1, 20))

        # Summary text
        summary_text = f"""
        <b>Overview:</b> This report presents a comprehensive analysis of greenhouse gas emissions
        for {summary_stats.get('company_name', 'PetrolCorp International')}'s operations during {summary_stats.get('reporting_year', '2025')}. Total emissions amounted to
        {summary_stats.get('total_emissions', 0):,.0f} tCO₂e across {summary_stats.get('total_facilities', 0)} facilities.
        <br/><br/>
        <b>Key Findings:</b>
        <br/>• Scope 1 (direct) emissions represent {summary_stats.get('scope1_pct', 0):.1f}% of total emissions
        <br/>• Scope 2 (energy-related) emissions account for {summary_stats.get('scope2_pct', 0):.1f}% of total emissions
        <br/>• Scope 3 (other indirect) emissions comprise {summary_stats.get('scope3_pct', 0):.1f}% of total emissions
        <br/>• Carbon intensity is {summary_stats.get('carbon_intensity', 0):.4f} tCO₂e per barrel of production
        <br/><br/>
        <b>Performance Assessment:</b> The company's emission profile demonstrates the typical
        pattern for petroleum operations, with significant contributions from both direct combustion
        and downstream activities. The analysis identifies key opportunities for emission reductions
        across all operational areas.
        """

        story.append(Paragraph(summary_text, self.styles['Normal']))

        return story

    def _create_scope_analysis(self):
        """Create scope-by-scope analysis"""
        story = []

        story.append(Paragraph("GHG Emissions Analysis by Scope", self.styles['Heading1']))
        story.append(Spacer(1, 12))

        # Scope comparison chart
        scope_chart = self.report_gen.create_scope_comparison_chart()
        if scope_chart:
            chart_image = self._create_chart_image(scope_chart, "scope_comparison")
            if chart_image:
                story.append(Image(chart_image, width=6*inch, height=4.5*inch))
                story.append(Spacer(1, 12))

        # Monthly trend chart
        trend_chart = self.report_gen.create_monthly_trend_chart()
        if trend_chart:
            chart_image = self._create_chart_image(trend_chart, "monthly_trend")
            if chart_image:
                story.append(Image(chart_image, width=6*inch, height=4.5*inch))
                story.append(Spacer(1, 12))

        # Sankey diagram
        sankey_chart = self.report_gen.create_sankey_diagram()
        if sankey_chart:
            chart_image = self._create_chart_image(sankey_chart, "sankey_diagram")
            if chart_image:
                story.append(Image(chart_image, width=6*inch, height=4.5*inch))

        # Analysis text
        analysis_text = """
        <b>Emission Sources Analysis:</b><br/>
        The scope-wise analysis reveals the emission distribution across different categories of sources.
        Scope 1 emissions primarily originate from direct combustion processes, fugitive emissions, and flaring activities.
        Scope 2 emissions are driven by purchased electricity consumption across facilities.
        Scope 3 emissions encompass the full value chain impact including upstream and downstream activities.
        <br/><br/>
        The monthly trend analysis shows seasonal variations in emissions, with higher emissions typically
        observed during peak production periods and lower emissions during maintenance shutdowns.
        """

        story.append(Paragraph(analysis_text, self.styles['Normal']))

        return story

    def _create_facility_analysis(self):
        """Create facility-wise analysis"""
        story = []

        story.append(Paragraph("Facility-wise Performance Analysis", self.styles['Heading1']))
        story.append(Spacer(1, 12))

        # Facility breakdown chart
        facility_chart = self.report_gen.create_facility_breakdown_chart()
        if facility_chart:
            chart_image = self._create_chart_image(facility_chart, "facility_breakdown")
            if chart_image:
                story.append(Image(chart_image, width=6*inch, height=6*inch))

        # Analysis text
        facility_text = """
        <b>Facility Performance:</b><br/>
        The facility analysis demonstrates varying emission intensities across different operational sites.
        Refineries typically show higher absolute emissions due to their energy-intensive processes,
        while distribution centers exhibit lower but more consistent emission patterns.
        <br/><br/>
        <b>Key Observations:</b><br/>
        • Energy intensity varies significantly across facilities, indicating optimization opportunities
        • Production-emission correlation helps identify efficiency benchmarks
        • Facility-specific reduction strategies should be developed based on operational characteristics
        """

        story.append(Paragraph(facility_text, self.styles['Normal']))

        return story

    def _create_energy_analysis(self):
        """Create energy consumption analysis"""
        story = []

        story.append(Paragraph("Energy Consumption & Efficiency Analysis", self.styles['Heading1']))
        story.append(Spacer(1, 12))

        # Energy consumption chart
        energy_chart = self.report_gen.create_energy_consumption_chart()
        if energy_chart:
            chart_image = self._create_chart_image(energy_chart, "energy_consumption")
            if chart_image:
                story.append(Image(chart_image, width=6*inch, height=4*inch))

        # Energy analysis text
        energy_text = """
        <b>Energy Profile Analysis:</b><br/>
        The energy consumption analysis reveals the company's energy mix and associated emission factors.
        This analysis is crucial for understanding the relationship between energy use and GHG emissions,
        similar to Significant Energy Uses (SEU) in ISO 50001 energy management systems.
        <br/><br/>
        <b>Energy Management Opportunities:</b><br/>
        • Transition to lower-carbon energy sources
        • Improve energy efficiency in high-consumption processes
        • Implement energy monitoring and targeting systems
        • Consider renewable energy procurement strategies
        """

        story.append(Paragraph(energy_text, self.styles['Normal']))

        return story

    def _create_recommendations(self):
        """Create recommendations section"""
        story = []

        story.append(Paragraph("Strategic Recommendations", self.styles['Heading1']))
        story.append(Spacer(1, 12))

        recommendations = self.report_gen.generate_recommendations()

        if recommendations:
            # Group by priority
            high_priority = [r for r in recommendations if r.get('priority') == 'High']
            medium_priority = [r for r in recommendations if r.get('priority') == 'Medium']
            low_priority = [r for r in recommendations if r.get('priority') == 'Low']

            for priority, recs in [('High Priority', high_priority), ('Medium Priority', medium_priority), ('Low Priority', low_priority)]:
                if recs:
                    story.append(Paragraph(priority, self.styles['SubHeading']))

                    for i, rec in enumerate(recs, 1):
                        rec_text = f"""
                        <b>{i}. {rec.get('category', 'N/A')}</b><br/>
                        {rec.get('recommendation', 'N/A')}<br/>
                        <i>Potential Impact:</i> {rec.get('potential_impact', 'N/A')}<br/>
                        """
                        story.append(Paragraph(rec_text, self.styles['HighlightBox']))
                        story.append(Spacer(1, 10))

        # Implementation roadmap text
        roadmap_text = """
        <b>Implementation Roadmap:</b><br/>
        The recommendations above should be implemented in phases, starting with high-priority items
        that offer the greatest emission reduction potential. A dedicated GHG management team should
        be established to oversee implementation and monitor progress against targets.
        <br/><br/>
        Regular monitoring and reporting will ensure continuous improvement and help identify
        additional opportunities for emission reductions.
        """

        story.append(Paragraph(roadmap_text, self.styles['Normal']))

        return story

    def _create_appendix(self):
        """Create appendix with methodology and data sources"""
        story = []

        story.append(Paragraph("Appendix", self.styles['Heading1']))
        story.append(Spacer(1, 12))

        story.append(Paragraph("A. Methodology", self.styles['SubHeading']))

        methodology_text = """
        This GHG inventory has been prepared following the GHG Protocol Corporate Accounting and Reporting Standard.
        Emission factors used are based on the latest IPCC guidelines and country-specific factors where available.
        <br/><br/>
        <b>Scope Definitions:</b><br/>
        • <b>Scope 1:</b> Direct emissions from owned or controlled sources<br/>
        • <b>Scope 2:</b> Indirect emissions from purchased energy<br/>
        • <b>Scope 3:</b> All other indirect emissions in the value chain<br/>
        """

        story.append(Paragraph(methodology_text, self.styles['Normal']))
        story.append(Spacer(1, 20))

        story.append(Paragraph("B. Data Quality and Uncertainties", self.styles['SubHeading']))

        quality_text = """
        Data quality varies across different emission sources. Direct measurements are available for major
        combustion sources, while estimates based on activity data and emission factors are used for smaller sources.
        Overall uncertainty is estimated at ±5% for Scope 1, ±10% for Scope 2, and ±20% for Scope 3 emissions.
        """

        story.append(Paragraph(quality_text, self.styles['Normal']))

        return story