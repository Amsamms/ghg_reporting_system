"""
Base class for emission factor loaders.
All authority-specific loaders inherit from this.
"""

from abc import ABC, abstractmethod
import pandas as pd
from typing import Optional, Dict, Any
from pathlib import Path


class EmissionFactorLoader(ABC):
    """
    Abstract base class for emission factor loaders.
    Each authority (DEFRA, EPA, IPCC, API, IEA) implements a concrete loader.
    """

    def __init__(self, source_authority: str):
        """
        Initialize loader.

        Args:
            source_authority: Authority name (e.g., "DEFRA", "EPA")
        """
        self.source_authority = source_authority

    @abstractmethod
    def load_raw(self, file_path: Path) -> pd.DataFrame:
        """
        Load raw emission factors from source file.

        Args:
            file_path: Path to source file (Excel, CSV, etc.)

        Returns:
            Raw DataFrame with authority-specific columns
        """
        pass

    @abstractmethod
    def get_column_mapping(self) -> Dict[str, str]:
        """
        Get mapping from raw columns to canonical columns.

        Returns:
            Dictionary mapping raw_column -> canonical_column
        """
        pass

    def normalize(self, raw_df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize raw emission factors to canonical format.

        Args:
            raw_df: Raw DataFrame from load_raw()

        Returns:
            Normalized DataFrame with canonical columns
        """
        from .normalize import normalize_emission_factors

        column_mapping = self.get_column_mapping()
        return normalize_emission_factors(
            raw_df,
            column_mapping,
            self.source_authority
        )

    def load_and_normalize(self, file_path: Path) -> pd.DataFrame:
        """
        Load raw data and normalize to canonical format (convenience method).

        Args:
            file_path: Path to source file

        Returns:
            Normalized DataFrame
        """
        raw_df = self.load_raw(file_path)
        return self.normalize(raw_df)

    def validate(self, df: pd.DataFrame) -> tuple[bool, list[str]]:
        """
        Validate normalized emission factors.

        Args:
            df: Normalized DataFrame

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        # Required columns
        required_cols = [
            'scope', 'subcategory', 'activity_code', 'activity_name',
            'gas', 'factor_value', 'factor_unit', 'source_authority',
            'source_year', 'valid_from'
        ]

        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            errors.append(f"Missing required columns: {missing_cols}")

        # Validate scope values
        if 'scope' in df.columns:
            invalid_scopes = df[~df['scope'].isin([1, 2, 3])]
            if not invalid_scopes.empty:
                errors.append(f"Invalid scope values found: {invalid_scopes['scope'].unique()}")

        # Validate factor_value
        if 'factor_value' in df.columns:
            non_positive = df[df['factor_value'] <= 0]
            if not non_positive.empty:
                errors.append(f"Non-positive factor_value found in {len(non_positive)} rows")

        # Validate gas names
        if 'gas' in df.columns:
            valid_gases = ['CO2', 'CH4', 'N2O', 'SF6', 'HFC-134a', 'HFC-125', 'HFC-32',
                           'HFC-143a', 'HFC-152a', 'CF4', 'C2F6', 'NF3']
            invalid_gases = df[~df['gas'].isin(valid_gases)]
            if not invalid_gases.empty:
                gases_found = invalid_gases['gas'].unique()
                errors.append(f"Non-standard gas names found: {gases_found} (may be valid, check manually)")

        is_valid = len(errors) == 0
        return is_valid, errors

    def get_authority_metadata(self) -> Dict[str, Any]:
        """
        Get metadata about this emission factor source.

        Returns:
            Dictionary with authority, version, retrieved_on, etc.
        """
        return {
            'source_authority': self.source_authority,
            'loader_class': self.__class__.__name__,
        }
