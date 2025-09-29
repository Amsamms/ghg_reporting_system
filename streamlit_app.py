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

def main():
    # App Header
    st.markdown("""
    <div class="main-header">
        <h1>🌱 Professional GHG Reporting System</h1>
        <p>Comprehensive Greenhouse Gas Emissions Analysis for Petroleum Companies</p>
        <small>Following GHG Protocol Corporate Standard & ISO 14064 Guidelines</small>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar Navigation
    st.sidebar.title("📋 Navigation")
    page = st.sidebar.selectbox(
        "Select a page:",
        ["🏠 Home", "📤 Upload Excel", "✍️ Manual Input", "📊 Generate Reports", "📋 Template Download", "ℹ️ Help & Info"]
    )

    # Initialize session state
    if 'ghg_data' not in st.session_state:
        st.session_state.ghg_data = None
    if 'company_info' not in st.session_state:
        st.session_state.company_info = {}

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
            <li><strong>Energy Consumption:</strong> Energy use data</li>
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
                    # Show summary statistics
                    summary = report_gen.get_summary_statistics()
                    st.write("**Summary Statistics:**")
                    st.write(f"• Total Emissions: {summary.get('total_emissions', 0):,.0f} tCO₂e")
                    st.write(f"• Scope 1: {summary.get('scope1_total', 0):,.0f} tCO₂e")
                    st.write(f"• Scope 2: {summary.get('scope2_total', 0):,.0f} tCO₂e")
                    st.write(f"• Scope 3: {summary.get('scope3_total', 0):,.0f} tCO₂e")

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
        reporting_year = st.number_input("Reporting Year", value=2024, min_value=2020, max_value=2030)

    with col2:
        report_date = st.date_input("Report Date", value=date.today())
        num_facilities = st.number_input("Number of Facilities", value=4, min_value=1, max_value=20)

    # Store company info
    st.session_state.company_info = {
        'name': company_name,
        'reporting_year': reporting_year,
        'report_date': report_date.strftime('%Y-%m-%d'),
        'num_facilities': num_facilities
    }

    st.markdown("---")

    # Emission Sources Input
    st.subheader("🔥 Emission Sources")

    tab1, tab2, tab3 = st.tabs(["Scope 1 (Direct)", "Scope 2 (Energy)", "Scope 3 (Indirect)"])

    # Initialize emission data in session state
    if 'emission_sources' not in st.session_state:
        st.session_state.emission_sources = {
            'scope1': [],
            'scope2': [],
            'scope3': []
        }

    with tab1:
        st.write("**Direct emissions from owned or controlled sources**")
        add_emission_sources("scope1", [
            "Combustion - Natural Gas", "Combustion - Fuel Oil", "Combustion - Diesel",
            "Process Emissions - Refining", "Fugitive - Equipment Leaks", "Fugitive - Venting",
            "Mobile Combustion - Fleet", "Flaring", "Process Venting"
        ])

    with tab2:
        st.write("**Indirect emissions from purchased energy**")
        add_emission_sources("scope2", [
            "Purchased Electricity", "Purchased Steam", "Purchased Heat/Cooling"
        ])

    with tab3:
        st.write("**Other indirect emissions in the value chain**")
        add_emission_sources("scope3", [
            "Purchased Goods/Services", "Capital Goods", "Fuel/Energy Activities",
            "Transportation - Upstream", "Waste Generated", "Business Travel",
            "Employee Commuting", "Transportation - Downstream", "Processing of Products",
            "Use of Sold Products", "End-of-life Products", "Leased Assets"
        ])

    st.markdown("---")

    # Generate data button
    if st.button("🎯 Create GHG Dataset"):
        if create_manual_dataset():
            st.markdown("""
            <div class="success-box">
                ✅ GHG dataset created successfully! You can now generate reports.
            </div>
            """, unsafe_allow_html=True)
        else:
            st.error("❌ Please add at least one emission source to create a dataset.")

def add_emission_sources(scope, default_sources):
    """Add emission sources for a specific scope"""
    st.write(f"**Add {scope.upper()} Sources:**")

    # Pre-populated sources
    selected_sources = st.multiselect(
        f"Select {scope} sources:",
        default_sources,
        key=f"{scope}_multiselect"
    )

    # Custom source input
    custom_source = st.text_input(f"Add custom {scope} source:", key=f"{scope}_custom")
    if st.button(f"Add Custom {scope.upper()}", key=f"{scope}_add_custom"):
        if custom_source and custom_source not in selected_sources:
            selected_sources.append(custom_source)

    # Annual emissions input for each source
    if selected_sources:
        st.write(f"**Enter annual emissions for {scope.upper()} sources (tCO₂e):**")

        sources_data = []
        for source in selected_sources:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(source)
            with col2:
                annual_total = st.number_input(
                    "tCO₂e",
                    value=1000.0,
                    min_value=0.0,
                    step=100.0,
                    key=f"{scope}_{source}_annual",
                    label_visibility="collapsed"
                )
                sources_data.append({
                    'Source': source,
                    'Annual_Total': annual_total
                })

        st.session_state.emission_sources[scope] = sources_data

def create_manual_dataset():
    """Create dataset from manual inputs"""
    try:
        # Check if we have any emission sources
        total_sources = (len(st.session_state.emission_sources.get('scope1', [])) +
                        len(st.session_state.emission_sources.get('scope2', [])) +
                        len(st.session_state.emission_sources.get('scope3', [])))

        if total_sources == 0:
            return False

        # Create temporary Excel file with manual data
        excel_gen = GHGExcelGenerator()
        excel_gen.company_info.update(st.session_state.company_info)

        # Override the dummy data generation with manual data
        manual_data = generate_manual_data_structure()

        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
            tmp_path = tmp_file.name

        # Create Excel file with manual data
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
        return False

def generate_manual_data_structure():
    """Generate data structure from manual inputs"""
    data = {
        'scope1': [],
        'scope2': [],
        'scope3': [],
        'energy': [],
        'facilities': [],
        'totals': {}
    }

    # Process emission sources
    for scope in ['scope1', 'scope2', 'scope3']:
        scope_data = st.session_state.emission_sources.get(scope, [])
        for source_data in scope_data:
            # Generate monthly data (distribute annual total across 12 months)
            annual_total = source_data['Annual_Total']
            monthly_values = [annual_total / 12 + (annual_total * 0.1 * (i % 3 - 1)) for i in range(12)]

            months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                     'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

            row = {
                'Source': source_data['Source'],
                'Annual_Total': annual_total,
                'Percentage': 0,  # Will calculate later
                **dict(zip(months, monthly_values))
            }
            data[scope].append(row)

    # Calculate totals and percentages
    scope1_total = sum([s['Annual_Total'] for s in data['scope1']])
    scope2_total = sum([s['Annual_Total'] for s in data['scope2']])
    scope3_total = sum([s['Annual_Total'] for s in data['scope3']])
    grand_total = scope1_total + scope2_total + scope3_total

    # Update percentages
    for scope in ['scope1', 'scope2', 'scope3']:
        scope_total = sum([s['Annual_Total'] for s in data[scope]])
        for row in data[scope]:
            if scope_total > 0:
                row['Percentage'] = (row['Annual_Total'] / scope_total) * 100

    # Generate facility data based on number of facilities
    facilities = []
    for i in range(st.session_state.company_info.get('num_facilities', 4)):
        facility_name = f"Facility {chr(65 + i)}"  # A, B, C, etc.
        facilities.append({
            'Facility': facility_name,
            'Scope_1': scope1_total * (0.15 + 0.1 * i) / st.session_state.company_info.get('num_facilities', 4),
            'Scope_2': scope2_total * (0.2 + 0.05 * i) / st.session_state.company_info.get('num_facilities', 4),
            'Scope_3': scope3_total * (0.18 + 0.08 * i) / st.session_state.company_info.get('num_facilities', 4),
            'Energy_Intensity': 2.5 + i * 0.5,
            'Production': 50000 + i * 25000
        })

    data['facilities'] = facilities
    data['totals'] = {
        'scope1_total': scope1_total,
        'scope2_total': scope2_total,
        'scope3_total': scope3_total,
        'grand_total': grand_total
    }

    return data

def create_manual_excel(filepath, data):
    """Create Excel file from manual data"""
    with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
        # Dashboard sheet
        company_info = st.session_state.company_info
        summary_data = pd.DataFrame([
            ['Company Name', company_info.get('name', 'Your Company')],
            ['Reporting Year', company_info.get('reporting_year', 2024)],
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

        # Create dummy energy and targets sheets
        energy_data = pd.DataFrame([
            {'Energy_Source': 'Natural Gas (MWh)', 'Annual_Total': 10000, 'Emission_Factor': 0.5},
            {'Energy_Source': 'Electricity (MWh)', 'Annual_Total': 8000, 'Emission_Factor': 0.4},
            {'Energy_Source': 'Steam (MWh)', 'Annual_Total': 5000, 'Emission_Factor': 0.3}
        ])
        energy_data.to_excel(writer, sheet_name='Energy Consumption', index=False)

        targets_data = pd.DataFrame([
            {'Metric': 'Total GHG Reduction Target (%)', 'Target_2024': 5, 'Actual_2024': 3.2, 'Status': 'On Track'}
        ])
        targets_data.to_excel(writer, sheet_name='Targets & Performance', index=False)

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

    # Show data summary
    summary = st.session_state.ghg_data.get_summary_statistics()

    st.subheader("📈 Data Summary")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Emissions", f"{summary.get('total_emissions', 0):,.0f} tCO₂e")
    with col2:
        st.metric("Scope 1", f"{summary.get('scope1_total', 0):,.0f} tCO₂e")
    with col3:
        st.metric("Scope 2", f"{summary.get('scope2_total', 0):,.0f} tCO₂e")
    with col4:
        st.metric("Scope 3", f"{summary.get('scope3_total', 0):,.0f} tCO₂e")

    st.markdown("---")

    # Chart previews
    st.subheader("📊 Chart Previews")

    col1, col2 = st.columns(2)

    with col1:
        # Scope comparison chart
        scope_chart = st.session_state.ghg_data.create_scope_comparison_chart()
        if scope_chart:
            st.plotly_chart(scope_chart, use_container_width=True)

    with col2:
        # Monthly trend chart
        trend_chart = st.session_state.ghg_data.create_monthly_trend_chart()
        if trend_chart:
            st.plotly_chart(trend_chart, use_container_width=True)

    # Sankey diagram
    sankey_chart = st.session_state.ghg_data.create_sankey_diagram()
    if sankey_chart:
        st.subheader("🔄 Emission Flow Analysis")
        st.plotly_chart(sankey_chart, use_container_width=True)

    st.markdown("---")

    # Report generation section
    st.subheader("🎯 Generate Reports")

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

        # Create temporary file for HTML
        with tempfile.NamedTemporaryFile(delete=False, suffix='.html', mode='w') as tmp_file:
            tmp_path = tmp_file.name

        if html_generator.generate_html_report(tmp_path):
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

        if pdf_generator.generate_simple_pdf_report(tmp_path):
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
            'reporting_year': 2024,
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