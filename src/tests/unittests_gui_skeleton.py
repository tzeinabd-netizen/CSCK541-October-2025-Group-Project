import os
import sys
import unittest
import customtkinter as ctk

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.gui.gui_skeleton import ClientCard, RecordCard, RecordManager, ClientDialog, RecordManagementSystem, AirlineDialog


class TestGUI(unittest.TestCase):
    """
    Test cases for the Graphical user interface.
    """

   # def test_fetch_first_matching_key(self):



  #  def test_datetime_to_string (self):



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


    # def test_buttons_created




    # def_test_open_dialog
















