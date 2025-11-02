"""
Transportation emissions calculation methods (Scope 3).
Includes freight, business travel, employee commuting.
"""

from typing import Dict, Any, Optional


def calculate_freight_emissions(
    mass: float,
    mass_unit: str,
    distance: float,
    distance_unit: str,
    ef_per_tonne_km: float,  # kg CO2e per tonne-km
    load_factor: float = 1.0,  # Adjustment for load utilization
) -> Dict[str, Any]:
    """
    Calculate freight transportation emissions.

    Formula:
        Emissions = Mass × Distance × EF × Load_factor

    Args:
        mass: Cargo mass
        mass_unit: Unit of mass
        distance: Distance traveled
        distance_unit: Unit of distance
        ef_per_tonne_km: Emission factor (kg CO2e/tonne-km)
        load_factor: Load factor adjustment (default 1.0)

    Returns:
        Dictionary with emissions
    """
    from ..units import converter

    # Convert to standard units
    mass_tonne = converter.convert_mass(mass, mass_unit, "kg") / 1000
    distance_km = converter.convert_to_canonical(distance, distance_unit, "volume")  # Using for length

    # Simple conversion for common distance units
    if distance_unit.lower() in ['mi', 'mile', 'miles']:
        distance_km = distance * 1.60934
    elif distance_unit.lower() in ['km', 'kilometer', 'kilometers']:
        distance_km = distance
    elif distance_unit.lower() in ['m', 'meter', 'meters']:
        distance_km = distance / 1000
    else:
        distance_km = distance  # Assume km

    # Calculate tonne-km
    tonne_km = mass_tonne * distance_km * load_factor

    # Calculate emissions
    co2e_kg = tonne_km * ef_per_tonne_km

    return {
        'emissions': {
            'CO2e': {'mass_kg': co2e_kg, 'co2e_kg': co2e_kg, 'gwp': 1},
        },
        'total_co2e_kg': co2e_kg,
        'tonne_km': tonne_km,
        'mass_tonne': mass_tonne,
        'distance_km': distance_km,
        'method': 'Freight transport',
    }


def calculate_business_travel_distance(
    distance: float,
    distance_unit: str,
    ef_per_km: float,  # kg CO2e/km (mode-specific)
    passengers: int = 1,
) -> Dict[str, Any]:
    """
    Calculate business travel emissions from distance.

    Args:
        distance: Distance traveled
        distance_unit: Unit of distance
        ef_per_km: Emission factor per km
        passengers: Number of passengers (for allocation)

    Returns:
        Dictionary with emissions
    """

    # Convert distance to km
    if distance_unit.lower() in ['mi', 'mile', 'miles']:
        distance_km = distance * 1.60934
    elif distance_unit.lower() in ['km', 'kilometer', 'kilometers']:
        distance_km = distance
    else:
        distance_km = distance

    # Calculate emissions per passenger
    co2e_kg = (distance_km * ef_per_km) / passengers

    return {
        'emissions': {
            'CO2e': {'mass_kg': co2e_kg, 'co2e_kg': co2e_kg, 'gwp': 1},
        },
        'total_co2e_kg': co2e_kg,
        'distance_km': distance_km,
        'passengers': passengers,
        'method': 'Business travel - distance',
    }


def calculate_business_travel_fuel(
    fuel_consumed: float,
    fuel_unit: str,
    fuel_type: str,
    ef_co2: float,
    ef_co2_unit: str,
    gwp_ch4: float = 28,
    gwp_n2o: float = 265,
) -> Dict[str, Any]:
    """
    Calculate business travel emissions from fuel consumption.

    Args:
        fuel_consumed: Fuel consumed
        fuel_unit: Unit of fuel
        fuel_type: Type of fuel
        ef_co2: CO2 emission factor
        ef_co2_unit: Unit of emission factor
        gwp_ch4: GWP for CH4
        gwp_n2o: GWP for N2O

    Returns:
        Dictionary with emissions
    """
    from .combustion import calculate_mobile_combustion

    return calculate_mobile_combustion(
        fuel_consumed=fuel_consumed,
        fuel_unit=fuel_unit,
        fuel_type=fuel_type,
        ef_co2=ef_co2,
        ef_co2_unit=ef_co2_unit,
        gwp_ch4=gwp_ch4,
        gwp_n2o=gwp_n2o,
    )


def calculate_employee_commuting(
    employees: int,
    avg_commute_distance_km: float,
    working_days: int,
    mode_split: Dict[str, float],  # {'car': 0.7, 'bus': 0.2, 'rail': 0.1}
    mode_ef: Dict[str, float],  # {'car': 0.17, 'bus': 0.10, 'rail': 0.04} kg CO2e/km
) -> Dict[str, Any]:
    """
    Calculate employee commuting emissions.

    Args:
        employees: Number of employees
        avg_commute_distance_km: Average one-way commute distance (km)
        working_days: Number of working days per year
        mode_split: Dictionary of mode split fractions (must sum to 1.0)
        mode_ef: Dictionary of emission factors by mode (kg CO2e/km)

    Returns:
        Dictionary with emissions
    """

    # Total commute distance for all employees
    total_distance_km = employees * avg_commute_distance_km * 2 * working_days  # *2 for round trip

    # Calculate emissions by mode
    emissions_by_mode = {}
    total_co2e_kg = 0.0

    for mode, fraction in mode_split.items():
        mode_distance = total_distance_km * fraction
        mode_emissions = mode_distance * mode_ef.get(mode, 0.0)
        emissions_by_mode[mode] = {
            'distance_km': mode_distance,
            'co2e_kg': mode_emissions,
        }
        total_co2e_kg += mode_emissions

    return {
        'emissions': {
            'CO2e': {'mass_kg': total_co2e_kg, 'co2e_kg': total_co2e_kg, 'gwp': 1},
        },
        'total_co2e_kg': total_co2e_kg,
        'total_distance_km': total_distance_km,
        'employees': employees,
        'working_days': working_days,
        'emissions_by_mode': emissions_by_mode,
        'method': 'Employee commuting',
    }


def calculate_air_travel(
    distance_km: float,
    flight_class: str = 'economy',  # economy, business, first
    radiative_forcing: float = 1.9,  # RFI multiplier for high-altitude emissions
    ef_base: Optional[float] = None,  # kg CO2/passenger-km
) -> Dict[str, Any]:
    """
    Calculate air travel emissions with radiative forcing index.

    Args:
        distance_km: Flight distance in km
        flight_class: Class of travel (affects space per passenger)
        radiative_forcing: RFI multiplier (typically 1.9 for aviation)
        ef_base: Base emission factor (if None, uses distance-based defaults)

    Returns:
        Dictionary with emissions
    """

    # Default emission factors by distance and class (kg CO2/pax-km)
    if ef_base is None:
        # Distance-based defaults (short-haul higher per km due to takeoff/landing)
        if distance_km < 500:
            ef_base = 0.25  # Short haul
        elif distance_km < 3700:
            ef_base = 0.15  # Medium haul
        else:
            ef_base = 0.12  # Long haul

        # Class multipliers (business/first take more space)
        class_multipliers = {
            'economy': 1.0,
            'premium_economy': 1.3,
            'business': 2.0,
            'first': 3.0,
        }
        ef_base *= class_multipliers.get(flight_class, 1.0)

    # Calculate base emissions
    co2_kg = distance_km * ef_base

    # Apply radiative forcing
    co2e_kg = co2_kg * radiative_forcing

    return {
        'emissions': {
            'CO2': {'mass_kg': co2_kg, 'co2e_kg': co2_kg, 'gwp': 1},
            'CO2e_with_RFI': {'mass_kg': co2e_kg, 'co2e_kg': co2e_kg, 'gwp': 1},
        },
        'total_co2e_kg': co2e_kg,
        'co2_only_kg': co2_kg,
        'distance_km': distance_km,
        'flight_class': flight_class,
        'radiative_forcing': radiative_forcing,
        'method': 'Air travel with RFI',
    }
