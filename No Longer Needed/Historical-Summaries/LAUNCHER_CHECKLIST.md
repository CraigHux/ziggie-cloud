# Ziggie Launcher Verification Checklist

## 1. Pre-Flight Checks

### Python Installation
- [ ] Python 3.6+ is installed on the system
  - Run: `python --version` in Command Prompt or PowerShell
  - Expected output: `Python 3.x.x` (version 3.6 or higher)
  - If not installed: Download from https://www.python.org
    - **IMPORTANT**: Check "Add Python to PATH" during installation
    - Restart Command Prompt after installation

### Required Files
- [ ] `C:\Ziggie\ziggie-launcher.bat` exists
- [ ] `C:\Ziggie\ziggie-launcher.py` exists
- [ ] `C:\Ziggie\create-desktop-shortcut.bat` exists (optional for shortcut creation)
- [ ] Workspace directory `C:\Ziggie` is accessible and readable

### File Integrity
- [ ] All launcher files are readable (not corrupted)
- [ ] File permissions allow execution

### Dependencies
- [ ] tkinter module is available (included with Python standard installation)
  - Test: Run `python -c "import tkinter; print('OK')"` in Command Prompt
  - If not available: Reinstall Python with tcl/tk support enabled

---

## 2. How to Test the Launcher

### Quick Test (No Desktop Shortcut)
1. Open Command Prompt or PowerShell
2. Navigate to the Ziggie directory: `cd C:\Ziggie`
3. Run the launcher:
   ```batch
   ziggie-launcher.bat
   ```
4. The launcher window should appear within 2-3 seconds
5. Verify the window displays:
   - Title: "Ziggie Control Center - Launcher"
   - Welcome message with editor selection
   - Two buttons: "VS Code" and "Cursor"
   - Session type radio buttons

### Test Editor Installation Check
1. Run the launcher (see Quick Test above)
2. Click "VS Code" button
   - If VS Code is NOT installed: Error dialog should appear with installation link
   - If VS Code IS installed: It should launch with C:\Ziggie workspace
3. Close the launcher and run again
4. Click "Cursor" button
   - If Cursor is NOT installed: Error dialog should appear with installation link
   - If Cursor IS installed: It should launch with C:\Ziggie workspace

### Test Session Options
1. Run the launcher
2. Select "New Session" (default)
3. Click an editor button
4. Verify: Editor opens in a new window
5. Run launcher again
6. Select "Continue Previous Session"
7. Click an editor button
8. Verify: Editor opens in the existing window (if editor supports reuse-window)

---

## 3. Common Errors and Solutions

### Error: "Python is not installed or not found"
**Cause**: Python not in PATH or not installed
**Solution**:
1. Install Python from https://www.python.org
2. During installation, CHECK "Add Python to PATH"
3. Restart Command Prompt after installation
4. Test: `python --version`

### Error: "Failed to launch the launcher"
**Cause**: ziggie-launcher.py is missing or corrupted
**Solution**:
1. Verify file exists: `dir C:\Ziggie\ziggie-launcher.py`
2. Check file size is reasonable (>5 KB)
3. Check file is readable (not corrupted)
4. If corrupted, restore from backup

### Error: "VS Code is not installed or not accessible"
**Cause**: VS Code not installed or not in PATH
**Solution**:
1. Install VS Code from https://code.visualstudio.com
2. Add VS Code to PATH during installation (option to check)
3. Test: Run `code --version` in Command Prompt
4. If still fails, reinstall VS Code with PATH option enabled

### Error: "Cursor is not installed or not accessible"
**Cause**: Cursor not installed or not in PATH
**Solution**:
1. Install Cursor from https://cursor.sh
2. Ensure installation added Cursor to PATH
3. Test: Run `cursor --version` in Command Prompt
4. If command not recognized, reinstall Cursor

### Error: "Could not determine Desktop location" (Desktop shortcut creation)
**Cause**: Registry key for Desktop path is missing or inaccessible
**Solution**:
1. Manually verify Desktop location (usually `C:\Users\[Username]\Desktop`)
2. Ensure you have read/write permissions to Desktop
3. Try running the shortcut creation script as Administrator
4. Create shortcut manually: Right-click > New > Shortcut
   - Target: `C:\Ziggie\ziggie-launcher.bat`
   - Start in: `C:\Ziggie`

### Launcher Window Not Appearing
**Cause**: Python subprocess issues or missing tkinter
**Solution**:
1. Verify tkinter is installed: `python -c "import tkinter; print('OK')"`
2. Try running with explicit Python path:
   ```batch
   C:\Path\To\python.exe C:\Ziggie\ziggie-launcher.py
   ```
3. Check Command Prompt for error messages
4. Reinstall Python with tcl/tk support

### Editor Launches but Workspace Not Loaded
**Cause**: Editor not set to open workspace path
**Solution**:
1. Verify `C:\Ziggie` directory exists and is accessible
2. Manually open editor: `code C:\Ziggie` or `cursor C:\Ziggie`
3. Check for permission issues on C:\Ziggie directory
4. Ensure editor installation is complete

---

## 4. Verification Steps After Creating Desktop Shortcut

### Before Creating Shortcut
- [ ] Run `ziggie-launcher.bat` directly from C:\Ziggie directory
- [ ] Verify it launches without errors
- [ ] Test both VS Code and Cursor buttons (or whichever is installed)

### Creating the Shortcut
1. Open Command Prompt or PowerShell as Administrator
2. Navigate to C:\Ziggie: `cd C:\Ziggie`
3. Run: `create-desktop-shortcut.bat`
4. Success message should appear:
   ```
   Shortcut created successfully: C:\Users\[Username]\Desktop\Ziggie Control Center.lnk
   ```

### After Creating Shortcut
- [ ] Shortcut appears on Desktop with correct name
- [ ] Shortcut icon displays correctly
- [ ] Double-click the shortcut launches the launcher window
- [ ] Launcher functions normally (buttons work, editors launch)
- [ ] Can select editor preference and open workspace
- [ ] Session options work (new vs. continue)

### Shortcut Properties Verification
1. Right-click shortcut > Properties
2. Verify:
   - **Target**: `C:\Ziggie\ziggie-launcher.bat`
   - **Start in**: `C:\Ziggie`
   - **Run**: Minimized or Normal window
   - **Description**: "Ziggie Control Center Launcher"

---

## 5. Quick Troubleshooting Guide

### Launcher Won't Start
1. Test Python: `python --version`
2. Test tkinter: `python -c "import tkinter"`
3. Verify files exist: `dir C:\Ziggie\ziggie-launcher.*`
4. Run from Command Prompt to see error: `python C:\Ziggie\ziggie-launcher.py`

### Launcher Opens but Buttons Don't Work
1. Check editor installation: `code --version` or `cursor --version`
2. Verify C:\Ziggie directory exists and is readable
3. Try running editor manually: `code C:\Ziggie` or `cursor C:\Ziggie`
4. Check for permission issues or antivirus blocking

### Shortcut Not Working
1. Delete shortcut and recreate it
2. Run shortcut creation script as Administrator
3. Manually create shortcut if automated method fails
4. Verify target path uses quotes if path contains spaces

### Launcher Crashes or Freezes
1. Check for Python updates: `python --version`
2. Restart Command Prompt/PowerShell
3. Restart computer if issue persists
4. Run Command Prompt as Administrator
5. Check Event Viewer for error details (Windows + E > Right-click > Event Viewer)

### Editor Doesn't Launch
1. Test editor directly: `code C:\Ziggie` or `cursor C:\Ziggie`
2. Check if editor is properly installed
3. Verify editor is in PATH: `where code` or `where cursor`
4. Check C:\Ziggie permissions (should be readable/accessible)
5. Check for antivirus blocking editor launch

### Session Options Not Working
1. Verify correct editor is installed
2. Some editors may not support `--reuse-window` flag
3. Try "New Session" option as default
4. Check editor version compatibility

---

## Summary Checklist

Before considering the launcher ready for use, ensure all items pass:

- [ ] Python 3.6+ installed and in PATH
- [ ] All launcher files present and intact
- [ ] tkinter module available
- [ ] Launcher starts without errors
- [ ] Launcher window displays correctly
- [ ] VS Code button works (if VS Code installed)
- [ ] Cursor button works (if Cursor installed)
- [ ] Session options function correctly
- [ ] Desktop shortcut created successfully (if needed)
- [ ] Shortcut launches launcher correctly
- [ ] Both editors accept workspace path correctly

---

## Quick Reference Commands

| Task | Command |
|------|---------|
| Test Python | `python --version` |
| Test tkinter | `python -c "import tkinter; print('OK')"` |
| Launch launcher | `C:\Ziggie\ziggie-launcher.bat` |
| Test VS Code | `code --version` |
| Test Cursor | `cursor --version` |
| Create shortcut | `C:\Ziggie\create-desktop-shortcut.bat` (as Admin) |
| Find VS Code | `where code` |
| Find Cursor | `where cursor` |
| Direct Python launch | `python C:\Ziggie\ziggie-launcher.py` |

---

## Support Resources

- **Python Installation**: https://www.python.org/downloads/
- **VS Code**: https://code.visualstudio.com
- **Cursor**: https://cursor.sh
- **Ziggie Documentation**: Check C:\Ziggie\README.md
- **Windows Path Configuration**: https://www.computerhope.com/issues/ch000549.htm

