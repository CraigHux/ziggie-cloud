@echo off
REM ============================================
REM Ziggie - Knowledge Base Status Check
REM ============================================
REM
REM This script checks the status of the Knowledge Base
REM system and displays any path-related issues
REM
REM Prerequisites:
REM  - Python 3.11+ installed
REM  - Knowledge Base configured (.env file)
REM

echo.
echo ============================================
echo Ziggie Knowledge Base - Status Check
echo ============================================
echo.

REM Navigate to KB directory
cd /d C:\Ziggie\ai-agents\knowledge-base

if not exist "manage.py" (
    echo ERROR: manage.py not found!
    echo Current directory: %cd%
    echo.
    echo Make sure you're in the correct location:
    echo   C:\Ziggie\ai-agents\knowledge-base
    echo.
    pause
    exit /b 1
)

if not exist ".env" (
    echo WARNING: .env file not found
    echo.
    echo Creating .env from .env.example...
    if exist ".env.example" (
        copy .env.example .env
        echo Created .env - please review and update API keys
    ) else (
        echo ERROR: .env.example not found either
        echo.
        pause
        exit /b 1
    )
)

echo Checking Knowledge Base Status...
echo.
echo Location: C:\Ziggie\ai-agents\knowledge-base
echo.

python manage.py status

if errorlevel 1 (
    echo.
    echo ERROR: Knowledge Base check failed
    echo Check the error messages above
    echo.
    pause
    exit /b 1
)

echo.
echo.
pause
