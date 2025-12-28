@echo off
REM Control Center Backend Startup Script

echo ========================================
echo Control Center Backend
echo ========================================
echo.

REM Check if virtual environment exists
if exist venv (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo No virtual environment found.
    echo Install dependencies with: pip install -r requirements.txt
    echo.
)

echo Starting FastAPI server...
echo Server will be available at: http://127.0.0.1:8080
echo.
echo Press Ctrl+C to stop the server
echo.

python main.py
