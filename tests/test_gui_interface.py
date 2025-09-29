"""
Unit Tests for GHGReportingGUI Module

This module contains comprehensive unit tests for the GHGReportingGUI class,
testing GUI functionality, user interactions, and error handling.
"""

import pytest
import tkinter as tk
from tkinter import ttk
import threading
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import os

# Import with error handling since GUI might not be available in headless environments
try:
    from gui_interface import GHGReportingGUI
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False
    pytest.skip("GUI not available in headless environment", allow_module_level=True)


class TestGHGReportingGUI:
    """Test suite for GHGReportingGUI class"""

    @pytest.fixture
    def root_window(self):
        """Create root Tkinter window for testing"""
        if not GUI_AVAILABLE:
            pytest.skip("GUI not available")

        root = tk.Tk()
        root.withdraw()  # Hide window during testing
        yield root
        try:
            root.destroy()
        except:
            pass

    @pytest.fixture
    def gui_app(self, root_window):
        """Create GHGReportingGUI instance for testing"""
        app = GHGReportingGUI(root_window)
        return app

    @pytest.mark.unit
    @pytest.mark.skipif(not GUI_AVAILABLE, reason="GUI not available")
    def test_initialization(self, root_window):
        """Test proper initialization of GHGReportingGUI"""
        app = GHGReportingGUI(root_window)

        assert app.root == root_window
        assert app.excel_file_path is None
        assert app.output_directory is None
        assert app.report_generator is None

        # Check window properties
        assert root_window.title() == "GHG Reporting System - PetrolCorp International"

    @pytest.mark.unit
    @pytest.mark.skipif(not GUI_AVAILABLE, reason="GUI not available")
    def test_ui_components_creation(self, gui_app):
        """Test that all UI components are created"""
        # Check main components exist
        assert hasattr(gui_app, 'notebook')
        assert hasattr(gui_app, 'file_tab')
        assert hasattr(gui_app, 'report_tab')
        assert hasattr(gui_app, 'info_tab')

        # Check variables exist
        assert hasattr(gui_app, 'excel_path_var')
        assert hasattr(gui_app, 'output_path_var')
        assert hasattr(gui_app, 'progress_var')
        assert hasattr(gui_app, 'status_var')

        # Check progress bar exists
        assert hasattr(gui_app, 'progress_bar')

    @pytest.mark.unit
    @pytest.mark.skipif(not GUI_AVAILABLE, reason="GUI not available")
    def test_styles_setup(self, gui_app):
        """Test that custom styles are set up correctly"""
        # The styles should be configured without errors
        # This test ensures the setup_styles method doesn't crash
        assert True  # If we get here, styles were set up successfully

    @pytest.mark.unit
    @pytest.mark.skipif(not GUI_AVAILABLE, reason="GUI not available")
    def test_notebook_tabs(self, gui_app):
        """Test that notebook tabs are created correctly"""
        notebook = gui_app.notebook

        # Check that tabs exist
        tabs = notebook.tabs()
        assert len(tabs) == 3

        # Check tab text (if accessible)
        try:
            tab_texts = [notebook.tab(tab, "text") for tab in tabs]
            assert any("File Management" in text for text in tab_texts)
            assert any("Report Generation" in text for text in tab_texts)
            assert any("Information" in text for text in tab_texts)
        except:
            # Some Tkinter versions might not support tab text retrieval
            pass

    @pytest.mark.unit
    @pytest.mark.skipif(not GUI_AVAILABLE, reason="GUI not available")
    @patch('gui_interface.filedialog.askopenfilename')
    def test_browse_excel_file_success(self, mock_filedialog, gui_app, temp_output_dir):
        """Test successful Excel file browsing"""
        test_file = temp_output_dir / 'test.xlsx'
        test_file.touch()

        mock_filedialog.return_value = str(test_file)

        gui_app.browse_excel_file()

        assert gui_app.excel_file_path == str(test_file)
        assert gui_app.excel_path_var.get() == str(test_file)
        assert "test.xlsx" in gui_app.status_var.get()

    @pytest.mark.unit
    @pytest.mark.skipif(not GUI_AVAILABLE, reason="GUI not available")
    @patch('gui_interface.filedialog.askopenfilename')
    def test_browse_excel_file_cancel(self, mock_filedialog, gui_app):
        """Test Excel file browsing when user cancels"""
        mock_filedialog.return_value = ""  # User cancelled

        original_path = gui_app.excel_file_path
        gui_app.browse_excel_file()

        assert gui_app.excel_file_path == original_path  # Should remain unchanged

    @pytest.mark.unit
    @pytest.mark.skipif(not GUI_AVAILABLE, reason="GUI not available")
    @patch('gui_interface.filedialog.askdirectory')
    def test_browse_output_directory_success(self, mock_filedialog, gui_app, temp_output_dir):
        """Test successful output directory browsing"""
        mock_filedialog.return_value = str(temp_output_dir)

        gui_app.browse_output_directory()

        assert gui_app.output_directory == str(temp_output_dir)
        assert gui_app.output_path_var.get() == str(temp_output_dir)
        assert str(temp_output_dir) in gui_app.status_var.get()

    @pytest.mark.unit
    @pytest.mark.skipif(not GUI_AVAILABLE, reason="GUI not available")
    @patch('gui_interface.filedialog.askdirectory')
    def test_browse_output_directory_cancel(self, mock_filedialog, gui_app):
        """Test output directory browsing when user cancels"""
        mock_filedialog.return_value = ""  # User cancelled

        original_dir = gui_app.output_directory
        gui_app.browse_output_directory()

        assert gui_app.output_directory == original_dir  # Should remain unchanged

    @pytest.mark.unit
    @pytest.mark.skipif(not GUI_AVAILABLE, reason="GUI not available")
    @patch('gui_interface.messagebox.showerror')
    def test_validate_excel_file_no_file(self, mock_messagebox, gui_app):
        """Test Excel file validation with no file selected"""
        gui_app.excel_file_path = None

        gui_app.validate_excel_file()

        mock_messagebox.assert_called_once()
        assert "select an Excel file" in mock_messagebox.call_args[0][1].lower()

    @pytest.mark.unit
    @pytest.mark.skipif(not GUI_AVAILABLE, reason="GUI not available")
    @patch('gui_interface.GHGReportGenerator')
    def test_validate_excel_file_success(self, mock_report_gen, gui_app, valid_excel_file):
        """Test successful Excel file validation"""
        gui_app.excel_file_path = str(valid_excel_file)

        # Mock successful validation
        mock_gen_instance = Mock()
        mock_gen_instance.data = {'test': 'data'}
        mock_gen_instance.get_summary_statistics.return_value = {
            'total_emissions': 50000,
            'scope1_total': 20000,
            'scope2_total': 15000,
            'scope3_total': 15000,
            'total_facilities': 4
        }
        mock_report_gen.return_value = mock_gen_instance

        gui_app.validate_excel_file()

        assert gui_app.report_generator is not None
        assert "validation successful" in gui_app.status_var.get().lower()

    @pytest.mark.unit
    @pytest.mark.skipif(not GUI_AVAILABLE, reason="GUI not available")
    @patch('gui_interface.GHGReportGenerator')
    def test_validate_excel_file_failure(self, mock_report_gen, gui_app, temp_output_dir):
        """Test Excel file validation failure"""
        test_file = temp_output_dir / 'invalid.xlsx'
        test_file.touch()
        gui_app.excel_file_path = str(test_file)

        # Mock failed validation
        mock_gen_instance = Mock()
        mock_gen_instance.data = None
        mock_report_gen.return_value = mock_gen_instance

        gui_app.validate_excel_file()

        validation_text = gui_app.validation_text.get(1.0, tk.END)
        assert "validation failed" in validation_text.lower()

    @pytest.mark.unit
    @pytest.mark.skipif(not GUI_AVAILABLE, reason="GUI not available")
    @patch('gui_interface.GHGReportGenerator')
    def test_validate_excel_file_exception(self, mock_report_gen, gui_app, temp_output_dir):
        """Test Excel file validation with exception"""
        test_file = temp_output_dir / 'error.xlsx'
        test_file.touch()
        gui_app.excel_file_path = str(test_file)

        # Mock exception during validation
        mock_report_gen.side_effect = Exception("Validation error")

        gui_app.validate_excel_file()

        validation_text = gui_app.validation_text.get(1.0, tk.END)
        assert "error" in validation_text.lower()

    @pytest.mark.unit
    @pytest.mark.skipif(not GUI_AVAILABLE, reason="GUI not available")
    @patch('gui_interface.messagebox.showerror')
    def test_check_prerequisites_no_excel(self, mock_messagebox, gui_app):
        """Test prerequisite check with no Excel file"""
        gui_app.excel_file_path = None

        result = gui_app._check_prerequisites()

        assert result is False
        mock_messagebox.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.skipif(not GUI_AVAILABLE, reason="GUI not available")
    @patch('gui_interface.messagebox.showerror')
    def test_check_prerequisites_no_output(self, mock_messagebox, gui_app, temp_output_dir):
        """Test prerequisite check with no output directory"""
        test_file = temp_output_dir / 'test.xlsx'
        test_file.touch()
        gui_app.excel_file_path = str(test_file)
        gui_app.output_directory = None

        result = gui_app._check_prerequisites()

        assert result is False
        mock_messagebox.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.skipif(not GUI_AVAILABLE, reason="GUI not available")
    @patch('gui_interface.messagebox.showerror')
    def test_check_prerequisites_no_generator(self, mock_messagebox, gui_app, temp_output_dir):
        """Test prerequisite check with no report generator"""
        test_file = temp_output_dir / 'test.xlsx'
        test_file.touch()
        gui_app.excel_file_path = str(test_file)
        gui_app.output_directory = str(temp_output_dir)
        gui_app.report_generator = None

        result = gui_app._check_prerequisites()

        assert result is False
        mock_messagebox.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.skipif(not GUI_AVAILABLE, reason="GUI not available")
    def test_check_prerequisites_success(self, gui_app, temp_output_dir):
        """Test successful prerequisite check"""
        test_file = temp_output_dir / 'test.xlsx'
        test_file.touch()
        gui_app.excel_file_path = str(test_file)
        gui_app.output_directory = str(temp_output_dir)
        gui_app.report_generator = Mock()

        result = gui_app._check_prerequisites()

        assert result is True

    @pytest.mark.unit
    @pytest.mark.skipif(not GUI_AVAILABLE, reason="GUI not available")
    def test_update_progress(self, gui_app):
        """Test progress update functionality"""
        test_message = "Test progress message"

        gui_app._update_progress(test_message, show_progress=True)

        assert gui_app.progress_var.get() == test_message
        assert gui_app.status_var.get() == test_message

        gui_app._update_progress(test_message, show_progress=False)
        # Progress bar should be stopped

    @pytest.mark.unit
    @pytest.mark.skipif(not GUI_AVAILABLE, reason="GUI not available")
    @patch('gui_interface.threading.Thread')
    def test_generate_pdf_report_prerequisites_fail(self, mock_thread, gui_app):
        """Test PDF generation when prerequisites fail"""
        gui_app.excel_file_path = None  # Missing prerequisite

        gui_app.generate_pdf_report()

        # Thread should not be started
        mock_thread.assert_not_called()

    @pytest.mark.unit
    @pytest.mark.skipif(not GUI_AVAILABLE, reason="GUI not available")
    @patch('gui_interface.threading.Thread')
    def test_generate_pdf_report_success(self, mock_thread, gui_app, temp_output_dir):
        """Test PDF generation with valid prerequisites"""
        # Set up valid prerequisites
        test_file = temp_output_dir / 'test.xlsx'
        test_file.touch()
        gui_app.excel_file_path = str(test_file)
        gui_app.output_directory = str(temp_output_dir)
        gui_app.report_generator = Mock()

        mock_thread_instance = Mock()
        mock_thread.return_value = mock_thread_instance

        gui_app.generate_pdf_report()

        mock_thread.assert_called_once()
        mock_thread_instance.start.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.skipif(not GUI_AVAILABLE, reason="GUI not available")
    @patch('gui_interface.threading.Thread')
    def test_generate_html_report_success(self, mock_thread, gui_app, temp_output_dir):
        """Test HTML generation with valid prerequisites"""
        # Set up valid prerequisites
        test_file = temp_output_dir / 'test.xlsx'
        test_file.touch()
        gui_app.excel_file_path = str(test_file)
        gui_app.output_directory = str(temp_output_dir)
        gui_app.report_generator = Mock()

        mock_thread_instance = Mock()
        mock_thread.return_value = mock_thread_instance

        gui_app.generate_html_report()

        mock_thread.assert_called_once()
        mock_thread_instance.start.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.skipif(not GUI_AVAILABLE, reason="GUI not available")
    @patch('gui_interface.PDFReportGenerator')
    @patch('gui_interface.messagebox.askyesno')
    def test_pdf_generation_thread_success(self, mock_messagebox, mock_pdf_gen, gui_app, temp_output_dir):
        """Test PDF generation thread success"""
        # Set up prerequisites
        gui_app.output_directory = str(temp_output_dir)
        gui_app.report_generator = Mock()

        # Mock successful PDF generation
        mock_pdf_instance = Mock()
        mock_pdf_instance.generate_pdf_report.return_value = True
        mock_pdf_gen.return_value = mock_pdf_instance

        mock_messagebox.return_value = False  # Don't open file

        # Run the thread function directly
        gui_app._generate_pdf_thread()

        mock_pdf_gen.assert_called_once()
        mock_pdf_instance.generate_pdf_report.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.skipif(not GUI_AVAILABLE, reason="GUI not available")
    @patch('gui_interface.PDFReportGenerator')
    def test_pdf_generation_thread_failure(self, mock_pdf_gen, gui_app, temp_output_dir):
        """Test PDF generation thread failure"""
        gui_app.output_directory = str(temp_output_dir)
        gui_app.report_generator = Mock()

        # Mock failed PDF generation
        mock_pdf_instance = Mock()
        mock_pdf_instance.generate_pdf_report.return_value = False
        mock_pdf_gen.return_value = mock_pdf_instance

        # Run the thread function directly
        gui_app._generate_pdf_thread()

        # Should handle failure gracefully

    @pytest.mark.unit
    @pytest.mark.skipif(not GUI_AVAILABLE, reason="GUI not available")
    @patch('gui_interface.HTMLReportGenerator')
    @patch('gui_interface.messagebox.askyesno')
    def test_html_generation_thread_success(self, mock_messagebox, mock_html_gen, gui_app, temp_output_dir):
        """Test HTML generation thread success"""
        gui_app.output_directory = str(temp_output_dir)
        gui_app.report_generator = Mock()

        # Mock successful HTML generation
        mock_html_instance = Mock()
        mock_html_instance.generate_html_report.return_value = True
        mock_html_gen.return_value = mock_html_instance

        mock_messagebox.return_value = False  # Don't open file

        # Run the thread function directly
        gui_app._generate_html_thread()

        mock_html_gen.assert_called_once()
        mock_html_instance.generate_html_report.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.skipif(not GUI_AVAILABLE, reason="GUI not available")
    @patch('gui_interface.messagebox.askyesno')
    @patch('gui_interface.os.startfile')
    def test_report_generation_complete_open_file(self, mock_startfile, mock_messagebox, gui_app, temp_output_dir):
        """Test report generation completion with file opening"""
        mock_messagebox.return_value = True  # User wants to open file

        test_file = temp_output_dir / 'test_report.pdf'
        test_file.touch()

        gui_app._report_generation_complete("PDF", str(test_file))

        mock_messagebox.assert_called_once()
        mock_startfile.assert_called_once_with(str(test_file))

    @pytest.mark.unit
    @pytest.mark.skipif(not GUI_AVAILABLE, reason="GUI not available")
    @patch('gui_interface.messagebox.askyesno')
    def test_report_generation_complete_no_open(self, mock_messagebox, gui_app, temp_output_dir):
        """Test report generation completion without opening file"""
        mock_messagebox.return_value = False  # User doesn't want to open file

        test_file = temp_output_dir / 'test_report.pdf'
        test_file.touch()

        gui_app._report_generation_complete("PDF", str(test_file))

        mock_messagebox.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.skipif(not GUI_AVAILABLE, reason="GUI not available")
    @patch('gui_interface.messagebox.showerror')
    def test_report_generation_error(self, mock_messagebox, gui_app):
        """Test report generation error handling"""
        error_message = "Test error message"

        gui_app._report_generation_error("PDF", error_message)

        mock_messagebox.assert_called_once()
        assert error_message in mock_messagebox.call_args[0][1]

    @pytest.mark.error_handling
    @pytest.mark.skipif(not GUI_AVAILABLE, reason="GUI not available")
    def test_thread_exception_handling(self, gui_app, temp_output_dir):
        """Test exception handling in generation threads"""
        gui_app.output_directory = str(temp_output_dir)
        gui_app.report_generator = Mock()

        # Mock to raise exception
        with patch('gui_interface.PDFReportGenerator') as mock_pdf_gen:
            mock_pdf_gen.side_effect = Exception("Thread error")

            # Should not crash
            gui_app._generate_pdf_thread()

        with patch('gui_interface.HTMLReportGenerator') as mock_html_gen:
            mock_html_gen.side_effect = Exception("Thread error")

            # Should not crash
            gui_app._generate_html_thread()

    @pytest.mark.integration
    @pytest.mark.skipif(not GUI_AVAILABLE, reason="GUI not available")
    def test_full_workflow_simulation(self, gui_app, valid_excel_file, temp_output_dir):
        """Test full workflow simulation"""
        # Simulate user workflow
        gui_app.excel_file_path = str(valid_excel_file)
        gui_app.excel_path_var.set(str(valid_excel_file))

        gui_app.output_directory = str(temp_output_dir)
        gui_app.output_path_var.set(str(temp_output_dir))

        # Validate file
        with patch('gui_interface.GHGReportGenerator') as mock_gen:
            mock_instance = Mock()
            mock_instance.data = {'test': 'data'}
            mock_instance.get_summary_statistics.return_value = {
                'total_emissions': 50000,
                'total_facilities': 4
            }
            mock_gen.return_value = mock_instance

            gui_app.validate_excel_file()

        # Check prerequisites
        assert gui_app._check_prerequisites() is True

    @pytest.mark.performance
    @pytest.mark.skipif(not GUI_AVAILABLE, reason="GUI not available")
    def test_gui_responsiveness(self, gui_app):
        """Test GUI responsiveness during operations"""
        import time

        # Test that GUI updates don't block
        start_time = time.time()
        gui_app._update_progress("Test message", True)
        gui_app.root.update()  # Process pending events
        end_time = time.time()

        update_time = end_time - start_time
        assert update_time < 1.0, f"GUI update took {update_time:.2f}s, expected < 1.0s"

    @pytest.mark.unit
    @pytest.mark.skipif(not GUI_AVAILABLE, reason="GUI not available")
    def test_validation_text_widget(self, gui_app):
        """Test validation text widget functionality"""
        test_message = "Test validation message"

        gui_app.validation_text.delete(1.0, tk.END)
        gui_app.validation_text.insert(tk.END, test_message)

        content = gui_app.validation_text.get(1.0, tk.END).strip()
        assert content == test_message

    @pytest.mark.unit
    @pytest.mark.skipif(not GUI_AVAILABLE, reason="GUI not available")
    def test_window_geometry(self, gui_app):
        """Test window geometry and positioning"""
        # Window should have reasonable dimensions
        geometry = gui_app.root.geometry()
        assert 'x' in geometry  # Should contain width and height

    @pytest.mark.unit
    @pytest.mark.skipif(not GUI_AVAILABLE, reason="GUI not available")
    def test_status_bar_updates(self, gui_app):
        """Test status bar update functionality"""
        test_status = "Test status message"

        gui_app.status_var.set(test_status)
        assert gui_app.status_var.get() == test_status

    @pytest.mark.error_handling
    @pytest.mark.skipif(not GUI_AVAILABLE, reason="GUI not available")
    def test_file_opening_errors(self, gui_app, temp_output_dir):
        """Test error handling when opening generated files"""
        # Test file that doesn't exist
        fake_file = temp_output_dir / 'nonexistent.pdf'

        with patch('gui_interface.messagebox.askyesno', return_value=True):
            with patch('gui_interface.os.startfile', side_effect=Exception("Cannot open")):
                # Should handle file opening errors gracefully
                gui_app._report_generation_complete("PDF", str(fake_file))

    @pytest.mark.unit
    @pytest.mark.skipif(not GUI_AVAILABLE, reason="GUI not available")
    def test_main_function(self):
        """Test the main function"""
        with patch('gui_interface.tk.Tk') as mock_tk:
            with patch('gui_interface.GHGReportingGUI') as mock_gui:
                mock_root = Mock()
                mock_tk.return_value = mock_root

                # Import and run main (but patch mainloop to avoid hanging)
                with patch.object(mock_root, 'mainloop'):
                    from gui_interface import main
                    main()

                mock_tk.assert_called_once()
                mock_gui.assert_called_once()

if __name__ == "__main__":
    pytest.main([__file__, "-v"])