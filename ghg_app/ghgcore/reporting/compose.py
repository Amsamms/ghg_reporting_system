"""
Report composition - builds the context dictionary for report generation.
Aggregates data from database and calculation engine.
"""

from typing import Dict, Any
from sqlmodel import Session
from datetime import date, datetime
from ..models import Organization, Facility
from ..engine.aggregation import (
    aggregate_by_scope,
    aggregate_by_subcategory,
    aggregate_by_facility,
    aggregate_by_month,
    get_summary_totals,
)
from ..engine.checks import run_all_checks
from ..engine.uncertainty import uncertainty_by_scope


def compose_report_context(
    session: Session,
    org_id: int,
    year: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Compose complete report context from database and calculations.

    Args:
        session: Database session
        org_id: Organization ID
        year: Reporting year (defaults to current year)

    Returns:
        Dictionary with all report data
    """

    if year is None:
        year = datetime.now().year

    # Get organization
    org = session.get(Organization, org_id)
    if not org:
        raise ValueError(f"Organization {org_id} not found")

    # Get facilities
    facilities = session.query(Facility).filter(Facility.org_id == org_id).all()

    # Date range
    start_date = org.period_start
    end_date = org.period_end

    # Get summary totals
    summary = get_summary_totals(session, org_id, start_date, end_date)

    # Aggregations
    by_scope = summary['by_scope']
    by_facility = summary['by_facility']
    by_subcategory = summary['by_subcategory']

    # Monthly trend
    by_month = aggregate_by_month(session, org_id, year)

    # Uncertainty analysis
    uncertainty = uncertainty_by_scope(by_scope)

    # QA/QC checks
    qaqc_results = run_all_checks(session, org_id)

    # Compose context
    context = {
        # Organization info
        'organization': {
            'id': org.id,
            'name': org.name,
            'country': org.country,
            'sector': org.sector,
            'base_year': org.base_year,
            'gwp_set': org.gwp_set,
            'electricity_method': org.electricity_method,
            'consolidation_approach': org.consolidation_approach,
        },

        # Reporting period
        'year': year,
        'period_start': start_date.isoformat(),
        'period_end': end_date.isoformat(),
        'generation_date': datetime.now().isoformat(),

        # Facilities
        'facilities': [
            {
                'name': f.name,
                'lat': f.lat,
                'lon': f.lon,
                'grid_region': f.grid_region,
            }
            for f in facilities
        ],

        # Summary metrics
        'summary': {
            'total_co2e_kg': summary['total_co2e_kg'],
            'total_co2e_tonnes': summary['total_co2e_tonnes'],
            'scope_1_pct': summary['scope_percentages'].get(1, 0),
            'scope_2_pct': summary['scope_percentages'].get(2, 0),
            'scope_3_pct': summary['scope_percentages'].get(3, 0),
        },

        # Detailed breakdowns
        'by_scope': by_scope,
        'by_facility': by_facility,
        'by_subcategory': by_subcategory,
        'by_month': by_month,

        # Uncertainty
        'uncertainty': uncertainty,

        # QA/QC
        'qaqc': qaqc_results,

        # Compliance
        'standards_compliance': {
            'iso_14064_1': True,
            'ghg_protocol': True,
            'gwp_set': org.gwp_set,
        },
    }

    return context


def format_emission_factor_table(session: Session, org_id: int) -> list:
    """
    Generate emission factor table for appendix.

    Args:
        session: Database session
        org_id: Organization ID

    Returns:
        List of emission factor records
    """
    from sqlmodel import select
    from ..models import Calculation, Activity, Facility

    # Get unique emission factors used
    query = (
        select(Calculation)
        .join(Activity, Calculation.activity_id == Activity.id)
        .join(Facility, Activity.facility_id == Facility.id)
        .where(Facility.org_id == org_id)
    )

    results = session.exec(query).all()

    # Extract unique factors from snapshots
    factors_used = []
    seen_codes = set()

    for calc in results:
        factor_snap = calc.factor_snapshot_json

        activity_code = factor_snap.get('activity_code')
        if activity_code not in seen_codes:
            seen_codes.add(activity_code)

            factors_used.append({
                'activity_code': activity_code,
                'activity_name': factor_snap.get('activity_name'),
                'gas': factor_snap.get('gas'),
                'factor_value': factor_snap.get('factor_value'),
                'factor_unit': factor_snap.get('factor_unit'),
                'source_authority': factor_snap.get('source_authority'),
                'source_doc': factor_snap.get('source_doc'),
                'source_year': factor_snap.get('source_year'),
                'citation': factor_snap.get('citation'),
            })

    return sorted(factors_used, key=lambda x: x['activity_code'])


def generate_sankey_data(by_scope: Dict, by_subcategory: Dict) -> Dict[str, Any]:
    """
    Generate data for Sankey diagram (emissions flow).

    Args:
        by_scope: Emissions by scope
        by_subcategory: Emissions by subcategory

    Returns:
        Sankey diagram data for Plotly
    """

    labels = ['Total']
    sources = []
    targets = []
    values = []

    # Add scopes
    scope_names = {1: 'Scope 1', 2: 'Scope 2', 3: 'Scope 3'}
    for scope, data in by_scope.items():
        scope_name = scope_names[scope]
        labels.append(scope_name)

        # Total -> Scope
        sources.append(0)  # Total
        targets.append(len(labels) - 1)  # Scope
        values.append(data.get('_total_co2e_kg', 0) / 1000)  # Convert to tonnes

    # Add subcategories
    for subcat, data in by_subcategory.items():
        labels.append(subcat.replace('_', ' ').title())

        # Find parent scope (simplified - you'd need to track this properly)
        # For now, just link to Scope 1
        sources.append(1)  # Scope 1 index
        targets.append(len(labels) - 1)
        values.append(data.get('_total_co2e_kg', 0) / 1000)

    return {
        'labels': labels,
        'sources': sources,
        'targets': targets,
        'values': values,
    }
