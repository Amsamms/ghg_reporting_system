"""
IPCC emission factor loader.
Handles IPCC Guidelines for National Greenhouse Gas Inventories.
"""

import pandas as pd
from pathlib import Path
from typing import Dict
from .loader_base import EmissionFactorLoader


class IPCCLoader(EmissionFactorLoader):
    """
    Loader for IPCC emission factors (2006/2019 Guidelines).
    https://www.ipcc-nggip.iges.or.jp/
    """

    def __init__(self):
        super().__init__(source_authority="IPCC")

    def load_raw(self, file_path: Path) -> pd.DataFrame:
        """
        Load IPCC emission factors.

        Args:
            file_path: Path to IPCC data file

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
        IPCC-specific column mapping.
        """
        return {
            'Fuel': 'activity_name',
            'Fuel Type': 'activity_name',
            'IPCC Code': 'activity_code',
            'CO2': 'factor_value',
            'CH4': 'factor_value',
            'N2O': 'factor_value',
            'Gas': 'gas',
            'Emission Factor': 'factor_value',
            'EF': 'factor_value',
            'Unit': 'factor_unit',
            'Default Unit': 'factor_unit',
            'Net Calorific Value': 'basis',
            'NCV': 'basis',
            'Chapter': 'source_table',
            'Volume': 'source_doc',
            'Technology': 'technology',
            'Default Value': 'factor_value',
            'Lower': 'uncertainty_pct',
            'Upper': 'uncertainty_pct',
        }

    def normalize(self, raw_df: pd.DataFrame) -> pd.DataFrame:
        """
        Custom normalization for IPCC data.
        """
        # Handle IPCC's multi-gas format similar to EPA
        gas_columns = {
            'CO2': 'CO2',
            'CH4': 'CH4',
            'N2O': 'N2O',
        }

        dfs = []
        has_gas_cols = any(col in raw_df.columns for col in gas_columns.keys())

        if has_gas_cols:
            for col, gas in gas_columns.items():
                if col in raw_df.columns:
                    df_gas = raw_df.copy()
                    df_gas['gas'] = gas
                    df_gas['factor_value'] = df_gas[col]
                    dfs.append(df_gas)

            raw_df = pd.concat(dfs, ignore_index=True)

        df = super().normalize(raw_df)

        # IPCC-specific settings
        df['geography'] = 'Global'
        df['region_code'] = 'GL'
        df['source_doc'] = '2006 IPCC Guidelines'

        # IPCC typically uses Net Calorific Value (NCV) = LHV
        df['basis'] = df['basis'].replace({'NCV': 'LHV', 'Net': 'LHV', 'Gross': 'HHV'})

        return df
