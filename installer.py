import os
import sys
import subprocess
import platform

def install_dependencies():
    """Install required dependencies"""
    print("Installing dependencies...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

def build_installer():
    """Build the installer for the current platform"""
    print("Building installer...")
    
    if platform.system() == "Windows":
        # Get PyInstaller
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        
        # Create the executable
        subprocess.check_call([
            "pyinstaller",
            "--name=InvoiceTaxApp",
            "--windowed",
            "--onefile",
            "--add-data=invoicetaxapp/resources/icon.ico;resources",
            "--icon=invoicetaxapp/resources/icon.ico",
            "invoicetaxapp/app.py"
        ])
        
        print("Executable created in dist/InvoiceTaxApp.exe")
        
        # Create Windows Installer (Optional, requires NSIS)
        try:
            import nsist
            # Add NSIS installer code here if needed
            print("NSIS installer creation would go here")
        except ImportError:
            print("NSIS module not found. Skipping Windows installer creation.")
            print("To create a full installer, install NSIS: https://nsis.sourceforge.io/")
    
    elif platform.system() == "Darwin":  # macOS
        subprocess.check_call([
            "pyinstaller",
            "--name=InvoiceTaxApp",
            "--windowed",
            "--onefile",
            "--add-data=invoicetaxapp/resources/icon.ico:resources",
            "--icon=invoicetaxapp/resources/icon.ico",
            "invoicetaxapp/app.py"
        ])
        print("Executable created in dist/InvoiceTaxApp")
    
    else:  # Linux
        subprocess.check_call([
            "pyinstaller",
            "--name=InvoiceTaxApp",
            "--windowed",
            "--onefile",
            "--add-data=invoicetaxapp/resources/icon.ico:resources",
            "invoicetaxapp/app.py"
        ])
        print("Executable created in dist/InvoiceTaxApp")

if __name__ == "__main__":
    install_dependencies()
    build_installer()