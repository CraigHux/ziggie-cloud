# Cursor IDE Guide for Ziggie Development

> **Last Updated**: 2025-12-28
> **Scope**: Setting up Cursor IDE for Ziggie AI ecosystem development

---

## Overview

Cursor is an AI-powered IDE built on VS Code that integrates seamlessly with Claude and other AI models. This guide covers installation, configuration, and optimal usage with the Ziggie workspace.

---

## Installation

### Windows

1. Download Cursor from https://cursor.com
2. Run the installer
3. Launch Cursor and complete initial setup
4. Sign in or create a Cursor account

### Verify Installation

```bash
# Check Cursor is in PATH
cursor --version
```

---

## Ziggie Workspace Configuration

### Opening Ziggie Workspaces

Open all related workspaces in a single window for best context:

1. **File > Add Folder to Workspace**
2. Add these folders:
   - `C:\Ziggie` - Core orchestration
   - `C:\ai-game-dev-system` - Knowledge base
   - `C:\meowping-rts` - Game frontend/backend
   - `C:\team-ziggie` - Agent configurations

Or from terminal:
```bash
cursor C:\Ziggie C:\ai-game-dev-system C:\meowping-rts C:\team-ziggie
```

### Recommended Extensions

Install these extensions for Ziggie development:

| Extension | Purpose |
|-----------|---------|
| Python | Python development |
| Pylance | Python IntelliSense |
| ES7+ React/Redux/React-Native snippets | Frontend development |
| Docker | Container management |
| YAML | Docker compose editing |
| Markdown All in One | Documentation |
| GitLens | Git history |
| REST Client | API testing |

---

## MCP Server Integration

Ziggie uses Model Context Protocol (MCP) servers for AI integration.

### MCP Configuration Location

The MCP configuration is stored in `C:\Ziggie\.mcp.json`.

### Active MCP Servers

| Server | Purpose | Port |
|--------|---------|------|
| filesystem | File access across workspaces | stdio |
| memory | Knowledge graph storage | stdio |
| chrome-devtools | Browser automation | stdio |
| comfyui | AI image generation | 8188 |
| hub | Multi-backend orchestration | stdio |
| github | Repository automation | stdio |
| postgres | Database operations | 5432 |

### Enabling Disabled Servers

Some servers are disabled by default (game engines). Enable them in `.mcp.json`:

```json
{
  "unity-mcp": {
    "disabled": false,  // Change from true
    ...
  }
}
```

---

## Keyboard Shortcuts

### Essential Cursor Shortcuts

| Action | Windows | Description |
|--------|---------|-------------|
| AI Chat | `Ctrl+L` | Open AI chat panel |
| Inline Edit | `Ctrl+K` | Edit selection with AI |
| Accept Suggestion | `Tab` | Accept AI completion |
| New Chat | `Ctrl+Shift+L` | Start new chat |
| Toggle Sidebar | `Ctrl+B` | Show/hide explorer |
| Command Palette | `Ctrl+Shift+P` | All commands |
| Quick Open | `Ctrl+P` | Open any file |
| Terminal | `Ctrl+`` | Toggle terminal |
| Search Files | `Ctrl+Shift+F` | Search across workspace |

### Git Shortcuts

| Action | Windows | Description |
|--------|---------|-------------|
| Git: Stage All | `Ctrl+Shift+G` then `+` | Stage changes |
| Git: Commit | In Source Control view | Commit staged |
| Git: Push | In Source Control view | Push to remote |

---

## AI Chat Best Practices

### Context Selection

1. **Select Code First**: Highlight relevant code before asking
2. **Use @-mentions**: `@file.py` to reference files
3. **Include Error Messages**: Paste full stack traces

### Effective Prompts

```
Good: "Explain the cache implementation in agents.py and suggest improvements"
Bad: "Fix the bug"

Good: "Refactor this function to use async/await pattern"
Bad: "Make this better"
```

### Ziggie-Specific Commands

When working with Ziggie, reference the agent system:

```
"Following the Ziggie agent hierarchy, create a new L2 agent for..."
"Check the knowledge-base at C:\ai-game-dev-system\knowledge-base for..."
```

---

## Project-Specific Settings

### settings.json

Create workspace settings at `C:\Ziggie\.vscode\settings.json`:

```json
{
  "python.defaultInterpreterPath": "python",
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "files.exclude": {
    "**/__pycache__": true,
    "**/*.pyc": true,
    "**/node_modules": true
  },
  "search.exclude": {
    "**/node_modules": true,
    "**/venv": true,
    "**/.git": true
  },
  "typescript.tsdk": "node_modules/typescript/lib"
}
```

### Python Environment

```bash
# Create virtual environment
python -m venv venv

# Activate
.\venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

---

## Debugging Configuration

### Python Backend (Control Center)

Create `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Control Center Backend",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": ["main:app", "--reload", "--port", "54112"],
      "cwd": "${workspaceFolder}/control-center/backend",
      "env": {
        "DEBUG": "true"
      }
    }
  ]
}
```

### Frontend (Next.js/React)

```json
{
  "name": "Frontend Debug",
  "type": "chrome",
  "request": "launch",
  "url": "http://localhost:3000",
  "webRoot": "${workspaceFolder}/control-center/frontend"
}
```

---

## Terminal Configuration

### PowerShell Profile

For fast terminal startup with conda lazy loading:

```powershell
# Add to $PROFILE
function Initialize-Conda {
    $condaPath = "C:\Users\$env:USERNAME\miniconda3\Scripts\conda.exe"
    if (Test-Path $condaPath) {
        (& $condaPath "shell.powershell" "hook") | Out-String | Where-Object { $_ } | Invoke-Expression
    }
}
function conda { Initialize-Conda; & conda @args }
```

### Multiple Terminals

- Terminal 1: Backend (`cd C:\Ziggie\control-center\backend && python main.py`)
- Terminal 2: Frontend (`cd C:\Ziggie\control-center\frontend && npm run dev`)
- Terminal 3: Git operations

---

## Common Workflows

### 1. Starting Development Session

```bash
# Terminal 1: Start backend
cd C:\Ziggie\control-center\backend
python main.py

# Terminal 2: Start frontend
cd C:\Ziggie\control-center\frontend
npm run dev
```

### 2. Running Tests

```bash
# Backend tests
cd C:\Ziggie\control-center\backend
python -m pytest tests/

# All Python tests
cd C:\Ziggie
python -m pytest test_*.py -v
```

### 3. Git Workflow

```bash
# Check status
git status

# Stage and commit
git add .
git commit -m "feat: description"

# Push
git push origin master
```

---

## Troubleshooting

### MCP Server Not Responding

1. Check if Node.js is installed: `node --version`
2. Check if npx is available: `npx --version`
3. Verify `.mcp.json` syntax is valid JSON
4. Restart Cursor

### Python Import Errors

1. Ensure virtual environment is activated
2. Check Python path in settings
3. Install missing packages: `pip install -r requirements.txt`

### Terminal Slow to Start

Apply conda lazy loading from PowerShell Profile section above.

---

## Resources

| Resource | Location |
|----------|----------|
| Ziggie CLAUDE.md | `C:\Ziggie\CLAUDE.md` |
| Knowledge Base | `C:\ai-game-dev-system\knowledge-base\` |
| API Documentation | `C:\Ziggie\docs\API-DOCUMENTATION.md` |
| Onboarding Guide | `C:\Ziggie\docs\ONBOARDING-GUIDE.md` |

---

*Cursor IDE Guide for Ziggie Development*
*Created: 2025-12-28*
