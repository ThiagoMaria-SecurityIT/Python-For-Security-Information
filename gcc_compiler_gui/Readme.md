# GCC Compiler GUI - Readme

## Overview
This application provides a graphical interface for compiling and running C programs using GCC, with optional Windows Sandbox support for secure compilation of untrusted code.

<p align="center">
  <img src="./images/image1.png" alt="GCC Compiler GUI Screenshot" width="600">
  <br>
  <em>GCC Compiler GUI Interface</em>
</p>

## Features
- Drag-and-drop interface for C source files
- Recent files history
- Terminal output with error highlighting
- Local compilation with GCC
- Windows Sandbox integration for secure execution
- Dark theme support

## Requirements
- Python 3.x
- Tkinter (usually included with Python)
- GCC compiler (via MSYS2 or other distribution)
- Windows 10/11 Pro/Enterprise for Sandbox functionality

## Installation

### 1. Install Python dependencies:
```bash
pip install tkinterdnd2 sv-ttk
```

### 2. Install GCC via MSYS2 (if not already installed):

#### Windows:
1. Download MSYS2 from [https://www.msys2.org/](https://www.msys2.org/)
2. Run the installer and follow the prompts
3. After installation, open MSYS2 terminal and run:
   ```bash
   pacman -Syu
   pacman -S mingw-w64-x86_64-gcc
   ```

#### Linux/macOS:
Most distributions come with GCC pre-installed. If not:
- Debian/Ubuntu: `sudo apt install gcc`
- macOS (using Homebrew): `brew install gcc`

### 3. Add GCC to PATH (Windows Tip):
After MSYS2 installation, add the MinGW binaries to your system PATH:
1. Find your MSYS2 installation directory (typically `C:\msys64`)
2. Add the following to your system PATH environment variable:
   ```
   C:\msys64\mingw64\bin
   ```
3. Restart your terminal/IDE for changes to take effect

## Security Considerations

### 1. Windows Sandbox Integration
The application includes detection and integration with Windows Sandbox for secure compilation:

#### Sandbox Detection Logic:
- Checks for Windows 10/11 Pro/Enterprise
- Verifies the "Containers-DisposableClientVM" feature is enabled using DISM
- Provides visual status indication in the UI

#### Sandbox Security Features:
- Isolated environment that disappears after closing
- Read/write access only to specified folders
- Memory limits (4GB in this implementation)
- Automatic termination capability

### 2. General Security Practices:
- Always verify source code before compiling locally
- Use Sandbox for untrusted code
- The application doesn't require admin privileges by default
- Temporary files are properly cleaned up after Sandbox sessions

### 3. Limitations:
- Sandbox only available on Windows Pro/Enterprise
- Local compilation requires trust in the source code
- No network isolation in the basic implementation

## Usage
1. Drag and drop a `.c` file onto the application or use the browse button
2. Click "Compile" to build locally or "Compile in Sandbox" for isolated compilation
3. Run the compiled program with the "Run" button
4. Use "Terminate Sandbox" to end any active sandbox instances

## Troubleshooting
- If GCC is not found, verify your PATH environment variable includes the MinGW binaries
- Sandbox requires virtualization to be enabled in BIOS
- Admin privileges may be required for some Sandbox operations

## License
MIT License

## About the Author

**Thiago de Maria - From Brazil to the World 🌎**  
*Senior Security Information Analyst | Passionate Programmer*

With a professional background in security analysis and a deep passion for programming, I created this tool to bridge the gap between secure development practices and accessible compiler interfaces. Most of my work here focuses on implementing security-first approaches in developer tools while maintaining usability.

Lets Connect:

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue)](https://www.linkedin.com/in/thiago-cequeira-99202239/)  
[![Hugging Face](https://img.shields.io/badge/🤗Hugging_Face-AI_projects-yellow)](https://huggingface.co/ThiSecur)
