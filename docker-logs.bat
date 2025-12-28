@echo off
REM Ziggie Control Center - Docker Logs Viewer

echo ========================================
echo   Ziggie Control Center - Live Logs
echo ========================================
echo.
echo Press Ctrl+C to stop viewing logs
echo.

cd /d C:\Ziggie
docker-compose logs -f
