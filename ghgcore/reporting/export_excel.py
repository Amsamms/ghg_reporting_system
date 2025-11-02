"""
Excel export for detailed inventory data and verification bundle.
"""

from pathlib import Path
from typing import Dict, Any
import pandas as pd
from datetime import datetime


def export_excel_inventory(
    context: Dict[str, Any],
    output_path: Path,
) -> Path:
    """
    Export detailed inventory to Excel with multiple sheets.

    Args:
        context: Report context
        output_path: Output Excel file path

    Returns:
        Path to generated Excel file
    """

    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        # Summary sheet
        summary_data = {
            'Metric': [
                'Organization',
                'Reporting Period Start',
                'Reporting Period End',
                'Total Emissions (tCO₂e)',
                'Scope 1 (tCO₂e)',
                'Scope 2 (tCO₂e)',
                'Scope 3 (tCO₂e)',
                'GWP Set',
                'Consolidation Approach',
            ],
            'Value': [
                context['organization']['name'],
                context['period_start'],
                context['period_end'],
                f"{context['summary']['total_co2e_tonnes']:,.2f}",
                f"{context['summary']['scope_1_pct']:.1f}%",
                f"{context['summary']['scope_2_pct']:.1f}%",
                f"{context['summary']['scope_3_pct']:.1f}%",
                context['organization']['gwp_set'],
                context['organization']['consolidation_approach'],
            ]
        }
        df_summary = pd.DataFrame(summary_data)
        df_summary.to_excel(writer, sheet_name='Summary', index=False)

        # Scope breakdown
        scope_data = []
        for scope, data in context['by_scope'].items():
            total_co2e = data.get('_total_co2e_kg', 0) / 1000

            scope_data.append({
                'Scope': f"Scope {scope}",
                'Total CO₂e (tonnes)': total_co2e,
                'Percentage': context['summary'].get(f'scope_{scope}_pct', 0),
            })

        df_scope = pd.DataFrame(scope_data)
        df_scope.to_excel(writer, sheet_name='By Scope', index=False)

        # Subcategory breakdown
        subcat_data = []
        for subcat, data in context['by_subcategory'].items():
            total_co2e = data.get('_total_co2e_kg', 0) / 1000

            subcat_data.append({
                'Subcategory': subcat.replace('_', ' ').title(),
                'Total CO₂e (tonnes)': total_co2e,
            })

        df_subcat = pd.DataFrame(subcat_data)
        df_subcat.to_excel(writer, sheet_name='By Subcategory', index=False)

        # Facility breakdown
        facility_data = []
        for facility, data in context['by_facility'].items():
            total_co2e = data.get('_total_co2e_kg', 0) / 1000

            facility_data.append({
                'Facility': facility,
                'Total CO₂e (tonnes)': total_co2e,
            })

        df_facility = pd.DataFrame(facility_data)
        df_facility.to_excel(writer, sheet_name='By Facility', index=False)

        # Monthly trend
        monthly_data = []
        for month, data in context['by_month'].items():
            total_co2e = data.get('_total_co2e_kg', 0) / 1000

            monthly_data.append({
                'Month': month,
                'Total CO₂e (tonnes)': total_co2e,
            })

        df_monthly = pd.DataFrame(monthly_data)
        df_monthly.to_excel(writer, sheet_name='Monthly Trend', index=False)

        # QA/QC Results
        qaqc = context['qaqc']
        qaqc_data = {
            'Check Category': ['Total Issues', 'Errors', 'Warnings', 'Info', 'Overall Status'],
            'Result': [
                qaqc['summary']['total_issues'],
                qaqc['summary']['errors'],
                qaqc['summary']['warnings'],
                qaqc['summary']['info'],
                'PASSED' if qaqc['passed'] else 'FAILED',
            ]
        }
        df_qaqc = pd.DataFrame(qaqc_data)
        df_qaqc.to_excel(writer, sheet_name='QA-QC Summary', index=False)

        # QA/QC Issues Detail
        if qaqc['issues']:
            issues_data = []
            for issue in qaqc['issues']:
                issues_data.append({
                    'Check': issue['check'],
                    'Severity': issue['severity'],
                    'Message': issue['message'],
                    'Entity ID': issue.get('entity_id', ''),
                })

            df_issues = pd.DataFrame(issues_data)
            df_issues.to_excel(writer, sheet_name='QA-QC Issues', index=False)

    return output_path


def export_verification_bundle(
    context: Dict[str, Any],
    output_dir: Path,
) -> Dict[str, Path]:
    """
    Export complete verification bundle with all supporting files.

    Args:
        context: Report context
        output_dir: Output directory

    Returns:
        Dictionary of generated file paths
    """

    output_dir.mkdir(parents=True, exist_ok=True)

    files = {}

    # Excel inventory
    excel_path = output_dir / "inventory_detailed.xlsx"
    export_excel_inventory(context, excel_path)
    files['inventory_excel'] = excel_path

    # Context JSON (for reproducibility)
    import json
    json_path = output_dir / "calculation_inputs.json"
    json_path.write_text(json.dumps(context, indent=2, default=str))
    files['inputs_json'] = json_path

    # Manifest file
    manifest_data = {
        'Generated': datetime.now().isoformat(),
        'Organization': context['organization']['name'],
        'Reporting Period': f"{context['period_start']} to {context['period_end']}",
        'Total Emissions (tCO₂e)': context['summary']['total_co2e_tonnes'],
        'Files Included': list(files.keys()),
        'Standards Compliance': context['standards_compliance'],
    }

    manifest_path = output_dir / "verification_manifest.json"
    manifest_path.write_text(json.dumps(manifest_data, indent=2, default=str))
    files['manifest'] = manifest_path

    return files
