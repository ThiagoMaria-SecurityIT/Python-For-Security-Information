import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
import sv_ttk
import subprocess
import os
import tempfile
import shutil
import platform
import sys

class GCCCompilerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("GCC Compiler GUI")
        self.root.geometry("800x600")
        
        sv_ttk.set_theme("dark")
        self.setup_ui()
        
    def setup_ui(self):
        """Initialize all UI components"""
        self.create_sidebar()
        self.create_main_panel()
        self.create_terminal()
        
    def create_sidebar(self):
        """VS Code-style sidebar with file tree"""
        self.sidebar = ttk.Frame(self.root, width=200, relief="sunken")
        self.sidebar.pack(side="left", fill="y", padx=5, pady=5)
        
        ttk.Label(self.sidebar, text="Files", style="Accent.TLabel").pack(pady=10)
        
        self.tree = ttk.Treeview(self.sidebar)
        self.tree.pack(expand=True, fill="both")
        
        # Create parent with explicit iid
        recent_files = self.tree.insert("", "end", text="Recent Files", iid="recent_files")
        self.tree.item("recent_files", open=True)
        self.tree.bind("<Double-1>", self.on_tree_select)
    
    def create_main_panel(self):
        """Main panel with drag-and-drop and buttons"""
        self.main_panel = ttk.Frame(self.root)
        self.main_panel.pack(side="top", fill="both", expand=True, padx=5, pady=5)
        
        # Drag-and-drop zone
        self.drop_zone = ttk.Label(
            self.main_panel,
            text="Drag .c or .txt file here",
            padding=50,
            style="Accent.TLabel",
            relief="groove"
        )
        self.drop_zone.pack(pady=20, fill="x")
        
        self.drop_zone.drop_target_register(DND_FILES)
        self.drop_zone.dnd_bind("<<Drop>>", self.handle_drop)
        
        # Button group
        btn_frame = ttk.Frame(self.main_panel)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="Browse", command=self.browse_file).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Add to Recent", command=self.add_to_recent).pack(side="left", padx=5)
        
        # Status bar
        self.status = ttk.Label(self.main_panel, text="Ready", relief="sunken")
        self.status.pack(side="bottom", fill="x", pady=5)
    
    def create_terminal(self):
        """Terminal emulator with colored output"""
        self.terminal = scrolledtext.ScrolledText(
            self.root,
            wrap=tk.WORD,
            width=80,
            height=15,
            font=('Consolas', 10)
        )
        self.terminal.pack(fill="both", expand=True, padx=5, pady=5)
        self.terminal.tag_config("error", foreground="red")
        self.terminal.tag_config("success", foreground="green")

    def add_to_recent(self):
        """Add current file to Recent Files list"""
        if not hasattr(self, "current_file"):
            self.log_output("Error: No file loaded to add!", "error")
            return
            
        file_name = os.path.basename(self.current_file)
        file_path = self.current_file
        
        # Check if file already exists in tree
        existing = []
        for child in self.tree.get_children("recent_files"):
            if self.tree.item(child, "values")[0] == file_path:
                existing.append(child)
        
        # Remove duplicates
        for item in existing:
            self.tree.delete(item)
        
        # Add to top of list
        self.tree.insert(
            "recent_files", 
            "0",  # Insert at top
            text=file_name,
            values=[file_path]  # Store full path
        )
        
        # Limit to 10 recent files
        children = self.tree.get_children("recent_files")
        if len(children) > 10:
            for item in children[10:]:
                self.tree.delete(item)
                
        self.log_output(f"Added to recent files: {file_name}", "success")

    def handle_drop(self, event):
        """Process dropped files"""
        file_path = event.data.strip("{}").strip("'\"")
        if file_path.lower().endswith((".txt", ".c")):
            if os.path.exists(file_path):
                self.current_file = file_path
                self.update_status(f"Loaded: {os.path.basename(file_path)}")
                self.display_file(file_path)
                self.add_to_recent()  # Auto-add to recent files
            else:
                self.log_output(f"Error: File not found: {file_path}", "error")
        else:
            self.log_output("Error: Only .c or .txt files supported!", "error")
            
    def browse_file(self):
        """Traditional file dialog"""
        file_path = filedialog.askopenfilename(filetypes=[("C Files", "*.c"), ("Text Files", "*.txt")])
        if file_path:
            self.current_file = file_path
            self.update_status(f"Loaded: {os.path.basename(file_path)}")
            self.display_file(file_path)
            self.add_to_recent()  # Auto-add to recent files

    def on_tree_select(self, event):
        """Handle file selection from treeview"""
        item = self.tree.selection()[0]
        file_path = self.tree.item(item, "values")[0]  # Get full path from values
        
        if os.path.exists(file_path) and file_path.endswith((".txt", ".c")):
            self.current_file = file_path
            self.update_status(f"Loaded: {os.path.basename(file_path)}")
            self.display_file(file_path)
        else:
            self.log_output(f"Error: File not found: {file_path}", "error")
            self.tree.delete(item)  # Remove missing file from tree
            
    def display_file(self, file_path):
        """Show file content in terminal"""
        try:
            with open(file_path, "r") as f:
                content = f.read()
            self.terminal.delete(1.0, tk.END)
            self.terminal.insert(tk.END, f"--- {file_path} ---\n{content}")
        except Exception as e:
            self.log_output(f"Error reading file: {str(e)}", "error")

    def compile_file(self):
        """Compile with GCC locally"""
        if not hasattr(self, "current_file"):
            self.log_output("Error: No file selected!", "error")
            return
            
        if not os.path.exists(self.current_file):
            self.log_output(f"Error: File not found: {self.current_file}", "error")
            return
        
        output_file = os.path.splitext(self.current_file)[0] + ".exe"
        cmd = f'gcc "{self.current_file}" -o "{output_file}"'
        
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self.log_output(f"Success! Compiled to {output_file}\n", "success")
                self.output_file = output_file
                self.add_to_recent()  # Add source file to recent
            else:
                self.log_output(result.stderr, "error")
                
        except Exception as e:
            self.log_output(f"Compilation failed: {str(e)}", "error")
            
    def run_output(self):
        """Run the compiled program"""
        if not hasattr(self, "output_file"):
            self.log_output("Error: Nothing to run! Compile first.", "error")
            return
            
        try:
            result = subprocess.run(
                f'"{self.output_file}"',
                shell=True,
                capture_output=True,
                text=True
            )
            self.log_output(result.stdout, "success")
            if result.stderr:
                self.log_output(result.stderr, "error")
                
        except Exception as e:
            self.log_output(f"Execution failed: {str(e)}", "error")

    def log_output(self, message, tag=None):
        """Print to terminal with color coding"""
        self.terminal.insert(tk.END, message + "\n", tag)
        self.terminal.see(tk.END)
        
    def update_status(self, message):
        """Update status bar"""
        self.status.config(text=message)

class SandboxManager:
    @staticmethod
    def is_available():
        """Check if Windows Sandbox is available and enabled"""
        try:
            if platform.system() != "Windows":
                return False
                
            win_ver = platform.win32_ver()
            if int(win_ver[0]) < 10:
                return False
                
            edition = win_ver[-1]
            if "Pro" not in edition and "Enterprise" not in edition:
                return False
                
            result = subprocess.run(
                ["dism", "/online", "/get-featureinfo", "/featurename:Containers-DisposableClientVM"],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            return "Enabled" in result.stdout
        except:
            return False

    @staticmethod
    def launch(config_path):
        """Launch Windows Sandbox with configuration file"""
        try:
            subprocess.run(
                ["WindowsSandbox.exe", config_path],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    @staticmethod
    def terminate():
        """Terminate all running Sandbox instances"""
        try:
            subprocess.run(
                ["taskkill", "/IM", "WindowsSandbox.exe", "/F"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            return True
        except subprocess.CalledProcessError:
            return False

    def create_sandbox_controls(self):
        """Add Windows Sandbox control buttons if available"""
        sandbox_frame = ttk.LabelFrame(self.main_panel, text="Windows Sandbox")
        sandbox_frame.pack(fill="x", pady=10)
        
        ttk.Button(
            sandbox_frame,
            text="🛡️ Compile in Sandbox",
            command=self.compile_in_sandbox
        ).pack(side="left", padx=5)
        
        ttk.Button(
            sandbox_frame,
            text="⏹️ Terminate Sandbox",
            command=self.terminate_sandbox
        ).pack(side="left", padx=5)
        
        self.sandbox_status = ttk.Label(
            sandbox_frame,
            text="🔴 Sandbox: Inactive",
            foreground="red"
        )
        self.sandbox_status.pack(side="left", padx=10)
    
    def compile_in_sandbox(self):
        """Compile the current file in Windows Sandbox"""
        if not hasattr(self, "current_file"):
            self.log_output("Error: No file selected for sandbox compilation!", "error")
            return
            
        try:
            with tempfile.TemporaryDirectory() as tmp_dir:
                src_file = os.path.basename(self.current_file)
                dst_file = os.path.join(tmp_dir, src_file)
                shutil.copy2(self.current_file, dst_file)
                
                batch_file = os.path.join(tmp_dir, "compile_and_run.bat")
                with open(batch_file, "w") as f:
                    f.write(f"""@echo off
gcc "{src_file}" -o output.exe
if exist output.exe (
    output.exe
    pause
) else (
    echo Compilation failed!
    pause
)
""")
                config_file = os.path.join(tmp_dir, "sandbox_config.wsb")
                with open(config_file, "w") as f:
                    f.write(f"""<Configuration>
    <MappedFolders>
        <MappedFolder>
            <HostFolder>{tmp_dir}</HostFolder>
            <ReadOnly>false</ReadOnly>
        </MappedFolder>
    </MappedFolders>
    <LogonCommand>
        <Command>cmd /c "{batch_file}"</Command>
    </LogonCommand>
    <MemoryInMB>4096</MemoryInMB>
</Configuration>""")
                
                if SandboxManager.launch(config_file):
                    self.sandbox_status.config(
                        text="🟢 Sandbox: Active",
                        foreground="green"
                    )
                    self.log_output("[Sandbox] Compilation environment launched\n")
                    self.add_to_recent()  # Add source file to recent
                
        except Exception as e:
            self.log_output(f"[Sandbox Error] {str(e)}\n", "error")
        
    def terminate_sandbox(self):
        """Terminate sandbox with feedback"""
        if SandboxManager.terminate():
            self.sandbox_status.config(
                text="🔴 Sandbox: Terminated",
                foreground="red"
            )
            self.log_output("[Sandbox] Terminated\n")
        else:
            self.log_output("[Sandbox] No active instances\n")

if __name__ == "__main__":
    def is_admin():
        try:
            return os.getuid() == 0
        except AttributeError:
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
    
    root = TkinterDnD.Tk()
    app = GCCCompilerGUI(root)
    
    # Add compile and run buttons after checking sandbox availability
    btn_frame = app.main_panel.winfo_children()[1]  # Get the button frame
    ttk.Button(btn_frame, text="Compile", command=app.compile_file).pack(side="left", padx=5)
    ttk.Button(btn_frame, text="Run", command=app.run_output).pack(side="left", padx=5)
    
    if SandboxManager.is_available():
        app.create_sandbox_controls()
    else:
        messagebox.showwarning(
            "Sandbox Unavailable",
            "Windows Sandbox is not available on this system.\n"
            "Only local compilation will be available.",
            parent=root
        )
    
    root.mainloop()
