import tkinter as tk
from tkinter import ttk, messagebox
import string
import pyperclip
import secrets
from threading import Timer  

class PasswordGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.masked_var = tk.BooleanVar(value=True)  # Default masked
        self.root.title("Password Generator")
        self.root.geometry("650x400")
        
        # Initialize clipboard-related attributes
        self.clipboard_timer = None
        self.last_copied_password = None
        self.countdown_var = tk.StringVar()
        self.countdown_var.set("Clipboard: Ready")
        
        # Create menu bar
        self.create_menu_bar()
        
        # Main container
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel (for password display)
        self.left_panel = ttk.Frame(self.main_frame)
        self.left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Right panel (for controls)
        self.right_panel = ttk.Frame(self.main_frame, width=200)
        self.right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        
        # Build the interface components
        self.create_password_display()
        self.create_controls()

    def create_menu_bar(self):
        menubar = tk.Menu(self.root)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Copy Password", command=self.copy_password)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        
        self.root.config(menu=menubar)
    
    def create_password_display(self):
        # Password display frame
        display_frame = ttk.LabelFrame(self.left_panel, text="Generated Password")
        display_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Password label
        self.password_var = tk.StringVar()
        self.password_label = ttk.Label(
            display_frame, 
            textvariable=self.password_var,
            font=('Courier', 14),
            wraplength=300,
            anchor=tk.CENTER
        )
        self.password_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Action buttons
        button_frame = ttk.Frame(self.left_panel)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(
            button_frame, 
            text="Copy", 
            command=self.copy_password
        ).pack(side=tk.LEFT, expand=True, padx=5)
        
        ttk.Button(
            button_frame, 
            text="Generate New", 
            command=self.generate_password
        ).pack(side=tk.LEFT, expand=True, padx=5)

        ttk.Button(
            button_frame,
            text="👁",  
            command=self.toggle_mask,
            width=3
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            button_frame, 
            text="Clear", 
            command=self.clear_all
        ).pack(side=tk.LEFT, expand=True, padx=5)

    def clear_all(self):
        """Clear both clipboard and displayed password"""
        # Clear clipboard
        try:
            pyperclip.copy('')
        except:
            pass
        
        # Clear display
        self.password_var.set('')
        
        # Cancel any countdown
        if self.clipboard_timer is not None:
            self.clipboard_timer.cancel()
            self.clipboard_timer = None
        
        # Update status
        self.countdown_var.set("Clipboard: Cleared")
    
    def create_controls(self):
        """Create the right panel controls"""
        # Controls frame
        controls_frame = ttk.LabelFrame(self.right_panel, text="Password Options")
        controls_frame.pack(fill=tk.BOTH, padx=5, pady=5)
        
        # Length control
        ttk.Label(controls_frame, text="Length (8-32):").pack(anchor=tk.W, pady=(5, 0))
        self.length_var = tk.IntVar(value=12)
        length_scale = tk.Scale(
            controls_frame,
            from_=8,
            to=32,
            variable=self.length_var,
            orient=tk.HORIZONTAL,
            command=lambda v: self.length_var.set(round(float(v))),
            bg="#f0f0f0",
            highlightthickness=0
        )
        length_scale.pack(fill=tk.X, padx=5, pady=(0, 10))
        
        # Character type options with validation
        self.upper_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            controls_frame,
            text="Uppercase Letters (A-Z)",
            variable=self.upper_var,
            command=self.validate_character_types
        ).pack(anchor=tk.W, padx=5, pady=2)
        
        self.lower_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            controls_frame,
            text="Lowercase Letters (a-z)",
            variable=self.lower_var,
            command=self.validate_character_types
        ).pack(anchor=tk.W, padx=5, pady=2)
        
        self.digits_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            controls_frame,
            text="Digits (0-9)",
            variable=self.digits_var,
            command=self.validate_character_types
        ).pack(anchor=tk.W, padx=5, pady=2)
        
        self.special_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            controls_frame,
            text="Special Characters (!@#)",
            variable=self.special_var,
            command=self.validate_character_types
        ).pack(anchor=tk.W, padx=5, pady=2)
        
        # Add countdown display
        countdown_frame = ttk.Frame(controls_frame)
        countdown_frame.pack(fill=tk.X, pady=(10, 5))
        
        ttk.Label(countdown_frame, text="Clipboard timer:").pack(side=tk.LEFT)
        self.countdown_label = ttk.Label(
            countdown_frame, 
            textvariable=self.countdown_var,
            font=('TkDefaultFont', 9, 'bold')
        )
        self.countdown_label.pack(side=tk.RIGHT)
 
        # Generate button
        ttk.Button(
            controls_frame,
            text="Generate Password",
            command=self.generate_password,
            style="Accent.TButton"
        ).pack(fill=tk.X, pady=10)
        
    def validate_character_types(self):
        """Ensure at least one character type is selected"""
        if not any([self.upper_var.get(), self.lower_var.get(), 
                    self.digits_var.get(), self.special_var.get()]):
            if self.special_var.get() is False:
                self.special_var.set(True)
            elif self.digits_var.get() is False:
                self.digits_var.set(True)
            elif self.lower_var.get() is False:
                self.lower_var.set(True)
            else:
                self.upper_var.set(True)
            
            messagebox.showwarning(
                "Selection Required",
                "At least one character type must be selected"
            )
    
    def generate_password(self):
        """Generate a cryptographically secure random password"""
        char_sets = {
            'upper': string.ascii_uppercase if self.upper_var.get() else '',
            'lower': string.ascii_lowercase if self.lower_var.get() else '',
            'digits': string.digits if self.digits_var.get() else '',
            'special': string.punctuation if self.special_var.get() else ''
        }
        
        # Get all available characters
        all_chars = ''.join(char_sets.values())
        if not all_chars:
            return
        
        length = self.length_var.get()
        
        # Ensure at least one character from each selected set
        password = []
        for char_type, chars in char_sets.items():
            if chars:
                password.append(secrets.choice(chars))
        
        # Fill the rest randomly
        while len(password) < length:
            password.append(secrets.choice(all_chars))
        
        # Shuffle to avoid predictable patterns
        secrets.SystemRandom().shuffle(password)
        
        # Store original password and set display based on mask state
        self.original_password = ''.join(password)
        self.update_password_display()

    def update_password_display(self):
        """Update password display based on mask state"""
        if hasattr(self, 'original_password'):
            if self.masked_var.get():
                self.password_var.set('•' * len(self.original_password))
                self.password_label.config(font=('Courier', 14))  # Normal font
            else:
                self.password_var.set(self.original_password)
                self.password_label.config(font=('Courier', 14, 'bold'))  # Bold when visible

    def toggle_mask(self):
        """Toggle password visibility"""
        self.masked_var.set(not self.masked_var.get())
        self.update_password_display()
        
    def update_countdown(self, remaining):
        """Update the countdown display"""
        if remaining > 0:
            self.countdown_var.set(f"Clearing in: {remaining}s")
            self.countdown_id = self.root.after(1000, self.update_countdown, remaining-1)
        else:
            # When countdown finishes, trigger clipboard check
            self.clear_clipboard_if_unchanged()
    
    def copy_password(self):
        """Copy the generated password to clipboard with safety timer"""
        password = self.password_var.get()
        if not password:
            messagebox.showwarning("Empty", "No password to copy")
            return
            
        # Cancel any pending clear operation
        if hasattr(self, 'countdown_id'):
            self.root.after_cancel(self.countdown_id)
             
        # Copy to clipboard
        pyperclip.copy(password)
        self.last_copied_password = password
        messagebox.showinfo("Copied", "Password copied to clipboard! (Will clear in 30 seconds)")

        # Start visual countdown
        self.update_countdown(30)
        
        # Schedule clipboard clearing
        self.clipboard_timer = Timer(30.0, self.clear_clipboard_if_unchanged)
        self.clipboard_timer.start()

    def clear_clipboard_if_unchanged(self):
        """Clear clipboard only if it still contains our password"""
        try:
            current_clipboard = pyperclip.paste()
            if current_clipboard == self.last_copied_password:
                # Case 1: Our password was auto-cleared
                pyperclip.copy('')
                self.countdown_var.set("Clipboard: Cleared")
                messagebox.showinfo(
                    "Clipboard Cleared", 
                    "Password has been automatically cleared from clipboard for security."
                )
            else:
                # Case 2: User copied something else during countdown
                self.countdown_var.set("Clipboard: No Passwords")
                return  # Don't proceed with clearing if password changed
        except Exception as e:
            self.countdown_var.set("Clipboard: Error")
        finally:
            self.last_copied_password = None
            self.clipboard_timer = None

    def on_close(self):
        """Clean up when closing the application"""
        if self.clipboard_timer is not None:
            self.clipboard_timer.cancel()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordGeneratorApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
