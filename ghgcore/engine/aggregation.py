"""
Aggregation functions for rolling up emissions across activities, facilities, scopes.
"""

from typing import Dict, Any, List, Optional
from sqlmodel import Session, select
from datetime import date, datetime
from ..models import Calculation, Activity, Facility, Source


def aggregate_by_scope(
    session: Session,
    org_id: int,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> Dict[int, Dict[str, float]]:
    """
    Aggregate emissions by GHG Protocol scope.

    Args:
        session: Database session
        org_id: Organization ID
        start_date: Start date filter (optional)
        end_date: End date filter (optional)

    Returns:
        Dictionary: {scope: {'CO2': mass, 'CH4': mass, ..., 'CO2e': total}}
    """

    # Query all calculations for the organization
    query = (
        select(Calculation, Activity, Source)
        .join(Activity, Calculation.activity_id == Activity.id)
        .join(Source, Activity.source_id == Source.id)
        .join(Facility, Activity.facility_id == Facility.id)
        .where(Facility.org_id == org_id)
    )

    if start_date:
        query = query.where(Activity.activity_date >= start_date)
    if end_date:
        query = query.where(Activity.activity_date <= end_date)

    results = session.exec(query).all()

    # Aggregate by scope
    by_scope = {1: {}, 2: {}, 3: {}}

    for calc, activity, source in results:
        scope = source.scope

        # Parse results JSON
        emissions = calc.results_json.get('emissions', {})

        for gas, data in emissions.items():
            mass_kg = data.get('mass_kg', 0)
            co2e_kg = data.get('co2e_kg', 0)

            if gas not in by_scope[scope]:
                by_scope[scope][gas] = {'mass_kg': 0, 'co2e_kg': 0}

            by_scope[scope][gas]['mass_kg'] += mass_kg
            by_scope[scope][gas]['co2e_kg'] += co2e_kg

    # Calculate CO2e totals
    for scope in by_scope:
        total_co2e = sum(data['co2e_kg'] for data in by_scope[scope].values())
        by_scope[scope]['_total_co2e_kg'] = total_co2e

    return by_scope


def aggregate_by_subcategory(
    session: Session,
    org_id: int,
    scope: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> Dict[str, Dict[str, float]]:
    """
    Aggregate emissions by subcategory.

    Args:
        session: Database session
        org_id: Organization ID
        scope: Filter by scope (optional)
        start_date: Start date filter
        end_date: End date filter

    Returns:
        Dictionary: {subcategory: {gas: mass, ...}}
    """

    query = (
        select(Calculation, Activity, Source)
        .join(Activity, Calculation.activity_id == Activity.id)
        .join(Source, Activity.source_id == Source.id)
        .join(Facility, Activity.facility_id == Facility.id)
        .where(Facility.org_id == org_id)
    )

    if scope:
        query = query.where(Source.scope == scope)
    if start_date:
        query = query.where(Activity.activity_date >= start_date)
    if end_date:
        query = query.where(Activity.activity_date <= end_date)

    results = session.exec(query).all()

    by_subcat = {}

    for calc, activity, source in results:
        subcat = source.subcategory

        if subcat not in by_subcat:
            by_subcat[subcat] = {}

        emissions = calc.results_json.get('emissions', {})

        for gas, data in emissions.items():
            mass_kg = data.get('mass_kg', 0)
            co2e_kg = data.get('co2e_kg', 0)

            if gas not in by_subcat[subcat]:
                by_subcat[subcat][gas] = {'mass_kg': 0, 'co2e_kg': 0}

            by_subcat[subcat][gas]['mass_kg'] += mass_kg
            by_subcat[subcat][gas]['co2e_kg'] += co2e_kg

    # Add totals
    for subcat in by_subcat:
        total_co2e = sum(data['co2e_kg'] for data in by_subcat[subcat].values())
        by_subcat[subcat]['_total_co2e_kg'] = total_co2e

    return by_subcat


def aggregate_by_facility(
    session: Session,
    org_id: int,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> Dict[str, Dict[str, float]]:
    """
    Aggregate emissions by facility.

    Args:
        session: Database session
        org_id: Organization ID
        start_date: Start date filter
        end_date: End date filter

    Returns:
        Dictionary: {facility_name: {gas: mass, ...}}
    """

    query = (
        select(Calculation, Activity, Facility)
        .join(Activity, Calculation.activity_id == Activity.id)
        .join(Facility, Activity.facility_id == Facility.id)
        .where(Facility.org_id == org_id)
    )

    if start_date:
        query = query.where(Activity.activity_date >= start_date)
    if end_date:
        query = query.where(Activity.activity_date <= end_date)

    results = session.exec(query).all()

    by_facility = {}

    for calc, activity, facility in results:
        facility_name = facility.name

        if facility_name not in by_facility:
            by_facility[facility_name] = {}

        emissions = calc.results_json.get('emissions', {})

        for gas, data in emissions.items():
            mass_kg = data.get('mass_kg', 0)
            co2e_kg = data.get('co2e_kg', 0)

            if gas not in by_facility[facility_name]:
                by_facility[facility_name][gas] = {'mass_kg': 0, 'co2e_kg': 0}

            by_facility[facility_name][gas]['mass_kg'] += mass_kg
            by_facility[facility_name][gas]['co2e_kg'] += co2e_kg

    # Add totals
    for facility_name in by_facility:
        total_co2e = sum(data['co2e_kg'] for data in by_facility[facility_name].values())
        by_facility[facility_name]['_total_co2e_kg'] = total_co2e

    return by_facility


def aggregate_by_month(
    session: Session,
    org_id: int,
    year: int,
) -> Dict[str, Dict[str, float]]:
    """
    Aggregate emissions by month for trend analysis.

    Args:
        session: Database session
        org_id: Organization ID
        year: Year to aggregate

    Returns:
        Dictionary: {month: {gas: mass, ...}}
    """

    start_date = date(year, 1, 1)
    end_date = date(year, 12, 31)

    query = (
        select(Calculation, Activity)
        .join(Activity, Calculation.activity_id == Activity.id)
        .join(Facility, Activity.facility_id == Facility.id)
        .where(Facility.org_id == org_id)
        .where(Activity.activity_date >= start_date)
        .where(Activity.activity_date <= end_date)
    )

    results = session.exec(query).all()

    by_month = {}

    for calc, activity in results:
        month_key = activity.activity_date.strftime('%Y-%m')

        if month_key not in by_month:
            by_month[month_key] = {}

        emissions = calc.results_json.get('emissions', {})

        for gas, data in emissions.items():
            mass_kg = data.get('mass_kg', 0)
            co2e_kg = data.get('co2e_kg', 0)

            if gas not in by_month[month_key]:
                by_month[month_key][gas] = {'mass_kg': 0, 'co2e_kg': 0}

            by_month[month_key][gas]['mass_kg'] += mass_kg
            by_month[month_key][gas]['co2e_kg'] += co2e_kg

    # Add totals and sort by month
    for month_key in by_month:
        total_co2e = sum(data['co2e_kg'] for data in by_month[month_key].values())
        by_month[month_key]['_total_co2e_kg'] = total_co2e

    return dict(sorted(by_month.items()))


def get_summary_totals(
    session: Session,
    org_id: int,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> Dict[str, Any]:
    """
    Get summary totals across all dimensions.

    Args:
        session: Database session
        org_id: Organization ID
        start_date: Start date filter
        end_date: End date filter

    Returns:
        Dictionary with comprehensive summary
    """

    by_scope = aggregate_by_scope(session, org_id, start_date, end_date)
    by_facility = aggregate_by_facility(session, org_id, start_date, end_date)
    by_subcategory = aggregate_by_subcategory(session, org_id, None, start_date, end_date)

    # Grand total
    total_co2e = sum(scope_data.get('_total_co2e_kg', 0) for scope_data in by_scope.values())

    # Convert to tonnes
    total_co2e_tonnes = total_co2e / 1000

    return {
        'total_co2e_kg': total_co2e,
        'total_co2e_tonnes': total_co2e_tonnes,
        'by_scope': by_scope,
        'by_facility': by_facility,
        'by_subcategory': by_subcategory,
        'scope_percentages': {
            scope: (data.get('_total_co2e_kg', 0) / total_co2e * 100) if total_co2e > 0 else 0
            for scope, data in by_scope.items()
        },
    }
