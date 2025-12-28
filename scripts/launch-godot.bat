@echo off
REM Launch Godot Engine (installed via winget)
set GODOT_PATH=C:\Users\minin\AppData\Local\Microsoft\WinGet\Packages\GodotEngine.GodotEngine_Microsoft.Winget.Source_8wekyb3d8bbwe\Godot_v4.5.1-stable_win64.exe

if exist "%GODOT_PATH%" (
    echo Launching Godot 4.5.1...
    "%GODOT_PATH%" %*
) else (
    echo ERROR: Godot not found at %GODOT_PATH%
    echo Please reinstall via: winget install GodotEngine.GodotEngine
    exit /b 1
)
