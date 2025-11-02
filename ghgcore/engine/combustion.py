"""
Stationary and mobile combustion calculation methods.
Implements Tier 1, 2, and 3 approaches per IPCC/GHG Protocol.
"""

from typing import Dict, Any, Tuple, Optional
from ..units import converter


def calculate_combustion_emissions(
    energy_input: float,
    energy_unit: str,
    ef_co2: float,
    ef_co2_unit: str,
    ef_ch4: Optional[float] = None,
    ef_ch4_unit: Optional[str] = None,
    ef_n2o: Optional[float] = None,
    ef_n2o_unit: Optional[str] = None,
    oxidation_frac: float = 1.0,
    basis: str = "HHV",
    gwp_ch4: float = 28,
    gwp_n2o: float = 265,
) -> Dict[str, Any]:
    """
    Calculate combustion emissions (Tier 1 method).

    Formula:
        CO2 = Energy_input (GJ) × EF_CO2 (kg/GJ) × oxidation_frac
        CH4 = Energy_input (GJ) × EF_CH4 (kg/GJ)
        N2O = Energy_input (GJ) × EF_N2O (kg/GJ)
        CO2e = CO2 + (CH4 × GWP_CH4) + (N2O × GWP_N2O)

    Args:
        energy_input: Fuel energy input
        energy_unit: Unit of energy input (e.g., "GJ", "MJ", "kWh")
        ef_co2: CO2 emission factor
        ef_co2_unit: Unit of CO2 EF (e.g., "kg CO2/GJ")
        ef_ch4: CH4 emission factor (optional)
        ef_ch4_unit: Unit of CH4 EF
        ef_n2o: N2O emission factor (optional)
        ef_n2o_unit: Unit of N2O EF
        oxidation_frac: Oxidation/combustion fraction (0-1)
        basis: Energy basis (HHV or LHV)
        gwp_ch4: GWP for CH4
        gwp_n2o: GWP for N2O

    Returns:
        Dictionary with emissions by gas and total CO2e
    """

    # Convert energy to canonical unit (GJ)
    energy_gj = converter.convert_energy(energy_input, energy_unit, "GJ")

    # Parse emission factor units and calculate
    # CO2
    ef_co2_num, ef_co2_denom = converter.parse_emission_factor_unit(ef_co2_unit)
    # Ensure denominator is in GJ
    ef_co2_per_gj = ef_co2  # Assume already in per GJ, add conversion if needed

    co2_kg = energy_gj * ef_co2_per_gj * oxidation_frac

    # CH4
    ch4_kg = 0.0
    if ef_ch4 is not None and ef_ch4_unit:
        ef_ch4_per_gj = ef_ch4  # Assume per GJ
        ch4_kg = energy_gj * ef_ch4_per_gj

    # N2O
    n2o_kg = 0.0
    if ef_n2o is not None and ef_n2o_unit:
        ef_n2o_per_gj = ef_n2o
        n2o_kg = energy_gj * ef_n2o_per_gj

    # Calculate CO2e
    co2e_kg = co2_kg + (ch4_kg * gwp_ch4) + (n2o_kg * gwp_n2o)

    return {
        'emissions': {
            'CO2': {'mass_kg': co2_kg, 'co2e_kg': co2_kg, 'gwp': 1},
            'CH4': {'mass_kg': ch4_kg, 'co2e_kg': ch4_kg * gwp_ch4, 'gwp': gwp_ch4},
            'N2O': {'mass_kg': n2o_kg, 'co2e_kg': n2o_kg * gwp_n2o, 'gwp': gwp_n2o},
        },
        'total_co2e_kg': co2e_kg,
        'energy_input_gj': energy_gj,
        'basis': basis,
        'oxidation_frac': oxidation_frac,
    }


def calculate_combustion_from_composition(
    energy_input: float,
    energy_unit: str,
    carbon_content: float,  # kg C / GJ
    oxidation_frac: float = 0.995,
    gwp_ch4: float = 28,
    gwp_n2o: float = 265,
    ef_ch4: float = 0.001,  # Default CH4 EF
    ef_n2o: float = 0.0001,  # Default N2O EF
) -> Dict[str, Any]:
    """
    Calculate combustion emissions from fuel composition (Tier 2 method).

    Formula:
        CO2 = Energy_input × Carbon_content × (44/12) × oxidation_frac
        where 44/12 is the molecular weight ratio CO2/C

    Args:
        energy_input: Fuel energy input
        energy_unit: Unit of energy
        carbon_content: Carbon content in kg C per GJ
        oxidation_frac: Oxidation fraction
        gwp_ch4: GWP for CH4
        gwp_n2o: GWP for N2O
        ef_ch4: CH4 emission factor (kg/GJ)
        ef_n2o: N2O emission factor (kg/GJ)

    Returns:
        Dictionary with emissions
    """

    # Convert energy
    energy_gj = converter.convert_energy(energy_input, energy_unit, "GJ")

    # Calculate CO2 from carbon content
    # Molecular weight ratio: CO2 (44) / C (12) = 3.667
    co2_kg = energy_gj * carbon_content * (44 / 12) * oxidation_frac

    # CH4 and N2O
    ch4_kg = energy_gj * ef_ch4
    n2o_kg = energy_gj * ef_n2o

    # Total CO2e
    co2e_kg = co2_kg + (ch4_kg * gwp_ch4) + (n2o_kg * gwp_n2o)

    return {
        'emissions': {
            'CO2': {'mass_kg': co2_kg, 'co2e_kg': co2_kg, 'gwp': 1},
            'CH4': {'mass_kg': ch4_kg, 'co2e_kg': ch4_kg * gwp_ch4, 'gwp': gwp_ch4},
            'N2O': {'mass_kg': n2o_kg, 'co2e_kg': n2o_kg * gwp_n2o, 'gwp': gwp_n2o},
        },
        'total_co2e_kg': co2e_kg,
        'energy_input_gj': energy_gj,
        'carbon_content_kg_per_gj': carbon_content,
        'oxidation_frac': oxidation_frac,
        'method': 'Tier 2 - Composition',
    }


def calculate_mobile_combustion(
    fuel_consumed: float,
    fuel_unit: str,
    fuel_type: str,
    ef_co2: float,
    ef_co2_unit: str,
    ef_ch4: Optional[float] = None,
    ef_ch4_unit: Optional[str] = None,
    ef_n2o: Optional[float] = None,
    ef_n2o_unit: Optional[str] = None,
    gwp_ch4: float = 28,
    gwp_n2o: float = 265,
) -> Dict[str, Any]:
    """
    Calculate mobile combustion emissions (vehicles, vessels, aircraft).

    Args:
        fuel_consumed: Amount of fuel consumed
        fuel_unit: Unit of fuel (e.g., "L", "gal", "kg")
        fuel_type: Fuel type (e.g., "diesel", "gasoline", "jet_fuel")
        ef_co2: CO2 emission factor
        ef_co2_unit: Unit of CO2 EF
        ef_ch4: CH4 emission factor
        ef_ch4_unit: Unit of CH4 EF
        ef_n2o: N2O emission factor
        ef_n2o_unit: Unit of N2O EF
        gwp_ch4: GWP for CH4
        gwp_n2o: GWP for N2O

    Returns:
        Dictionary with emissions
    """

    # Convert fuel to energy
    # First check if fuel is already in energy units
    if fuel_unit.upper() in ['GJ', 'MJ', 'KWH', 'MMBTU']:
        energy_gj = converter.convert_energy(fuel_consumed, fuel_unit, "GJ")
    else:
        # Convert volume/mass to energy
        if fuel_unit.lower() in ['l', 'liter', 'litre', 'gal', 'gallon', 'bbl', 'barrel']:
            energy_gj = converter.volume_to_energy(
                fuel_consumed, fuel_unit, fuel_type, output_unit="GJ"
            )
        else:
            # Assume mass unit
            energy_gj = converter.mass_to_energy(
                fuel_consumed, fuel_unit, fuel_type, output_unit="GJ"
            )

    # Use standard combustion calculation
    return calculate_combustion_emissions(
        energy_input=energy_gj,
        energy_unit="GJ",
        ef_co2=ef_co2,
        ef_co2_unit=ef_co2_unit,
        ef_ch4=ef_ch4,
        ef_ch4_unit=ef_ch4_unit,
        ef_n2o=ef_n2o,
        ef_n2o_unit=ef_n2o_unit,
        oxidation_frac=0.99,  # Typical for mobile combustion
        gwp_ch4=gwp_ch4,
        gwp_n2o=gwp_n2o,
    )
