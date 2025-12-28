@echo off
REM Ziggie Control Center - Launcher Batch Wrapper
REM This batch file checks for Python and launches the GUI launcher

setlocal enabledelayedexpansion
cd /d "%~dp0"

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ============================================
    echo ERROR: Python is not installed or not found
    echo ============================================
    echo.
    echo Please install Python from: https://www.python.org
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    echo After installing Python, please restart your command prompt.
    echo.
    pause
    exit /b 1
)

REM Launch the Python launcher GUI
echo Launching Ziggie Control Center Launcher...
python "%~dp0ziggie-launcher.py"

if %errorlevel% neq 0 (
    echo.
    echo ============================================
    echo ERROR: Failed to launch the launcher
    echo ============================================
    echo.
    echo Please ensure all files are in place:
    echo - C:\Ziggie\ziggie-launcher.py
    echo - C:\Ziggie\ziggie-launcher.bat
    echo.
    pause
    exit /b 1
)

exit /b 0
