"""
Electricity and purchased energy calculation methods (Scope 2).
Implements location-based and market-based methods per GHG Protocol Scope 2 Guidance.
"""

from typing import Dict, Any, Optional


def calculate_location_based_electricity(
    electricity_kwh: float,
    grid_ef: float,  # kg CO2/kWh
    gwp_ch4: float = 28,
    gwp_n2o: float = 265,
    ch4_fraction: float = 0.0,  # Fraction of emissions that are CH4
    n2o_fraction: float = 0.0,  # Fraction of emissions that are N2O
) -> Dict[str, Any]:
    """
    Calculate location-based Scope 2 emissions from electricity.

    Formula:
        CO2e = Electricity (kWh) × Grid EF (kg CO2e/kWh)

    Args:
        electricity_kwh: Electricity consumed in kWh
        grid_ef: Grid emission factor in kg CO2/kWh (or kg CO2e/kWh)
        gwp_ch4: GWP for CH4
        gwp_n2o: GWP for N2O
        ch4_fraction: Fraction of grid emissions that are CH4 (typically ~0)
        n2o_fraction: Fraction of grid emissions that are N2O (typically ~0)

    Returns:
        Dictionary with emissions
    """

    # Calculate total emissions
    total_co2e_kg = electricity_kwh * grid_ef

    # Split by gas if fractions provided (typically grid factors are CO2 only)
    co2_kg = total_co2e_kg * (1 - ch4_fraction - n2o_fraction)
    ch4_kg = (total_co2e_kg * ch4_fraction) / gwp_ch4  # Convert CO2e back to CH4 mass
    n2o_kg = (total_co2e_kg * n2o_fraction) / gwp_n2o

    return {
        'emissions': {
            'CO2': {'mass_kg': co2_kg, 'co2e_kg': co2_kg, 'gwp': 1},
            'CH4': {'mass_kg': ch4_kg, 'co2e_kg': ch4_kg * gwp_ch4, 'gwp': gwp_ch4},
            'N2O': {'mass_kg': n2o_kg, 'co2e_kg': n2o_kg * gwp_n2o, 'gwp': gwp_n2o},
        },
        'total_co2e_kg': total_co2e_kg,
        'electricity_kwh': electricity_kwh,
        'grid_ef_kg_per_kwh': grid_ef,
        'method': 'Location-based',
    }


def calculate_market_based_electricity(
    electricity_kwh: float,
    supplier_ef: Optional[float] = None,  # kg CO2/kWh from supplier
    certificates_kwh: float = 0.0,  # RECs/EACs in kWh
    residual_mix_ef: Optional[float] = None,  # Residual mix EF
    grid_ef: Optional[float] = None,  # Fallback to grid average if no supplier EF
) -> Dict[str, Any]:
    """
    Calculate market-based Scope 2 emissions from electricity.

    Market-based method reflects contractual instruments (PPAs, RECs, EACs).

    Args:
        electricity_kwh: Electricity consumed in kWh
        supplier_ef: Supplier-specific emission factor (kg CO2/kWh)
        certificates_kwh: Renewable energy certificates (kWh)
        residual_mix_ef: Residual mix emission factor (after RECs removed)
        grid_ef: Grid average EF (fallback if no supplier-specific data)

    Returns:
        Dictionary with emissions and dual reporting
    """

    # Determine effective EF
    if supplier_ef is not None:
        effective_ef = supplier_ef
    elif residual_mix_ef is not None:
        effective_ef = residual_mix_ef
    elif grid_ef is not None:
        effective_ef = grid_ef
    else:
        raise ValueError("Must provide either supplier_ef, residual_mix_ef, or grid_ef")

    # Apply certificates (zero out covered portion)
    uncovered_kwh = max(0, electricity_kwh - certificates_kwh)
    covered_kwh = min(electricity_kwh, certificates_kwh)

    # Emissions only from uncovered portion
    co2_kg = uncovered_kwh * effective_ef

    return {
        'emissions': {
            'CO2': {'mass_kg': co2_kg, 'co2e_kg': co2_kg, 'gwp': 1},
        },
        'total_co2e_kg': co2_kg,
        'electricity_kwh': electricity_kwh,
        'certificates_kwh': certificates_kwh,
        'uncovered_kwh': uncovered_kwh,
        'covered_kwh': covered_kwh,
        'effective_ef_kg_per_kwh': effective_ef,
        'method': 'Market-based',
    }


def calculate_dual_reporting_electricity(
    electricity_kwh: float,
    grid_ef: float,
    supplier_ef: Optional[float] = None,
    certificates_kwh: float = 0.0,
    residual_mix_ef: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Calculate both location-based and market-based emissions (dual reporting).

    GHG Protocol Scope 2 Guidance requires dual reporting.

    Args:
        electricity_kwh: Electricity consumed
        grid_ef: Grid average emission factor
        supplier_ef: Supplier-specific EF
        certificates_kwh: Renewable certificates
        residual_mix_ef: Residual mix EF

    Returns:
        Dictionary with both methods
    """

    location_based = calculate_location_based_electricity(electricity_kwh, grid_ef)

    market_based = calculate_market_based_electricity(
        electricity_kwh=electricity_kwh,
        supplier_ef=supplier_ef,
        certificates_kwh=certificates_kwh,
        residual_mix_ef=residual_mix_ef,
        grid_ef=grid_ef,
    )

    return {
        'location_based': location_based,
        'market_based': market_based,
        'electricity_kwh': electricity_kwh,
    }


def calculate_purchased_steam_heat(
    energy_quantity: float,
    energy_unit: str,  # e.g., "GJ", "MMBtu", "MWh"
    emission_factor: float,
    ef_unit: str,  # e.g., "kg CO2/GJ"
) -> Dict[str, Any]:
    """
    Calculate emissions from purchased steam, heat, or cooling.

    Args:
        energy_quantity: Amount of energy purchased
        energy_unit: Unit of energy
        emission_factor: Emission factor for the utility
        ef_unit: Unit of emission factor

    Returns:
        Dictionary with emissions
    """
    from ..units import converter

    # Convert to canonical energy unit (GJ)
    energy_gj = converter.convert_energy(energy_quantity, energy_unit, "GJ")

    # Calculate emissions (assume EF is per GJ)
    co2_kg = energy_gj * emission_factor

    return {
        'emissions': {
            'CO2': {'mass_kg': co2_kg, 'co2e_kg': co2_kg, 'gwp': 1},
        },
        'total_co2e_kg': co2_kg,
        'energy_gj': energy_gj,
        'emission_factor': emission_factor,
        'method': 'Purchased energy',
    }
