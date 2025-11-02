"""
CLI tool to seed emission factors into the database from Excel/CSV files.
Usage: python -m ghgcore.factors.seed_factors --from-excel path/to/file.xlsx
"""

import argparse
from pathlib import Path
from sqlmodel import Session, select
from ..db import engine, create_db_and_tables
from ..models import EmissionFactor
from .loader_defra import DEFRALoader
from .loader_epa import EPALoader
from .loader_ipcc import IPCCLoader
from .loader_api import APILoader
from .loader_iea import IEALoader


def seed_from_excel(file_path: Path, authority: str = None):
    """
    Seed emission factors from Excel file.

    Args:
        file_path: Path to Excel file
        authority: Authority name (auto-detect if None)
    """
    # Auto-detect authority from filename if not specified
    if authority is None:
        filename_lower = file_path.name.lower()
        if 'defra' in filename_lower or 'uk' in filename_lower:
            authority = 'DEFRA'
        elif 'epa' in filename_lower or 'cfr' in filename_lower:
            authority = 'EPA'
        elif 'ipcc' in filename_lower:
            authority = 'IPCC'
        elif 'api' in filename_lower:
            authority = 'API'
        elif 'iea' in filename_lower:
            authority = 'IEA'
        else:
            raise ValueError("Cannot auto-detect authority. Please specify with --authority")

    # Get appropriate loader
    loaders = {
        'DEFRA': DEFRALoader(),
        'EPA': EPALoader(),
        'IPCC': IPCCLoader(),
        'API': APILoader(),
        'IEA': IEALoader(),
    }

    loader = loaders.get(authority.upper())
    if not loader:
        raise ValueError(f"Unknown authority: {authority}")

    print(f"Loading emission factors from {file_path} using {authority} loader...")

    # Load and normalize
    df = loader.load_and_normalize(file_path)

    # Validate
    is_valid, errors = loader.validate(df)
    if not is_valid:
        print("⚠️  Validation warnings:")
        for error in errors:
            print(f"  - {error}")
        print()

    # Insert into database
    with Session(engine) as session:
        count = 0
        for _, row in df.iterrows():
            ef = EmissionFactor(
                scope=int(row['scope']) if row['scope'] else 1,
                subcategory=row['subcategory'],
                activity_code=row['activity_code'],
                activity_name=row['activity_name'],
                gas=row['gas'],
                factor_value=float(row['factor_value']),
                factor_unit=row['factor_unit'],
                basis=row['basis'] if row['basis'] else 'NA',
                oxidation_frac=float(row['oxidation_frac']) if row['oxidation_frac'] else 1.0,
                fuel_state=row['fuel_state'] if row['fuel_state'] else 'NA',
                source_authority=row['source_authority'],
                source_doc=row['source_doc'],
                source_table=row['source_table'],
                source_year=int(row['source_year']) if row['source_year'] else 2024,
                geography=row['geography'] if row['geography'] else 'Global',
                region_code=row['region_code'],
                market_or_location=row['market_or_location'] if row['market_or_location'] else 'NA',
                technology=row['technology'],
                uncertainty_pct=float(row['uncertainty_pct']) if row['uncertainty_pct'] else None,
                valid_from=row['valid_from'],
                valid_to=row['valid_to'],
                citation=row['citation'],
                method_equation_ref=row['method_equation_ref'],
                notes=row['notes'],
            )
            session.add(ef)
            count += 1

        session.commit()
        print(f"✓ Successfully seeded {count} emission factors from {authority}")


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Seed emission factors into the GHG inventory database"
    )
    parser.add_argument(
        '--from-excel',
        type=Path,
        help='Path to Excel file containing emission factors'
    )
    parser.add_argument(
        '--authority',
        type=str,
        choices=['DEFRA', 'EPA', 'IPCC', 'API', 'IEA'],
        help='Emission factor authority (auto-detect if not specified)'
    )
    parser.add_argument(
        '--init-db',
        action='store_true',
        help='Initialize database and create tables'
    )

    args = parser.parse_args()

    # Initialize database if requested
    if args.init_db:
        print("Initializing database...")
        create_db_and_tables()
        from ..db import init_db
        init_db()
        print("✓ Database initialized")

    # Seed from Excel
    if args.from_excel:
        if not args.from_excel.exists():
            print(f"Error: File not found: {args.from_excel}")
            return

        seed_from_excel(args.from_excel, args.authority)


if __name__ == "__main__":
    main()
