# Cyber Tools
A Python-based GUI application for self-built cybersecurity tools.

## Features
- Modern Dark UI
- FTP Server & Client
- RDP Host & Client (with EXE compilation)

## Setup & Installation

> **Note:** This project uses a Python virtual environment (`cyberToolsEnv`) that is **not** included in the repository. You must create it yourself before running the app.

### 1. Create the virtual environment
```powershell
python -m venv cyberToolsEnv
```

### 2. Activate the virtual environment
```powershell
.\cyberToolsEnv\Scripts\Activate.ps1
```

### 3. Install dependencies
```powershell
pip install -r requirements.txt
```

### 4. Start the app
```powershell
python main.py
```

> **Why the venv path?** Some features (like compiling the RDP client into a `.exe`) require `pyinstaller` and `pip` to be resolved from the local `cyberToolsEnv` folder. Running with the system Python won't work for those features.