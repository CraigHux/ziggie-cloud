@echo off
REM ============================================
REM Ziggie - Start All Services
REM ============================================
REM
REM This script starts all Ziggie services:
REM  1. Control Center Backend (port 8080)
REM  2. Control Center Frontend (port 3000)
REM  3. Knowledge Base status display
REM
REM Services will open in separate console windows
REM
REM Prerequisites:
REM  - Python 3.11+ installed
REM  - Node.js 20+ installed
REM  - All dependencies installed
REM  - Configuration paths updated to C:\Ziggie
REM

setlocal enabledelayedexpansion

echo.
echo ============================================
echo Ziggie - All Services Startup
echo ============================================
echo.

REM Check if directories exist
if not exist "C:\Ziggie\control-center\backend" (
    echo ERROR: Backend directory not found at C:\Ziggie\control-center\backend
    echo.
    pause
    exit /b 1
)

if not exist "C:\Ziggie\control-center\frontend" (
    echo ERROR: Frontend directory not found at C:\Ziggie\control-center\frontend
    echo.
    pause
    exit /b 1
)

if not exist "C:\Ziggie\ai-agents\knowledge-base" (
    echo ERROR: Knowledge Base directory not found at C:\Ziggie\ai-agents\knowledge-base
    echo.
    pause
    exit /b 1
)

echo Starting services in separate windows...
echo.

REM Start backend in new window
echo [1/3] Starting Backend on port 54112...
start "Ziggie Backend" cmd /k "cd /d C:\Ziggie\control-center\backend && python main.py"

REM Wait for backend to initialize
timeout /t 3 /nobreak

REM Start frontend in new window
echo [2/3] Starting Frontend on port 3001...
start "Ziggie Frontend" cmd /k "cd /d C:\Ziggie\control-center\frontend && npm run dev"

REM Wait for frontend to initialize
timeout /t 2 /nobreak

REM Show Knowledge Base status in new window
echo [3/3] Opening Knowledge Base Status...
start "Ziggie Knowledge Base Status" cmd /k "cd /d C:\Ziggie\ai-agents\knowledge-base && python manage.py status && pause"

echo.
echo ============================================
echo Services Started!
echo ============================================
echo.
echo Backend: http://127.0.0.1:54112
echo Backend Docs: http://127.0.0.1:54112/docs
echo.
echo Frontend: http://localhost:3001
echo.
echo Knowledge Base: C:\Ziggie\ai-agents\knowledge-base
echo.
echo All services are running in separate windows
echo Use Ctrl+C in any window to stop that service
echo.
echo Close all windows to fully stop Ziggie
echo.
pause
