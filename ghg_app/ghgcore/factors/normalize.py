"""
Normalization functions to map raw emission factors to canonical format.
"""

import pandas as pd
from typing import Dict, Any
from datetime import datetime


def normalize_emission_factors(
    raw_df: pd.DataFrame,
    column_mapping: Dict[str, str],
    source_authority: str
) -> pd.DataFrame:
    """
    Normalize raw emission factors to canonical format.

    Args:
        raw_df: Raw DataFrame from authority source
        column_mapping: Dict mapping raw_column -> canonical_column
        source_authority: Authority name

    Returns:
        DataFrame with canonical columns
    """

    # Create copy to avoid modifying original
    df = raw_df.copy()

    # Rename columns according to mapping
    # Only rename columns that exist in the DataFrame
    existing_mappings = {k: v for k, v in column_mapping.items() if k in df.columns}
    df = df.rename(columns=existing_mappings)

    # Ensure source_authority is set
    if 'source_authority' not in df.columns:
        df['source_authority'] = source_authority

    # Fill in default values for optional fields
    defaults = {
        'basis': 'NA',
        'oxidation_frac': 1.0,
        'fuel_state': 'NA',
        'geography': 'Global',
        'region_code': None,
        'market_or_location': 'NA',
        'technology': None,
        'uncertainty_pct': None,
        'valid_to': None,
        'citation': None,
        'method_equation_ref': None,
        'notes': None,
    }

    for col, default_val in defaults.items():
        if col not in df.columns:
            df[col] = default_val

    # Ensure valid_from exists (use current date if not specified)
    if 'valid_from' not in df.columns:
        df['valid_from'] = datetime.now().date()

    # Data type conversions
    if 'scope' in df.columns:
        df['scope'] = pd.to_numeric(df['scope'], errors='coerce').fillna(1).astype(int)

    if 'factor_value' in df.columns:
        df['factor_value'] = pd.to_numeric(df['factor_value'], errors='coerce')

    if 'source_year' in df.columns:
        df['source_year'] = pd.to_numeric(df['source_year'], errors='coerce').fillna(
            datetime.now().year
        ).astype(int)

    if 'uncertainty_pct' in df.columns:
        df['uncertainty_pct'] = pd.to_numeric(df['uncertainty_pct'], errors='coerce')

    if 'oxidation_frac' in df.columns:
        df['oxidation_frac'] = pd.to_numeric(df['oxidation_frac'], errors='coerce').fillna(1.0)

    # Clean up gas names (standardize formatting)
    if 'gas' in df.columns:
        df['gas'] = df['gas'].str.strip().str.upper()
        # Handle common variations
        df['gas'] = df['gas'].replace({
            'CO₂': 'CO2',
            'CH₄': 'CH4',
            'N₂O': 'N2O',
        })

    # Ensure required canonical columns exist (add empty if missing)
    canonical_columns = [
        'scope', 'subcategory', 'activity_code', 'activity_name', 'gas',
        'factor_value', 'factor_unit', 'basis', 'oxidation_frac', 'fuel_state',
        'source_authority', 'source_doc', 'source_table', 'source_year',
        'geography', 'region_code', 'market_or_location', 'technology',
        'uncertainty_pct', 'valid_from', 'valid_to', 'citation',
        'method_equation_ref', 'notes'
    ]

    for col in canonical_columns:
        if col not in df.columns:
            df[col] = None

    # Select and order columns
    df = df[canonical_columns]

    # Drop rows with missing critical values
    df = df.dropna(subset=['activity_code', 'gas', 'factor_value', 'factor_unit'])

    return df


def infer_scope_from_subcategory(subcategory: str) -> int:
    """
    Infer GHG Protocol scope from subcategory.

    Args:
        subcategory: Subcategory string

    Returns:
        Scope number (1, 2, or 3)
    """
    scope_1_categories = [
        'stationary_combustion', 'mobile_combustion', 'flaring',
        'fugitives', 'process_co2', 'venting', 'process_emissions'
    ]

    scope_2_categories = [
        'purchased_electricity', 'purchased_steam', 'purchased_heat',
        'purchased_cooling', 'electricity', 'steam', 'heat', 'cooling'
    ]

    # Scope 3 is everything else
    if any(cat in subcategory.lower() for cat in scope_1_categories):
        return 1
    elif any(cat in subcategory.lower() for cat in scope_2_categories):
        return 2
    else:
        return 3


def standardize_unit(unit_str: str) -> str:
    """
    Standardize emission factor unit strings.

    Args:
        unit_str: Raw unit string

    Returns:
        Standardized unit string
    """
    # Replace common variations
    unit_str = unit_str.replace('kgCO2e', 'kg CO2e')
    unit_str = unit_str.replace('kgCO2', 'kg CO2')
    unit_str = unit_str.replace('kgCH4', 'kg CH4')
    unit_str = unit_str.replace('kgN2O', 'kg N2O')

    # Standardize per notation
    unit_str = unit_str.replace(' per ', '/')

    return unit_str.strip()
