@echo off
echo ========================================
echo Chrome DevTools Debug Launcher (Edge)
echo ========================================
echo.

set PORT=9222
set DATA_DIR=%USERPROFILE%\.cache\chrome-devtools-mcp\edge-profile-stable

if not exist "%DATA_DIR%" (
    echo Creating debug profile directory...
    mkdir "%DATA_DIR%"
)

echo Launching Edge with remote debugging on port %PORT%...
echo Profile: %DATA_DIR%
echo.

start "" "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" ^
    --remote-debugging-port=%PORT% ^
    --user-data-dir="%DATA_DIR%" ^
    --no-first-run ^
    --disable-extensions ^
    --disable-default-apps

timeout /t 3 /nobreak > nul

echo.
echo Chrome should now be running with remote debugging enabled.
echo.
echo Access Points:
echo   http://localhost:%PORT%/json
echo   http://localhost:%PORT%/json/version
echo.
echo MCP Server can now connect to Chrome!
echo ========================================
pause
