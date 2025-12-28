# Unreal Engine MCP Integration Guide - Session C

> **L1 Strategic Agent**: Unreal Engine MCP Integration
> **Session Date**: 2025-12-28
> **Status**: READY FOR INSTALLATION (UE5 not installed)

---

## Executive Summary

This document provides comprehensive guidance for integrating Unreal Engine 5 with the Ziggie ecosystem via Model Context Protocol (MCP). The Unreal MCP server implementation exists and is fully functional, but requires Unreal Engine 5.5+ installation to enable.

### Current State

| Component | Status | Location |
|-----------|--------|----------|
| MCP Server Config | Configured (disabled) | C:\Ziggie\.mcp.json |
| Python MCP Server | Ready | C:\ai-game-dev-system\mcp-servers\unreal-mcp\Python\ |
| UnrealMCP Plugin | Ready | C:\ai-game-dev-system\mcp-servers\unreal-mcp\MCPGameProject\Plugins\UnrealMCP\ |
| Unreal Engine 5 | NOT INSTALLED | C:\Program Files\Epic Games\ (empty) |
| Hub Integration | Configured | UNREAL_MCP_URL: http://localhost:8081 |

---

## 1. Installation Requirements

### 1.1 Unreal Engine 5.5+ Installation

**Recommended Method**: Epic Games Launcher

```text
1. Download Epic Games Launcher: https://www.unrealengine.com/download
2. Install Unreal Engine 5.5+ (or latest 5.x)
3. Required disk space: ~100-150 GB
4. Installation path: C:\Program Files\Epic Games\UE_5.x
```

**Alternative**: Compiled from source (for advanced users)
- GitHub: https://github.com/EpicGames/UnrealEngine (requires Epic Games account link)

### 1.2 System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| OS | Windows 10 64-bit | Windows 11 64-bit |
| CPU | Quad-core Intel/AMD | 6+ cores |
| RAM | 16 GB | 32+ GB |
| GPU | DirectX 12 compatible | RTX 3060+ |
| Disk | SSD 256 GB | NVMe SSD 500+ GB |

### 1.3 Python Environment

The Unreal MCP server requires Python 3.10+ with specific dependencies:

```bash
# Using uv (recommended - already configured in .mcp.json)
cd C:\ai-game-dev-system\mcp-servers\unreal-mcp
uv sync

# Or using pip
pip install mcp websockets aiohttp
```

---

## 2. Unreal MCP Server Architecture

### 2.1 Component Overview

```text
┌─────────────────────────────────────────────────────────────────┐
│                      Claude Code / AI Agent                      │
└─────────────────────────────────────────────────────────────────┘
                                │ MCP Protocol (stdio)
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│              Python MCP Server (unreal_mcp_server.py)            │
│              Port: 8081 (configurable)                           │
└─────────────────────────────────────────────────────────────────┘
                                │ TCP Socket / HTTP
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│              UnrealMCP Plugin (C++ UE Plugin)                    │
│              Running inside Unreal Editor                        │
└─────────────────────────────────────────────────────────────────┘
                                │ Unreal API
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Unreal Engine 5.5+ Editor                     │
│              Blueprints, Actors, Assets, Levels                  │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 File Structure

```text
C:\ai-game-dev-system\mcp-servers\unreal-mcp\
├── Python/
│   ├── unreal_mcp_server.py          # Main MCP server
│   ├── tools/
│   │   ├── blueprint_tools.py        # Blueprint creation/modification
│   │   ├── editor_tools.py           # Editor commands
│   │   ├── node_tools.py             # Blueprint node manipulation
│   │   ├── project_tools.py          # Project management
│   │   └── umg_tools.py              # UMG/UI tools
│   ├── scripts/                      # Test scripts
│   │   ├── actors/
│   │   ├── blueprints/
│   │   └── node/
│   ├── .venv/                        # Python virtual environment
│   └── README.md
├── MCPGameProject/                   # Reference UE5 project
│   ├── Plugins/UnrealMCP/           # The MCP plugin
│   │   ├── Source/UnrealMCP/
│   │   │   ├── Private/
│   │   │   │   ├── Commands/
│   │   │   │   │   ├── UnrealMCPBlueprintCommands.cpp
│   │   │   │   │   ├── UnrealMCPBlueprintNodeCommands.cpp
│   │   │   │   │   ├── UnrealMCPEditorCommands.cpp
│   │   │   │   │   ├── UnrealMCPProjectCommands.cpp
│   │   │   │   │   └── UnrealMCPUMGCommands.cpp
│   │   │   │   ├── MCPServerRunnable.cpp
│   │   │   │   ├── UnrealMCPBridge.cpp
│   │   │   │   └── UnrealMCPModule.cpp
│   │   │   └── Public/              # Header files
│   │   ├── UnrealMCP.Build.cs
│   │   └── UnrealMCP.uplugin
│   ├── Config/
│   ├── MCPGameProject.uproject
│   └── MCPGameProject.sln
├── Docs/
│   ├── README.md
│   └── Tools/
│       ├── actor_tools.md
│       ├── blueprint_tools.md
│       ├── editor_tools.md
│       └── node_tools.md
├── mcp.json                          # MCP server configuration
├── venv/                             # Alternative venv
└── README.md
```

---

## 3. MCP Server Configuration

### 3.1 Current Configuration (C:\Ziggie\.mcp.json)

```json
{
  "unreal-mcp": {
    "command": "cmd",
    "args": [
      "/c", "cd", "/d", "C:\\ai-game-dev-system\\mcp-servers\\unreal-mcp",
      "&&", "uv", "run", "python", "src/unreal_mcp_server.py"
    ],
    "env": {
      "UNREAL_HOST": "127.0.0.1",
      "UNREAL_PORT": "8081"
    },
    "disabled": true,
    "_comment": "Enable when Unreal Engine 5.5+ is installed with UnrealMCP plugin"
  }
}
```

### 3.2 Hub Integration

The MCP Hub server is configured to route Unreal requests:

```json
{
  "hub": {
    "env": {
      "UNREAL_MCP_URL": "http://localhost:8081"
    }
  }
}
```

### 3.3 Enabling Unreal MCP

To enable the Unreal MCP server after UE5 installation:

1. Edit `C:\Ziggie\.mcp.json`
2. Change `"disabled": true` to `"disabled": false` for unreal-mcp
3. Verify the Python path matches your setup
4. Restart Claude Code to load the new configuration

---

## 4. UnrealMCP Plugin Installation

### 4.1 Copy Plugin to Your Project

```bash
# Copy the UnrealMCP plugin to your UE5 project
xcopy /E /I "C:\ai-game-dev-system\mcp-servers\unreal-mcp\MCPGameProject\Plugins\UnrealMCP" "C:\YourProject\Plugins\UnrealMCP"
```

### 4.2 Enable Plugin in UE5 Editor

1. Open your project in Unreal Editor
2. Go to Edit > Plugins
3. Search for "UnrealMCP"
4. Enable the plugin
5. Restart the Editor when prompted

### 4.3 Verify Plugin Loading

After restarting, check the Output Log for:
```
LogUnrealMCP: UnrealMCP Plugin Loaded
LogUnrealMCP: MCP Server started on port 8081
```

---

## 5. Available MCP Tools

### 5.1 Blueprint Tools

| Tool | Description |
|------|-------------|
| `create_blueprint` | Create a new Blueprint class |
| `add_component` | Add component to Blueprint |
| `compile_blueprint` | Compile Blueprint |
| `spawn_blueprint` | Spawn Blueprint actor in level |

### 5.2 Editor Tools

| Tool | Description |
|------|-------------|
| `open_level` | Open a level by path |
| `save_level` | Save current level |
| `create_level` | Create new level |
| `get_selected_actors` | Get currently selected actors |
| `focus_viewport` | Focus viewport on actor |

### 5.3 Node Tools

| Tool | Description |
|------|-------------|
| `add_node` | Add node to Blueprint graph |
| `connect_nodes` | Connect two nodes |
| `get_node_info` | Get node properties |
| `delete_node` | Remove node from graph |

### 5.4 Project Tools

| Tool | Description |
|------|-------------|
| `get_project_info` | Get project configuration |
| `list_assets` | List assets in folder |
| `import_asset` | Import external asset |
| `export_asset` | Export asset to file |

### 5.5 UMG Tools (UI)

| Tool | Description |
|------|-------------|
| `create_widget` | Create UMG widget |
| `add_widget_child` | Add child to widget |
| `set_widget_property` | Set widget property |

---

## 6. Claude Code Integration

### 6.1 Example Commands

Once Unreal MCP is enabled, you can use commands like:

```text
User: Create a new Blueprint actor called "EnemySpawner" with a Box Collision component

Claude: I'll create the Blueprint and add the component...
[Uses create_blueprint and add_component tools]
```

### 6.2 Asset Import Workflow

```text
User: Import all PNG files from C:\assets\textures into the project

Claude: I'll scan the folder and import each texture...
[Uses project_tools.list_files and import_asset]
```

### 6.3 Level Design Automation

```text
User: Create a new level called "Level_01" and spawn 10 enemy spawners in a grid pattern

Claude: I'll create the level and place the actors...
[Uses create_level, spawn_blueprint with calculated positions]
```

---

## 7. Python Bridge Setup

### 7.1 Python Scripting in UE5

Unreal Engine 5 includes built-in Python scripting:

1. Enable Python Editor Script Plugin:
   - Edit > Plugins > Scripting > Python Editor Script Plugin

2. Python paths are automatically added:
   - `{ProjectDir}/Content/Python`
   - `{EngineDir}/Content/Python`

### 7.2 Remote Control API (Alternative)

UE5's Remote Control API provides HTTP-based automation:

1. Enable Remote Control API Plugin
2. Access via HTTP: `http://localhost:30010/remote/`

### 7.3 Command Line Automation

```bash
# Run UE5 with Python script
"C:\Program Files\Epic Games\UE_5.5\Engine\Binaries\Win64\UnrealEditor-Cmd.exe" ^
  "C:\YourProject\YourProject.uproject" ^
  -ExecutePythonScript="C:\scripts\my_automation.py"
```

---

## 8. Troubleshooting

### 8.1 Connection Issues

**Problem**: MCP server can't connect to Unreal Editor

**Solutions**:
1. Verify Unreal Editor is running
2. Check plugin is loaded (Output Log)
3. Verify port 8081 is not blocked
4. Check firewall settings

```powershell
# Test port connectivity
Test-NetConnection -ComputerName localhost -Port 8081
```

### 8.2 Plugin Not Loading

**Problem**: UnrealMCP plugin not appearing in Editor

**Solutions**:
1. Verify .uplugin file syntax
2. Check UE5 version compatibility (5.5+)
3. Rebuild project in Visual Studio
4. Check Output Log for errors

### 8.3 Python Server Errors

**Problem**: unreal_mcp_server.py crashes

**Solutions**:
1. Verify Python 3.10+ is installed
2. Check uv is installed: `uv --version`
3. Reinstall dependencies: `uv sync`
4. Check UNREAL_HOST and UNREAL_PORT environment variables

---

## 9. Quick Start Checklist

### Phase 1: Install Unreal Engine

- [ ] Download Epic Games Launcher
- [ ] Install Unreal Engine 5.5+
- [ ] Verify installation at `C:\Program Files\Epic Games\UE_5.5\`

### Phase 2: Install UnrealMCP Plugin

- [ ] Copy plugin to your project's Plugins folder
- [ ] Open project in Unreal Editor
- [ ] Enable UnrealMCP plugin
- [ ] Restart Editor
- [ ] Verify plugin loaded in Output Log

### Phase 3: Configure MCP Server

- [ ] Verify Python 3.10+ installed
- [ ] Install uv: `pip install uv`
- [ ] Navigate to `C:\ai-game-dev-system\mcp-servers\unreal-mcp`
- [ ] Run: `uv sync`
- [ ] Test server: `uv run python Python/unreal_mcp_server.py`

### Phase 4: Enable in Claude Code

- [ ] Edit `C:\Ziggie\.mcp.json`
- [ ] Set `"disabled": false` for unreal-mcp
- [ ] Restart Claude Code
- [ ] Verify Unreal MCP server appears in available tools

### Phase 5: Verify Integration

- [ ] Open Unreal Editor with your project
- [ ] Verify MCP server connects (Output Log)
- [ ] Test a simple command via Claude Code
- [ ] Document any issues for troubleshooting

---

## 10. Future Enhancements

### 10.1 Planned Features

| Feature | Priority | Status |
|---------|----------|--------|
| Asset generation integration (ComfyUI -> UE5) | HIGH | Planned |
| Level streaming automation | MEDIUM | Planned |
| PCG (Procedural Content Generation) tools | MEDIUM | Planned |
| Niagara VFX automation | LOW | Backlog |
| Behavior tree integration | LOW | Backlog |

### 10.2 MeowPing RTS Integration

For the MeowPing RTS project, Unreal MCP will enable:

1. **Unit Asset Import**: Import 2D sprites generated by ComfyUI
2. **Level Generation**: Procedural map creation
3. **Blueprint Automation**: AI behavior blueprints
4. **Build Automation**: Packaging and distribution

---

## 11. References

### 11.1 Internal Documentation

| Document | Path |
|----------|------|
| MCP Configuration | C:\Ziggie\.mcp.json |
| Game Engine MCP Guide | C:\Ziggie\docs\GAME-ENGINE-MCP-INSTALLATION-GUIDE.md |
| Unity MCP Guide | C:\Ziggie\docs\UNITY-MCP-INTEGRATION-SESSION-C.md |
| Hub MCP Server | C:\ai-game-dev-system\mcp-servers\hub\ |

### 11.2 External Resources

- Unreal Engine Documentation: https://docs.unrealengine.com
- UnrealMCP GitHub: https://github.com/vgvishesh/UnrealMCP
- MCP Specification: https://modelcontextprotocol.io
- Python Scripting in UE5: https://docs.unrealengine.com/5.5/en-US/scripting-the-unreal-editor-using-python/

### 11.3 Related Files

| File | Purpose |
|------|---------|
| unreal_mcp_server.py | Main MCP server entry point |
| blueprint_tools.py | Blueprint manipulation tools |
| editor_tools.py | Editor automation tools |
| node_tools.py | Blueprint graph node tools |
| project_tools.py | Project/asset management |
| umg_tools.py | UI widget tools |
| UnrealMCP.uplugin | Plugin descriptor |
| MCPServerRunnable.cpp | Plugin server thread |
| UnrealMCPBridge.cpp | MCP-to-UE bridge |

---

## 12. Session C Findings Summary

### Key Discoveries

1. **Unreal MCP Implementation Exists**: Complete Python MCP server and C++ plugin ready
2. **UE5 Not Installed**: No Unreal Engine found at `C:\Program Files\Epic Games\`
3. **Configuration Ready**: MCP hub already configured with UNREAL_MCP_URL
4. **Documentation Available**: Tool documentation in Docs/Tools/*.md

### Blocking Issue

**Unreal Engine 5.5+ must be installed** to enable Unreal MCP integration.

### Recommended Next Steps

1. Install Unreal Engine 5.5+ via Epic Games Launcher (~100-150 GB)
2. Test with MCPGameProject reference project first
3. Then integrate UnrealMCP plugin into MeowPing RTS project
4. Enable unreal-mcp in .mcp.json after verification

---

*Document generated by L1 Strategic Agent - Session C*
*Path: C:\Ziggie\docs\UNREAL-MCP-INTEGRATION-SESSION-C.md*
