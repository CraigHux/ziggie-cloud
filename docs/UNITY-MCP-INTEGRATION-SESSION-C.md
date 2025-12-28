# Unity MCP Integration Guide - Session C

> **Source**: L1 Strategic Agent - Unity MCP Integration
> **Session**: C (2025-12-28)
> **Status**: Configuration Ready, Pending Unity Installation
> **Last Updated**: 2025-12-28

---

## Executive Summary

This document provides comprehensive guidance for integrating Unity MCP (Model Context Protocol) servers with the Ziggie AI ecosystem. The integration enables Claude AI to directly interact with Unity Editor for game development automation, asset management, and scene manipulation.

### Current Configuration Status

| Component | Status | Notes |
|-----------|--------|-------|
| unity-mcp (custom) | Configured, Disabled | Path: `C:\ai-game-dev-system\mcp-servers\unity-mcp\server` |
| mcp-unity (CoderGamester) | Configured, Disabled | Recommended implementation |
| Unity Hub | **NOT INSTALLED** | Required pre-requisite |
| Unity Editor | **NOT INSTALLED** | Required pre-requisite |
| Hub MCP Reference | Active | `UNITY_MCP_URL: http://localhost:8080` |

---

## Table of Contents

1. [Pre-requisites](#1-pre-requisites)
2. [Unity Hub Installation](#2-unity-hub-installation)
3. [Unity Editor Installation](#3-unity-editor-installation)
4. [MCP Server Options](#4-mcp-server-options)
5. [Option A: mcp-unity (Recommended)](#5-option-a-mcp-unity-recommended)
6. [Option B: unity-mcp (Custom)](#6-option-b-unity-mcp-custom)
7. [Claude Code Configuration](#7-claude-code-configuration)
8. [Testing Procedures](#8-testing-procedures)
9. [Troubleshooting](#9-troubleshooting)
10. [Integration with Ziggie Ecosystem](#10-integration-with-ziggie-ecosystem)

---

## 1. Pre-requisites

### System Requirements

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| Windows | 10 (64-bit) | 11 (64-bit) |
| RAM | 8 GB | 16 GB+ |
| Storage | 20 GB free | 50 GB+ SSD |
| Node.js | v18+ | v20 LTS |
| npm | v9+ | v10+ |

### Required Software

```text
1. Unity Hub (latest)
2. Unity Editor 2022.3 LTS or newer
3. Node.js v18+ (for MCP server)
4. Visual Studio 2022 (or VS Code with C# extension)
5. Git (for package installation)
```

### Verification Commands

```powershell
# Check Node.js version
node --version
# Expected: v18.x.x or higher

# Check npm version
npm --version
# Expected: v9.x.x or higher

# Check if Unity Hub is installed
Test-Path "C:\Program Files\Unity Hub\Unity Hub.exe"

# Check for Unity installations
Get-ChildItem "C:\Program Files\Unity\Hub\Editor" -ErrorAction SilentlyContinue
```

---

## 2. Unity Hub Installation

### Step 1: Download Unity Hub

```powershell
# Option A: Using winget (recommended)
winget install -e --id Unity.UnityHub --accept-source-agreements --accept-package-agreements

# Option B: Direct download
# Visit: https://unity.com/download
# Download: Unity Hub for Windows
```

### Step 2: Verify Installation

```powershell
# Check installation path
$hubPath = "C:\Program Files\Unity Hub\Unity Hub.exe"
if (Test-Path $hubPath) {
    Write-Host "Unity Hub installed successfully" -ForegroundColor Green
} else {
    Write-Host "Unity Hub NOT found" -ForegroundColor Red
}
```

### Step 3: First-time Setup

1. Launch Unity Hub
2. Sign in with Unity account (or create one)
3. Accept license agreement
4. Configure preferences (optional)

---

## 3. Unity Editor Installation

### Recommended Versions

| Version | Support Level | Use Case |
|---------|---------------|----------|
| 2022.3 LTS | Long-term support | Production projects |
| 2023.2 | Tech stream | Latest features |
| 6000.0 (Unity 6) | Future LTS | New projects (2024+) |

### Installation via Unity Hub

```powershell
# Launch Unity Hub (if not running)
Start-Process "C:\Program Files\Unity Hub\Unity Hub.exe"
```

**GUI Steps:**
1. Click **Installs** in left sidebar
2. Click **Install Editor** button
3. Select **Unity 2022.3 LTS** (recommended)
4. Add modules:
   - **Windows Build Support (IL2CPP)**
   - **WebGL Build Support** (for web games)
   - **Visual Studio 2022** (if not installed)
5. Click **Install**

### Required Unity Packages for MCP

After installation, these packages are needed in your Unity project:

```json
// Packages/manifest.json additions
{
  "dependencies": {
    "com.unity.editorcoroutines": "1.0.0",
    "com.unity.nuget.newtonsoft-json": "3.2.1"
  }
}
```

---

## 4. MCP Server Options

The Ziggie ecosystem has two Unity MCP server configurations:

### Option A: mcp-unity (CoderGamester) - RECOMMENDED

| Aspect | Details |
|--------|---------|
| Repository | https://github.com/CoderGamester/mcp-unity |
| Version | 1.2.0 |
| Transport | stdio |
| Maturity | Production-ready |
| Features | Scene, assets, scripts, build automation |

### Option B: unity-mcp (Custom)

| Aspect | Details |
|--------|---------|
| Location | `C:\ai-game-dev-system\mcp-servers\unity-mcp` |
| Transport | stdio / HTTP (port 8080) |
| Maturity | Development |
| Features | Custom extensions for Ziggie |

---

## 5. Option A: mcp-unity (Recommended)

### Installation Steps

#### Step 1: Install Unity Package

Open Unity Package Manager (Window > Package Manager):

1. Click **+** button
2. Select **Add package from git URL**
3. Enter: `https://github.com/CoderGamester/mcp-unity.git`
4. Click **Add**

**Alternative (manifest.json):**
```json
{
  "dependencies": {
    "com.codergamester.mcp-unity": "https://github.com/CoderGamester/mcp-unity.git"
  }
}
```

#### Step 2: Configure Unity Project

After package installation:

1. Open **Edit > Project Settings > MCP Unity**
2. Enable **Auto-start Server**
3. Set **Port**: 8080 (matches Ziggie config)
4. Set **Transport**: stdio

#### Step 3: Enable in .mcp.json

Current configuration in `C:\Ziggie\.mcp.json`:

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
    "_comment": "CoderGamester's MCP Unity (recommended) - Enable when Unity Editor is installed"
  }
}
```

**To Enable:**
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
    "disabled": false
  }
}
```

#### Step 4: Start Unity and Test

1. Open Unity with your project
2. Wait for MCP server to auto-start
3. Check console for: "MCP Unity Server started on port 8080"

---

## 6. Option B: unity-mcp (Custom)

### Directory Structure

```text
C:\ai-game-dev-system\mcp-servers\unity-mcp\
├── server/
│   ├── dist/
│   │   └── index.js          # Compiled server
│   ├── src/
│   │   └── index.ts          # TypeScript source
│   ├── package.json
│   └── tsconfig.json
├── unity-package/
│   ├── Editor/
│   │   └── MCPBridge.cs      # Unity Editor script
│   └── package.json
└── README.md
```

### Installation Steps

#### Step 1: Build the Server

```powershell
cd C:\ai-game-dev-system\mcp-servers\unity-mcp\server

# Install dependencies
npm install

# Build TypeScript
npm run build
```

#### Step 2: Install Unity Package

Copy the unity-package folder to your Unity project:

```powershell
$source = "C:\ai-game-dev-system\mcp-servers\unity-mcp\unity-package"
$dest = "C:\YourUnityProject\Packages\com.ziggie.mcp-bridge"
Copy-Item -Path $source -Destination $dest -Recurse
```

#### Step 3: Enable in .mcp.json

```json
{
  "unity-mcp": {
    "command": "cmd",
    "args": [
      "/c", "cd", "/d", "C:\\ai-game-dev-system\\mcp-servers\\unity-mcp\\server",
      "&&", "node", "dist/index.js"
    ],
    "env": {
      "MCP_TRANSPORT": "stdio",
      "UNITY_MCP_PORT": "8080"
    },
    "disabled": false
  }
}
```

---

## 7. Claude Code Configuration

### Current Ziggie .mcp.json Integration

The hub MCP server already references Unity MCP:

```json
{
  "hub": {
    "env": {
      "UNITY_MCP_URL": "http://localhost:8080",
      ...
    }
  }
}
```

### Available MCP Tools (Expected)

When properly configured, Claude Code gains access to these Unity tools:

| Tool | Description |
|------|-------------|
| `unity_get_scene` | Get current scene hierarchy |
| `unity_create_object` | Create GameObjects |
| `unity_modify_object` | Modify transform, components |
| `unity_get_assets` | List project assets |
| `unity_import_asset` | Import external assets |
| `unity_run_script` | Execute C# scripts |
| `unity_build` | Trigger build process |
| `unity_play_mode` | Enter/exit play mode |

### Testing Claude Code Connection

After enabling the MCP server:

```text
# In Claude Code, try:
"List all GameObjects in the current Unity scene"
"Create a new empty GameObject named 'TestObject'"
"Get the project asset folder structure"
```

---

## 8. Testing Procedures

### Pre-flight Checklist

```text
[ ] Unity Hub installed
[ ] Unity Editor 2022.3+ installed
[ ] Unity project created/opened
[ ] MCP Unity package installed in project
[ ] Node.js v18+ available
[ ] .mcp.json updated (disabled: false)
[ ] Claude Code restarted
```

### Test 1: Server Connectivity

```powershell
# Check if server process starts
cd C:\ai-game-dev-system\mcp-servers\mcp-unity\Server~
npx -y mcp-unity@1.2.0

# Expected output: Server listening on stdio
# Press Ctrl+C to stop
```

### Test 2: Unity Console Check

In Unity Editor console, look for:
```
[MCP Unity] Server started successfully
[MCP Unity] Listening on port 8080
[MCP Unity] Transport: stdio
```

### Test 3: Claude Code Integration

1. Restart Claude Code (to reload MCP config)
2. Open a new conversation
3. Ask: "Can you access Unity? List available Unity tools."
4. Expected: Claude lists unity_* tools

### Test 4: Basic Operations

```text
# Test scene access
"Get the current Unity scene hierarchy"

# Test object creation
"Create a Cube at position (0, 1, 0)"

# Test asset listing
"List all prefabs in the Assets folder"
```

---

## 9. Troubleshooting

### Issue 1: Unity Hub Not Found

**Symptom:**
```
Unity Hub not found in Program Files
```

**Solution:**
```powershell
# Install via winget
winget install -e --id Unity.UnityHub

# Or download from: https://unity.com/download
```

### Issue 2: MCP Server Won't Start

**Symptom:**
```
Error: Cannot find module 'mcp-unity'
```

**Solution:**
```powershell
# Clear npm cache
npm cache clean --force

# Reinstall globally
npm install -g mcp-unity@1.2.0
```

### Issue 3: Unity Editor Not Responding to MCP

**Symptom:**
- Server starts but Claude can't interact with Unity

**Solutions:**

1. **Check Unity is running in Editor mode** (not Play mode)
2. **Verify package installation:**
   ```
   Window > Package Manager > Search "mcp"
   ```
3. **Check Unity console for errors**
4. **Restart Unity Editor**

### Issue 4: Port 8080 Already in Use

**Symptom:**
```
Error: listen EADDRINUSE: address already in use :::8080
```

**Solution:**
```powershell
# Find process using port 8080
netstat -ano | findstr :8080

# Kill the process (replace PID)
taskkill /PID <PID> /F

# Or change port in .mcp.json
"UNITY_MCP_PORT": "8081"
```

### Issue 5: Node.js Version Mismatch

**Symptom:**
```
SyntaxError: Unexpected token '??='
```

**Solution:**
```powershell
# Install Node.js v18+
winget install -e --id OpenJS.NodeJS.LTS

# Verify version
node --version  # Should be v18+
```

### Issue 6: Claude Code Doesn't See Unity Tools

**Symptom:**
- Claude says no Unity tools available

**Solutions:**

1. **Verify .mcp.json has `disabled: false`**
2. **Restart Claude Code completely**
3. **Check MCP server is in PATH**
4. **Run manually to check for errors:**
   ```powershell
   cd C:\ai-game-dev-system\mcp-servers\mcp-unity\Server~
   npx -y mcp-unity@1.2.0
   ```

---

## 10. Integration with Ziggie Ecosystem

### Hub MCP Integration

The Ziggie Hub MCP (`C:\ai-game-dev-system\mcp-servers\hub`) is configured to route Unity requests:

```python
# hub/mcp_hub_server.py
BACKENDS = {
    "unity": os.getenv("UNITY_MCP_URL", "http://localhost:8080"),
    ...
}
```

### Asset Pipeline Integration

Unity MCP enables automated asset import from ComfyUI:

```text
ComfyUI generates sprite → S3 upload → Unity MCP imports → In-game asset
```

### Recommended Workflow

1. **Asset Generation** (ComfyUI MCP)
   - Generate 2D sprites, textures
   - Output to `C:\ai-game-dev-system\assets\ai-generated`

2. **Asset Import** (Unity MCP)
   - Import assets into Unity project
   - Configure import settings (sprite, texture)

3. **Scene Assembly** (Unity MCP)
   - Create GameObjects with imported assets
   - Configure prefabs

4. **Build & Test** (Unity MCP)
   - Trigger builds
   - Run automated tests

---

## Quick Reference

### Enable Unity MCP

Edit `C:\Ziggie\.mcp.json`:
```json
"mcp-unity": {
  ...
  "disabled": false
}
```

### Installation Commands

```powershell
# Install Unity Hub
winget install -e --id Unity.UnityHub

# Install via Unity Hub GUI:
# 1. Launch Unity Hub
# 2. Installs > Install Editor > 2022.3 LTS
# 3. Add Windows Build Support + WebGL

# Install mcp-unity package in Unity project:
# Package Manager > Add from git URL:
# https://github.com/CoderGamester/mcp-unity.git
```

### Verification

```powershell
# Check Unity Hub
Test-Path "C:\Program Files\Unity Hub\Unity Hub.exe"

# Check Unity Editor
Get-ChildItem "C:\Program Files\Unity\Hub\Editor"

# Test MCP server
npx -y mcp-unity@1.2.0
```

---

## Next Steps

1. [ ] Install Unity Hub using winget
2. [ ] Install Unity Editor 2022.3 LTS
3. [ ] Create new Unity project for MeowPing RTS
4. [ ] Install mcp-unity package
5. [ ] Enable mcp-unity in .mcp.json
6. [ ] Test Claude Code integration
7. [ ] Configure asset import pipeline
8. [ ] Document project-specific setup

---

## References

- Unity Hub Download: https://unity.com/download
- mcp-unity Repository: https://github.com/CoderGamester/mcp-unity
- Unity Editor Manual: https://docs.unity3d.com/Manual/
- MCP Specification: https://modelcontextprotocol.io/
- Ziggie Ecosystem: C:\Ziggie\ZIGGIE-ECOSYSTEM-MASTER-STATUS-V5.md

---

*Document created by L1 Strategic Agent - Session C*
*Ziggie AI Ecosystem - Unity MCP Integration*
