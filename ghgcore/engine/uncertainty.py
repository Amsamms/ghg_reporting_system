"""
Uncertainty quantification and propagation for GHG inventories.
Implements root-sum-of-squares (RSS) and Monte Carlo methods.
"""

import math
from typing import Dict, Any, List, Optional
import random


def propagate_uncertainty_rss(
    emissions: List[Dict[str, float]],
) -> Dict[str, float]:
    """
    Propagate uncertainty using root-sum-of-squares method.

    For independent sources: σ_total = sqrt(Σ(σ_i²))

    Args:
        emissions: List of emission dicts with 'value' and 'uncertainty_pct'

    Returns:
        Dictionary with total and combined uncertainty
    """

    total_value = 0.0
    sum_variance = 0.0

    for emission in emissions:
        value = emission.get('value', 0)
        uncertainty_pct = emission.get('uncertainty_pct', 0)

        total_value += value

        # Convert percentage to absolute uncertainty
        abs_uncertainty = value * (uncertainty_pct / 100)

        # Add variance (σ²)
        sum_variance += abs_uncertainty ** 2

    # Combined standard deviation
    combined_std = math.sqrt(sum_variance)

    # Convert back to percentage
    combined_uncertainty_pct = (combined_std / total_value * 100) if total_value > 0 else 0

    return {
        'total_value': total_value,
        'combined_std_deviation': combined_std,
        'combined_uncertainty_pct': combined_uncertainty_pct,
        'confidence_interval_95': combined_std * 1.96,  # 95% CI
    }


def calculate_activity_uncertainty(
    activity_data_uncertainty: float,  # %
    emission_factor_uncertainty: float,  # %
) -> float:
    """
    Calculate combined uncertainty for a single activity.

    For multiplication: σ_total = sqrt((σ_data)² + (σ_ef)²)

    Args:
        activity_data_uncertainty: Uncertainty in activity data (%)
        emission_factor_uncertainty: Uncertainty in emission factor (%)

    Returns:
        Combined uncertainty (%)
    """

    combined = math.sqrt(
        activity_data_uncertainty ** 2 +
        emission_factor_uncertainty ** 2
    )

    return combined


def assign_tier_uncertainty(
    method_tier: int,
    data_source: str,
) -> float:
    """
    Assign typical uncertainty based on IPCC tier and data source.

    Args:
        method_tier: IPCC tier (1, 2, or 3)
        data_source: Data source type ('measured', 'estimated', 'default')

    Returns:
        Typical uncertainty percentage
    """

    # IPCC default uncertainties by tier
    tier_uncertainties = {
        1: 50,  # Tier 1: Default factors, high uncertainty
        2: 25,  # Tier 2: Country-specific or sector-specific
        3: 10,  # Tier 3: Direct measurement, facility-specific
    }

    base_uncertainty = tier_uncertainties.get(method_tier, 50)

    # Adjust for data source
    data_source_factors = {
        'measured': 0.5,  # Reduce by half for measured data
        'estimated': 1.0,  # No adjustment
        'default': 1.5,   # Increase for default assumptions
    }

    factor = data_source_factors.get(data_source.lower(), 1.0)

    return base_uncertainty * factor


def monte_carlo_uncertainty(
    mean_values: List[float],
    uncertainties: List[float],  # Standard deviations
    n_iterations: int = 10000,
    confidence_level: float = 0.95,
) -> Dict[str, Any]:
    """
    Monte Carlo simulation for uncertainty propagation.

    Args:
        mean_values: List of mean emission values
        uncertainties: List of standard deviations
        n_iterations: Number of Monte Carlo iterations
        confidence_level: Confidence level (default 0.95 for 95%)

    Returns:
        Dictionary with simulation results
    """

    simulation_totals = []

    for _ in range(n_iterations):
        iteration_total = 0

        for mean, std in zip(mean_values, uncertainties):
            # Sample from normal distribution
            sampled_value = random.gauss(mean, std)
            # Ensure non-negative
            sampled_value = max(0, sampled_value)
            iteration_total += sampled_value

        simulation_totals.append(iteration_total)

    # Sort results
    simulation_totals.sort()

    # Calculate statistics
    mean_total = sum(simulation_totals) / n_iterations
    median_total = simulation_totals[n_iterations // 2]

    # Confidence interval
    lower_idx = int((1 - confidence_level) / 2 * n_iterations)
    upper_idx = int((1 + confidence_level) / 2 * n_iterations)

    lower_bound = simulation_totals[lower_idx]
    upper_bound = simulation_totals[upper_idx]

    return {
        'mean': mean_total,
        'median': median_total,
        'lower_bound': lower_bound,
        'upper_bound': upper_bound,
        'confidence_level': confidence_level,
        'std_deviation': (upper_bound - lower_bound) / (2 * 1.96),  # Approximate
        'n_iterations': n_iterations,
    }


def uncertainty_by_scope(
    scope_emissions: Dict[int, Dict[str, Any]],
) -> Dict[int, Dict[str, float]]:
    """
    Calculate uncertainty for each scope.

    Args:
        scope_emissions: Dict of emissions by scope with uncertainty info

    Returns:
        Dict of uncertainty metrics by scope
    """

    scope_uncertainty = {}

    for scope, data in scope_emissions.items():
        emissions_list = []

        for gas, gas_data in data.items():
            if gas.startswith('_'):  # Skip metadata fields
                continue

            value = gas_data.get('co2e_kg', 0)
            uncertainty_pct = gas_data.get('uncertainty_pct', 25)  # Default 25%

            emissions_list.append({
                'value': value,
                'uncertainty_pct': uncertainty_pct,
            })

        if emissions_list:
            scope_uncertainty[scope] = propagate_uncertainty_rss(emissions_list)
        else:
            scope_uncertainty[scope] = {
                'total_value': 0,
                'combined_uncertainty_pct': 0,
            }

    return scope_uncertainty


def quality_score(
    data_quality: str,  # 'high', 'medium', 'low'
    completeness: float,  # 0-1
    has_documentation: bool,
) -> float:
    """
    Calculate a quality score for emissions data (0-100).

    Args:
        data_quality: Qualitative data quality assessment
        completeness: Data completeness fraction (0-1)
        has_documentation: Whether supporting documentation exists

    Returns:
        Quality score (0-100)
    """

    # Base score from data quality
    quality_scores = {
        'high': 80,
        'medium': 50,
        'low': 20,
    }

    base_score = quality_scores.get(data_quality.lower(), 50)

    # Adjust for completeness
    completeness_score = completeness * 15

    # Documentation bonus
    doc_score = 5 if has_documentation else 0

    total_score = base_score + completeness_score + doc_score

    return min(100, total_score)
