# MCP Filesystem Server - Configuration Reload Fix

> **Issue**: MCP Filesystem server not picking up new paths from .mcp.json
> **Root Cause**: MCP servers cache configuration at startup
> **Status**: Documented with workarounds

---

## Problem Description

After modifying `.mcp.json` to expand filesystem MCP paths:
```json
"filesystem": {
  "command": "cmd",
  "args": [
    "/c", "npx", "-y", "@modelcontextprotocol/server-filesystem",
    "C:/Ziggie",
    "C:/ai-game-dev-system",
    "C:/meowping-rts",
    "C:/team-ziggie"
  ]
}
```

The MCP Filesystem server continues to only allow access to `C:/Ziggie`, showing:
```
Access denied - path outside allowed directories: C:\ai-game-dev-system not in C:\Ziggie
```

## Root Cause Analysis

Based on web research and diagnosis:

1. **MCP servers are launched at Claude Code/VSCode startup**
2. **Configuration is cached in the running node.exe process**
3. **No hot-reload mechanism exists by default**
4. **Project `.mcp.json` is the correct config location** (verified: no overrides in `~/.claude/settings.local.json`)

## Solutions

### Solution 1: Full VSCode Restart (Recommended)
```powershell
# 1. Save all work
# 2. Close VSCode completely (not just Claude Code panel)
# 3. Ensure VSCode is not running in system tray
# 4. Reopen VSCode
# 5. Open Claude Code extension
```

### Solution 2: Developer Reload Window
```
1. Press Ctrl+Shift+P (Command Palette)
2. Type: "Developer: Reload Window"
3. Press Enter
4. Wait for VSCode to reload
5. Reopen Claude Code panel
```

### Solution 3: Kill MCP Server Processes
```powershell
# Kill all node.exe processes (will kill MCP servers)
taskkill /F /IM node.exe

# Then reload VSCode window or restart VSCode
```

### Solution 5: Use Node Directly (Recommended for Windows)
If npx-based paths aren't working, use node directly with the globally installed package:

1. Install globally first:
```powershell
npm install -g @modelcontextprotocol/server-filesystem
```

2. Update `.mcp.json` to use node:
```json
"filesystem": {
  "command": "node",
  "args": [
    "C:\\Users\\minin\\AppData\\Roaming\\npm\\node_modules\\@modelcontextprotocol\\server-filesystem\\dist\\index.js",
    "C:\\Ziggie",
    "C:\\ai-game-dev-system",
    "C:\\meowping-rts",
    "C:\\team-ziggie"
  ]
}
```

3. Reload VSCode (Ctrl+Shift+P → "Developer: Reload Window")

### Solution 6: Use cmd /c node with Forward Slashes (Latest Attempt)
Matches the pattern used by other working MCP servers:

```json
"filesystem": {
  "command": "cmd",
  "args": [
    "/c", "node",
    "C:/Users/minin/AppData/Roaming/npm/node_modules/@modelcontextprotocol/server-filesystem/dist/index.js",
    "C:/Ziggie",
    "C:/ai-game-dev-system",
    "C:/meowping-rts",
    "C:/team-ziggie"
  ]
}
```

Key differences from Solution 5:
- Wraps node in `cmd /c` for Windows compatibility
- Uses forward slashes (/) instead of backslashes

Reload VSCode after applying (Ctrl+Shift+P → "Developer: Reload Window")

### Solution 7: User-Level Settings (RECOMMENDED)

**Root Cause Discovered**: The Roots protocol causes Claude Code to send only the current workspace as an allowed directory, overriding command-line arguments. See [Filesystem MCP documentation](https://mcpservers.org/servers/modelcontextprotocol/filesystem).

**Fix**: Create a user-level MCP settings file that Claude Code reads BEFORE the project `.mcp.json`:

1. Create `~/.claude/settings.json` (on Windows: `C:\Users\<username>\.claude\settings.json`):
```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "C:/Ziggie",
        "C:/ai-game-dev-system",
        "C:/meowping-rts",
        "C:/team-ziggie"
      ]
    }
  }
}
```

2. Reload VSCode (Ctrl+Shift+P → "Developer: Reload Window")

**Why this works**: User-level settings are shared between CLI and VSCode extension per [Claude Code docs](https://code.claude.com/docs/en/vs-code).

### Solution 4: Use Native Claude Code Tools (Workaround)
Native Claude Code tools have broader access than MCP Filesystem:
- `Read` - Can read any file on the system
- `Write` - Can write to any file
- `Glob` - Can search any directory
- `Grep` - Can search content anywhere
- `Bash` - Can run any command

**This workaround is effective for Stage 1 completion.**

## Verification

After applying a solution, verify with:
```powershell
# From Claude Code, try to read a file outside C:/Ziggie
mcp__filesystem__read_file path="C:/ai-game-dev-system/README.md"
```

If successful, you should see file contents instead of "Access denied".

## Future Improvement: MCP Hot Reload

Consider adding the `mcp-hot-reload` tool for development:
- [mcp-hot-reload on LobeHub](https://lobehub.com/mcp/claude-code-mcp-reload-mcp-hot-reload)
- Allows restarting individual MCP servers without full application restart

## References

- [Claude Code MCP Setup](https://code.claude.com/docs/en/vs-code)
- [MCP Server Restart Tool](https://github.com/non-dirty/mcp-server-restart)
- [VS Code MCP Developer Guide](https://code.visualstudio.com/api/extension-guides/ai/mcp)
- [Model Context Protocol Servers](https://github.com/modelcontextprotocol/servers)

---

**Created**: 2024-12-24
**Status**: Issue documented, workarounds available
