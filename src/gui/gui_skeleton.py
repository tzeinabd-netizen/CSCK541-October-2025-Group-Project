"""
Travel Record Management System

Modern GUI built with CustomTkinter for a clean, professional user experience.
This module provides a complete CRUD interface for managing Clients, Airlines, and Flights.

"""

from __future__ import annotations
import os
import sys
from datetime import datetime, time as dt_time
from typing import Dict, Any, Callable, List, Tuple, Optional, Iterable
import random

# CustomTkinter for modern UI components
try:
    import customtkinter as ctk
except ImportError:
    print("Error: customtkinter not installed. Run: pip install customtkinter")
    raise

# Standard tkinter for messagebox and DateEntry
from tkinter import messagebox
try:
    from tkcalendar import DateEntry
except ImportError:
    messagebox.showerror("Error", "tkcalendar not installed. Run: pip install tkcalendar")
    raise

# Ensure src/ is on path so local imports work when running module directly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Local backend modules
from record.record_manager import RecordManager
from data.data_loader import LoadCountries, LoadCities

# ============================================================================
# CUSTOMTKINTER CONFIGURATION
# ============================================================================
# Configure CustomTkinter appearance and theme
ctk.set_appearance_mode("light")  # Options: "light", "dark", "system"
ctk.set_default_color_theme("blue")  # Options: "blue", "green", "dark-blue"

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _get_field(record: Dict, *keys: Iterable[str], default: str = "") -> str:
    """
    Robustly fetch the first matching key value from record dictionary.
    
    This function safely extracts field values from records that may have
    different key naming conventions (e.g., "ID" vs "id", "Name" vs "name").
    
    Args:
        record: Dictionary containing record data
        *keys: Variable number of possible key names to try
        default: Default value to return if no keys are found
        
    Returns:
        String value of the first matching key, or default if none found
    """
    for key in keys:
        if key in record and record[key] is not None:
            return str(record[key])
    return default

def datetime_to_string(dt: datetime) -> str:
    """
    Format datetime object to standardized string format.
    
    Args:
        dt: datetime object to format
        
    Returns:
        Formatted string in "YYYY-MM-DD HH:MM" format
    """
    return dt.strftime("%Y-%m-%d %H:%M")

def call_flexible(fn: Callable, /, *args, **kwargs):
    """
    Attempts to call a function with various combinations of args/kwargs.
    Used to support backend methods with different signatures.
    
    This helper allows the GUI to work with backend methods that may accept
    parameters as positional arguments, keyword arguments, or a mix of both.

    """
    try:
        return fn(*args, **kwargs)
    except TypeError:
        try:
            return fn(**kwargs)
        except TypeError:
            return fn(*args)

# ============================================================================
# CARD COMPONENTS - Reusable UI Cards for Displaying Records
# ============================================================================

class ClientCard(ctk.CTkFrame):
    """
    Card widget displaying a single client record with avatar, contact info, and actions.
    
    This component provides a modern card-based UI for client records, featuring:
    - Avatar with client initials
    - Client name and location information
    - Phone number display
    - Edit and Delete action buttons
    - Hover effects for better interactivity
    """
    
    def __init__(self, master, client_data: dict, on_edit=None, on_delete=None, **kwargs):
        super().__init__(master, **kwargs)
        self.client_data = client_data
        self.on_edit = on_edit
        self.on_delete = on_delete
        
        # Configure card appearance
        self.configure(
            fg_color="#ffffff",
            corner_radius=12,
            border_width=1,
            border_color="#e0e0e0"
        )
        
        # Bind hover events for visual feedback
        self.bind("<Enter>", self._on_hover)
        self.bind("<Leave>", self._on_leave)
        
        self._create_widgets()

    def _create_widgets(self):
        """Build the card's internal widget layout."""
        self.grid_columnconfigure(1, weight=1)
        
        # Avatar with initials
        name = _get_field(self.client_data, "Name", "name", "")
        initials = "".join([n[0].upper() for n in name.split()[:2]]) if name else "??"
        
        # Random color selection for avatar background
        colors = ["#3b82f6", "#8b5cf6", "#06b6d4", "#10b981", "#f59e0b", "#ef4444"]
        avatar_color = random.choice(colors)
        
        self.avatar = ctk.CTkLabel(
            self,
            text=initials,
            width=45,
            height=45,
            corner_radius=22,
            fg_color=avatar_color,
            text_color="white",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.avatar.grid(row=0, column=0, rowspan=2, padx=(15, 12), pady=15)
        
        # Client ID and Name
        client_id = _get_field(self.client_data, "ID", "id", "")
        name_with_id = f"ID: {client_id} | {name}" if client_id else name
        
        self.name_label = ctk.CTkLabel(
            self,
            text=name_with_id,
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#1a1a1a",
            anchor="w"
        )
        self.name_label.grid(row=0, column=1, sticky="sw", pady=(15, 0))
        
        # Location (City, Country)
        city = _get_field(self.client_data, "City", "city", "")
        country = _get_field(self.client_data, "Country", "country", "")
        location = f"{city}, {country}" if city or country else "No location"
        
        self.location_label = ctk.CTkLabel(
            self,
            text=location,
            font=ctk.CTkFont(size=12),
            text_color="#666666",
            anchor="w"
        )
        self.location_label.grid(row=1, column=1, sticky="nw", pady=(2, 15))
        
        # Phone number
        phone = _get_field(self.client_data, "Phone_Number", "phone_number", "phone", "")
        self.phone_label = ctk.CTkLabel(
            self,
            text=phone,
            font=ctk.CTkFont(size=12),
            text_color="#666666",
            width=120
        )
        self.phone_label.grid(row=0, column=2, rowspan=2, padx=10)
        
        # Action buttons frame
        self.actions_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.actions_frame.grid(row=0, column=3, rowspan=2, padx=(5, 15), pady=10)
        
        # Edit button
        self.edit_btn = ctk.CTkButton(
            self.actions_frame,
            text="Edit",
            width=60,
            height=28,
            corner_radius=6,
            fg_color="#f0f0f0",
            hover_color="#e0e0e0",
            text_color="#1a1a1a",
            font=ctk.CTkFont(size=12),
            command=lambda: self.on_edit(self.client_data) if self.on_edit else None
        )
        self.edit_btn.pack(side="left", padx=(0, 5))
        
        # Delete button
        self.delete_btn = ctk.CTkButton(
            self.actions_frame,
            text="Delete",
            width=60,
            height=28,
            corner_radius=6,
            fg_color="transparent",
            hover_color="#dc2626",
            border_width=1,
            border_color="#dc2626",
            text_color="#000000",
            font=ctk.CTkFont(size=12),
            command=lambda: self.on_delete(self.client_data) if self.on_delete else None
        )
        self.delete_btn.pack(side="left")

    def _on_hover(self, event):
        """Handle mouse enter event - subtle visual feedback."""
        self.configure(border_color="#e0e0e0")

    def _on_leave(self, event):
        """Handle mouse leave event - restore default appearance."""
        self.configure(border_color="#e0e0e0")


class RecordCard(ctk.CTkFrame):
    """
    Generic card component for displaying Airlines and Flights.
    
    This component provides a consistent card-based UI for non-client records,
    displaying relevant information and action buttons.

    """
    
    def __init__(self, master, record_data: dict, record_type: str, on_edit=None, on_delete=None, **kwargs):
        super().__init__(master, **kwargs)
        self.record_data = record_data
        self.record_type = record_type
        self.on_edit = on_edit
        self.on_delete = on_delete
        
        # Configure card appearance
        self.configure(
            fg_color="#ffffff",
            corner_radius=12,
            border_width=1,
            border_color="#e0e0e0"
        )
        
        # Bind hover events
        self.bind("<Enter>", self._on_hover)
        self.bind("<Leave>", self._on_leave)
        
        self._create_widgets()

    def _create_widgets(self):
        """Build the card's internal widget layout based on record type."""
        self.grid_columnconfigure(0, weight=1)
        
        # Content frame
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=15)
        
        # Format information text based on record type
        if self.record_type == "Airline":
            company = _get_field(self.record_data, "Company_Name", "company_name", "company", "")
            rec_id = _get_field(self.record_data, "ID", "id", "")
            info_text = f"ID: {rec_id} | {company}"
        else:  # Flight
            client_id = _get_field(self.record_data, "Client_ID", "client_id", "")
            airline_id = _get_field(self.record_data, "Airline_ID", "airline_id", "")
            start = _get_field(self.record_data, "Start_City", "start_city", "")
            end = _get_field(self.record_data, "End_City", "end_city", "")
            date_val = _get_field(self.record_data, "Date", "date", "")
            
            if isinstance(date_val, datetime):
                date_str = date_val.strftime("%Y-%m-%d %H:%M")
            else:
                date_str = str(date_val)
            
            info_text = f"Client {client_id} → Airline {airline_id} | {start} to {end} | {date_str}"
        
        # Information label
        label = ctk.CTkLabel(
            content_frame,
            text=info_text,
            font=ctk.CTkFont(size=14),
            text_color="#1a1a1a",
            anchor="w"
        )
        label.pack(side="left", fill="x", expand=True)
        
        # Action buttons frame
        actions_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        actions_frame.pack(side="right", padx=(10, 0))
        
        # Edit button
        edit_btn = ctk.CTkButton(
            actions_frame,
            text="Edit",
            width=60,
            height=28,
            corner_radius=6,
            fg_color="#f0f0f0",
            hover_color="#e0e0e0",
            text_color="#1a1a1a",
            font=ctk.CTkFont(size=12),
            command=lambda: self.on_edit(self.record_data) if self.on_edit else None
        )
        edit_btn.pack(side="left", padx=(0, 5))
        
        # Delete button
        delete_btn = ctk.CTkButton(
            actions_frame,
            text="Delete",
            width=60,
            height=28,
            corner_radius=6,
            fg_color="transparent",
            hover_color="#dc2626",
            border_width=1,
            border_color="#dc2626",
            text_color="#000000",
            font=ctk.CTkFont(size=12),
            command=lambda: self.on_delete(self.record_data) if self.on_delete else None
        )
        delete_btn.pack(side="left")

    def _on_hover(self, event):
        """Handle mouse enter event - subtle visual feedback."""
        self.configure(border_color="#06b6d4")

    def _on_leave(self, event):
        """Handle mouse leave event - restore default appearance."""
        self.configure(border_color="#e0e0e0")

# ============================================================================
# DIALOG COMPONENTS - Modal Forms for Create/Update Operations
# ============================================================================

class ClientDialog(ctk.CTkToplevel):
    """
    Modal dialog for creating or editing a client record.

    """
    
    def __init__(self, master, client_data: Optional[dict] = None, on_save=None, country_list=None, city_list=None):
        super().__init__(master)
        self.client_data = client_data
        self.on_save = on_save
        self.country_list = country_list or []
        self.city_list = city_list or []
        self.result = None
        
        # Window configuration
        self.title("Edit Client" if client_data else "Create Client")
        self.geometry("450x700")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()
        
        # Center the dialog on the parent window
        self.update_idletasks()
        x = master.winfo_x() + (master.winfo_width() - 450) // 2
        y = master.winfo_y() + (master.winfo_height() - 600) // 2
        self.geometry(f"+{x}+{y}")
        
        self._create_widgets()
        
        # Pre-populate fields if editing
        if client_data:
            self._populate_fields()

    def _create_widgets(self):
        """Build the dialog's form widgets."""


        self.main_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=30, pady=25)
        
        # Title
        title_text = "Edit Client" if self.client_data else "New Client"
        self.title_label = ctk.CTkLabel(
            self.main_frame,
            text=title_text,
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title_label.pack(anchor="w", pady=(0, 20))
        
        # Field configurations: (field_name, label, placeholder)
        self.fields = {}
        field_configs = [
            ("Name", "Full Name", "Enter client name"),
            ("Address_Line_1", "Address Line 1", "Street address"),
            ("Address_Line_2", "Address Line 2", "Apt, suite, etc. (optional)"),
            ("Address_Line_3", "Address Line 3", "Additional address (optional)"),
            ("City", "City", "Enter city"),
            ("State", "State / Province", "Enter state or province"),
            ("Zip_Code", "Zip / Postal Code", "Enter zip code"),
            ("Country", "Country", "Enter country"),
            ("Phone_Number", "Phone Number", "+1 (555) 123-4567"),
        ]
        
        # Create form fields
        for field_name, label, placeholder in field_configs:
            self._create_field(field_name, label, placeholder)
        
        # Buttons frame
        self.buttons_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.buttons_frame.pack(fill="x", pady=(25, 0))
        
        # Cancel button
        self.cancel_btn = ctk.CTkButton(
            self.buttons_frame,
            text="Cancel",
            width=100,
            height=40,
            corner_radius=8,
            fg_color="#474747",
            hover_color="#3b3b3b",
            border_width=1,
            border_color="#3b3b3b",
            command=self.destroy
        )
        self.cancel_btn.pack(side="left")
        
        # Save button
        self.save_btn = ctk.CTkButton(
            self.buttons_frame,
            text="Save Client",
            width=120,
            height=40,
            corner_radius=8,
            fg_color="#06b6d4",
            hover_color="#0891b2",
            command=self._save
        )
        self.save_btn.pack(side="right")

    def _create_field(self, name: str, label: str, placeholder: str):
        """
        Create a form field with label and input widget.
        
        Args:
            name: Field name (used as key in fields dict)
            label: Display label for the field
            placeholder: Placeholder text for text inputs
        """
        # Field label
        label_widget = ctk.CTkLabel(
            self.main_frame,
            text=label,
            font=ctk.CTkFont(size=13),
            text_color="#666666"
        )
        label_widget.pack(anchor="w", pady=(10, 3))
        
        # Create appropriate input widget based on field type
        if name == "Country":
            entry = ctk.CTkComboBox(
                self.main_frame,
                values=self.country_list,
                height=38,
                corner_radius=8,
                border_width=1,
                border_color="#d0d0d0",
                fg_color="#ffffff",
                button_color="#e0e0e0",
                button_hover_color="#d0d0d0"
            )
        elif name == "City":
            entry = ctk.CTkComboBox(
                self.main_frame,
                values=self.city_list,
                height=38,
                corner_radius=8,
                border_width=1,
                border_color="#d0d0d0",
                fg_color="#ffffff",
                button_color="#e0e0e0",
                button_hover_color="#d0d0d0"
            )
        else:
            # Standard text entry
            entry = ctk.CTkEntry(
                self.main_frame,
                placeholder_text=placeholder,
                height=38,
                corner_radius=8,
                border_width=1,
                border_color="#d0d0d0",
                fg_color="#ffffff"
            )
        
        entry.pack(fill="x")
        self.fields[name] = entry

    def _populate_fields(self):
        """Pre-populate form fields with existing client data."""
        if not self.client_data:
            return
        
        # Field mapping: (field_name, [possible_keys])
        field_mapping = {
            "Name": ("Name", "name"),
            "Address_Line_1": ("Address_Line_1", "address_line_1", "address1"),
            "Address_Line_2": ("Address_Line_2", "address_line_2", "address2"),
            "Address_Line_3": ("Address_Line_3", "address_line_3", "address3"),
            "City": ("City", "city"),
            "State": ("State", "state"),
            "Zip_Code": ("Zip_Code", "zip_code", "zip"),
            "Country": ("Country", "country"),
            "Phone_Number": ("Phone_Number", "phone_number", "phone"),
        }
        
        # Populate each field
        for field_name, keys in field_mapping.items():
            value = _get_field(self.client_data, *keys)
            if value and field_name in self.fields:
                if isinstance(self.fields[field_name], ctk.CTkComboBox):
                    self.fields[field_name].set(value)
                else:
                    self.fields[field_name].insert(0, value)

    def _save(self):
        """Collect form data and trigger save callback."""
        data = {}
        for name, entry in self.fields.items():
            if isinstance(entry, ctk.CTkComboBox):
                data[name] = entry.get().strip()
            else:
                data[name] = entry.get().strip()
        
        # Validation
        if not data.get("Name"):
            messagebox.showerror("Validation Error", "Name is required")
            return
        
        # Include ID if editing
        if self.client_data:
            rec_id = self.client_data.get("ID") or self.client_data.get("id")
            if rec_id:
                data["id"] = int(rec_id) if isinstance(rec_id, (int, str)) else rec_id
        
        self.result = data
        if self.on_save:
            self.on_save(data)
        self.destroy()


class AirlineDialog(ctk.CTkToplevel):
    """
    Modal dialog for creating or editing an airline record.

    """
    
    def __init__(self, master, airline_data: Optional[dict] = None, on_save=None):
        super().__init__(master)
        self.airline_data = airline_data
        self.on_save = on_save
        self.result = None
        
        # Window configuration
        self.title("Edit Airline" if airline_data else "Create Airline")
        self.geometry("400x250")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()
        
        # Center the dialog
        self.update_idletasks()
        x = master.winfo_x() + (master.winfo_width() - 400) // 2
        y = master.winfo_y() + (master.winfo_height() - 200) // 2
        self.geometry(f"+{x}+{y}")
        
        self._create_widgets()
        
        # Pre-populate if editing
        if airline_data:
            self._populate_fields()

    def _create_widgets(self):
        """Build the dialog's form widgets."""
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=30, pady=25)
        
        # Title
        title_text = "Edit Airline" if self.airline_data else "New Airline"
        self.title_label = ctk.CTkLabel(
            self.main_frame,
            text=title_text,
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title_label.pack(anchor="w", pady=(0, 20))
        
        # Company name label
        ctk.CTkLabel(
            self.main_frame,
            text="Company Name",
            font=ctk.CTkFont(size=13),
            text_color="#888888"
        ).pack(anchor="w", pady=(0, 3))
        
        # Company name entry
        self.company_entry = ctk.CTkEntry(
            self.main_frame,
            placeholder_text="Enter airline company name",
            height=38,
            corner_radius=8,
            border_width=1,
            border_color="#d0d0d0",
            fg_color="#ffffff"
        )
        self.company_entry.pack(fill="x", pady=(0, 20))
        
        # Buttons frame
        self.buttons_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.buttons_frame.pack(fill="x")
        
        # Cancel button
        self.cancel_btn = ctk.CTkButton(
            self.buttons_frame,
            text="Cancel",
            width=100,
            height=40,
            corner_radius=8,
            fg_color="#474747",
            hover_color="#3b3b3b",
            border_width=1,
            border_color="#3b3b3b",
            command=self.destroy
        )
        self.cancel_btn.pack(side="left")
        
        # Save button
        self.save_btn = ctk.CTkButton(
            self.buttons_frame,
            text="Save Airline",
            width=120,
            height=40,
            corner_radius=8,
            fg_color="#06b6d4",
            hover_color="#0891b2",
            command=self._save
        )
        self.save_btn.pack(side="right")

    def _populate_fields(self):
        """Pre-populate form fields with existing airline data."""
        if self.airline_data:
            company = _get_field(self.airline_data, "Company_Name", "company_name", "company", "")
            if company:
                self.company_entry.insert(0, company)

    def _save(self):
        """Collect form data and trigger save callback."""
        company_name = self.company_entry.get().strip()
        
        # Validation
        if not company_name:
            messagebox.showerror("Validation Error", "Company name is required")
            return
        
        self.result = {"Company_Name": company_name}
        
        # Include ID if editing
        if self.airline_data:
            rec_id = self.airline_data.get("ID") or self.airline_data.get("id")
            if rec_id:
                self.result["id"] = int(rec_id) if isinstance(rec_id, (int, str)) else rec_id
        
        if self.on_save:
            self.on_save(self.result)
        self.destroy()

# ============================================================================
# MAIN APPLICATION CLASS
# ============================================================================

class RecordManagementSystem(ctk.CTk):
    """
    Main CustomTkinter application class for the Travel Record Management System.
    
    This class provides the complete GUI interface with:
    - Sidebar navigation for switching between Clients, Airlines, and Flights
    - Card-based record display with search functionality
    - CRUD operations (Create, Read, Update, Delete) for all record types
    - Modern, responsive UI built with CustomTkinter

    """
    
    def __init__(self) -> None:
        super().__init__()
        
        # Initialize backend RecordManager
        self.record_manager = RecordManager()
        
        # Load country and city lists for dropdowns
        try:
            self.country_list = LoadCountries()
            self.city_list = LoadCities()
        except Exception:
            # Fallback if data loading fails
            self.country_list = ["United States", "Canada", "United Kingdom"]
            self.city_list = ["New York", "Toronto", "London"]
        
        # Window configuration
        self.title("Travel Record Management System")
        self.geometry("1100x700")
        self.minsize(900, 600)
        
        # Track current section for navigation
        self.current_section = "Client"
        
        # Build the UI
        self._create_layout()
        
        # Load initial records
        self._refresh_records()

    def _create_layout(self):
        """
        Create the main application layout with sidebar and content area.
        
        The layout consists of:
        - Left sidebar: Navigation and statistics
        - Right content area: Section title, search, and record cards
        """
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self._create_sidebar()
        self._create_main_content()

    def _create_sidebar(self):
        """
        Create the left sidebar navigation panel.
        
        The sidebar includes:
        - Application logo and title
        - Navigation buttons for Clients, Airlines, and Flights
        - Statistics panel showing total record count
        """
        self.sidebar = ctk.CTkFrame(
            self,
            width=220,
            corner_radius=0,
            fg_color="#f5f5f5"
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        
        # Logo section
        self.logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.logo_frame.pack(fill="x", padx=20, pady=(25, 30))
        
        self.logo_label = ctk.CTkLabel(
            self.logo_frame,
            text="✈ TravelApp",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#06b6d4"
        )
        self.logo_label.pack(anchor="w")
        
        self.subtitle_label = ctk.CTkLabel(
            self.logo_frame,
            text="Record Management",
            font=ctk.CTkFont(size=11),
            text_color="#888888"
        )
        self.subtitle_label.pack(anchor="w")
        
        # Navigation buttons
        self.nav_buttons = {}
        nav_items = [
            ("Client", "👥  Clients"),
            ("Airline", "🛫  Airlines"),
            ("Flight", "✈️  Flights"),
        ]
        
        for section_id, label in nav_items:
            btn = ctk.CTkButton(
                self.sidebar,
                text=label,
                anchor="w",
                height=45,
                corner_radius=10,
                font=ctk.CTkFont(size=14),
                fg_color="transparent" if section_id != "Client" else "#06b6d4",
                text_color="white" if section_id == "Client" else "#666666",
                hover_color="#e0e0e0" if section_id != "Client" else "#0891b2",
                command=lambda s=section_id: self._switch_section(s)
            )
            btn.pack(fill="x", padx=15, pady=3)
            self.nav_buttons[section_id] = btn
        
        # Statistics section
        self.stats_frame = ctk.CTkFrame(
            self.sidebar,
            fg_color="#ffffff",
            corner_radius=12
        )
        self.stats_frame.pack(fill="x", padx=15, pady=15, side="bottom")
        
        self.stats_title = ctk.CTkLabel(
            self.stats_frame,
            text="Total Records",
            font=ctk.CTkFont(size=11),
            text_color="#666666"
        )
        self.stats_title.pack(anchor="w", padx=15, pady=(12, 2))
        
        self.stats_count = ctk.CTkLabel(
            self.stats_frame,
            text="0",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#06b6d4"
        )
        self.stats_count.pack(anchor="w", padx=15, pady=(0, 12))

    def _create_main_content(self):
        """
        Create the main content area with header, search, and record display.
        
        The content area includes:
        - Section title (changes based on current section)
        - Search bar for filtering records
        - Add New button for creating records
        - Scrollable container for record cards
        """
        self.main_frame = ctk.CTkFrame(self, fg_color="#ffffff", corner_radius=0)
        self.main_frame.grid(row=0, column=1, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)
        
        # Header section
        self.header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent", height=80)
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=30, pady=(25, 15))
        self.header_frame.grid_columnconfigure(1, weight=1)
        
        # Section title
        self.section_title = ctk.CTkLabel(
            self.header_frame,
            text="Client Records",
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color="#1a1a1a"
        )
        self.section_title.grid(row=0, column=0, sticky="w")
        
        # Search bar and add button frame
        self.search_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.search_frame.grid(row=0, column=1, sticky="e")
        
        # Search entry
        self.search_entry = ctk.CTkEntry(
            self.search_frame,
            placeholder_text="🔍 Search records...",
            width=250,
            height=40,
            corner_radius=10,
            border_width=1,
            border_color="#d0d0d0",
            fg_color="#ffffff"
        )
        self.search_entry.pack(side="left", padx=(0, 12))
        self.search_entry.bind("<KeyRelease>", self._on_search)
        
        # Add New button
        self.add_btn = ctk.CTkButton(
            self.search_frame,
            text="+ Add New",
            width=110,
            height=40,
            corner_radius=10,
            fg_color="#06b6d4",
            hover_color="#0891b2",
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self._add_record
        )
        self.add_btn.pack(side="left")
        
        # Records container (scrollable)
        self.records_container = ctk.CTkScrollableFrame(
            self.main_frame,
            fg_color="transparent",
            scrollbar_button_color="#3b3b3b",
            scrollbar_button_hover_color="#4b4b4b"
        )
        self.records_container.grid(row=1, column=0, sticky="nsew", padx=30, pady=(0, 20))
        self.records_container.grid_columnconfigure(0, weight=1)

    def _switch_section(self, section: str):
        """
        Switch to a different section (Client, Airline, or Flight).
        
        Args:
            section: Section identifier ("Client", "Airline", or "Flight")
        """
        self.current_section = section
        
        # Update navigation button states
        for section_id, btn in self.nav_buttons.items():
            if section_id == section:
                btn.configure(fg_color="#06b6d4", text_color="white", hover_color="#0891b2")
            else:
                btn.configure(fg_color="transparent", text_color="#666666", hover_color="#e0e0e0")
        
        # Update section title
        titles = {
            "Client": "Client Records",
            "Airline": "Airline Records",
            "Flight": "Flight Records"
        }
        self.section_title.configure(text=titles.get(section, "Records"))
        
        # Clear search and refresh records
        self.search_entry.delete(0, "end")
        self._refresh_records()

    def _refresh_records(self, filter_text: str = ""):
        """
        Refresh the records display with optional filtering.
        
        This method:
        1. Clears existing record cards
        2. Fetches records from the backend
        3. Applies search filter if provided
        4. Creates and displays record cards
        5. Updates statistics
        
        Args:
            filter_text: Optional search term to filter records
        """
        # Clear existing cards
        for widget in self.records_container.winfo_children():
            widget.destroy()
        
        # Get current section's records
        records = self.record_manager.GetAllRecords(self.current_section)
        
        # Apply search filter if provided
        if filter_text:
            filter_lower = filter_text.lower()
            records = [
                r for r in records
                if any(filter_lower in str(v).lower() for v in r.values() if v is not None)
            ]
        
        # Create and display record cards
        for record in records:
            if self.current_section == "Client":
                card = ClientCard(
                    self.records_container,
                    record,
                    on_edit=self._edit_record,
                    on_delete=self._delete_record
                )
            else:
                card = RecordCard(
                    self.records_container,
                    record,
                    self.current_section,
                    on_edit=self._edit_record,
                    on_delete=self._delete_record
                )
            card.pack(fill="x", pady=(0, 10))
        
        # Update statistics
        total = (
            len(self.record_manager.GetAllRecords("Client")) +
            len(self.record_manager.GetAllRecords("Airline")) +
            len(self.record_manager.GetAllRecords("Flight"))
        )
        self.stats_count.configure(text=str(total))

    def _on_search(self, event):
        """
        Handle search input changes - filters records in real-time.
        
        Args:
            event: Key release event from search entry
        """
        filter_text = self.search_entry.get()
        self._refresh_records(filter_text)

    def _add_record(self):
        """Open dialog to add a new record based on current section."""
        if self.current_section == "Client":
            dialog = ClientDialog(
                self,
                on_save=self._save_new_client,
                country_list=self.country_list,
                city_list=self.city_list
            )
            self.wait_window(dialog)
        elif self.current_section == "Airline":
            dialog = AirlineDialog(self, on_save=self._save_new_airline)
            self.wait_window(dialog)
        elif self.current_section == "Flight":
            self._open_flight_dialog()

    def _save_new_client(self, data: dict):
        """
        Save a new client record to the backend.

        """
        try:
            self.record_manager.CreateClient(
                data.get("Name", ""),
                data.get("Address_Line_1", ""),
                data.get("Address_Line_2", ""),
                data.get("Address_Line_3", ""),
                data.get("City", ""),
                data.get("State", ""),
                data.get("Zip_Code", ""),
                data.get("Country", ""),
                data.get("Phone_Number", "")
            )
            messagebox.showinfo("Success", "Client created successfully!")
            self._refresh_records()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create client: {e}")

    def _save_new_airline(self, data: dict):
        """
        Save a new airline record to the backend.
        
        Args:
            data: Dictionary containing airline form data
        """
        try:
            self.record_manager.CreateAirline(data.get("Company_Name", ""))
            messagebox.showinfo("Success", "Airline created successfully!")
            self._refresh_records()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create airline: {e}")

    def _edit_record(self, record: dict):
        """
        Open dialog to edit an existing record.
        
        Args:
            record: Dictionary containing the record data to edit
        """
        if self.current_section == "Client":
            dialog = ClientDialog(
                self,
                client_data=record,
                on_save=self._save_edited_client,
                country_list=self.country_list,
                city_list=self.city_list
            )
            self.wait_window(dialog)
        elif self.current_section == "Airline":
            dialog = AirlineDialog(self, airline_data=record, on_save=self._save_edited_airline)
            self.wait_window(dialog)
        elif self.current_section == "Flight":
            self._open_flight_dialog(record)

    def _save_edited_client(self, data: dict):
        """
        Save edited client record to the backend.
        
        Args:
            data: Dictionary containing updated client form data
        """
        try:
            rec_id = data.get("id")
            if not rec_id:
                messagebox.showerror("Error", "Client ID not found")
                return
            
            self.record_manager.UpdateClient(
                int(rec_id),
                Name=data.get("Name", ""),
                Address_Line_1=data.get("Address_Line_1", ""),
                Address_Line_2=data.get("Address_Line_2", ""),
                Address_Line_3=data.get("Address_Line_3", ""),
                City=data.get("City", ""),
                State=data.get("State", ""),
                Zip_Code=data.get("Zip_Code", ""),
                Country=data.get("Country", ""),
                Phone_Number=data.get("Phone_Number", "")
            )
            messagebox.showinfo("Success", "Client updated successfully!")
            self._refresh_records()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update client: {e}")

    def _save_edited_airline(self, data: dict):
        """
        Save edited airline record to the backend.

        """
        try:
            rec_id = data.get("id")
            if not rec_id:
                messagebox.showerror("Error", "Airline ID not found")
                return
            
            self.record_manager.UpdateAirline(int(rec_id), data.get("Company_Name", ""))
            messagebox.showinfo("Success", "Airline updated successfully!")
            self._refresh_records()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update airline: {e}")

    def _delete_record(self, record: dict):
        """
        Delete a record with confirmation dialog.

        """
        # Flight records use Client_ID and Airline_ID instead of ID
        if self.current_section == "Flight":
            client_id = record.get("Client_ID") or record.get("client_id")
            airline_id = record.get("Airline_ID") or record.get("airline_id")
            
            if not client_id or not airline_id:
                messagebox.showerror("Error", "Flight record IDs not found")
                return
            
            # Get flight info for confirmation message
            start_city = _get_field(record, "Start_City", "start_city", "")
            end_city = _get_field(record, "End_City", "end_city", "")
            flight_info = f"Flight from {start_city} to {end_city}" if start_city and end_city else "this flight"
            
            # Confirm deletion
            if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{flight_info}'?"):
                try:
                    self.record_manager.DeleteFlight(int(client_id), int(airline_id))
                    messagebox.showinfo("Success", "Flight deleted successfully!")
                    self._refresh_records()
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to delete flight: {e}")
        else:
            # Client and Airline records use ID
            rec_id = record.get("ID") or record.get("id")
            if not rec_id:
                messagebox.showerror("Error", "Record ID not found")
                return
            
            # Get record name for confirmation message
            name = _get_field(record, "Name", "name", "Company_Name", "company_name", "this record")
            
            # Confirm deletion
            if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{name}'?"):
                try:
                    self.record_manager.DeleteRecord(int(rec_id), self.current_section)
                    messagebox.showinfo("Success", "Record deleted successfully!")
                    self._refresh_records()
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to delete record: {e}")

    def _pick_datetime(self, initial_datetime: Optional[datetime] = None) -> Optional[datetime]:
        """
        Open a popup window for selecting date and time.
        
        Uses standard tkinter for DateEntry compatibility.
        
        Args:
            initial_datetime: Optional datetime to pre-select
            
        Returns:
            Selected datetime object, or None if cancelled
        """
        import tkinter as tk
        from tkinter import ttk
        
        result = {"value": None}
        
        def submit():
            """Handle datetime selection submission."""
            try:
                date = date_entry.get_date()
                hour = int(hour_spin.get())
                minute = int(min_spin.get())
                
                if not (0 <= hour < 24 and 0 <= minute < 60):
                    raise ValueError("Time out of range")
                
                time_obj = dt_time(hour=hour, minute=minute)
                result["value"] = datetime.combine(date, time_obj)
                picker_window.destroy()
            except (ValueError, AttributeError) as e:
                messagebox.showerror("Error", f"Invalid date/time: {e}")
        
        # Create picker window using standard tkinter
        picker_window = tk.Toplevel(self)
        picker_window.title("Date-Time Picker")
        picker_window.geometry("280x250")
        picker_window.configure(bg="#ffffff")
        picker_window.transient(self)
        picker_window.grab_set()
        
        # Center the window
        picker_window.update_idletasks()
        x = (picker_window.winfo_screenwidth() // 2) - (picker_window.winfo_width() // 2)
        y = (picker_window.winfo_screenheight() // 2) - (picker_window.winfo_height() // 2)
        picker_window.geometry(f"+{x}+{y}")
        
        # Date picker
        tk.Label(picker_window, text="Select Date:", bg="#ffffff", fg="#1a1a1a", font=("Arial", 11)).pack(pady=5)
        date_entry = DateEntry(
            picker_window,
            width=12,
            background='darkblue',
            foreground='white',
            date_pattern='yyyy-mm-dd'
        )
        date_entry.pack(pady=5)
        
        # Time picker
        tk.Label(picker_window, text="Select Time (HH:MM):", bg="#ffffff", fg="#1a1a1a", font=("Arial", 11)).pack(pady=5)
        time_frame = tk.Frame(picker_window, bg="#ffffff")
        time_frame.pack(pady=5)
        
        hour_spin = tk.Spinbox(time_frame, from_=0, to=23, wrap=True, width=3, format="%02.0f", font=("Arial", 11))
        hour_spin.pack(side="left", padx=2)
        tk.Label(time_frame, text=":", bg="#ffffff", fg="#1a1a1a", font=("Arial", 11)).pack(side="left")
        min_spin = tk.Spinbox(time_frame, from_=0, to=59, wrap=True, width=3, format="%02.0f", font=("Arial", 11))
        min_spin.pack(side="left", padx=2)
        
        # Pre-fill if editing
        if initial_datetime:
            date_entry.set_date(initial_datetime.date())
            hour_spin.delete(0, "end")
            hour_spin.insert(0, f"{initial_datetime.hour:02d}")
            min_spin.delete(0, "end")
            min_spin.insert(0, f"{initial_datetime.minute:02d}")
        
        # Buttons
        button_frame = tk.Frame(picker_window, bg="#ffffff")
        button_frame.pack(pady=15)
        tk.Button(button_frame, text="OK", command=submit, width=10, bg="#06b6d4", fg="white", font=("Arial", 10)).pack(side="left", padx=5)
        tk.Button(button_frame, text="Cancel", command=picker_window.destroy, width=10, bg="#e0e0e0", fg="#1a1a1a", font=("Arial", 10)).pack(side="left", padx=5)
        
        picker_window.wait_window()
        return result["value"]

    def _open_flight_dialog(self, record: Optional[dict] = None):
        """
        Open flight creation/editing dialog.
        
        This dialog handles the more complex flight record with:
        - Client ID and Airline ID selection
        - Date and time picker
        - Start and end city selection

        """
        dialog = ctk.CTkToplevel(self)
        dialog.title("Edit Flight" if record else "Create Flight")
        dialog.geometry("450x550")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - 450) // 2
        y = self.winfo_y() + (self.winfo_height() - 400) // 2
        dialog.geometry(f"+{x}+{y}")
        
        main_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=30, pady=25)
        
        # Title
        title_text = "Edit Flight" if record else "New Flight"
        ctk.CTkLabel(
            main_frame,
            text=title_text,
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(anchor="w", pady=(0, 20))
        
        fields = {}
        date_value_storage = {"value": None}
        
        # Client ID field
        ctk.CTkLabel(main_frame, text="Client ID", font=ctk.CTkFont(size=13), text_color="#666666").pack(anchor="w", pady=(10, 3))
        client_entry = ctk.CTkEntry(main_frame, height=38, corner_radius=8, border_width=1, border_color="#d0d0d0", fg_color="#ffffff")
        client_entry.pack(fill="x")
        fields["Client_ID"] = client_entry
        
        # Airline ID field
        ctk.CTkLabel(main_frame, text="Airline ID", font=ctk.CTkFont(size=13), text_color="#666666").pack(anchor="w", pady=(10, 3))
        airline_entry = ctk.CTkEntry(main_frame, height=38, corner_radius=8, border_width=1, border_color="#d0d0d0", fg_color="#ffffff")
        airline_entry.pack(fill="x")
        fields["Airline_ID"] = airline_entry
        
        # Date/Time picker
        ctk.CTkLabel(main_frame, text="Date & Time", font=ctk.CTkFont(size=13), text_color="#666666").pack(anchor="w", pady=(10, 3))
        date_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        date_frame.pack(fill="x")
        
        date_display = ctk.CTkEntry(date_frame, width=200, state="readonly", height=38, corner_radius=8, border_width=1, border_color="#d0d0d0", fg_color="#ffffff")
        date_display.pack(side="left", padx=(0, 10))
        
        def open_picker():
            """Open the datetime picker dialog."""
            selected = self._pick_datetime(date_value_storage.get("value"))
            if selected:
                date_value_storage["value"] = selected
                date_display.configure(state="normal")
                date_display.delete(0, "end")
                date_display.insert(0, selected.strftime("%Y-%m-%d %H:%M"))
                date_display.configure(state="readonly")
        
        ctk.CTkButton(date_frame, text="Pick Date/Time", command=open_picker, width=120).pack(side="left")
        fields["Date"] = date_display
        
        # Start City field
        ctk.CTkLabel(main_frame, text="Start City", font=ctk.CTkFont(size=13), text_color="#666666").pack(anchor="w", pady=(10, 3))
        start_city = ctk.CTkComboBox(main_frame, values=self.city_list, height=38, corner_radius=8, border_width=1, border_color="#d0d0d0", fg_color="#ffffff", button_color="#e0e0e0", button_hover_color="#d0d0d0")
        start_city.pack(fill="x")
        fields["Start_City"] = start_city
        
        # End City field
        ctk.CTkLabel(main_frame, text="End City", font=ctk.CTkFont(size=13), text_color="#666666").pack(anchor="w", pady=(10, 3))
        end_city = ctk.CTkComboBox(main_frame, values=self.city_list, height=38, corner_radius=8, border_width=1, border_color="#d0d0d0", fg_color="#ffffff", button_color="#e0e0e0", button_hover_color="#d0d0d0")
        end_city.pack(fill="x")
        fields["End_City"] = end_city
        
        # Pre-fill fields if editing
        if record:
            client_id = _get_field(record, "Client_ID", "client_id", "")
            airline_id = _get_field(record, "Airline_ID", "airline_id", "")
            if client_id:
                client_entry.insert(0, str(client_id))
            if airline_id:
                airline_entry.insert(0, str(airline_id))
            
            date_val = _get_field(record, "Date", "date", "")
            if isinstance(date_val, datetime):
                date_value_storage["value"] = date_val
                date_display.configure(state="normal")
                date_display.insert(0, date_val.strftime("%Y-%m-%d %H:%M"))
                date_display.configure(state="readonly")
            elif date_val:
                try:
                    parsed = datetime.fromisoformat(str(date_val))
                    date_value_storage["value"] = parsed
                    date_display.configure(state="normal")
                    date_display.insert(0, parsed.strftime("%Y-%m-%d %H:%M"))
                    date_display.configure(state="readonly")
                except:
                    pass
            
            start_city.set(_get_field(record, "Start_City", "start_city", ""))
            end_city.set(_get_field(record, "End_City", "end_city", ""))
        
        # Buttons frame
        buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        buttons_frame.pack(fill="x", pady=(20, 0))
        
        def save_flight():
            """Save flight data to backend."""
            try:
                client_id = int(fields["Client_ID"].get())
                airline_id = int(fields["Airline_ID"].get())
                date_value = date_value_storage.get("value")
                
                if not date_value:
                    messagebox.showerror("Error", "Please select a date and time")
                    return
                
                start = fields["Start_City"].get()
                end = fields["End_City"].get()
                
                if record:
                    self.record_manager.UpdateFlight(client_id, airline_id, Date=date_value, Start_City=start, End_City=end)
                    messagebox.showinfo("Success", "Flight updated successfully!")
                else:
                    self.record_manager.CreateFlight(client_id, airline_id, date_value, start, end)
                    messagebox.showinfo("Success", "Flight created successfully!")
                
                dialog.destroy()
                self._refresh_records()
            except ValueError:
                messagebox.showerror("Error", "Client ID and Airline ID must be integers")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save flight: {e}")
        
        # Cancel and Save buttons
        ctk.CTkButton(buttons_frame, text="Cancel", command=dialog.destroy, width=100, height=40, corner_radius=8, fg_color="#474747", border_width=1, border_color="#d0d0d0", text_color="white").pack(side="left")
        ctk.CTkButton(buttons_frame, text="Save Flight", command=save_flight, width=120, height=40, corner_radius=8, fg_color="#06b6d4", hover_color="#0891b2").pack(side="right")
        
        dialog.wait_window()

# ============================================================================
# ENTRY POINT
# ============================================================================

def main() -> None:
    """
    Create and run the GUI application.
    
    This is the main entry point for the application. It initializes
    the CustomTkinter window and starts the event loop.
    """
    app = RecordManagementSystem()
    app.mainloop()

if __name__ == "__main__":
    main()
