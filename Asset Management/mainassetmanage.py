import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import csv
import os
from tkcalendar import DateEntry  # Requires installation: pip install tkcalendar

# ISO 27001 compliance considerations
class ISOMetadata:
    def __init__(self):
        self.creation_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.last_modified = self.creation_date
        self.owner = "IT Hardware Asset Management"
        self.classification = "Confidential"
        self.retention_period = "5 years"
        
    def update_modified(self):
        self.last_modified = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Device types and roles
DEVICE_TYPES = ["Laptop", "Smartphone", "Desktop", "Walkie-Talkie", "Headset"]
EMPLOYEE_ROLES = [
    "Attendant (Office)", 
    "Attendant (WFH)", 
    "Manager", 
    "Coordinator", 
    "Supervisor", 
    "IT Manager", 
    "IT Analyst", 
    "Security Information Manager", 
    "Human Resources", 
    "Security Guard"
]

# Role-based device permissions
ROLE_DEVICE_MAPPING = {
    "Attendant (Office)": ["Desktop", "Headset"],
    "Attendant (WFH)": ["Desktop", "Headset"],
    "Manager": ["Laptop", "Smartphone"],
    "Coordinator": ["Laptop", "Smartphone"],
    "Supervisor": ["Desktop"],
    "IT Manager": ["Laptop", "Desktop"],
    "IT Analyst": ["Laptop", "Desktop"],
    "Security Information Manager": ["Laptop"],
    "Human Resources": ["Desktop"],
    "Security Guard": ["Walkie-Talkie"]
}

class AssetManagementSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("IT Hardware Asset Management System - ISO 27001 Compliance Features Included")
        self.root.geometry("1000x700")
        
        # ISO metadata for the system
        self.iso_metadata = ISOMetadata()
        
        # Data storage
        self.assets = []
        self.employees = []
        self.load_data()
        
        # Create tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(pady=10, expand=True, fill="both")
        
        # Create frames for tabs
        self.asset_frame = ttk.Frame(self.notebook, width=900, height=600)
        self.employee_frame = ttk.Frame(self.notebook, width=900, height=600)
        self.report_frame = ttk.Frame(self.notebook, width=900, height=600)
        self.audit_frame = ttk.Frame(self.notebook, width=900, height=600)
        
        self.asset_frame.pack(fill="both", expand=True)
        self.employee_frame.pack(fill="both", expand=True)
        self.report_frame.pack(fill="both", expand=True)
        self.audit_frame.pack(fill="both", expand=True)
        
        # Add tabs
        self.notebook.add(self.asset_frame, text="Asset Management")
        self.notebook.add(self.employee_frame, text="Employee Management")
        self.notebook.add(self.report_frame, text="Reports")
        self.notebook.add(self.audit_frame, text="Audit Logs")
        
        # Initialize tabs
        self.create_asset_tab()
        self.create_employee_tab()
        self.create_report_tab()
        self.create_audit_tab()
        
        # Add logout button
        self.logout_btn = ttk.Button(root, text="Logout", command=self.on_close)
        self.logout_btn.pack(pady=5)
        
        # Bind close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def load_data(self):
        # Load data from CSV files if they exist
        try:
            with open('assets.csv', mode='r') as file:
                reader = csv.DictReader(file)
                self.assets = list(reader)
        except FileNotFoundError:
            self.assets = []
            
        try:
            with open('employees.csv', mode='r') as file:
                reader = csv.DictReader(file)
                self.employees = list(reader)
        except FileNotFoundError:
            self.employees = []
            
        try:
            with open('audit_log.csv', mode='r') as file:
                reader = csv.DictReader(file)
                self.audit_logs = list(reader)
        except FileNotFoundError:
            self.audit_logs = []
    
    def save_data(self):
        # Save data to CSV files
        if self.assets:
            with open('assets.csv', mode='w', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=self.assets[0].keys())
                writer.writeheader()
                writer.writerows(self.assets)
                
        if self.employees:
            with open('employees.csv', mode='w', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=self.employees[0].keys())
                writer.writeheader()
                writer.writerows(self.employees)
                
        if self.audit_logs:
            with open('audit_log.csv', mode='w', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=self.audit_logs[0].keys())
                writer.writeheader()
                writer.writerows(self.audit_logs)
    
    def log_audit(self, action, details, user="System"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = {
            "timestamp": timestamp,
            "user": user,
            "action": action,
            "details": details,
            "iso_classification": self.iso_metadata.classification
        }
        self.audit_logs.append(log_entry)
        self.iso_metadata.update_modified()
    
    def create_asset_tab(self):
        # Asset ID
        ttk.Label(self.asset_frame, text="Asset ID:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.asset_id_entry = ttk.Entry(self.asset_frame)
        self.asset_id_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        # Device Type
        ttk.Label(self.asset_frame, text="Device Type:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.device_type_combo = ttk.Combobox(self.asset_frame, values=DEVICE_TYPES, state="readonly")
        self.device_type_combo.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        # Serial Number
        ttk.Label(self.asset_frame, text="Serial Number:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.serial_entry = ttk.Entry(self.asset_frame)
        self.serial_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        
        # Purchase Date
        ttk.Label(self.asset_frame, text="Purchase Date:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        self.purchase_date_entry = DateEntry(self.asset_frame)
        self.purchase_date_entry.grid(row=3, column=1, padx=5, pady=5, sticky="w")
        
        # Status
        ttk.Label(self.asset_frame, text="Status:").grid(row=4, column=0, padx=5, pady=5, sticky="e")
        self.status_combo = ttk.Combobox(self.asset_frame, values=["In Deposit", "Assigned"], state="readonly")
        self.status_combo.grid(row=4, column=1, padx=5, pady=5, sticky="w")
        
        # Assigned To
        ttk.Label(self.asset_frame, text="Assigned To:").grid(row=5, column=0, padx=5, pady=5, sticky="e")
        self.assigned_to_combo = ttk.Combobox(self.asset_frame, state="readonly")
        self.assigned_to_combo.grid(row=5, column=1, padx=5, pady=5, sticky="w")
        self.update_assigned_to_combo()
        
        # Assignment Date
        ttk.Label(self.asset_frame, text="Assignment Date:").grid(row=6, column=0, padx=5, pady=5, sticky="e")
        self.assignment_date_entry = DateEntry(self.asset_frame)
        self.assignment_date_entry.grid(row=6, column=1, padx=5, pady=5, sticky="w")
        
        # Location
        ttk.Label(self.asset_frame, text="Location:").grid(row=7, column=0, padx=5, pady=5, sticky="e")
        self.location_combo = ttk.Combobox(self.asset_frame, values=["Office", "Home"], state="readonly")
        self.location_combo.grid(row=7, column=1, padx=5, pady=5, sticky="w")
        
        # Buttons
        self.add_asset_btn = ttk.Button(self.asset_frame, text="Add Asset", command=self.add_asset)
        self.add_asset_btn.grid(row=8, column=0, padx=5, pady=10)
        
        self.update_asset_btn = ttk.Button(self.asset_frame, text="Update Asset", command=self.update_asset)
        self.update_asset_btn.grid(row=8, column=1, padx=5, pady=10)
        
        self.remove_asset_btn = ttk.Button(self.asset_frame, text="Remove Asset", command=self.remove_asset)
        self.remove_asset_btn.grid(row=8, column=2, padx=5, pady=10)
        
        # Asset Treeview
        self.asset_tree = ttk.Treeview(self.asset_frame, columns=("ID", "Type", "Serial", "Status", "Assigned To", "Location"), show="headings")
        self.asset_tree.heading("ID", text="Asset ID")
        self.asset_tree.heading("Type", text="Device Type")
        self.asset_tree.heading("Serial", text="Serial Number")
        self.asset_tree.heading("Status", text="Status")
        self.asset_tree.heading("Assigned To", text="Assigned To")
        self.asset_tree.heading("Location", text="Location")
        self.asset_tree.grid(row=9, column=0, columnspan=3, padx=5, pady=5, sticky="nsew")
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(self.asset_frame, orient="vertical", command=self.asset_tree.yview)
        scrollbar.grid(row=9, column=3, sticky="ns")
        self.asset_tree.configure(yscrollcommand=scrollbar.set)
        
        # Bind selection event
        self.asset_tree.bind("<<TreeviewSelect>>", self.on_asset_select)
        
        # Configure grid weights
        self.asset_frame.grid_rowconfigure(9, weight=1)
        self.asset_frame.grid_columnconfigure(0, weight=1)
        self.asset_frame.grid_columnconfigure(1, weight=1)
        self.asset_frame.grid_columnconfigure(2, weight=1)
        
        # Update treeview
        self.update_asset_tree()
    
    def create_employee_tab(self):
        # Employee ID
        ttk.Label(self.employee_frame, text="Employee ID:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.emp_id_entry = ttk.Entry(self.employee_frame)
        self.emp_id_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        # Employee Name
        ttk.Label(self.employee_frame, text="Name:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.emp_name_entry = ttk.Entry(self.employee_frame)
        self.emp_name_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        # Role
        ttk.Label(self.employee_frame, text="Role:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.role_combo = ttk.Combobox(self.employee_frame, values=EMPLOYEE_ROLES, state="readonly")
        self.role_combo.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        
        # Department
        ttk.Label(self.employee_frame, text="Department:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        self.dept_combo = ttk.Combobox(self.employee_frame, values=["Customer Service", "IT", "Security", "HR", "Management"], state="readonly")
        self.dept_combo.grid(row=3, column=1, padx=5, pady=5, sticky="w")
        
        # Hire Date
        ttk.Label(self.employee_frame, text="Hire Date:").grid(row=4, column=0, padx=5, pady=5, sticky="e")
        self.hire_date_entry = DateEntry(self.employee_frame)
        self.hire_date_entry.grid(row=4, column=1, padx=5, pady=5, sticky="w")
        
        # Buttons
        self.add_emp_btn = ttk.Button(self.employee_frame, text="Add Employee", command=self.add_employee)
        self.add_emp_btn.grid(row=5, column=0, padx=5, pady=10)
        
        self.update_emp_btn = ttk.Button(self.employee_frame, text="Update Employee", command=self.update_employee)
        self.update_emp_btn.grid(row=5, column=1, padx=5, pady=10)
        
        self.remove_emp_btn = ttk.Button(self.employee_frame, text="Remove Employee", command=self.remove_employee)
        self.remove_emp_btn.grid(row=5, column=2, padx=5, pady=10)
        
        # Employee Treeview
        self.emp_tree = ttk.Treeview(self.employee_frame, columns=("ID", "Name", "Role", "Department", "Hire Date"), show="headings")
        self.emp_tree.heading("ID", text="Employee ID")
        self.emp_tree.heading("Name", text="Name")
        self.emp_tree.heading("Role", text="Role")
        self.emp_tree.heading("Department", text="Department")
        self.emp_tree.heading("Hire Date", text="Hire Date")
        self.emp_tree.grid(row=6, column=0, columnspan=3, padx=5, pady=5, sticky="nsew")
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(self.employee_frame, orient="vertical", command=self.emp_tree.yview)
        scrollbar.grid(row=6, column=3, sticky="ns")
        self.emp_tree.configure(yscrollcommand=scrollbar.set)
        
        # Bind selection event
        self.emp_tree.bind("<<TreeviewSelect>>", self.on_emp_select)
        
        # Configure grid weights
        self.employee_frame.grid_rowconfigure(6, weight=1)
        self.employee_frame.grid_columnconfigure(0, weight=1)
        self.employee_frame.grid_columnconfigure(1, weight=1)
        self.employee_frame.grid_columnconfigure(2, weight=1)
        
        # Update treeview
        self.update_emp_tree()
    
    def create_report_tab(self):
        # Report type selection
        ttk.Label(self.report_frame, text="Report Type:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.report_type_combo = ttk.Combobox(self.report_frame, 
                                           values=["All Assets", 
                                                  "Assigned Assets", 
                                                  "Unassigned Assets",
                                                  "Assets by Type",
                                                  "Assets by Location",
                                                  "Employee Asset Report"], 
                                           state="readonly")
        self.report_type_combo.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        # Generate report button
        self.generate_report_btn = ttk.Button(self.report_frame, text="Generate Report", command=self.generate_report)
        self.generate_report_btn.grid(row=0, column=2, padx=5, pady=5)
        
        # Export button
        self.export_report_btn = ttk.Button(self.report_frame, text="Export to CSV", command=self.export_report)
        self.export_report_btn.grid(row=0, column=3, padx=5, pady=5)
        
        # Report display
        self.report_text = tk.Text(self.report_frame, wrap=tk.WORD)
        self.report_text.grid(row=1, column=0, columnspan=4, padx=5, pady=5, sticky="nsew")
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(self.report_frame, orient="vertical", command=self.report_text.yview)
        scrollbar.grid(row=1, column=4, sticky="ns")
        self.report_text.configure(yscrollcommand=scrollbar.set)
        
        # Configure grid weights
        self.report_frame.grid_rowconfigure(1, weight=1)
        self.report_frame.grid_columnconfigure(0, weight=1)
        self.report_frame.grid_columnconfigure(1, weight=1)
        self.report_frame.grid_columnconfigure(2, weight=1)
        self.report_frame.grid_columnconfigure(3, weight=1)
    
    def create_audit_tab(self):
        # Audit log display
        self.audit_tree = ttk.Treeview(self.audit_frame, columns=("Timestamp", "User", "Action", "Details"), show="headings")
        self.audit_tree.heading("Timestamp", text="Timestamp")
        self.audit_tree.heading("User", text="User")
        self.audit_tree.heading("Action", text="Action")
        self.audit_tree.heading("Details", text="Details")
        self.audit_tree.grid(row=0, column=0, columnspan=4, padx=5, pady=5, sticky="nsew")
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(self.audit_frame, orient="vertical", command=self.audit_tree.yview)
        scrollbar.grid(row=0, column=4, sticky="ns")
        self.audit_tree.configure(yscrollcommand=scrollbar.set)
        
        # Filter options
        ttk.Label(self.audit_frame, text="Filter by Date:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.audit_date_from = DateEntry(self.audit_frame)
        self.audit_date_from.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Label(self.audit_frame, text="to").grid(row=1, column=2, padx=5, pady=5)
        self.audit_date_to = DateEntry(self.audit_frame)
        self.audit_date_to.grid(row=1, column=3, padx=5, pady=5, sticky="w")
        
        # Filter button
        self.filter_audit_btn = ttk.Button(self.audit_frame, text="Filter", command=self.filter_audit_logs)
        self.filter_audit_btn.grid(row=1, column=4, padx=5, pady=5)
        
        # Configure grid weights
        self.audit_frame.grid_rowconfigure(0, weight=1)
        self.audit_frame.grid_columnconfigure(0, weight=1)
        self.audit_frame.grid_columnconfigure(1, weight=1)
        self.audit_frame.grid_columnconfigure(2, weight=1)
        self.audit_frame.grid_columnconfigure(3, weight=1)
        
        # Update audit log display
        self.update_audit_tree()
    
    def update_assigned_to_combo(self):
        employee_names = [f"{emp['employee_id']} - {emp['name']}" for emp in self.employees]
        self.assigned_to_combo['values'] = employee_names
    
    def update_asset_tree(self):
        # Clear existing items
        for item in self.asset_tree.get_children():
            self.asset_tree.delete(item)
            
        # Add assets to treeview
        for asset in self.assets:
            assigned_to = asset.get('assigned_to', 'N/A')
            if assigned_to != 'N/A':
                # Find employee name
                for emp in self.employees:
                    if emp['employee_id'] == assigned_to:
                        assigned_to = f"{emp['employee_id']} - {emp['name']}"
                        break
            
            self.asset_tree.insert("", "end", values=(
                asset['asset_id'],
                asset['device_type'],
                asset['serial_number'],
                asset['status'],
                assigned_to,
                asset.get('location', 'Office')
            ))
    
    def update_emp_tree(self):
        # Clear existing items
        for item in self.emp_tree.get_children():
            self.emp_tree.delete(item)
            
        # Add employees to treeview
        for emp in self.employees:
            self.emp_tree.insert("", "end", values=(
                emp['employee_id'],
                emp['name'],
                emp['role'],
                emp['department'],
                emp['hire_date']
            ))
    
    def update_audit_tree(self):
        # Clear existing items
        for item in self.audit_tree.get_children():
            self.audit_tree.delete(item)
            
        # Add audit logs to treeview
        for log in self.audit_logs[-100:]:  # Show last 100 entries by default
            self.audit_tree.insert("", "end", values=(
                log['timestamp'],
                log['user'],
                log['action'],
                log['details']
            ))
    
    def on_asset_select(self, event):
        selected = self.asset_tree.focus()
        if not selected:
            return
            
        values = self.asset_tree.item(selected, 'values')
        if not values:
            return
            
        # Find the asset in the list
        asset_id = values[0]
        asset = next((a for a in self.assets if a['asset_id'] == asset_id), None)
        
        if asset:
            self.asset_id_entry.delete(0, tk.END)
            self.asset_id_entry.insert(0, asset['asset_id'])
            
            self.device_type_combo.set(asset['device_type'])
            self.serial_entry.delete(0, tk.END)
            self.serial_entry.insert(0, asset['serial_number'])
            
            # Set purchase date
            try:
                purchase_date = datetime.strptime(asset['purchase_date'], "%Y-%m-%d")
                self.purchase_date_entry.set_date(purchase_date)
            except:
                pass
            
            self.status_combo.set(asset['status'])
            
            # Set assigned to
            assigned_to = asset.get('assigned_to', '')
            if assigned_to:
                # Find employee name
                for emp in self.employees:
                    if emp['employee_id'] == assigned_to:
                        self.assigned_to_combo.set(f"{emp['employee_id']} - {emp['name']}")
                        break
            else:
                self.assigned_to_combo.set('')
            
            # Set assignment date
            if 'assignment_date' in asset:
                try:
                    assignment_date = datetime.strptime(asset['assignment_date'], "%Y-%m-%d")
                    self.assignment_date_entry.set_date(assignment_date)
                except:
                    pass
            
            self.location_combo.set(asset.get('location', 'Office'))
    
    def on_emp_select(self, event):
        selected = self.emp_tree.focus()
        if not selected:
            return
            
        values = self.emp_tree.item(selected, 'values')
        if not values:
            return
            
        # Find the employee in the list
        emp_id = values[0]
        emp = next((e for e in self.employees if e['employee_id'] == emp_id), None)
        
        if emp:
            self.emp_id_entry.delete(0, tk.END)
            self.emp_id_entry.insert(0, emp['employee_id'])
            
            self.emp_name_entry.delete(0, tk.END)
            self.emp_name_entry.insert(0, emp['name'])
            
            self.role_combo.set(emp['role'])
            self.dept_combo.set(emp['department'])
            
            # Set hire date
            try:
                hire_date = datetime.strptime(emp['hire_date'], "%Y-%m-%d")
                self.hire_date_entry.set_date(hire_date)
            except:
                pass
    
    def add_asset(self):
        asset_id = self.asset_id_entry.get().strip()
        device_type = self.device_type_combo.get()
        serial_number = self.serial_entry.get().strip()
        purchase_date = self.purchase_date_entry.get_date().strftime("%Y-%m-%d")
        status = self.status_combo.get()
        assigned_to = self.assigned_to_combo.get()
        assignment_date = self.assignment_date_entry.get_date().strftime("%Y-%m-%d")
        location = self.location_combo.get()
        
        # Validate inputs
        if not all([asset_id, device_type, serial_number, purchase_date, status]):
            messagebox.showerror("Error", "Please fill all required fields!")
            return
            
        # Check if asset ID already exists
        if any(a['asset_id'] == asset_id for a in self.assets):
            messagebox.showerror("Error", "Asset ID already exists!")
            return
            
        # Extract employee ID from assigned_to if it's not empty
        emp_id = ""
        if assigned_to:
            emp_id = assigned_to.split(" - ")[0]
            
            # Check if employee exists
            if not any(e['employee_id'] == emp_id for e in self.employees):
                messagebox.showerror("Error", "Selected employee doesn't exist!")
                return
                
            # Check if device type is allowed for employee's role
            emp = next(e for e in self.employees if e['employee_id'] == emp_id)
            allowed_devices = ROLE_DEVICE_MAPPING.get(emp['role'], [])
            
            if device_type not in allowed_devices:
                messagebox.showerror("Error", f"This device type is not allowed for {emp['role']} role!")
                return
        
        # Create asset dictionary
        asset = {
            "asset_id": asset_id,
            "device_type": device_type,
            "serial_number": serial_number,
            "purchase_date": purchase_date,
            "status": status,
            "assigned_to": emp_id if assigned_to else "",
            "assignment_date": assignment_date if assigned_to else "",
            "location": location if status == "Assigned" else "Deposit"
        }
        
        # Add to assets list
        self.assets.append(asset)
        
        # Update treeview
        self.update_asset_tree()
        
        # Clear form
        self.clear_asset_form()
        
        # Log the action
        self.log_audit("Add Asset", f"Added asset {asset_id} ({device_type})")
        
        messagebox.showinfo("Success", "Asset added successfully!")
    
    def update_asset(self):
        selected = self.asset_tree.focus()
        if not selected:
            messagebox.showerror("Error", "Please select an asset to update!")
            return
            
        values = self.asset_tree.item(selected, 'values')
        if not values:
            return
            
        asset_id = values[0]
        
        # Get updated values
        new_device_type = self.device_type_combo.get()
        new_serial = self.serial_entry.get().strip()
        new_purchase_date = self.purchase_date_entry.get_date().strftime("%Y-%m-%d")
        new_status = self.status_combo.get()
        new_assigned_to = self.assigned_to_combo.get()
        new_assignment_date = self.assignment_date_entry.get_date().strftime("%Y-%m-%d")
        new_location = self.location_combo.get()
        
        # Validate inputs
        if not all([new_device_type, new_serial, new_purchase_date, new_status]):
            messagebox.showerror("Error", "Please fill all required fields!")
            return
            
        # Find the asset
        asset = next((a for a in self.assets if a['asset_id'] == asset_id), None)
        if not asset:
            messagebox.showerror("Error", "Asset not found!")
            return
            
        # Extract employee ID from assigned_to if it's not empty
        emp_id = ""
        if new_assigned_to:
            emp_id = new_assigned_to.split(" - ")[0]
            
            # Check if employee exists
            if not any(e['employee_id'] == emp_id for e in self.employees):
                messagebox.showerror("Error", "Selected employee doesn't exist!")
                return
                
            # Check if device type is allowed for employee's role
            emp = next(e for e in self.employees if e['employee_id'] == emp_id)
            allowed_devices = ROLE_DEVICE_MAPPING.get(emp['role'], [])
            
            if new_device_type not in allowed_devices:
                messagebox.showerror("Error", f"This device type is not allowed for {emp['role']} role!")
                return
        
        # Update asset
        asset['device_type'] = new_device_type
        asset['serial_number'] = new_serial
        asset['purchase_date'] = new_purchase_date
        asset['status'] = new_status
        asset['assigned_to'] = emp_id if new_assigned_to else ""
        asset['assignment_date'] = new_assignment_date if new_assigned_to else ""
        asset['location'] = new_location if new_status == "Assigned" else "Deposit"
        
        # Update treeview
        self.update_asset_tree()
        
        # Clear form
        self.clear_asset_form()
        
        # Log the action
        self.log_audit("Update Asset", f"Updated asset {asset_id}")
        
        messagebox.showinfo("Success", "Asset updated successfully!")
    
    def remove_asset(self):
        selected = self.asset_tree.focus()
        if not selected:
            messagebox.showerror("Error", "Please select an asset to remove!")
            return
            
        values = self.asset_tree.item(selected, 'values')
        if not values:
            return
            
        asset_id = values[0]
        
        # Confirm deletion
        if not messagebox.askyesno("Confirm", f"Are you sure you want to remove asset {asset_id}?"):
            return
            
        # Find and remove the asset
        self.assets = [a for a in self.assets if a['asset_id'] != asset_id]
        
        # Update treeview
        self.update_asset_tree()
        
        # Clear form
        self.clear_asset_form()
        
        # Log the action
        self.log_audit("Remove Asset", f"Removed asset {asset_id}")
        
        messagebox.showinfo("Success", "Asset removed successfully!")
    
    def clear_asset_form(self):
        self.asset_id_entry.delete(0, tk.END)
        self.device_type_combo.set('')
        self.serial_entry.delete(0, tk.END)
        self.purchase_date_entry.set_date(datetime.now())
        self.status_combo.set('')
        self.assigned_to_combo.set('')
        self.assignment_date_entry.set_date(datetime.now())
        self.location_combo.set('Office')
    
    def add_employee(self):
        emp_id = self.emp_id_entry.get().strip()
        name = self.emp_name_entry.get().strip()
        role = self.role_combo.get()
        department = self.dept_combo.get()
        hire_date = self.hire_date_entry.get_date().strftime("%Y-%m-%d")
        
        # Validate inputs
        if not all([emp_id, name, role, department, hire_date]):
            messagebox.showerror("Error", "Please fill all required fields!")
            return
            
        # Check if employee ID already exists
        if any(e['employee_id'] == emp_id for e in self.employees):
            messagebox.showerror("Error", "Employee ID already exists!")
            return
            
        # Create employee dictionary
        employee = {
            "employee_id": emp_id,
            "name": name,
            "role": role,
            "department": department,
            "hire_date": hire_date
        }
        
        # Add to employees list
        self.employees.append(employee)
        
        # Update treeview and assigned_to combo
        self.update_emp_tree()
        self.update_assigned_to_combo()
        
        # Clear form
        self.clear_emp_form()
        
        # Log the action
        self.log_audit("Add Employee", f"Added employee {emp_id} - {name}")
        
        messagebox.showinfo("Success", "Employee added successfully!")
    
    def update_employee(self):
        selected = self.emp_tree.focus()
        if not selected:
            messagebox.showerror("Error", "Please select an employee to update!")
            return
            
        values = self.emp_tree.item(selected, 'values')
        if not values:
            return
            
        emp_id = values[0]
        
        # Get updated values
        new_name = self.emp_name_entry.get().strip()
        new_role = self.role_combo.get()
        new_dept = self.dept_combo.get()
        new_hire_date = self.hire_date_entry.get_date().strftime("%Y-%m-%d")
        
        # Validate inputs
        if not all([new_name, new_role, new_dept, new_hire_date]):
            messagebox.showerror("Error", "Please fill all required fields!")
            return
            
        # Find the employee
        employee = next((e for e in self.employees if e['employee_id'] == emp_id), None)
        if not employee:
            messagebox.showerror("Error", "Employee not found!")
            return
            
        # Check if role change affects existing asset assignments
        if employee['role'] != new_role:
            # Find all assets assigned to this employee
            assigned_assets = [a for a in self.assets if a.get('assigned_to') == emp_id]
            
            for asset in assigned_assets:
                # Check if device is still allowed with new role
                allowed_devices = ROLE_DEVICE_MAPPING.get(new_role, [])
                if asset['device_type'] not in allowed_devices:
                    messagebox.showerror("Error", 
                        f"Cannot change role because employee has {asset['device_type']} assigned which is not allowed for {new_role}!")
                    return
        
        # Update employee
        employee['name'] = new_name
        employee['role'] = new_role
        employee['department'] = new_dept
        employee['hire_date'] = new_hire_date
        
        # Update treeview and assigned_to combo
        self.update_emp_tree()
        self.update_assigned_to_combo()
        
        # Clear form
        self.clear_emp_form()
        
        # Log the action
        self.log_audit("Update Employee", f"Updated employee {emp_id}")
        
        messagebox.showinfo("Success", "Employee updated successfully!")
    
    def remove_employee(self):
        selected = self.emp_tree.focus()
        if not selected:
            messagebox.showerror("Error", "Please select an employee to remove!")
            return
            
        values = self.emp_tree.item(selected, 'values')
        if not values:
            return
            
        emp_id = values[0]
        
        # Check if employee has assets assigned
        assigned_assets = [a for a in self.assets if a.get('assigned_to') == emp_id]
        if assigned_assets:
            messagebox.showerror("Error", 
                "Cannot remove employee with assigned assets. Please unassign assets first!")
            return
            
        # Confirm deletion
        if not messagebox.askyesno("Confirm", f"Are you sure you want to remove employee {emp_id}?"):
            return
            
        # Find and remove the employee
        self.employees = [e for e in self.employees if e['employee_id'] != emp_id]
        
        # Update treeview and assigned_to combo
        self.update_emp_tree()
        self.update_assigned_to_combo()
        
        # Clear form
        self.clear_emp_form()
        
        # Log the action
        self.log_audit("Remove Employee", f"Removed employee {emp_id}")
        
        messagebox.showinfo("Success", "Employee removed successfully!")
    
    def clear_emp_form(self):
        self.emp_id_entry.delete(0, tk.END)
        self.emp_name_entry.delete(0, tk.END)
        self.role_combo.set('')
        self.dept_combo.set('')
        self.hire_date_entry.set_date(datetime.now())
    
    def generate_report(self):
        report_type = self.report_type_combo.get()
        if not report_type:
            messagebox.showerror("Error", "Please select a report type!")
            return
            
        self.report_text.delete(1.0, tk.END)
        
        if report_type == "All Assets":
            self.generate_all_assets_report()
        elif report_type == "Assigned Assets":
            self.generate_assigned_assets_report()
        elif report_type == "Unassigned Assets":
            self.generate_unassigned_assets_report()
        elif report_type == "Assets by Type":
            self.generate_assets_by_type_report()
        elif report_type == "Assets by Location":
            self.generate_assets_by_location_report()
        elif report_type == "Employee Asset Report":
            self.generate_employee_asset_report()
        
        # Log the action
        self.log_audit("Generate Report", f"Generated {report_type} report")
    
    def generate_all_assets_report(self):
        self.report_text.insert(tk.END, "ALL ASSETS REPORT\n")
        self.report_text.insert(tk.END, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        self.report_text.insert(tk.END, "="*50 + "\n\n")
        
        headers = ["Asset ID", "Device Type", "Serial", "Status", "Assigned To", "Location", "Purchase Date"]
        row_format = "{:<15} {:<15} {:<20} {:<15} {:<25} {:<15} {:<15}\n"
        
        self.report_text.insert(tk.END, row_format.format(*headers))
        self.report_text.insert(tk.END, "-"*120 + "\n")
        
        for asset in sorted(self.assets, key=lambda x: x['device_type']):
            assigned_to = asset.get('assigned_to', 'N/A')
            if assigned_to != 'N/A':
                # Find employee name
                for emp in self.employees:
                    if emp['employee_id'] == assigned_to:
                        assigned_to = f"{emp['name']} ({emp['employee_id']})"
                        break
            
            row = [
                asset['asset_id'],
                asset['device_type'],
                asset['serial_number'],
                asset['status'],
                assigned_to,
                asset.get('location', 'Office'),
                asset['purchase_date']
            ]
            self.report_text.insert(tk.END, row_format.format(*row))
        
        self.report_text.insert(tk.END, "\n" + "="*50 + "\n")
        self.report_text.insert(tk.END, f"Total Assets: {len(self.assets)}\n")
    
    def generate_assigned_assets_report(self):
        assigned_assets = [a for a in self.assets if a['status'] == "Assigned"]
        
        self.report_text.insert(tk.END, "ASSIGNED ASSETS REPORT\n")
        self.report_text.insert(tk.END, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        self.report_text.insert(tk.END, "="*50 + "\n\n")
        
        headers = ["Asset ID", "Device Type", "Serial", "Assigned To", "Role", "Department", "Location"]
        row_format = "{:<15} {:<15} {:<20} {:<25} {:<20} {:<15} {:<15}\n"
        
        self.report_text.insert(tk.END, row_format.format(*headers))
        self.report_text.insert(tk.END, "-"*120 + "\n")
        
        for asset in sorted(assigned_assets, key=lambda x: x['device_type']):
            assigned_to = asset.get('assigned_to', '')
            emp_name = "N/A"
            role = "N/A"
            dept = "N/A"
            
            if assigned_to:
                # Find employee details
                for emp in self.employees:
                    if emp['employee_id'] == assigned_to:
                        emp_name = f"{emp['name']} ({emp['employee_id']})"
                        role = emp['role']
                        dept = emp['department']
                        break
            
            row = [
                asset['asset_id'],
                asset['device_type'],
                asset['serial_number'],
                emp_name,
                role,
                dept,
                asset.get('location', 'Office')
            ]
            self.report_text.insert(tk.END, row_format.format(*row))
        
        self.report_text.insert(tk.END, "\n" + "="*50 + "\n")
        self.report_text.insert(tk.END, f"Total Assigned Assets: {len(assigned_assets)}\n")
    
    def generate_unassigned_assets_report(self):
        unassigned_assets = [a for a in self.assets if a['status'] != "Assigned"]
        
        self.report_text.insert(tk.END, "UNASSIGNED ASSETS REPORT\n")
        self.report_text.insert(tk.END, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        self.report_text.insert(tk.END, "="*50 + "\n\n")
        
        headers = ["Asset ID", "Device Type", "Serial", "Status", "Purchase Date"]
        row_format = "{:<15} {:<15} {:<20} {:<15} {:<15}\n"
        
        self.report_text.insert(tk.END, row_format.format(*headers))
        self.report_text.insert(tk.END, "-"*80 + "\n")
        
        for asset in sorted(unassigned_assets, key=lambda x: x['device_type']):
            row = [
                asset['asset_id'],
                asset['device_type'],
                asset['serial_number'],
                asset['status'],
                asset['purchase_date']
            ]
            self.report_text.insert(tk.END, row_format.format(*row))
        
        self.report_text.insert(tk.END, "\n" + "="*50 + "\n")
        self.report_text.insert(tk.END, f"Total Unassigned Assets: {len(unassigned_assets)}\n")
    
    def generate_assets_by_type_report(self):
        self.report_text.insert(tk.END, "ASSETS BY TYPE REPORT\n")
        self.report_text.insert(tk.END, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        self.report_text.insert(tk.END, "="*50 + "\n\n")
        
        # Count by type
        type_counts = {}
        for asset in self.assets:
            device_type = asset['device_type']
            type_counts[device_type] = type_counts.get(device_type, 0) + 1
        
        # Sort by count descending
        sorted_types = sorted(type_counts.items(), key=lambda x: x[1], reverse=True)
        
        headers = ["Device Type", "Count", "Percentage"]
        row_format = "{:<20} {:<10} {:<10}\n"
        
        self.report_text.insert(tk.END, row_format.format(*headers))
        self.report_text.insert(tk.END, "-"*40 + "\n")
        
        total_assets = len(self.assets)
        for device_type, count in sorted_types:
            percentage = (count / total_assets) * 100 if total_assets > 0 else 0
            row = [
                device_type,
                str(count),
                f"{percentage:.1f}%"
            ]
            self.report_text.insert(tk.END, row_format.format(*row))
        
        self.report_text.insert(tk.END, "\n" + "="*50 + "\n")
        self.report_text.insert(tk.END, f"Total Assets: {total_assets}\n")
    
    def generate_assets_by_location_report(self):
        self.report_text.insert(tk.END, "ASSETS BY LOCATION REPORT\n")
        self.report_text.insert(tk.END, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        self.report_text.insert(tk.END, "="*50 + "\n\n")
        
        # Count by location
        location_counts = {}
        for asset in self.assets:
            location = asset.get('location', 'Deposit')
            location_counts[location] = location_counts.get(location, 0) + 1
        
        # Sort by count descending
        sorted_locations = sorted(location_counts.items(), key=lambda x: x[1], reverse=True)
        
        headers = ["Location", "Count", "Percentage"]
        row_format = "{:<20} {:<10} {:<10}\n"
        
        self.report_text.insert(tk.END, row_format.format(*headers))
        self.report_text.insert(tk.END, "-"*40 + "\n")
        
        total_assets = len(self.assets)
        for location, count in sorted_locations:
            percentage = (count / total_assets) * 100 if total_assets > 0 else 0
            row = [
                location,
                str(count),
                f"{percentage:.1f}%"
            ]
            self.report_text.insert(tk.END, row_format.format(*row))
        
        self.report_text.insert(tk.END, "\n" + "="*50 + "\n")
        self.report_text.insert(tk.END, f"Total Assets: {total_assets}\n")
    
    def generate_employee_asset_report(self):
        self.report_text.insert(tk.END, "EMPLOYEE ASSET REPORT\n")
        self.report_text.insert(tk.END, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        self.report_text.insert(tk.END, "="*50 + "\n\n")
        
        headers = ["Employee ID", "Name", "Role", "Department", "Assets Assigned", "Device Types"]
        row_format = "{:<15} {:<20} {:<20} {:<15} {:<15} {:<30}\n"
        
        self.report_text.insert(tk.END, row_format.format(*headers))
        self.report_text.insert(tk.END, "-"*120 + "\n")
        
        for emp in sorted(self.employees, key=lambda x: x['role']):
            # Find assets assigned to this employee
            assigned_assets = [a for a in self.assets if a.get('assigned_to') == emp['employee_id']]
            device_types = ", ".join(set(a['device_type'] for a in assigned_assets))
            
            row = [
                emp['employee_id'],
                emp['name'],
                emp['role'],
                emp['department'],
                str(len(assigned_assets)),
                device_types
            ]
            self.report_text.insert(tk.END, row_format.format(*row))
        
        self.report_text.insert(tk.END, "\n" + "="*50 + "\n")
        self.report_text.insert(tk.END, f"Total Employees: {len(self.employees)}\n")
    
    def export_report(self):
        report_text = self.report_text.get(1.0, tk.END)
        if not report_text.strip():
            messagebox.showerror("Error", "No report to export!")
            return
            
        filename = f"asset_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        try:
            with open(filename, 'w') as file:
                # Convert the text report to CSV format
                lines = report_text.split('\n')
                for line in lines:
                    # Split on multiple spaces (simple approach for demo)
                    row = [x for x in line.split('  ') if x.strip()]
                    file.write(','.join(row) + '\n')
            
            # Log the action
            self.log_audit("Export Report", f"Exported report to {filename}")
            
            messagebox.showinfo("Success", f"Report exported to {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export report: {str(e)}")
    
    def filter_audit_logs(self):
        date_from = self.audit_date_from.get_date()
        date_to = self.audit_date_to.get_date()
        
        # Clear existing items
        for item in self.audit_tree.get_children():
            self.audit_tree.delete(item)
            
        # Add filtered logs to treeview
        for log in self.audit_logs:
            try:
                log_date = datetime.strptime(log['timestamp'], "%Y-%m-%d %H:%M:%S").date()
                if date_from <= log_date <= date_to:
                    self.audit_tree.insert("", "end", values=(
                        log['timestamp'],
                        log['user'],
                        log['action'],
                        log['details']
                    ))
            except:
                continue
        
        # Log the action
        self.log_audit("Filter Audit Logs", f"Filtered logs from {date_from} to {date_to}")
    
    def on_close(self):
        # Save data before closing
        self.save_data()
        
        # Log the action
        self.log_audit("System Shutdown", "Asset management system closed")
        
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = AssetManagementSystem(root)
    root.mainloop()
