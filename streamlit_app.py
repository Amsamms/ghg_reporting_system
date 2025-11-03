"""
Main Streamlit application for GHG Inventory Management System.
Entry point for the auditor-grade GHG inventory web app.
"""

import streamlit as st
from pathlib import Path
import sys

# Add ghgcore to path
sys.path.insert(0, str(Path(__file__).parent))

from sqlmodel import select
from ghgcore.db import init_db, get_db
from ghgcore.models import Organization, Facility, Activity, EmissionFactor, Calculation


def main():
    """Main application entry point."""

    # Page config
    st.set_page_config(
        page_title="GHG Inventory Management System",
        page_icon="🌱",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Initialize database on first run
    if 'db_initialized' not in st.session_state:
        with st.spinner("Initializing database..."):
            init_db()
            st.session_state.db_initialized = True

    # Sidebar navigation
    st.sidebar.title("🌱 GHG Inventory System")
    st.sidebar.markdown("---")

    pages = {
        "🏠 Home": "Home",
        "🏢 Project Setup": "Project Setup",
        "📝 Inventory Builder": "Inventory Builder",
        "🔢 Factor Picker": "Factor Picker",
        "📊 Results & Charts": "Results and Charts",
        "✅ QA/QC": "QA/QC",
        "📄 Report Composer": "Report Composer",
        "📥 Exports": "Exports",
    }

    selection = st.sidebar.radio("Navigate", list(pages.keys()))

    # Display selected page
    page = pages[selection]

    if page == "Home":
        show_home()
    elif page == "Project Setup":
        show_project_setup()
    elif page == "Inventory Builder":
        show_inventory_builder()
    elif page == "Factor Picker":
        show_factor_picker()
    elif page == "Results and Charts":
        show_results()
    elif page == "QA/QC":
        show_qaqc()
    elif page == "Report Composer":
        show_report_composer()
    elif page == "Exports":
        show_exports()

    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
        **Standards Compliance:**
        - ISO 14064-1:2018 ✓
        - GHG Protocol Corporate Standard ✓

        **Version:** 1.0.0
    """)


def show_home():
    """Home page."""

    st.title("🌱 GHG Inventory Management System")
    st.markdown("""
    ### Welcome to the Auditor-Grade GHG Inventory Application

    This system provides comprehensive greenhouse gas accounting, analysis, and reporting for
    **petroleum companies and industrial organizations** in accordance with:

    - **ISO 14064-1:2018** - Specification with guidance for quantification and reporting of GHG emissions
    - **GHG Protocol Corporate Standard** - Global standard for corporate GHG inventories

    ---

    ### Key Features

    #### 📊 **Professional Reporting**
    - Interactive HTML reports with Sankey diagrams
    - Print-ready PDF reports with executive summaries
    - Comprehensive Excel exports with verification bundles

    #### 🔬 **Calculation Engine**
    - Unit-safe calculations with pint library
    - Supports petroleum units (bbl, scf, Nm3, toe)
    - Multiple calculation methods (Tier 1, 2, 3)
    - Emission factor provenance and snapshotting

    #### 🎯 **Emission Coverage**
    - **Scope 1:** Stationary/mobile combustion, flaring, fugitives, process emissions
    - **Scope 2:** Electricity (location & market-based), steam, heat, cooling
    - **Scope 3:** Transportation, business travel, employee commuting

    #### ✅ **Quality Assurance**
    - Automated QA/QC checks
    - Uncertainty quantification (RSS & Monte Carlo)
    - Completeness tracking
    - Outlier detection

    ---

    ### Getting Started

    1. **Project Setup** - Create organization and facilities
    2. **Inventory Builder** - Add emission activities
    3. **Factor Picker** - Select appropriate emission factors
    4. **Results & Charts** - View aggregated results
    5. **QA/QC** - Review data quality
    6. **Report Composer** - Customize report sections
    7. **Exports** - Generate HTML/PDF/Excel reports

    ---

    ### System Architecture

    This application uses:
    - **Backend:** SQLModel ORM with SQLite (production-ready for PostgreSQL)
    - **Calculation Engine:** Python with pint for unit handling
    - **Frontend:** Streamlit for interactive UI
    - **Reporting:** Jinja2 templates + WeasyPrint for PDF

    ---

    ### Support

    For questions or issues, please refer to the documentation or contact your administrator.
    """)

    # Quick stats if data exists
    from ghgcore.db import get_db
    from ghgcore.models import Organization, Activity
    from sqlmodel import select

    with get_db() as session:
        org_count = len(session.exec(select(Organization)).all())
        activity_count = len(session.exec(select(Activity)).all())

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Organizations", org_count)

    with col2:
        st.metric("Activities", activity_count)

    with col3:
        st.metric("Database", "Active", delta="SQLite")


def show_project_setup():
    """Project setup page."""
    st.title("🏢 Project Setup")
    st.markdown("Configure your organization and facilities for GHG inventory.")

    from ghgcore.db import get_db
    from ghgcore.models import Organization, Facility
    from ghgcore.schemas import OrganizationCreate, FacilityCreate
    from datetime import date

    with st.expander("➕ Create New Organization", expanded=True):
        with st.form("org_form"):
            name = st.text_input("Organization Name")
            country = st.text_input("Country")
            sector = st.selectbox("Sector", [
                "Petroleum Refining",
                "Upstream Oil & Gas",
                "Petrochemicals",
                "Pipelines & Terminals",
                "Other"
            ])

            col1, col2 = st.columns(2)
            with col1:
                base_year = st.number_input("Base Year", min_value=2000, max_value=2030, value=2020)
                period_start = st.date_input("Period Start", value=date(2024, 1, 1))

            with col2:
                gwp_set = st.selectbox("GWP Set", ["AR5", "AR6"])
                period_end = st.date_input("Period End", value=date(2024, 12, 31))

            electricity_method = st.selectbox("Electricity Method", ["location", "market", "both"])
            consolidation = st.selectbox("Consolidation Approach", [
                "operational_control",
                "financial_control",
                "equity_share"
            ])

            submitted = st.form_submit_button("Create Organization")

            if submitted and name:
                with get_db() as session:
                    org = Organization(
                        name=name,
                        country=country,
                        sector=sector,
                        base_year=base_year,
                        period_start=period_start,
                        period_end=period_end,
                        gwp_set=gwp_set,
                        electricity_method=electricity_method,
                        consolidation_approach=consolidation,
                    )
                    session.add(org)
                    session.commit()
                    st.success(f"✓ Organization '{name}' created successfully!")

    # List existing organizations
    st.markdown("### Existing Organizations")

    with get_db() as session:
        orgs = session.exec(select(Organization)).all()

    if orgs:
        for org in orgs:
            with st.expander(f"📁 {org.name}"):
                st.write(f"**Country:** {org.country}")
                st.write(f"**Sector:** {org.sector}")
                st.write(f"**Reporting Period:** {org.period_start} to {org.period_end}")
                st.write(f"**GWP Set:** {org.gwp_set}")

                # Add facilities for this org
                st.markdown("#### Add Facility")
                with st.form(f"facility_form_{org.id}"):
                    fac_name = st.text_input("Facility Name")
                    lat = st.number_input("Latitude", value=0.0)
                    lon = st.number_input("Longitude", value=0.0)
                    grid_region = st.text_input("Grid Region")

                    if st.form_submit_button("Add Facility"):
                        with get_db() as session:
                            facility = Facility(
                                org_id=org.id,
                                name=fac_name,
                                lat=lat if lat != 0.0 else None,
                                lon=lon if lon != 0.0 else None,
                                grid_region=grid_region if grid_region else None,
                            )
                            session.add(facility)
                            session.commit()
                            st.success(f"✓ Facility '{fac_name}' added!")
    else:
        st.info("No organizations yet. Create one to get started!")


def show_inventory_builder():
    """Inventory builder page."""
    st.title("📝 Inventory Builder")
    st.markdown("Add emission activities for your facilities.")

    with get_db() as session:
        # Get organizations
        orgs = session.exec(select(Organization)).all()

        if not orgs:
            st.warning("⚠️ No organizations found. Please create an organization in **Project Setup** first.")
            return

        # Select organization
        org_options = {f"{org.name} (ID: {org.id})": org.id for org in orgs}
        selected_org = st.selectbox("Select Organization", list(org_options.keys()))
        org_id = org_options[selected_org]

        # Get facilities for this org
        facilities = session.exec(select(Facility).where(Facility.organization_id == org_id)).all()

        if not facilities:
            st.warning(f"⚠️ No facilities found for this organization. Please add facilities in **Project Setup** first.")
            return

        # Select facility
        fac_options = {f"{fac.name} (ID: {fac.id})": fac.id for fac in facilities}
        selected_fac = st.selectbox("Select Facility", list(fac_options.keys()))
        facility_id = fac_options[selected_fac]

        st.markdown("---")
        st.markdown("### ➕ Add New Activity")

        # Activity form
        with st.form("activity_form", clear_on_submit=True):
            col1, col2 = st.columns(2)

            with col1:
                activity_type = st.selectbox("Activity Type", [
                    "stationary_combustion",
                    "mobile_combustion",
                    "purchased_electricity",
                    "flaring",
                    "fugitives",
                    "transport",
                    "other"
                ])
                scope = st.selectbox("Scope", [1, 2, 3])
                description = st.text_input("Description", placeholder="e.g., Natural gas boiler combustion")

            with col2:
                value = st.number_input("Activity Value", min_value=0.0, value=0.0, format="%.2f")
                unit = st.selectbox("Unit", [
                    "GJ", "MWh", "kWh", "kg", "tonne", "bbl", "scf", "Nm3", "toe", "liters", "gallons"
                ])
                period_start = st.date_input("Period Start")
                period_end = st.date_input("Period End")

            notes = st.text_area("Notes (optional)")

            submitted = st.form_submit_button("Add Activity")

            if submitted:
                # Create activity
                activity = Activity(
                    organization_id=org_id,
                    facility_id=facility_id,
                    scope=scope,
                    subcategory=activity_type,
                    description=description,
                    period_start=period_start,
                    period_end=period_end,
                    value=value,
                    unit=unit,
                    notes=notes
                )
                session.add(activity)
                session.commit()
                session.refresh(activity)
                st.success(f"✅ Activity #{activity.id} added successfully!")
                st.rerun()

        st.markdown("---")
        st.markdown("### 📋 Existing Activities")

        # List activities for this facility
        activities = session.exec(
            select(Activity)
            .where(Activity.facility_id == facility_id)
            .order_by(Activity.id.desc())
        ).all()

        if activities:
            for act in activities:
                with st.expander(f"🔖 Activity #{act.id}: {act.description} ({act.subcategory})"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.write(f"**Scope:** {act.scope}")
                        st.write(f"**Type:** {act.subcategory}")
                    with col2:
                        st.write(f"**Value:** {act.value} {act.unit}")
                        st.write(f"**Period:** {act.period_start} to {act.period_end}")
                    with col3:
                        if act.notes:
                            st.write(f"**Notes:** {act.notes}")

                    # Delete button
                    if st.button(f"🗑️ Delete Activity #{act.id}", key=f"delete_{act.id}"):
                        session.delete(act)
                        session.commit()
                        st.success(f"Activity #{act.id} deleted")
                        st.rerun()
        else:
            st.info("No activities added yet. Use the form above to add your first activity.")


def show_factor_picker():
    """Emission factor picker page."""
    st.title("🔢 Emission Factor Picker")
    st.markdown("Browse and manage emission factors from various authorities.")

    with get_db() as session:
        # Tabs for different functions
        tab1, tab2, tab3 = st.tabs(["📚 Browse Factors", "➕ Add Factor", "📥 Import Factors"])

        with tab1:
            st.markdown("### Browse Emission Factors")

            # Get all emission factors
            from ghgcore.models import EmissionFactor
            factors = session.exec(select(EmissionFactor)).all()

            if not factors:
                st.info("No emission factors in database. Add factors manually or import from file.")
                st.markdown("""
                **Tip:** You can add emission factors in the following ways:
                1. Use the **Add Factor** tab to add individual factors manually
                2. Use the **Import Factors** tab to bulk import from CSV/Excel
                3. Use the seed_factors.py script with DEFRA, EPA, IPCC, API, or IEA data
                """)
            else:
                # Filter options
                col1, col2, col3 = st.columns(3)
                with col1:
                    authorities = list(set([f.authority for f in factors if f.authority]))
                    selected_authority = st.selectbox("Filter by Authority", ["All"] + authorities)

                with col2:
                    scopes = list(set([f.scope for f in factors if f.scope]))
                    selected_scope = st.selectbox("Filter by Scope", ["All"] + [str(s) for s in sorted(scopes)])

                with col3:
                    search_term = st.text_input("🔍 Search description")

                # Apply filters
                filtered_factors = factors
                if selected_authority != "All":
                    filtered_factors = [f for f in filtered_factors if f.authority == selected_authority]
                if selected_scope != "All":
                    filtered_factors = [f for f in filtered_factors if str(f.scope) == selected_scope]
                if search_term:
                    filtered_factors = [f for f in filtered_factors if search_term.lower() in (f.description or "").lower()]

                st.markdown(f"**Found {len(filtered_factors)} factors**")

                # Display factors
                for factor in filtered_factors[:50]:  # Limit to 50 for performance
                    with st.expander(f"🔖 {factor.description[:80] if factor.description else 'No description'} | {factor.authority or 'Unknown'} | Scope {factor.scope}"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Factor Value:** {factor.factor_value}")
                            st.write(f"**Unit:** {factor.factor_unit}")
                            st.write(f"**Scope:** {factor.scope}")
                            st.write(f"**Subcategory:** {factor.subcategory}")
                        with col2:
                            st.write(f"**Authority:** {factor.authority or 'N/A'}")
                            st.write(f"**Year:** {factor.year or 'N/A'}")
                            st.write(f"**Region:** {factor.region or 'Global'}")
                            st.write(f"**Source:** {factor.source_reference or 'N/A'}")

                        if factor.notes:
                            st.write(f"**Notes:** {factor.notes}")

                if len(filtered_factors) > 50:
                    st.info(f"Showing first 50 of {len(filtered_factors)} factors. Use filters to narrow results.")

        with tab2:
            st.markdown("### ➕ Add Emission Factor Manually")

            with st.form("add_factor_form", clear_on_submit=True):
                col1, col2 = st.columns(2)

                with col1:
                    description = st.text_input("Description*", placeholder="e.g., Natural gas combustion")
                    factor_value = st.number_input("Factor Value*", min_value=0.0, format="%.6f")
                    factor_unit = st.text_input("Factor Unit*", value="kg CO2e/GJ", placeholder="e.g., kg CO2e/GJ")
                    scope = st.selectbox("Scope*", [1, 2, 3])
                    subcategory = st.text_input("Subcategory*", placeholder="e.g., stationary_combustion")

                with col2:
                    authority = st.text_input("Authority", placeholder="e.g., EPA, DEFRA, IPCC")
                    year = st.number_input("Year", min_value=1990, max_value=2030, value=2023, step=1)
                    region = st.text_input("Region", value="Global")
                    source_reference = st.text_input("Source Reference", placeholder="URL or document reference")

                notes = st.text_area("Notes (optional)")

                submitted = st.form_submit_button("Add Emission Factor")

                if submitted:
                    if not description or not factor_value or not factor_unit or not subcategory:
                        st.error("Please fill in all required fields (marked with *)")
                    else:
                        from ghgcore.models import EmissionFactor
                        ef = EmissionFactor(
                            description=description,
                            factor_value=factor_value,
                            factor_unit=factor_unit,
                            scope=scope,
                            subcategory=subcategory,
                            authority=authority if authority else None,
                            year=year,
                            region=region if region else "Global",
                            source_reference=source_reference if source_reference else None,
                            notes=notes if notes else None
                        )
                        session.add(ef)
                        session.commit()
                        st.success(f"✅ Emission factor added successfully! (ID: {ef.id})")
                        st.rerun()

        with tab3:
            st.markdown("### 📥 Import Emission Factors from File")
            st.info("""
            **Import CSV/Excel file with emission factors**

            Required columns:
            - `description`: Factor description
            - `factor_value`: Numeric emission factor value
            - `factor_unit`: Unit (e.g., kg CO2e/GJ)
            - `scope`: Emission scope (1, 2, or 3)
            - `subcategory`: Activity subcategory

            Optional columns:
            - `authority`: Source authority (EPA, DEFRA, IPCC, etc.)
            - `year`: Publication year
            - `region`: Geographic region
            - `source_reference`: URL or reference
            - `notes`: Additional notes
            """)

            uploaded_file = st.file_uploader("Upload CSV or Excel file", type=['csv', 'xlsx'])

            if uploaded_file:
                import pandas as pd
                from ghgcore.models import EmissionFactor

                try:
                    # Read file
                    if uploaded_file.name.endswith('.csv'):
                        df = pd.read_csv(uploaded_file)
                    else:
                        df = pd.read_excel(uploaded_file)

                    st.write(f"**Preview:** {len(df)} rows")
                    st.dataframe(df.head(10))

                    # Validate required columns
                    required_cols = ['description', 'factor_value', 'factor_unit', 'scope', 'subcategory']
                    missing_cols = [col for col in required_cols if col not in df.columns]

                    if missing_cols:
                        st.error(f"Missing required columns: {', '.join(missing_cols)}")
                    else:
                        if st.button("Import All Factors"):
                            imported = 0
                            errors = []

                            for idx, row in df.iterrows():
                                try:
                                    ef = EmissionFactor(
                                        description=str(row['description']),
                                        factor_value=float(row['factor_value']),
                                        factor_unit=str(row['factor_unit']),
                                        scope=int(row['scope']),
                                        subcategory=str(row['subcategory']),
                                        authority=str(row.get('authority')) if pd.notna(row.get('authority')) else None,
                                        year=int(row.get('year')) if pd.notna(row.get('year')) else None,
                                        region=str(row.get('region', 'Global')) if pd.notna(row.get('region')) else 'Global',
                                        source_reference=str(row.get('source_reference')) if pd.notna(row.get('source_reference')) else None,
                                        notes=str(row.get('notes')) if pd.notna(row.get('notes')) else None
                                    )
                                    session.add(ef)
                                    imported += 1
                                except Exception as e:
                                    errors.append(f"Row {idx + 1}: {str(e)}")

                            session.commit()

                            if errors:
                                st.warning(f"Imported {imported} factors with {len(errors)} errors")
                                with st.expander("View Errors"):
                                    for error in errors:
                                        st.write(error)
                            else:
                                st.success(f"✅ Successfully imported {imported} emission factors!")
                            st.rerun()

                except Exception as e:
                    st.error(f"Error reading file: {str(e)}")


def show_results():
    """Results and charts page."""
    st.title("📊 Results & Charts")
    st.info("Results visualization - to be implemented")


def show_qaqc():
    """QA/QC page."""
    st.title("✅ QA/QC Checks")
    st.info("Quality assurance interface - to be implemented")


def show_report_composer():
    """Report composer page."""
    st.title("📄 Report Composer")
    st.info("Report customization interface - to be implemented")


def show_exports():
    """Exports page."""
    st.title("📥 Export Reports")

    from ghgcore.db import get_db
    from ghgcore.models import Organization
    from ghgcore.reporting.compose import compose_report_context
    from ghgcore.reporting.export_html import export_html_report
    from ghgcore.reporting.export_excel import export_excel_inventory
    from sqlmodel import select
    from pathlib import Path
    import os

    # Get organizations
    with get_db() as session:
        orgs = session.exec(select(Organization)).all()

    if not orgs:
        st.warning("No organizations found. Create an organization first in Project Setup.")
        return

    st.markdown("### Generate ISO 14064-1 Compliant Reports")

    # Select organization
    org_options = {org.name: org.id for org in orgs}
    selected_org_name = st.selectbox("Select Organization", list(org_options.keys()))
    org_id = org_options[selected_org_name]

    # AI Recommendations toggle
    st.markdown("---")
    st.markdown("### 🤖 AI-Powered Recommendations")

    ai_enabled = st.checkbox(
        "Enable AI Recommendations (GPT-5)",
        help="Uses OpenAI GPT-5-mini to generate strategic emission reduction recommendations. Requires OPENAI_API_KEY environment variable."
    )

    if ai_enabled:
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            st.error("⚠️ OPENAI_API_KEY environment variable not set. AI recommendations will fallback to rule-based.")
            st.code("export OPENAI_API_KEY='your-api-key-here'", language="bash")
        else:
            st.success("✓ API key detected. AI recommendations will be used.")

    # Report options
    st.markdown("---")
    st.markdown("### Report Options")

    col1, col2 = st.columns(2)

    with col1:
        include_charts = st.checkbox("Include Charts", value=True)

    with col2:
        include_evidence = st.checkbox("Include Evidence Manifest", value=True)

    # Generate report button
    st.markdown("---")

    if st.button("🚀 Generate Reports", type="primary", use_container_width=True):
        with st.spinner("Generating comprehensive GHG inventory report..."):
            try:
                with get_db() as session:
                    # Compose report context
                    context = compose_report_context(
                        session,
                        org_id=org_id,
                        use_ai_recommendations=ai_enabled
                    )

                    # Create export directory
                    export_dir = Path("exports") / selected_org_name.replace(" ", "_")
                    export_dir.mkdir(parents=True, exist_ok=True)

                    # Generate HTML report
                    html_path = export_dir / "ghg_inventory_report.html"
                    export_html_report(context, html_path)

                    # Generate Excel report
                    excel_path = export_dir / "ghg_inventory_detailed.xlsx"
                    export_excel_inventory(context, excel_path)

                st.success(f"✓ Reports generated successfully!")

                # Show download links
                st.markdown("### 📥 Download Reports")

                col1, col2 = st.columns(2)

                with col1:
                    if html_path.exists():
                        with open(html_path, 'rb') as f:
                            st.download_button(
                                label="📄 Download HTML Report",
                                data=f,
                                file_name="ghg_inventory_report.html",
                                mime="text/html",
                                use_container_width=True
                            )

                with col2:
                    if excel_path.exists():
                        with open(excel_path, 'rb') as f:
                            st.download_button(
                                label="📊 Download Excel Report",
                                data=f,
                                file_name="ghg_inventory_detailed.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                use_container_width=True
                            )

                # Show AI recommendations if enabled
                if ai_enabled and context.get('recommendations'):
                    st.markdown("---")
                    st.markdown("### 💡 AI-Generated Strategic Recommendations")

                    if context.get('ai_powered'):
                        st.success("🤖 Powered by GPT-5-mini")
                    else:
                        st.info("ℹ️ Using rule-based recommendations (AI unavailable)")

                    for rec in context['recommendations']:
                        priority = rec.get('priority', 'Medium')
                        category = rec.get('category', '')
                        recommendation = rec.get('recommendation', '')
                        impact = rec.get('potential_impact', '')

                        # Color code by priority
                        if priority == 'High':
                            priority_color = "🔴"
                        elif priority == 'Medium':
                            priority_color = "🟡"
                        else:
                            priority_color = "🟢"

                        with st.expander(f"{priority_color} **{priority} Priority**: {category}"):
                            st.markdown(f"**Recommendation:**\n{recommendation}")
                            st.markdown(f"**Potential Impact:**\n{impact}")

            except Exception as e:
                st.error(f"Error generating reports: {e}")
                import traceback
                st.code(traceback.format_exc())


if __name__ == "__main__":
    main()
