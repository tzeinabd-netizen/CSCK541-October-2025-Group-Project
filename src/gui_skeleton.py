# ======================
# Import Tkinter modules
# ======================

import tkinter as tk
from tkinter import ttk, messagebox

# ======================
# Main Application Class
# ======================
# This class creates the main window and tabs for managing
# client, airline, and flight records with CRUD operations.
# This allows us to organize all GUI elements inside a single class.

class RecordManagementSystem(tk.Tk):
    def __init__(self):
        super().__init__() # Call the parent constructor to initialize the Tk window
        
        # Set the window title and size
        self.title("Travel Agent Record Management System")
        self.geometry("900x600") # Width x Height

        # Notebook for tabs
        self.notebook = ttk.Notebook(self) # Notebook allows multiple tabs
        self.notebook.pack(fill='both', expand=True) # Fill entire window


        # ======================
        # Create individual tabs
        # ======================
        self.client_tab = ttk.Frame(self.notebook)  # Tab for Clients
        self.airline_tab = ttk.Frame(self.notebook) # Tab for Airlines
        self.flight_tab = ttk.Frame(self.notebook)  # Tab for Flights

        # Add tabs to notebook and give them a title
        self.notebook.add(self.client_tab, text="Clients")
        self.notebook.add(self.airline_tab, text="Airlines")
        self.notebook.add(self.flight_tab, text="Flights")
        
        # ======================
        # Build the content inside each tab
        # ======================
        
        self.build_client_tab()
        self.build_airline_tab()
        self.build_flight_tab()

    def build_client_tab(self):
        # Title label for the tab
        tk.Label(self.client_tab, text="Client Records", font=("Arial", 16)).pack(pady=10)

        # Frame to hold the buttons horizontally
        button_frame = tk.Frame(self.client_tab)
        button_frame.pack(pady=10)

        # Buttons for actions
        tk.Button(button_frame, text="Create Client", command=self.create_client).grid(row=0, column=0, padx=5)
        tk.Button(button_frame, text="Update Client", command=self.update_client).grid(row=0, column=1, padx=5)
        tk.Button(button_frame, text="Delete Client", command=self.delete_client).grid(row=0, column=2, padx=5)
        tk.Button(button_frame, text="Search Client", command=self.search_client).grid(row=0, column=3, padx=5)

        # display client records
        self.client_listbox = tk.Listbox(self.client_tab, width=120)
        self.client_listbox.pack(pady=20)

    # ===============================
    # Build Airline Tab
    # ===============================
    def build_airline_tab(self):
        tk.Label(self.airline_tab, text="Airline Records", font=("Arial", 16)).pack(pady=10)

        button_frame = tk.Frame(self.airline_tab)
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Create Airline", command=self.create_airline).grid(row=0, column=0, padx=5)
        tk.Button(button_frame, text="Update Airline", command=self.update_airline).grid(row=0, column=1, padx=5)
        tk.Button(button_frame, text="Delete Airline", command=self.delete_airline).grid(row=0, column=2, padx=5)
        tk.Button(button_frame, text="Search Airline", command=self.search_airline).grid(row=0, column=3, padx=5)

        self.airline_listbox = tk.Listbox(self.airline_tab, width=120)
        self.airline_listbox.pack(pady=20)

    # ===============================
    # Build Flight Tab
    # ===============================

    def build_flight_tab(self):
        tk.Label(self.flight_tab, text="Flight Records", font=("Arial", 16)).pack(pady=10)

        button_frame = tk.Frame(self.flight_tab)
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Create Flight", command=self.create_flight).grid(row=0, column=0, padx=5)
        tk.Button(button_frame, text="Update Flight", command=self.update_flight).grid(row=0, column=1, padx=5)
        tk.Button(button_frame, text="Delete Flight", command=self.delete_flight).grid(row=0, column=2, padx=5)
        tk.Button(button_frame, text="Search Flight", command=self.search_flight).grid(row=0, column=3, padx=5)

        self.flight_listbox = tk.Listbox(self.flight_tab, width=120)
        self.flight_listbox.pack(pady=20)

    # =======================
    # Client CRUD windows
    # =======================
    def create_client(self):
        """Open a popup window to create a new client"""
        self.client_form_window(title="Create Client")

    def update_client(self):
        """Open a popup window to update an existing client"""
        self.client_form_window(title="Update Client")

    def client_form_window(self, title="Client Form"):
        """Popup window for creating/updating a client"""
        form = tk.Toplevel(self)
        form.title(title)
        form.geometry("400x500")

        # Fields required for a client

        fields = [
            "ID", "Type", "Name", "Address Line 1", "Address Line 2", 
            "Address Line 3", "City", "State", "Zip Code", "Country", "Phone Number"
        ]
        entries = {}

        # Create a Label and Entry for each field
        for i, field in enumerate(fields):
            tk.Label(form, text=field).grid(row=i, column=0, sticky='w', padx=10, pady=5)
            entry = tk.Entry(form, width=30)
            entry.grid(row=i, column=1, padx=10, pady=5)
            entries[field] = entry

        # Save button
        tk.Button(form, text="Save", command=lambda: self.save_client(entries, form)).grid(row=len(fields), column=0, columnspan=2, pady=10)

    def save_client(self, entries, window):
        """Placeholder save method"""
        client_data = {field: entry.get() for field, entry in entries.items()}
        print("Client Data Saved:", client_data)
        messagebox.showinfo("Info", "Client saved successfully!")
        window.destroy() # Close the popup window

    # =======================
    # Airline CRUD windows
    # =======================
    def create_airline(self):
        self.airline_form_window(title="Create Airline")

    def update_airline(self):
        self.airline_form_window(title="Update Airline")

    def airline_form_window(self, title="Airline Form"):
        form = tk.Toplevel(self)
        form.title(title)
        form.geometry("400x200")

        fields = ["ID", "Type", "Company Name"]
        entries = {}

        for i, field in enumerate(fields):
            tk.Label(form, text=field).grid(row=i, column=0, sticky='w', padx=10, pady=5)
            entry = tk.Entry(form, width=30)
            entry.grid(row=i, column=1, padx=10, pady=5)
            entries[field] = entry

        tk.Button(form, text="Save", command=lambda: self.save_airline(entries, form)).grid(row=len(fields), column=0, columnspan=2, pady=10)

    def save_airline(self, entries, window):
        airline_data = {field: entry.get() for field, entry in entries.items()}
        print("Airline Data Saved:", airline_data)
        messagebox.showinfo("Info", "Airline saved successfully!")
        window.destroy()

    # =======================
    # Flight CRUD windows
    # =======================
    def create_flight(self):
        self.flight_form_window(title="Create Flight")

    def update_flight(self):
        self.flight_form_window(title="Update Flight")

    def flight_form_window(self, title="Flight Form"):
        form = tk.Toplevel(self)
        form.title(title)
        form.geometry("400x300")

        fields = ["Client_ID", "Airline_ID", "Date", "Start City", "End City"]
        entries = {}

        for i, field in enumerate(fields):
            tk.Label(form, text=field).grid(row=i, column=0, sticky='w', padx=10, pady=5)
            entry = tk.Entry(form, width=30)
            entry.grid(row=i, column=1, padx=10, pady=5)
            entries[field] = entry

        tk.Button(form, text="Save", command=lambda: self.save_flight(entries, form)).grid(row=len(fields), column=0, columnspan=2, pady=10)

    def save_flight(self, entries, window):
        flight_data = {field: entry.get() for field, entry in entries.items()}
        print("Flight Data Saved:", flight_data)
        messagebox.showinfo("Info", "Flight saved successfully!")
        window.destroy()

    # =======================
    # Delete/Search placeholders
    # =======================
    def delete_client(self): messagebox.showinfo("Info", "Delete Client clicked")
    def search_client(self): messagebox.showinfo("Info", "Search Client clicked")
    def delete_airline(self): messagebox.showinfo("Info", "Delete Airline clicked")
    def search_airline(self): messagebox.showinfo("Info", "Search Airline clicked")
    def delete_flight(self): messagebox.showinfo("Info", "Delete Flight clicked")
    def search_flight(self): messagebox.showinfo("Info", "Search Flight clicked")

if __name__ == "__main__":
    app = RecordManagementSystem()
    app.mainloop()
