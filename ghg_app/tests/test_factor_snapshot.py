"""
Unit tests for emission factor snapshot immutability.
Critical for audit trail and reproducibility.
"""

import pytest
from sqlmodel import Session
from ghgcore.db import engine, create_db_and_tables
from ghgcore.models import Organization, Facility, Source, Activity, EmissionFactor, Calculation
from datetime import date


@pytest.fixture(scope="function")
def test_session():
    """Create a fresh test database for each test."""
    create_db_and_tables()
    with Session(engine) as session:
        yield session


def test_factor_snapshot_immutability(test_session):
    """
    Test that calculation snapshots don't change when emission factors are updated.
    This is critical for audit trails.
    """

    # Create test organization
    org = Organization(
        name="Test Org",
        country="Test",
        sector="Test",
        base_year=2024,
        period_start=date(2024, 1, 1),
        period_end=date(2024, 12, 31),
        gwp_set="AR5",
    )
    test_session.add(org)
    test_session.commit()

    # Create facility
    facility = Facility(
        org_id=org.id,
        name="Test Facility",
    )
    test_session.add(facility)
    test_session.commit()

    # Create source
    source = Source(
        scope=1,
        subcategory="stationary_combustion",
    )
    test_session.add(source)
    test_session.commit()

    # Create emission factor
    ef = EmissionFactor(
        scope=1,
        subcategory="stationary_combustion",
        activity_code="TEST_FUEL",
        activity_name="Test Fuel",
        gas="CO2",
        factor_value=50.0,  # Original value
        factor_unit="kg CO2/GJ",
        basis="HHV",
        source_authority="TEST",
        source_doc="Test Doc",
        source_year=2024,
        valid_from=date(2024, 1, 1),
    )
    test_session.add(ef)
    test_session.commit()

    original_ef_id = ef.id

    # Create activity
    activity = Activity(
        facility_id=facility.id,
        source_id=source.id,
        activity_type="test_combustion",
        activity_date=date(2024, 6, 1),
        method_key="TEST",
        units_json={"quantity": 1000, "unit": "GJ"},
    )
    test_session.add(activity)
    test_session.commit()

    # Create calculation with factor snapshot
    factor_snapshot = {
        'id': ef.id,
        'activity_code': ef.activity_code,
        'factor_value': ef.factor_value,
        'factor_unit': ef.factor_unit,
        'source_authority': ef.source_authority,
        'source_year': ef.source_year,
    }

    calc = Calculation(
        activity_id=activity.id,
        method_key="TEST",
        input_snapshot_json={'energy': 1000, 'unit': 'GJ'},
        factor_snapshot_json=factor_snapshot,
        results_json={
            'emissions': {
                'CO2': {'mass_kg': 50000, 'co2e_kg': 50000}
            },
            'total_co2e_kg': 50000
        },
        calc_version="1.0",
    )
    test_session.add(calc)
    test_session.commit()

    original_calc_id = calc.id
    original_snapshot = calc.factor_snapshot_json.copy()

    # Now UPDATE the emission factor (simulating a library update)
    ef.factor_value = 60.0  # Changed from 50 to 60
    test_session.add(ef)
    test_session.commit()

    # Retrieve the original calculation
    calc_retrieved = test_session.get(Calculation, original_calc_id)

    # CRITICAL TEST: The snapshot should still have the original value (50.0)
    assert calc_retrieved.factor_snapshot_json['factor_value'] == 50.0
    assert calc_retrieved.factor_snapshot_json == original_snapshot

    # But the live emission factor should have the new value
    ef_retrieved = test_session.get(EmissionFactor, original_ef_id)
    assert ef_retrieved.factor_value == 60.0

    print("✓ Snapshot immutability test PASSED: Historical calculations unchanged")


def test_calculation_reproducibility(test_session):
    """
    Test that calculations can be reproduced from snapshots.
    """

    # Create minimal setup
    org = Organization(
        name="Test Org 2",
        country="Test",
        sector="Test",
        base_year=2024,
        period_start=date(2024, 1, 1),
        period_end=date(2024, 12, 31),
    )
    test_session.add(org)
    test_session.commit()

    facility = Facility(org_id=org.id, name="Facility")
    test_session.add(facility)
    test_session.commit()

    source = Source(scope=1, subcategory="test")
    test_session.add(source)
    test_session.commit()

    activity = Activity(
        facility_id=facility.id,
        source_id=source.id,
        activity_type="test",
        activity_date=date(2024, 1, 1),
        method_key="TEST",
        units_json={"quantity": 100, "unit": "GJ"},
    )
    test_session.add(activity)
    test_session.commit()

    # Create calculation with complete snapshots
    input_snapshot = {
        'energy_gj': 100,
        'fuel_type': 'natural_gas',
    }

    factor_snapshot = {
        'activity_code': 'NG',
        'factor_value': 56.1,
        'factor_unit': 'kg CO2/GJ',
        'oxidation_frac': 0.995,
    }

    expected_co2 = 100 * 56.1 * 0.995  # = 5581.95 kg

    results = {
        'emissions': {
            'CO2': {'mass_kg': expected_co2, 'co2e_kg': expected_co2}
        },
        'total_co2e_kg': expected_co2,
    }

    calc = Calculation(
        activity_id=activity.id,
        method_key="TEST",
        input_snapshot_json=input_snapshot,
        factor_snapshot_json=factor_snapshot,
        results_json=results,
    )
    test_session.add(calc)
    test_session.commit()

    # Retrieve and verify reproducibility
    calc_retrieved = test_session.get(Calculation, calc.id)

    # All snapshot data should be present
    assert calc_retrieved.input_snapshot_json == input_snapshot
    assert calc_retrieved.factor_snapshot_json == factor_snapshot

    # Results should match
    assert abs(calc_retrieved.results_json['total_co2e_kg'] - expected_co2) < 0.01

    # Re-calculate from snapshot to verify
    recalc_co2 = (
        calc_retrieved.input_snapshot_json['energy_gj'] *
        calc_retrieved.factor_snapshot_json['factor_value'] *
        calc_retrieved.factor_snapshot_json['oxidation_frac']
    )

    assert abs(recalc_co2 - expected_co2) < 0.01

    print("✓ Calculation reproducibility test PASSED")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
