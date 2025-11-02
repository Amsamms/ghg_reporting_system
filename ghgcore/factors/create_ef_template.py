"""
Script to create the Emission Factor Master Template Excel file.
Run this to generate the canonical EF_Master_Template.xlsx
"""

import pandas as pd
from pathlib import Path
from datetime import date


def create_ef_master_template():
    """Create the emission factor master template with all required sheets."""

    output_path = Path(__file__).parent / "templates" / "EF_Master_Template.xlsx"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Define the canonical columns
    ef_columns = [
        'scope', 'subcategory', 'activity_code', 'activity_name', 'gas',
        'factor_value', 'factor_unit', 'basis', 'oxidation_frac', 'fuel_state',
        'source_authority', 'source_doc', 'source_table', 'source_year',
        'geography', 'region_code', 'market_or_location', 'technology',
        'uncertainty_pct', 'valid_from', 'valid_to', 'citation',
        'method_equation_ref', 'notes'
    ]

    # Sample emission factors (illustrative)
    sample_factors = [
        # Scope 1 - Stationary Combustion - Natural Gas
        {
            'scope': 1, 'subcategory': 'stationary_combustion',
            'activity_code': 'S1_SC_NG', 'activity_name': 'Pipeline natural gas - combustion',
            'gas': 'CO2', 'factor_value': 56.1, 'factor_unit': 'kg CO2/GJ',
            'basis': 'HHV', 'oxidation_frac': 0.995, 'fuel_state': 'gas',
            'source_authority': 'EPA', 'source_doc': '40 CFR 98 Subpart C',
            'source_table': 'Table C-1', 'source_year': 2025,
            'geography': 'USA', 'region_code': 'US', 'market_or_location': 'NA',
            'technology': 'boiler', 'uncertainty_pct': 3.0,
            'valid_from': '2025-01-01', 'valid_to': None,
            'citation': 'https://www.ecfr.gov/current/title-40/chapter-I/subchapter-C/part-98',
            'method_equation_ref': 'EPA C-1',
            'notes': 'Default emission factor for natural gas combustion'
        },
        {
            'scope': 1, 'subcategory': 'stationary_combustion',
            'activity_code': 'S1_SC_NG', 'activity_name': 'Pipeline natural gas - combustion',
            'gas': 'CH4', 'factor_value': 0.001, 'factor_unit': 'kg CH4/GJ',
            'basis': 'HHV', 'oxidation_frac': 1.0, 'fuel_state': 'gas',
            'source_authority': 'EPA', 'source_doc': '40 CFR 98 Subpart C',
            'source_table': 'Table C-2', 'source_year': 2025,
            'geography': 'USA', 'region_code': 'US', 'market_or_location': 'NA',
            'technology': 'boiler', 'uncertainty_pct': 50.0,
            'valid_from': '2025-01-01', 'valid_to': None,
            'citation': 'https://www.ecfr.gov/current/title-40/chapter-I/subchapter-C/part-98',
            'method_equation_ref': 'EPA C-2',
            'notes': 'Methane emissions from natural gas combustion'
        },
        {
            'scope': 1, 'subcategory': 'stationary_combustion',
            'activity_code': 'S1_SC_NG', 'activity_name': 'Pipeline natural gas - combustion',
            'gas': 'N2O', 'factor_value': 0.0001, 'factor_unit': 'kg N2O/GJ',
            'basis': 'HHV', 'oxidation_frac': 1.0, 'fuel_state': 'gas',
            'source_authority': 'EPA', 'source_doc': '40 CFR 98 Subpart C',
            'source_table': 'Table C-2', 'source_year': 2025,
            'geography': 'USA', 'region_code': 'US', 'market_or_location': 'NA',
            'technology': 'boiler', 'uncertainty_pct': 50.0,
            'valid_from': '2025-01-01', 'valid_to': None,
            'citation': 'https://www.ecfr.gov/current/title-40/chapter-I/subchapter-C/part-98',
            'method_equation_ref': 'EPA C-2',
            'notes': 'Nitrous oxide emissions from natural gas combustion'
        },

        # Scope 1 - Stationary Combustion - Refinery Fuel Gas
        {
            'scope': 1, 'subcategory': 'stationary_combustion',
            'activity_code': 'S1_SC_FUELGAS', 'activity_name': 'Refinery fuel gas - combustion',
            'gas': 'CO2', 'factor_value': 57.5, 'factor_unit': 'kg CO2/GJ',
            'basis': 'HHV', 'oxidation_frac': 0.995, 'fuel_state': 'gas',
            'source_authority': 'IPCC', 'source_doc': '2006 GL Vol2',
            'source_table': 'Ch2 defaults', 'source_year': 2019,
            'geography': 'Global', 'region_code': 'GL', 'market_or_location': 'NA',
            'technology': 'heater', 'uncertainty_pct': 5.0,
            'valid_from': '2019-01-01', 'valid_to': None,
            'citation': 'https://www.ipcc-nggip.iges.or.jp/public/2006gl/',
            'method_equation_ref': 'IPCC V2Ch2',
            'notes': 'Composition-specific overrides allowed'
        },

        # Scope 1 - Stationary Combustion - Diesel
        {
            'scope': 1, 'subcategory': 'stationary_combustion',
            'activity_code': 'S1_SC_DIESEL', 'activity_name': 'Diesel oil - combustion',
            'gas': 'CO2', 'factor_value': 74.1, 'factor_unit': 'kg CO2/GJ',
            'basis': 'HHV', 'oxidation_frac': 0.99, 'fuel_state': 'liquid',
            'source_authority': 'IPCC', 'source_doc': '2006 GL Vol2',
            'source_table': 'Table 2.3', 'source_year': 2019,
            'geography': 'Global', 'region_code': 'GL', 'market_or_location': 'NA',
            'technology': 'generator', 'uncertainty_pct': 5.0,
            'valid_from': '2019-01-01', 'valid_to': None,
            'citation': 'https://www.ipcc-nggip.iges.or.jp/public/2006gl/',
            'method_equation_ref': 'IPCC V2Ch2 Eq2.1',
            'notes': 'Default diesel emission factor'
        },

        # Scope 2 - Electricity - Egypt Grid
        {
            'scope': 2, 'subcategory': 'purchased_electricity',
            'activity_code': 'S2_ELECTRICITY', 'activity_name': 'Grid electricity - Egypt (location)',
            'gas': 'CO2', 'factor_value': 0.45, 'factor_unit': 'kg CO2/kWh',
            'basis': 'NA', 'oxidation_frac': None, 'fuel_state': 'NA',
            'source_authority': 'IEA', 'source_doc': 'Country CO2 factors',
            'source_table': 'Egypt 2023', 'source_year': 2024,
            'geography': 'Egypt', 'region_code': 'EG', 'market_or_location': 'location',
            'technology': 'grid-mix', 'uncertainty_pct': 10.0,
            'valid_from': '2024-01-01', 'valid_to': None,
            'citation': 'https://www.iea.org/data-and-statistics',
            'method_equation_ref': 'IEA method',
            'notes': 'Illustrative Egypt grid emission factor'
        },

        # Scope 1 - Flaring
        {
            'scope': 1, 'subcategory': 'flaring',
            'activity_code': 'S1_FLARE_NG', 'activity_name': 'Natural gas flaring',
            'gas': 'CO2', 'factor_value': 2.55, 'factor_unit': 'kg CO2/Nm3',
            'basis': 'NA', 'oxidation_frac': 0.98, 'fuel_state': 'gas',
            'source_authority': 'API', 'source_doc': 'API Compendium',
            'source_table': 'Flaring defaults', 'source_year': 2021,
            'geography': 'Global', 'region_code': 'GL', 'market_or_location': 'NA',
            'technology': 'smokeless_flare', 'uncertainty_pct': 15.0,
            'valid_from': '2021-01-01', 'valid_to': None,
            'citation': 'https://www.api.org/oil-and-natural-gas/environment/clean-air/ghg-emissions-estimation',
            'method_equation_ref': 'API Compendium 2021',
            'notes': 'Assumes 98% destruction efficiency for smokeless flare'
        },

        # Scope 3 - Transportation
        {
            'scope': 3, 'subcategory': 'transport_downstream',
            'activity_code': 'S3_TRUCK_DIESEL', 'activity_name': 'Heavy duty truck - diesel',
            'gas': 'CO2', 'factor_value': 0.062, 'factor_unit': 'kg CO2/tonne-km',
            'basis': 'NA', 'oxidation_frac': None, 'fuel_state': 'NA',
            'source_authority': 'DEFRA', 'source_doc': '2024 GHG Conversion Factors',
            'source_table': 'Freight transport', 'source_year': 2024,
            'geography': 'UK', 'region_code': 'GB', 'market_or_location': 'NA',
            'technology': 'articulated_hgv', 'uncertainty_pct': 20.0,
            'valid_from': '2024-01-01', 'valid_to': None,
            'citation': 'https://www.gov.uk/government/publications/greenhouse-gas-reporting-conversion-factors-2024',
            'method_equation_ref': 'DEFRA 2024',
            'notes': 'Average load factor included'
        },
    ]

    # Create DataFrame
    df_factors = pd.DataFrame(sample_factors, columns=ef_columns)

    # GWP sets
    gwp_columns = ['set_name', 'gas', 'horizon_yr', 'value']
    gwp_data = [
        # AR5
        {'set_name': 'AR5', 'gas': 'CO2', 'horizon_yr': 100, 'value': 1},
        {'set_name': 'AR5', 'gas': 'CH4', 'horizon_yr': 100, 'value': 28},
        {'set_name': 'AR5', 'gas': 'N2O', 'horizon_yr': 100, 'value': 265},
        {'set_name': 'AR5', 'gas': 'SF6', 'horizon_yr': 100, 'value': 23500},
        {'set_name': 'AR5', 'gas': 'HFC-134a', 'horizon_yr': 100, 'value': 1300},
        # AR6
        {'set_name': 'AR6', 'gas': 'CO2', 'horizon_yr': 100, 'value': 1},
        {'set_name': 'AR6', 'gas': 'CH4', 'horizon_yr': 100, 'value': 27.9},
        {'set_name': 'AR6', 'gas': 'N2O', 'horizon_yr': 100, 'value': 273},
        {'set_name': 'AR6', 'gas': 'SF6', 'horizon_yr': 100, 'value': 25200},
        {'set_name': 'AR6', 'gas': 'HFC-134a', 'horizon_yr': 100, 'value': 1530},
    ]
    df_gwp = pd.DataFrame(gwp_data, columns=gwp_columns)

    # Activity catalog
    activity_columns = ['activity_code', 'activity_name', 'scope', 'subcategory', 'default_unit', 'method_key']
    activity_data = [
        {'activity_code': 'S1_SC_NG', 'activity_name': 'Natural gas combustion',
         'scope': 1, 'subcategory': 'stationary_combustion', 'default_unit': 'GJ', 'method_key': 'EPA_C1'},
        {'activity_code': 'S1_SC_DIESEL', 'activity_name': 'Diesel combustion',
         'scope': 1, 'subcategory': 'stationary_combustion', 'default_unit': 'GJ', 'method_key': 'IPCC_V2CH2'},
        {'activity_code': 'S2_ELECTRICITY', 'activity_name': 'Grid electricity',
         'scope': 2, 'subcategory': 'purchased_electricity', 'default_unit': 'kWh', 'method_key': 'LOCATION_BASED'},
        {'activity_code': 'S1_FLARE_NG', 'activity_name': 'Natural gas flaring',
         'scope': 1, 'subcategory': 'flaring', 'default_unit': 'Nm3', 'method_key': 'API_FLARE'},
        {'activity_code': 'S3_TRUCK_DIESEL', 'activity_name': 'Truck transportation',
         'scope': 3, 'subcategory': 'transport_downstream', 'default_unit': 'tonne-km', 'method_key': 'DEFRA_FREIGHT'},
    ]
    df_activity = pd.DataFrame(activity_data, columns=activity_columns)

    # Documentation sheet
    doc_data = {
        'Field': ef_columns,
        'Description': [
            'GHG Protocol scope (1, 2, or 3)',
            'Emission subcategory (e.g., stationary_combustion, flaring)',
            'Stable activity code (e.g., S1_SC_NG)',
            'Human-readable activity name',
            'Greenhouse gas (CO2, CH4, N2O, etc.)',
            'Emission factor numeric value',
            'Unit of emission factor (e.g., kg CO2/GJ)',
            'Energy basis: HHV, LHV, or NA',
            'Oxidation/combustion fraction (0-1)',
            'Fuel physical state: gas, liquid, solid, or NA',
            'Authoritative source: DEFRA, EPA, IPCC, API, IEA, Other',
            'Source document name',
            'Table/section reference within source document',
            'Publication year of source',
            'Geographic applicability (country or "Global")',
            'ISO country code (e.g., EG, US) or region code',
            'For electricity: location, market, or NA',
            'Technology/equipment type (optional)',
            'Uncertainty as percentage (optional)',
            'Valid from date (YYYY-MM-DD)',
            'Valid to date (YYYY-MM-DD) or blank if current',
            'Full citation or URL',
            'Method equation reference (e.g., EPA C-1)',
            'Additional notes'
        ],
        'Example': [
            '1', 'stationary_combustion', 'S1_SC_NG', 'Pipeline natural gas',
            'CO2', '56.1', 'kg CO2/GJ', 'HHV', '0.995', 'gas',
            'EPA', '40 CFR 98 Subpart C', 'Table C-1', '2025',
            'USA', 'US', 'NA', 'boiler', '3.0',
            '2025-01-01', '', 'https://...', 'EPA C-1', 'Example'
        ]
    }
    df_doc = pd.DataFrame(doc_data)

    # Write to Excel with multiple sheets
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        df_factors.to_excel(writer, sheet_name='emission_factors', index=False)
        df_gwp.to_excel(writer, sheet_name='gwp_sets', index=False)
        df_activity.to_excel(writer, sheet_name='activity_catalog', index=False)
        df_doc.to_excel(writer, sheet_name='documentation', index=False)

    print(f"✓ Emission Factor Master Template created at: {output_path}")
    return output_path


if __name__ == "__main__":
    create_ef_master_template()
