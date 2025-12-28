@echo off
REM Launch Godot Engine with the AITestProject (MCP-enabled)
set GODOT_PATH=C:\Users\minin\AppData\Local\Microsoft\WinGet\Packages\GodotEngine.GodotEngine_Microsoft.Winget.Source_8wekyb3d8bbwe\Godot_v4.5.1-stable_win64.exe
set PROJECT_PATH=C:\ai-game-dev-system\projects\godot\AITestProject

echo Launching Godot 4.5.1 with AITestProject...
echo.
echo IMPORTANT: Once Godot opens, the MCP addon will start a WebSocket server on port 9080.
echo The godot-mcp MCP server will then be able to connect.
echo.
"%GODOT_PATH%" --editor --path "%PROJECT_PATH%"
