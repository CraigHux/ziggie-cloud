# Game Engine MCP Installation Guide

> **Purpose**: Complete installation guide for Unity, Unreal Engine, and Godot MCP integration
> **Last Updated**: 2025-12-28
> **Audience**: Developers setting up AI-assisted game development pipelines

---

## Table of Contents

1. [Quick Start Summary](#quick-start-summary)
2. [Unity MCP Installation](#unity-mcp-installation)
3. [Unreal Engine MCP Installation](#unreal-engine-mcp-installation)
4. [Godot MCP Installation](#godot-mcp-installation)
5. [MCP Configuration for Ziggie](#mcp-configuration-for-ziggie)
6. [Troubleshooting](#troubleshooting)
7. [Sources and References](#sources-and-references)

---

## Quick Start Summary

| Engine | Disk Space | Install Time | Prerequisites |
|--------|------------|--------------|---------------|
| **Unity** | 8-15 GB | 30-60 min | Unity Hub, Node.js 18+ |
| **Unreal Engine** | 50-100 GB | 2-4 hours | Epic Games Launcher, Python 3.12+, Visual Studio 2022 |
| **Godot** | ~500 MB | 15 min | Node.js 18+, Godot 4.x (already installed) |

### One-Command Quick Install

```powershell
# Unity MCP (after Unity is installed)
# In Unity: Window > Package Manager > + > Add package from git URL:
# https://github.com/CoderGamester/mcp-unity.git

# Unreal MCP Server (after Unreal is installed)
cd C:\ai-game-dev-system\mcp-servers\unreal-mcp\Python
uv venv && uv pip install -r requirements.txt

# Godot MCP Server (after Godot addon is enabled)
cd C:\ai-game-dev-system\mcp-servers\godot-mcp\server
npm install && npm run build
```

---

## Unity MCP Installation

### Overview

MCP Unity enables AI assistants (Claude, Cursor, Windsurf) to control Unity Editor through natural language. It provides tools for scene manipulation, asset management, and project automation.

**Features**:
- Execute Unity menu items
- Create/modify GameObjects and components
- Run Unity Test Runner
- Install packages via Package Manager
- Access scene hierarchy and asset database

### Prerequisites

| Requirement | Version | Notes |
|-------------|---------|-------|
| Unity Hub | Latest | [Download](https://unity.com/download) |
| Unity Editor | 2022.3 LTS+ | Recommended: 2022.3.x LTS |
| Node.js | 18+ | [Download](https://nodejs.org/) |
| npm | 9+ | Included with Node.js |

### Step 1: Install Unity Hub (Already Installed)

Unity Hub should already be installed. Verify:

```powershell
# Check Unity Hub location
Test-Path "C:\Program Files\Unity Hub\Unity Hub.exe"
```

If not installed:
```powershell
winget install Unity.UnityHub
```

### Step 2: Install Unity Editor

1. Open **Unity Hub**
2. Go to **Installs** tab
3. Click **Install Editor**
4. Select **Unity 2022.3 LTS** (or newer)
5. Choose modules:
   - **Windows Build Support (IL2CPP)** - Required
   - **WebGL Build Support** - Recommended for web games
   - **Documentation** - Recommended
6. Click **Install**

**Disk Space**: 8-15 GB depending on modules
**Time**: 20-40 minutes (download dependent)

### Step 3: Install MCP Unity Package

**Option A: Via Unity Package Manager (Recommended)**

1. Open Unity Editor with a project
2. Navigate to **Window > Package Manager**
3. Click the **+** button in top-left
4. Select **Add package from git URL...**
5. Enter: `https://github.com/CoderGamester/mcp-unity.git`
6. Click **Add**

**Option B: Manual Installation**

```powershell
# Clone to local directory
git clone https://github.com/CoderGamester/mcp-unity.git C:\ai-game-dev-system\mcp-servers\mcp-unity

# Or use existing installation
# The package is already cloned at: C:\ai-game-dev-system\mcp-servers\mcp-unity
```

Then in Unity:
1. Window > Package Manager > + > Add package from disk
2. Navigate to `C:\ai-game-dev-system\mcp-servers\mcp-unity\package.json`

### Step 4: Configure MCP Server

**Option A: Via Unity Editor (Recommended)**

1. Open Unity Editor
2. Navigate to **Tools > MCP Unity > Server Window**
3. Click **Configure** button for your AI client
4. Confirm the configuration popup

**Option B: Manual Configuration**

Add to your MCP config (already configured in `C:\Ziggie\.mcp.json`):

```json
{
  "mcp-unity": {
    "command": "cmd",
    "args": [
      "/c", "cd", "/d", "C:\\ai-game-dev-system\\mcp-servers\\mcp-unity\\Server~",
      "&&", "npx", "-y", "mcp-unity@1.2.0"
    ],
    "env": {
      "MCP_TRANSPORT": "stdio"
    },
    "disabled": true,
    "_comment": "Enable when Unity Editor is installed"
  }
}
```

### Step 5: Start MCP Server

1. Open Unity Editor
2. Navigate to **Tools > MCP Unity > Server Window**
3. Click **Start Server**
4. Default WebSocket port: **8090**

### Step 6: Test Connection

```powershell
# Test WebSocket connection
npx wscat -c ws://localhost:8090/McpUnity
```

Expected: Connection established (Ctrl+C to exit)

### Unity MCP Verification Checklist

```text
[ ] Unity Hub installed
[ ] Unity Editor 2022.3+ installed
[ ] Node.js 18+ installed (node --version)
[ ] MCP Unity package added to project
[ ] Server Window accessible (Tools > MCP Unity > Server Window)
[ ] WebSocket server running on port 8090
[ ] MCP config enabled in .mcp.json
```

---

## Unreal Engine MCP Installation

### Overview

Unreal MCP enables AI assistants to control Unreal Engine 5.5+ through natural language. It provides comprehensive tools for actor management, Blueprint development, and editor control.

**Features**:
- Create/delete actors (cubes, spheres, lights, cameras)
- Blueprint class creation and component configuration
- Blueprint node graph manipulation
- Viewport camera control
- Input mapping creation

### Prerequisites

| Requirement | Version | Notes |
|-------------|---------|-------|
| Epic Games Launcher | Latest | [Download](https://store.epicgames.com/download) |
| Unreal Engine | 5.5+ | Required for MCP plugin |
| Visual Studio 2022 | Latest | With C++ workload |
| Python | 3.12+ | [Download](https://python.org/) |
| uv | Latest | Python package manager |

### Step 1: Install Epic Games Launcher

```powershell
# Download and install Epic Games Launcher
winget install EpicGames.EpicGamesLauncher
```

Or download from: https://store.epicgames.com/download

### Step 2: Install Visual Studio 2022 with C++ Workload

Visual Studio is required to build the Unreal plugin.

```powershell
# Install Visual Studio 2022 Community with required workloads
winget install Microsoft.VisualStudio.2022.Community --override "--add Microsoft.VisualStudio.Workload.NativeDesktop --add Microsoft.VisualStudio.Workload.NativeGame --add Microsoft.VisualStudio.Component.VC.Tools.x86.x64 --includeRecommended"
```

**Required Workloads**:
- Desktop development with C++
- Game development with C++

**Disk Space**: 15-25 GB for Visual Studio

### Step 3: Install Unreal Engine 5.5+

1. Open **Epic Games Launcher**
2. Go to **Unreal Engine** tab
3. Click **Library**
4. Click **+** to add engine version
5. Select **Unreal Engine 5.5** (or newer)
6. Click **Install**

**Disk Space**: 50-100 GB
**Time**: 2-4 hours (download dependent)

### Step 4: Install Python and uv

```powershell
# Install Python 3.12+
winget install Python.Python.3.12

# Install uv (Python package manager)
pip install uv
```

### Step 5: Install UnrealMCP Plugin

**Option A: Use Sample Project (Fastest)**

The sample project is already configured at:
`C:\ai-game-dev-system\mcp-servers\unreal-mcp\MCPGameProject`

1. Right-click `MCPGameProject.uproject`
2. Select **Generate Visual Studio project files**
3. Open the `.sln` file in Visual Studio
4. Set build configuration to **Development Editor**
5. Build the solution

**Option B: Add Plugin to Existing Project**

1. Copy plugin to your project:
```powershell
Copy-Item -Recurse "C:\ai-game-dev-system\mcp-servers\unreal-mcp\MCPGameProject\Plugins\UnrealMCP" "C:\YourProject\Plugins\"
```

2. Regenerate project files:
   - Right-click `.uproject` file
   - Select **Generate Visual Studio project files**

3. Build the project in Visual Studio

4. Enable plugin in Unreal:
   - Edit > Plugins
   - Find "UnrealMCP" in Editor category
   - Enable and restart editor

### Step 6: Setup Python MCP Server

```powershell
# Navigate to Python server directory
cd C:\ai-game-dev-system\mcp-servers\unreal-mcp\Python

# Create virtual environment and install dependencies
uv venv
.venv\Scripts\activate
uv pip install -r requirements.txt

# Or use uv run (no activation needed)
uv run python unreal_mcp_server.py
```

### Step 7: Configure MCP for Ziggie

Already configured in `C:\Ziggie\.mcp.json`:

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

### Step 8: Start and Test

1. **Start Unreal Editor** with the plugin enabled
2. The TCP server starts automatically on port **55557**
3. **Start MCP Server**:
```powershell
cd C:\ai-game-dev-system\mcp-servers\unreal-mcp\Python
uv run python unreal_mcp_server.py
```

### Unreal MCP Verification Checklist

```text
[ ] Epic Games Launcher installed
[ ] Unreal Engine 5.5+ installed
[ ] Visual Studio 2022 with C++ workload installed
[ ] Python 3.12+ installed (python --version)
[ ] uv installed (uv --version)
[ ] UnrealMCP plugin built and enabled
[ ] TCP server running on port 55557
[ ] Python MCP server can connect
[ ] MCP config enabled in .mcp.json
```

---

## Godot MCP Installation

### Overview

Godot MCP provides comprehensive integration between Godot Engine and AI assistants. Since Godot is already installed, this is the fastest setup.

**Features**:
- Full project access (scripts, scenes, nodes, resources)
- Scene tree manipulation
- GDScript editing and creation
- Project settings access
- Editor state control

### Prerequisites

| Requirement | Version | Status |
|-------------|---------|--------|
| Godot Engine | 4.x | Already installed |
| Node.js | 18+ | Already installed |
| npm | 9+ | Already installed |

### Step 1: Verify Godot Installation

```powershell
# Check Godot location
Test-Path "C:\Program Files\Godot\Godot_v4*"
# Or common user installation
Test-Path "$env:USERPROFILE\Godot\Godot_v4*"
```

### Step 2: Build MCP Server

The Godot MCP server is already cloned at:
`C:\ai-game-dev-system\mcp-servers\godot-mcp`

```powershell
# Navigate to server directory
cd C:\ai-game-dev-system\mcp-servers\godot-mcp\server

# Install dependencies
npm install

# Build TypeScript
npm run build
```

### Step 3: Install Godot Addon

**Option A: Use Example Project**

The example project includes the addon pre-configured:
1. Open Godot
2. Import project from `C:\ai-game-dev-system\mcp-servers\godot-mcp\project.godot`

**Option B: Add to Existing Project**

```powershell
# Copy addon to your project
Copy-Item -Recurse "C:\ai-game-dev-system\mcp-servers\godot-mcp\addons\godot_mcp" "C:\YourGodotProject\addons\"
```

Then in Godot:
1. Open your project
2. Go to **Project > Project Settings > Plugins**
3. Enable **Godot MCP** plugin

### Step 4: Configure MCP for Ziggie

Already configured in `C:\Ziggie\.mcp.json`:

```json
{
  "godot-mcp": {
    "command": "cmd",
    "args": [
      "/c", "cd", "/d", "C:\\ai-game-dev-system\\mcp-servers\\godot-mcp\\server",
      "&&", "node", "dist/index.js"
    ],
    "env": {
      "MCP_TRANSPORT": "stdio",
      "GODOT_MCP_PORT": "6005"
    },
    "disabled": true,
    "_comment": "Enable when Godot Engine is installed with MCP addon"
  }
}
```

### Step 5: Start Server and Connect

1. **Open Godot project** with MCP addon enabled
2. In the editor dock, find **Godot MCP Server** panel
3. Set port (default: **9080**) and click **Start Server**
4. **Enable MCP** in `.mcp.json` by removing `"disabled": true`

### Step 6: Test Connection

```powershell
# Test the server
cd C:\ai-game-dev-system\mcp-servers\godot-mcp\server
node simple_client.js
```

### Godot MCP Verification Checklist

```text
[ ] Godot 4.x installed
[ ] Node.js 18+ installed (node --version)
[ ] MCP server built (npm run build)
[ ] Godot addon copied to project
[ ] Plugin enabled in Project Settings
[ ] WebSocket server running in Godot
[ ] MCP config enabled in .mcp.json
```

---

## MCP Configuration for Ziggie

### Current Configuration

The `.mcp.json` file at `C:\Ziggie\.mcp.json` already includes configurations for all three engines. They are disabled by default with `"disabled": true`.

### Enabling Game Engine MCPs

To enable a game engine MCP:

1. Open `C:\Ziggie\.mcp.json`
2. Find the engine configuration (e.g., `mcp-unity`)
3. Remove the `"disabled": true` line
4. Save the file
5. Restart Claude Code or your MCP client

### Full Configuration Reference

```json
{
  "mcpServers": {
    "mcp-unity": {
      "command": "cmd",
      "args": [
        "/c", "cd", "/d", "C:\\ai-game-dev-system\\mcp-servers\\mcp-unity\\Server~",
        "&&", "npx", "-y", "mcp-unity@1.2.0"
      ],
      "env": {
        "MCP_TRANSPORT": "stdio"
      }
    },
    "unreal-mcp": {
      "command": "cmd",
      "args": [
        "/c", "cd", "/d", "C:\\ai-game-dev-system\\mcp-servers\\unreal-mcp\\Python",
        "&&", "uv", "run", "python", "unreal_mcp_server.py"
      ],
      "env": {
        "UNREAL_HOST": "127.0.0.1",
        "UNREAL_PORT": "8081"
      }
    },
    "godot-mcp": {
      "command": "cmd",
      "args": [
        "/c", "cd", "/d", "C:\\ai-game-dev-system\\mcp-servers\\godot-mcp\\server",
        "&&", "node", "dist/index.js"
      ],
      "env": {
        "MCP_TRANSPORT": "stdio",
        "GODOT_MCP_PORT": "6005"
      }
    }
  }
}
```

---

## Troubleshooting

### Common Issues

#### Unity MCP

| Issue | Cause | Solution |
|-------|-------|----------|
| Connection failed | WebSocket not running | Tools > MCP Unity > Server Window > Start Server |
| Path with spaces fails | MCP limitation | Move project to path without spaces |
| Port conflict | Another app using 8090 | Change port in Server Window |
| Node.js not found | Not in PATH | Reinstall Node.js or add to PATH |

**Debug Commands**:
```powershell
# Test WebSocket
npx wscat -c ws://localhost:8090/McpUnity

# Check Node.js
node --version

# Enable logging
$env:LOGGING = "true"
$env:LOGGING_FILE = "true"
```

#### Unreal MCP

| Issue | Cause | Solution |
|-------|-------|----------|
| Plugin not loading | Build failed | Rebuild in Visual Studio |
| TCP connection refused | Editor not running | Start Unreal Editor first |
| Python import errors | Missing dependencies | `uv pip install -r requirements.txt` |
| Visual Studio errors | Missing workloads | Install C++ game development workload |

**Debug Commands**:
```powershell
# Test TCP connection
Test-NetConnection -ComputerName localhost -Port 55557

# Check Python
python --version
uv --version

# Rebuild plugin
cd C:\ai-game-dev-system\mcp-servers\unreal-mcp\MCPGameProject
# Right-click .uproject > Generate Visual Studio project files
```

#### Godot MCP

| Issue | Cause | Solution |
|-------|-------|----------|
| Addon not visible | Not in correct folder | Ensure `addons/godot_mcp/` structure |
| Server build failed | npm issues | Delete node_modules, run `npm install` |
| Connection timeout | Port mismatch | Verify port in Godot panel and config |
| Script errors | Godot version | Ensure Godot 4.x (not 3.x) |

**Debug Commands**:
```powershell
# Rebuild server
cd C:\ai-game-dev-system\mcp-servers\godot-mcp\server
Remove-Item -Recurse node_modules
npm install
npm run build

# Test connection
node simple_client.js
```

### WSL2 Networking (Windows 11)

If running MCP server in WSL2 while engine runs on Windows:

**Solution 1: Enable Mirrored Mode**
```ini
# ~/.wslconfig
[wsl2]
networkingMode=mirrored
```
Then: `wsl --shutdown` and reopen WSL.

**Solution 2: Use Windows Host IP**
```bash
export UNITY_HOST=$(grep -m1 nameserver /etc/resolv.conf | awk '{print $2}')
```

---

## Sources and References

### Unity MCP
- [mcp-unity by CoderGamester](https://github.com/CoderGamester/mcp-unity) - Recommended implementation
- [Unity-MCP by IvanMurzak](https://github.com/IvanMurzak/Unity-MCP) - Runtime AI integration
- [unity-mcp by CoplayDev](https://github.com/CoplayDev/unity-mcp) - Alternative implementation
- [Unity MCP Server Guide - Apidog](https://apidog.com/blog/unity-mcp-server/)

### Unreal MCP
- [unreal-mcp by chongdashu](https://github.com/chongdashu/unreal-mcp) - Primary implementation
- [Unreal_mcp by ChiR24](https://github.com/ChiR24/Unreal_mcp) - TypeScript/C++/Rust implementation
- [UnrealMCP by kvick-games](https://github.com/kvick-games/UnrealMCP) - Alternative plugin
- [Unreal Engine MCP Server Guide - Apidog](https://apidog.com/blog/unreal-engine-mcp-server/)

### Godot MCP
- [godot-mcp by Coding-Solo](https://github.com/Coding-Solo/godot-mcp) - Debug/launch focused
- [Godot-MCP by ee0pdt](https://github.com/ee0pdt/Godot-MCP) - Comprehensive integration
- [GDAI MCP Server](https://gdaimcp.com/docs/installation) - All-in-one solution
- [Godot MCP 2.0 - Next Generation](https://lobehub.com/mcp/pedrogabriel-better-godot-mcp) - Latest version

### General MCP
- [Model Context Protocol Specification](https://modelcontextprotocol.io/specification/2025-11-25)
- [MCP Servers Repository](https://github.com/modelcontextprotocol/servers)

---

## Summary

| Engine | Current Status | Next Steps |
|--------|----------------|------------|
| **Unity** | Server cloned, needs Unity Editor | Install Unity 2022.3 LTS via Unity Hub |
| **Unreal** | Server cloned, needs Unreal Editor | Install Unreal 5.5+ via Epic Games Launcher |
| **Godot** | Ready (Godot installed) | Build server, enable addon, enable in .mcp.json |

### Estimated Total Installation Time

| Component | Time |
|-----------|------|
| Unity Hub + Editor | 30-60 min |
| Epic Games + Unreal | 2-4 hours |
| Visual Studio 2022 | 30-60 min |
| Godot MCP (already installed) | 15 min |
| **Total (all three)** | **4-6 hours** |

---

*Document created for Ziggie AI Game Development Ecosystem*
*Path: C:\Ziggie\docs\GAME-ENGINE-MCP-INSTALLATION-GUIDE.md*
