@echo off
REM ============================================
REM Ziggie - Start Control Center Backend
REM ============================================
REM
REM This script starts the FastAPI backend server
REM for the Control Center on port 8080
REM
REM Prerequisites:
REM  - Python 3.11+ installed
REM  - pip dependencies installed (see requirements.txt)
REM  - All configuration paths updated to C:\Ziggie
REM

echo.
echo ============================================
echo Ziggie Control Center - Backend Startup
echo ============================================
echo.

REM Navigate to backend directory
cd /d C:\Ziggie\control-center\backend

if not exist "main.py" (
    echo ERROR: main.py not found!
    echo Current directory: %cd%
    echo.
    echo Make sure you're in the correct location:
    echo   C:\Ziggie\control-center\backend
    echo.
    pause
    exit /b 1
)

echo Starting Control Center Backend...
echo.
echo Location: C:\Ziggie\control-center\backend
echo Port: 54112
echo URL: http://127.0.0.1:54112
echo Docs: http://127.0.0.1:54112/docs
echo.
echo Press Ctrl+C to stop the server
echo.

python main.py

if errorlevel 1 (
    echo.
    echo ERROR: Backend failed to start
    echo Check the error messages above
    echo.
    pause
    exit /b 1
)

pause
