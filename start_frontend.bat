@echo off
REM ============================================
REM Ziggie - Start Control Center Frontend
REM ============================================
REM
REM This script starts the React frontend dev server
REM for the Control Center on port 3000
REM
REM Prerequisites:
REM  - Node.js 20+ installed
REM  - npm dependencies installed (see package.json)
REM  - Backend running on port 8080 (optional but recommended)
REM

echo.
echo ============================================
echo Ziggie Control Center - Frontend Startup
echo ============================================
echo.

REM Navigate to frontend directory
cd /d C:\Ziggie\control-center\frontend

if not exist "package.json" (
    echo ERROR: package.json not found!
    echo Current directory: %cd%
    echo.
    echo Make sure you're in the correct location:
    echo   C:\Ziggie\control-center\frontend
    echo.
    pause
    exit /b 1
)

if not exist "node_modules" (
    echo WARNING: node_modules not found
    echo Installing dependencies...
    echo.
    call npm install
    if errorlevel 1 (
        echo.
        echo ERROR: Failed to install dependencies
        echo.
        pause
        exit /b 1
    )
)

echo Starting Control Center Frontend...
echo.
echo Location: C:\Ziggie\control-center\frontend
echo Port: 3001
echo URL: http://localhost:3001
echo.
echo Backend: http://127.0.0.1:54112 (expected)
echo.
echo Press Ctrl+C to stop the server
echo.

call npm run dev

if errorlevel 1 (
    echo.
    echo ERROR: Frontend failed to start
    echo Check the error messages above
    echo.
    pause
    exit /b 1
)

pause
