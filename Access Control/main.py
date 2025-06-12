import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
import json
import os

class AccessControlSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Employee Access Control System")
        self.root.geometry("1200x700")  # Larger window size
        
        # Configure style for larger widgets
        self.style = ttk.Style()
        self.style.configure('TButton', padding=6)
        self.style.configure('TEntry', padding=6)
        self.style.configure('TCombobox', padding=6)
        
        # Data storage
        self.employees = []
        self.access_log = []
        self.door_readers = {
            100: "Main Entrance Turnstile",
            101: "Engineering Workroom",
            102: "Server Room",
            106: "Cafeteria",
            107: "Restrooms",
            108: "IT Closet",
            109: "Security Office",
            110: "Executive Suite",
            112: "Financial Office",
            113: "Reception",
            115: "HR Department"
        }
        
        # Logical Access Control data
        self.logical_resources = {
            "NETWORK": ["VPN", "WiFi", "LAN"],
            "SYSTEMS": ["CRM", "ERP", "Accounting"],
            "DATA": ["Customer DB", "Financials", "HR Records"]
        }
        self.logical_access_rules = []
        self.logical_access_log = []
        
        # Load existing data
        self.load_data()
        
        # Create GUI
        self.create_widgets()
        
    def create_widgets(self):
        # Notebook for multiple tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Physical Access Control Tab
        self.physical_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.physical_tab, text="Physical Access Control")
        
        # Employee Management Tab
        self.employee_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.employee_tab, text="Employee Management")
        
        # Door Management Tab
        self.door_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.door_tab, text="Door Management")
        
        # Logical Access Control Tab
        self.logical_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.logical_tab, text="Logical Access Control")
        
        # Logs Tab
        self.logs_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.logs_tab, text="Access Logs")
        
        # Build each tab
        self.build_physical_tab()
        self.build_employee_tab()
        self.build_door_tab()
        self.build_logical_tab()
        self.build_logs_tab()
    
    def build_physical_tab(self):
        # Frame for better organization
        access_frame = ttk.Frame(self.physical_tab)
        access_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Badge Entry
        ttk.Label(access_frame, text="Badge Number:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.badge_entry = ttk.Entry(access_frame, width=25)
        self.badge_entry.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        # Door Reader Selection
        ttk.Label(access_frame, text="Door Reader:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.door_combobox = ttk.Combobox(access_frame, values=list(self.door_readers.values()), width=25)
        self.door_combobox.grid(row=1, column=1, padx=10, pady=10, sticky="w")
        self.door_combobox.current(0)
        
        # Access Button
        self.access_button = ttk.Button(access_frame, text="Attempt Access", command=self.attempt_access, width=20)
        self.access_button.grid(row=2, column=0, columnspan=2, pady=15)
        
        # Status Display
        self.status_label = ttk.Label(access_frame, text="Ready for badge scan...", font=('Arial', 12))
        self.status_label.grid(row=3, column=0, columnspan=2, pady=15)
        
        # Turnstile Control
        ttk.Label(access_frame, text="Turnstile Control:").grid(row=4, column=0, padx=10, pady=10, sticky="e")
        self.turnstile_button = ttk.Button(access_frame, text="Unlock Turnstile", command=self.unlock_turnstile, width=20)
        self.turnstile_button.grid(row=4, column=1, padx=10, pady=10, sticky="w")
        self.turnstile_button.config(state=tk.DISABLED)
    
    def build_employee_tab(self):
        # Frame for employee list and search
        list_frame = ttk.Frame(self.employee_tab)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Search Frame
        search_frame = ttk.Frame(list_frame)
        search_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=5)
        self.employee_search = ttk.Entry(search_frame, width=30)
        self.employee_search.pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="Search", command=self.search_employees).pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="Clear", command=self.refresh_employee_list).pack(side=tk.LEFT, padx=5)
        
        # Employee List Treeview
        self.employee_tree = ttk.Treeview(list_frame, columns=("Name", "Badge", "Role", "Access Doors", "Badge Type"))
        self.employee_tree.heading("#0", text="ID")
        self.employee_tree.heading("Name", text="Name")
        self.employee_tree.heading("Badge", text="Badge Number")
        self.employee_tree.heading("Role", text="Role")
        self.employee_tree.heading("Access Doors", text="Access Doors")
        self.employee_tree.heading("Badge Type", text="Badge Type")
        
        # Add scrollbars
        yscroll = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.employee_tree.yview)
        xscroll = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL, command=self.employee_tree.xview)
        self.employee_tree.configure(yscroll=yscroll.set, xscroll=xscroll.set)
        
        self.employee_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        yscroll.pack(side=tk.RIGHT, fill=tk.Y)
        xscroll.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Employee Form
        form_frame = ttk.Frame(self.employee_tab)
        form_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(form_frame, text="Name:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
        self.emp_name = ttk.Entry(form_frame, width=30)
        self.emp_name.grid(row=0, column=1, padx=10, pady=5, sticky="w")
        
        ttk.Label(form_frame, text="Badge Number:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.emp_badge = ttk.Entry(form_frame, width=30)
        self.emp_badge.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        
        ttk.Label(form_frame, text="Role:").grid(row=2, column=0, padx=10, pady=5, sticky="e")
        self.emp_role = ttk.Combobox(form_frame, values=["Employee", "IT Manager", "Senior IT", "Junior IT", "HR Manager", "HR Staff", "Security", "Finance", "Visitor"], width=27)
        self.emp_role.grid(row=2, column=1, padx=10, pady=5, sticky="w")
        
        ttk.Label(form_frame, text="Access Doors:").grid(row=3, column=0, padx=10, pady=5, sticky="e")
        self.emp_doors = ttk.Entry(form_frame, width=30)
        self.emp_doors.grid(row=3, column=1, padx=10, pady=5, sticky="w")
        
        ttk.Label(form_frame, text="Badge Type:").grid(row=4, column=0, padx=10, pady=5, sticky="e")
        self.emp_badge_type = ttk.Combobox(form_frame, values=["Permanent", "Temporary (24h)"], width=27)
        self.emp_badge_type.grid(row=4, column=1, padx=10, pady=5, sticky="w")
        
        # Buttons
        button_frame = ttk.Frame(self.employee_tab)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="Add Employee", command=self.add_employee, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Update Employee", command=self.update_employee, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Remove Employee", command=self.remove_employee, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear Form", command=self.clear_employee_form, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Export to CSV", command=self.export_employees_csv, width=15).pack(side=tk.LEFT, padx=5)
        
        # Load employee data into treeview
        self.refresh_employee_list()
        
        # Bind treeview selection to form
        self.employee_tree.bind("<<TreeviewSelect>>", self.on_employee_select)
    
    def build_door_tab(self):
        # Frame for door list and search
        list_frame = ttk.Frame(self.door_tab)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Search Frame
        search_frame = ttk.Frame(list_frame)
        search_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=5)
        self.door_search = ttk.Entry(search_frame, width=30)
        self.door_search.pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="Search", command=self.search_doors).pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="Clear", command=self.refresh_door_list).pack(side=tk.LEFT, padx=5)
        
        # Door List Treeview
        self.door_tree = ttk.Treeview(list_frame, columns=("ID", "Name"))
        self.door_tree.heading("#0", text="")
        self.door_tree.heading("ID", text="Door ID")
        self.door_tree.heading("Name", text="Door Name")
        
        # Add scrollbars
        yscroll = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.door_tree.yview)
        xscroll = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL, command=self.door_tree.xview)
        self.door_tree.configure(yscroll=yscroll.set, xscroll=xscroll.set)
        
        self.door_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        yscroll.pack(side=tk.RIGHT, fill=tk.Y)
        xscroll.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Door Form
        form_frame = ttk.Frame(self.door_tab)
        form_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(form_frame, text="Door ID:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
        self.door_id = ttk.Entry(form_frame, width=30)
        self.door_id.grid(row=0, column=1, padx=10, pady=5, sticky="w")
        
        ttk.Label(form_frame, text="Door Name:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.door_name = ttk.Entry(form_frame, width=30)
        self.door_name.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        
        # Buttons
        button_frame = ttk.Frame(self.door_tab)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="Add Door", command=self.add_door, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Update Door", command=self.update_door, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Remove Door", command=self.remove_door, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear Form", command=self.clear_door_form, width=15).pack(side=tk.LEFT, padx=5)
        
        # Load door data into treeview
        self.refresh_door_list()
        
        # Bind treeview selection to form
        self.door_tree.bind("<<TreeviewSelect>>", self.on_door_select)
    
    def build_logical_tab(self):
        # Main frame
        logical_frame = ttk.Frame(self.logical_tab)
        logical_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Access Rules Configuration
        ttk.Label(logical_frame, text="Configure Logical Access Rules", font=('Arial', 12, 'bold')).grid(row=0, column=0, columnspan=3, pady=10)
        
        # Role selection
        ttk.Label(logical_frame, text="Role:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.logical_role = ttk.Combobox(logical_frame, values=["Employee", "IT Manager", "Senior IT", "Junior IT", "HR Manager", "HR Staff", "Security", "Finance", "Visitor"])
        self.logical_role.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        # Resource type selection
        ttk.Label(logical_frame, text="Resource Type:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.resource_type = ttk.Combobox(logical_frame, values=list(self.logical_resources.keys()))
        self.resource_type.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        self.resource_type.bind("<<ComboboxSelected>>", self.update_resource_options)
        
        # Specific resource selection
        ttk.Label(logical_frame, text="Specific Resource:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        self.specific_resource = ttk.Combobox(logical_frame)
        self.specific_resource.grid(row=3, column=1, padx=5, pady=5, sticky="w")
        
        # Access level
        ttk.Label(logical_frame, text="Access Level:").grid(row=4, column=0, padx=5, pady=5, sticky="e")
        self.access_level = ttk.Combobox(logical_frame, values=["Read", "Write", "Admin"])
        self.access_level.grid(row=4, column=1, padx=5, pady=5, sticky="w")
        
        # Buttons
        ttk.Button(logical_frame, text="Add Rule", command=self.add_logical_rule).grid(row=5, column=0, pady=10)
        ttk.Button(logical_frame, text="Remove Rule", command=self.remove_logical_rule).grid(row=5, column=1, pady=10)
        
        # Rules Treeview
        self.rules_tree = ttk.Treeview(logical_frame, columns=("Role", "ResourceType", "Resource", "AccessLevel"))
        self.rules_tree.heading("#0", text="ID")
        self.rules_tree.heading("Role", text="Role")
        self.rules_tree.heading("ResourceType", text="Resource Type")
        self.rules_tree.heading("Resource", text="Resource")
        self.rules_tree.heading("AccessLevel", text="Access Level")
        self.rules_tree.grid(row=6, column=0, columnspan=2, pady=10)
        
        # Access Test Frame
        test_frame = ttk.LabelFrame(logical_frame, text="Test Logical Access")
        test_frame.grid(row=7, column=0, columnspan=2, pady=10)
        
        ttk.Label(test_frame, text="Badge Number:").grid(row=0, column=0, padx=5, pady=5)
        self.test_badge = ttk.Entry(test_frame)
        self.test_badge.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(test_frame, text="Resource to Access:").grid(row=1, column=0, padx=5, pady=5)
        self.test_resource = ttk.Combobox(test_frame, values=self.get_all_resources())
        self.test_resource.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Button(test_frame, text="Check Access", command=self.test_logical_access).grid(row=2, column=0, columnspan=2, pady=5)
        
        self.test_result = ttk.Label(test_frame, text="", font=('Arial', 10))
        self.test_result.grid(row=3, column=0, columnspan=2)
        
        # Load existing rules
        self.refresh_rules_list()
    
    def build_logs_tab(self):
        # Frame for logs
        logs_frame = ttk.Frame(self.logs_tab)
        logs_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Logs Treeview
        self.logs_tree = ttk.Treeview(logs_frame, columns=("Timestamp", "Name", "Badge", "Location", "Result", "Type"))
        self.logs_tree.heading("#0", text="ID")
        self.logs_tree.heading("Timestamp", text="Timestamp")
        self.logs_tree.heading("Name", text="Name")
        self.logs_tree.heading("Badge", text="Badge Number")
        self.logs_tree.heading("Location", text="Location")
        self.logs_tree.heading("Result", text="Result")
        self.logs_tree.heading("Type", text="Type")
        
        # Add scrollbars
        yscroll = ttk.Scrollbar(logs_frame, orient=tk.VERTICAL, command=self.logs_tree.yview)
        xscroll = ttk.Scrollbar(logs_frame, orient=tk.HORIZONTAL, command=self.logs_tree.xview)
        self.logs_tree.configure(yscroll=yscroll.set, xscroll=xscroll.set)
        
        self.logs_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        yscroll.pack(side=tk.RIGHT, fill=tk.Y)
        xscroll.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Filter Frame
        filter_frame = ttk.Frame(self.logs_tab)
        filter_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(filter_frame, text="Filter by:").pack(side=tk.LEFT, padx=5)
        self.log_filter_type = ttk.Combobox(filter_frame, values=["All", "Granted", "Denied", "Physical", "Logical"], width=10)
        self.log_filter_type.pack(side=tk.LEFT, padx=5)
        self.log_filter_type.current(0)
        
        ttk.Button(filter_frame, text="Apply Filter", command=self.refresh_logs).pack(side=tk.LEFT, padx=5)
        ttk.Button(filter_frame, text="Export to CSV", command=self.export_logs).pack(side=tk.RIGHT, padx=5)
        
        # Load initial logs
        self.refresh_logs()
    
    def update_resource_options(self, event):
        """Update resource options when resource type changes"""
        selected_type = self.resource_type.get()
        self.specific_resource['values'] = self.logical_resources.get(selected_type, [])
    
    def get_all_resources(self):
        """Get all resources for the test combobox"""
        all_resources = []
        for resource_type in self.logical_resources.values():
            all_resources.extend(resource_type)
        return all_resources
    
    def add_logical_rule(self):
        """Add a new logical access rule"""
        role = self.logical_role.get()
        res_type = self.resource_type.get()
        resource = self.specific_resource.get()
        access_level = self.access_level.get()
        
        if not all([role, res_type, resource, access_level]):
            messagebox.showerror("Error", "Please fill all fields")
            return
            
        new_rule = {
            "role": role,
            "resource_type": res_type,
            "resource": resource,
            "access_level": access_level
        }
        
        self.logical_access_rules.append(new_rule)
        self.save_data()
        self.refresh_rules_list()
        
    def remove_logical_rule(self):
        """Remove selected logical access rule"""
        selected = self.rules_tree.focus()
        if not selected:
            messagebox.showerror("Error", "Please select a rule to remove")
            return
            
        item = self.rules_tree.item(selected)
        rule_index = int(item["text"]) - 1
        
        if 0 <= rule_index < len(self.logical_access_rules):
            del self.logical_access_rules[rule_index]
            self.save_data()
            self.refresh_rules_list()
        
    def refresh_rules_list(self):
        """Refresh the rules treeview"""
        self.rules_tree.delete(*self.rules_tree.get_children())
        for i, rule in enumerate(self.logical_access_rules):
            self.rules_tree.insert("", "end", text=str(i+1), values=(
                rule['role'],
                rule['resource_type'],
                rule['resource'],
                rule['access_level']
            ))
            
    def test_logical_access(self):
        """Test if a badge has access to a resource"""
        badge = self.test_badge.get()
        resource = self.test_resource.get()
        
        if not badge or not resource:
            messagebox.showerror("Error", "Please enter both badge number and resource")
            return
            
        # Find employee
        employee = next((emp for emp in self.employees if emp["badge_number"] == badge), None)
        if not employee:
            self.test_result.config(text="Access Denied: Badge not registered", foreground="red")
            self.log_logical_access(badge, None, resource, False)
            return
            
        # Check logical access rules
        role = employee['role']
        access_granted = False
        access_level = ""
        
        for rule in self.logical_access_rules:
            if rule['role'] == role and rule['resource'] == resource:
                access_granted = True
                access_level = rule['access_level']
                break
                
        if access_granted:
            result = f"Access Granted ({access_level}) to {resource}"
            self.test_result.config(text=result, foreground="green")
        else:
            self.test_result.config(text="Access Denied: No permissions for this resource", foreground="red")
            
        # Log the attempt
        self.log_logical_access(badge, employee['name'], resource, access_granted)
        
    def log_logical_access(self, badge, name, resource, granted):
        """Log logical access attempts"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.logical_access_log.append({
            "timestamp": timestamp,
            "badge_number": badge,
            "name": name,
            "resource": resource,
            "result": "Granted" if granted else "Denied",
            "type": "Logical"
        })
        self.save_data()
        self.refresh_logs()
    
    def search_employees(self):
        query = self.employee_search.get().lower()
        if not query:
            self.refresh_employee_list()
            return
        
        filtered = []
        for emp in self.employees:
            if (query in emp["name"].lower() or 
                query in emp["badge_number"].lower() or 
                query in emp["role"].lower()):
                filtered.append(emp)
        
        self.employee_tree.delete(*self.employee_tree.get_children())
        for i, emp in enumerate(filtered):
            self.employee_tree.insert("", "end", text=str(i+1), values=(
                emp["name"],
                emp["badge_number"],
                emp["role"],
                emp["access_doors"],
                emp["badge_type"]
            ))
    
    def search_doors(self):
        query = self.door_search.get().lower()
        if not query:
            self.refresh_door_list()
            return
        
        filtered = []
        for door_id, door_name in self.door_readers.items():
            if (query in str(door_id).lower() or 
                query in door_name.lower()):
                filtered.append((door_id, door_name))
        
        self.door_tree.delete(*self.door_tree.get_children())
        for i, (door_id, door_name) in enumerate(filtered):
            self.door_tree.insert("", "end", text=str(i+1), values=(door_id, door_name))
    
    def on_employee_select(self, event):
        selected = self.employee_tree.focus()
        if not selected:
            return
            
        item = self.employee_tree.item(selected)
        self.emp_name.delete(0, tk.END)
        self.emp_name.insert(0, item["values"][0])
        self.emp_badge.delete(0, tk.END)
        self.emp_badge.insert(0, item["values"][1])
        self.emp_role.set(item["values"][2])
        self.emp_doors.delete(0, tk.END)
        self.emp_doors.insert(0, item["values"][3])
        self.emp_badge_type.set(item["values"][4])
    
    def on_door_select(self, event):
        selected = self.door_tree.focus()
        if not selected:
            return
            
        item = self.door_tree.item(selected)
        self.door_id.delete(0, tk.END)
        self.door_id.insert(0, item["values"][0])
        self.door_name.delete(0, tk.END)
        self.door_name.insert(0, item["values"][1])
    
    def attempt_access(self):
        badge_number = self.badge_entry.get()
        door_name = self.door_combobox.get()
        
        if not badge_number:
            messagebox.showerror("Error", "Please enter a badge number")
            return
            
        # Find door ID from name
        door_id = [k for k, v in self.door_readers.items() if v == door_name][0]
        
        # Find employee
        employee = next((emp for emp in self.employees if emp["badge_number"] == badge_number), None)
        
        if not employee:
            self.log_access(badge_number, None, door_id, "Access Denied: Badge not registered")
            self.status_label.config(text="Access Denied: Badge not registered", foreground="red")
            return
            
        # Check if badge is expired (for temporary badges)
        if employee["badge_type"] == "Temporary (24h)":
            issue_date = datetime.strptime(employee["issue_date"], "%Y-%m-%d %H:%M:%S")
            if datetime.now() > issue_date + timedelta(hours=24):
                self.log_access(badge_number, employee["name"], door_id, "Access Denied: Temporary badge expired")
                self.status_label.config(text="Access Denied: Temporary badge expired", foreground="red")
                return
        
        # Check door access
        allowed_doors = [int(d) for d in employee["access_doors"].split(",")]
        if door_id in allowed_doors:
            self.log_access(badge_number, employee["name"], door_id, "Access Granted")
            self.status_label.config(text=f"Access Granted for {employee['name']}", foreground="green")
            
            # If this is the turnstile, enable unlock button
            if door_id == 100:
                self.turnstile_button.config(state=tk.NORMAL)
        else:
            self.log_access(badge_number, employee["name"], door_id, "Access Denied: Unauthorized door")
            self.status_label.config(text="Access Denied: Unauthorized door", foreground="red")
    
    def unlock_turnstile(self):
        messagebox.showinfo("Turnstile", "Turnstile unlocked for 5 seconds")
        self.turnstile_button.config(state=tk.DISABLED)
    
    def add_employee(self):
        name = self.emp_name.get()
        badge = self.emp_badge.get()
        role = self.emp_role.get()
        doors = self.emp_doors.get()
        badge_type = self.emp_badge_type.get()
        
        if not all([name, badge, role, doors, badge_type]):
            messagebox.showerror("Error", "Please fill all fields")
            return
            
        # Check if badge already exists
        if any(emp["badge_number"] == badge for emp in self.employees):
            messagebox.showerror("Error", "Badge number already in use")
            return
            
        new_employee = {
            "name": name,
            "badge_number": badge,
            "role": role,
            "access_doors": doors,
            "badge_type": badge_type,
            "issue_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        self.employees.append(new_employee)
        self.save_data()
        self.refresh_employee_list()
        self.clear_employee_form()
        messagebox.showinfo("Success", "Employee added successfully")
    
    def update_employee(self):
        selected = self.employee_tree.focus()
        if not selected:
            messagebox.showerror("Error", "Please select an employee to update")
            return
            
        # Get employee data from tree
        item = self.employee_tree.item(selected)
        badge = item["values"][1]
        
        # Find employee in list
        employee = next((emp for emp in self.employees if emp["badge_number"] == badge), None)
        if not employee:
            messagebox.showerror("Error", "Employee not found")
            return
            
        # Update employee data
        employee["name"] = self.emp_name.get()
        employee["role"] = self.emp_role.get()
        employee["access_doors"] = self.emp_doors.get()
        employee["badge_type"] = self.emp_badge_type.get()
        
        self.save_data()
        self.refresh_employee_list()
        messagebox.showinfo("Success", "Employee updated successfully")
    
    def remove_employee(self):
        selected = self.employee_tree.focus()
        if not selected:
            messagebox.showerror("Error", "Please select an employee to remove")
            return
            
        # Get employee data from tree
        item = self.employee_tree.item(selected)
        badge = item["values"][1]
        
        # Confirm deletion
        if not messagebox.askyesno("Confirm", "Are you sure you want to remove this employee?"):
            return
            
        # Remove employee
        self.employees = [emp for emp in self.employees if emp["badge_number"] != badge]
        self.save_data()
        self.refresh_employee_list()
        self.clear_employee_form()
        messagebox.showinfo("Success", "Employee removed successfully")
    
    def add_door(self):
        door_id = self.door_id.get()
        door_name = self.door_name.get()
        
        if not door_id or not door_name:
            messagebox.showerror("Error", "Please enter both door ID and name")
            return
            
        try:
            door_id = int(door_id)
        except ValueError:
            messagebox.showerror("Error", "Door ID must be a number")
            return
            
        if door_id in self.door_readers:
            messagebox.showerror("Error", "Door ID already exists")
            return
            
        self.door_readers[door_id] = door_name
        self.save_data()
        self.refresh_door_list()
        self.refresh_door_combobox()
        self.clear_door_form()
        messagebox.showinfo("Success", "Door added successfully")
    
    def update_door(self):
        selected = self.door_tree.focus()
        if not selected:
            messagebox.showerror("Error", "Please select a door to update")
            return
            
        # Get door data from tree
        item = self.door_tree.item(selected)
        old_id = int(item["values"][0])
        
        new_id = self.door_id.get()
        new_name = self.door_name.get()
        
        if not new_id or not new_name:
            messagebox.showerror("Error", "Please enter both door ID and name")
            return
            
        try:
            new_id = int(new_id)
        except ValueError:
            messagebox.showerror("Error", "Door ID must be a number")
            return
            
        # Remove old door and add new one
        if old_id in self.door_readers:
            del self.door_readers[old_id]
        
        self.door_readers[new_id] = new_name
        self.save_data()
        self.refresh_door_list()
        self.refresh_door_combobox()
        self.clear_door_form()
        messagebox.showinfo("Success", "Door updated successfully")
    
    def remove_door(self):
        selected = self.door_tree.focus()
        if not selected:
            messagebox.showerror("Error", "Please select a door to remove")
            return
            
        # Get door data from tree
        item = self.door_tree.item(selected)
        door_id = int(item["values"][0])
        
        # Confirm deletion
        if not messagebox.askyesno("Confirm", "Are you sure you want to remove this door?"):
            return
            
        if door_id in self.door_readers:
            del self.door_readers[door_id]
            self.save_data()
            self.refresh_door_list()
            self.refresh_door_combobox()
            self.clear_door_form()
            messagebox.showinfo("Success", "Door removed successfully")
    
    def refresh_employee_list(self):
        self.employee_tree.delete(*self.employee_tree.get_children())
        for i, emp in enumerate(self.employees):
            self.employee_tree.insert("", "end", text=str(i+1), values=(
                emp["name"],
                emp["badge_number"],
                emp["role"],
                emp["access_doors"],
                emp["badge_type"]
            ))
    
    def refresh_door_list(self):
        self.door_tree.delete(*self.door_tree.get_children())
        for i,  (door_id, door_name) in enumerate(self.door_readers.items()):
            self.door_tree.insert("", "end", text=str(i+1), values=(door_id, door_name))
    
    def refresh_door_combobox(self):
        """Refresh the door combobox in the physical access tab"""
        self.door_combobox['values'] = list(self.door_readers.values())
        if self.door_readers:
            self.door_combobox.current(0)
    
    def clear_employee_form(self):
        """Clear the employee form"""
        self.emp_name.delete(0, tk.END)
        self.emp_badge.delete(0, tk.END)
        self.emp_role.set('')
        self.emp_doors.delete(0, tk.END)
        self.emp_badge_type.set('')
    
    def clear_door_form(self):
        """Clear the door form"""
        self.door_id.delete(0, tk.END)
        self.door_name.delete(0, tk.END)
    
    def log_access(self, badge_number, name, door_id, result):
        """Log physical access attempts"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        door_name = self.door_readers.get(door_id, "Unknown Door")
        
        self.access_log.append({
            "timestamp": timestamp,
            "badge_number": badge_number,
            "name": name,
            "door_id": door_id,
            "door_name": door_name,
            "result": result,
            "type": "Physical"
        })
        self.save_data()
        self.refresh_logs()
    
    def refresh_logs(self):
        """Refresh the logs treeview with all logs"""
        self.logs_tree.delete(*self.logs_tree.get_children())
        
        # Combine physical and logical logs
        all_logs = []
        
        # Add physical logs
        for log in self.access_log:
            all_logs.append({
                "timestamp": log["timestamp"],
                "name": log["name"],
                "badge": log["badge_number"],
                "location": log["door_name"],
                "result": log["result"],
                "type": "Physical"
            })
        
        # Add logical logs
        for log in self.logical_access_log:
            all_logs.append({
                "timestamp": log["timestamp"],
                "name": log["name"],
                "badge": log["badge_number"],
                "location": log["resource"],
                "result": log["result"],
                "type": "Logical"
            })
        
        # Sort logs by timestamp (newest first)
        all_logs.sort(key=lambda x: x["timestamp"], reverse=True)
        
        # Apply filter if selected
        filter_type = self.log_filter_type.get()
        if filter_type != "All":
            if filter_type in ["Granted", "Denied"]:
                all_logs = [log for log in all_logs if log["result"] == filter_type]
            else:
                all_logs = [log for log in all_logs if log["type"] == filter_type]
        
        # Add logs to treeview
        for i, log in enumerate(all_logs):
            self.logs_tree.insert("", "end", text=str(i+1), values=(
                log["timestamp"],
                log["name"],
                log["badge"],
                log["location"],
                log["result"],
                log["type"]
            ))
    
    def export_employees_csv(self):
        """Export employee data to CSV"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")],
            title="Save Employee Data As"
        )
        
        if not filename:
            return
            
        try:
            with open(filename, 'w') as f:
                f.write("Name,Badge Number,Role,Access Doors,Badge Type,Issue Date\n")
                for emp in self.employees:
                    f.write(f'"{emp["name"]}",{emp["badge_number"]},{emp["role"]},{emp["access_doors"]},{emp["badge_type"]},{emp["issue_date"]}\n')
            messagebox.showinfo("Success", "Employee data exported successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export data: {str(e)}")
    
    def export_logs(self):
        """Export logs to CSV"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")],
            title="Save Logs As"
        )
        
        if not filename:
            return
            
        try:
            with open(filename, 'w') as f:
                f.write("Timestamp,Name,Badge Number,Location,Result,Type\n")
                
                # Combine physical and logical logs
                all_logs = []
                all_logs.extend(self.access_log)
                all_logs.extend(self.logical_access_log)
                
                # Sort logs by timestamp (newest first)
                all_logs.sort(key=lambda x: x["timestamp"], reverse=True)
                
                for log in all_logs:
                    if "door_name" in log:  # Physical log
                        f.write(f'"{log["timestamp"]}","{log["name"]}",{log["badge_number"]},"{log["door_name"]}",{log["result"]},Physical\n')
                    else:  # Logical log
                        f.write(f'"{log["timestamp"]}","{log["name"]}",{log["badge_number"]},"{log["resource"]}",{log["result"]},Logical\n')
                        
            messagebox.showinfo("Success", "Logs exported successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export logs: {str(e)}")
    
    def load_data(self):
        """Load data from JSON files"""
        try:
            if os.path.exists("employees.json"):
                with open("employees.json", "r") as f:
                    self.employees = json.load(f)
            
            if os.path.exists("doors.json"):
                with open("doors.json", "r") as f:
                    self.door_readers = json.load(f)
            
            if os.path.exists("access_log.json"):
                with open("access_log.json", "r") as f:
                    self.access_log = json.load(f)
            
            if os.path.exists("logical_rules.json"):
                with open("logical_rules.json", "r") as f:
                    self.logical_access_rules = json.load(f)
            
            if os.path.exists("logical_logs.json"):
                with open("logical_logs.json", "r") as f:
                    self.logical_access_log = json.load(f)
                    
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load data: {str(e)}")
    
    def save_data(self):
        """Save data to JSON files"""
        try:
            with open("employees.json", "w") as f:
                json.dump(self.employees, f)
            
            with open("doors.json", "w") as f:
                json.dump(self.door_readers, f)
            
            with open("access_log.json", "w") as f:
                json.dump(self.access_log, f)
            
            with open("logical_rules.json", "w") as f:
                json.dump(self.logical_access_rules, f)
            
            with open("logical_logs.json", "w") as f:
                json.dump(self.logical_access_log, f)
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save data: {str(e)}")

def main():
    root = tk.Tk()
    app = AccessControlSystem(root)
    root.mainloop()

if __name__ == "__main__":
    main()
