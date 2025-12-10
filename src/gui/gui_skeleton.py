from __future__ import annotations
import os
import sys
from datetime import datetime, date, time
from typing import Dict, Any, Callable, List, Tuple
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

# Ensure src/ is on path so local imports work when running module directly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Local backend modules 
from record.record_manager import RecordManager
from data.data_loader import LoadCountries, LoadCities

# tkcalendar DateEntry for date selection
try:
    from tkcalendar import DateEntry
except ImportError:
    messagebox.showerror("Error", "tkcalendar not installed. Run: pip install tkcalendar")
    raise

# ----------------------
# Visual configuration
# ----------------------
# Background Colors
OUTER_BG = "#E9FBFF"        # Lightest background (main window)
PANEL_BG = "#06162A"        # Dark panel background (frames)
PANEL_ACCENT = "#0E4A78"    # Accent color for headers/separators

# Card/Button Colors
CARD_BG = "#0F5A8B"         # Default color for dashboard tiles
CARD_HOVER = "#0E6BA3"      # Hover color for dashboard tiles
BUTTON_SAVE = "#198754"     # Green for Create/Save
BUTTON_DELETE = "#C62828"   # Red for Delete
BUTTON_SEARCH = "#F08A00"   # Orange for Search
BUTTON_CANCEL = "#1F3B6F"   # Dark blue for Cancel

# Treview Colors
TREE_ALT = "#F6FBFF"        # Alternate row color in treeviews

# Fonts
FONT_FAMILY = "Segoe UI"
FONT = (FONT_FAMILY, 12)
HEADING_FONT = (FONT_FAMILY, 20, "bold")
SUBHEADING_FONT = (FONT_FAMILY, 12, "bold")
DATETIME_FORMAT = "%Y-%m-%d %H:%M"

# ----------------------
# Helpers: datetime conversion & flexible caller 
# ----------------------
def build_datetime_from_ui(selected_date: date, hour_str: str, minute_str: str, ampm: str) -> datetime:
    # Convert DateEntry and time components into a single datetime object
    hour, minute = int(hour_str or 0), int(minute_str or 0)
    hour = hour % 12 + (12 if ampm.upper() == "PM" and hour != 12 else 0 if ampm.upper() == "AM" and hour == 12 else 0)
    return datetime.combine(selected_date, time(hour=hour, minute=minute))

def datetime_to_string(dt: datetime) -> str:
    # Fortmat datetime object to string
    return dt.strftime(DATETIME_FORMAT)

def call_flexible(fn: Callable, /, *args, **kwargs):
    # Attempts to call a function with various combinations of args/kwargs.
    # Used to support backend methods with different signatures.
    try: return fn(*args, **kwargs)
    except TypeError:
        try: return fn(**kwargs)
        except TypeError: return fn(*args)

def _get_field(record: Dict, *keys, default=""):
    # Safely get field from record with multiple possible keys
    for k in keys:
        if k in record and record[k] is not None:
            return record[k]
    return default

def make_tile(master, text: str, color: str, command: Callable):
    # Creates a dashboard tile with hover effect
    frame = tk.Frame(master, bg=color, width=260, height=140); frame.pack_propagate(False)
    on_enter = lambda _e: frame.config(bg=CARD_HOVER)
    on_leave = lambda _e: frame.config(bg=color)
    btn = tk.Button(frame, text=text, bg=color, fg="white", font=(FONT_FAMILY, 14, "bold"), bd=0, activebackground=color, activeforeground="white", command=command)
    btn.pack(expand=True, fill="both", padx=12, pady=12)
    # Bind hover events to both frame and button
    for w in (frame, btn): 
        w.bind("<Enter>", on_enter);
        w.bind("<Leave>", on_leave)
    return frame

# ----------------------
# Main GUI class 
# ----------------------
class RecordManagementSystem(tk.Tk):
    def __init__(self):
        super().__init__()
        # Window setup
        self.title("Travel Agent Record Management System") 
        self.geometry("1180x760")
        self.minsize(1000, 620)
        self.configure(bg=OUTER_BG) # Main Window background color
        
        # Nested frames for styling
        outer = tk.Frame(self, bg=OUTER_BG)
        outer.pack(fill="both", expand=True, padx=18, pady=18)
        panel = tk.Frame(outer, bg=PANEL_BG)
        panel.pack(fill="both", expand=True, padx=8, pady=8)
        self.container = tk.Frame(panel, bg=PANEL_ACCENT)
        self.container.pack(fill="both", expand=True, padx=14, pady=14)
        
        # Styles for Treeview (Grid)
        self.style = ttk.Style(self)
        try: self.style.theme_use("clam")
        except Exception: pass

        # Custom Treeview style
        self.style.configure("Custom.Treeview", font=FONT, rowheight=28, fieldbackground="white")
        self.style.configure("Custom.Treeview.Heading", font=(FONT_FAMILY, 12, "bold"), background=PANEL_BG, foreground="white")
        self.style.map("Custom.Treeview", background=[("selected", "#D9F1FF")])

        # Backend & Data Initialization
        self.record_manager = RecordManager()
        try: 
            self.country_list, self.city_list = LoadCountries(), LoadCities()
        except Exception: 
            # Fallback if data loading fails
            self.country_list, self.city_list = ["United States", "Canada"], ["New York", "Toronto"]
        # Track last action for "Back" button logic
        self.last_action = {"Client": None, "Airline": None, "Flight": None}

        # Notebook
        self.notebook = ttk.Notebook(self.container)
        self.notebook.pack(fill="both", expand=True)

        # Create tab frames
        self.client_tab, self.airline_tab, self.flight_tab = ttk.Frame(self.notebook), ttk.Frame(self.notebook), ttk.Frame(self.notebook)
        
        # Add tabs to notebook
        self.notebook.add(self._build_main_tab(), text="Home")
        self.notebook.add(self.client_tab, text="Clients")
        self.notebook.add(self.airline_tab, text="Airlines")
        self.notebook.add(self.flight_tab, text="Flights")
        
        # Build each tab
        self._build_client_tab()
        self._build_airline_tab()
        self._build_flight_tab()

    def _goto_tab(self, idx: int):
        # Switch to tab by index
        self.notebook.select(idx)

    # ----------------------
    # HOME tab (dashboard)
    # ----------------------
    def _build_main_tab(self):
        f = ttk.Frame(self.notebook); 
        tk.Label(f, text="Record Management Dashboard", bg=PANEL_ACCENT, fg="white", font=HEADING_FONT, pady=14).pack(fill="x", pady=(8, 18), padx=6)
        tiles_frame = tk.Frame(f, bg=PANEL_ACCENT); tiles_frame.pack(pady=6)
        row = tk.Frame(tiles_frame, bg=PANEL_ACCENT); row.pack()
        make_tile(row, "Clients", CARD_BG, lambda: self._goto_tab(1)).pack(side="left", padx=14)
        make_tile(row, "Airlines", CARD_BG, lambda: self._goto_tab(2)).pack(side="left", padx=14)
        make_tile(row, "Flights", CARD_BG, lambda: self._goto_tab(3)).pack(side="left", padx=14)
        tk.Label(f, text="Use the tabs above or choose a tile to manage records.", bg=PANEL_ACCENT, fg="white", font=SUBHEADING_FONT).pack(pady=(22, 6))
        return f

    # ----------------------
    # Tab Builder Function
    # ----------------------
    def _build_tab_layout(self, tab: ttk.Frame, name: str, button_color: str, columns: Tuple[str, ...], refresh_func: Callable, crud_methods: Dict[str, Callable], column_widths: Dict[str, int] = None):
        """
        Standardized layout for Client, Airline, and Flight tabs.
        Includes header with CRUD buttons and a Treeview for displaying records.
        """
        header_frame = tk.Frame(tab, bg=PANEL_ACCENT)
        header_frame.pack(fill="x", pady=8, padx=6)
        
        # Back button logic
        def back_command():
            if self.last_action.get(name) == "search":
                refresh_func(); self.last_action[name] = None
            else: self._goto_tab(0)
            
        tk.Button(header_frame, text="Back", bg=PANEL_BG, fg="white", font=FONT, width=10, command=back_command).pack(side="left", padx=6)
       
       # Center frame for CRUD buttons
        center = tk.Frame(header_frame, bg=PANEL_ACCENT); 
        center.pack(side="left", expand=True)

        tk.Button(center, text=f"Create {name}", bg=button_color, fg="white", font=FONT, width=16, command=crud_methods["create"]).pack(side="left", padx=8)
        tk.Button(center, text=f"Update {name}", bg=BUTTON_CANCEL, fg="white", font=FONT, width=16, command=crud_methods["update"]).pack(side="left", padx=8)
        tk.Button(center, text=f"Delete {name}", bg=BUTTON_DELETE, fg="white", font=FONT, width=16, command=crud_methods["delete"]).pack(side="left", padx=8)
        tk.Button(center, text=f"Search {name}", bg=BUTTON_SEARCH, fg="white", font=FONT, width=16, command=crud_methods["search"]).pack(side="left", padx=8)

        # Treeview for records
        tree = ttk.Treeview(tab, columns=columns, show="headings", style="Custom.Treeview", height=18)
       
        for c in columns:
            tree.heading(c, text=c.replace("_", " "))
            tree.column(c, width=column_widths.get(c, 110) if column_widths else 110, anchor="center", stretch=True)
       
        tree.pack(fill="both", expand=True, padx=12, pady=10)
        self._add_striping(tree)
        return tree

    def _build_client_tab(self):
        cols = ("ID", "Type", "Name", "Address_Line_1", "Address_Line_2", "Address_Line_3", "City", "State", "Zip_Code", "Country", "Phone_Number")
        self.client_tree = self._build_tab_layout(self.client_tab, "Client", BUTTON_SAVE, cols, self.refresh_client_list,
                                                  {"create": self.create_client, "update": self.update_client, "delete": self.delete_client, "search": self.search_client})

    def _build_airline_tab(self):
        cols = ("ID", "Type", "Company_Name")
        self.airline_tree = self._build_tab_layout(self.airline_tab, "Airline", BUTTON_SAVE, cols, self.refresh_airline_list,
                                                   {"create": self.create_airline, "update": self.update_airline, "delete": self.delete_airline, "search": self.search_airline},
                                                   column_widths={"ID": 100, "Type": 100, "Company_Name": 300})

    def _build_flight_tab(self):
        cols = ("Client_ID", "Airline_ID", "Type", "Date", "Start_City", "End_City")
        self.flight_tree = self._build_tab_layout(self.flight_tab, "Flight", BUTTON_SAVE,cols, self.refresh_flight_list,
                                                  {"create": self.create_flight, "update": self.update_flight, "delete": self.delete_flight, "search": self.search_flight},
                                                  column_widths={"Client_ID": 150, "Airline_ID": 150, "Type": 100, "Date": 180, "Start_City": 150, "End_City": 150})

    # ----------------------
    # Treeview Helpers 
    # ----------------------
    def _add_striping(self, tree: ttk.Treeview):
        # Add row striping to Treeview
        tree.tag_configure("oddrow", background="white"); 
        tree.tag_configure("evenrow", background=TREE_ALT)

    def _refresh_tree(self, tree: ttk.Treeview, rectype: str, field_extractor: Callable[[Dict], List[Any]]):
       # Generic tree refresh function
        tree.delete(*tree.get_children())
       
       # Populate tree with records
        for i, rec in enumerate(self.record_manager.GetAllRecords(rectype)):
            vals = field_extractor(rec)
            tag = "evenrow" if i % 2 == 0 else "oddrow"
            tree.insert("", "end", values=vals, tags=(tag,))

    # Refresh functions for each tab
    def refresh_client_list(self):
        fields = lambda rec: [_get_field(rec, "ID"), "Client", _get_field(rec, "Name"), _get_field(rec, "Address_Line_1"), _get_field(rec, "Address_Line_2"), _get_field(rec, "Address_Line_3"), _get_field(rec, "City"), _get_field(rec, "State"), _get_field(rec, "Zip_Code"), _get_field(rec, "Country"), _get_field(rec, "Phone_Number")]
        self._refresh_tree(self.client_tree, "Client", fields)

    def refresh_airline_list(self):
        fields = lambda rec: [_get_field(rec, "ID"), "Airline", _get_field(rec, "Company_Name")]
        self._refresh_tree(self.airline_tree, "Airline", fields)

    def refresh_flight_list(self):
        def fields(rec):
            date_val = _get_field(rec, "Date")
            date_str = datetime_to_string(date_val) if isinstance(date_val, datetime) else str(date_val)
            return [_get_field(rec, "Client_ID"), _get_field(rec, "Airline_ID"), "Flight", date_str, _get_field(rec, "Start_City"), _get_field(rec, "End_City")]
        self._refresh_tree(self.flight_tree, "Flight", fields)

    # ----------------------
    # Form popup & CRUD FunctionS
    # ----------------------
    def _form_popup(self, title: str, fields: Dict[str, Any], save_callback: Callable):
        # Generic form popup for Create/Update operations
        win = tk.Toplevel(self)
        win.title(title)
        win.transient(self)
        win.grab_set()

        widgets: Dict[str, Any] = {}
        for i, (label, val) in enumerate(fields.items()):
            tk.Label(win, text=label.replace("_", " "), font=(FONT_FAMILY, 11, "bold")).grid(row=i, column=0, sticky="w", padx=8, pady=8)
             # Create appropriate widget based on field type
            if isinstance(val, list):
                # Dropdown for list of options
                w = ttk.Combobox(win, values=val, state="readonly", width=36); w.grid(row=i, column=1, columnspan=4, sticky="w", padx=8, pady=8)
                widgets[label] = w
            elif val == "datetime":
                dp = DateEntry(win, date_pattern="yyyy-mm-dd"); dp.grid(row=i, column=1, sticky="w", padx=8, pady=8)
                hr = ttk.Combobox(win, values=[str(h) for h in range(1, 13)], width=4, state="readonly"); hr.set("12"); hr.grid(row=i, column=2, sticky="w", padx=6)
                mn = ttk.Combobox(win, values=[f"{m:02d}" for m in range(0, 60)], width=5, state="readonly"); mn.set("00"); mn.grid(row=i, column=3, sticky="w", padx=6)
                ampm = ttk.Combobox(win, values=["AM", "PM"], width=4, state="readonly"); ampm.set("PM"); ampm.grid(row=i, column=4, sticky="w", padx=6)
                widgets[label] = (dp, hr, mn, ampm)
            else:
                # Standard text entry
                w = ttk.Entry(win, width=40); 
                w.insert(0, str(val))
                w.grid(row=i, column=1, columnspan=4, sticky="w", padx=8, pady=8)
                widgets[label] = w
        # Save and Cancel buttons
        tk.Button(win, text="Save", bg=BUTTON_SAVE, fg="white", width=12, command=lambda: save_callback(widgets, win)).grid(row=len(fields), column=1, pady=12, padx=8, sticky="w")
        tk.Button(win, text="Cancel", bg=BUTTON_CANCEL, fg="white", width=12, command=win.destroy).grid(row=len(fields), column=2, pady=12, padx=8, sticky="e")
        return win, widgets

    # ----------------------
    # CRUD Functions
    # ----------------------
    # Generic function to get selected record from Treeview
    def _get_selected_record(self, tree: ttk.Treeview, rectype: str) -> Dict | None:
        sel = tree.focus()
        if not sel:
            messagebox.showerror("Error", f"Select a {rectype.lower()} to update")
            return None
        return self.record_manager.GetAllRecords(rectype)[tree.index(sel)]

    def _crud_operation(self, rectype: str, fields_builder: Callable[[Dict | None], Dict], save_logic: Callable[[Dict, tk.Toplevel, Dict | None], None], is_update: bool = False, is_delete: bool = False, post_refresh: Callable = None):
        # Generic CRUD operation handler
        record = None
        # Step 1: Get selected record for update/delete
        if is_update or is_delete:
            record = self._get_selected_record(getattr(self, f"{rectype.lower()}_tree"), rectype)
            if not record: return

        # Step 2: Handle delete operation
        if is_delete:
            try:
                delete_fn = self.record_manager.DeleteFlight if rectype == "Flight" else self.record_manager.DeleteRecord
                args = (int(_get_field(record, "Client_ID")), int(_get_field(record, "Airline_ID"))) if rectype == "Flight" else (record["ID"], rectype)
                if delete_fn(*args):
                    messagebox.showinfo("Success", f"{rectype} deleted"); post_refresh()
                else: messagebox.showerror("Error", "Delete failed")
            except Exception as e: messagebox.showerror("Error", str(e))
            return

        # Step 3: Build form for create/update
        fields = fields_builder(record)
        
        def save(widgets: Dict, win: tk.Toplevel):
            try:
                save_logic(widgets, win, record)
                messagebox.showinfo("Success", f"{rectype} {'updated' if is_update else 'created'}")
                win.destroy(); post_refresh()
            except Exception as e: messagebox.showerror("Error", str(e))

        win, widgets = self._form_popup(f"{'Update' if is_update else 'Create'} {rectype}", fields, save)
        
        # Pre-fill logic for update forms (Client is simple, Flight is complex)
        if is_update and rectype == "Flight":
            try:
                widgets["Client_ID"].set(str(_get_field(record, "Client_ID"))); widgets["Airline_ID"].set(str(_get_field(record, "Airline_ID")))
                date_val = _get_field(record, "Date")
                if isinstance(date_val, datetime):
                    widgets["Date"][0].set_date(date_val)
                    hr24 = date_val.hour; dhr, ampm = (12, "AM") if hr24 == 0 else (hr24, "AM") if 1 <= hr24 <= 11 else (12, "PM") if hr24 == 12 else (hr24 - 12, "PM")
                    widgets["Date"][1].set(str(dhr)); widgets["Date"][2].set(f"{date_val.minute:02d}"); widgets["Date"][3].set(ampm)
                widgets["Start_City"].set(_get_field(record, "Start_City")); widgets["End_City"].set(_get_field(record, "End_City"))
            except Exception: pass
        elif is_update and rectype == "Client":
            try:
                 for key in fields:
                    if isinstance(widgets[key], ttk.Combobox):
                        widgets[key].set(_get_field(record, key))
                    elif isinstance(widgets[key], ttk.Entry):
                         widgets[key].delete(0, tk.END)
                         widgets[key].insert(0, _get_field(record, key))
            except Exception: pass


    # ----------------------
    # CLIENT CRUD 
    # ----------------------
    def create_client(self):
        fields = lambda _: {"Name": "", "Address_Line_1": "", "Address_Line_2": "", "Address_Line_3": "", "City": self.city_list, "State": "", "Zip_Code": "", "Country": self.country_list, "Phone_Number": ""}
        def save(widgets, win, _):
            kwargs = {k: widgets[k].get() for k in fields(None)}
            call_flexible(self.record_manager.CreateClient, *kwargs.values(), **kwargs)
        self._crud_operation("Client", fields, save, post_refresh=self.refresh_client_list)

    def update_client(self):
        fields = lambda rec: {"Name": _get_field(rec, "Name"), "Address_Line_1": _get_field(rec, "Address_Line_1"), "Address_Line_2": _get_field(rec, "Address_Line_2"), "Address_Line_3": _get_field(rec, "Address_Line_3"), "City": self.city_list, "State": _get_field(rec, "State"), "Zip_Code": _get_field(rec, "Zip_Code"), "Country": self.country_list, "Phone_Number": _get_field(rec, "Phone_Number")}
        def save(widgets, win, record):
            call_flexible(self.record_manager.UpdateClient, record["ID"], **{k: widgets[k].get() for k in fields(record)})
        self._crud_operation("Client", fields, save, is_update=True, post_refresh=self.refresh_client_list)

    def delete_client(self):
        self._crud_operation("Client", None, None, is_delete=True, post_refresh=self.refresh_client_list)

    def search_client(self):
        term = simpledialog.askstring("Search Client", "Enter search term (name, city, etc.)"); 
        if not term: return
        results = self.record_manager.SearchRecords(term, "Client")
        self.client_tree.delete(*self.client_tree.get_children())
        fields = lambda rec: [_get_field(rec, "ID"), "Client", _get_field(rec, "Name"), _get_field(rec, "Address_Line_1"), _get_field(rec, "Address_Line_2"), _get_field(rec, "Address_Line_3"), _get_field(rec, "City"), _get_field(rec, "State"), _get_field(rec, "Zip_Code"), _get_field(rec, "Country"), _get_field(rec, "Phone_Number")]
        for i, rec in enumerate(results):
            tag = "evenrow" if i % 2 == 0 else "oddrow"; self.client_tree.insert("", "end", values=fields(rec), tags=(tag,))
        self.last_action["Client"] = "search"

    # ----------------------
    # AIRLINE CRUD 
    # ----------------------
    def create_airline(self):
        fields = lambda _: {"Company_Name": ""}
        def save(widgets, win, _):
            name = widgets["Company_Name"].get()
            call_flexible(self.record_manager.CreateAirline, name, Company_Name=name)
        self._crud_operation("Airline", fields, save, post_refresh=self.refresh_airline_list)

    def update_airline(self):
        fields = lambda rec: {"Company_Name": _get_field(rec, "Company_Name")}
        def save(widgets, win, record):
            name = widgets["Company_Name"].get()
            call_flexible(self.record_manager.UpdateAirline, record["ID"], name, Company_Name=name)
        self._crud_operation("Airline", fields, save, is_update=True, post_refresh=self.refresh_airline_list)

    def delete_airline(self):
        self._crud_operation("Airline", None, None, is_delete=True, post_refresh=self.refresh_airline_list)

    def search_airline(self):
        term = simpledialog.askstring("Search Airline", "Enter search term (company name, id, etc.)"); 
        if not term: return
        results = self.record_manager.SearchRecords(term, "Airline")
        self.airline_tree.delete(*self.airline_tree.get_children())
        fields = lambda rec: [_get_field(rec, "ID"), "Airline", _get_field(rec, "Company_Name")]
        for i, rec in enumerate(results):
            tag = "evenrow" if i % 2 == 0 else "oddrow"; self.airline_tree.insert("", "end", values=fields(rec), tags=(tag,))
        self.last_action["Airline"] = "search"

    # ----------------------
    # FLIGHT CRUD
    # ----------------------
    def create_flight(self):
        clients = [str(c["ID"]) for c in self.record_manager.GetAllRecords("Client")]
        airlines = [str(a["ID"]) for a in self.record_manager.GetAllRecords("Airline")]
        fields = lambda _: {"Client_ID": clients, "Airline_ID": airlines, "Date": "datetime", "Start_City": self.city_list, "End_City": self.city_list}
        def save(widgets, win, _):
            client_id, airline_id = int(widgets["Client_ID"].get()), int(widgets["Airline_ID"].get())
            dp, hr, mn, ampm = widgets["Date"]; dt = build_datetime_from_ui(dp.get_date(), hr.get(), mn.get(), ampm.get())
            call_flexible(self.record_manager.CreateFlight, client_id, airline_id, dt, widgets["Start_City"].get(), widgets["End_City"].get(), Client_ID=client_id, Airline_ID=airline_id, Date=dt, Start_City=widgets["Start_City"].get(), End_City=widgets["End_City"].get())
        self._crud_operation("Flight", fields, save, post_refresh=self.refresh_flight_list)

    def update_flight(self):
        clients = [str(c["ID"]) for c in self.record_manager.GetAllRecords("Client")]
        airlines = [str(a["ID"]) for a in self.record_manager.GetAllRecords("Airline")]
        fields = lambda rec: {"Client_ID": clients, "Airline_ID": airlines, "Date": "datetime", "Start_City": self.city_list, "End_City": self.city_list}
        def save(widgets, win, record):
            client_id, airline_id = int(widgets["Client_ID"].get()), int(widgets["Airline_ID"].get())
            dp, hr, mn, ampm = widgets["Date"]; dt = build_datetime_from_ui(dp.get_date(), hr.get(), mn.get(), ampm.get())
            call_flexible(self.record_manager.UpdateFlight, client_id, airline_id, Date=dt, Start_City=widgets["Start_City"].get(), End_City=widgets["End_City"].get(), Client_ID=client_id, Airline_ID=airline_id)
        self._crud_operation("Flight", fields, save, is_update=True, post_refresh=self.refresh_flight_list)

    def delete_flight(self):
        self._crud_operation("Flight", None, None, is_delete=True, post_refresh=self.refresh_flight_list)

    def search_flight(self):
        term = simpledialog.askstring("Search Flight", "Enter search term (client id, airline id, city, etc.)"); 
        if not term: return
        results = self.record_manager.SearchRecords(term, "Flight")
        self.flight_tree.delete(*self.flight_tree.get_children())
        def fields(rec):
            date_val = _get_field(rec, "Date"); date_str = datetime_to_string(date_val) if isinstance(date_val, datetime) else str(date_val)
            return [_get_field(rec, "Client_ID"), _get_field(rec, "Airline_ID"), "Flight", date_str, _get_field(rec, "Start_City"), _get_field(rec, "End_City")]
        for i, rec in enumerate(results):
            tag = "evenrow" if i % 2 == 0 else "oddrow"; self.flight_tree.insert("", "end", values=fields(rec), tags=(tag,))
        self.last_action["Flight"] = "search"


# ----------------------
# Entry point
# ----------------------
if __name__ == "__main__":
    app = RecordManagementSystem()
    app.mainloop()
