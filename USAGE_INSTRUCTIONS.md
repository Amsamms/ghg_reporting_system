# 📖 GHG Reporting System - Complete Usage Instructions

**Step-by-Step Guide to Using the Professional GHG Reporting System**

---

## 🚀 Quick Start Guide

### **Option 1: Web Application (Streamlit) - Recommended**

#### **Step 1: Launch the Web Application**
```bash
# Navigate to project directory
cd "/home/amsamms/projects/Amr Abu Mady/ghg_reporting_system"

# Activate virtual environment
source ../ghg_report_env/bin/activate

# Launch web application
streamlit run streamlit_app.py
```

#### **Step 2: Access the Application**
- Open your web browser
- Go to: **http://localhost:8501**
- You'll see the professional GHG Reporting interface

---

## 🌐 Web Application Usage Guide

### **📱 Navigation Pages Overview**

1. **🏠 Home** - Overview, features, and sample data
2. **📤 Upload Excel** - Upload completed Excel templates
3. **✍️ Manual Input** - Enter data through web forms
4. **📊 Generate Reports** - Create and download reports
5. **📋 Template Download** - Get Excel templates
6. **ℹ️ Help & Info** - Comprehensive help system

---

### **Method 1: Using Excel Templates (Recommended)**

#### **Step 1: Download Template**
1. Go to **"📋 Template Download"** page
2. Choose your option:
   - **"📄 Blank Template"** - Empty template for your data
   - **"🧪 Sample Template"** - Pre-filled example for learning
3. Click **"📥 Download"** button
4. Save the Excel file to your computer

#### **Step 2: Fill the Excel Template**
Open the downloaded Excel file. It contains these sheets:

**📊 Required Sheets:**
- **Dashboard:** Company information and summary
- **Scope 1 Emissions:** Direct emission sources (combustion, fugitive, process)
- **Scope 2 Emissions:** Energy purchases (electricity, steam, heat)
- **Scope 3 Emissions:** Value chain emissions (suppliers, transportation, etc.)
- **Energy Consumption:** Energy usage data
- **Facility Breakdown:** Site-specific information
- **Targets & Performance:** Goals and progress tracking

**✍️ How to Fill Each Sheet:**

**Dashboard Sheet:**
```
Company Name: [Your Company Name]
Reporting Year: [e.g., 2024]
Report Date: [Today's date]
Total Facilities: [Number of your facilities]
```

**Scope 1 Emissions:**
```
Source                    | Annual_Total | Jan | Feb | ... | Dec
Combustion - Natural Gas  | 5000        | 450 | 420 | ... | 380
Process Emissions         | 2500        | 200 | 210 | ... | 190
Fugitive - Equipment      | 1200        | 100 | 95  | ... | 105
```

**Scope 2 & 3 Emissions:** Follow same format with your emission sources

#### **Step 3: Upload Completed Template**
1. Go to **"📤 Upload Excel"** page
2. Drag and drop your completed Excel file OR click "Browse"
3. Wait for **✅ "File uploaded and validated successfully!"**
4. Review the **Data Preview** to ensure everything loaded correctly

#### **Step 4: Generate Reports**
1. Go to **"📊 Generate Reports"** page
2. Review your **📈 Data Summary** and **📊 Chart Previews**
3. Choose your report format:
   - **🌐 HTML Report:** Interactive, web-ready (click "Generate & Download HTML Report")
   - **📄 PDF Report:** Professional, print-ready (click "Generate & Download PDF Report")
4. Click the download button when report is ready

---

### **Method 2: Manual Data Entry**

#### **Step 1: Enter Company Information**
1. Go to **"✍️ Manual Input"** page
2. Fill in:
   - **Company Name:** Your organization name
   - **Reporting Year:** Usually current year (2024)
   - **Report Date:** Today's date
   - **Number of Facilities:** Your operational sites

#### **Step 2: Add Emission Sources**
Work through the three tabs:

**🔥 Scope 1 (Direct) Tab:**
1. Select from pre-populated sources (e.g., "Combustion - Natural Gas")
2. OR add custom sources in the text box and click "Add Custom"
3. Enter **annual emissions (tCO₂e)** for each source
4. Example: Natural Gas = 5000 tCO₂e, Diesel = 2000 tCO₂e

**⚡ Scope 2 (Energy) Tab:**
1. Select energy sources (e.g., "Purchased Electricity")
2. Enter annual emissions for each
3. Example: Electricity = 3000 tCO₂e, Steam = 1500 tCO₂e

**🔗 Scope 3 (Indirect) Tab:**
1. Select value chain sources (e.g., "Transportation - Upstream")
2. Enter annual emissions for each
3. Example: Transportation = 2500 tCO₂e, Business Travel = 800 tCO₂e

#### **Step 3: Create Dataset**
1. After entering ALL emission sources across all three scopes
2. Click **"🎯 Create GHG Dataset"**
3. Wait for **✅ "GHG dataset created successfully!"**

#### **Step 4: Generate Reports**
1. Go to **"📊 Generate Reports"** page
2. Same process as Method 1 above

---

## ⌨️ Command Line Interface (Alternative)

### **Basic Commands**

#### **Create Sample Data**
```bash
python main.py --sample
```

#### **Generate Reports via CLI**
```bash
# HTML report only
python main.py --cli --excel data/sample_ghg_data.xlsx --output reports/ --types html

# PDF report only
python main.py --cli --excel data/sample_ghg_data.xlsx --output reports/ --types pdf

# Both HTML and PDF
python main.py --cli --excel data/sample_ghg_data.xlsx --output reports/ --types pdf html
```

#### **Launch GUI (if tkinter available)**
```bash
python main.py
```

---

## 📊 Understanding Your Reports

### **📈 HTML Report Features:**
- **Interactive Charts:** Click, zoom, hover for details
- **Navigation Menu:** Jump to different sections
- **Responsive Design:** Works on desktop and mobile
- **Professional Styling:** Ready for stakeholder presentations

### **📄 PDF Report Features:**
- **Executive Summary:** Key metrics and findings
- **Comprehensive Analysis:** Detailed scope breakdowns
- **Facility Performance:** Site-specific analysis
- **Strategic Recommendations:** Prioritized action items
- **Methodology Section:** Standards compliance information
- **Professional Formatting:** Print-ready quality

### **📊 Chart Types in Reports:**
1. **Sankey Diagrams:** Emission flow from sources → scopes → total
2. **Scope Comparison:** Bar charts showing Scope 1, 2, 3 breakdown
3. **Monthly Trends:** Time series showing seasonal patterns
4. **Facility Breakdown:** Performance comparison across sites
5. **Energy Mix:** Pie charts showing energy source distribution

---

## 🔧 Troubleshooting Guide

### **Common Issues & Solutions**

#### **Excel Upload Problems:**
- **Error:** "Failed to load Excel file"
- **Solution:** Ensure file has all required sheets (Dashboard, Scope 1/2/3 Emissions, etc.)
- **Check:** File format is .xlsx or .xls
- **Verify:** Data is in correct columns (Source, Annual_Total, etc.)

#### **Manual Input Issues:**
- **Error:** "Please add at least one emission source"
- **Solution:** Add emission sources in ALL three scope tabs before clicking "Create GHG Dataset"
- **Check:** Enter non-zero values for annual emissions

#### **Chart Display Problems:**
- **Issue:** Charts not showing properly
- **Solution:** Refresh the page or try in different browser
- **Alternative:** Use CLI method to generate reports

#### **Download Problems:**
- **Issue:** Reports not downloading
- **Solution:** Check browser download settings
- **Try:** Right-click on download button and "Save as..."

### **Browser Compatibility:**
- ✅ **Chrome** (Recommended)
- ✅ **Firefox**
- ✅ **Safari**
- ✅ **Microsoft Edge**

---

## 💡 Best Practices

### **Data Collection Tips:**
1. **Start with Sample Template:** Learn the format first
2. **Collect Monthly Data:** More accurate than annual estimates
3. **Use Consistent Units:** Stick to tCO₂e throughout
4. **Include All Sources:** Don't forget small emission sources
5. **Verify Calculations:** Double-check your emission factors

### **Report Generation Tips:**
1. **Use HTML for Analysis:** Interactive features help explore data
2. **Use PDF for Sharing:** Professional format for stakeholders
3. **Generate Both Formats:** Different audiences prefer different formats
4. **Keep Raw Data:** Save your Excel files for future updates

### **Data Quality Checks:**
- ✅ Total emissions seem reasonable for your organization size
- ✅ Scope percentages align with industry benchmarks
- ✅ Monthly patterns make sense (no extreme outliers)
- ✅ Facility data adds up to organizational totals

---

## 🎯 Step-by-Step Example Walkthrough

### **Complete Example: Small Petroleum Company**

#### **Step 1: Company Setup**
```
Company Name: ABC Petroleum Services
Reporting Year: 2024
Facilities: 3 (Refinery A, Terminal B, Office C)
```

#### **Step 2: Emission Sources**
**Scope 1:**
- Combustion - Natural Gas: 8,500 tCO₂e
- Combustion - Diesel: 3,200 tCO₂e
- Process Emissions: 2,800 tCO₂e
- Fugitive - Equipment: 1,500 tCO₂e

**Scope 2:**
- Purchased Electricity: 4,200 tCO₂e
- Purchased Steam: 1,800 tCO₂e

**Scope 3:**
- Transportation - Upstream: 3,500 tCO₂e
- Business Travel: 800 tCO₂e
- Employee Commuting: 1,200 tCO₂e

#### **Step 3: Expected Results**
- **Total Emissions:** 27,500 tCO₂e
- **Scope 1:** 16,000 tCO₂e (58.2%)
- **Scope 2:** 6,000 tCO₂e (21.8%)
- **Scope 3:** 5,500 tCO₂e (20.0%)

#### **Step 4: Generated Reports**
Your reports will include:
- Professional charts showing emission breakdown
- Facility performance comparison
- Strategic recommendations for reduction
- Compliance with GHG Protocol standards

---

## 🆘 Getting Additional Help

### **Resources Available:**
1. **In-App Help:** Click "ℹ️ Help & Info" in the web application
2. **Sample Templates:** Use provided examples to learn format
3. **Test Data:** Load sample data to see how reports look
4. **Documentation:** Read README.md for technical details

### **Support Checklist:**
- [ ] Tried sample data first to understand system
- [ ] Checked browser compatibility
- [ ] Verified Excel template format
- [ ] Reviewed error messages for guidance
- [ ] Tested with smaller dataset first

---

**🌱 You're Ready to Create Professional GHG Reports!**

The system provides everything you need for comprehensive greenhouse gas emissions reporting that meets professional standards and regulatory requirements. Start with the sample data to familiarize yourself, then use your real data to create stunning reports! 🎯