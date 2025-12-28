@echo off
REM Ziggie Control Center - Docker Startup Script
REM This script stops all non-containerized services and starts Docker containers

echo ========================================
echo   Ziggie Control Center - Docker Mode
echo ========================================
echo.

echo [1/4] Stopping non-containerized services...
echo.
REM Kill any Python processes on port 54112
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :54112') do (
    echo Stopping process %%a on port 54112...
    taskkill /F /PID %%a >nul 2>&1
)

REM Kill any Node processes on port 3001
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3001') do (
    echo Stopping process %%a on port 3001...
    taskkill /F /PID %%a >nul 2>&1
)

echo Done.
echo.

echo [2/4] Building Docker images...
echo.
cd /d C:\Ziggie
docker-compose build

echo.
echo [3/4] Starting Docker containers...
echo.
docker-compose up -d

echo.
echo [4/4] Checking container status...
echo.
docker-compose ps

echo.
echo ========================================
echo   Ziggie Control Center is now running
echo ========================================
echo.
echo   Backend API:  http://localhost:54112
echo   API Docs:     http://localhost:54112/docs
echo   Frontend:     http://localhost:3001
echo   MongoDB:      mongodb://localhost:27017
echo.
echo To view logs: docker-compose logs -f
echo To stop:      docker-compose down
echo.
pause
