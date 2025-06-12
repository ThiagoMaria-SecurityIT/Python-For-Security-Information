# 🔐 Secure Password Generator  

#### Love this tool? Help me keep it updated!  

[![GitHub Sponsors](https://img.shields.io/badge/Sponsor-%E2%9D%A4-red?logo=GitHub&style=for-the-badge)](https://github.com/sponsors/ThiagoMaria-SecurityIT)
## Overview
A cryptographically secure password generator application built with Python and Tkinter.  
Designed for users who need reliable password generation without unnecessary complexity.

![App Screenshot](https://github.com/ThiagoMaria-SecurityIT/Tutoriais/blob/main/SecurePassGenerator/images/securimathiago2.png) 

## Key Features

### Security Features
- **Cryptographically Secure Generation**
  - Utilizes Python's `secrets` module (OS-level entropy sources)
  - Generates truly random passwords using `secrets` module
  - Guarantees at least one character from each selected character set
- **Secure Memory Handling**
  - Passwords are wiped from memory after generation
- **Controlled Clipboard Exposure**
  - Automatic clipboard clearing after 30 seconds with visual countdown
  - Detects external clipboard modifications during countdown
    
### User Experience
- Adjustable password length (8-32 characters)
- Selectable character sets
- Configurable character sets:
  - Uppercase (A-Z)
  - Lowercase (a-z)
  - Digits (0-9)
  - Special characters (!@# etc.)
- Password visibility toggle
- One-click clipboard and display clearing (Copy to clipboard functionality)
- Cross-platform (Windows/macOS/Linux)

### 🌟 Easy to use
- 🔄 One-click generation with customizable length (8-32 chars)  
- 📋 Auto-copy (clipboard clears after 30 seconds)  
- 🎲 True randomness (powered by your OS’s crypto magic)  
- 🎨 Clean GUI (no confusing menus)
  
  ## Technical Specifications
- **Language**: Python 3.8+
- **Dependencies**: 
  - Standard Libraries Only (`tkinter`, `secrets`, `pyperclip`)
- **Platform Support**: Windows, macOS, Linux
- **Security Architecture**:
  - No network connectivity
  - No password storage  
  - No telemetry or analytics  
    

## Security Notes
- Passwords are generated locally and never stored/transmitted
- Uses OS-level cryptographic randomness (`/dev/urandom` or Windows equivalent)
- Guarantees at least one character from each selected set
  
## 🌟 Superpowers (Fun part of code)
- **🎲 Crypto-Grade Randomness**  
  Uses your OS's best kept secrets (`secrets` module)
- **⏱️ Self-Destructing Clipboard**  
  Auto-wipes passwords after 30 seconds (with countdown!)
- **👁️ Peek-a-Boo Mode**  
  Toggle password visibility with one click
- **🧹 One-Click Cleanup**  
  Wipe both display and clipboard instantly
## 🔒 Security Guarantees

1. **No Telemetry**: The app never connects to the internet.
2. **Memory Protection**: 
   - Passwords are wiped from memory after generation
   - Uses Python's `secrets` module (cryptographically secure)
3. **Clipboard Safety**: 
   - Pyperclip automatically clears clipboard after 30s  
---
## ⚡ Quick Start  
1. **Download**: Click "Code" → "Download ZIP"  
2. **Run**: Double-click `main.py` (needs [Python](https://www.python.org/downloads/) and **pyperclip** (pip install pyperclip))
   
## Alternative Installation 
```bash
# Clone the repository
git clone https://github.com/ThiagoMaria-SecurityIT/SecurePassGenerator.git

# Navigate to project directory
cd SecurePassGenerator

# Install pyperclip
pip install pyperclip

# Run the application
python main.py
``` 
---
## Usage Guide
1. Configure desired password length using the slider
2. Select required character sets
3. Click "Generate Password"
4. Use the visibility toggle (👁) to reveal/hide password
5. Copy to clipboard (auto-clears after 30 seconds)
6. Use "Clear" to immediately remove password from display and clipboard

## Security Considerations
- Always verify the integrity of downloaded scripts
- For maximum security, generate passwords on air-gapped systems
- Consider your operating system's clipboard management policies

## Development
```python
# Key Architecture Components
- PasswordGeneratorApp class (main application logic)
- Tkinter-based GUI
- Thread-safe clipboard management
```

---
🛡️ Security Specs  
```
SecurityLevel = {  
    "Randomness": "OS-grade (/dev/urandom)",   
    "Memory": "Auto-wiped",  
    "Clipboard": "30s time bomb 💣"  
}  
```
---

## 🤔 Why Trust This?  
| Security Feature      | Guarantee                               |  
|-----------------------|-----------------------------------------|  
| **Randomness**        | Uses your OS’s built-in crypto (no DIY math!) |  
| **No Internet**       | Runs 100% offline—no sneaky calls home  |  
| **Clipboard Safety**  | Auto-wipes after 30 seconds (has a countdown)            |  

---
## 🤝 Credits & Disclaimer  

**Development Assistance**:  
This project was created with AI-powered suggestions from [DeepSeek Chat](https://deepseek.com) (like a very smart rubber duck 🦆💡).  

**Important Notes**:  
🔐 **Passwords**: Generated passwords are cryptographically secure and safe to use.  
⚠️ **Code**: Review before production use - as with any open-source project, test thoroughly in your environment.  

---
## 🎩 Hat Tip

Cheers to DeepSeek's AI for not judging my 3AM coding questions.  
While the passwords are **pro-level secure**, treat the code like a beginner skateboarder – **wear a helmet!** 🛹⚠️  

## 📜 License  
MIT License © Thiago Maria - See [LICENSE](LICENSE) for full details – *Use it, share it.*  

## Acknowledgements
- Python Cryptographic Authority for the `secrets` module
- Tkinter maintainers
- Pyperclip developers
  
## ☕ Support the Project
Love this tool? Help me keep it updated!  

[![GitHub Sponsors](https://img.shields.io/badge/Sponsor-%E2%9D%A4-red?logo=GitHub&style=for-the-badge)](https://github.com/sponsors/ThiagoMaria-SecurityIT)
