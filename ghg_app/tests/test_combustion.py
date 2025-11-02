"""
Unit tests for combustion calculation engine.
"""

import pytest
from ghgcore.engine.combustion import (
    calculate_combustion_emissions,
    calculate_combustion_from_composition,
    calculate_mobile_combustion,
)


def test_stationary_combustion_basic():
    """Test basic stationary combustion calculation."""

    result = calculate_combustion_emissions(
        energy_input=1000,  # GJ
        energy_unit="GJ",
        ef_co2=56.1,  # kg CO2/GJ (natural gas typical)
        ef_co2_unit="kg CO2/GJ",
        oxidation_frac=0.995,
        gwp_ch4=28,
        gwp_n2o=265,
    )

    # Check CO2 emissions
    expected_co2 = 1000 * 56.1 * 0.995
    assert abs(result['emissions']['CO2']['mass_kg'] - expected_co2) < 0.1

    # Check total CO2e (should be close to CO2 since no CH4/N2O in this test)
    assert abs(result['total_co2e_kg'] - expected_co2) < 1.0


def test_combustion_with_ch4_n2o():
    """Test combustion with CH4 and N2O emissions."""

    result = calculate_combustion_emissions(
        energy_input=1000,  # GJ
        energy_unit="GJ",
        ef_co2=56.1,
        ef_co2_unit="kg CO2/GJ",
        ef_ch4=0.001,  # kg CH4/GJ
        ef_ch4_unit="kg CH4/GJ",
        ef_n2o=0.0001,  # kg N2O/GJ
        ef_n2o_unit="kg N2O/GJ",
        oxidation_frac=0.995,
        gwp_ch4=28,
        gwp_n2o=265,
    )

    # CO2
    expected_co2 = 1000 * 56.1 * 0.995
    assert abs(result['emissions']['CO2']['mass_kg'] - expected_co2) < 0.1

    # CH4
    expected_ch4 = 1000 * 0.001
    assert abs(result['emissions']['CH4']['mass_kg'] - expected_ch4) < 0.01

    # N2O
    expected_n2o = 1000 * 0.0001
    assert abs(result['emissions']['N2O']['mass_kg'] - expected_n2o) < 0.001

    # Total CO2e
    expected_total = expected_co2 + (expected_ch4 * 28) + (expected_n2o * 265)
    assert abs(result['total_co2e_kg'] - expected_total) < 1.0


def test_combustion_from_composition():
    """Test Tier 2 combustion from carbon content."""

    result = calculate_combustion_from_composition(
        energy_input=1000,  # GJ
        energy_unit="GJ",
        carbon_content=15.3,  # kg C/GJ (typical for natural gas)
        oxidation_frac=0.995,
        gwp_ch4=28,
    )

    # CO2 = Energy × C_content × (44/12) × oxidation
    expected_co2 = 1000 * 15.3 * (44/12) * 0.995
    assert abs(result['emissions']['CO2']['mass_kg'] - expected_co2) < 1.0

    assert result['method'] == 'Tier 2 - Composition'


def test_mobile_combustion():
    """Test mobile combustion calculation."""

    result = calculate_mobile_combustion(
        fuel_consumed=1000,
        fuel_unit="L",
        fuel_type="diesel",
        ef_co2=74.1,  # kg CO2/GJ
        ef_co2_unit="kg CO2/GJ",
        gwp_ch4=28,
    )

    # Should convert fuel to energy and calculate emissions
    assert result['total_co2e_kg'] > 0
    assert 'CO2' in result['emissions']


def test_energy_unit_conversion_in_combustion():
    """Test that different energy units give same result."""

    # 1000 GJ
    result_gj = calculate_combustion_emissions(
        energy_input=1000,
        energy_unit="GJ",
        ef_co2=56.1,
        ef_co2_unit="kg CO2/GJ",
    )

    # 1,000,000 MJ = 1000 GJ
    result_mj = calculate_combustion_emissions(
        energy_input=1000000,
        energy_unit="MJ",
        ef_co2=56.1,
        ef_co2_unit="kg CO2/GJ",
    )

    # Results should be identical (within rounding)
    assert abs(result_gj['total_co2e_kg'] - result_mj['total_co2e_kg']) < 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
