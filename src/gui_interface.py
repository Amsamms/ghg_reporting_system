import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import sys
from pathlib import Path
import threading
from datetime import datetime

# Add the src directory to Python path
sys.path.append(os.path.dirname(__file__))

from report_generator import GHGReportGenerator
from pdf_report import PDFReportGenerator
from html_report import HTMLReportGenerator

class GHGReportingGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("GHG Reporting System - PetrolCorp International")
        self.root.geometry("800x600")
        self.root.configure(bg='#f0f0f0')

        # Initialize variables
        self.excel_file_path = None
        self.output_directory = None
        self.report_generator = None

        self.setup_ui()
        self.setup_styles()

    def setup_styles(self):
        """Setup custom styles for ttk widgets"""
        style = ttk.Style()
        style.theme_use('clam')

        # Configure styles
        style.configure('Title.TLabel',
                       font=('Arial', 16, 'bold'),
                       foreground='#2E86C1',
                       background='#f0f0f0')

        style.configure('Heading.TLabel',
                       font=('Arial', 12, 'bold'),
                       foreground='#2874A6',
                       background='#f0f0f0')

        style.configure('Custom.TButton',
                       font=('Arial', 10, 'bold'),
                       padding=10)

    def setup_ui(self):
        """Setup the user interface"""
        # Main title
        title_frame = tk.Frame(self.root, bg='#f0f0f0', height=80)
        title_frame.pack(fill='x', padx=20, pady=10)
        title_frame.pack_propagate(False)

        title_label = ttk.Label(title_frame,
                               text="🌱 GHG Emissions Reporting System",
                               style='Title.TLabel')
        title_label.pack(anchor='center', expand=True)

        subtitle_label = ttk.Label(title_frame,
                                  text="Professional GHG Report Generator for Petroleum Companies",
                                  font=('Arial', 10),
                                  foreground='#5D6D7E',
                                  background='#f0f0f0')
        subtitle_label.pack(anchor='center')

        # Main container with notebook for tabs
        main_container = ttk.Frame(self.root)
        main_container.pack(fill='both', expand=True, padx=20, pady=10)

        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill='both', expand=True)

        # Tab 1: File Management
        self.file_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.file_tab, text="📁 File Management")
        self.setup_file_management_tab()

        # Tab 2: Report Generation
        self.report_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.report_tab, text="📊 Report Generation")
        self.setup_report_generation_tab()

        # Tab 3: Settings & Info
        self.info_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.info_tab, text="ℹ️ Information")
        self.setup_info_tab()

        # Status bar
        self.setup_status_bar()

    def setup_file_management_tab(self):
        """Setup file management tab"""
        # Excel file selection
        file_frame = ttk.LabelFrame(self.file_tab, text="Excel Data File", padding=15)
        file_frame.pack(fill='x', padx=10, pady=10)

        self.excel_path_var = tk.StringVar()
        excel_path_entry = ttk.Entry(file_frame, textvariable=self.excel_path_var, width=60)
        excel_path_entry.pack(side='left', fill='x', expand=True)

        ttk.Button(file_frame,
                  text="Browse Excel File",
                  command=self.browse_excel_file,
                  style='Custom.TButton').pack(side='right', padx=(10, 0))

        # Output directory selection
        output_frame = ttk.LabelFrame(self.file_tab, text="Output Directory", padding=15)
        output_frame.pack(fill='x', padx=10, pady=10)

        self.output_path_var = tk.StringVar()
        output_path_entry = ttk.Entry(output_frame, textvariable=self.output_path_var, width=60)
        output_path_entry.pack(side='left', fill='x', expand=True)

        ttk.Button(output_frame,
                  text="Select Output Folder",
                  command=self.browse_output_directory,
                  style='Custom.TButton').pack(side='right', padx=(10, 0))

        # File validation
        validation_frame = ttk.LabelFrame(self.file_tab, text="File Validation", padding=15)
        validation_frame.pack(fill='x', padx=10, pady=10)

        ttk.Button(validation_frame,
                  text="🔍 Validate Excel File",
                  command=self.validate_excel_file,
                  style='Custom.TButton').pack(anchor='center')

        # Validation results
        self.validation_text = tk.Text(validation_frame, height=8, width=70,
                                     font=('Consolas', 9),
                                     bg='#f8f9fa', relief='sunken')
        self.validation_text.pack(pady=(10, 0))

        validation_scrollbar = ttk.Scrollbar(validation_frame, orient='vertical',
                                           command=self.validation_text.yview)
        validation_scrollbar.pack(side='right', fill='y')
        self.validation_text.config(yscrollcommand=validation_scrollbar.set)

    def setup_report_generation_tab(self):
        """Setup report generation tab"""
        # Report options
        options_frame = ttk.LabelFrame(self.report_tab, text="Report Generation Options", padding=15)
        options_frame.pack(fill='x', padx=10, pady=10)

        # PDF Report button
        pdf_frame = tk.Frame(options_frame, bg='white', relief='ridge', bd=2)
        pdf_frame.pack(fill='x', pady=5)

        ttk.Label(pdf_frame, text="📄 PDF Report",
                 font=('Arial', 12, 'bold'),
                 foreground='#C0392B').pack(anchor='w', padx=10, pady=5)

        ttk.Label(pdf_frame,
                 text="Generate professional PDF report with charts, analysis, and recommendations",
                 font=('Arial', 9)).pack(anchor='w', padx=10)

        ttk.Button(pdf_frame,
                  text="Generate PDF Report",
                  command=self.generate_pdf_report,
                  style='Custom.TButton').pack(anchor='center', pady=10)

        # HTML Report button
        html_frame = tk.Frame(options_frame, bg='white', relief='ridge', bd=2)
        html_frame.pack(fill='x', pady=5)

        ttk.Label(html_frame, text="🌐 Interactive HTML Report",
                 font=('Arial', 12, 'bold'),
                 foreground='#2874A6').pack(anchor='w', padx=10, pady=5)

        ttk.Label(html_frame,
                 text="Generate interactive HTML report with dynamic charts and navigation",
                 font=('Arial', 9)).pack(anchor='w', padx=10)

        ttk.Button(html_frame,
                  text="Generate HTML Report",
                  command=self.generate_html_report,
                  style='Custom.TButton').pack(anchor='center', pady=10)

        # Progress frame
        progress_frame = ttk.LabelFrame(self.report_tab, text="Generation Progress", padding=15)
        progress_frame.pack(fill='x', padx=10, pady=10)

        self.progress_var = tk.StringVar(value="Ready to generate reports...")
        self.progress_label = ttk.Label(progress_frame, textvariable=self.progress_var)
        self.progress_label.pack(anchor='w')

        self.progress_bar = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.progress_bar.pack(fill='x', pady=(10, 0))

    def setup_info_tab(self):
        """Setup information tab"""
        # System info
        info_frame = ttk.LabelFrame(self.info_tab, text="System Information", padding=15)
        info_frame.pack(fill='both', expand=True, padx=10, pady=10)

        info_text = tk.Text(info_frame, font=('Consolas', 10), bg='#f8f9fa', relief='flat')
        info_text.pack(fill='both', expand=True)

        info_content = """
📊 GHG Reporting System v1.0

🏢 Company: PetrolCorp International
📅 Report Year: 2024
🌍 Standards: GHG Protocol Corporate Standard, ISO 14064

📋 Report Features:
• Comprehensive Scope 1, 2, and 3 emissions analysis
• Sankey diagrams for emission flow visualization
• Facility-wise performance breakdown
• Energy consumption analysis (SEU equivalent)
• Monthly trend analysis
• Strategic recommendations with priority levels
• Interactive charts and professional formatting

📈 Chart Types Included:
• Scope comparison bar charts
• Monthly emission trends
• Sankey flow diagrams
• Facility breakdown analysis
• Energy consumption pie charts
• Performance scatter plots

🎯 Key Benefits:
• Professional PDF reports for stakeholder presentations
• Interactive HTML reports for detailed analysis
• Automated chart generation from Excel data
• Industry-standard GHG reporting methodology
• Customizable recommendations engine

⚙️ Technical Specifications:
• Python-based backend with Plotly visualizations
• ReportLab PDF generation
• Jinja2 HTML templating
• Pandas data processing
• OpenpyXL Excel integration

📞 Support Information:
For technical support or customization requests,
contact the development team.

Generated on: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        info_text.insert('1.0', info_content)
        info_text.config(state='disabled')

    def setup_status_bar(self):
        """Setup status bar"""
        self.status_frame = tk.Frame(self.root, bg='#34495e', height=25)
        self.status_frame.pack(fill='x', side='bottom')
        self.status_frame.pack_propagate(False)

        self.status_var = tk.StringVar(value="Ready | Select Excel file and output directory to begin")
        self.status_label = tk.Label(self.status_frame,
                                   textvariable=self.status_var,
                                   bg='#34495e',
                                   fg='white',
                                   font=('Arial', 9))
        self.status_label.pack(side='left', padx=10, pady=2)

    def browse_excel_file(self):
        """Browse for Excel file"""
        file_path = filedialog.askopenfilename(
            title="Select GHG Data Excel File",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
        )
        if file_path:
            self.excel_file_path = file_path
            self.excel_path_var.set(file_path)
            self.status_var.set(f"Excel file selected: {os.path.basename(file_path)}")

    def browse_output_directory(self):
        """Browse for output directory"""
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.output_directory = directory
            self.output_path_var.set(directory)
            self.status_var.set(f"Output directory: {directory}")

    def validate_excel_file(self):
        """Validate the selected Excel file"""
        if not self.excel_file_path:
            messagebox.showerror("Error", "Please select an Excel file first.")
            return

        self.validation_text.delete(1.0, tk.END)
        self.validation_text.insert(tk.END, "Validating Excel file...\n")
        self.validation_text.update()

        try:
            # Create report generator to validate file
            self.report_generator = GHGReportGenerator(self.excel_file_path)

            if self.report_generator.data:
                self.validation_text.insert(tk.END, "✅ File validation successful!\n\n")

                # Display file contents summary
                self.validation_text.insert(tk.END, "📊 File Structure:\n")
                for sheet_name, df in self.report_generator.data.items():
                    self.validation_text.insert(tk.END, f"  • {sheet_name}: {len(df)} rows, {len(df.columns)} columns\n")

                # Display summary statistics
                summary = self.report_generator.get_summary_statistics()
                self.validation_text.insert(tk.END, f"\n📈 Summary Statistics:\n")
                self.validation_text.insert(tk.END, f"  • Total Emissions: {summary.get('total_emissions', 0):,.0f} tCO₂e\n")
                self.validation_text.insert(tk.END, f"  • Scope 1: {summary.get('scope1_total', 0):,.0f} tCO₂e\n")
                self.validation_text.insert(tk.END, f"  • Scope 2: {summary.get('scope2_total', 0):,.0f} tCO₂e\n")
                self.validation_text.insert(tk.END, f"  • Scope 3: {summary.get('scope3_total', 0):,.0f} tCO₂e\n")
                self.validation_text.insert(tk.END, f"  • Total Facilities: {summary.get('total_facilities', 0)}\n")

                self.validation_text.insert(tk.END, "\n✅ Ready to generate reports!")
                self.status_var.set("File validated successfully - Ready to generate reports")
            else:
                self.validation_text.insert(tk.END, "❌ File validation failed - Invalid Excel format")
                self.status_var.set("File validation failed")

        except Exception as e:
            self.validation_text.insert(tk.END, f"❌ Validation Error: {str(e)}\n")
            self.status_var.set("Validation error occurred")

    def generate_pdf_report(self):
        """Generate PDF report in separate thread"""
        if not self._check_prerequisites():
            return

        # Run in separate thread to avoid GUI freezing
        thread = threading.Thread(target=self._generate_pdf_thread)
        thread.daemon = True
        thread.start()

    def _generate_pdf_thread(self):
        """PDF generation thread"""
        try:
            self.root.after(0, self._update_progress, "Generating PDF report...", True)

            # Create PDF generator
            pdf_generator = PDFReportGenerator(self.report_generator)

            # Generate output filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            pdf_filename = f"GHG_Report_{timestamp}.pdf"
            pdf_path = os.path.join(self.output_directory, pdf_filename)

            # Generate PDF
            success = pdf_generator.generate_pdf_report(pdf_path)

            if success:
                self.root.after(0, self._report_generation_complete, "PDF", pdf_path)
            else:
                self.root.after(0, self._report_generation_error, "PDF", "Unknown error occurred")

        except Exception as e:
            self.root.after(0, self._report_generation_error, "PDF", str(e))

    def generate_html_report(self):
        """Generate HTML report in separate thread"""
        if not self._check_prerequisites():
            return

        # Run in separate thread to avoid GUI freezing
        thread = threading.Thread(target=self._generate_html_thread)
        thread.daemon = True
        thread.start()

    def _generate_html_thread(self):
        """HTML generation thread"""
        try:
            self.root.after(0, self._update_progress, "Generating HTML report...", True)

            # Create HTML generator
            html_generator = HTMLReportGenerator(self.report_generator)

            # Generate output filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            html_filename = f"GHG_Report_{timestamp}.html"
            html_path = os.path.join(self.output_directory, html_filename)

            # Generate HTML
            success = html_generator.generate_html_report(html_path)

            if success:
                self.root.after(0, self._report_generation_complete, "HTML", html_path)
            else:
                self.root.after(0, self._report_generation_error, "HTML", "Unknown error occurred")

        except Exception as e:
            self.root.after(0, self._report_generation_error, "HTML", str(e))

    def _check_prerequisites(self):
        """Check if all prerequisites are met"""
        if not self.excel_file_path:
            messagebox.showerror("Error", "Please select an Excel file first.")
            return False

        if not self.output_directory:
            messagebox.showerror("Error", "Please select an output directory first.")
            return False

        if not self.report_generator:
            messagebox.showerror("Error", "Please validate the Excel file first.")
            return False

        return True

    def _update_progress(self, message, show_progress=True):
        """Update progress indicators"""
        self.progress_var.set(message)
        self.status_var.set(message)

        if show_progress:
            self.progress_bar.start()
        else:
            self.progress_bar.stop()

    def _report_generation_complete(self, report_type, file_path):
        """Handle successful report generation"""
        self._update_progress(f"{report_type} report generated successfully!", False)

        result = messagebox.askyesno(
            "Report Generated",
            f"{report_type} report has been generated successfully!\n\n"
            f"File: {os.path.basename(file_path)}\n"
            f"Location: {os.path.dirname(file_path)}\n\n"
            "Would you like to open the file?"
        )

        if result:
            try:
                os.startfile(file_path)  # Windows
            except:
                try:
                    os.system(f'open "{file_path}"')  # macOS
                except:
                    os.system(f'xdg-open "{file_path}"')  # Linux

    def _report_generation_error(self, report_type, error_message):
        """Handle report generation error"""
        self._update_progress("Report generation failed", False)
        messagebox.showerror(
            f"{report_type} Generation Error",
            f"Failed to generate {report_type} report:\n\n{error_message}"
        )

def main():
    """Main function to run the GUI"""
    root = tk.Tk()
    app = GHGReportingGUI(root)

    # Center window on screen
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')

    root.mainloop()

if __name__ == "__main__":
    main()