@echo off
REM Control Center Backend Installation Script

echo ========================================
echo Control Center Backend - Installation
echo ========================================
echo.

REM Check for Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

echo Python found:
python --version
echo.

REM Create virtual environment (optional but recommended)
echo Do you want to create a virtual environment? (y/n)
set /p CREATE_VENV=

if /i "%CREATE_VENV%"=="y" (
    echo Creating virtual environment...
    python -m venv venv

    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

REM Install dependencies
echo.
echo Installing dependencies from requirements.txt...
pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo To start the server:
echo   1. Run: run.bat
echo   2. Or manually: python main.py
echo.
echo To test the server:
echo   python test_server.py
echo.
echo Server will run on: http://127.0.0.1:8080
echo.
pause
