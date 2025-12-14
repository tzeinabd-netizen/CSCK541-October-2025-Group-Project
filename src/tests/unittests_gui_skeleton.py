import os
import sys
import unittest
import customtkinter as ctk
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.gui.gui_skeleton import RecordManagementSystem,datetime_to_string, _get_field, ClientDialog, AirlineDialog


class TestGUI(unittest.TestCase):
    """
    Test cases for the Graphical user interface.
    """

    def test_fetch_first_matching_key(self):
        """Test the _get_field function to fetch the first matching key from a dictionary."""
        record = {"ID": 1, "name": "Test Name", "Phone_Number": "5551234"}
        # Test with the first matching key
        self.assertEqual(_get_field(record, "ID", "id"), "1")
        # Test with a fallback key
        self.assertEqual(_get_field(record, "Name", "name"), "Test Name")
        # Test with missing keys
        self.assertEqual(_get_field(record, "Missing"), "")


    def test_datetime_to_string (self):
        """Test the datetime_to_string function to convert datetime to string."""
        test_dt = datetime(2025, 12, 14, 14, 35, 10)
        expected_str = "2025-12-14 14:35"
        self.assertEqual(datetime_to_string(test_dt), expected_str)

    def test_app_created(self):
        """Test existence of application"""
        app = RecordManagementSystem()

        self.assertIsNotNone(app)
        self.assertIsInstance(app,ctk.CTk)


    def test_main_content_created(self):
        """Test main content has been created"""
        app = RecordManagementSystem()

        self.assertIsInstance(app.main_frame, ctk.CTkFrame)
        self.assertIsInstance(app.header_frame, ctk.CTkFrame)
        self.assertIsInstance(app.section_title, ctk.CTkLabel)
        self.assertIsInstance(app.search_frame, ctk.CTkFrame)
        self.assertIsInstance(app.records_container, ctk.CTkScrollableFrame)
        self.assertIsInstance(app.add_btn, ctk.CTkButton)
        self.assertIsInstance(app.search_entry, ctk.CTkEntry)


    def test_sidebar_created(self):
        """Test sidebar has been created"""
        app = RecordManagementSystem()

        self.assertIsInstance(app.sidebar, ctk.CTkFrame)
        self.assertIsInstance(app.logo_frame, ctk.CTkFrame)
        self.assertIsInstance(app.logo_label, ctk.CTkLabel)
        self.assertIsInstance(app.subtitle_label, ctk.CTkLabel)
        self.assertIsInstance(app.stats_frame, ctk.CTkFrame)
        self.assertIsInstance(app.stats_title, ctk.CTkLabel)
        self.assertIsInstance(app.stats_count, ctk.CTkLabel)

    def test_buttons_created(self):
        """Test buttons have been created"""
        app = RecordManagementSystem()

        self.assertIn("Client", app.nav_buttons)
        self.assertIn("Airline", app.nav_buttons)
        self.assertIn("Flight", app.nav_buttons)

        self.assertIsInstance(app.add_btn, ctk.CTkButton)

        client_btn = app.nav_buttons["Client"]
        self.assertEqual(app.current_section, "Client")
        self.assertNotEqual(client_btn.cget("fg_color"), "transparent")















