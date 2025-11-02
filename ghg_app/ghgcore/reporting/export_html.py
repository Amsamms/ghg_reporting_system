"""
HTML report export using Jinja2 templates.
"""

from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path
from typing import Dict, Any
import json


def get_jinja_env() -> Environment:
    """Get configured Jinja2 environment."""
    template_dir = Path(__file__).parent / "templates"

    env = Environment(
        loader=FileSystemLoader(template_dir),
        autoescape=select_autoescape(['html', 'xml'])
    )

    # Add custom filters
    env.filters['tojson'] = lambda x: json.dumps(x, default=str)
    env.filters['format_number'] = lambda x: f"{x:,.2f}" if x else "0.00"
    env.filters['format_pct'] = lambda x: f"{x:.1f}%" if x else "0.0%"

    return env


def export_html_report(
    context: Dict[str, Any],
    output_path: Path,
    template_name: str = "base.html",
) -> Path:
    """
    Export HTML report from context.

    Args:
        context: Report context dictionary
        output_path: Output file path
        template_name: Jinja2 template name

    Returns:
        Path to generated HTML file
    """

    env = get_jinja_env()

    # Load template
    template = env.get_template(template_name)

    # Render
    html_content = template.render(**context)

    # Write to file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html_content, encoding='utf-8')

    return output_path


def generate_plotly_chart_html(chart_data: Dict[str, Any], chart_type: str = "bar") -> str:
    """
    Generate Plotly chart HTML snippet.

    Args:
        chart_data: Data for chart
        chart_type: Chart type (bar, pie, sankey, etc.)

    Returns:
        HTML string with embedded Plotly chart
    """

    chart_id = f"chart_{id(chart_data)}"

    html = f"""
    <div id="{chart_id}" class="chart-container"></div>
    <script>
        var data = {json.dumps(chart_data['data'])};
        var layout = {json.dumps(chart_data.get('layout', {}))};
        Plotly.newPlot('{chart_id}', data, layout, {{responsive: true}});
    </script>
    """

    return html


def create_scope_breakdown_chart(by_scope: Dict) -> Dict[str, Any]:
    """Create Plotly data for scope breakdown chart."""

    labels = [f"Scope {scope}" for scope in sorted(by_scope.keys())]
    values = [data.get('_total_co2e_kg', 0) / 1000 for scope, data in sorted(by_scope.items())]

    return {
        'data': [{
            'type': 'pie',
            'labels': labels,
            'values': values,
            'hole': 0.3,
            'marker': {
                'colors': ['#d62728', '#ff7f0e', '#2ca02c']
            }
        }],
        'layout': {
            'title': 'Emissions by Scope (tCO₂e)',
            'showlegend': True,
        }
    }


def create_monthly_trend_chart(by_month: Dict) -> Dict[str, Any]:
    """Create Plotly data for monthly trend chart."""

    months = list(by_month.keys())
    values = [data.get('_total_co2e_kg', 0) / 1000 for data in by_month.values()]

    return {
        'data': [{
            'type': 'scatter',
            'mode': 'lines+markers',
            'x': months,
            'y': values,
            'name': 'Monthly Emissions',
            'line': {'color': '#2c5f2d', 'width': 3},
            'marker': {'size': 8}
        }],
        'layout': {
            'title': 'Monthly Emissions Trend (tCO₂e)',
            'xaxis': {'title': 'Month'},
            'yaxis': {'title': 'Emissions (tCO₂e)'},
        }
    }


def create_sankey_chart(sankey_data: Dict) -> Dict[str, Any]:
    """Create Plotly data for Sankey diagram."""

    return {
        'data': [{
            'type': 'sankey',
            'node': {
                'label': sankey_data['labels'],
                'color': '#2c5f2d',
                'pad': 15,
                'thickness': 20,
            },
            'link': {
                'source': sankey_data['sources'],
                'target': sankey_data['targets'],
                'value': sankey_data['values'],
            }
        }],
        'layout': {
            'title': 'Emissions Flow Diagram',
            'font': {'size': 12},
        }
    }
