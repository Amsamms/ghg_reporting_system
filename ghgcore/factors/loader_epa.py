"""
EPA (US) emission factor loader.
Handles 40 CFR Part 98 (Greenhouse Gas Reporting Program) factors.
"""

import pandas as pd
from pathlib import Path
from typing import Dict
from .loader_base import EmissionFactorLoader


class EPALoader(EmissionFactorLoader):
    """
    Loader for EPA 40 CFR Part 98 emission factors.
    https://www.epa.gov/ghgreporting
    """

    def __init__(self):
        super().__init__(source_authority="EPA")

    def load_raw(self, file_path: Path) -> pd.DataFrame:
        """
        Load EPA emission factors.

        Args:
            file_path: Path to EPA data file (CSV or Excel)

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
        EPA-specific column mapping.
        """
        return {
            'Fuel Type': 'activity_name',
            'Fuel Code': 'activity_code',
            'CO2 Factor': 'factor_value',
            'CH4 Factor': 'factor_value',
            'N2O Factor': 'factor_value',
            'Gas': 'gas',
            'Emission Factor': 'factor_value',
            'Unit': 'factor_unit',
            'Default Unit': 'factor_unit',
            'HHV': 'basis',
            'Subpart': 'source_table',
            'Table': 'source_table',
            'Year': 'source_year',
        }

    def normalize(self, raw_df: pd.DataFrame) -> pd.DataFrame:
        """
        Custom normalization for EPA data.
        """
        # Handle EPA's multi-gas format (separate columns for CO2, CH4, N2O)
        # Convert to long format if necessary
        dfs = []

        gas_columns = {
            'CO2 Factor': 'CO2',
            'CH4 Factor': 'CH4',
            'N2O Factor': 'N2O',
        }

        # Check if data has separate gas columns
        has_gas_cols = any(col in raw_df.columns for col in gas_columns.keys())

        if has_gas_cols:
            # Melt from wide to long format
            for col, gas in gas_columns.items():
                if col in raw_df.columns:
                    df_gas = raw_df.copy()
                    df_gas['gas'] = gas
                    df_gas['factor_value'] = df_gas[col]
                    dfs.append(df_gas)

            raw_df = pd.concat(dfs, ignore_index=True)

        df = super().normalize(raw_df)

        # EPA-specific settings
        df['geography'] = 'USA'
        df['region_code'] = 'US'
        df['source_doc'] = '40 CFR Part 98'

        # Set default oxidation fraction for EPA factors
        df['oxidation_frac'] = df['oxidation_frac'].fillna(0.995)

        return df
