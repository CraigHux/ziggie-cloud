@echo off
REM Ziggie Control Center - Desktop Shortcut Creator
REM This script creates a desktop shortcut for the Ziggie launcher

setlocal enabledelayedexpansion
cd /d "%~dp0"

REM Get the desktop path
for /f "tokens=3" %%A in ('reg query "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders" /v Desktop 2^>nul') do set "DESKTOP=%%A"

if not defined DESKTOP (
    echo Error: Could not determine Desktop location
    pause
    exit /b 1
)

REM Define paths
set "LAUNCHER_PATH=%~dp0ziggie-launcher.bat"
set "SHORTCUT_PATH=%DESKTOP%\Ziggie Control Center.lnk"
set "ICON_PATH=%~dp0icon.ico"

REM Check if launcher exists
if not exist "%LAUNCHER_PATH%" (
    echo.
    echo ============================================
    echo ERROR: Launcher not found
    echo ============================================
    echo.
    echo Could not find: %LAUNCHER_PATH%
    echo.
    pause
    exit /b 1
)

REM Create the shortcut using PowerShell
echo Creating desktop shortcut...
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
"try { ^
    $WshShell = New-Object -ComObject WScript.Shell; ^
    $Shortcut = $WshShell.CreateShortcut('%SHORTCUT_PATH%'); ^
    $Shortcut.TargetPath = '%LAUNCHER_PATH%'; ^
    $Shortcut.WorkingDirectory = '%~dp0'; ^
    $Shortcut.Description = 'Ziggie Control Center Launcher'; ^
    $Shortcut.WindowStyle = 1; ^
    if (Test-Path '%ICON_PATH%') { ^
        $Shortcut.IconLocation = '%ICON_PATH%'; ^
    } else { ^
        $Shortcut.IconLocation = 'C:\Windows\System32\cmd.exe, 0'; ^
    } ^
    $Shortcut.Save(); ^
    Write-Host 'Shortcut created successfully: %SHORTCUT_PATH%'; ^
} catch { ^
    Write-Host 'Error creating shortcut: $_'; ^
    exit 1; ^
}"

if %errorlevel% equ 0 (
    echo.
    echo ============================================
    echo SUCCESS
    echo ============================================
    echo.
    echo Desktop shortcut created successfully!
    echo Location: %SHORTCUT_PATH%
    echo.
    echo You can now use the shortcut to launch Ziggie with your favorite editor.
    echo.
    pause
    exit /b 0
) else (
    echo.
    echo ============================================
    echo ERROR: Failed to create shortcut
    echo ============================================
    echo.
    pause
    exit /b 1
)
