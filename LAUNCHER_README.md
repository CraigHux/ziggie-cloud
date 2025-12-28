# Ziggie Control Center - Launcher

A desktop launcher application that provides a graphical interface to choose between **VS Code** or **Cursor** and open the Ziggie workspace.

## Features

- **Easy Editor Selection**: Simple GUI to choose between VS Code or Cursor
- **Session Management**: Option to start a new session or continue from the previous session
- **Installation Verification**: Automatically checks if the selected editor is installed
- **Professional Interface**: Dark theme with tech-inspired colors
- **Quick Launch**: Desktop shortcut for easy access
- **Error Handling**: Helpful error messages with installation links

## Files

- **ziggie-launcher.py** - Main Python GUI application using tkinter
- **ziggie-launcher.bat** - Batch wrapper that checks for Python and runs the launcher
- **create-desktop-shortcut.bat** - Script to create a desktop shortcut
- **LAUNCHER_README.md** - This documentation file

## Prerequisites

### Required

1. **Python 3.7+** - Must be installed and added to PATH
   - Download from: https://www.python.org
   - **Important**: Check "Add Python to PATH" during installation

2. **Either VS Code or Cursor** (or both)
   - **VS Code**: https://code.visualstudio.com
   - **Cursor**: https://cursor.sh

### Optional

- Custom icon file (`C:\Ziggie\icon.ico`) - For better desktop shortcut appearance
  - If not present, a default Windows command prompt icon will be used

## Installation & Setup

### Step 1: Verify Python Installation

Open Command Prompt and run:

```bash
python --version
```

You should see output like: `Python 3.x.x`

If not installed, download and install from https://www.python.org

### Step 2: Install VS Code and/or Cursor

- **VS Code**: Download from https://code.visualstudio.com
- **Cursor**: Download from https://cursor.sh

Make sure to install them in their default locations and ensure the command-line tools are available.

### Step 3: Create Desktop Shortcut (Optional but Recommended)

Run the shortcut creation script:

```bash
C:\Ziggie\create-desktop-shortcut.bat
```

This will create a shortcut on your Desktop named "Ziggie Control Center" that you can double-click to launch the application.

## Usage

### Method 1: Desktop Shortcut

After running `create-desktop-shortcut.bat`, look for "Ziggie Control Center" on your Desktop and double-click it.

### Method 2: Command Line

Open Command Prompt or PowerShell and run:

```bash
C:\Ziggie\ziggie-launcher.bat
```

Or directly with Python:

```bash
python C:\Ziggie\ziggie-launcher.py
```

### Method 3: File Explorer

Navigate to `C:\Ziggie` and double-click `ziggie-launcher.bat`

## How to Use the Launcher

1. **Launch the Application**
   - The Ziggie Control Center window opens with a welcome message

2. **Select an Editor**
   - Click the "VS Code" button to open VS Code
   - Click the "Cursor" button to open Cursor

3. **Choose Session Type** (optional)
   - **New Session**: Opens a fresh workspace (default)
   - **Continue Previous Session**: Reopens the previous workspace state if available

4. **Automatic Launch**
   - The launcher verifies the editor is installed
   - Opens the editor with the C:\Ziggie workspace
   - Closes automatically after successful launch

## Troubleshooting

### "Python is not installed or not found"

**Solution**: Install Python from https://www.python.org

During installation, make sure to:
1. Check the box "Add Python to PATH"
2. Complete the installation
3. Restart your command prompt or computer

### "VS Code/Cursor is not installed or not accessible"

**Solutions**:
1. Install the editor from the provided link
2. Use the default installation location
3. Make sure the command-line tools are installed (the installer option)
4. Restart your computer after installation

To verify the editor is accessible, open Command Prompt and run:
```bash
code --version      # For VS Code
cursor --version    # For Cursor
```

### Launcher window appears but nothing happens

**Solutions**:
1. Check that Python is properly installed: `python --version`
2. Verify the editor is accessible from command line
3. Check that C:\Ziggie directory exists
4. Try running from Command Prompt instead of double-clicking

### Can't find the launcher files

**Solutions**:
1. Verify all files are in `C:\Ziggie`:
   - ziggie-launcher.py
   - ziggie-launcher.bat
   - create-desktop-shortcut.bat
   - LAUNCHER_README.md

2. If files are missing, re-download or recreate them

## Customization

### Custom Icon

To use a custom icon for the desktop shortcut:

1. Create or obtain an icon file (.ico format)
2. Save it as `C:\Ziggie\icon.ico`
3. Run `create-desktop-shortcut.bat` again

The launcher will automatically use this icon for both the desktop shortcut and the window.

### Color Theme

To modify the color scheme, edit `ziggie-launcher.py` and look for the `configure_style` method:

```python
self.bg_color = "#1a1a1a"      # Dark background (change hex color)
self.fg_color = "#e8e8e8"      # Light text
self.accent_color = "#4a9eff"  # Tech blue
self.success_color = "#4caf50" # Green
self.warning_color = "#ff9800" # Orange
```

### Window Size

To change the window size, modify this line in the `__init__` method:

```python
self.root.geometry("500x450")  # Change dimensions (width x height)
```

## System Information

- **Workspace Location**: C:\Ziggie
- **Supported Platforms**: Windows
- **Python Version**: 3.7+
- **GUI Framework**: tkinter (included with Python)

## What Happens When You Launch

1. **Editor Check**: The launcher verifies the selected editor is installed
2. **Workspace Setup**: Opens the C:\Ziggie directory in the editor
3. **Session Management**:
   - New Session: Opens with fresh state
   - Continue Previous Session: Uses `--reuse-window` flag to restore previous state
4. **Launcher Closes**: The launcher window closes automatically after 1 second

## Integration with Control Center

The launcher is part of the Ziggie Control Center ecosystem:
- Located in: `C:\Ziggie\ziggie-launcher.py`
- Workspace path: `C:\Ziggie`
- Compatible with both frontend and backend directories

## Support & Documentation

For more information about Ziggie:
- Frontend: `C:\Ziggie\control-center\frontend`
- Backend: `C:\Ziggie\control-center\backend`

## Version History

### v1.0 (2025-11-08)
- Initial release
- Support for VS Code and Cursor
- Session type selection
- Desktop shortcut creation
- Professional UI with dark theme
- Comprehensive error handling

## Notes

- The launcher requires active internet connection for editor installation links
- Some antivirus software may flag batch files; these are safe to use
- The launcher doesn't modify any workspace files, it only opens them in an editor
- Session preference (New vs Continue) is remembered within the launcher window

## License & Attribution

Ziggie Control Center Launcher - Part of the Ziggie ecosystem

---

**Last Updated**: November 8, 2025
**Status**: Production Ready
