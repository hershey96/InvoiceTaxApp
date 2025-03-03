import os
import sys
import subprocess
import platform
import argparse
import shutil
from pathlib import Path

# Application constants
APP_NAME = "InvoiceTaxApp"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "Business invoice management and tax calculation application"
GITHUB_REPO = "https://github.com/YOUR_USERNAME/InvoiceTaxApp"

def check_python_version():
    """Check if Python version is compatible"""
    required_version = (3, 7)
    current_version = sys.version_info
    
    if current_version < required_version:
        print(f"Error: {APP_NAME} requires Python {required_version[0]}.{required_version[1]} or higher.")
        print(f"Current Python version is {current_version[0]}.{current_version[1]}.{current_version[2]}")
        sys.exit(1)
    
    print(f"Python version check passed: {current_version[0]}.{current_version[1]}.{current_version[2]}")

def install_dependencies(verbose=False):
    """Install required dependencies"""
    print("Installing dependencies...")
    
    pip_args = [sys.executable, "-m", "pip", "install", "--upgrade", "pip"]
    if verbose:
        subprocess.check_call(pip_args)
    else:
        subprocess.check_call(pip_args, stdout=subprocess.DEVNULL)
    
    requirements_args = [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]
    if verbose:
        subprocess.check_call(requirements_args)
    else:
        subprocess.check_call(requirements_args, stdout=subprocess.DEVNULL)
    
    print("All dependencies installed successfully.")

def create_icon_if_missing():
    """Create a basic icon if none exists"""
    resources_dir = Path("invoicetaxapp/resources")
    icon_path = resources_dir / "icon.ico"
    
    if not resources_dir.exists():
        print(f"Creating resources directory: {resources_dir}")
        resources_dir.mkdir(parents=True, exist_ok=True)
    
    if not icon_path.exists():
        print("No icon found. Creating a basic icon...")
        try:
            from PIL import Image, ImageDraw
            
            # Create a simple icon
            img = Image.new('RGBA', (256, 256), color=(255, 255, 255, 0))
            draw = ImageDraw.Draw(img)
            
            # Drawing a simple invoice icon
            draw.rectangle([40, 40, 216, 216], fill=(66, 133, 244, 255), outline=(25, 75, 165, 255), width=8)
            draw.rectangle([70, 80, 186, 110], fill=(255, 255, 255, 255))
            draw.rectangle([70, 130, 186, 160], fill=(255, 255, 255, 255))
            draw.rectangle([70, 180, 186, 210], fill=(255, 255, 255, 255))
            
            # Save the image as .ico
            img.save(icon_path, format='ICO')
            print(f"Created basic icon at {icon_path}")
        except ImportError:
            print("Pillow not installed. Skipping icon creation.")
            print("You can create your own icon and place it at: invoicetaxapp/resources/icon.ico")

def build_windows_executable(verbose=False, one_file=True, icon_path=None):
    """Build Windows executable with PyInstaller"""
    print("Building Windows executable...")
    
    # Prepare PyInstaller command
    pyinstaller_args = [
        "pyinstaller",
        f"--name={APP_NAME}",
        "--windowed",
    ]
    
    if one_file:
        pyinstaller_args.append("--onefile")
    
    # Add icon if specified or if exists in default location
    if icon_path:
        icon_path = Path(icon_path)
    else:
        icon_path = Path("invoicetaxapp/resources/icon.ico")
    
    if icon_path.exists():
        pyinstaller_args.append(f"--icon={icon_path}")
        # Also add as data file
        pyinstaller_args.append(f"--add-data={icon_path};resources")
    
    # Add data directories
    for data_dir in ["data", "exports"]:
        if os.path.exists(data_dir):
            pyinstaller_args.append(f"--add-data={data_dir};{data_dir}")
    
    # Add main script
    pyinstaller_args.append("invoicetaxapp/app.py")
    
    # Run PyInstaller
    try:
        if verbose:
            subprocess.check_call(pyinstaller_args)
        else:
            subprocess.check_call(pyinstaller_args, stdout=subprocess.DEVNULL)
        print(f"Executable created successfully: dist/{APP_NAME}.exe")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error building executable: {e}")
        return False

def build_macos_executable(verbose=False, one_file=True, icon_path=None):
    """Build macOS executable with PyInstaller"""
    print("Building macOS application...")
    
    # Prepare PyInstaller command
    pyinstaller_args = [
        "pyinstaller",
        f"--name={APP_NAME}",
        "--windowed",
    ]
    
    if one_file:
        pyinstaller_args.append("--onefile")
    
    # Add icon if specified or if exists in default location
    if icon_path:
        icon_path = Path(icon_path)
    else:
        # For macOS, ideally use .icns format
        icon_path = Path("invoicetaxapp/resources/icon.ico")
    
    if icon_path.exists():
        pyinstaller_args.append(f"--icon={icon_path}")
        # Also add as data file, note the colon separator for macOS
        pyinstaller_args.append(f"--add-data={icon_path}:resources")
    
    # Add data directories
    for data_dir in ["data", "exports"]:
        if os.path.exists(data_dir):
            pyinstaller_args.append(f"--add-data={data_dir}:{data_dir}")
    
    # Add main script
    pyinstaller_args.append("invoicetaxapp/app.py")
    
    # Run PyInstaller
    try:
        if verbose:
            subprocess.check_call(pyinstaller_args)
        else:
            subprocess.check_call(pyinstaller_args, stdout=subprocess.DEVNULL)
        print(f"Application created successfully: dist/{APP_NAME}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error building application: {e}")
        return False

def build_linux_executable(verbose=False, one_file=True, icon_path=None):
    """Build Linux executable with PyInstaller"""
    print("Building Linux executable...")
    
    # Prepare PyInstaller command
    pyinstaller_args = [
        "pyinstaller",
        f"--name={APP_NAME}",
        "--windowed",
    ]
    
    if one_file:
        pyinstaller_args.append("--onefile")
    
    # Add icon if specified or if exists in default location
    if icon_path:
        icon_path = Path(icon_path)
    else:
        icon_path = Path("invoicetaxapp/resources/icon.ico")
    
    if icon_path.exists():
        # Also add as data file, note the colon separator for Linux
        pyinstaller_args.append(f"--add-data={icon_path}:resources")
    
    # Add data directories
    for data_dir in ["data", "exports"]:
        if os.path.exists(data_dir):
            pyinstaller_args.append(f"--add-data={data_dir}:{data_dir}")
    
    # Add main script
    pyinstaller_args.append("invoicetaxapp/app.py")
    
    # Run PyInstaller
    try:
        if verbose:
            subprocess.check_call(pyinstaller_args)
        else:
            subprocess.check_call(pyinstaller_args, stdout=subprocess.DEVNULL)
        print(f"Executable created successfully: dist/{APP_NAME}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error building executable: {e}")
        return False

def create_windows_installer(verbose=False):
    """Create Windows installer using Inno Setup"""
    print("Creating Windows installer...")
    
    # Check if Inno Setup is installed
    inno_setup_path = None
    possible_paths = [
        r"C:\Program Files\Inno Setup 6\ISCC.exe",
        r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
        r"C:\Program Files\Inno Setup 5\ISCC.exe",
        r"C:\Program Files (x86)\Inno Setup 5\ISCC.exe"
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            inno_setup_path = path
            break
    
    if not inno_setup_path:
        print("Inno Setup not found. Please install Inno Setup from https://jrsoftware.org/isdl.php")
        print("Skipping installer creation.")
        return False
    
    # Create Inno Setup script
    iss_script = f"""
[Setup]
AppName={APP_NAME}
AppVersion={APP_VERSION}
DefaultDirName={{pf}}\\{APP_NAME}
DefaultGroupName={APP_NAME}
UninstallDisplayIcon={{app}}\\{APP_NAME}.exe
Compression=lzma2
SolidCompression=yes
OutputDir=installer
OutputBaseFilename={APP_NAME}_Setup

[Files]
Source: "dist\\{APP_NAME}.exe"; DestDir: "{{app}}"; Flags: ignoreversion
Source: "README.md"; DestDir: "{{app}}"; Flags: isreadme

[Dirs]
Name: "{{app}}\\data"; Permissions: users-modify
Name: "{{app}}\\exports"; Permissions: users-modify

[Icons]
Name: "{{group}}\\{APP_NAME}"; Filename: "{{app}}\\{APP_NAME}.exe"
Name: "{{commondesktop}}\\{APP_NAME}"; Filename: "{{app}}\\{APP_NAME}.exe"

[Run]
Filename: "{{app}}\\{APP_NAME}.exe"; Description: "Launch {APP_NAME}"; Flags: nowait postinstall skipifsilent
    """
    
    # Create installer directory if it doesn't exist
    os.makedirs("installer", exist_ok=True)
    
    # Write script to file
    iss_file = "installer_script.iss"
    with open(iss_file, "w") as f:
        f.write(iss_script)
    
    # Run Inno Setup compiler
    try:
        inno_args = [inno_setup_path, iss_file]
        if verbose:
            subprocess.check_call(inno_args)
        else:
            subprocess.check_call(inno_args, stdout=subprocess.DEVNULL)
        print(f"Installer created successfully: installer/{APP_NAME}_Setup.exe")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error creating installer: {e}")
        return False

def organize_project_files():
    """Create or verify project directory structure"""
    print("Setting up project directory structure...")
    
    # Create main module directory
    os.makedirs("invoicetaxapp", exist_ok=True)
    
    # Create resources directory
    os.makedirs("invoicetaxapp/resources", exist_ok=True)
    
    # Create data and exports directories
    os.makedirs("data", exist_ok=True)
    os.makedirs("exports", exist_ok=True)
    
    # Create __init__.py if it doesn't exist
    init_file = "invoicetaxapp/__init__.py"
    if not os.path.exists(init_file):
        with open(init_file, "w") as f:
            f.write(f'__version__ = "{APP_VERSION}"\n')
    
    # Create README.md if it doesn't exist
    readme_file = "README.md"
    if not os.path.exists(readme_file):
        with open(readme_file, "w") as f:
            f.write(f"# {APP_NAME}\n\n")
            f.write(f"{APP_DESCRIPTION}\n\n")
            f.write("## Features\n\n")
            f.write("- Manage invoices with dates, amounts, and descriptions\n")
            f.write("- Import invoices directly from PDF remittance advices\n")
            f.write("- Calculate quarterly federal and state tax payments\n")
            f.write("- Calculate SEP 401(k) contribution limits\n")
            f.write("- Generate comprehensive tax reports\n")
            f.write("- Export data to CSV\n\n")
            f.write("## Installation\n\n")
            f.write("See the GitHub repository for installation instructions:\n")
            f.write(f"{GITHUB_REPO}\n")
    
    # Create requirements.txt if it doesn't exist
    requirements_file = "requirements.txt"
    if not os.path.exists(requirements_file):
        with open(requirements_file, "w") as f:
            f.write("tkcalendar>=1.6.1\n")
            f.write("pdfplumber>=0.7.6\n")
            f.write("pillow>=9.3.0\n")
            f.write("pyinstaller>=5.6.0\n")
    
    print("Project directory structure set up successfully.")

def main():
    """Main installer function"""
    parser = argparse.ArgumentParser(description=f"Build {APP_NAME} executable and installer")
    
    parser.add_argument('--verbose', '-v', action='store_true', help='Show detailed output')
    parser.add_argument('--no-onefile', action='store_true', help='Create a directory-based executable instead of a single file')
    parser.add_argument('--icon', help='Path to custom icon file')
    parser.add_argument('--skip-deps', action='store_true', help='Skip dependency installation')
    parser.add_argument('--installer', action='store_true', help='Create installer (Windows only)')
    
    args = parser.parse_args()
    
    print(f"=== {APP_NAME} Build Tool ===")
    
    # Check Python version
    check_python_version()
    
    # Set up project files
    organize_project_files()
    
    # Create an icon if missing
    create_icon_if_missing()
    
    # Install dependencies if needed
    if not args.skip_deps:
        try:
            install_dependencies(args.verbose)
        except subprocess.CalledProcessError as e:
            print(f"Error installing dependencies: {e}")
            sys.exit(1)
    
    # Build executable based on platform
    system = platform.system()
    one_file = not args.no_onefile
    success = False
    
    if system == "Windows":
        success = build_windows_executable(args.verbose, one_file, args.icon)
        if success and args.installer:
            create_windows_installer(args.verbose)
    elif system == "Darwin":  # macOS
        success = build_macos_executable(args.verbose, one_file, args.icon)
    else:  # Linux
        success = build_linux_executable(args.verbose, one_file, args.icon)
    
    if success:
        print(f"\n{APP_NAME} build completed successfully!")
        if system == "Windows":
            print(f"Executable: dist/{APP_NAME}.exe")
            if args.installer:
                print(f"Installer: installer/{APP_NAME}_Setup.exe")
        elif system == "Darwin":
            print(f"Application: dist/{APP_NAME}")
        else:
            print(f"Executable: dist/{APP_NAME}")
    else:
        print(f"\n{APP_NAME} build failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
