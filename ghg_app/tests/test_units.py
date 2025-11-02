"""
Unit tests for unit conversion module.
"""

import pytest
from ghgcore.units import converter, ureg


def test_energy_conversion():
    """Test energy unit conversions."""

    # MJ to GJ
    result = converter.convert_energy(1000, "MJ", "GJ")
    assert abs(result - 1.0) < 0.001

    # kWh to GJ
    result = converter.convert_energy(1000, "kWh", "GJ")
    assert abs(result - 3.6) < 0.001


def test_mass_conversion():
    """Test mass unit conversions."""

    # Tonne to kg
    result = converter.convert_mass(1, "tonne", "kg")
    assert abs(result - 1000) < 0.001

    # lb to kg
    result = converter.convert_mass(1, "lb", "kg")
    assert abs(result - 0.453592) < 0.001


def test_volume_conversion():
    """Test volume unit conversions."""

    # Barrel to m3
    result = converter.convert_volume(1, "bbl", "m**3")
    assert abs(result - 0.158987) < 0.001

    # Liter to m3
    result = converter.convert_volume(1000, "L", "m**3")
    assert abs(result - 1.0) < 0.001


def test_volume_to_energy():
    """Test fuel volume to energy conversion."""

    # Diesel: 1000 L should give roughly 38.6 GJ
    result = converter.volume_to_energy(
        volume=1000,
        volume_unit="L",
        fuel_type="diesel",
        output_unit="GJ"
    )

    # Diesel has ~38.6 MJ/L = 38.6 GJ/1000L
    assert 38 < result < 40


def test_hhv_to_lhv():
    """Test HHV to LHV conversion."""

    energy_hhv = 100  # GJ
    fuel_type = "natural_gas"

    energy_lhv = converter.hhv_to_lhv(energy_hhv, fuel_type)

    # Natural gas: LHV ~90% of HHV
    assert 89 < energy_lhv < 91


def test_emission_factor_unit_parsing():
    """Test parsing of emission factor units."""

    # Test simple unit
    num, denom = converter.parse_emission_factor_unit("kg/GJ")
    assert num == "kg"
    assert denom == "GJ"

    # Test compound numerator
    num, denom = converter.parse_emission_factor_unit("kg CO2/kWh")
    assert num == "kg"
    assert denom == "kWh"


def test_petroleum_units_defined():
    """Test that petroleum-specific units are defined."""

    # Test barrel
    barrel = 1 * ureg.bbl
    liters = barrel.to('L')
    assert abs(liters.magnitude - 158.9873) < 0.01

    # Test scf (standard cubic foot)
    scf = 1 * ureg.scf
    m3 = scf.to('m**3')
    assert abs(m3.magnitude - 0.0283168) < 0.001

    # Test toe (tonne of oil equivalent)
    toe = 1 * ureg.toe
    gj = toe.to('GJ')
    assert abs(gj.magnitude - 41.868) < 0.01


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
