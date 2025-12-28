@echo off
REM Ziggie Control Center - Docker Stop Script

echo ========================================
echo   Stopping Ziggie Control Center
echo ========================================
echo.

cd /d C:\Ziggie

echo Stopping Docker containers...
docker-compose down

echo.
echo ========================================
echo   All containers stopped
echo ========================================
echo.
pause
