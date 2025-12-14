"""
Travel Record Management System

Modern GUI built with CustomTkinter for a clean, professional user experience.
This module provides a complete CRUD interface for managing Clients, Airlines, and Flights.

"""

from __future__ import annotations
import os
import sys
from datetime import datetime, date, time as dt_time, time
from typing import Dict, Any, Callable, List, Tuple, Optional, Iterable
import random
import re
import tkinter as tk 
from tkinter import messagebox, ttk

# CustomTkinter for modern UI components
try:
    import customtkinter as ctk
except ImportError:
    print("Error: customtkinter not installed. Run: pip install customtkinter")
    raise

# Standard tkinter for messagebox and DateEntry
try:
    from tkcalendar import DateEntry
except ImportError:
    messagebox.showerror("Error", "tkcalendar not installed. Run: pip install tkcalendar")
    raise

# Ensure src/ is on path so local imports work when running module directly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Local backend modules (Assuming these modules exist)
from record.record_manager import RecordManager
from data.data_loader import LoadCountries, LoadCities

# ============================================================================
# CUSTOMTKINTER CONFIGURATION
# ============================================================================
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# ============================================================================
# HELPER FUNCTIONS 
# ============================================================================

def _get_field(record: Dict, *keys: Iterable[str], default: str = "") -> str:
    """Robustly fetch the first matching key value from record dictionary."""
    for key in keys:
        if key in record and record[key] is not None:
            return str(record[key])
    return default

def datetime_to_string(dt: datetime) -> str:
    """Format datetime object to standardized string format."""
    return dt.strftime("%Y-%m-%d %H:%M")

def call_flexible(fn: Callable, /, *args, **kwargs):
    """Attempts to call a function with various combinations of args/kwargs."""
    try:
        return fn(*args, **kwargs)
    except TypeError:
        try:
            return fn(**kwargs)
        except TypeError:
            return fn(*args)

def _parse_id_from_dropdown(dropdown_value: str) -> Optional[int]:
    """
    Extracts the integer ID from a dropdown string formatted as "Name (ID)".
    """
    match = re.search(r'\((\d+)\)$', dropdown_value)
    if match:
        try:
            return int(match.group(1))
        except ValueError:
            return None
    return None

def _format_client_name(client_record: dict) -> str:
    """Format client record for display in a dropdown."""
    client_id = _get_field(client_record, "ID", "id", default="?")
    name = _get_field(client_record, "Name", "name", default="Unknown Client")
    return f"{name} ({client_id})"

def _format_airline_name(airline_record: dict) -> str:
    """Format airline record for display in a dropdown."""
    airline_id = _get_field(airline_record, "ID", "id", default="?")
    company = _get_field(airline_record, "Company_Name", "company_name", "company", default="Unknown Airline")
    return f"{company} ({airline_id})"

def build_datetime_from_ui(selected_date: date, hour_str: str, minute_str: str, ampm: str) -> datetime:
    """
    Converts DateEntry and 12-hour time components into a single 24-hour datetime object.
    """
    hour, minute = int(hour_str or 0), int(minute_str or 0)
    
    # 12-hour to 24-hour conversion logic
    if ampm.upper() == "PM" and hour != 12:
        hour += 12
    elif ampm.upper() == "AM" and hour == 12:
        hour = 0
        
    return datetime.combine(selected_date, time(hour=hour, minute=minute))

# ============================================================================
# CARD COMPONENTS
# ============================================================================

class ClientCard(ctk.CTkFrame):
    def __init__(self, master, client_data: dict, on_edit=None, on_delete=None, **kwargs):
        super().__init__(master, **kwargs)
        self.client_data = client_data
        self.on_edit = on_edit
        self.on_delete = on_delete
        
        self.configure(fg_color="#ffffff", corner_radius=12, border_width=1, border_color="#e0e0e0")
        self.bind("<Enter>", self._on_hover)
        self.bind("<Leave>", self._on_leave)
        self._create_widgets()

    def _create_widgets(self):
        self.grid_columnconfigure(1, weight=1)
        
        name = _get_field(self.client_data, "Name", "name", "")
        initials = "".join([n[0].upper() for n in name.split()[:2]]) if name else "??"
        colors = ["#3b82f6", "#8b5cf6", "#06b6d4", "#10b981", "#f59e0b", "#ef4444"]
        avatar_color = random.choice(colors)
        
        self.avatar = ctk.CTkLabel(
            self, text=initials, width=45, height=45, corner_radius=22, fg_color=avatar_color, 
            text_color="white", font=ctk.CTkFont(size=16, weight="bold")
        )
        self.avatar.grid(row=0, column=0, rowspan=2, padx=(15, 12), pady=15)
        
        client_id = _get_field(self.client_data, "ID", "id", "")
        name_with_id = f"ID: {client_id} | {name}" if client_id else name
        
        self.name_label = ctk.CTkLabel(
            self, text=name_with_id, font=ctk.CTkFont(size=15, weight="bold"), 
            text_color="#1a1a1a", anchor="w"
        )
        self.name_label.grid(row=0, column=1, sticky="sw", pady=(15, 0))
        
        city = _get_field(self.client_data, "City", "city", "")
        country = _get_field(self.client_data, "Country", "country", "")
        location = f"{city}, {country}" if city or country else "No location"
        
        self.location_label = ctk.CTkLabel(
            self, text=location, font=ctk.CTkFont(size=12), text_color="#666666", anchor="w"
        )
        self.location_label.grid(row=1, column=1, sticky="nw", pady=(2, 15))
        
        phone = _get_field(self.client_data, "Phone_Number", "phone_number", "phone", "")
        self.phone_label = ctk.CTkLabel(
            self, text=phone, font=ctk.CTkFont(size=12), text_color="#666666", width=120
        )
        self.phone_label.grid(row=0, column=2, rowspan=2, padx=10)
        
        self.actions_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.actions_frame.grid(row=0, column=3, rowspan=2, padx=(5, 15), pady=10)
        
        self.edit_btn = ctk.CTkButton(
            self.actions_frame, text="Edit", width=60, height=28, corner_radius=6, 
            fg_color="#f0f0f0", hover_color="#e0e0e0", text_color="#1a1a1a", 
            font=ctk.CTkFont(size=12), command=lambda: self.on_edit(self.client_data) if self.on_edit else None
        )
        self.edit_btn.pack(side="left", padx=(0, 5))
        
        self.delete_btn = ctk.CTkButton(
            self.actions_frame, text="Delete", width=60, height=28, corner_radius=6, 
            fg_color="transparent", hover_color="#dc2626", border_width=1, 
            border_color="#dc2626", text_color="#dc2626", font=ctk.CTkFont(size=12), 
            command=lambda: self.on_delete(self.client_data) if self.on_delete else None
        )
        self.delete_btn.pack(side="left")

    def _on_hover(self, event):
        self.configure(border_color="#06b6d4")

    def _on_leave(self, event):
        self.configure(border_color="#e0e0e0")

class FlightCard(ctk.CTkFrame):
    """NEW Card component for detailed Flight record display."""
    def __init__(self, master, flight_data: dict, on_edit=None, on_delete=None, **kwargs):
        super().__init__(master, **kwargs)
        self.flight_data = flight_data
        self.on_edit = on_edit
        self.on_delete = on_delete
        
        self.configure(fg_color="#ffffff", corner_radius=12, border_width=1, border_color="#e0e0e0")
        self.bind("<Enter>", self._on_hover)
        self.bind("<Leave>", self._on_leave)
        self._create_widgets()

    def _create_widgets(self):
        self.grid_columnconfigure(1, weight=1)
        
        # 1. Avatar (Fixed '✈' icon)
        initials = "✈"
        avatar_color = "#06b6d4" 
        
        self.avatar = ctk.CTkLabel(
            self, text=initials, width=45, height=45, corner_radius=22, fg_color=avatar_color, 
            text_color="white", font=ctk.CTkFont(size=20, weight="bold")
        )
        self.avatar.grid(row=0, column=0, rowspan=2, padx=(15, 12), pady=15)
        
        # 2. Main Title (Route and Client Name)
        # ENHANCEMENT: Use Client_Name instead of Client_ID
        client_name = _get_field(self.flight_data, "Client_Name", default="Unknown Client")
        start = _get_field(self.flight_data, "Start_City", "start_city", "")
        end = _get_field(self.flight_data, "End_City", "end_city", "")
        route_text = f"Client: {client_name} | {start} → {end}"
        
        self.route_label = ctk.CTkLabel(
            self, text=route_text, font=ctk.CTkFont(size=15, weight="bold"), 
            text_color="#1a1a1a", anchor="w"
        )
        self.route_label.grid(row=0, column=1, sticky="sw", pady=(15, 0))
        
        # 3. Details (Date/Time and Airline Name)
        # ENHANCEMENT: Use Airline_Company_Name instead of Airline_ID
        date_val = _get_field(self.flight_data, "Date", "date", "")
        airline_name = _get_field(self.flight_data, "Airline_Company_Name", default="Unknown Airline")
        
        if isinstance(date_val, datetime):
            date_str = date_val.strftime("%Y-%m-%d %H:%M")
        else:
            date_str = str(date_val)
            
        detail_text = f"Airline: {airline_name} | Departure: {date_str}"
        
        self.detail_label = ctk.CTkLabel(
            self, text=detail_text, font=ctk.CTkFont(size=12), text_color="#666666", anchor="w"
        )
        self.detail_label.grid(row=1, column=1, sticky="nw", pady=(2, 15))
        
        # 4. Action Buttons
        self.actions_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.actions_frame.grid(row=0, column=3, rowspan=2, padx=(5, 15), pady=10)
        
        self.edit_btn = ctk.CTkButton(
            self.actions_frame, text="Edit", width=60, height=28, corner_radius=6, 
            fg_color="#f0f0f0", hover_color="#e0e0e0", text_color="#1a1a1a", 
            font=ctk.CTkFont(size=12), command=lambda: self.on_edit(self.flight_data) if self.on_edit else None
        )
        self.edit_btn.pack(side="left", padx=(0, 5))
        
        self.delete_btn = ctk.CTkButton(
            self.actions_frame, text="Delete", width=60, height=28, corner_radius=6, 
            fg_color="transparent", hover_color="#dc2626", border_width=1, 
            border_color="#dc2626", text_color="#dc2626", font=ctk.CTkFont(size=12), 
            command=lambda: self.on_delete(self.flight_data) if self.on_delete else None
        )
        self.delete_btn.pack(side="left")

    def _on_hover(self, event):
        self.configure(border_color="#06b6d4")

    def _on_leave(self, event):
        self.configure(border_color="#e0e0e0")


class RecordCard(ctk.CTkFrame):
    """Handles Airline records only."""
    def __init__(self, master, record_data: dict, record_type: str, on_edit=None, on_delete=None, **kwargs):
        super().__init__(master, **kwargs)
        self.record_data = record_data
        self.record_type = record_type
        self.on_edit = on_edit
        self.on_delete = on_delete
        
        self.configure(fg_color="#ffffff", corner_radius=12, border_width=1, border_color="#e0e0e0")
        self.bind("<Enter>", self._on_hover)
        self.bind("<Leave>", self._on_leave)
        self._create_widgets()

    def _create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=15)
        
        # This Card now only handles Airline
        company = _get_field(self.record_data, "Company_Name", "company_name", "company", "")
        rec_id = _get_field(self.record_data, "ID", "id", "")
        info_text = f"ID: {rec_id} | {company}"
        
        label = ctk.CTkLabel(
            content_frame, text=info_text, font=ctk.CTkFont(size=14), 
            text_color="#1a1a1a", anchor="w"
        )
        label.pack(side="left", fill="x", expand=True)
        
        actions_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        actions_frame.pack(side="right", padx=(10, 0))
        
        edit_btn = ctk.CTkButton(
            actions_frame, text="Edit", width=60, height=28, corner_radius=6, 
            fg_color="#f0f0f0", hover_color="#e0e0e0", text_color="#1a1a1a", 
            font=ctk.CTkFont(size=12), command=lambda: self.on_edit(self.record_data) if self.on_edit else None
        )
        edit_btn.pack(side="left", padx=(0, 5))
        
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
        self.configure(border_color="#06b6d4")

    def _on_leave(self, event):
        self.configure(border_color="#e0e0e0")


class ClientDialog(ctk.CTkToplevel):
    def __init__(self, master, client_data: Optional[dict] = None, on_save=None, country_list=None, city_list=None):
        super().__init__(master)
        self.client_data = client_data
        self.on_save = on_save
        self.country_list = country_list or []
        self.city_list = city_list or []
        self.result = None
        
        self.title("Edit Client" if client_data else "Create Client")
        self.geometry("450x1000")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()
        
        self.update_idletasks()
        x = master.winfo_x() + (master.winfo_width() - 450) // 2
        y = master.winfo_y() + (master.winfo_height() - 600) // 2
        self.geometry(f"+{x}+{y}")
        
        self._create_widgets()
        
        if client_data:
            self._populate_fields()

    def _create_widgets(self):
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=30, pady=25)
        
        title_text = "Edit Client" if self.client_data else "New Client"
        self.title_label = ctk.CTkLabel(
            self.main_frame, text=title_text, font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title_label.pack(anchor="w", pady=(0, 20))
        
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
        
        for field_name, label, placeholder in field_configs:
            self._create_field(field_name, label, placeholder)
        
        self.buttons_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.buttons_frame.pack(fill="x", pady=(25, 0))
        
        self.cancel_btn = ctk.CTkButton(
            self.buttons_frame, text="Cancel", width=100, height=40, corner_radius=8, 
            fg_color="transparent", hover_color="#3b3b3b", border_width=1, 
            border_color="#3b3b3b", command=self.destroy
        )
        self.cancel_btn.pack(side="left")
        
        self.save_btn = ctk.CTkButton(
            self.buttons_frame, text="Save Client", width=120, height=40, corner_radius=8, 
            fg_color="#06b6d4", hover_color="#0891b2", command=self._save
        )
        self.save_btn.pack(side="right")

    def _create_field(self, name: str, label: str, placeholder: str):
        label_widget = ctk.CTkLabel(
            self.main_frame, text=label, font=ctk.CTkFont(size=13), text_color="#666666"
        )
        label_widget.pack(anchor="w", pady=(10, 3))
        
        if name == "Country":
            entry = ctk.CTkComboBox(
                self.main_frame, values=self.country_list, height=38, corner_radius=8, 
                border_width=1, border_color="#d0d0d0", fg_color="#ffffff", 
                button_color="#e0e0e0", button_hover_color="#d0d0d0"
            )
        elif name == "City":
            entry = ctk.CTkComboBox(
                self.main_frame, values=self.city_list, height=38, corner_radius=8, 
                border_width=1, border_color="#d0d0d0", fg_color="#ffffff", 
                button_color="#e0e0e0", button_hover_color="#d0d0d0"
            )
        else:
            entry = ctk.CTkEntry(
                self.main_frame, placeholder_text=placeholder, height=38, corner_radius=8, 
                border_width=1, border_color="#d0d0d0", fg_color="#ffffff"
            )
        
        entry.pack(fill="x")
        self.fields[name] = entry

    def _populate_fields(self):
        if not self.client_data:
            return
        
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
        
        for field_name, keys in field_mapping.items():
            value = _get_field(self.client_data, *keys)
            if value and field_name in self.fields:
                if isinstance(self.fields[field_name], ctk.CTkComboBox):
                    self.fields[field_name].set(value)
                else:
                    self.fields[field_name].insert(0, value)

    def _save(self):
        data = {}
        for name, entry in self.fields.items():
            if isinstance(entry, ctk.CTkComboBox):
                data[name] = entry.get().strip()
            else:
                data[name] = entry.get().strip()
        
        if not data.get("Name"):
            messagebox.showerror("Validation Error", "Name is required")
            return
        
        if self.client_data:
            rec_id = self.client_data.get("ID") or self.client_data.get("id")
            if rec_id:
                data["id"] = int(rec_id) if isinstance(rec_id, (int, str)) else rec_id
        
        self.result = data
        if self.on_save:
            self.on_save(data)
        self.destroy()


class AirlineDialog(ctk.CTkToplevel):
    # ... (implementation omitted for brevity, assumed unchanged)
    def __init__(self, master, airline_data: Optional[dict] = None, on_save=None):
        super().__init__(master)
        self.airline_data = airline_data
        self.on_save = on_save
        self.result = None
        
        self.title("Edit Airline" if airline_data else "Create Airline")
        self.geometry("400x200")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()
        
        self.update_idletasks()
        x = master.winfo_x() + (master.winfo_width() - 400) // 2
        y = master.winfo_y() + (master.winfo_height() - 200) // 2
        self.geometry(f"+{x}+{y}")
        
        self._create_widgets()
        
        if airline_data:
            self._populate_fields()

    def _create_widgets(self):
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=30, pady=25)
        
        title_text = "Edit Airline" if self.airline_data else "New Airline"
        self.title_label = ctk.CTkLabel(
            self.main_frame, text=title_text, font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title_label.pack(anchor="w", pady=(0, 20))
        
        ctk.CTkLabel(
            self.main_frame, text="Company Name", font=ctk.CTkFont(size=13), text_color="#888888"
        ).pack(anchor="w", pady=(0, 3))
        
        self.company_entry = ctk.CTkEntry(
            self.main_frame, placeholder_text="Enter airline company name", height=38, 
            corner_radius=8, border_width=1, border_color="#d0d0d0", fg_color="#ffffff"
        )
        self.company_entry.pack(fill="x", pady=(0, 20))
        
        self.buttons_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.buttons_frame.pack(fill="x")
        
        self.cancel_btn = ctk.CTkButton(
            self.buttons_frame, text="Cancel", width=100, height=40, corner_radius=8, 
            fg_color="transparent", hover_color="#3b3b3b", border_width=1, 
            border_color="#3b3b3b", command=self.destroy
        )
        self.cancel_btn.pack(side="left")
        
        self.save_btn = ctk.CTkButton(
            self.buttons_frame, text="Save Airline", width=120, height=40, corner_radius=8, 
            fg_color="#06b6d4", hover_color="#0891b2", command=self._save
        )
        self.save_btn.pack(side="right")

    def _populate_fields(self):
        if self.airline_data:
            company = _get_field(self.airline_data, "Company_Name", "company_name", "company", "")
            if company:
                self.company_entry.insert(0, company)

    def _save(self):
        company_name = self.company_entry.get().strip()
        
        if not company_name:
            messagebox.showerror("Validation Error", "Company name is required")
            return
        
        self.result = {"Company_Name": company_name}
        
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
    
    def __init__(self) -> None:
        super().__init__()
        
        self.record_manager = RecordManager()
        
        # Load country and city lists
        try:
            self.country_list = LoadCountries()
            self.city_list = LoadCities()
        except Exception:
            self.country_list = ["United States", "Canada", "United Kingdom"]
            self.city_list = ["New York", "Toronto", "London"]
            
        # Initialize placeholders for flight dropdown data
        self.client_dropdown_list = []
        self.airline_dropdown_list = []
        
        # ENHANCEMENT: Dictionaries for quick lookup of names by ID
        # These maps store ID -> full_record, allowing name lookups for FlightCard.
        self.client_lookup = {}
        self.airline_lookup = {}
        
        self.title("Travel Agent Record Management System")
        self.geometry("1100x700")
        self.minsize(900, 600)
        
        self.current_section = "Client"
        
        self._create_layout()
        
        # FIX: Defer data loading and initial refresh to ensure CTK is fully initialized, 
        # resolving the `AttributeError: '_tkinter.tkapp' object has no attribute '...'`
        self.after(0, self._initial_setup)
        
    def _initial_setup(self):
        """Runs after the main window is ready."""
        self._load_flight_dropdown_data()
        self._refresh_records()

    def _load_flight_dropdown_data(self):
        """
        Fetches and formats Client and Airline records for use in Flight ComboBoxes.
        Format: "Name (ID)". Also populates ID lookup dictionaries.
        """
        all_clients = self.record_manager.GetAllRecords("Client")
        all_airlines = self.record_manager.GetAllRecords("Airline")
        
        self.client_dropdown_list = [_format_client_name(c) for c in all_clients]
        self.airline_dropdown_list = [_format_airline_name(a) for a in all_airlines]
        
        # ENHANCEMENT: Populate lookup dictionaries for name retrieval
        self.client_lookup = {
            int(_get_field(c, "ID", "id", default="0")): c 
            for c in all_clients
        }
        self.airline_lookup = {
            int(_get_field(a, "ID", "id", default="0")): a 
            for a in all_airlines
        }

    def _create_layout(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self._create_sidebar()
        self._create_main_content()

    def _create_sidebar(self):
        self.sidebar = ctk.CTkFrame(
            self, width=220, corner_radius=0, fg_color="#f5f5f5"
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        
        self.logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.logo_frame.pack(fill="x", padx=20, pady=(25, 30))
        
        self.logo_label = ctk.CTkLabel(
            self.logo_frame, text="✈ TravelApp", font=ctk.CTkFont(size=22, weight="bold"), 
            text_color="#06b6d4"
        )
        self.logo_label.pack(anchor="w")
        
        self.subtitle_label = ctk.CTkLabel(
            self.logo_frame, text="Record Management", font=ctk.CTkFont(size=11), text_color="#888888"
        )
        self.subtitle_label.pack(anchor="w")
        
        self.nav_buttons = {}
        nav_items = [
            ("Client", "👥  Clients"),
            ("Airline", "🛫  Airlines"),
            ("Flight", "✈️  Flights"),
        ]
        
        for section_id, label in nav_items:
            btn = ctk.CTkButton(
                self.sidebar, text=label, anchor="w", height=45, corner_radius=10, 
                font=ctk.CTkFont(size=14), 
                fg_color="transparent" if section_id != "Client" else "#06b6d4",
                text_color="white" if section_id == "Client" else "#666666",
                hover_color="#e0e0e0" if section_id != "Client" else "#0891b2",
                command=lambda s=section_id: self._switch_section(s)
            )
            btn.pack(fill="x", padx=15, pady=3)
            self.nav_buttons[section_id] = btn
        
        self.stats_frame = ctk.CTkFrame(
            self.sidebar, fg_color="#ffffff", corner_radius=12
        )
        self.stats_frame.pack(fill="x", padx=15, pady=15, side="bottom")
        
        self.stats_title = ctk.CTkLabel(
            self.stats_frame, text="Total Records", font=ctk.CTkFont(size=11), text_color="#666666"
        )
        self.stats_title.pack(anchor="w", padx=15, pady=(12, 2))
        
        self.stats_count = ctk.CTkLabel(
            self.stats_frame, text="0", font=ctk.CTkFont(size=28, weight="bold"), 
            text_color="#06b6d4"
        )
        self.stats_count.pack(anchor="w", padx=15, pady=(0, 12))

    def _create_main_content(self):
        self.main_frame = ctk.CTkFrame(self, fg_color="#ffffff", corner_radius=0)
        self.main_frame.grid(row=0, column=1, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)
        
        self.header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent", height=80)
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=30, pady=(25, 15))
        self.header_frame.grid_columnconfigure(1, weight=1)
        
        self.section_title = ctk.CTkLabel(
            self.header_frame, text="Client Records", font=ctk.CTkFont(size=26, weight="bold"), 
            text_color="#1a1a1a"
        )
        self.section_title.grid(row=0, column=0, sticky="w")
        
        self.search_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.search_frame.grid(row=0, column=1, sticky="e")
        
        self.search_entry = ctk.CTkEntry(
            self.search_frame, placeholder_text="🔍 Search records...", width=250, height=40, 
            corner_radius=10, border_width=1, border_color="#d0d0d0", fg_color="#ffffff"
        )
        self.search_entry.pack(side="left", padx=(0, 12))
        self.search_entry.bind("<KeyRelease>", self._on_search)
        
        self.add_btn = ctk.CTkButton(
            self.search_frame, text="+ Add New", width=110, height=40, corner_radius=10, 
            fg_color="#06b6d4", hover_color="#0891b2", font=ctk.CTkFont(size=14, weight="bold"), 
            command=self._add_record
        )
        self.add_btn.pack(side="left")
        
        self.records_container = ctk.CTkScrollableFrame(
            self.main_frame, fg_color="transparent", scrollbar_button_color="#3b3b3b", 
            scrollbar_button_hover_color="#4b4b4b"
        )
        self.records_container.grid(row=1, column=0, sticky="nsew", padx=30, pady=(0, 20))
        self.records_container.grid_columnconfigure(0, weight=1)

    def _switch_section(self, section: str):
        self.current_section = section
        
        if section in ("Flight", "Client", "Airline"):
            # Reload data for lookups and dropdowns
            self._load_flight_dropdown_data()
            
        for section_id, btn in self.nav_buttons.items():
            if section_id == section:
                btn.configure(fg_color="#06b6d4", text_color="white", hover_color="#0891b2")
            else:
                btn.configure(fg_color="transparent", text_color="#666666", hover_color="#e0e0e0")
        
        titles = {
            "Client": "Client Records",
            "Airline": "Airline Records",
            "Flight": "Flight Records"
        }
        self.section_title.configure(text=titles.get(section, "Records"))
        
        self.search_entry.delete(0, "end")
        self._refresh_records()

    def _refresh_records(self, filter_text: str = ""):
        for widget in self.records_container.winfo_children():
            widget.destroy()
        
        records = self.record_manager.GetAllRecords(self.current_section)
        
        if filter_text:
            filter_lower = filter_text.lower()
            records = [
                r for r in records
                if any(filter_lower in str(v).lower() for v in r.values() if v is not None)
            ]
            
        # ENHANCEMENT: Enrich flight records with names for display
        if self.current_section == "Flight":
            enhanced_records = []
            for record in records:
                client_id_str = _get_field(record, "Client_ID", "client_id", default="0")
                airline_id_str = _get_field(record, "Airline_ID", "airline_id", default="0")
                
                try:
                    client_id = int(client_id_str)
                    airline_id = int(airline_id_str)
                except ValueError:
                    continue # Skip invalid records
                
                # Get Client Name from lookup
                client_record = self.client_lookup.get(client_id, {})
                client_name = _get_field(client_record, "Name", "name", default=f"Client ID: {client_id}")
                
                # Get Airline Company Name from lookup
                airline_record = self.airline_lookup.get(airline_id, {})
                airline_name = _get_field(airline_record, "Company_Name", "company_name", default=f"Airline ID: {airline_id}")
                
                # Add the names to the record dictionary for use in FlightCard
                record['Client_Name'] = client_name
                record['Airline_Company_Name'] = airline_name
                enhanced_records.append(record)
            records = enhanced_records
        
        for record in records:
            if self.current_section == "Client":
                card = ClientCard(
                    self.records_container, record, on_edit=self._edit_record, on_delete=self._delete_record
                )
            elif self.current_section == "Flight":
                # Use the new FlightCard for detailed display
                card = FlightCard(
                    self.records_container, record, on_edit=self._edit_record, on_delete=self._delete_record
                )
            elif self.current_section == "Airline":
                # Use the existing RecordCard for Airlines
                card = RecordCard(
                    self.records_container, record, self.current_section, 
                    on_edit=self._edit_record, on_delete=self._delete_record
                )
            else:
                continue # Should not happen
                
            card.pack(fill="x", pady=(0, 10))
        
        total = (
            len(self.record_manager.GetAllRecords("Client")) +
            len(self.record_manager.GetAllRecords("Airline")) +
            len(self.record_manager.GetAllRecords("Flight"))
        )
        self.stats_count.configure(text=str(total))

    def _on_search(self, event):
        filter_text = self.search_entry.get()
        self._refresh_records(filter_text)

    def _add_record(self):
        if self.current_section == "Client":
            dialog = ClientDialog(
                self, on_save=self._save_new_client, country_list=self.country_list, city_list=self.city_list
            )
            self.wait_window(dialog)
        elif self.current_section == "Airline":
            dialog = AirlineDialog(self, on_save=self._save_new_airline)
            self.wait_window(dialog)
        elif self.current_section == "Flight":
            self._open_flight_dialog()

    def _save_new_client(self, data: dict):
        try:
            call_flexible(self.record_manager.CreateClient,
                Name=data.get("Name", ""), Address_Line_1=data.get("Address_Line_1", ""), Address_Line_2=data.get("Address_Line_2", ""), 
                Address_Line_3=data.get("Address_Line_3", ""), City=data.get("City", ""), State=data.get("State", ""), 
                Zip_Code=data.get("Zip_Code", ""), Country=data.get("Country", ""), Phone_Number=data.get("Phone_Number", "")
            )
            messagebox.showinfo("Success", "Client created successfully!")
            self._refresh_records()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create client: {e}")

    def _save_new_airline(self, data: dict):
        try:
            call_flexible(self.record_manager.CreateAirline, data.get("Company_Name", ""))
            messagebox.showinfo("Success", "Airline created successfully!")
            self._refresh_records()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create airline: {e}")

    def _edit_record(self, record: dict):
        if self.current_section == "Client":
            dialog = ClientDialog(
                self, client_data=record, on_save=self._save_edited_client, 
                country_list=self.country_list, city_list=self.city_list
            )
            self.wait_window(dialog)
        elif self.current_section == "Airline":
            dialog = AirlineDialog(self, airline_data=record, on_save=self._save_edited_airline)
            self.wait_window(dialog)
        elif self.current_section == "Flight":
            self._open_flight_dialog(record)

    def _save_edited_client(self, data: dict):
        try:
            rec_id = data.get("id")
            if not rec_id:
                messagebox.showerror("Error", "Client ID not found")
                return
            
            call_flexible(self.record_manager.UpdateClient, int(rec_id), 
                Name=data.get("Name", ""), Address_Line_1=data.get("Address_Line_1", ""), 
                Address_Line_2=data.get("Address_Line_2", ""), Address_Line_3=data.get("Address_Line_3", ""), 
                City=data.get("City", ""), State=data.get("State", ""), Zip_Code=data.get("Zip_Code", ""), 
                Country=data.get("Country", ""), Phone_Number=data.get("Phone_Number", "")
            )
            messagebox.showinfo("Success", "Client updated successfully!")
            self._refresh_records()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update client: {e}")

    def _save_edited_airline(self, data: dict):
        try:
            rec_id = data.get("id")
            if not rec_id:
                messagebox.showerror("Error", "Airline ID not found")
                return
            
            call_flexible(self.record_manager.UpdateAirline, int(rec_id), data.get("Company_Name", ""))
            messagebox.showinfo("Success", "Airline updated successfully!")
            self._refresh_records()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update airline: {e}")

    def _delete_record(self, record: dict):
        if self.current_section == "Flight":
            client_id = record.get("Client_ID") or record.get("client_id")
            airline_id = record.get("Airline_ID") or record.get("airline_id")
            
            if not client_id or not airline_id:
                messagebox.showerror("Error", "Flight record IDs not found")
                return
            
            # Use the enriched name fields for the confirmation message
            client_name = _get_field(record, "Client_Name", default="A Client")
            airline_name = _get_field(record, "Airline_Company_Name", default="An Airline")
            start_city = _get_field(record, "Start_City", "start_city", "")
            end_city = _get_field(record, "End_City", "end_city", "")
            flight_info = f"Flight for {client_name} ({start_city} to {end_city})"
            
            if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{flight_info}'?"):
                try:
                    self.record_manager.DeleteFlight(int(client_id), int(airline_id))
                    messagebox.showinfo("Success", "Flight deleted successfully!")
                    self._refresh_records()
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to delete flight: {e}")
        else:
            rec_id = record.get("ID") or record.get("id")
            if not rec_id:
                messagebox.showerror("Error", "Record ID not found")
                return
            
            name = _get_field(record, "Name", "name", "Company_Name", "company_name", "this record")
            
            if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{name}'?"):
                try:
                    self.record_manager.DeleteRecord(int(rec_id), self.current_section)
                    messagebox.showinfo("Success", "Record deleted successfully!")
                    self._refresh_records()
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to delete record: {e}")

    def _open_flight_dialog(self, record: Optional[dict] = None):
        """
        Open flight creation/editing dialog with dropdowns for Client/Airline ID 
        and embedded date/time selection.
        """
        dialog = ctk.CTkToplevel(self)
        dialog.title("Edit Flight" if record else "Create Flight")
        dialog.geometry("500x550")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        
        dialog.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - 500) // 2
        y = self.winfo_y() + (self.winfo_height() - 550) // 2
        dialog.geometry(f"+{x}+{y}")
        
        main_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=30, pady=25)
        
        title_text = "Edit Flight" if record else "New Flight"
        ctk.CTkLabel(
            main_frame, text=title_text, font=ctk.CTkFont(size=24, weight="bold")
        ).pack(anchor="w", pady=(0, 20))
        
        fields = {}
        
        # ----------------------------------------------------------------------
        # Client ID Dropdown
        # ----------------------------------------------------------------------
        ctk.CTkLabel(main_frame, text="Client", font=ctk.CTkFont(size=13), text_color="#666666").pack(anchor="w", pady=(10, 3))
        client_combo = ctk.CTkComboBox(
            main_frame, values=self.client_dropdown_list, height=38, corner_radius=8, 
            border_width=1, border_color="#d0d0d0", fg_color="#ffffff", 
            button_color="#e0e0e0", button_hover_color="#d0d0d0"
        )
        client_combo.pack(fill="x")
        fields["Client_ID"] = client_combo
        
        # ----------------------------------------------------------------------
        # Airline ID Dropdown
        # ----------------------------------------------------------------------
        ctk.CTkLabel(main_frame, text="Airline", font=ctk.CTkFont(size=13), text_color="#666666").pack(anchor="w", pady=(10, 3))
        airline_combo = ctk.CTkComboBox(
            main_frame, values=self.airline_dropdown_list, height=38, corner_radius=8, 
            border_width=1, border_color="#d0d0d0", fg_color="#ffffff", 
            button_color="#e0e0e0", button_hover_color="#d0d0d0"
        )
        airline_combo.pack(fill="x")
        fields["Airline_ID"] = airline_combo
        
        # ----------------------------------------------------------------------
        # Date & Time Picker (FIXED VISIBILITY AND INTERACTION)
        # ----------------------------------------------------------------------
        ctk.CTkLabel(main_frame, text="Date & Time", font=ctk.CTkFont(size=13), text_color="#666666").pack(anchor="w", pady=(10, 3))
        
        # FIX: Set background to a known, single color string (#FFFFFF) to prevent TclError 
        # when mixing CTK and standard tk widgets.
        date_time_frame = tk.Frame(main_frame, background="#FFFFFF") 
        date_time_frame.pack(fill="x", pady=(0, 10))
        
        # Date Entry (tkcalendar)
        # FIX: Add selectmode='day' and state='normal' for full interaction (month/year change)
        dp = DateEntry(
            date_time_frame, 
            date_pattern="yyyy-mm-dd", 
            width=12,
            selectmode='day',           # Ensures day selection is active
            state='normal',             # Ensures the widget is fully interactive
            foreground='#1a1a1a',       # Text color
            background='#ffffff',       # Widget background
            borderwidth=1,              # Visible border for clarity
            relief="solid"              # Solid border style
        )
        dp.pack(side="left", padx=(0, 10))
        
        # Time Comboboxes (ttk)
        hr_values = [str(h) for h in range(1, 13)]
        mn_values = [f"{m:02d}" for m in range(0, 60)]
        
        hr = ttk.Combobox(date_time_frame, values=hr_values, width=3, state="readonly"); hr.set("12")
        hr.pack(side="left", padx=(5, 2))
        
        # FIX: Explicitly set background for the standard tk.Label to white
        tk.Label(date_time_frame, text=":", background="#FFFFFF").pack(side="left") 
        
        mn = ttk.Combobox(date_time_frame, values=mn_values, width=3, state="readonly"); mn.set("00")
        mn.pack(side="left", padx=(2, 5))
        
        ampm = ttk.Combobox(date_time_frame, values=["AM", "PM"], width=3, state="readonly"); ampm.set("PM")
        ampm.pack(side="left", padx=(5, 0))
        
        fields["Date"] = (dp, hr, mn, ampm)
        
        # ----------------------------------------------------------------------
        # Start City field
        # ----------------------------------------------------------------------
        ctk.CTkLabel(main_frame, text="Start City", font=ctk.CTkFont(size=13), text_color="#666666").pack(anchor="w", pady=(10, 3))
        start_city = ctk.CTkComboBox(main_frame, values=self.city_list, height=38, corner_radius=8, border_width=1, border_color="#d0d0d0", fg_color="#ffffff", button_color="#e0e0e0", button_hover_color="#d0d0d0")
        start_city.pack(fill="x")
        fields["Start_City"] = start_city
        
        # ----------------------------------------------------------------------
        # End City field
        # ----------------------------------------------------------------------
        ctk.CTkLabel(main_frame, text="End City", font=ctk.CTkFont(size=13), text_color="#666666").pack(anchor="w", pady=(10, 3))
        end_city = ctk.CTkComboBox(main_frame, values=self.city_list, height=38, corner_radius=8, border_width=1, border_color="#d0d0d0", fg_color="#ffffff", button_color="#e0e0e0", button_hover_color="#d0d0d0")
        end_city.pack(fill="x")
        fields["End_City"] = end_city
        
        # Pre-fill fields if editing
        if record:
            client_id = _get_field(record, "Client_ID", "client_id", "")
            airline_id = _get_field(record, "Airline_ID", "airline_id", "")
            
            # Set dropdown values for Client and Airline IDs (using "Name (ID)")
            if client_id:
                client_item = next((item for item in self.client_dropdown_list if f"({client_id})" in item), self.client_dropdown_list[0] if self.client_dropdown_list else "")
                client_combo.set(client_item)
            if airline_id:
                airline_item = next((item for item in self.airline_dropdown_list if f"({airline_id})" in item), self.airline_dropdown_list[0] if self.airline_dropdown_list else "")
                airline_combo.set(airline_item)
            
            # Set Date/Time fields
            date_val = _get_field(record, "Date", "date", "")
            if isinstance(date_val, datetime):
                dp.set_date(date_val.date())
                
                hr24 = date_val.hour
                # Convert 24hr to 12hr format
                dhr, ampm = (12, "AM") if hr24 == 0 else (hr24, "AM") if 1 <= hr24 <= 11 else (12, "PM") if hr24 == 12 else (hr24 - 12, "PM")
                
                hr.set(str(dhr))
                mn.set(f"{date_val.minute:02d}")
                ampm.set(ampm)
            
            start_city.set(_get_field(record, "Start_City", "start_city", ""))
            end_city.set(_get_field(record, "End_City", "end_city", ""))
        
        # Buttons frame
        buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        buttons_frame.pack(fill="x", pady=(20, 0))
        
        def save_flight():
            """Save flight data to backend."""
            client_id = _parse_id_from_dropdown(fields["Client_ID"].get())
            airline_id = _parse_id_from_dropdown(fields["Airline_ID"].get())
            
            dp_widget, hr_widget, mn_widget, ampm_widget = fields["Date"]
            
            try:
                # Use the integrated helper to get the final datetime object
                date_value = build_datetime_from_ui(dp_widget.get_date(), hr_widget.get(), mn_widget.get(), ampm_widget.get())
            except Exception:
                messagebox.showerror("Validation Error", "Please select a valid date and time")
                return
            
            start = fields["Start_City"].get()
            end = fields["End_City"].get()
            
            if not client_id or not airline_id:
                messagebox.showerror("Error", "Please select a valid Client and Airline")
                return
            if not start or not end:
                messagebox.showerror("Error", "Start City and End City are required")
                return
            
            try:
                if record:
                    call_flexible(self.record_manager.UpdateFlight, client_id, airline_id, Date=date_value, Start_City=start, End_City=end)
                    messagebox.showinfo("Success", "Flight updated successfully!")
                else:
                    call_flexible(self.record_manager.CreateFlight, client_id, airline_id, date_value, start, end)
                    messagebox.showinfo("Success", "Flight created successfully!")
                
                dialog.destroy()
                self._refresh_records()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save flight: {e}")
        
        # Cancel and Save buttons
        ctk.CTkButton(buttons_frame, text="Cancel", command=dialog.destroy, width=100, height=40, corner_radius=8, fg_color="transparent", hover_color="#f0f0f0", border_width=1, border_color="#d0d0d0", text_color="#1a1a1a").pack(side="left")
        ctk.CTkButton(buttons_frame, text="Save Flight", command=save_flight, width=120, height=40, corner_radius=8, fg_color="#06b6d4", hover_color="#0891b2").pack(side="right")
        
        dialog.wait_window()

# ============================================================================
# ENTRY POINT
# ============================================================================

def main() -> None:
    app = RecordManagementSystem()
    app.mainloop()

if __name__ == "__main__":
    main()
