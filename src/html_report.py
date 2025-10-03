import plotly
import plotly.graph_objects as go
from jinja2 import Template
import json
import base64
import os
from datetime import datetime
from report_generator import GHGReportGenerator

class HTMLReportGenerator:
    def __init__(self, report_generator):
        self.report_gen = report_generator

    def _get_logo_base64(self):
        """Convert logo to base64 for embedding in HTML"""
        # Get the directory where this script is located (src/)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Go up one level to ghg_reporting_system/ then into assets/
        logo_path = os.path.join(script_dir, "..", "assets", "epromlogo-scaled.gif")
        logo_path = os.path.normpath(logo_path)  # Normalize the path

        try:
            if os.path.exists(logo_path):
                with open(logo_path, 'rb') as f:
                    logo_data = base64.b64encode(f.read()).decode('utf-8')
                    return f"data:image/gif;base64,{logo_data}"
        except Exception as e:
            print(f"Error loading logo: {e}")
        return None

    def generate_html_report(self, output_path, facility_filter=None, use_ai=False):
        """Generate interactive HTML report

        Args:
            output_path: Path to save HTML file
            facility_filter: Optional facility name to filter data
            use_ai: If True, use AI-generated recommendations
        """
        try:
            # Get all charts and data with facility filtering
            charts = self._generate_all_charts(facility_filter)
            recommendations = self.report_gen.generate_recommendations(use_ai=use_ai)
            summary_stats = self.report_gen.get_summary_statistics(facility_filter)
            logo_base64 = self._get_logo_base64()
            custom_text = self.report_gen.get_custom_text()

            # Create HTML template
            html_template = self._create_html_template()

            # Render template with data
            template = Template(html_template)
            html_content = template.render(
                charts=charts,
                recommendations=recommendations,
                summary_stats=summary_stats,
                logo_base64=logo_base64,
                custom_text=custom_text,
                report_date=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            )

            # Write to file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)

            return True
        except Exception as e:
            print(f"Error generating HTML report: {e}")
            return False

    def _generate_all_charts(self, facility_filter=None):
        """Generate all charts as HTML divs

        Args:
            facility_filter: Optional facility name to filter data
        """
        charts = {}

        # Scope comparison chart
        scope_chart = self.report_gen.create_scope_comparison_chart(facility_filter)
        if scope_chart:
            charts['scope_comparison'] = plotly.io.to_html(scope_chart, include_plotlyjs=False, div_id="scope-comparison-chart", config={'displayModeBar': True})

        # Monthly trend chart
        trend_chart = self.report_gen.create_monthly_trend_chart(facility_filter)
        if trend_chart:
            charts['monthly_trend'] = plotly.io.to_html(trend_chart, include_plotlyjs=False, div_id="monthly-trend-chart", config={'displayModeBar': True})

        # Sankey diagram - with proper configuration for better rendering
        # Using threshold_percent=80 as default
        sankey_chart = self.report_gen.create_sankey_diagram(facility_filter, threshold_percent=80)
        if sankey_chart:
            charts['sankey'] = plotly.io.to_html(
                sankey_chart,
                include_plotlyjs=False,
                div_id="sankey-chart",
                config={'displayModeBar': True, 'responsive': True}
            )

        # Facility breakdown
        facility_chart = self.report_gen.create_facility_breakdown_chart()
        if facility_chart:
            charts['facility_breakdown'] = plotly.io.to_html(facility_chart, include_plotlyjs=False, div_id="facility-chart", config={'displayModeBar': True})

        # Emission By Source
        emission_chart = self.report_gen.create_emission_by_source_chart()
        if emission_chart:
            charts['emission_by_source'] = plotly.io.to_html(emission_chart, include_plotlyjs=False, div_id="emission-chart", config={'displayModeBar': True})

        return charts

    def _create_html_template(self):
        """Create comprehensive HTML template"""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EPROM GHG Emissions Report - {{ summary_stats.company_name }}</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            min-height: 100vh;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }

        .header {
            background: linear-gradient(135deg, #2E86C1 0%, #1B4F72 100%);
            color: white;
            padding: 2rem;
            text-align: center;
        }

        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }

        .header p {
            font-size: 1.2rem;
            opacity: 0.9;
        }

        .nav {
            background: #34495e;
            padding: 1rem 0;
            position: sticky;
            top: 0;
            z-index: 100;
        }

        .nav ul {
            list-style: none;
            display: flex;
            justify-content: center;
            flex-wrap: wrap;
        }

        .nav li {
            margin: 0 1rem;
        }

        .nav a {
            color: white;
            text-decoration: none;
            padding: 0.5rem 1rem;
            border-radius: 5px;
            transition: background 0.3s;
        }

        .nav a:hover {
            background: #2c3e50;
        }

        .content {
            padding: 2rem;
        }

        .section {
            margin-bottom: 3rem;
        }

        .section h2 {
            color: #2E86C1;
            font-size: 2rem;
            margin-bottom: 1rem;
            border-bottom: 3px solid #2E86C1;
            padding-bottom: 0.5rem;
        }

        .kpi-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }

        .kpi-card {
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            padding: 1.5rem;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: transform 0.3s;
        }

        .kpi-card:hover {
            transform: translateY(-5px);
        }

        .kpi-card i {
            font-size: 2rem;
            color: #2E86C1;
            margin-bottom: 0.5rem;
        }

        .kpi-card h3 {
            color: #2E86C1;
            margin-bottom: 0.5rem;
        }

        .kpi-card .value {
            font-size: 1.5rem;
            font-weight: bold;
            color: #2c3e50;
        }

        .chart-container {
            background: white;
            border-radius: 10px;
            padding: 1rem;
            margin: 1rem 0;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }

        .recommendations {
            display: grid;
            gap: 1rem;
        }

        .recommendation-card {
            background: white;
            border-left: 4px solid #2E86C1;
            padding: 1.5rem;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }

        .recommendation-card.high-priority {
            border-left-color: #e74c3c;
        }

        .recommendation-card.medium-priority {
            border-left-color: #f39c12;
        }

        .recommendation-card.low-priority {
            border-left-color: #27ae60;
        }

        .recommendation-card h4 {
            color: #2c3e50;
            margin-bottom: 0.5rem;
        }

        .recommendation-card .priority {
            display: inline-block;
            padding: 0.25rem 0.5rem;
            border-radius: 3px;
            font-size: 0.8rem;
            font-weight: bold;
            text-transform: uppercase;
            margin-bottom: 0.5rem;
        }

        .priority.high { background: #e74c3c; color: white; }
        .priority.medium { background: #f39c12; color: white; }
        .priority.low { background: #27ae60; color: white; }

        .footer {
            background: #2c3e50;
            color: white;
            text-align: center;
            padding: 2rem;
            margin-top: 3rem;
        }

        .highlight {
            background: linear-gradient(120deg, #a8edea 0%, #fed6e3 100%);
            padding: 1rem;
            border-radius: 10px;
            margin: 1rem 0;
        }

        @media (max-width: 768px) {
            .nav ul {
                flex-direction: column;
                align-items: center;
            }

            .kpi-grid {
                grid-template-columns: 1fr;
            }

            .header h1 {
                font-size: 2rem;
            }
        }

        .methodology {
            background: #f8f9fa;
            padding: 1.5rem;
            border-radius: 10px;
            margin: 1rem 0;
            border: 1px solid #dee2e6;
        }

        .data-table {
            width: 100%;
            border-collapse: collapse;
            margin: 1rem 0;
        }

        .data-table th,
        .data-table td {
            padding: 0.75rem;
            text-align: left;
            border-bottom: 1px solid #dee2e6;
        }

        .data-table th {
            background: #2E86C1;
            color: white;
        }

        .data-table tr:hover {
            background: #f8f9fa;
        }

        .scroll-to-top {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: #2E86C1;
            color: white;
            border: none;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            cursor: pointer;
            display: none;
            z-index: 1000;
            transition: all 0.3s;
        }

        .scroll-to-top:hover {
            background: #1B4F72;
        }

        /* Print-specific CSS for PDF generation */
        @media print {
            body {
                background: white;
            }

            .container {
                max-width: 100% !important;
                width: 100% !important;
            }

            .scroll-to-top {
                display: none !important;
            }

            .section {
                page-break-inside: avoid;
                margin-bottom: 1rem;
            }

            .chart-container {
                page-break-inside: avoid;
                page-break-after: auto;
                margin: 1rem 0;
            }

            .kpi-grid {
                page-break-inside: avoid;
                gap: 1rem;
            }

            .recommendation-card {
                page-break-inside: avoid;
            }

            .methodology {
                page-break-inside: avoid;
            }

            h2 {
                page-break-after: avoid;
            }

            .header {
                page-break-after: avoid;
            }

            .nav {
                display: none;
            }

            .footer {
                page-break-before: auto;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header class="header">
            {% if logo_base64 %}
            <div style="text-align: center; margin-bottom: 1.5rem;">
                <div style="display: inline-block; background: white; padding: 15px 30px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <img src="{{ logo_base64 }}" alt="EPROM Logo" style="max-width: 300px; height: auto; display: block;">
                </div>
            </div>
            {% endif %}
            <h1><i class="fas fa-leaf"></i> EPROM GHG Emissions Report</h1>
            <p>{{ summary_stats.company_name }} - Comprehensive Environmental Assessment</p>
            <small>Generated on {{ report_date }}</small>
        </header>

        <nav class="nav">
            <ul>
                <li><a href="#overview"><i class="fas fa-chart-line"></i> Overview</a></li>
                <li><a href="#scope-analysis"><i class="fas fa-layer-group"></i> Scope Analysis</a></li>
                <li><a href="#facility-analysis"><i class="fas fa-industry"></i> Facilities</a></li>
                <li><a href="#emission-analysis"><i class="fas fa-smog"></i> Emission By Source</a></li>
                <li><a href="#recommendations"><i class="fas fa-lightbulb"></i> Recommendations</a></li>
                <li><a href="#methodology"><i class="fas fa-cogs"></i> Methodology</a></li>
            </ul>
        </nav>

        <div class="content">
            <section id="overview" class="section">
                <h2><i class="fas fa-chart-line"></i> Executive Overview of {{ summary_stats.company_name }}</h2>

                {% if custom_text.company_introduction and custom_text.company_introduction != 'nan' and custom_text.company_introduction|length > 0 %}
                <div class="highlight" style="background: linear-gradient(120deg, #e0f7fa 0%, #b2ebf2 100%); margin-bottom: 2rem;">
                    <h3><i class="fas fa-building"></i> About {{ summary_stats.company_name }}</h3>
                    <p style="white-space: pre-line; line-height: 1.8; text-align: justify;">{{ custom_text.company_introduction }}</p>
                </div>
                {% endif %}

                <div class="kpi-grid">
                    <div class="kpi-card">
                        <i class="fas fa-smog"></i>
                        <h3>Total Emissions</h3>
                        <div class="value">{{ "{:,.0f}".format(summary_stats.total_emissions) }} tCO₂e</div>
                    </div>
                    <div class="kpi-card">
                        <i class="fas fa-fire"></i>
                        <h3>Scope 1 (Direct)</h3>
                        <div class="value">{{ "{:,.0f}".format(summary_stats.scope1_total) }} tCO₂e</div>
                        <small>{{ "{:.1f}".format(summary_stats.scope1_pct) }}%</small>
                    </div>
                    <div class="kpi-card">
                        <i class="fas fa-plug"></i>
                        <h3>Scope 2 (Energy)</h3>
                        <div class="value">{{ "{:,.0f}".format(summary_stats.scope2_total) }} tCO₂e</div>
                        <small>{{ "{:.1f}".format(summary_stats.scope2_pct) }}%</small>
                    </div>
                    <div class="kpi-card">
                        <i class="fas fa-link"></i>
                        <h3>Scope 3 (Indirect)</h3>
                        <div class="value">{{ "{:,.0f}".format(summary_stats.scope3_total) }} tCO₂e</div>
                        <small>{{ "{:.1f}".format(summary_stats.scope3_pct) }}%</small>
                    </div>
                    <div class="kpi-card">
                        <i class="fas fa-industry"></i>
                        <h3>Facilities</h3>
                        <div class="value">{{ summary_stats.total_facilities }}</div>
                        {% if summary_stats.facility_names %}
                        <small style="display: block; margin-top: 8px; line-height: 1.4;">
                            {% for facility in summary_stats.facility_names %}
                                {{ facility }}{% if not loop.last %}, {% endif %}
                            {% endfor %}
                        </small>
                        {% endif %}
                    </div>
                    <div class="kpi-card">
                        <i class="fas fa-tachometer-alt"></i>
                        <h3>Carbon Intensity</h3>
                        <div class="value">{{ "{:.4f}".format(summary_stats.carbon_intensity) }}</div>
                        <small>tCO₂e/barrel</small>
                    </div>
                </div>

                <div class="highlight">
                    <h3><i class="fas fa-info-circle"></i> Executive Overview of {{ summary_stats.company_name }}</h3>
                    <p>This comprehensive GHG assessment provides a detailed analysis of {{ summary_stats.company_name }}'s carbon footprint across all operational scopes. The report identifies key emission sources, tracks performance against industry benchmarks, and provides actionable recommendations for emission reduction strategies.</p>
                </div>
            </section>

            <section id="scope-analysis" class="section">
                <h2><i class="fas fa-layer-group"></i> Scope-wise Emission Analysis</h2>

                {% if charts.scope_comparison %}
                <div class="chart-container">
                    <h3>Emissions by Scope</h3>
                    {{ charts.scope_comparison | safe }}
                </div>
                {% endif %}

                {% if charts.monthly_trend %}
                <div class="chart-container">
                    <h3>Monthly Emission Trends</h3>
                    {{ charts.monthly_trend | safe }}
                </div>
                {% endif %}

                {% if charts.sankey %}
                <div class="chart-container">
                    <h3>Emission Flow Analysis (Sankey Diagram)</h3>
                    {{ charts.sankey | safe }}
                </div>
                {% endif %}

                <div class="methodology">
                    <h4><i class="fas fa-info"></i> Scope Definitions</h4>
                    <ul>
                        <li><strong>Scope 1 (Direct):</strong> Emissions from sources owned or controlled by the organization</li>
                        <li><strong>Scope 2 (Energy Indirect):</strong> Emissions from purchased electricity, steam, heat, and cooling</li>
                        <li><strong>Scope 3 (Other Indirect):</strong> All other indirect emissions in the value chain</li>
                    </ul>
                </div>
            </section>

            <section id="facility-analysis" class="section">
                <h2><i class="fas fa-industry"></i> Facility Performance Analysis</h2>

                {% if charts.facility_breakdown %}
                <div class="chart-container">
                    <h3>Facility-wise Breakdown</h3>
                    {{ charts.facility_breakdown | safe }}
                </div>
                {% endif %}

                <div class="highlight">
                    <h3><i class="fas fa-chart-bar"></i> Facility Performance Insights</h3>
                    <p>The facility analysis reveals varying emission intensities across operational sites. Refineries show higher absolute emissions due to energy-intensive processes, while distribution centers exhibit more consistent patterns. This analysis helps identify optimization opportunities and benchmark performance across similar facilities.</p>
                </div>
            </section>

            <section id="emission-analysis" class="section">
                <h2><i class="fas fa-smog"></i> Emission By Source</h2>

                {% if charts.emission_by_source %}
                <div class="chart-container">
                    <h3>Emission Distribution and Analysis</h3>
                    {{ charts.emission_by_source | safe }}
                </div>
                {% endif %}

                <div class="methodology">
                    <h4><i class="fas fa-cog"></i> Emission Source Analysis</h4>
                    <p>This analysis identifies major emission sources from energy-related activities and their contribution to the total GHG footprint. This approach enables targeted emission reduction strategies and strategic transitions to lower-carbon energy sources.</p>
                </div>
            </section>

            <section id="recommendations" class="section">
                <h2><i class="fas fa-lightbulb"></i> Strategic Recommendations</h2>

                <div class="recommendations">
                    {% for rec in recommendations %}
                    <div class="recommendation-card {{ rec.priority.lower() }}-priority">
                        <span class="priority {{ rec.priority.lower() }}">{{ rec.priority }} Priority</span>
                        <h4>{{ rec.category }}</h4>
                        <p>{{ rec.recommendation }}</p>
                        <div style="margin-top: 1rem;">
                            <strong>Potential Impact:</strong> {{ rec.potential_impact }}
                        </div>
                    </div>
                    {% endfor %}
                </div>

                <div class="highlight">
                    <h3><i class="fas fa-road"></i> Implementation Roadmap</h3>
                    <p>These recommendations should be implemented in phases, prioritizing high-impact, quick-win opportunities while developing longer-term strategic initiatives. A dedicated sustainability team should oversee implementation and track progress against established targets.</p>
                </div>
            </section>

            <section id="methodology" class="section">
                <h2><i class="fas fa-cogs"></i> Methodology & Standards</h2>

                <div class="methodology">
                    <h4><i class="fas fa-book"></i> Reporting Standards</h4>
                    <p>This GHG inventory follows the <strong>GHG Protocol Corporate Accounting and Reporting Standard</strong>, the most widely used international standard for corporate GHG emissions accounting. Emission factors are based on the latest IPCC guidelines and country-specific factors where available.</p>
                </div>

                <div class="methodology">
                    <h4><i class="fas fa-database"></i> Data Quality Assessment</h4>
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Scope</th>
                                <th>Data Source</th>
                                <th>Quality Level</th>
                                <th>Uncertainty</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>Scope 1</td>
                                <td>Direct measurements, fuel records</td>
                                <td>High</td>
                                <td>±5%</td>
                            </tr>
                            <tr>
                                <td>Scope 2</td>
                                <td>Utility bills, energy meters</td>
                                <td>High</td>
                                <td>±10%</td>
                            </tr>
                            <tr>
                                <td>Scope 3</td>
                                <td>Estimates, supplier data</td>
                                <td>Medium</td>
                                <td>±20%</td>
                            </tr>
                        </tbody>
                    </table>
                </div>

                <div class="methodology">
                    <h4><i class="fas fa-shield-alt"></i> Verification & Assurance</h4>
                    <p>All Scope 1 and Scope 2 emissions have been internally verified. Selected Scope 3 categories have undergone limited external assurance. The report follows international best practices for GHG data management and quality assurance.</p>
                </div>
            </section>

            {% if custom_text.conclusion_text and custom_text.conclusion_text != 'nan' and custom_text.conclusion_text|length > 0 %}
            <section id="conclusion" class="section">
                <h2><i class="fas fa-flag-checkered"></i> Conclusion & Final Notes</h2>
                <div class="highlight" style="background: linear-gradient(120deg, #fff9c4 0%, #fff59d 100%);">
                    <p style="white-space: pre-line; line-height: 1.8; text-align: justify; font-size: 1.05rem;">{{ custom_text.conclusion_text }}</p>
                </div>
            </section>
            {% endif %}
        </div>

        <footer class="footer">
            <p>&copy; {{ summary_stats.reporting_year }} {{ summary_stats.company_name }} - Sustainability Reporting</p>
            <p>Generated by EPROM with Advanced GHG Reporting System</p>
            <p style="margin-top: 10px; font-style: italic;">Developed by Amsamms</p>
        </footer>
    </div>

    <button class="scroll-to-top" onclick="scrollToTop()">
        <i class="fas fa-arrow-up"></i>
    </button>

    <script>
        // Smooth scrolling for navigation links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                document.querySelector(this.getAttribute('href')).scrollIntoView({
                    behavior: 'smooth'
                });
            });
        });

        // Show/hide scroll to top button
        window.addEventListener('scroll', function() {
            const scrollButton = document.querySelector('.scroll-to-top');
            if (window.pageYOffset > 300) {
                scrollButton.style.display = 'block';
            } else {
                scrollButton.style.display = 'none';
            }
        });

        function scrollToTop() {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        }

        // Add animation to KPI cards
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver(function(entries) {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.animation = 'fadeInUp 0.6s ease forwards';
                }
            });
        }, observerOptions);

        document.querySelectorAll('.kpi-card, .recommendation-card').forEach(card => {
            observer.observe(card);
        });

        // Add CSS animation
        const style = document.createElement('style');
        style.textContent = `
            @keyframes fadeInUp {
                from {
                    opacity: 0;
                    transform: translateY(30px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
        `;
        document.head.appendChild(style);
    </script>
</body>
</html>
        """