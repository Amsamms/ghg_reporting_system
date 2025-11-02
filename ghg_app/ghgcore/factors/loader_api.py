"""
API (American Petroleum Institute) emission factor loader.
Handles API Compendium of Greenhouse Gas Emissions Methodologies.
"""

import pandas as pd
from pathlib import Path
from typing import Dict
from .loader_base import EmissionFactorLoader


class APILoader(EmissionFactorLoader):
    """
    Loader for API Compendium emission factors.
    Specific to petroleum industry operations (flaring, fugitives, etc.)
    """

    def __init__(self):
        super().__init__(source_authority="API")

    def load_raw(self, file_path: Path) -> pd.DataFrame:
        """
        Load API emission factors.

        Args:
            file_path: Path to API data file

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
        API-specific column mapping.
        """
        return {
            'Source Type': 'subcategory',
            'Activity': 'activity_name',
            'Activity Code': 'activity_code',
            'Emission Source': 'activity_name',
            'Gas Type': 'gas',
            'GHG': 'gas',
            'Emission Factor': 'factor_value',
            'EF': 'factor_value',
            'Units': 'factor_unit',
            'Unit': 'factor_unit',
            'Technology': 'technology',
            'Equipment Type': 'technology',
            'Destruction Efficiency': 'oxidation_frac',
            'Section': 'source_table',
            'Table': 'source_table',
            'Year': 'source_year',
            'Uncertainty': 'uncertainty_pct',
        }

    def normalize(self, raw_df: pd.DataFrame) -> pd.DataFrame:
        """
        Custom normalization for API data.
        """
        df = super().normalize(raw_df)

        # API-specific settings
        df['geography'] = 'Global'
        df['region_code'] = 'GL'
        df['source_doc'] = 'API Compendium'

        # Map API source types to subcategories
        subcategory_mapping = {
            'Flaring': 'flaring',
            'Flare': 'flaring',
            'Fugitive': 'fugitives',
            'Fugitives': 'fugitives',
            'Equipment Leaks': 'fugitives',
            'Venting': 'venting',
            'Storage Tanks': 'fugitives',
            'Combustion': 'stationary_combustion',
        }

        if 'subcategory' in df.columns:
            df['subcategory'] = df['subcategory'].replace(subcategory_mapping)

        # API factors are typically Scope 1
        df['scope'] = df['scope'].fillna(1).astype(int)

        return df
