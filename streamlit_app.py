import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import io
import base64
from datetime import datetime, date
import tempfile
import os
import sys

# Add src directory to path
current_dir = os.path.dirname(__file__)
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

from report_generator import GHGReportGenerator
from html_report import HTMLReportGenerator
from simple_pdf_report import SimplePDFReportGenerator
from excel_generator import GHGExcelGenerator

# Configure Streamlit page
st.set_page_config(
    page_title="🌱 GHG Reporting System",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #2E86C1, #1B4F72);
        color: white;
        padding: 2rem;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 2rem;
    }

    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #2E86C1;
    }

    .success-box {
        background: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid #c3e6cb;
        margin: 1rem 0;
    }

    .warning-box {
        background: #fff3cd;
        color: #856404;
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid #ffeaa7;
        margin: 1rem 0;
    }

    .info-box {
        background: #cce7ff;
        color: #0066cc;
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid #99d6ff;
        margin: 1rem 0;
    }

    .stButton > button {
        width: 100%;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# Authentication Functions
# ============================================

def check_credentials(username, password):
    """Check if username and password match those stored in Streamlit secrets

    To configure credentials in Streamlit Cloud:
    1. Go to App Settings → Secrets
    2. Add the following:
       [auth]
       username = "your_username"
       password = "your_password"
    """
    try:
        return (username == st.secrets["auth"]["username"] and
                password == st.secrets["auth"]["password"])
    except Exception as e:
        st.error(f"Error reading authentication secrets. Please configure secrets in Streamlit Cloud.")
        st.error(f"Error details: {str(e)}")
        return False

def show_login_page():
    """Display login page with username and password fields"""
    # Center the login form
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 2rem;">
            <h1>🔒 Login Required</h1>
            <p style="color: #666;">Please enter your credentials to access the GHG Reporting System</p>
        </div>
        """, unsafe_allow_html=True)

        # Login form
        with st.form("login_form"):
            username = st.text_input("👤 Username", placeholder="Enter your username")
            password = st.text_input("🔑 Password", type="password", placeholder="Enter your password")
            submit_button = st.form_submit_button("🚀 Login", use_container_width=True)

            if submit_button:
                if username and password:
                    if check_credentials(username, password):
                        st.session_state.authenticated = True
                        st.session_state.username = username
                        st.success("✅ Login successful! Redirecting...")
                        st.rerun()
                    else:
                        st.error("❌ Invalid username or password. Please try again.")
                else:
                    st.warning("⚠️ Please enter both username and password.")

        st.markdown("""
        <div style="text-align: center; padding: 1rem; color: #888; font-size: 0.9rem;">
            <p>🌱 EPROM Professional GHG Reporting System</p>
            <p>Secure access for authorized users only</p>
        </div>
        """, unsafe_allow_html=True)

def main():
    # Initialize authentication state
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False

    # Check if user is authenticated
    if not st.session_state.authenticated:
        show_login_page()
        return

    # ============================================
    # Main Application (After Authentication)
    # ============================================

    # App Header with Logo
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    logo_path = os.path.join(script_dir, "assets", "epromlogo-scaled.gif")

    # Display logo
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if os.path.exists(logo_path):
            st.image(logo_path, use_container_width=True)

    st.markdown("""
    <div class="main-header">
        <h1>EPROM 🌱 Professional GHG Reporting System</h1>
        <p>Comprehensive Greenhouse Gas Emissions Analysis for Petroleum Companies</p>
        <small>Following GHG Protocol Corporate Standard & ISO 14064 Guidelines</small>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar Navigation
    st.sidebar.title("📋 Navigation")

    # Add logout button at the top of sidebar
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.username = None
        st.rerun()

    # Display logged in user
    if 'username' in st.session_state and st.session_state.username:
        st.sidebar.markdown(f"**👤 Logged in as:** {st.session_state.username}")

    st.sidebar.markdown("---")
    page = st.sidebar.selectbox(
        "Select a page:",
        ["🏠 Home", "📤 Upload Excel", "✍️ Manual Input", "📊 Generate Reports", "📋 Template Download", "ℹ️ Help & Info"]
    )

    # Initialize session state
    if 'ghg_data' not in st.session_state:
        st.session_state.ghg_data = None
    if 'company_info' not in st.session_state:
        st.session_state.company_info = {}
    if 'selected_facility' not in st.session_state:
        st.session_state.selected_facility = 'All Facilities'

    # Page routing
    if page == "🏠 Home":
        show_home_page()
    elif page == "📤 Upload Excel":
        show_upload_page()
    elif page == "✍️ Manual Input":
        show_manual_input_page()
    elif page == "📊 Generate Reports":
        show_reports_page()
    elif page == "📋 Template Download":
        show_template_page()
    elif page == "ℹ️ Help & Info":
        show_help_page()

def show_home_page():
    """Home page with system overview"""

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>🎯 Key Features</h3>
            <ul>
                <li>Complete Scope 1, 2 & 3 tracking</li>
                <li>Professional visualizations</li>
                <li>Interactive HTML reports</li>
                <li>PDF reports with recommendations</li>
                <li>Excel template support</li>
                <li>Manual data entry</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>📊 Chart Types</h3>
            <ul>
                <li>Sankey flow diagrams</li>
                <li>Scope comparison charts</li>
                <li>Monthly trend analysis</li>
                <li>Facility breakdowns</li>
                <li>Energy consumption analysis</li>
                <li>Performance dashboards</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3>🏭 Industry Standards</h3>
            <ul>
                <li>GHG Protocol compliance</li>
                <li>ISO 14064 guidelines</li>
                <li>Petroleum industry focus</li>
                <li>Regulatory reporting ready</li>
                <li>Stakeholder presentations</li>
                <li>Professional quality</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Quick Start Guide
    st.subheader("🚀 Quick Start Guide")

    tab1, tab2 = st.tabs(["📤 Upload Method", "✍️ Manual Input Method"])

    with tab1:
        st.markdown("""
        <div class="info-box">
            <h4>Using Excel Template (Recommended)</h4>
            <ol>
                <li>Download the Excel template from the "📋 Template Download" page</li>
                <li>Fill in your GHG emissions data</li>
                <li>Upload the completed template in "📤 Upload Excel" page</li>
                <li>Generate professional reports in "📊 Generate Reports" page</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)

    with tab2:
        st.markdown("""
        <div class="info-box">
            <h4>Manual Data Entry</h4>
            <ol>
                <li>Go to "✍️ Manual Input" page</li>
                <li>Enter your company information</li>
                <li>Add emission sources for each scope</li>
                <li>Generate reports with your custom data</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)

    # Sample data demo
    st.subheader("🎯 Try with Sample Data")
    if st.button("🧪 Load Sample GHG Data"):
        load_sample_data()
        st.markdown("""
        <div class="success-box">
            ✅ Sample data loaded successfully! Go to "📊 Generate Reports" to see the results.
        </div>
        """, unsafe_allow_html=True)

def show_upload_page():
    """Page for uploading Excel files"""
    st.header("📤 Upload Excel Template")

    st.markdown("""
    <div class="info-box">
        <h4>📋 Upload Instructions</h4>
        <p>Upload an Excel file with your GHG emissions data. The file should contain the following sheets:</p>
        <ul>
            <li><strong>Dashboard:</strong> Company information and summary</li>
            <li><strong>Scope 1 Emissions:</strong> Direct emission sources</li>
            <li><strong>Scope 2 Emissions:</strong> Energy-related emissions</li>
            <li><strong>Scope 3 Emissions:</strong> Value chain emissions</li>
            <li><strong>Emission By Source:</strong> Energy-related emission sources</li>
            <li><strong>Facility Breakdown:</strong> Site-specific data</li>
            <li><strong>Targets & Performance:</strong> Goal tracking</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Choose an Excel file",
        type=['xlsx', 'xls'],
        help="Upload your GHG emissions data in Excel format"
    )

    if uploaded_file is not None:
        try:
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_path = tmp_file.name

            # Load data using report generator
            report_gen = GHGReportGenerator(tmp_path)

            if report_gen.data:
                st.session_state.ghg_data = report_gen

                st.markdown("""
                <div class="success-box">
                    ✅ Excel file uploaded and validated successfully!
                </div>
                """, unsafe_allow_html=True)

                # Show data preview
                st.subheader("📊 Data Preview")

                col1, col2 = st.columns(2)

                with col1:
                    st.write("**File Structure:**")
                    for sheet_name, df in report_gen.data.items():
                        st.write(f"• {sheet_name}: {len(df)} rows, {len(df.columns)} columns")

                with col2:
                    # Show summary statistics (no facility filter for upload preview)
                    summary = report_gen.get_summary_statistics(facility_filter=None)
                    st.write("**Summary Statistics:**")
                    st.write(f"• Total Emissions: {summary.get('total_emissions', 0):,.0f} tCO2e")
                    st.write(f"• Scope 1: {summary.get('scope1_total', 0):,.0f} tCO2e")
                    st.write(f"• Scope 2: {summary.get('scope2_total', 0):,.0f} tCO2e")
                    st.write(f"• Scope 3: {summary.get('scope3_total', 0):,.0f} tCO2e")

                # Show data tables
                st.subheader("📋 Data Tables")
                selected_sheet = st.selectbox(
                    "Select sheet to preview:",
                    list(report_gen.data.keys())
                )

                if selected_sheet in report_gen.data:
                    df = report_gen.data[selected_sheet]
                    st.dataframe(df.head(10), use_container_width=True)
                    st.write(f"Showing first 10 rows of {len(df)} total rows")

            else:
                st.error("❌ Failed to load Excel file. Please check the file format and try again.")

            # Clean up temporary file
            os.unlink(tmp_path)

        except Exception as e:
            st.error(f"❌ Error processing Excel file: {str(e)}")

def show_manual_input_page():
    """Page for manual data input"""
    st.header("✍️ Manual Data Input")

    # Company Information Section
    st.subheader("🏢 Company Information")
    col1, col2 = st.columns(2)

    with col1:
        company_name = st.text_input("Company Name", value="Your Company Name")
        reporting_year = st.number_input("Reporting Year", value=2025, min_value=2020, max_value=2030)

    with col2:
        report_date = st.date_input("Report Date", value=date.today())
        num_facilities = st.number_input("Number of Facilities", value=2, min_value=1, max_value=10)

    st.markdown("---")

    # Custom Report Text Section
    st.subheader("📝 Custom Report Text (Optional)")
    st.info("Add custom text to personalize your HTML report. Leave empty to skip these sections.")

    company_introduction = st.text_area(
        "Company Introduction (appears at the beginning of the report)",
        value="",
        height=150,
        placeholder="Example: Company A is specialized in refining operations. It has been established since 1995 and operates multiple facilities across the region...",
        help="This text will appear in the Executive Overview section of the HTML report"
    )

    conclusion_title = st.text_input(
        "Conclusion Section Title",
        value="Conclusion & Final Notes",
        placeholder="Example: Final Remarks, Summary & Outlook, etc.",
        help="Customize the heading for the conclusion section of the HTML report"
    )

    conclusion_text = st.text_area(
        "Conclusion Section Content (appears at the end of the report)",
        value="",
        height=150,
        placeholder="Example: The company is committed to reducing emissions by 30% by 2030. Further investments in renewable energy and carbon capture technologies are planned...",
        help="This text will appear at the end of the HTML report, before the footer"
    )

    # Store company info
    st.session_state.company_info = {
        'name': company_name,
        'reporting_year': reporting_year,
        'report_date': report_date.strftime('%Y-%m-%d'),
        'num_facilities': num_facilities,
        'company_introduction': company_introduction.strip(),
        'conclusion_title': conclusion_title.strip() if conclusion_title.strip() else 'Conclusion & Final Notes',
        'conclusion_text': conclusion_text.strip()
    }

    st.markdown("---")

    # Initialize facilities data in session state
    if 'facilities_data' not in st.session_state:
        st.session_state.facilities_data = []

    # Facility Input Section
    st.subheader("🏭 Facility Emissions Data")
    st.info("📝 Enter emissions data for each facility. The system will automatically aggregate all facilities.")

    # Create tabs for each facility
    if num_facilities > 0:
        facility_tabs = st.tabs([f"Facility {i+1}" for i in range(int(num_facilities))])

        for idx, tab in enumerate(facility_tabs):
            with tab:
                add_facility_emissions(idx)

    st.markdown("---")

    # Emission By Source Input Section
    st.subheader("💨 Emission By Source Data")
    st.info("📝 Enter emissions data for energy-related sources (separate from Scope 1,2,3 data above).")

    # Initialize emission_by_source data in session state
    if 'emission_by_source_data' not in st.session_state:
        st.session_state.emission_by_source_data = []

    # Predefined emission sources
    emission_sources = ['Natural Gas', 'Electricity', 'Steam', 'Fuel Oil', 'Diesel', 'Gasoline']

    st.write("**Select emission sources to include:**")
    selected_emission_sources = st.multiselect(
        "Emission Sources",
        emission_sources,
        key="emission_sources_select"
    )

    # Custom emission sources
    if 'custom_emission_sources' not in st.session_state:
        st.session_state.custom_emission_sources = []

    st.markdown("---")
    st.write("**➕ Add Custom Emission Source:**")

    col1, col2 = st.columns([3, 1])
    with col1:
        new_emission_source = st.text_input(
            "Custom emission source name",
            key="new_emission_source_input",
            placeholder="e.g., Propane, Biomass, etc."
        )
    with col2:
        if st.button("Add Source", key="add_emission_source_button"):
            if new_emission_source:
                all_emission_sources = emission_sources + selected_emission_sources + st.session_state.custom_emission_sources
                if new_emission_source in all_emission_sources:
                    st.error(f"❌ Error: '{new_emission_source}' already exists.")
                else:
                    st.session_state.custom_emission_sources.append(new_emission_source)
                    st.success(f"✅ Added custom source: '{new_emission_source}'")
                    st.rerun()

    # Display custom sources with delete option
    if st.session_state.custom_emission_sources:
        st.write("**Custom Emission Sources:**")
        for idx, source in enumerate(st.session_state.custom_emission_sources):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.text(f"• {source}")
            with col2:
                if st.button("🗑️ Delete", key=f"delete_emission_source_{idx}"):
                    st.session_state.custom_emission_sources.pop(idx)
                    st.rerun()

    # Combine all selected sources
    all_selected_emission_sources = selected_emission_sources + st.session_state.custom_emission_sources

    # Input data for selected sources
    if all_selected_emission_sources:
        st.markdown("---")
        st.write("**Enter emissions data (tCO₂e):**")

        # Input method selection
        emission_input_method = st.radio(
            "Data input method:",
            ["Annual Total", "Monthly Values"],
            key="emission_input_method",
            help="Choose annual for quick input, monthly for precise data"
        )

        emission_sources_data = []
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

        if emission_input_method == "Annual Total":
            for source in all_selected_emission_sources:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(source)
                with col2:
                    annual_total = st.number_input(
                        "tCO₂e/year",
                        value=1000.0,
                        min_value=0.0,
                        step=100.0,
                        key=f"emission_{source}_annual",
                        label_visibility="collapsed"
                    )

                emission_sources_data.append({
                    'Source': source,
                    'Annual_Total_tCO2e': annual_total,
                    **{month: annual_total / 12 for month in months}
                })
        else:
            # Monthly input
            for source in all_selected_emission_sources:
                with st.expander(f"📊 {source} - Monthly Data", expanded=False):
                    monthly_values = {}
                    cols = st.columns(4)
                    for i, month in enumerate(months):
                        with cols[i % 4]:
                            monthly_values[month] = st.number_input(
                                month,
                                value=100.0,
                                min_value=0.0,
                                step=10.0,
                                key=f"emission_{source}_{month}"
                            )

                    annual_total = sum(monthly_values.values())
                    st.write(f"**Annual Total: {annual_total:,.2f} tCO₂e**")

                    emission_sources_data.append({
                        'Source': source,
                        'Annual_Total_tCO2e': annual_total,
                        **monthly_values
                    })

        # Store in session state
        st.session_state.emission_by_source_data = emission_sources_data

        # Show summary
        st.markdown("---")
        total_emission_by_source = sum([s['Annual_Total_tCO2e'] for s in emission_sources_data])
        st.metric("Total Emission By Source", f"{total_emission_by_source:,.0f} tCO₂e")

    st.markdown("---")

    # Generate data button
    if st.button("🎯 Create GHG Dataset"):
        if create_manual_dataset_from_facilities():
            st.markdown("""
            <div class="success-box">
                ✅ GHG dataset created successfully! You can now generate reports.
            </div>
            """, unsafe_allow_html=True)
        else:
            st.error("❌ Please enter emissions data for at least one facility.")

def add_facility_emissions(facility_idx):
    """Add emissions data for a specific facility with full source breakdown"""

    # Facility name
    facility_name = st.text_input(
        "Facility Name",
        value=f"Facility {chr(65 + facility_idx)}",  # A, B, C, etc.
        key=f"facility_{facility_idx}_name"
    )

    # Production data
    production = st.number_input(
        "Production (barrels or units/year)",
        value=100000.0,
        min_value=0.0,
        step=10000.0,
        key=f"facility_{facility_idx}_production"
    )

    st.markdown("---")

    # Emission sources by scope
    scope_sources = {
        'scope1': [
            "Combustion - Natural Gas", "Combustion - Fuel Oil", "Combustion - Diesel",
            "Process Emissions - Refining", "Fugitive - Equipment Leaks", "Fugitive - Venting",
            "Mobile Combustion - Fleet", "Flaring", "Process Venting"
        ],
        'scope2': [
            "Purchased Electricity", "Purchased Steam", "Purchased Heat/Cooling"
        ],
        'scope3': [
            "Purchased Goods/Services", "Capital Goods", "Fuel/Energy Activities",
            "Transportation - Upstream", "Waste Generated", "Business Travel",
            "Employee Commuting", "Transportation - Downstream", "Processing of Products",
            "Use of Sold Products", "End-of-life Products", "Leased Assets"
        ]
    }

    st.write("**📋 Emission Sources Configuration:**")

    # Initialize custom sources in session state
    if 'custom_sources' not in st.session_state:
        st.session_state.custom_sources = {}

    for scope in ['scope1', 'scope2', 'scope3']:
        key = f"facility_{facility_idx}_{scope}_custom"
        if key not in st.session_state.custom_sources:
            st.session_state.custom_sources[key] = []

    # Collect all sources data
    facility_sources = {
        'scope1': [],
        'scope2': [],
        'scope3': []
    }

    # Scope 1 Sources
    with st.expander("🔥 Scope 1 - Direct Emissions Sources", expanded=True):
        st.write("**Select emission sources for this facility:**")
        selected_scope1 = st.multiselect(
            "Scope 1 Sources",
            scope_sources['scope1'],
            key=f"facility_{facility_idx}_scope1_sources"
        )

        # Custom sources UI for Scope 1
        custom_scope1 = add_custom_source_ui(facility_idx, 'scope1', scope_sources['scope1'], selected_scope1)

        # Combine predefined and custom sources
        all_scope1_sources = selected_scope1 + custom_scope1

        if all_scope1_sources:
            facility_sources['scope1'] = add_sources_with_data(
                facility_idx, 'scope1', all_scope1_sources
            )

    # Scope 2 Sources
    with st.expander("⚡ Scope 2 - Energy Emissions Sources", expanded=False):
        st.write("**Select emission sources for this facility:**")
        selected_scope2 = st.multiselect(
            "Scope 2 Sources",
            scope_sources['scope2'],
            key=f"facility_{facility_idx}_scope2_sources"
        )

        # Custom sources UI for Scope 2
        custom_scope2 = add_custom_source_ui(facility_idx, 'scope2', scope_sources['scope2'], selected_scope2)

        # Combine predefined and custom sources
        all_scope2_sources = selected_scope2 + custom_scope2

        if all_scope2_sources:
            facility_sources['scope2'] = add_sources_with_data(
                facility_idx, 'scope2', all_scope2_sources
            )

    # Scope 3 Sources
    with st.expander("🔗 Scope 3 - Indirect Emissions Sources", expanded=False):
        st.write("**Select emission sources for this facility:**")
        selected_scope3 = st.multiselect(
            "Scope 3 Sources",
            scope_sources['scope3'],
            key=f"facility_{facility_idx}_scope3_sources"
        )

        # Custom sources UI for Scope 3
        custom_scope3 = add_custom_source_ui(facility_idx, 'scope3', scope_sources['scope3'], selected_scope3)

        # Combine predefined and custom sources
        all_scope3_sources = selected_scope3 + custom_scope3

        if all_scope3_sources:
            facility_sources['scope3'] = add_sources_with_data(
                facility_idx, 'scope3', all_scope3_sources
            )

    # Calculate totals
    scope1_total = sum([s['annual_total'] for s in facility_sources['scope1']])
    scope2_total = sum([s['annual_total'] for s in facility_sources['scope2']])
    scope3_total = sum([s['annual_total'] for s in facility_sources['scope3']])
    total_emissions = scope1_total + scope2_total + scope3_total

    # Summary metrics
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Scope 1 Total", f"{scope1_total:,.0f} tCO2e")
    with col2:
        st.metric("Scope 2 Total", f"{scope2_total:,.0f} tCO2e")
    with col3:
        st.metric("Scope 3 Total", f"{scope3_total:,.0f} tCO2e")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Annual Emissions", f"{total_emissions:,.0f} tCO2e")
    with col2:
        energy_intensity = total_emissions / production if production > 0 else 0
        st.metric("Energy Intensity", f"{energy_intensity:.4f} tCO2e/unit")

    # Store facility data
    facility_data = {
        'idx': facility_idx,
        'name': facility_name,
        'production': production,
        'scope1_total': scope1_total,
        'scope2_total': scope2_total,
        'scope3_total': scope3_total,
        'total': total_emissions,
        'intensity': energy_intensity,
        'sources': facility_sources
    }

    # Update session state
    if len(st.session_state.facilities_data) <= facility_idx:
        st.session_state.facilities_data.extend([{}] * (facility_idx + 1 - len(st.session_state.facilities_data)))
    st.session_state.facilities_data[facility_idx] = facility_data

def add_custom_source_ui(facility_idx, scope, predefined_sources, selected_sources):
    """UI for adding custom emission sources with duplicate validation"""

    key = f"facility_{facility_idx}_{scope}_custom"
    custom_sources_list = st.session_state.custom_sources[key]

    st.markdown("---")
    st.write("**➕ Add Custom Source:**")

    col1, col2, col3 = st.columns([3, 2, 1])

    with col1:
        new_source_name = st.text_input(
            "Custom source name",
            key=f"{key}_input",
            placeholder="e.g., Refrigerant Leaks, Steam Boiler, etc."
        )

    with col2:
        add_button = st.button("Add Source", key=f"{key}_add_button")

    # Handle adding new custom source
    if add_button and new_source_name:
        # Check for duplicates
        all_existing_sources = predefined_sources + selected_sources + custom_sources_list
        if new_source_name in all_existing_sources:
            st.error(f"❌ Error: '{new_source_name}' already exists. Please use a different name.")
        else:
            st.session_state.custom_sources[key].append(new_source_name)
            st.success(f"✅ Added custom source: '{new_source_name}'")
            st.rerun()

    # Display existing custom sources with delete buttons
    if custom_sources_list:
        st.write("**Custom Sources:**")
        for idx, custom_source in enumerate(custom_sources_list):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.text(f"• {custom_source}")
            with col2:
                if st.button("🗑️ Delete", key=f"{key}_delete_{idx}"):
                    st.session_state.custom_sources[key].pop(idx)
                    st.rerun()

    return custom_sources_list

def add_sources_with_data(facility_idx, scope, sources):
    """Add emission data for each source - supports annual or monthly input"""

    st.write(f"**Enter data for {len(sources)} selected source(s):**")

    # Input method selection for this scope
    input_method = st.radio(
        "Data input method:",
        ["Annual Total (÷12 for monthly)", "Monthly Values (12 inputs per source)"],
        key=f"facility_{facility_idx}_{scope}_method",
        help="Choose annual for quick input, monthly for precise data"
    )

    sources_data = []
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
             'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    for source in sources:
        st.write(f"**{source}**")

        if input_method == "Annual Total (÷12 for monthly)":
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(source)
            with col2:
                annual_total = st.number_input(
                    "tCO2e/year",
                    value=1000.0,
                    min_value=0.0,
                    step=50.0,
                    key=f"facility_{facility_idx}_{scope}_{source}_annual",
                    label_visibility="collapsed"
                )

            sources_data.append({
                'source': source,
                'annual_total': annual_total,
                'input_method': 'annual',
                'monthly_values': {month: annual_total / 12 for month in months}
            })

        else:  # Monthly input
            with st.expander(f"📅 {source} - Monthly Data", expanded=False):
                monthly_values = {}
                for row_idx in range(4):
                    cols = st.columns(3)
                    for col_idx in range(3):
                        month_idx = row_idx * 3 + col_idx
                        month = months[month_idx]
                        with cols[col_idx]:
                            monthly_values[month] = st.number_input(
                                month,
                                value=85.0,
                                min_value=0.0,
                                step=5.0,
                                key=f"facility_{facility_idx}_{scope}_{source}_{month}",
                                label_visibility="visible"
                            )

                annual_total = sum(monthly_values.values())
                st.write(f"Annual Total: {annual_total:,.2f} tCO2e")

                sources_data.append({
                    'source': source,
                    'annual_total': annual_total,
                    'input_method': 'monthly',
                    'monthly_values': monthly_values
                })

    return sources_data

# OLD FUNCTION REMOVED - No longer used with per-facility input structure

def create_manual_dataset_from_facilities():
    """Create dataset from facility-level manual inputs"""
    try:
        # Check if we have facility data
        if not st.session_state.facilities_data or len(st.session_state.facilities_data) == 0:
            return False

        # Filter out empty facility data
        valid_facilities = [f for f in st.session_state.facilities_data if f]

        if len(valid_facilities) == 0:
            return False

        # Create temporary Excel file with facility data
        excel_gen = GHGExcelGenerator()
        excel_gen.company_info.update(st.session_state.company_info)

        # Generate data structure from facility inputs
        manual_data = generate_data_from_facilities(valid_facilities)

        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
            tmp_path = tmp_file.name

        # Create Excel file with real facility data
        create_manual_excel(tmp_path, manual_data)

        # Load with report generator
        report_gen = GHGReportGenerator(tmp_path)

        if report_gen.data:
            st.session_state.ghg_data = report_gen

            # Clean up temporary file
            os.unlink(tmp_path)
            return True

        return False

    except Exception as e:
        st.error(f"Error creating dataset: {str(e)}")
        import traceback
        st.error(f"Detailed error: {traceback.format_exc()}")
        return False

def generate_data_from_facilities(facilities):
    """Generate data structure from real facility inputs with source-level detail

    Handles: Facility → Scope → Source → Monthly/Annual data
    """
    data = {
        'scope1': [],
        'scope2': [],
        'scope3': [],
        'emission_by_source': [],
        'facilities': [],
        'totals': {}
    }

    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
             'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    # Aggregate sources across all facilities per scope
    aggregated_sources = {
        'scope1': {},
        'scope2': {},
        'scope3': {}
    }

    # Collect all sources from all facilities
    for facility in facilities:
        sources = facility.get('sources', {})

        for scope in ['scope1', 'scope2', 'scope3']:
            for source_data in sources.get(scope, []):
                source_name = source_data['source']

                if source_name not in aggregated_sources[scope]:
                    aggregated_sources[scope][source_name] = {
                        'annual_total': 0,
                        'monthly_values': {month: 0 for month in months}
                    }

                # Add this facility's contribution to the source
                aggregated_sources[scope][source_name]['annual_total'] += source_data['annual_total']

                for month in months:
                    aggregated_sources[scope][source_name]['monthly_values'][month] += source_data['monthly_values'].get(month, 0)

    # Create scope emission entries with source-level detail
    for scope in ['scope1', 'scope2', 'scope3']:
        for source_name, source_agg in aggregated_sources[scope].items():
            annual_total = source_agg['annual_total']
            monthly_vals = source_agg['monthly_values']

            # Calculate percentage within scope
            scope_total = sum([s['annual_total'] for s in aggregated_sources[scope].values()])
            percentage = (annual_total / scope_total * 100) if scope_total > 0 else 0

            data[scope].append({
                'Source': source_name,
                'Annual_Total': annual_total,
                'Percentage': percentage,
                **monthly_vals
            })

    # Create facility breakdown with REAL user input data
    scope1_total = 0
    scope2_total = 0
    scope3_total = 0

    for facility in facilities:
        facility_scope1 = facility.get('scope1_total', 0)
        facility_scope2 = facility.get('scope2_total', 0)
        facility_scope3 = facility.get('scope3_total', 0)

        scope1_total += facility_scope1
        scope2_total += facility_scope2
        scope3_total += facility_scope3

        data['facilities'].append({
            'Facility': facility['name'],
            'Scope_1': facility_scope1,
            'Scope_2': facility_scope2,
            'Scope_3': facility_scope3,
            'Energy_Intensity': facility['intensity'],
            'Production': facility['production']
        })

    # Store totals
    grand_total = scope1_total + scope2_total + scope3_total

    data['totals'] = {
        'scope1_total': scope1_total,
        'scope2_total': scope2_total,
        'scope3_total': scope3_total,
        'grand_total': grand_total
    }

    # Add emission_by_source data from session state
    import streamlit as st
    if hasattr(st, 'session_state') and hasattr(st.session_state, 'emission_by_source_data'):
        data['emission_by_source'] = st.session_state.emission_by_source_data
    else:
        data['emission_by_source'] = []

    return data

# OLD FUNCTION REMOVED - Used fake facility generation with arbitrary multipliers
# Replaced by generate_data_from_facilities() which uses REAL user input

def create_manual_excel(filepath, data):
    """Create Excel file from manual data"""
    with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
        # Dashboard sheet
        company_info = st.session_state.company_info
        summary_data = pd.DataFrame([
            ['Company Name', company_info.get('name', 'Your Company')],
            ['Reporting Year', company_info.get('reporting_year', 2025)],
            ['Report Date', company_info.get('report_date', datetime.now().strftime('%Y-%m-%d'))],
            ['Total GHG Emissions (tCO2e)', f"{data['totals']['grand_total']:.2f}"],
            ['Scope 1 Emissions (tCO2e)', f"{data['totals']['scope1_total']:.2f}"],
            ['Scope 2 Emissions (tCO2e)', f"{data['totals']['scope2_total']:.2f}"],
            ['Scope 3 Emissions (tCO2e)', f"{data['totals']['scope3_total']:.2f}"],
            ['Total Facilities', company_info.get('num_facilities', 4)]
        ])
        summary_data.to_excel(writer, sheet_name='Dashboard', index=False, header=False)

        # Emission sheets
        pd.DataFrame(data['scope1']).to_excel(writer, sheet_name='Scope 1 Emissions', index=False)
        pd.DataFrame(data['scope2']).to_excel(writer, sheet_name='Scope 2 Emissions', index=False)
        pd.DataFrame(data['scope3']).to_excel(writer, sheet_name='Scope 3 Emissions', index=False)
        pd.DataFrame(data['facilities']).to_excel(writer, sheet_name='Facility Breakdown', index=False)

        # Create Emission By Source sheet (use dummy data if not provided)
        if 'emission_by_source' in data and data['emission_by_source']:
            emission_data = pd.DataFrame(data['emission_by_source'])
        else:
            # Dummy data if user didn't input
            emission_data = pd.DataFrame([
                {'Source': 'Natural Gas', 'Annual_Total_tCO2e': 10000},
                {'Source': 'Electricity', 'Annual_Total_tCO2e': 8000},
                {'Source': 'Steam', 'Annual_Total_tCO2e': 5000}
            ])
        emission_data.to_excel(writer, sheet_name='Emission By Source', index=False)

        targets_data = pd.DataFrame([
            {'Metric': 'Total GHG Reduction Target (%)', 'Target_2024': 5, 'Actual_2024': 3.2, 'Status': 'On Track'}
        ])
        targets_data.to_excel(writer, sheet_name='Targets & Performance', index=False)

        # Custom Text sheet
        company_intro = company_info.get('company_introduction', '')
        conclusion_title = company_info.get('conclusion_title', 'Conclusion & Final Notes')
        conclusion = company_info.get('conclusion_text', '')
        custom_text_data = pd.DataFrame([
            ['Field', 'Content'],
            ['Company Introduction', company_intro],
            ['Conclusion Title', conclusion_title],
            ['Conclusion', conclusion]
        ])
        custom_text_data.to_excel(writer, sheet_name='Custom Text', index=False, header=False)

def show_reports_page():
    """Page for generating reports"""
    st.header("📊 Generate Reports")

    if st.session_state.ghg_data is None:
        st.markdown("""
        <div class="warning-box">
            ⚠️ No GHG data loaded. Please either:
            <ul>
                <li>Upload an Excel file in the "📤 Upload Excel" page, or</li>
                <li>Enter data manually in the "✍️ Manual Input" page, or</li>
                <li>Load sample data from the "🏠 Home" page</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        return

    # Facility filtering section
    st.subheader("🏭 Facility Selection")

    # Get list of facilities from data
    facilities_df = st.session_state.ghg_data.data.get('Facility Breakdown', pd.DataFrame())
    facility_options = ['All Facilities'] + list(facilities_df['Facility'].values) if not facilities_df.empty and 'Facility' in facilities_df.columns else ['All Facilities']

    selected_facility = st.selectbox(
        "Select facility to view:",
        facility_options,
        help="Choose 'All Facilities' for combined view or select a specific facility"
    )

    # Store selected facility in session state for report generation
    st.session_state.selected_facility = selected_facility

    st.markdown("---")

    # Show data summary (filtered if specific facility selected)
    summary = st.session_state.ghg_data.get_summary_statistics(selected_facility if selected_facility != 'All Facilities' else None)

    st.subheader(f"📈 Data Summary - {selected_facility}")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Emissions", f"{summary.get('total_emissions', 0):,.0f} tCO2e")
    with col2:
        st.metric("Scope 1", f"{summary.get('scope1_total', 0):,.0f} tCO2e")
    with col3:
        st.metric("Scope 2", f"{summary.get('scope2_total', 0):,.0f} tCO2e")
    with col4:
        st.metric("Scope 3", f"{summary.get('scope3_total', 0):,.0f} tCO2e")

    st.markdown("---")

    # Chart previews
    st.subheader("📊 Chart Previews")

    col1, col2 = st.columns(2)

    with col1:
        # Scope comparison chart
        scope_chart = st.session_state.ghg_data.create_scope_comparison_chart(selected_facility if selected_facility != 'All Facilities' else None)
        if scope_chart:
            st.plotly_chart(scope_chart, use_container_width=True)

    with col2:
        # Monthly trend chart
        trend_chart = st.session_state.ghg_data.create_monthly_trend_chart(selected_facility if selected_facility != 'All Facilities' else None)
        if trend_chart:
            st.plotly_chart(trend_chart, use_container_width=True)

    # Sankey diagram with threshold control
    st.subheader("🔄 Emission Flow Analysis")

    col1, col2 = st.columns([3, 1])
    with col1:
        st.write("**Sankey Diagram Threshold Control:**")
    with col2:
        threshold_percent = st.number_input(
            "Threshold (%)",
            min_value=0,
            max_value=100,
            value=80,
            step=5,
            key="sankey_threshold",
            help="Show individual sources up to this percentage. Remaining sources grouped as 'Others'."
        )

    sankey_chart = st.session_state.ghg_data.create_sankey_diagram(
        facility_filter=selected_facility if selected_facility != 'All Facilities' else None,
        threshold_percent=threshold_percent
    )
    if sankey_chart:
        st.plotly_chart(sankey_chart, use_container_width=True)

    st.markdown("---")

    # Report generation section
    st.subheader("🎯 Generate Reports")

    # AI Recommendations Toggle
    st.markdown("### 🤖 AI-Powered Recommendations")
    use_ai_recs = st.checkbox(
        "Use AI to generate personalized recommendations",
        value=False,
        help="Enable GPT-5 to analyze your data and generate tailored recommendations (requires OpenAI API key)"
    )

    if use_ai_recs:
        with st.expander("⚙️ AI Configuration", expanded=True):
            st.info("""
            **About AI Recommendations:**
            - Uses OpenAI's GPT-5-mini model to analyze your emissions data
            - Generates 5-6 personalized recommendations based on your actual emission sources
            - Considers petroleum industry best practices and GHG Protocol standards
            - Cost: ~$0.01-0.02 per report
            - Falls back to rule-based recommendations if API fails
            """)

            api_key_input = st.text_input(
                "OpenAI API Key",
                type="password",
                placeholder="sk-...",
                help="Get your API key from https://platform.openai.com/api-keys"
            )

            if api_key_input:
                os.environ['OPENAI_API_KEY'] = api_key_input
                st.success("✅ API key configured!")
            else:
                st.warning("⚠️ Please enter your OpenAI API key to use AI recommendations")

        # Store in session state
        st.session_state.use_ai_recommendations = use_ai_recs and bool(api_key_input)
    else:
        st.session_state.use_ai_recommendations = False
        st.info("💡 Using rule-based recommendations (threshold-driven analysis)")

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🌐 Interactive HTML Report")
        st.write("Comprehensive report with interactive charts and navigation")

        if st.button("📥 Generate & Download HTML Report", type="primary"):
            html_report = generate_html_report()
            if html_report:
                st.download_button(
                    label="📥 Download HTML Report",
                    data=html_report,
                    file_name=f"GHG_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                    mime="text/html"
                )

    with col2:
        st.markdown("### 📄 Professional PDF Report")
        st.write("Executive summary with charts and recommendations")

        if st.button("📥 Generate & Download PDF Report", type="primary"):
            pdf_report = generate_pdf_report()
            if pdf_report:
                st.download_button(
                    label="📥 Download PDF Report",
                    data=pdf_report,
                    file_name=f"GHG_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf"
                )

def show_template_page():
    """Page for downloading Excel templates"""
    st.header("📋 Download Excel Template")

    st.markdown("""
    <div class="info-box">
        <h4>📊 Excel Template Information</h4>
        <p>Download our professional Excel template to get started with GHG reporting.
        The template includes all necessary sheets and sample data to guide your input.</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📝 Template Features")
        st.write("""
        - **Dashboard:** Company information and summary
        - **Scope 1 Emissions:** Direct emission sources
        - **Scope 2 Emissions:** Energy-related emissions
        - **Scope 3 Emissions:** Value chain emissions
        - **Energy Consumption:** Energy use tracking
        - **Facility Breakdown:** Site-specific data
        - **Targets & Performance:** Goal monitoring
        """)

    with col2:
        st.markdown("### 🎯 Sample Data Included")
        st.write("""
        - Realistic petroleum industry emission sources
        - Monthly emission patterns
        - Multiple facility scenarios
        - Energy intensity calculations
        - Performance targets and KPIs
        - Professional formatting
        """)

    st.markdown("---")

    # Template download options
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📄 Blank Template")
        st.write("Clean template ready for your data input")

        if st.button("📥 Download Blank Template"):
            template_data = create_blank_template()
            st.download_button(
                label="📥 Download Blank Excel Template",
                data=template_data,
                file_name=f"GHG_Template_Blank_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    with col2:
        st.markdown("### 🧪 Sample Template")
        st.write("Template with realistic sample data for testing")

        if st.button("📥 Download Sample Template"):
            sample_data = create_sample_template()
            st.download_button(
                label="📥 Download Sample Excel Template",
                data=sample_data,
                file_name=f"GHG_Template_Sample_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

def show_help_page():
    """Help and information page"""
    st.header("ℹ️ Help & Information")

    tab1, tab2, tab3, tab4 = st.tabs(["📋 User Guide", "🏭 GHG Standards", "🔧 Technical Info", "❓ FAQ"])

    with tab1:
        st.markdown("""
        ## 📋 User Guide

        ### Getting Started
        1. **Choose your input method:**
           - Upload an Excel file with your data
           - Enter data manually through web forms
           - Load sample data to explore features

        2. **Generate reports:**
           - HTML reports for interactive analysis
           - PDF reports for professional presentations
           - Download templates for data collection

        ### Data Requirements
        - **Scope 1:** Direct emissions from owned/controlled sources
        - **Scope 2:** Indirect emissions from purchased energy
        - **Scope 3:** Other indirect emissions in value chain
        - **Facilities:** Site-specific operational data
        - **Energy:** Consumption data for efficiency analysis

        ### Report Features
        - Executive summary with key metrics
        - Professional charts and visualizations
        - Strategic recommendations
        - Regulatory compliance information
        """)

    with tab2:
        st.markdown("""
        ## 🏭 GHG Protocol Standards

        ### Corporate Standard Compliance
        This system follows the **GHG Protocol Corporate Accounting and Reporting Standard**,
        the most widely used international standard for corporate GHG emissions accounting.

        ### Scope Definitions
        - **Scope 1 (Direct):** Emissions from sources owned or controlled by the organization
        - **Scope 2 (Energy Indirect):** Emissions from purchased electricity, steam, heat, cooling
        - **Scope 3 (Other Indirect):** All other indirect emissions in the value chain

        ### ISO 14064 Guidelines
        The system also aligns with ISO 14064 principles for:
        - GHG inventories and verification
        - Organizational quantification and reporting
        - Project-level quantification and reporting

        ### Petroleum Industry Focus
        - Refinery operations and processes
        - Upstream and downstream activities
        - Fugitive emissions tracking
        - Flaring and venting analysis
        """)

    with tab3:
        st.markdown("""
        ## 🔧 Technical Information

        ### System Architecture
        - **Frontend:** Streamlit web application
        - **Backend:** Python with pandas, plotly, reportlab
        - **Charts:** Interactive Plotly visualizations
        - **Reports:** HTML and PDF generation
        - **Data:** Excel integration and processing

        ### Performance Specifications
        - Supports datasets up to 1000+ emission sources
        - Report generation < 30 seconds
        - Cross-platform compatibility
        - Production-ready deployment

        ### File Formats Supported
        - **Input:** Excel (.xlsx, .xls)
        - **Output:** HTML, PDF
        - **Templates:** Excel with sample data

        ### Browser Compatibility
        - Chrome (recommended)
        - Firefox
        - Safari
        - Edge
        """)

    with tab4:
        st.markdown("""
        ## ❓ Frequently Asked Questions

        ### Q: What data do I need to get started?
        A: You need emission data for your operations categorized by GHG Protocol scopes.
        Our Excel template provides guidance on required data structure.

        ### Q: Can I use this for non-petroleum companies?
        A: Yes! While designed for petroleum companies, the system works for any organization
        tracking GHG emissions following the GHG Protocol.

        ### Q: How accurate are the calculations?
        A: The system uses standard emission factors and follows GHG Protocol calculation
        methodologies. Accuracy depends on the quality of input data.

        ### Q: Can I customize the reports?
        A: Reports include professional formatting and industry-standard content.
        Company information and data-driven content is customizable.

        ### Q: Is my data secure?
        A: All processing happens locally in your browser session. No data is stored
        on external servers.

        ### Q: What if I need help with data collection?
        A: Download our Excel template which includes sample data and guidance for
        each emission category and data field.
        """)

def load_sample_data():
    """Load sample GHG data"""
    try:
        # Create sample data using the existing generator
        excel_gen = GHGExcelGenerator()

        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
            tmp_path = tmp_file.name

        # Generate sample Excel file
        excel_gen.create_excel_template(tmp_path)

        # Load with report generator
        report_gen = GHGReportGenerator(tmp_path)

        if report_gen.data:
            st.session_state.ghg_data = report_gen

            # Clean up
            os.unlink(tmp_path)
            return True

        return False

    except Exception as e:
        st.error(f"Error loading sample data: {str(e)}")
        return False

def generate_html_report():
    """Generate HTML report and return as string"""
    try:
        if st.session_state.ghg_data is None:
            return None

        html_generator = HTMLReportGenerator(st.session_state.ghg_data)

        # Get selected facility if available
        facility_filter = None
        if 'selected_facility' in st.session_state and st.session_state.selected_facility != 'All Facilities':
            facility_filter = st.session_state.selected_facility

        # Create temporary file for HTML
        with tempfile.NamedTemporaryFile(delete=False, suffix='.html', mode='w') as tmp_file:
            tmp_path = tmp_file.name

        # Get use_ai from session state
        use_ai = st.session_state.get('use_ai_recommendations', False)

        if html_generator.generate_html_report(tmp_path, facility_filter, use_ai=use_ai):
            with open(tmp_path, 'r', encoding='utf-8') as f:
                html_content = f.read()

            os.unlink(tmp_path)
            return html_content

        return None

    except Exception as e:
        st.error(f"Error generating HTML report: {str(e)}")
        return None

def generate_pdf_report():
    """Generate PDF report and return as bytes"""
    try:
        if st.session_state.ghg_data is None:
            return None

        pdf_generator = SimplePDFReportGenerator(st.session_state.ghg_data)

        # Create temporary file for PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_path = tmp_file.name

        # Get use_ai from session state
        use_ai = st.session_state.get('use_ai_recommendations', False)

        if pdf_generator.generate_simple_pdf_report(tmp_path, use_ai=use_ai):
            with open(tmp_path, 'rb') as f:
                pdf_content = f.read()

            os.unlink(tmp_path)
            return pdf_content

        return None

    except Exception as e:
        st.error(f"Error generating PDF report: {str(e)}")
        return None

def create_blank_template():
    """Create blank Excel template"""
    try:
        excel_gen = GHGExcelGenerator()

        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
            tmp_path = tmp_file.name

        # Create template with minimal data
        excel_gen.company_info = {
            'name': '[Your Company Name]',
            'reporting_year': 2025,
            'report_date': datetime.now().strftime('%Y-%m-%d'),
            'facilities': ['Facility A', 'Facility B', 'Facility C', 'Facility D']
        }

        excel_gen.create_excel_template(tmp_path)

        with open(tmp_path, 'rb') as f:
            template_data = f.read()

        os.unlink(tmp_path)
        return template_data

    except Exception as e:
        st.error(f"Error creating blank template: {str(e)}")
        return None

def create_sample_template():
    """Create sample Excel template with data"""
    try:
        excel_gen = GHGExcelGenerator()

        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
            tmp_path = tmp_file.name

        # Generate sample Excel file with full data
        excel_gen.create_excel_template(tmp_path)

        with open(tmp_path, 'rb') as f:
            template_data = f.read()

        os.unlink(tmp_path)
        return template_data

    except Exception as e:
        st.error(f"Error creating sample template: {str(e)}")
        import traceback
        st.error(f"Detailed error: {traceback.format_exc()}")
        return None

if __name__ == "__main__":
    main()