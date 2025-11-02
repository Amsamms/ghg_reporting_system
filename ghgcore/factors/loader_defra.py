"""
DEFRA (UK) emission factor loader.
Handles UK Government GHG Conversion Factors.
"""

import pandas as pd
from pathlib import Path
from typing import Dict
from .loader_base import EmissionFactorLoader


class DEFRALoader(EmissionFactorLoader):
    """
    Loader for DEFRA UK GHG Conversion Factors.
    https://www.gov.uk/government/publications/greenhouse-gas-reporting-conversion-factors
    """

    def __init__(self):
        super().__init__(source_authority="DEFRA")

    def load_raw(self, file_path: Path) -> pd.DataFrame:
        """
        Load DEFRA emission factors from Excel file.

        Args:
            file_path: Path to DEFRA Excel file

        Returns:
            Raw DataFrame
        """
        # DEFRA typically publishes multi-sheet Excel files
        # Load all sheets and concatenate
        dfs = []

        try:
            xl_file = pd.ExcelFile(file_path)

            for sheet_name in xl_file.sheet_names:
                # Skip documentation/info sheets
                if 'info' in sheet_name.lower() or 'contents' in sheet_name.lower():
                    continue

                df = pd.read_excel(file_path, sheet_name=sheet_name)
                df['_source_sheet'] = sheet_name
                dfs.append(df)

            if dfs:
                return pd.concat(dfs, ignore_index=True)
            else:
                raise ValueError("No valid data sheets found in DEFRA file")

        except Exception as e:
            raise ValueError(f"Error loading DEFRA file: {e}")

    def get_column_mapping(self) -> Dict[str, str]:
        """
        DEFRA-specific column mapping.
        Note: Actual DEFRA column names may vary by year/version.
        """
        return {
            'Scope': 'scope',
            'Level 1': 'subcategory',
            'Level 2': 'activity_name',
            'Level 3': 'activity_code',
            'GHG': 'gas',
            'kgCO2e': 'factor_value',
            'Unit': 'factor_unit',
            'UOM': 'factor_unit',
            'Year': 'source_year',
            'GHG Conversion Factor 2024': 'factor_value',
            'Activity': 'activity_name',
            'Type': 'technology',
        }

    def normalize(self, raw_df: pd.DataFrame) -> pd.DataFrame:
        """
        Custom normalization for DEFRA data.
        """
        df = super().normalize(raw_df)

        # DEFRA-specific post-processing
        # Set geography to UK
        df['geography'] = 'UK'
        df['region_code'] = 'GB'

        # Set source document
        df['source_doc'] = '2024 GHG Conversion Factors'

        # Infer subcategory from sheet name if available
        if '_source_sheet' in raw_df.columns:
            def map_sheet_to_subcategory(sheet_name):
                sheet_lower = sheet_name.lower()
                if 'fuel' in sheet_lower or 'combustion' in sheet_lower:
                    return 'stationary_combustion'
                elif 'electricity' in sheet_lower:
                    return 'purchased_electricity'
                elif 'transport' in sheet_lower or 'freight' in sheet_lower:
                    return 'transport_downstream'
                elif 'travel' in sheet_lower:
                    return 'business_travel'
                else:
                    return 'other'

            if 'subcategory' not in df.columns or df['subcategory'].isna().all():
                df['subcategory'] = raw_df['_source_sheet'].apply(map_sheet_to_subcategory)

        return df
