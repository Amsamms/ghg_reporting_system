"""
QA/QC checks for data quality and completeness.
Implements validation rules per GHG Protocol and ISO 14064-1.
"""

from typing import List, Dict, Any, Tuple
from sqlmodel import Session, select
from ..models import Activity, EmissionFactor, Calculation, Facility, Source
from datetime import date


class QAQCCheck:
    """Base class for QA/QC checks."""

    def __init__(self, name: str, severity: str = "warning"):
        self.name = name
        self.severity = severity  # "error", "warning", "info"
        self.issues = []

    def add_issue(self, message: str, entity_id: Optional[int] = None):
        """Add an issue found during check."""
        self.issues.append({
            'check': self.name,
            'severity': self.severity,
            'message': message,
            'entity_id': entity_id,
        })

    def clear(self):
        """Clear issues list."""
        self.issues = []


def check_missing_data(session: Session, org_id: int) -> List[Dict[str, Any]]:
    """
    Check for activities with missing or incomplete data.

    Args:
        session: Database session
        org_id: Organization ID

    Returns:
        List of issues found
    """

    check = QAQCCheck("Missing Data", "error")

    # Find activities without calculations
    query = (
        select(Activity)
        .join(Facility, Activity.facility_id == Facility.id)
        .where(Facility.org_id == org_id)
        .where(~Activity.calculations.any())
    )

    activities_without_calc = session.exec(query).all()

    for activity in activities_without_calc:
        check.add_issue(
            f"Activity {activity.id} has no calculations",
            entity_id=activity.id
        )

    # Find activities with missing emission factors
    all_activities = (
        select(Activity)
        .join(Facility, Activity.facility_id == Facility.id)
        .where(Facility.org_id == org_id)
    )

    for activity in session.exec(all_activities).all():
        if not activity.units_json.get('quantity'):
            check.add_issue(
                f"Activity {activity.id} missing quantity data",
                entity_id=activity.id
            )

        if not activity.units_json.get('unit'):
            check.add_issue(
                f"Activity {activity.id} missing unit specification",
                entity_id=activity.id
            )

    return check.issues


def check_negative_values(session: Session, org_id: int) -> List[Dict[str, Any]]:
    """
    Check for negative emission values (physical impossibility).

    Args:
        session: Database session
        org_id: Organization ID

    Returns:
        List of issues
    """

    check = QAQCCheck("Negative Values", "error")

    query = (
        select(Calculation, Activity)
        .join(Activity, Calculation.activity_id == Activity.id)
        .join(Facility, Activity.facility_id == Facility.id)
        .where(Facility.org_id == org_id)
    )

    for calc, activity in session.exec(query).all():
        total_co2e = calc.results_json.get('total_co2e_kg', 0)

        if total_co2e < 0:
            check.add_issue(
                f"Calculation {calc.id} has negative CO2e: {total_co2e} kg",
                entity_id=calc.id
            )

        # Check individual gases
        emissions = calc.results_json.get('emissions', {})
        for gas, data in emissions.items():
            mass = data.get('mass_kg', 0)
            if mass < 0:
                check.add_issue(
                    f"Calculation {calc.id} has negative {gas}: {mass} kg",
                    entity_id=calc.id
                )

    return check.issues


def check_outliers(session: Session, org_id: int) -> List[Dict[str, Any]]:
    """
    Check for outlier values using statistical methods.

    Args:
        session: Database session
        org_id: Organization ID

    Returns:
        List of issues
    """

    check = QAQCCheck("Outliers", "warning")

    # Get all calculations by subcategory
    query = (
        select(Calculation, Activity, Source)
        .join(Activity, Calculation.activity_id == Activity.id)
        .join(Source, Activity.source_id == Source.id)
        .join(Facility, Activity.facility_id == Facility.id)
        .where(Facility.org_id == org_id)
    )

    # Group by subcategory
    by_subcategory = {}
    for calc, activity, source in session.exec(query).all():
        subcat = source.subcategory
        if subcat not in by_subcategory:
            by_subcategory[subcat] = []

        co2e = calc.results_json.get('total_co2e_kg', 0)
        by_subcategory[subcat].append({
            'calc_id': calc.id,
            'co2e': co2e,
        })

    # Check for outliers using IQR method
    for subcat, values in by_subcategory.items():
        if len(values) < 4:  # Need minimum data points
            continue

        co2e_values = sorted([v['co2e'] for v in values])

        # Calculate quartiles
        q1_idx = len(co2e_values) // 4
        q3_idx = 3 * len(co2e_values) // 4

        q1 = co2e_values[q1_idx]
        q3 = co2e_values[q3_idx]
        iqr = q3 - q1

        # Outlier thresholds
        lower_bound = q1 - 3 * iqr
        upper_bound = q3 + 3 * iqr

        for val_dict in values:
            co2e = val_dict['co2e']
            if co2e < lower_bound or co2e > upper_bound:
                check.add_issue(
                    f"Calculation {val_dict['calc_id']} in {subcat} is an outlier: {co2e:.2f} kg CO2e "
                    f"(expected range: {lower_bound:.2f} - {upper_bound:.2f})",
                    entity_id=val_dict['calc_id']
                )

    return check.issues


def check_basis_consistency(session: Session, org_id: int) -> List[Dict[str, Any]]:
    """
    Check for HHV/LHV basis consistency within fuel types.

    Args:
        session: Database session
        org_id: Organization ID

    Returns:
        List of issues
    """

    check = QAQCCheck("Basis Consistency", "warning")

    # Get all calculations with their snapshots
    query = (
        select(Calculation, Activity)
        .join(Activity, Calculation.activity_id == Activity.id)
        .join(Facility, Activity.facility_id == Facility.id)
        .where(Facility.org_id == org_id)
    )

    # Group by activity type
    by_activity_type = {}
    for calc, activity in session.exec(query).all():
        act_type = activity.activity_type

        if act_type not in by_activity_type:
            by_activity_type[act_type] = []

        # Extract basis from factor snapshot
        factor_snapshot = calc.factor_snapshot_json
        basis = factor_snapshot.get('basis', 'NA')

        by_activity_type[act_type].append({
            'calc_id': calc.id,
            'basis': basis,
        })

    # Check consistency
    for act_type, calcs in by_activity_type.items():
        bases = set(c['basis'] for c in calcs)

        if len(bases) > 1:
            check.add_issue(
                f"Activity type '{act_type}' uses inconsistent energy basis: {bases}. "
                f"Consider standardizing to HHV or LHV."
            )

    return check.issues


def check_emission_factor_currency(session: Session, org_id: int) -> List[Dict[str, Any]]:
    """
    Check if emission factors are current (not expired).

    Args:
        session: Database session
        org_id: Organization ID

    Returns:
        List of issues
    """

    check = QAQCCheck("Factor Currency", "warning")

    query = (
        select(Calculation, Activity)
        .join(Activity, Calculation.activity_id == Activity.id)
        .join(Facility, Activity.facility_id == Facility.id)
        .where(Facility.org_id == org_id)
    )

    today = date.today()

    for calc, activity in session.exec(query).all():
        factor_snapshot = calc.factor_snapshot_json

        valid_to = factor_snapshot.get('valid_to')
        source_year = factor_snapshot.get('source_year')

        # Check if factor has expired
        if valid_to:
            try:
                valid_to_date = date.fromisoformat(valid_to)
                if valid_to_date < today:
                    check.add_issue(
                        f"Calculation {calc.id} uses expired emission factor (expired: {valid_to})",
                        entity_id=calc.id
                    )
            except:
                pass

        # Warn if factor is > 5 years old
        if source_year and (today.year - source_year) > 5:
            check.add_issue(
                f"Calculation {calc.id} uses emission factor from {source_year} (>5 years old)",
                entity_id=calc.id
            )

    return check.issues


def check_completeness(session: Session, org_id: int) -> Dict[str, Any]:
    """
    Check data completeness across scopes and categories.

    Args:
        session: Database session
        org_id: Organization ID

    Returns:
        Completeness report
    """

    # Get all required sources
    all_sources = session.exec(select(Source)).all()

    # Get sources with activities
    query = (
        select(Source.id)
        .join(Activity, Source.id == Activity.source_id)
        .join(Facility, Activity.facility_id == Facility.id)
        .where(Facility.org_id == org_id)
        .distinct()
    )

    sources_with_data = set(session.exec(query).all())

    # Calculate completeness by scope
    completeness_by_scope = {}

    for scope in [1, 2, 3]:
        scope_sources = [s for s in all_sources if s.scope == scope]
        scope_sources_with_data = [s for s in scope_sources if s.id in sources_with_data]

        completeness_pct = (
            len(scope_sources_with_data) / len(scope_sources) * 100
            if scope_sources else 0
        )

        completeness_by_scope[scope] = {
            'total_categories': len(scope_sources),
            'categories_with_data': len(scope_sources_with_data),
            'completeness_pct': completeness_pct,
        }

    overall_completeness = (
        len(sources_with_data) / len(all_sources) * 100
        if all_sources else 0
    )

    return {
        'overall_completeness_pct': overall_completeness,
        'by_scope': completeness_by_scope,
        'total_sources': len(all_sources),
        'sources_with_data': len(sources_with_data),
    }


def run_all_checks(session: Session, org_id: int) -> Dict[str, Any]:
    """
    Run all QA/QC checks and compile results.

    Args:
        session: Database session
        org_id: Organization ID

    Returns:
        Comprehensive QA/QC report
    """

    all_issues = []

    # Run each check
    all_issues.extend(check_missing_data(session, org_id))
    all_issues.extend(check_negative_values(session, org_id))
    all_issues.extend(check_outliers(session, org_id))
    all_issues.extend(check_basis_consistency(session, org_id))
    all_issues.extend(check_emission_factor_currency(session, org_id))

    # Get completeness
    completeness = check_completeness(session, org_id)

    # Count by severity
    errors = [i for i in all_issues if i['severity'] == 'error']
    warnings = [i for i in all_issues if i['severity'] == 'warning']
    infos = [i for i in all_issues if i['severity'] == 'info']

    return {
        'summary': {
            'total_issues': len(all_issues),
            'errors': len(errors),
            'warnings': len(warnings),
            'info': len(infos),
        },
        'issues': all_issues,
        'completeness': completeness,
        'passed': len(errors) == 0,
    }
