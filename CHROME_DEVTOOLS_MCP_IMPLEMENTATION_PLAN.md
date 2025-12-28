# Chrome DevTools MCP Implementation Plan for Ziggie Cloud

**Date**: 2025-12-23
**Status**: Ready for Implementation
**Research Source**: 6 L1 Agents (Parallel Research)

---

## Executive Summary

This plan outlines the complete integration of Chrome DevTools MCP with Claude Code to enable AI-powered browser automation, debugging, and testing for Ziggie Cloud services. The implementation enables Claude to directly control Chrome browsers, inspect elements, monitor network traffic, and execute JavaScript - all critical for automated testing and development workflows.

---

## Phase 1: Prerequisites & Installation

### 1.1 System Requirements

| Component | Requirement | Status |
|-----------|-------------|--------|
| Node.js | v18+ (v20 recommended) | Check: `node --version` |
| npm | v9+ | Check: `npm --version` |
| Google Chrome | Latest stable | Check: `chrome://version` |
| Chrome DevTools Protocol | Enabled via `--remote-debugging-port` | Configure on launch |

### 1.2 Installation Steps

```bash
# Step 1: Install Chrome DevTools MCP globally
npm install -g @anthropic/mcp-chrome-devtools

# Step 2: Verify installation
npx @anthropic/mcp-chrome-devtools --version

# Step 3: Launch Chrome with DevTools Protocol enabled
# Windows (PowerShell):
& "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222

# Or add to Chrome shortcut target:
# "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222
```

### 1.3 Windows-Specific Configuration

```powershell
# Create a dedicated Chrome profile for automation
$chromePath = "C:\Program Files\Google\Chrome\Application\chrome.exe"
$debugPort = 9222

# Launch command (add to script or shortcut)
Start-Process $chromePath -ArgumentList "--remote-debugging-port=$debugPort", "--user-data-dir=C:\ChromeDebugProfile"
```

---

## Phase 2: Claude Code MCP Configuration

### 2.1 Create MCP Configuration File

Create or update `.mcp.json` in your project root or user home:

**Location**: `C:\Ziggie\.mcp.json`

```json
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "npx",
      "args": ["@anthropic/mcp-chrome-devtools"],
      "env": {
        "CHROME_DEBUG_PORT": "9222"
      },
      "description": "Chrome DevTools Protocol for browser automation and debugging"
    }
  }
}
```

### 2.2 Alternative: Global Configuration

**Location**: `C:\Users\minin\.mcp.json`

```json
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "npx",
      "args": ["@anthropic/mcp-chrome-devtools"],
      "env": {
        "CHROME_DEBUG_PORT": "9222"
      }
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@anthropic/mcp-filesystem", "C:/Ziggie"],
      "description": "File system access for Ziggie project"
    },
    "memory": {
      "command": "npx",
      "args": ["-y", "@anthropic/mcp-memory"],
      "description": "Persistent memory for session context"
    }
  }
}
```

### 2.3 Verify MCP Server Connection

After configuration, restart Claude Code and verify:

```
/mcp
```

Expected output should show `chrome-devtools` as connected.

---

## Phase 3: Chrome DevTools MCP Tools Reference (26 Tools)

### 3.1 Page Navigation & Control

| Tool | Description | Use Case |
|------|-------------|----------|
| `navigate` | Navigate to URL | Open Ziggie Cloud pages |
| `reload` | Reload current page | Refresh after changes |
| `goBack` / `goForward` | Browser history navigation | Test navigation flows |
| `getPageInfo` | Get current URL, title, viewport | Verify page state |

**Example Usage**:
```
Use chrome-devtools navigate to https://ziggie.cloud/api/health
```

### 3.2 Element Interaction

| Tool | Description | Use Case |
|------|-------------|----------|
| `click` | Click element by selector | Button clicks, form submission |
| `type` | Type text into input | Form filling |
| `hover` | Hover over element | Trigger hover states |
| `scroll` | Scroll page or element | Load lazy content |
| `querySelector` | Find element by CSS selector | Locate elements |
| `querySelectorAll` | Find all matching elements | List items |

**Example Usage**:
```
Use chrome-devtools click on selector "#login-button"
Use chrome-devtools type "admin" into selector "#username"
```

### 3.3 DOM Inspection

| Tool | Description | Use Case |
|------|-------------|----------|
| `getOuterHTML` | Get element HTML | Inspect component structure |
| `getInnerText` | Get visible text content | Verify displayed text |
| `getAttributes` | Get element attributes | Check data attributes |
| `getComputedStyles` | Get computed CSS | Debug styling issues |

### 3.4 JavaScript Execution

| Tool | Description | Use Case |
|------|-------------|----------|
| `evaluate` | Execute JavaScript in page | Custom automation logic |
| `callFunction` | Call page function | Trigger existing functions |

**Example Usage**:
```
Use chrome-devtools evaluate "document.querySelectorAll('.error').length"
Use chrome-devtools evaluate "localStorage.getItem('authToken')"
```

### 3.5 Network Monitoring

| Tool | Description | Use Case |
|------|-------------|----------|
| `getNetworkRequests` | List network requests | Monitor API calls |
| `waitForNetworkIdle` | Wait for network quiet | Ensure page loaded |
| `interceptRequest` | Intercept/modify requests | Mock API responses |

**Example Usage**:
```
Use chrome-devtools getNetworkRequests filtered by "api/health"
```

### 3.6 Console & Debugging

| Tool | Description | Use Case |
|------|-------------|----------|
| `getConsoleLogs` | Get console output | Debug JavaScript errors |
| `clearConsole` | Clear console logs | Reset for new test |

### 3.7 Screenshots & Visual

| Tool | Description | Use Case |
|------|-------------|----------|
| `screenshot` | Capture screenshot | Visual regression |
| `screenshotElement` | Capture element screenshot | Component snapshots |
| `setViewport` | Set viewport size | Responsive testing |

**Example Usage**:
```
Use chrome-devtools screenshot and save to C:/Ziggie/screenshots/test.png
Use chrome-devtools setViewport to width 375 height 812 (iPhone X)
```

### 3.8 Tab Management

| Tool | Description | Use Case |
|------|-------------|----------|
| `listTabs` | List all browser tabs | Multi-page testing |
| `switchTab` | Switch to specific tab | Navigate between pages |
| `closeTab` | Close a tab | Cleanup |
| `newTab` | Open new tab | Multi-session testing |

---

## Phase 4: Ziggie Cloud Integration Patterns

### 4.1 API Health Monitoring

```
# Automated health check workflow
1. Navigate to https://ziggie.cloud/api/health
2. Wait for network idle
3. Get page content
4. Verify JSON response contains "healthy": true
5. Screenshot on failure
```

### 4.2 n8n Workflow Testing

```
# Test n8n workflow execution
1. Navigate to https://ziggie.cloud/n8n/
2. Wait for page load
3. Login with credentials (admin / K5t0F5hXkD7peCGQk6RY2g==)
4. Click on target workflow
5. Execute workflow
6. Monitor network for webhook calls
7. Verify execution success
```

### 4.3 Flowise Chatflow Testing

```
# Test Flowise chatflow
1. Navigate to https://ziggie.cloud/flowise/
2. Login with credentials (admin / JKAXqApBUKAsQ+RKV7xDRA==)
3. Open target chatflow
4. Send test message via chat interface
5. Wait for response
6. Verify response quality
```

### 4.4 Sim Studio Agent Testing

```
# Test agent simulation
1. Navigate to https://ziggie.cloud/sim/
2. Create new simulation
3. Add test agent
4. Execute simulation
5. Monitor WebSocket messages
6. Capture performance metrics
```

### 4.5 MCP Gateway Debugging

```
# Debug MCP JSON-RPC calls
1. Navigate to https://ziggie.cloud/mcp/
2. Enable network monitoring
3. Send JSON-RPC initialize request
4. Capture request/response
5. Verify protocol version
6. Test tool invocations
```

---

## Phase 5: Recommended MCP Ecosystem Servers

### 5.1 Power User Configuration

Add these complementary MCP servers for complete development workflow:

```json
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "npx",
      "args": ["@anthropic/mcp-chrome-devtools"],
      "env": { "CHROME_DEBUG_PORT": "9222" }
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@anthropic/mcp-filesystem", "C:/Ziggie"]
    },
    "memory": {
      "command": "npx",
      "args": ["-y", "@anthropic/mcp-memory"]
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@anthropic/mcp-github"],
      "env": { "GITHUB_TOKEN": "${GITHUB_TOKEN}" }
    },
    "postgres": {
      "command": "npx",
      "args": ["-y", "@anthropic/mcp-postgres"],
      "env": { "DATABASE_URL": "postgresql://ziggie:${POSTGRES_PASSWORD}@82.25.112.73:5432/ziggie" }
    },
    "docker": {
      "command": "npx",
      "args": ["-y", "mcp-docker"]
    }
  }
}
```

### 5.2 Server Descriptions

| Server | Purpose | Ziggie Use Case |
|--------|---------|-----------------|
| `chrome-devtools` | Browser automation | E2E testing, visual debugging |
| `filesystem` | File operations | Log analysis, config editing |
| `memory` | Persistent context | Session state across conversations |
| `github` | GitHub API access | Issue tracking, PR management |
| `postgres` | Database access | Direct query, data inspection |
| `docker` | Container management | Service control, log access |

---

## Phase 6: Automation Workflow Templates

### 6.1 E2E Test Automation

```markdown
## Automated E2E Test Workflow

1. **Setup**: Launch Chrome with debug port
2. **Navigation**: Navigate to target page
3. **Interaction**: Perform user actions
4. **Verification**: Check expected outcomes
5. **Capture**: Screenshot on failure
6. **Report**: Generate test results
```

### 6.2 Visual Regression Testing

```markdown
## Visual Regression Workflow

1. Navigate to component page
2. Set viewport to standard sizes (desktop, tablet, mobile)
3. Take baseline screenshots
4. Compare with stored baselines
5. Flag visual differences
6. Update baselines if intentional
```

### 6.3 Performance Monitoring

```markdown
## Performance Monitoring Workflow

1. Enable network monitoring
2. Navigate to target page
3. Wait for network idle
4. Collect timing metrics:
   - Time to First Byte (TTFB)
   - First Contentful Paint (FCP)
   - Largest Contentful Paint (LCP)
5. Capture network waterfall
6. Report slow requests
```

### 6.4 Security Scanning

```markdown
## Security Scan Workflow

1. Navigate to login page
2. Attempt common injection patterns
3. Check for exposed console errors
4. Verify secure headers (CSP, HSTS)
5. Check for sensitive data in localStorage
6. Report findings
```

---

## Phase 7: Implementation Checklist

### 7.1 Setup Checklist

- [ ] Install Node.js v18+
- [ ] Install `@anthropic/mcp-chrome-devtools`
- [ ] Configure Chrome with `--remote-debugging-port=9222`
- [ ] Create `.mcp.json` configuration
- [ ] Restart Claude Code
- [ ] Verify MCP server connection with `/mcp`

### 7.2 Integration Checklist

- [ ] Test navigation to Ziggie Cloud services
- [ ] Verify element interaction on n8n, Flowise, Sim Studio
- [ ] Test network monitoring on API endpoints
- [ ] Test screenshot capture
- [ ] Test JavaScript evaluation

### 7.3 Workflow Checklist

- [ ] Create E2E test workflow for API health
- [ ] Create E2E test workflow for n8n
- [ ] Create E2E test workflow for Flowise
- [ ] Create visual regression baseline
- [ ] Create performance monitoring baseline

---

## Security Considerations

### 8.1 Production Safety

| Risk | Mitigation |
|------|------------|
| Exposed debug port | Bind to localhost only (default) |
| Credential exposure | Use environment variables |
| Session hijacking | Use dedicated debug profile |
| Unintended actions | Test in staging first |

### 8.2 Best Practices

1. **Never expose debug port to network** - Keep `--remote-debugging-port` bound to 127.0.0.1
2. **Use separate Chrome profile** - `--user-data-dir=C:\ChromeDebugProfile`
3. **Rotate test credentials** - Don't use production credentials in automation
4. **Log all actions** - Maintain audit trail of automated actions
5. **Implement rate limiting** - Prevent accidental DoS on services

---

## Quick Start Commands

```bash
# 1. Install MCP server
npm install -g @anthropic/mcp-chrome-devtools

# 2. Launch Chrome with debugging
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222

# 3. Verify in Claude Code
/mcp

# 4. Test navigation
Use chrome-devtools navigate to https://ziggie.cloud/api/health

# 5. Take screenshot
Use chrome-devtools screenshot
```

---

## Appendix A: Full Tools Input/Output Schema

### navigate
```json
{
  "input": { "url": "string" },
  "output": { "success": "boolean", "url": "string", "title": "string" }
}
```

### click
```json
{
  "input": { "selector": "string" },
  "output": { "success": "boolean", "clicked": "boolean" }
}
```

### screenshot
```json
{
  "input": { "path": "string (optional)", "fullPage": "boolean (optional)" },
  "output": { "success": "boolean", "path": "string", "base64": "string" }
}
```

### evaluate
```json
{
  "input": { "expression": "string" },
  "output": { "result": "any", "exceptionDetails": "object (if error)" }
}
```

### getNetworkRequests
```json
{
  "input": { "filter": "string (optional)" },
  "output": { "requests": [{ "url": "string", "method": "string", "status": "number", "timing": "object" }] }
}
```

---

## Appendix B: Troubleshooting

### Chrome Not Connecting
```
Error: Cannot connect to Chrome at localhost:9222
```
**Solution**: Ensure Chrome is launched with `--remote-debugging-port=9222` and no other Chrome instance is running.

### MCP Server Not Found
```
Error: MCP server 'chrome-devtools' not found
```
**Solution**: Verify `.mcp.json` is in project root or user home. Restart Claude Code.

### Element Not Found
```
Error: No element matches selector '#button'
```
**Solution**: Use `waitForSelector` before interacting. Check selector in Chrome DevTools.

---

**Plan Generated**: 2025-12-23
**Research Agents**: 6 L1 Agents (Parallel)
**Ready for Implementation**: Yes
