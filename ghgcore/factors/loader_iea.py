"""
IEA (International Energy Agency) emission factor loader.
Handles IEA electricity grid emission factors and energy statistics.
"""

import pandas as pd
from pathlib import Path
from typing import Dict
from .loader_base import EmissionFactorLoader


class IEALoader(EmissionFactorLoader):
    """
    Loader for IEA emission factors.
    Primarily for electricity grid factors by country.
    """

    def __init__(self):
        super().__init__(source_authority="IEA")

    def load_raw(self, file_path: Path) -> pd.DataFrame:
        """
        Load IEA emission factors.

        Args:
            file_path: Path to IEA data file

        Returns:
            Raw DataFrame
        """
        if file_path.suffix.lower() == '.csv':
            return pd.read_csv(file_path)
        elif file_path.suffix.lower() in ['.xlsx', '.xls']:
            return pd.read_excel(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")

    def get_column_mapping(self) -> Dict[str, str]:
        """
        IEA-specific column mapping.
        """
        return {
            'Country': 'geography',
            'Country/Region': 'geography',
            'ISO Code': 'region_code',
            'Year': 'source_year',
            'Emission Factor': 'factor_value',
            'EF': 'factor_value',
            'gCO2/kWh': 'factor_value',
            'Grid Factor': 'factor_value',
            'Unit': 'factor_unit',
            'Technology': 'technology',
            'Grid Mix': 'technology',
        }

    def normalize(self, raw_df: pd.DataFrame) -> pd.DataFrame:
        """
        Custom normalization for IEA data.
        """
        df = super().normalize(raw_df)

        # IEA-specific settings
        df['source_doc'] = 'IEA Country CO2 Factors'

        # IEA factors are typically Scope 2 electricity
        df['scope'] = df['scope'].fillna(2).astype(int)
        df['subcategory'] = df['subcategory'].fillna('purchased_electricity')
        df['gas'] = df['gas'].fillna('CO2')

        # Convert gCO2/kWh to kg CO2/kWh if needed
        if 'factor_unit' in df.columns:
            mask = df['factor_unit'].str.contains('gCO2', na=False)
            df.loc[mask, 'factor_value'] = df.loc[mask, 'factor_value'] / 1000
            df.loc[mask, 'factor_unit'] = 'kg CO2/kWh'

        # Set market_or_location
        df['market_or_location'] = df['market_or_location'].fillna('location')

        # Generate activity codes if missing
        if 'activity_code' not in df.columns or df['activity_code'].isna().all():
            df['activity_code'] = 'S2_ELECTRICITY_' + df['region_code'].fillna('XX')

        if 'activity_name' not in df.columns or df['activity_name'].isna().all():
            df['activity_name'] = 'Grid electricity - ' + df['geography'].fillna('Unknown')

        return df
