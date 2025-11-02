"""
Fugitive emissions calculation methods.
Includes equipment leaks, tank losses, loading operations.
"""

from typing import Dict, Any, List, Optional


def calculate_equipment_leaks_component_factor(
    components: List[Dict[str, Any]],
    gwp_ch4: float = 28,
    gwp_n2o: float = 265,
) -> Dict[str, Any]:
    """
    Calculate equipment leak emissions using component-factor approach.

    Each component has: count, gas_type, emission_factor

    Args:
        components: List of component dicts with 'count', 'gas', 'ef_kg_per_component_per_year'
        gwp_ch4: GWP for CH4
        gwp_n2o: GWP for N2O

    Returns:
        Dictionary with emissions
    """

    emissions_by_gas = {
        'CH4': 0.0,
        'VOC': 0.0,
        'CO2': 0.0,
        'N2O': 0.0,
    }

    for component in components:
        count = component.get('count', 0)
        gas = component.get('gas', 'CH4')
        ef = component.get('ef_kg_per_component_per_year', 0.0)
        operating_hours = component.get('operating_hours', 8760)  # Annual default

        # Calculate emissions for this component type
        mass_kg = count * ef * (operating_hours / 8760)

        if gas in emissions_by_gas:
            emissions_by_gas[gas] += mass_kg
        else:
            emissions_by_gas[gas] = mass_kg

    # Convert to CO2e
    co2e_kg = (
        emissions_by_gas.get('CO2', 0) +
        emissions_by_gas.get('CH4', 0) * gwp_ch4 +
        emissions_by_gas.get('N2O', 0) * gwp_n2o
    )

    # Note: VOCs are not GHGs, reported separately
    return {
        'emissions': {
            'CO2': {
                'mass_kg': emissions_by_gas.get('CO2', 0),
                'co2e_kg': emissions_by_gas.get('CO2', 0),
                'gwp': 1
            },
            'CH4': {
                'mass_kg': emissions_by_gas.get('CH4', 0),
                'co2e_kg': emissions_by_gas.get('CH4', 0) * gwp_ch4,
                'gwp': gwp_ch4
            },
            'N2O': {
                'mass_kg': emissions_by_gas.get('N2O', 0),
                'co2e_kg': emissions_by_gas.get('N2O', 0) * gwp_n2o,
                'gwp': gwp_n2o
            },
            'VOC': {
                'mass_kg': emissions_by_gas.get('VOC', 0),
                'co2e_kg': 0,  # VOC not a GHG
                'gwp': 0
            },
        },
        'total_co2e_kg': co2e_kg,
        'component_count': len(components),
        'method': 'Component-factor',
    }


def calculate_tank_flashing_losses(
    throughput: float,
    throughput_unit: str,
    loss_factor: float,  # kg VOC/bbl or kg VOC/m3
    voc_to_ch4_ratio: float = 0.6,  # Fraction of VOC that is CH4
    gwp_ch4: float = 28,
) -> Dict[str, Any]:
    """
    Calculate tank flashing/breathing losses.

    Args:
        throughput: Tank throughput volume
        throughput_unit: Unit of throughput
        loss_factor: Loss factor (mass/volume)
        voc_to_ch4_ratio: Fraction of VOC that is methane
        gwp_ch4: GWP for CH4

    Returns:
        Dictionary with emissions
    """
    from ..units import converter

    # Convert throughput to barrels (common petroleum unit)
    throughput_bbl = converter.convert_volume(throughput, throughput_unit, "m**3") / 0.158987

    # Calculate losses
    voc_kg = throughput_bbl * loss_factor
    ch4_kg = voc_kg * voc_to_ch4_ratio

    co2e_kg = ch4_kg * gwp_ch4

    return {
        'emissions': {
            'CH4': {'mass_kg': ch4_kg, 'co2e_kg': ch4_kg * gwp_ch4, 'gwp': gwp_ch4},
            'VOC': {'mass_kg': voc_kg, 'co2e_kg': 0, 'gwp': 0},
        },
        'total_co2e_kg': co2e_kg,
        'throughput_bbl': throughput_bbl,
        'method': 'Tank losses',
    }


def calculate_pipeline_blowdown(
    pipeline_volume: float,
    pipeline_volume_unit: str,
    gas_pressure: float,  # bar or psi
    gas_pressure_unit: str,
    temperature_c: float,
    ch4_mole_fraction: float = 0.95,
    gwp_ch4: float = 28,
) -> Dict[str, Any]:
    """
    Calculate emissions from pipeline blowdown/depressurization.

    Uses ideal gas law to estimate gas mass.

    Args:
        pipeline_volume: Internal volume of pipeline
        pipeline_volume_unit: Unit of volume
        gas_pressure: Gas pressure
        gas_pressure_unit: Unit of pressure
        temperature_c: Gas temperature in Celsius
        ch4_mole_fraction: Mole fraction of CH4 in gas
        gwp_ch4: GWP for CH4

    Returns:
        Dictionary with emissions
    """
    from ..units import converter

    # Convert to standard units
    volume_m3 = converter.convert_volume(pipeline_volume, pipeline_volume_unit, "m**3")

    # Convert pressure to bar
    if gas_pressure_unit.lower() == 'psi':
        pressure_bar = gas_pressure * 0.0689476
    else:
        pressure_bar = gas_pressure

    # Ideal gas law: n = PV/RT
    # where R = 0.08314 bar·m³/(mol·K)
    temperature_k = temperature_c + 273.15
    R = 0.08314  # bar·m³/(mol·K)

    moles_total = (pressure_bar * volume_m3) / (R * temperature_k)

    # CH4 mass (molecular weight = 16 g/mol)
    ch4_moles = moles_total * ch4_mole_fraction
    ch4_kg = (ch4_moles * 16) / 1000  # Convert g to kg

    co2e_kg = ch4_kg * gwp_ch4

    return {
        'emissions': {
            'CH4': {'mass_kg': ch4_kg, 'co2e_kg': ch4_kg * gwp_ch4, 'gwp': gwp_ch4},
        },
        'total_co2e_kg': co2e_kg,
        'pipeline_volume_m3': volume_m3,
        'pressure_bar': pressure_bar,
        'method': 'Pipeline blowdown',
    }


def calculate_loading_operations(
    product_loaded: float,
    product_unit: str,
    loss_factor: float,  # kg VOC per unit loaded
    vapor_recovery_efficiency: float = 0.0,  # 0-1
    voc_to_ch4_ratio: float = 0.3,
    gwp_ch4: float = 28,
) -> Dict[str, Any]:
    """
    Calculate emissions from product loading (truck, rail, ship).

    Args:
        product_loaded: Amount of product loaded
        product_unit: Unit of product
        loss_factor: Emission factor
        vapor_recovery_efficiency: Vapor recovery system efficiency (0-1)
        voc_to_ch4_ratio: Fraction of VOC that is CH4
        gwp_ch4: GWP for CH4

    Returns:
        Dictionary with emissions
    """
    from ..units import converter

    # Convert to standard volume
    volume_m3 = converter.convert_volume(product_loaded, product_unit, "m**3")

    # Calculate gross emissions
    voc_gross_kg = volume_m3 * loss_factor

    # Apply vapor recovery
    voc_net_kg = voc_gross_kg * (1 - vapor_recovery_efficiency)
    ch4_kg = voc_net_kg * voc_to_ch4_ratio

    co2e_kg = ch4_kg * gwp_ch4

    return {
        'emissions': {
            'CH4': {'mass_kg': ch4_kg, 'co2e_kg': ch4_kg * gwp_ch4, 'gwp': gwp_ch4},
            'VOC': {'mass_kg': voc_net_kg, 'co2e_kg': 0, 'gwp': 0},
        },
        'total_co2e_kg': co2e_kg,
        'product_loaded_m3': volume_m3,
        'vapor_recovery_efficiency': vapor_recovery_efficiency,
        'method': 'Loading operations',
    }
