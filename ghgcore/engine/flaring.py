"""
Flaring and thermal oxidizer calculation methods.
Implements API Compendium methodologies for petroleum industry.
"""

from typing import Dict, Any, Optional


def calculate_flare_emissions(
    gas_volume: float,
    gas_volume_unit: str,  # e.g., "Nm3", "scf"
    ef_co2: float,  # kg CO2/volume
    ef_co2_unit: str,
    destruction_efficiency: float = 0.98,  # Typical for smokeless flare
    assist_gas_volume: float = 0.0,
    assist_gas_unit: str = "Nm3",
    assist_ef_co2: float = 0.0,
    gwp_ch4: float = 28,
    unburned_ch4_factor: Optional[float] = None,  # kg CH4 per volume of uncombusted gas
) -> Dict[str, Any]:
    """
    Calculate flare emissions using API Compendium method.

    Formula:
        Combusted CO2 = Volume × EF_CO2 × destruction_efficiency
        Uncombusted CH4 = Volume × (1 - destruction_efficiency) × CH4_content
        Assist gas CO2 = Assist_volume × Assist_EF

    Args:
        gas_volume: Volume of gas flared
        gas_volume_unit: Unit of gas volume
        ef_co2: CO2 emission factor
        ef_co2_unit: Unit of emission factor
        destruction_efficiency: Fraction of gas destroyed (0-1), default 0.98 for smokeless
        assist_gas_volume: Volume of assist gas (natural gas, air)
        assist_gas_unit: Unit of assist gas
        assist_ef_co2: Emission factor for assist gas
        gwp_ch4: GWP for CH4
        unburned_ch4_factor: CH4 content factor for uncombusted portion

    Returns:
        Dictionary with emissions
    """
    from ..units import converter

    # Convert volumes to canonical unit
    gas_nm3 = converter.convert_volume(gas_volume, gas_volume_unit, "m**3")

    # CO2 from combustion
    co2_combustion_kg = gas_nm3 * ef_co2 * destruction_efficiency

    # Assist gas CO2 (if used)
    co2_assist_kg = 0.0
    if assist_gas_volume > 0 and assist_ef_co2 > 0:
        assist_nm3 = converter.convert_volume(assist_gas_volume, assist_gas_unit, "m**3")
        co2_assist_kg = assist_nm3 * assist_ef_co2

    total_co2_kg = co2_combustion_kg + co2_assist_kg

    # Uncombusted CH4
    ch4_kg = 0.0
    if unburned_ch4_factor:
        uncombusted_fraction = 1 - destruction_efficiency
        ch4_kg = gas_nm3 * uncombusted_fraction * unburned_ch4_factor

    # Total CO2e
    co2e_kg = total_co2_kg + (ch4_kg * gwp_ch4)

    return {
        'emissions': {
            'CO2': {'mass_kg': total_co2_kg, 'co2e_kg': total_co2_kg, 'gwp': 1},
            'CH4': {'mass_kg': ch4_kg, 'co2e_kg': ch4_kg * gwp_ch4, 'gwp': gwp_ch4},
        },
        'total_co2e_kg': co2e_kg,
        'gas_volume_nm3': gas_nm3,
        'destruction_efficiency': destruction_efficiency,
        'assist_gas_nm3': assist_nm3 if assist_gas_volume > 0 else 0,
        'method': 'API Flaring',
    }


def calculate_flare_from_energy(
    energy_content: float,
    energy_unit: str,
    carbon_content_factor: float = 15.3,  # kg C/GJ (typical for natural gas)
    destruction_efficiency: float = 0.98,
    gwp_ch4: float = 28,
) -> Dict[str, Any]:
    """
    Calculate flare emissions from energy content (alternative method).

    Args:
        energy_content: Total energy flared
        energy_unit: Unit of energy
        carbon_content_factor: Carbon content (kg C/GJ)
        destruction_efficiency: Destruction efficiency
        gwp_ch4: GWP for CH4

    Returns:
        Dictionary with emissions
    """
    from ..units import converter

    # Convert to GJ
    energy_gj = converter.convert_energy(energy_content, energy_unit, "GJ")

    # CO2 from carbon combustion
    # CO2 = C × (44/12)
    co2_kg = energy_gj * carbon_content_factor * (44 / 12) * destruction_efficiency

    # Uncombusted CH4 (assume CH4 content ~95% of carbon for natural gas)
    # This is a simplified approach
    uncombusted_c_kg = energy_gj * carbon_content_factor * (1 - destruction_efficiency)
    ch4_kg = uncombusted_c_kg * (16 / 12)  # Convert C to CH4 mass

    co2e_kg = co2_kg + (ch4_kg * gwp_ch4)

    return {
        'emissions': {
            'CO2': {'mass_kg': co2_kg, 'co2e_kg': co2_kg, 'gwp': 1},
            'CH4': {'mass_kg': ch4_kg, 'co2e_kg': ch4_kg * gwp_ch4, 'gwp': gwp_ch4},
        },
        'total_co2e_kg': co2e_kg,
        'energy_gj': energy_gj,
        'destruction_efficiency': destruction_efficiency,
        'method': 'Flaring from energy',
    }


def calculate_thermal_oxidizer(
    voc_mass: float,
    voc_unit: str,
    destruction_efficiency: float = 0.98,
    voc_to_co2_ratio: float = 3.0,  # Typical molecular weight ratio
) -> Dict[str, Any]:
    """
    Calculate emissions from thermal oxidizers treating VOCs.

    Args:
        voc_mass: Mass of VOC destroyed
        voc_unit: Unit of VOC mass
        destruction_efficiency: Destruction efficiency
        voc_to_co2_ratio: Mass ratio of CO2 produced per unit VOC

    Returns:
        Dictionary with emissions
    """
    from ..units import converter

    # Convert to kg
    voc_kg = converter.convert_mass(voc_mass, voc_unit, "kg")

    # CO2 produced from VOC oxidation
    co2_kg = voc_kg * destruction_efficiency * voc_to_co2_ratio

    return {
        'emissions': {
            'CO2': {'mass_kg': co2_kg, 'co2e_kg': co2_kg, 'gwp': 1},
        },
        'total_co2e_kg': co2_kg,
        'voc_destroyed_kg': voc_kg * destruction_efficiency,
        'method': 'Thermal oxidizer',
    }
