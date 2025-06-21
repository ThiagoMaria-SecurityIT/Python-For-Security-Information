import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pyperclip
import os
import subprocess
import threading
import json # For structured configuration saving/loading
import platform # For OS detection
import logging
from datetime import datetime
from functools import partial

# Configure logging for better error tracking and diagnostics
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class VirtualEnvTool:
    """
    A Tkinter-based GUI tool designed as a cheat sheet for managing Python virtual environments
    and executing PowerShell commands, specifically tailored for common development tasks.

    It provides functionalities to:
    - Set environment variables (virtual environment path, script path, Python executable path).
    - Generate and copy common commands for virtual environment activation, script execution, etc.
    - Execute commands directly within an integrated terminal-like display.
    - Toggle informative pop-up messages.
    - Save and load environment configurations.
    """

    def __init__(self, root: tk.Tk):
        """
        Initializes the VirtualEnvTool application.

        Args:
            root: The root Tkinter window.
        """
        self.root = root
        self.root.title("Python & PowerShell VirtualEnv Cheat Sheet")
        self.root.geometry("1200x800")
        self.show_popups = True  # Control variable for popups

        # Define a consistent color palette for the dark theme
        self.colors = {
            "bg_primary": "#2d2d2d",      # Dark background
            "fg_primary": "#ffffff",      # White foreground text
            "entry_bg": "#3d3d3d",        # Slightly lighter background for entry fields
            "button_bg": "#4a4a4a",       # Darker background for general buttons
            "button_fg": "#ffffff",       # White text for buttons
            "terminal_bg": "#1e1e1e",     # Very dark background for terminal
            "terminal_fg_normal": "#06d6a0", # Green/teal for normal terminal output
            "terminal_fg_error": "#ff6b6b",  # Coral red for terminal errors
            "highlight_accent": "#118ab2", # Pacific blue for highlights/active states
            "copy_button": "#06d6a0",      # Seafoam Green for copy buttons
            "execute_button": "#ff6b6b",   # Coral Red for execute buttons
            "success_feedback": "#06d6a0", # Seafoam Green for success feedback
            "separator_color": "#6b7280"   # Gray for terminal separators
        }

        self._apply_theme()
        self._create_menubar()
        self._create_widgets()

    def _apply_theme(self):
        """Applies the defined dark theme and custom styles to Tkinter widgets."""
        self.root.tk_setPalette(
            background=self.colors["bg_primary"],
            foreground=self.colors["fg_primary"],
            activeBackground=self.colors["highlight_accent"],
            activeForeground=self.colors["fg_primary"],
            highlightBackground=self.colors["highlight_accent"],
            highlightForeground=self.colors["fg_primary"],
            selectBackground=self.colors["highlight_accent"],
            selectForeground=self.colors["fg_primary"],
            insertBackground=self.colors["fg_primary"] # Cursor color
        )

        style = ttk.Style(self.root)
        style.theme_use('clam') # 'clam' theme provides a good base for customization

        # General style for labels, entries, and buttons
        style.configure("TLabel", background=self.colors["bg_primary"], foreground=self.colors["fg_primary"])
        style.configure("TEntry", fieldbackground=self.colors["entry_bg"], foreground=self.colors["fg_primary"],
                        insertcolor=self.colors["fg_primary"], borderwidth=0, relief="flat")
        style.map("TEntry", fieldbackground=[('focus', self.colors["entry_bg"])]) # Prevent color change on focus

        # Style for placeholder text in Entry
        style.configure("Placeholder.TEntry", fieldbackground=self.colors["entry_bg"], foreground=self.colors["separator_color"],
                        insertcolor=self.colors["fg_primary"], borderwidth=0, relief="flat")
        style.map("Placeholder.TEntry", fieldbackground=[('focus', self.colors["entry_bg"])])


        style.configure("TButton",
                        background=self.colors["button_bg"],
                        foreground=self.colors["button_fg"],
                        borderwidth=0,
                        focuscolor=self.colors["button_bg"], # Remove focus border artifact
                        font=('Arial', 10, 'bold'))
        style.map("TButton",
                  background=[('active', self.colors["highlight_accent"])],
                  foreground=[('active', self.colors["fg_primary"])])

        # Specific styles for Copy and Execute buttons
        style.configure("Copy.TButton", background=self.colors["copy_button"], foreground=self.colors["button_fg"], width=8) # Set fixed width for alignment
        style.map("Copy.TButton", background=[('active', self._darken_color(self.colors["copy_button"], 0.1))])

        style.configure("Execute.TButton", background=self.colors["execute_button"], foreground=self.colors["button_fg"], width=8) # Set fixed width for alignment
        style.map("Execute.TButton", background=[('active', self._darken_color(self.colors["execute_button"], 0.1))])

        # Success feedback style for buttons/labels
        style.configure("Success.TLabel", background=self.colors["success_feedback"], foreground=self.colors["fg_primary"])

        # Frame styles
        style.configure("TFrame", background=self.colors["bg_primary"])
        style.configure("Terminal.TFrame", background=self.colors["terminal_bg"])
        style.configure("Input.TFrame", background=self.colors["bg_primary"])

        # Notebook (tabs) styles
        style.configure('TNotebook', background=self.colors["bg_primary"], borderwidth=0)
        style.configure('TNotebook.Tab',
                        background=self.colors["button_bg"],
                        foreground=self.colors["fg_primary"],
                        font=('Arial', 10, 'bold'),
                        padding=[10, 5],
                        borderwidth=0)
        style.map('TNotebook.Tab',
                  background=[('selected', self.colors["highlight_accent"]), ('active', self.colors["highlight_accent"])],
                  foreground=[('selected', self.colors["fg_primary"]), ('active', self.colors["fg_primary"])])

    def _darken_color(self, hex_color: str, factor: float) -> str:
        """Darkens a hex color by a given factor."""
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        darkened_rgb = tuple(max(0, int(c * (1 - factor))) for c in rgb)
        return f'#{darkened_rgb[0]:02x}{darkened_rgb[1]:02x}{darkened_rgb[2]:02x}'

    def _create_menubar(self):
        """Creates the application's menu bar with File and Edit options."""
        menubar = tk.Menu(self.root, bg=self.colors["bg_primary"], fg=self.colors["fg_primary"])
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0, bg=self.colors["bg_primary"], fg=self.colors["fg_primary"])
        file_menu.add_command(label="Save Config", command=self.save_config)
        file_menu.add_command(label="Load Config", command=self.load_config)
        file_menu.add_separator(background=self.colors["button_bg"])
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        # Edit menu with toggle for pop-ups
        edit_menu = tk.Menu(menubar, tearoff=0, bg=self.colors["bg_primary"], fg=self.colors["fg_primary"])
        self.popup_var = tk.BooleanVar(value=self.show_popups)
        edit_menu.add_checkbutton(
            label="Enable Pop-ups",
            variable=self.popup_var,
            command=self.toggle_popups
        )
        menubar.add_cascade(label="Edit", menu=edit_menu)

    def _create_widgets(self):
        """Organizes and creates all GUI widgets for the application."""
        # Main frame to hold all sections
        main_frame = ttk.Frame(self.root, style="TFrame", padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.grid_rowconfigure(1, weight=1) # Give the notebook/commands section vertical weight
        main_frame.grid_rowconfigure(2, weight=1) # Give terminal section vertical weight
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)

        # Input fields and buttons for paths
        input_frame = ttk.Frame(main_frame, style="Input.TFrame", padding="10")
        input_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        input_frame.columnconfigure(1, weight=1) # Entry field column

        self.env_entry = self._create_input_field(input_frame, "Virtual Env Path:", 0)
        self.script_entry = self._create_input_field(input_frame, "Script Path:", 1)
        self.py_path_entry = self._create_input_field(input_frame, "Python Executable Path:", 2)

        # Browse buttons for paths
        ttk.Button(input_frame, text="Browse Dir", command=partial(self.browse_path, self.env_entry, True)).grid(row=0, column=2, padx=5)
        ttk.Button(input_frame, text="Browse File", command=partial(self.browse_path, self.script_entry, False)).grid(row=1, column=2, padx=5)
        ttk.Button(input_frame, text="Browse File", command=partial(self.browse_path, self.py_path_entry, False)).grid(row=2, column=2, padx=5)

        # Default paths (can be pre-filled)
        self.env_entry.insert(0, os.path.expanduser(os.path.join("~", "Documents", "Projects", "my_project", "venv")))
        self.script_entry.insert(0, os.path.expanduser(os.path.join("~", "Documents", "Projects", "my_project", "script.py")))
        self.py_path_entry.insert(0, self._get_default_python_path())

        # Notebook for command categories
        self.notebook = ttk.Notebook(main_frame, style="TNotebook")
        self.notebook.grid(row=1, column=0, sticky="nsew", padx=(0, 5), pady=(0, 5))

        # Commands defined with templates for dynamic values
        self.commands_data = {
            "Basic Commands": [
                ("Create Virtual Environment", "python -m venv {env}"),
                ("Activate (Windows)", "{env}\\Scripts\\activate.ps1"),
                ("Activate (Linux/Mac)", "source {env}/bin/activate"),
                ("Deactivate", "deactivate"),
                ("Install Package", "pip install package"),
                ("Run Script", "{py_path} {script}"),
                ("List Installed Packages", "pip list"),
                ("Freeze Requirements", "pip freeze > requirements.txt")
            ],
            "Advanced Commands": [
                ("List Python Installations", "py --list"),
                ("Create with Python 3.9", "py -3.9 -m venv {env}"),
                ("Create with Specific Python", "\"{py_path}\" -m venv {env}"),
                ("Check Python Version", "python --version"),
                ("Upgrade pip", "python -m pip install --upgrade pip"),
                ("Install dev dependencies", "pip install -e .[dev]")
            ],
            "PowerShell Specific": [
                ("Check Execution Policy", "Get-ExecutionPolicy -List"),
                ("Set RemoteSigned Policy", "Set-ExecutionPolicy RemoteSigned -Scope CurrentUser"),
                ("Unblock Activate.ps1", "Unblock-File {env}\\Scripts\\Activate.ps1"),
                ("Run PS as Admin", "Start-Process powershell -Verb RunAs")
            ],
            "Troubleshooting": [
                ("Recreate Virtualenv", "rm -rf {env} && python -m venv {env}"),
                ("Clean pip cache", "pip cache purge"),
                ("Fix corrupt packages", "pip install --force-reinstall package"),
                ("Check environment", "python -m pip check")
            ],
            # NEW TAB: Make Exe
            "Make Exe": [
                ("Install PyInstaller", "pip install pyinstaller"),
                ("Build Onefile Executable", "pyinstaller --onefile \"{script}\""),
                ("Build Windowed Executable", "pyinstaller --onefile --windowed \"{script}\""),
                ("Open dist Folder", "OPEN_DIST_FOLDER_SPECIAL_COMMAND") # Special identifier for custom handler
            ]
        }
        self._create_command_tabs()

        # Terminal output section
        terminal_frame = ttk.Frame(main_frame, style="Terminal.TFrame", padding="10")
        terminal_frame.grid(row=1, column=1, rowspan=2, sticky="nsew", padx=(5, 0), pady=(0,0))
        terminal_frame.grid_rowconfigure(0, weight=1) # Output area
        terminal_frame.grid_rowconfigure(1, weight=0) # Input area
        terminal_frame.grid_columnconfigure(0, weight=1)

        terminal_label = ttk.Label(terminal_frame, text="Terminal Output:", background=self.colors["terminal_bg"], foreground=self.colors["fg_primary"], font=('Arial', 12, 'bold'))
        terminal_label.pack(side=tk.TOP, anchor=tk.W, pady=(0, 5))

        self.terminal_output = tk.Text(terminal_frame, wrap="word", bg=self.colors["terminal_bg"],
                                       fg=self.colors["terminal_fg_normal"], font=('Consolas', 10),
                                       relief="flat", padx=5, pady=5, state='disabled') # Set to disabled
        self.terminal_output.pack(fill=tk.BOTH, expand=True)

        terminal_scrollbar = ttk.Scrollbar(terminal_frame, command=self.terminal_output.yview, style="TScrollbar")
        terminal_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.terminal_output.config(yscrollcommand=terminal_scrollbar.set)

        # Terminal Input Section
        terminal_input_frame = ttk.Frame(terminal_frame, style="Input.TFrame")
        terminal_input_frame.pack(fill=tk.X, pady=(5, 0))
        terminal_input_frame.columnconfigure(0, weight=1) # Input entry takes most space

        self.terminal_input_entry = ttk.Entry(terminal_input_frame, style="Placeholder.TEntry") # Start with placeholder style
        self.terminal_input_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        self.terminal_input_entry.bind("<Return>", self._execute_terminal_input_command) # Bind Enter key
        
        # Placeholder text for terminal input
        self.terminal_input_entry.insert(0, "Type command here and press Enter...")
        self.terminal_input_entry.bind("<FocusIn>", self._clear_placeholder)
        self.terminal_input_entry.bind("<FocusOut>", self._add_placeholder)

        ttk.Button(terminal_input_frame, text="Run", command=self._execute_terminal_input_command, style="Execute.TButton").grid(row=0, column=1, sticky="e")

        # Clear Terminal Button
        clear_terminal_btn = ttk.Button(terminal_frame, text="Clear Terminal", command=self._clear_terminal_output, style="Execute.TButton")
        clear_terminal_btn.pack(side=tk.BOTTOM, pady=5)


        # Configure tags for terminal text styling
        self.terminal_output.tag_config('normal', foreground=self.colors["terminal_fg_normal"])
        self.terminal_output.tag_config('error', foreground=self.colors["terminal_fg_error"])
        self.terminal_output.tag_config('new_command', foreground=self.colors["highlight_accent"], font=('Consolas', 10, 'bold'))

        self._log_terminal_output("Application ready. Enter your paths and use the commands.", new_command=True)

    def _get_default_python_path(self) -> str:
        """
        Attempts to find a common Python executable path for the current OS.
        Prioritizes 'python3' on Unix-like systems and 'python.exe' on Windows.

        Returns:
            A string representing a likely Python executable path.
        """
        python_exec_name = "python.exe" if platform.system() == "Windows" else "python3"

        # 1. Try using 'where' (Windows) or 'which' (Linux/macOS)
        try:
            command = ["where", python_exec_name] if platform.system() == "Windows" else ["which", python_exec_name]
            result = subprocess.run(command, capture_output=True, text=True, check=True, shell=True)
            if result.stdout.strip():
                return result.stdout.splitlines()[0].strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            logging.info(f"'{python_exec_name}' not found in PATH via system command. Trying common paths.")

        # 2. Fallback to common installation directories
        if platform.system() == "Windows":
            common_paths = [
                os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Programs', 'Python', 'Python312', python_exec_name),
                os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Programs', 'Python', 'Python311', python_exec_name),
                os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Programs', 'Python', 'Python310', python_exec_name),
                os.path.join("C:", "Python312", python_exec_name),
                os.path.join("C:", "Python311", python_exec_name),
                os.path.join("C:", "Python310", python_exec_name)
            ]
        else: # Linux/macOS
            common_paths = [
                "/usr/bin/python3",
                "/usr/local/bin/python3",
                os.path.expanduser("~/anaconda3/bin/python"),
                os.path.expanduser("~/miniforge3/bin/python")
            ]

        for path in common_paths:
            if os.path.exists(path):
                return path

        logging.warning(f"Could not find a common path for '{python_exec_name}'. Defaulting to generic 'python'.")
        return "python" # Generic fallback if no specific path found

    def _create_input_field(self, parent: ttk.Frame, label_text: str, row: int) -> ttk.Entry:
        """
        Creates a labeled input entry field with styling.

        Args:
            parent: The parent Tkinter frame.
            label_text: The text for the label.
            row: The grid row for this field.

        Returns:
            The created ttk.Entry widget.
        """
        label = ttk.Label(parent, text=label_text, style="TLabel")
        label.grid(row=row, column=0, padx=5, pady=5, sticky="w")
        entry = ttk.Entry(parent, style="TEntry")
        entry.grid(row=row, column=1, padx=5, pady=5, sticky="ew")
        return entry

    def _create_command_tabs(self):
        """Creates notebook tabs and populates them with commands."""
        for tab_name, commands in self.commands_data.items():
            tab_frame = ttk.Frame(self.notebook, style="TFrame", padding="10")
            self.notebook.add(tab_frame, text=tab_name)

            # Create a scrollable canvas inside each tab
            canvas = tk.Canvas(tab_frame, bg=self.colors["bg_primary"], highlightthickness=0)
            scrollbar = ttk.Scrollbar(tab_frame, orient="vertical", command=canvas.yview)
            scrollable_frame = ttk.Frame(canvas, style="TFrame")

            scrollable_frame.bind(
                "<Configure>",
                lambda e, canvas=canvas: canvas.configure(
                    scrollregion=canvas.bbox("all")
                )
            )

            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=tab_frame.winfo_width())
            canvas.configure(yscrollcommand=scrollbar.set)

            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

            # Bind canvas width to parent frame width for responsiveness
            tab_frame.bind("<Configure>", lambda e, canvas=canvas, sf=scrollable_frame: canvas.itemconfigure(canvas.find_withtag("all")[0], width=e.width))

            for i, (desc, cmd_template) in enumerate(commands):
                row_frame = ttk.Frame(scrollable_frame, style="TFrame")
                row_frame.pack(fill='x', pady=3, padx=5)
                # Configure columns for alignment: label takes space, buttons have fixed width
                row_frame.grid_columnconfigure(0, weight=1) # Command label
                row_frame.grid_columnconfigure(1, weight=0) # Copy button
                row_frame.grid_columnconfigure(2, weight=0) # Execute button
                row_frame.grid_columnconfigure(3, weight=1) # NEW: Empty column to push buttons left

                # Command description label
                label = ttk.Label(row_frame, text=desc, font=('Consolas', 9), wraplength=300, justify=tk.LEFT)
                label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

                # Copy button
                copy_button = ttk.Button(row_frame, text="Copy", style="Copy.TButton",
                                         command=partial(self.copy_command_with_feedback, cmd_template, label))
                copy_button.grid(row=0, column=1, padx=5, pady=5, sticky="e")

                # Execute button - conditional based on command type
                if cmd_template == "OPEN_DIST_FOLDER_SPECIAL_COMMAND":
                    execute_button = ttk.Button(row_frame, text="Open", style="Execute.TButton",
                                                command=self._open_dist_folder)
                else:
                    execute_button = ttk.Button(row_frame, text="Execute", style="Execute.TButton",
                                                command=partial(self.execute_command_in_terminal, cmd_template))
                execute_button.grid(row=0, column=2, padx=5, pady=5, sticky="e")

    def browse_path(self, entry_widget: ttk.Entry, is_directory: bool = False):
        """
        Opens a file or directory dialog and updates the given entry widget with the selected path.

        Args:
            entry_widget: The ttk.Entry widget to update.
            is_directory: If True, opens a directory dialog; otherwise, opens a file dialog.
        """
        initial_dir = os.path.dirname(entry_widget.get()) if entry_widget.get() and os.path.exists(entry_widget.get()) else os.path.expanduser("~")
        try:
            if is_directory:
                path = filedialog.askdirectory(initialdir=initial_dir)
            else:
                path = filedialog.askopenfilename(initialdir=initial_dir)
            if path:
                entry_widget.delete(0, tk.END)
                entry_widget.insert(0, path)
                logging.info(f"Path selected: {path}")
        except Exception as e:
            logging.error(f"Error during path browsing: {e}", exc_info=True)
            if self.show_popups:
                messagebox.showerror("Error", f"Failed to browse path: {e}")

    def copy_command_with_feedback(self, cmd_template: str, feedback_label: ttk.Label):
        """
        Constructs a command, copies it to the clipboard, and provides visual feedback on the label.

        Args:
            cmd_template: The command string template with placeholders.
            feedback_label: The label widget to provide visual feedback on.
        """
        cmd = self._format_command(cmd_template)
        if not cmd: # _format_command already shows error/warning
            return

        try:
            pyperclip.copy(cmd)
            # Visual feedback: temporarily change label style
            original_style = feedback_label.cget('style') # Get current style
            feedback_label.configure(style='Success.TLabel')
            self.root.after(750, lambda: feedback_label.configure(style=original_style)) # Restore after 0.75 sec

            if self.show_popups:
                messagebox.showinfo("Copied!", f"Command copied to clipboard:\n{cmd}")
            logging.info(f"Command copied: {cmd}")
        except Exception as e:
            logging.error(f"Failed to copy command '{cmd}' to clipboard: {e}", exc_info=True)
            if self.show_popups:
                messagebox.showerror("Error", f"Failed to copy to clipboard:\n{e}")

    def _format_command(self, cmd_template: str) -> str:
        """
        Formats the command template with current entry field values.
        Performs basic validation for required placeholders.

        Args:
            cmd_template: The command template string.

        Returns:
            The formatted command string, or an empty string if validation fails.
        """
        # Special handling for "OPEN_DIST_FOLDER_SPECIAL_COMMAND" as it's not a shell command
        if cmd_template == "OPEN_DIST_FOLDER_SPECIAL_COMMAND":
            return cmd_template # Return as is, it will be handled by _open_dist_folder

        env = self.env_entry.get().strip()
        script = self.script_entry.get().strip()
        py_path = self.py_path_entry.get().strip()

        # Basic input validation for essential paths
        missing_inputs = []
        if "{env}" in cmd_template and not env:
            missing_inputs.append("Virtual Environment Path")
        if "{script}" in cmd_template and not script:
            missing_inputs.append("Script Path")
        if "{py_path}" in cmd_template and not py_path:
            missing_inputs.append("Python Executable Path")
        
        if missing_inputs:
            warning_msg = f"Please fill in the following required fields:\n- " + "\n- ".join(missing_inputs)
            if self.show_popups:
                messagebox.showwarning("Missing Input", warning_msg)
            logging.warning(f"Command formatting failed due to missing inputs: {', '.join(missing_inputs)}")
            return ""

        # Normalize paths for the current OS (e.g., convert / to \ on Windows)
        # os.path.normpath is generally robust for this.
        # For Windows, explicit replacement for PowerShell scripts might be needed.
        if platform.system() == 'Windows':
            env = os.path.normpath(env)
            script = os.path.normpath(script)
            py_path = os.path.normpath(py_path)
            # Special handling for PowerShell activation scripts
            if "activate.ps1" in cmd_template.lower():
                 cmd_template = cmd_template.replace('/', '\\')

        try:
            return cmd_template.format(env=env, script=script, py_path=py_path)
        except KeyError as e:
            error_msg = f"Command template format error: Missing placeholder '{e}'. Template: {cmd_template}"
            logging.error(error_msg, exc_info=True)
            if self.show_popups:
                messagebox.showerror("Formatting Error", error_msg)
            return ""
        except Exception as e:
            error_msg = f"An unexpected error occurred during command formatting: {e}. Template: {cmd_template}"
            logging.error(error_msg, exc_info=True)
            if self.show_popups:
                messagebox.showerror("Error", error_msg)
            return ""

    def _execute_terminal_input_command(self, event=None):
        """
        Executes the command entered in the terminal input entry field.
        This method is bound to the 'Run' button and the Enter key in the input field.
        """
        command = self.terminal_input_entry.get().strip()
        if not command or command == "Type command here and press Enter...": # Check for placeholder text
            return

        self.terminal_input_entry.delete(0, tk.END) # Clear the input field
        self._add_placeholder(None) # Re-add placeholder after clearing

        # Pass the raw command directly to _run_command, no template formatting needed here
        self._log_terminal_output(f"> {command}", new_command=True)
        threading.Thread(target=self._run_command, args=(command,)).start()
        logging.info(f"User input command initiated: {command}")


    def execute_command_in_terminal(self, cmd_template: str):
        """
        Executes a formatted command (from a cheat sheet button) in a separate thread and displays output in the terminal widget.

        Args:
            cmd_template: The command string template with placeholders.
        """
        cmd = self._format_command(cmd_template)
        if not cmd: # _format_command already shows error/warning
            return

        self._log_terminal_output(f"> {cmd}", new_command=True)

        # Execute command in a separate thread to keep GUI responsive
        threading.Thread(target=self._run_command, args=(cmd,)).start()
        logging.info(f"Command execution initiated from button: {cmd}")

    def _run_command(self, command: str):
        """
        Internal method to run the command and capture its output.
        Handles OS-specific shell requirements and error conditions.
        This runs in a separate thread.

        Args:
            command: The full command string to execute.
        """
        use_shell = True
        executable = None

        if platform.system() == 'Windows':
            # For PowerShell activation scripts, use powershell.exe explicitly
            if "activate.ps1" in command.lower() and not command.lower().startswith("powershell.exe"):
                # Ensure the path to activate.ps1 is quoted if it contains spaces
                command = f"powershell.exe -NoProfile -ExecutionPolicy Bypass -Command \"& '{command}'\""
                use_shell = False # powershell.exe is the explicit executable
            elif command.lower().startswith("python ") or command.lower().startswith("pip "):
                # For python/pip commands, it's generally safe with shell=True on Windows
                pass
        else: # Linux/macOS
            # 'source' command requires shell=True to modify the current shell's environment
            if "source " in command.lower() and not command.lower().startswith("source "):
                command = f"source {command}"
                use_shell = True
            elif command.lower().startswith("python ") or command.lower().startswith("pip "):
                # For python/pip on Unix, shell=True is usually fine.
                pass

        try:
            process = subprocess.run(
                command,
                shell=use_shell,
                capture_output=True,
                text=True, # Decode stdout/stderr as text
                check=False, # Do not raise CalledProcessError automatically for non-zero exit codes
                encoding='utf-8', # Specify encoding for cross-platform consistency
                errors='replace' # Replace un-decodable characters
            )

            if process.stdout:
                self._log_terminal_output(process.stdout.strip())
            if process.stderr:
                self._log_terminal_output(process.stderr.strip(), is_error=True)

            if process.returncode != 0:
                error_msg = f"Command failed with exit code {process.returncode}."
                logging.error(f"{error_msg} Command: {command}")
                self._log_terminal_output(error_msg, is_error=True)
                if self.show_popups:
                    self.root.after(0, lambda: messagebox.showerror("Command Failed", f"Command '{command}' failed.\nSee terminal for details."))
            else:
                logging.info(f"Command executed successfully: {command}")

        except FileNotFoundError:
            error_msg = f"Error: Command or executable not found. Check your PATH or command spelling. Command: '{command}'"
            logging.error(error_msg, exc_info=True)
            self._log_terminal_output(error_msg, is_error=True)
            if self.show_popups:
                self.root.after(0, lambda: messagebox.showerror("Error", "Command or executable not found.\nCheck your paths and environment setup."))
        except Exception as e:
            error_msg = f"An unexpected error occurred during command execution: {e}. Command: '{command}'"
            logging.error(error_msg, exc_info=True)
            self._log_terminal_output(error_msg, is_error=True)
            if self.show_popups:
                self.root.after(0, lambda: messagebox.showerror("Error", f"An unexpected error occurred:\n{e}\nSee terminal for details."))
        finally:
            self._log_terminal_output(f"Execution finished.", new_command=False) # No new command tag, just a line break

    def _open_dist_folder(self):
        """
        Opens the PyInstaller 'dist' folder, derived from the script path.
        """
        script_path = self.script_entry.get().strip()
        if not script_path:
            if self.show_popups:
                messagebox.showwarning("Missing Input", "Please provide a Script Path to open the dist folder.")
            self._log_terminal_output("Cannot open dist folder: Script Path is not set.", is_error=True)
            return

        script_dir = os.path.dirname(script_path)
        if not script_dir: # If script_path is just a filename, assume current working directory
            script_dir = os.getcwd()

        dist_path = os.path.join(script_dir, "dist")
        dist_path = os.path.normpath(dist_path) # Normalize path for consistency

        if not os.path.isdir(dist_path):
            if self.show_popups:
                messagebox.showwarning("Folder Not Found", f"The 'dist' folder was not found at:\n{dist_path}\n"
                                                          "Please ensure you've built the executable first.")
            self._log_terminal_output(f"Error: 'dist' folder not found at {dist_path}", is_error=True)
            return

        self._open_directory(dist_path)

    def _open_directory(self, path: str):
        """Opens a directory using the default file explorer for the OS."""
        try:
            if platform.system() == "Windows":
                os.startfile(path)
            elif platform.system() == "Darwin": # macOS
                subprocess.run(["open", path], check=True)
            else: # Linux
                subprocess.run(["xdg-open", path], check=True)
            self._log_terminal_output(f"Opened folder: {path}")
        except FileNotFoundError:
            error_msg = f"Error: Command to open folder not found on your system. Path: {path}"
            logging.error(error_msg)
            self._log_terminal_output(error_msg, is_error=True)
            if self.show_popups:
                messagebox.showerror("Error", error_msg)
        except subprocess.CalledProcessError as e:
            error_msg = f"Error opening folder '{path}': {e.stderr.strip()}"
            logging.error(error_msg)
            self._log_terminal_output(error_msg, is_error=True)
            if self.show_popups:
                messagebox.showerror("Error", error_msg)
        except Exception as e:
            error_msg = f"An unexpected error occurred while opening folder '{path}': {e}"
            logging.error(error_msg, exc_info=True)
            self._log_terminal_output(error_msg, is_error=True)
            if self.show_popups:
                messagebox.showerror("Error", error_msg)


    def _log_terminal_output(self, message: str, is_error: bool = False, new_command: bool = False):
        """
        Logs a message to the terminal output widget.
        This function is designed to be called from any thread, ensuring GUI updates
        are marshaled to the main Tkinter thread using `self.root.after()`.

        Args:
            message: The message string to log.
            is_error: If True, the message is treated as an error and styled differently.
            new_command: If True, indicates the start of a new command execution, adding a separator.
        """
        self.root.after(0, lambda: self._update_terminal_text(message, is_error, new_command))

    def _update_terminal_text(self, message: str, is_error: bool, new_command: bool):
        """
        Inserts message into the terminal text widget and scrolls to the end.
        This function MUST be called from the main Tkinter thread.
        """
        self.terminal_output.configure(state='normal') # Enable editing temporarily

        if new_command:
            self.terminal_output.insert(tk.END, f"\n--- {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---\n", 'new_command')
        
        tag = 'error' if is_error else 'normal'
        self.terminal_output.insert(tk.END, message + "\n", tag)
        self.terminal_output.see(tk.END) # Scroll to the end
        self.terminal_output.configure(state='disabled') # Disable editing again

    def _clear_terminal_output(self):
        """Clears all text from the terminal output widget."""
        self.terminal_output.configure(state='normal')
        self.terminal_output.delete(1.0, tk.END)
        self.terminal_output.configure(state='disabled')
        self._log_terminal_output("Terminal cleared.", new_command=True)

    def _clear_placeholder(self, event):
        """Clears the placeholder text from the terminal input entry when focused."""
        if self.terminal_input_entry.get() == "Type command here and press Enter...":
            self.terminal_input_entry.delete(0, tk.END)
            self.terminal_input_entry.configure(style="TEntry") # Change style to normal Entry style

    def _add_placeholder(self, event):
        """Adds the placeholder text to the terminal input entry if it's empty when unfocused."""
        if not self.terminal_input_entry.get():
            self.terminal_input_entry.insert(0, "Type command here and press Enter...")
            self.terminal_input_entry.configure(style="Placeholder.TEntry") # Revert to placeholder style


    def toggle_popups(self):
        """Toggles the state of information pop-up messages."""
        self.show_popups = self.popup_var.get()
        logging.info(f"Pop-ups {'enabled' if self.show_popups else 'disabled'}.")

    def save_config(self):
        """Saves the current configuration (paths and popup setting) to a JSON file."""
        config_data = {
            "env_path": self.env_entry.get(),
            "script_path": self.script_entry.get(),
            "py_path": self.py_path_entry.get(),
            "show_popups": self.show_popups
        }
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")],
                title="Save Configuration"
            )
            if file_path:
                with open(file_path, 'w') as f:
                    json.dump(config_data, f, indent=4)
                if self.show_popups:
                    messagebox.showinfo("Config Saved", "Configuration saved successfully!")
                logging.info(f"Configuration saved to {file_path}")
        except Exception as e:
            logging.error(f"Failed to save configuration: {e}", exc_info=True)
            if self.show_popups:
                messagebox.showerror("Error", f"Failed to save configuration:\n{e}")

    def load_config(self):
        """Loads configuration (paths and popup setting) from a selected JSON file."""
        try:
            file_path = filedialog.askopenfilename(
                defaultextension=".json",
                filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")],
                title="Load Configuration"
            )
            if file_path:
                with open(file_path, 'r') as f:
                    config_data = json.load(f)

                self._set_entry_value(self.env_entry, config_data.get("env_path", ""))
                self._set_entry_value(self.script_entry, config_data.get("script_path", ""))
                self._set_entry_value(self.py_path_entry, config_data.get("py_path", ""))
                
                # Update popup setting
                self.show_popups = config_data.get("show_popups", True) # Default to True if not found
                self.popup_var.set(self.show_popups) # Update checkbutton state

                if self.show_popups:
                    messagebox.showinfo("Config Loaded", "Configuration loaded successfully!")
                logging.info(f"Configuration loaded from {file_path}")
        except FileNotFoundError:
            logging.warning("No config file selected or file not found during load.")
        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse JSON configuration file: {e}", exc_info=True)
            if self.show_popups:
                messagebox.showerror("Error", f"Failed to load configuration: Invalid JSON file.\n{e}")
        except Exception as e:
            logging.error(f"Failed to load configuration: {e}", exc_info=True)
            if self.show_popups:
                messagebox.showerror("Error", f"Failed to load configuration:\n{e}")

    def _set_entry_value(self, entry_widget: ttk.Entry, value: str):
        """Helper to safely set the value of an Entry widget."""
        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, value)

if __name__ == "__main__":
    root = tk.Tk()
    app = VirtualEnvTool(root)
    root.mainloop()
