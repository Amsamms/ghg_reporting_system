"""
Unit handling with pint for unit-safe calculations.
Supports petroleum industry units and conversions.
"""

import pint
from pint import UnitRegistry
from typing import Union, Tuple


# Initialize pint unit registry
ureg = UnitRegistry()

# Define petroleum-specific units
ureg.define('bbl = 158.9873 * liter = barrel')  # Standard barrel
ureg.define('scf = 0.0283168 * meter**3 = standard_cubic_foot')  # Standard cubic foot
ureg.define('Nm3 = meter**3 = normal_cubic_meter')  # Normal cubic meter (0°C, 1 atm)
ureg.define('toe = 41.868 * GJ = tonne_of_oil_equivalent')  # Tonne of oil equivalent
ureg.define('tCO2e = 1000 * kg = tonne_CO2_equivalent')  # Tonne CO2 equivalent

# Common aliases
ureg.define('@alias bbl = barrel')
ureg.define('@alias scf = standard_cubic_foot')
ureg.define('@alias toe = tonne_oil_equivalent')

# Energy content defaults (for reference)
ENERGY_CONTENT_DEFAULTS = {
    'natural_gas': 38.3 * ureg.MJ / ureg.Nm3,  # HHV
    'crude_oil': 6.119 * ureg.GJ / ureg.bbl,  # HHV
    'diesel': 38.6 * ureg.MJ / ureg.liter,  # HHV
    'gasoline': 34.2 * ureg.MJ / ureg.liter,  # HHV
    'fuel_oil': 40.4 * ureg.MJ / ureg.kg,  # HHV
    'lpg': 46.1 * ureg.MJ / ureg.kg,  # HHV
    'coal': 25.8 * ureg.MJ / ureg.kg,  # Bituminous HHV
}

# HHV to LHV conversion factors (typical)
HHV_TO_LHV = {
    'natural_gas': 0.90,  # 10% reduction
    'diesel': 0.95,
    'gasoline': 0.93,
    'fuel_oil': 0.95,
    'lpg': 0.92,
    'coal': 0.98,
}


class UnitConverter:
    """Helper class for unit conversions in GHG calculations."""

    def __init__(self):
        self.ureg = ureg

    def convert_to_canonical(self, value: float, from_unit: str, target_dimension: str) -> float:
        """
        Convert value to canonical unit for storage.

        Args:
            value: Numeric value
            from_unit: Source unit string (e.g., "MJ", "bbl", "kWh")
            target_dimension: Target dimension ("energy", "mass", "volume", "energy_specific")

        Returns:
            Value in canonical unit (GJ for energy, kg for mass, m3 for volume)
        """
        quantity = value * self.ureg(from_unit)

        if target_dimension == "energy":
            # Canonical: GJ
            return quantity.to('GJ').magnitude

        elif target_dimension == "mass":
            # Canonical: kg
            return quantity.to('kg').magnitude

        elif target_dimension == "volume":
            # Canonical: m3
            return quantity.to('m**3').magnitude

        elif target_dimension == "energy_specific":
            # For emission factors like kg/GJ
            return quantity.magnitude  # Keep as is

        else:
            raise ValueError(f"Unknown target dimension: {target_dimension}")

    def convert_energy(self, value: float, from_unit: str, to_unit: str = "GJ") -> float:
        """
        Convert energy values.

        Args:
            value: Energy value
            from_unit: Source unit (e.g., "MJ", "kWh", "MMBtu")
            to_unit: Target unit (default: "GJ")

        Returns:
            Converted value
        """
        quantity = value * self.ureg(from_unit)
        return quantity.to(to_unit).magnitude

    def convert_mass(self, value: float, from_unit: str, to_unit: str = "kg") -> float:
        """
        Convert mass values.

        Args:
            value: Mass value
            from_unit: Source unit (e.g., "tonne", "lb", "g")
            to_unit: Target unit (default: "kg")

        Returns:
            Converted value
        """
        quantity = value * self.ureg(from_unit)
        return quantity.to(to_unit).magnitude

    def convert_volume(self, value: float, from_unit: str, to_unit: str = "m**3") -> float:
        """
        Convert volume values.

        Args:
            value: Volume value
            from_unit: Source unit (e.g., "bbl", "gal", "L")
            to_unit: Target unit (default: "m3")

        Returns:
            Converted value
        """
        quantity = value * self.ureg(from_unit)
        return quantity.to(to_unit).magnitude

    def volume_to_energy(self, volume: float, volume_unit: str, fuel_type: str,
                         energy_content_per_unit: float = None,
                         energy_content_unit: str = None,
                         output_unit: str = "GJ") -> float:
        """
        Convert fuel volume to energy content.

        Args:
            volume: Fuel volume
            volume_unit: Volume unit (e.g., "bbl", "L", "m3")
            fuel_type: Fuel type (e.g., "diesel", "gasoline")
            energy_content_per_unit: Optional custom energy content
            energy_content_unit: Unit of energy content (e.g., "MJ/L")
            output_unit: Desired energy unit (default: "GJ")

        Returns:
            Energy content in output_unit
        """
        vol_quantity = volume * self.ureg(volume_unit)

        # Use custom energy content if provided, otherwise use defaults
        if energy_content_per_unit and energy_content_unit:
            ec_quantity = energy_content_per_unit * self.ureg(energy_content_unit)
        else:
            ec_quantity = ENERGY_CONTENT_DEFAULTS.get(fuel_type)
            if ec_quantity is None:
                raise ValueError(f"No default energy content for fuel_type: {fuel_type}")

        energy = vol_quantity * ec_quantity
        return energy.to(output_unit).magnitude

    def mass_to_energy(self, mass: float, mass_unit: str, fuel_type: str,
                       energy_content_per_unit: float = None,
                       energy_content_unit: str = None,
                       output_unit: str = "GJ") -> float:
        """
        Convert fuel mass to energy content.

        Args:
            mass: Fuel mass
            mass_unit: Mass unit (e.g., "kg", "tonne", "lb")
            fuel_type: Fuel type (e.g., "coal", "fuel_oil")
            energy_content_per_unit: Optional custom energy content
            energy_content_unit: Unit of energy content (e.g., "MJ/kg")
            output_unit: Desired energy unit (default: "GJ")

        Returns:
            Energy content in output_unit
        """
        mass_quantity = mass * self.ureg(mass_unit)

        if energy_content_per_unit and energy_content_unit:
            ec_quantity = energy_content_per_unit * self.ureg(energy_content_unit)
        else:
            ec_quantity = ENERGY_CONTENT_DEFAULTS.get(fuel_type)
            if ec_quantity is None:
                raise ValueError(f"No default energy content for fuel_type: {fuel_type}")

        energy = mass_quantity * ec_quantity
        return energy.to(output_unit).magnitude

    def hhv_to_lhv(self, energy_hhv: float, fuel_type: str) -> float:
        """
        Convert HHV (higher heating value) to LHV (lower heating value).

        Args:
            energy_hhv: Energy in HHV basis
            fuel_type: Fuel type

        Returns:
            Energy in LHV basis
        """
        factor = HHV_TO_LHV.get(fuel_type, 0.95)  # Default 5% reduction
        return energy_hhv * factor

    def lhv_to_hhv(self, energy_lhv: float, fuel_type: str) -> float:
        """
        Convert LHV to HHV.

        Args:
            energy_lhv: Energy in LHV basis
            fuel_type: Fuel type

        Returns:
            Energy in HHV basis
        """
        factor = HHV_TO_LHV.get(fuel_type, 0.95)
        return energy_lhv / factor

    def parse_emission_factor_unit(self, factor_unit: str) -> Tuple[str, str]:
        """
        Parse emission factor unit into numerator and denominator.

        Args:
            factor_unit: e.g., "kg CO2/GJ", "kg CH4/kWh", "g/km"

        Returns:
            Tuple of (numerator_unit, denominator_unit)
        """
        if '/' not in factor_unit:
            raise ValueError(f"Invalid emission factor unit format: {factor_unit}")

        # Split by '/'
        parts = factor_unit.split('/')

        # Handle compound numerators like "kg CO2"
        numerator = parts[0].strip()
        denominator = parts[1].strip()

        # Extract just the unit (remove gas names)
        # e.g., "kg CO2" -> "kg", "g N2O" -> "g"
        numerator_parts = numerator.split()
        if len(numerator_parts) > 1:
            numerator_unit = numerator_parts[0]
        else:
            numerator_unit = numerator

        return (numerator_unit, denominator)


# Global instance
converter = UnitConverter()


def get_converter() -> UnitConverter:
    """Get the global unit converter instance."""
    return converter
