# 🌱 GHG Inventory Management System

> **Auditor-Grade GHG Inventory Application for Petroleum Companies**

A comprehensive greenhouse gas accounting, analysis, and reporting system compliant with **ISO 14064-1:2018** and **GHG Protocol Corporate Standard**, specifically designed for Egyptian petroleum companies (refineries, terminals, pipelines, upstream operations).

---

## 🎯 Features

### Core Capabilities

- **Modular Calculation Engine** with unit-safe math and factor provenance
- **Streamlit UI** for interactive inventory management
- **Normalized Database Schema** (SQLite MVP, ORM-ready for PostgreSQL)
- **Canonical Emission Factor Format** with loaders for DEFRA/EPA/IPCC/API/IEA
- **Full Provenance & Snapshotting** for auditor verification
- **ISO 14064-1 Structured Reports** (HTML & PDF) with verification bundles

### Calculation Methods

#### Scope 1 (Direct Emissions)
- **Stationary Combustion:** Tier 1-2 methods with HHV/LHV basis
- **Mobile Combustion:** Fleet vehicles, equipment
- **Flaring:** API Compendium methodology with destruction efficiency
- **Fugitive Emissions:** Equipment leaks, tank losses, pipeline blowdowns
- **Process Emissions:** CO₂ from chemical reactions

#### Scope 2 (Energy Indirect)
- **Electricity:** Location-based & Market-based (dual reporting)
- **Purchased Steam/Heat/Cooling:** Energy-based factors

#### Scope 3 (Value Chain)
- **Transportation:** Freight (tonne-km), business travel, commuting
- **Air Travel:** With radiative forcing index (RFI)

### Quality Assurance

- Missing data detection
- Negative value checks
- Statistical outlier detection
- HHV/LHV basis consistency validation
- Emission factor currency checks
- Completeness scoring by scope

### Uncertainty Quantification

- Root-sum-of-squares (RSS) propagation
- Monte Carlo simulation (10,000 iterations)
- IPCC tier-based uncertainty assignment
- Confidence interval calculation (95%)

---

## 🚀 Quick Start

### Installation

```bash
# Clone repository
cd ghg_reporting_system/ghg_app

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python -m ghgcore.db
```

### Launch Application

```bash
# Run Streamlit app
streamlit run app.py
```

Open browser to `http://localhost:8501`

---

## 📁 Project Structure

```
ghg_app/
├── app.py                          # Main Streamlit application
├── requirements.txt                 # Python dependencies
├── README.md                       # This file
│
├── ghgcore/                        # Core calculation engine
│   ├── __init__.py
│   ├── models.py                   # SQLModel ORM (all tables)
│   ├── schemas.py                  # Pydantic validation
│   ├── db.py                       # Database session management
│   ├── units.py                    # Pint unit registry & converters
│   │
│   ├── factors/                    # Emission factor management
│   │   ├── loader_base.py          # Base loader class
│   │   ├── loader_defra.py         # UK DEFRA loader
│   │   ├── loader_epa.py           # US EPA 40 CFR 98
│   │   ├── loader_ipcc.py          # IPCC 2006/2019 Guidelines
│   │   ├── loader_api.py           # API Compendium (petroleum)
│   │   ├── loader_iea.py           # IEA grid factors
│   │   ├── normalize.py            # Canonical format mapper
│   │   ├── seed_factors.py         # CLI to populate database
│   │   ├── create_ef_template.py   # Generate Excel template
│   │   └── templates/
│   │       └── EF_Master_Template.xlsx
│   │
│   ├── engine/                     # Calculation methods
│   │   ├── combustion.py           # Stationary & mobile combustion
│   │   ├── electricity.py          # Scope 2 electricity (dual reporting)
│   │   ├── flaring.py              # Flare & thermal oxidizer
│   │   ├── fugitives.py            # Equipment leaks, tanks
│   │   ├── transport.py            # Scope 3 transportation
│   │   ├── aggregation.py          # Rollup by scope/facility/month
│   │   ├── uncertainty.py          # RSS & Monte Carlo
│   │   └── checks.py               # QA/QC validation rules
│   │
│   └── reporting/                  # Report generation
│       ├── compose.py              # Build report context
│       ├── export_html.py          # HTML export with Plotly
│       ├── export_pdf.py           # PDF via WeasyPrint/ReportLab
│       ├── export_excel.py         # Excel verification bundle
│       └── templates/
│           ├── base.html           # Jinja2 base template
│           └── sections/           # ISO 14064-1 section templates
│               ├── 01_title.html
│               ├── 02_summary.html
│               ├── 03_intro.html
│               ├── 04_boundaries.html
│               ├── 05_base_year_period.html
│               ├── 06_sources_sinks.html
│               ├── 07_methods.html
│               ├── 08_data_management.html
│               ├── 09_results.html
│               ├── 10_uncertainty.html
│               ├── 11_improvement.html
│               └── 12_appendices.html
│
├── ui/                             # Streamlit pages (multipage app)
│   └── pages/
│       ├── 01_Project_Setup.py
│       ├── 02_Inventory_Builder.py
│       ├── 03_Factor_Picker.py
│       ├── 04_Results_and_Charts.py
│       ├── 05_QA_QC.py
│       ├── 06_Report_Composer.py
│       └── 07_Exports.py
│
├── tests/                          # Test suite
│   ├── test_units.py
│   ├── test_combustion.py
│   ├── test_electricity.py
│   ├── test_factor_snapshot.py
│   └── test_aggregation.py
│
├── exports/                        # Generated reports (runtime)
└── uploads/                        # Evidence files (runtime)
```

---

## 🗄️ Database Schema

### Core Tables

- **Organization:** Company info, GWP set, reporting period
- **Facility:** Sites with geolocation
- **Source:** Emission source categories (Scope 1/2/3)
- **Activity:** Individual emission activities
- **EmissionFactor:** Canonical factors with full provenance
- **GWP:** IPCC AR5/AR6 global warming potentials
- **Calculation:** Immutable calculation records with snapshots
- **Attachment:** Evidence files (invoices, meter readings)
- **ReportSection:** User-editable ISO clause text
- **AuditTrail:** Change log for all entities

### Key Principle: Factor Immutability

When an emission factor is selected, the **entire factor row** is frozen into `Calculation.factor_snapshot_json`. This ensures:
- Historical calculations never change when factor libraries are updated
- Full audit trail for verifiers
- Reproducible results

---

## 📊 Emission Factor Template

Run to generate the canonical Excel template:

```bash
python -m ghgcore.factors.create_ef_template
```

Columns:
- `scope`, `subcategory`, `activity_code`, `activity_name`
- `gas`, `factor_value`, `factor_unit`
- `basis` (HHV/LHV), `oxidation_frac`, `fuel_state`
- `source_authority`, `source_doc`, `source_table`, `source_year`
- `geography`, `region_code`, `market_or_location`
- `technology`, `uncertainty_pct`, `valid_from`, `valid_to`
- `citation`, `method_equation_ref`, `notes`

### Seeding Factors

```bash
# From canonical Excel template
python -m ghgcore.factors.seed_factors --from-excel path/to/EF_Master.xlsx --init-db

# Auto-detect authority from filename
python -m ghgcore.factors.seed_factors --from-excel DEFRA_2024_factors.xlsx

# Specify authority explicitly
python -m ghgcore.factors.seed_factors --from-excel factors.xlsx --authority EPA
```

---

## 🧪 Testing

```bash
# Run all tests
pytest

# With coverage
pytest --cov=ghgcore --cov-report=html

# Specific test module
pytest tests/test_combustion.py -v
```

### Test Coverage

- Unit conversions (bbl, scf, Nm3, toe, tCO₂e)
- Combustion calculations (Tier 1-2)
- Factor snapshot immutability
- Electricity dual reporting
- Aggregation accuracy
- Uncertainty propagation

---

## 📖 Usage Workflow

### 1. Project Setup

```python
# Create organization via UI or programmatically
from ghgcore.db import get_db
from ghgcore.models import Organization
from datetime import date

with get_db() as session:
    org = Organization(
        name="ABC Petroleum",
        country="Egypt",
        sector="Petroleum Refining",
        base_year=2020,
        period_start=date(2024, 1, 1),
        period_end=date(2024, 12, 31),
        gwp_set="AR5",
    )
    session.add(org)
    session.commit()
```

### 2. Seed Emission Factors

```bash
python -m ghgcore.factors.seed_factors --from-excel EF_Master_Template.xlsx --init-db
```

### 3. Add Activities

Use Streamlit UI or API to add activities with activity data.

### 4. Calculate Emissions

```python
from ghgcore.engine.combustion import calculate_combustion_emissions

result = calculate_combustion_emissions(
    energy_input=1000,
    energy_unit="GJ",
    ef_co2=56.1,
    ef_co2_unit="kg CO2/GJ",
    oxidation_frac=0.995,
    gwp_ch4=28,
)

print(result['total_co2e_kg'])  # Total CO2e emissions
```

### 5. Generate Report

```python
from ghgcore.reporting.compose import compose_report_context
from ghgcore.reporting.export_html import export_html_report
from ghgcore.reporting.export_pdf import export_pdf_report
from pathlib import Path

# Compose context
context = compose_report_context(session, org_id=1, year=2024)

# Export HTML
export_html_report(context, Path("exports/report.html"))

# Export PDF
export_pdf_report(context, Path("exports/report.pdf"))
```

---

## 🔧 Configuration

### Database

Default: SQLite (`ghg_inventory.db`)

For production PostgreSQL:

```python
# In ghgcore/db.py, change:
DATABASE_URL = "postgresql://user:pass@localhost/ghg_inventory"
```

### Units

Add custom petroleum units in `ghgcore/units.py`:

```python
ureg.define('custom_unit = X * base_unit')
```

---

## 📋 Standards Compliance

### ISO 14064-1:2018 Requirements

✅ Organization boundaries (operational control/equity share)
✅ Quantification methods by scope
✅ Base year & reporting period
✅ GHG sources and sinks identification
✅ Quantification approach documentation
✅ Data quality management
✅ GHG inventory report structure

### GHG Protocol Corporate Standard

✅ Scope 1, 2, 3 accounting
✅ Consolidation approaches
✅ Dual reporting for Scope 2 (location + market-based)
✅ Emission factor transparency
✅ Recalculation policy support

---

## 🛡️ Data Quality

The system implements multiple QA/QC layers:

1. **Input Validation:** Pydantic schemas ensure type safety
2. **Unit Safety:** Pint prevents dimensional errors
3. **Automated Checks:** Missing data, negatives, outliers
4. **Factor Currency:** Warns on expired/old factors
5. **Completeness:** Tracks coverage across scopes
6. **Uncertainty:** Quantifies data quality impact

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License.

---

## 🙏 Acknowledgments

- **GHG Protocol** for corporate accounting standards
- **ISO 14064-1** for specification guidance
- **API** for petroleum industry methodologies
- **IPCC** for emission factor guidance
- **DEFRA/EPA/IEA** for regional factors

---

## 📧 Support

For questions or support, please open an issue in the repository.

---

**🌱 Building a sustainable future through better emissions reporting! 🌍**
