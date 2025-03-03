# InvoiceTaxApp
Business invoice management and tax calculation application

```markdown
# Invoice Tax App

A business invoice management and tax calculation application with PDF import capabilities.

## Features

- Manage invoices with dates, amounts, and descriptions
- Import invoices directly from PDF remittance advices
- Calculate quarterly federal and state tax payments
- Calculate SEP 401(k) contribution limits
- Generate comprehensive tax reports
- Export data to CSV

## Installation

### Option 1: Install from GitHub (Development Version)

1. Clone the repository:
   ```
   git clone https://github.com/YOUR_USERNAME/InvoiceTaxApp.git
   cd InvoiceTaxApp
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the application:
   ```
   python -m invoicetaxapp.app
   ```

### Option 2: Install with Installer (End Users)

1. Download the latest installer from the [Releases](https://github.com/YOUR_USERNAME/InvoiceTaxApp/releases) page
2. Run the installer and follow the on-screen instructions
3. Launch the application from your desktop or start menu

### Creating Your Own Installer

To build an installer from source:

```
python installer.py
```

This will create an executable in the `dist` folder.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
```

## 5. Building a Full Windows Installer with Inno Setup

For a professional Windows installer:

1. Download and install [Inno Setup](https://jrsoftware.org/isdl.php)
2. Create an `installer.iss` file:

```
[Setup]
AppName=Invoice Tax App
AppVersion=1.0
DefaultDirName={pf}\InvoiceTaxApp
DefaultGroupName=Invoice Tax App
UninstallDisplayIcon={app}\InvoiceTaxApp.exe
Compression=lzma2
SolidCompression=yes
OutputDir=installer
OutputBaseFilename=InvoiceTaxApp_Setup

[Files]
Source: "dist\InvoiceTaxApp.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "README.md"; DestDir: "{app}"; Flags: isreadme

[Icons]
Name: "{group}\Invoice Tax App"; Filename: "{app}\InvoiceTaxApp.exe"
Name: "{commondesktop}\Invoice Tax App"; Filename: "{app}\InvoiceTaxApp.exe"

[Run]
Filename: "{app}\InvoiceTaxApp.exe"; Description: "Launch Invoice Tax App"; Flags: nowait postinstall skipifsilent
```

3. Compile with Inno Setup after building your app with PyInstaller

## 6. Working with GitHub Releases

Once you've built your installer:

1. Create a new release on GitHub:
   - Go to your repository
   - Click "Releases" on the right sidebar
   - Click "Create a new release"
   - Set a version tag (e.g., "v1.0.0")
   - Add release notes
   - Upload your installer file
   - Click "Publish release"

2. Now users can download your installer directly from GitHub