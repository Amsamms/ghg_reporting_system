from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.graphics.shapes import Drawing, Rect
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics import renderPDF
import os
from datetime import datetime
from report_generator import GHGReportGenerator

class SimplePDFReportGenerator:
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

    def generate_simple_pdf_report(self, output_path, use_ai=False):
        """Generate comprehensive PDF report with detailed information

        Args:
            output_path: Path to save PDF file
            use_ai: If True, use AI-generated recommendations
        """
        # Store use_ai in instance variable for use in _create_recommendations
        self.use_ai = use_ai

        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=50, leftMargin=50,
            topMargin=50, bottomMargin=50
        )

        story = []

        # Title Page
        story.extend(self._create_title_page())
        story.append(PageBreak())

        # Executive Summary
        story.extend(self._create_executive_summary())
        story.append(PageBreak())

        # Comprehensive Data Analysis
        story.extend(self._create_comprehensive_data_analysis())
        story.append(Spacer(1, 30))

        # Simple Charts
        story.extend(self._create_simple_charts())
        story.append(PageBreak())

        # Scope-by-Scope Analysis
        story.extend(self._create_scope_analysis())
        story.append(Spacer(1, 30))

        # Facility Analysis
        story.extend(self._create_facility_analysis())
        story.append(Spacer(1, 30))

        # Energy Analysis
        story.extend(self._create_energy_analysis())
        story.append(PageBreak())

        # Performance Targets
        story.extend(self._create_performance_targets())
        story.append(Spacer(1, 30))

        # Recommendations
        story.extend(self._create_recommendations())
        story.append(PageBreak())

        # Methodology and Standards
        story.extend(self._create_methodology_section())

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
            ["Company:", "PetrolCorp International"],
            ["Reporting Year:", "2024"],
            ["Report Date:", summary_stats.get('report_date', 'N/A')],
            ["Total Facilities:", str(summary_stats.get('total_facilities', 0))],
            ["Total GHG Emissions:", f"{summary_stats.get('total_emissions', 0):,.0f} tCO2e"],
            ["Carbon Intensity:", f"{summary_stats.get('carbon_intensity', 0):.4f} tCO2e/barrel"]
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
            ["Scope 1 Emissions", f"{summary_stats.get('scope1_total', 0):,.0f} tCO2e", f"{summary_stats.get('scope1_pct', 0):.1f}%"],
            ["Scope 2 Emissions", f"{summary_stats.get('scope2_total', 0):,.0f} tCO2e", f"{summary_stats.get('scope2_pct', 0):.1f}%"],
            ["Scope 3 Emissions", f"{summary_stats.get('scope3_total', 0):,.0f} tCO2e", f"{summary_stats.get('scope3_pct', 0):.1f}%"],
            ["Total Emissions", f"{summary_stats.get('total_emissions', 0):,.0f} tCO2e", "100.0%"]
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
        for PetrolCorp International's operations during 2024. Total emissions amounted to
        {summary_stats.get('total_emissions', 0):,.0f} tCO2e across {summary_stats.get('total_facilities', 0)} facilities.
        <br/><br/>
        <b>Key Findings:</b>
        <br/>• Scope 1 (direct) emissions represent {summary_stats.get('scope1_pct', 0):.1f}% of total emissions
        <br/>• Scope 2 (energy-related) emissions account for {summary_stats.get('scope2_pct', 0):.1f}% of total emissions
        <br/>• Scope 3 (other indirect) emissions comprise {summary_stats.get('scope3_pct', 0):.1f}% of total emissions
        <br/>• Carbon intensity is {summary_stats.get('carbon_intensity', 0):.4f} tCO2e per barrel of production
        """

        story.append(Paragraph(summary_text, self.styles['Normal']))
        return story

    def _create_data_tables(self):
        """Create detailed data tables"""
        story = []

        story.append(Paragraph("Detailed Emission Data", self.styles['Heading1']))
        story.append(Spacer(1, 12))

        # Get scope 1 data
        if self.report_gen.data and 'Scope 1 Emissions' in self.report_gen.data:
            scope1_df = self.report_gen.data['Scope 1 Emissions']
            if not scope1_df.empty and 'Source' in scope1_df.columns and 'Annual_Total' in scope1_df.columns:
                story.append(Paragraph("Scope 1 Emissions (Direct)", self.styles['SubHeading']))

                # Top 5 scope 1 sources
                top_scope1 = scope1_df.nlargest(5, 'Annual_Total')
                scope1_data = [["Source", "Annual Total (tCO2e)", "Percentage"]]

                for _, row in top_scope1.iterrows():
                    scope1_data.append([
                        str(row['Source'])[:30] + "..." if len(str(row['Source'])) > 30 else str(row['Source']),
                        f"{row['Annual_Total']:,.0f}",
                        f"{row['Percentage']:.1f}%"
                    ])

                scope1_table = Table(scope1_data, colWidths=[3*inch, 1.5*inch, 1*inch])
                scope1_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FF6B6B')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ]))

                story.append(scope1_table)
                story.append(Spacer(1, 20))

        return story

    def _create_simple_charts(self):
        """Create simple charts using ReportLab"""
        story = []

        story.append(Paragraph("Emission Analysis Charts", self.styles['Heading1']))
        story.append(Spacer(1, 12))

        # Simple pie chart for scope distribution
        summary_stats = self.report_gen.get_summary_statistics()

        drawing = Drawing(400, 300)
        pie = Pie()
        pie.x = 50
        pie.y = 50
        pie.width = 200
        pie.height = 200

        pie.data = [
            summary_stats.get('scope1_total', 0),
            summary_stats.get('scope2_total', 0),
            summary_stats.get('scope3_total', 0)
        ]
        pie.labels = ['Scope 1', 'Scope 2', 'Scope 3']
        pie.slices.strokeWidth = 0.5
        pie.slices[0].fillColor = colors.HexColor('#FF6B6B')
        pie.slices[1].fillColor = colors.HexColor('#4ECDC4')
        pie.slices[2].fillColor = colors.HexColor('#45B7D1')

        drawing.add(pie)
        story.append(drawing)
        story.append(Spacer(1, 20))

        # Chart description
        chart_text = f"""
        <b>Scope Distribution Analysis:</b><br/>
        The pie chart above shows the distribution of emissions across the three GHG Protocol scopes.
        Scope 1 represents {summary_stats.get('scope1_pct', 0):.1f}% of total emissions,
        Scope 2 accounts for {summary_stats.get('scope2_pct', 0):.1f}%,
        and Scope 3 comprises {summary_stats.get('scope3_pct', 0):.1f}% of the total
        {summary_stats.get('total_emissions', 0):,.0f} tCO2e annual emissions.
        """

        story.append(Paragraph(chart_text, self.styles['Normal']))
        return story

    def _create_recommendations(self):
        """Create recommendations section"""
        story = []

        story.append(Paragraph("Strategic Recommendations", self.styles['Heading1']))
        story.append(Spacer(1, 12))

        recommendations = self.report_gen.generate_recommendations(use_ai=getattr(self, 'use_ai', False))

        if recommendations:
            for i, rec in enumerate(recommendations[:5], 1):  # Show top 5 recommendations
                rec_text = f"""
                <b>{i}. {rec.get('category', 'N/A')} ({rec.get('priority', 'Medium')} Priority)</b><br/>
                {rec.get('recommendation', 'N/A')}<br/>
                <i>Potential Impact:</i> {rec.get('potential_impact', 'N/A')}<br/>
                """
                story.append(Paragraph(rec_text, self.styles['HighlightBox']))
                story.append(Spacer(1, 10))

        return story
    def _create_comprehensive_data_analysis(self):
        """Create comprehensive data analysis section"""
        story = []
        story.append(Paragraph("Comprehensive Data Analysis", self.styles['Heading1']))
        story.append(Spacer(1, 12))
        
        summary_stats = self.report_gen.get_summary_statistics()
        detailed_data = [
            ["Metric Category", "Value", "Units", "Analysis"],
            ["Total GHG Emissions", f"{summary_stats.get('total_emissions', 0):,.0f}", "tCO2e", "Annual footprint"],
            ["Scope 1 (Direct)", f"{summary_stats.get('scope1_total', 0):,.0f}", "tCO2e", f"{summary_stats.get('scope1_pct', 0):.1f}% of total"],
            ["Scope 2 (Energy)", f"{summary_stats.get('scope2_total', 0):,.0f}", "tCO2e", f"{summary_stats.get('scope2_pct', 0):.1f}% of total"],
            ["Scope 3 (Indirect)", f"{summary_stats.get('scope3_total', 0):,.0f}", "tCO2e", f"{summary_stats.get('scope3_pct', 0):.1f}% of total"],
            ["Carbon Intensity", f"{summary_stats.get('carbon_intensity', 0):.4f}", "tCO2e/barrel", "Efficiency"],
            ["Facilities", f"{summary_stats.get('total_facilities', 0)}", "count", "Sites"]
        ]
        
        table = Table(detailed_data, colWidths=[1.8*inch, 1.2*inch, 0.8*inch, 2.2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E86C1')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ]))
        story.append(table)
        return story

    def _create_scope_analysis(self):
        """Create scope analysis section"""
        story = []
        story.append(Paragraph("Scope-by-Scope Analysis", self.styles['Heading1']))
        story.append(Spacer(1, 15))

        summary_stats = self.report_gen.get_summary_statistics()

        analysis_text = f"""
        <b>Scope 1 (Direct Emissions): {summary_stats.get('scope1_total', 0):,.0f} tCO2e</b><br/>
        Direct emissions from owned or controlled sources including combustion equipment, process emissions,
        and fugitive releases. These emissions are under direct operational control and represent
        {summary_stats.get('scope1_pct', 0):.1f}% of total emissions.<br/><br/>

        <b>Scope 2 (Energy Indirect): {summary_stats.get('scope2_total', 0):,.0f} tCO2e</b><br/>
        Emissions from purchased electricity, steam, heat, and cooling consumed by the organization.
        These emissions occur at the facility where energy is generated but are attributed to the
        energy consumer. Represents {summary_stats.get('scope2_pct', 0):.1f}% of total emissions.<br/><br/>

        <b>Scope 3 (Other Indirect): {summary_stats.get('scope3_total', 0):,.0f} tCO2e</b><br/>
        All other indirect emissions in the value chain including suppliers, transportation,
        waste, and end-of-life treatment of products. These emissions occur in the value chain
        and represent {summary_stats.get('scope3_pct', 0):.1f}% of total emissions.
        """
        story.append(Paragraph(analysis_text, self.styles['Normal']))
        story.append(Spacer(1, 15))
        return story

    def _create_facility_analysis(self):
        """Create facility analysis section"""
        story = []
        story.append(Paragraph("Facility Analysis", self.styles['Heading1']))
        story.append(Spacer(1, 15))

        summary_stats = self.report_gen.get_summary_statistics()

        analysis_text = f"""
        <b>Multi-facility Performance Overview</b><br/>
        The organization operates {summary_stats.get('total_facilities', 0)} facilities with varying
        emission profiles. Analysis of emissions across operational sites reveals opportunities for
        best-practice sharing and targeted improvements.<br/><br/>

        Each facility's contribution to total emissions has been assessed, with site-specific
        recommendations developed for high-emission locations. Energy intensity metrics enable
        performance comparison across sites and identification of efficiency opportunities.
        """
        story.append(Paragraph(analysis_text, self.styles['Normal']))
        story.append(Spacer(1, 15))
        return story

    def _create_energy_analysis(self):
        """Create energy analysis section"""
        story = []
        story.append(Paragraph("Energy Management Analysis", self.styles['Heading1']))
        story.append(Spacer(1, 15))

        analysis_text = """
        <b>Energy-GHG Correlation</b><br/>
        Energy consumption directly correlates with GHG emissions, making energy management
        critical for carbon reduction strategies. The organization's energy mix, consumption
        patterns, and intensity metrics have been analyzed to identify optimization opportunities.<br/><br/>

        Key areas for improvement include transitioning to renewable energy sources, implementing
        energy efficiency measures, and optimizing production processes to reduce energy intensity.
        Best practices from ISO 50001 energy management standards have been considered in developing
        recommendations for energy performance improvement.
        """
        story.append(Paragraph(analysis_text, self.styles['Normal']))
        story.append(Spacer(1, 15))
        return story

    def _create_performance_targets(self):
        """Create performance targets section"""
        story = []
        story.append(Paragraph("Performance Targets & Goals", self.styles['Heading1']))
        story.append(Spacer(1, 15))

        analysis_text = """
        <b>Target Framework and Objectives</b><br/>
        The organization has established science-based targets aligned with international climate
        goals and industry best practices. These targets provide a roadmap for continuous improvement
        in GHG performance and demonstrate commitment to environmental stewardship.<br/><br/>

        Target categories include absolute emission reductions, intensity improvements, and
        renewable energy adoption. Progress is tracked quarterly with annual verification and
        reporting to stakeholders. Targets are reviewed regularly to ensure alignment with
        evolving climate science and regulatory requirements.
        """
        story.append(Paragraph(analysis_text, self.styles['Normal']))
        story.append(Spacer(1, 15))
        return story

    def _create_methodology_section(self):
        """Create methodology section"""
        story = []
        story.append(Paragraph("Methodology & Standards", self.styles['Heading1']))
        story.append(Spacer(1, 15))

        methodology_text = """
        <b>GHG Protocol Compliance</b><br/>
        This report has been prepared following the GHG Protocol Corporate Accounting and Reporting
        Standard, the most widely used international framework for corporate GHG inventories.
        Emission factors are based on IPCC guidelines and country-specific data where available.<br/><br/>

        <b>Data Quality and Uncertainty</b><br/>
        Data quality varies by scope with estimated uncertainty of ±5% for Scope 1 direct measurements,
        ±10% for Scope 2 utility-based calculations, and ±20% for Scope 3 estimated values.
        Continuous improvement processes are in place to enhance data accuracy.<br/><br/>

        <b>Verification and Assurance</b><br/>
        Internal data quality reviews and validation procedures have been applied throughout
        the inventory development process. Selected emissions categories have undergone limited
        external assurance by qualified third-party verifiers.
        """
        story.append(Paragraph(methodology_text, self.styles['Normal']))
        story.append(Spacer(1, 30))

        # Footer signature
        footer_text = """
        <para align="center">
        <i>Developed by Amsamms</i>
        </para>
        """
        story.append(Paragraph(footer_text, self.styles['Normal']))
        story.append(Spacer(1, 15))
        return story
