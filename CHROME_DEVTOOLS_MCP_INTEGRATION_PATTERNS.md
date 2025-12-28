# Chrome DevTools MCP Integration Patterns for Ziggie Cloud Services

> **Research Date**: 2025-12-23
> **Context**: Integration patterns for debugging, testing, and profiling Ziggie Cloud services using Chrome DevTools MCP
> **Services Covered**: Ziggie API (FastAPI), Sim Studio, MCP Gateway, n8n, Flowise, Open WebUI

---

## Table of Contents

1. [Chrome DevTools MCP Overview](#chrome-devtools-mcp-overview)
2. [Setup & Configuration](#setup--configuration)
3. [Integration Pattern 1: FastAPI Backend Debugging (Ziggie API)](#integration-pattern-1-fastapi-backend-debugging-ziggie-api)
4. [Integration Pattern 2: Real-Time Application Testing (n8n)](#integration-pattern-2-real-time-application-testing-n8n)
5. [Integration Pattern 3: Performance Profiling SPAs (Flowise, Open WebUI)](#integration-pattern-3-performance-profiling-spas-flowise-open-webui)
6. [Integration Pattern 4: Visual Regression Testing](#integration-pattern-4-visual-regression-testing)
7. [Integration Pattern 5: CI/CD Integration](#integration-pattern-5-cicd-integration)
8. [Integration Pattern 6: WebSocket Debugging (MCP Gateway)](#integration-pattern-6-websocket-debugging-mcp-gateway)
9. [Advanced Patterns](#advanced-patterns)
10. [Example Prompts for Claude Code](#example-prompts-for-claude-code)

---

## Chrome DevTools MCP Overview

### What is Chrome DevTools MCP?

Released in **public preview by Google's Chrome DevTools team on September 23, 2025**, [Chrome DevTools MCP](https://developer.chrome.com/blog/chrome-devtools-mcp) is an official Model Context Protocol server that connects AI assistants directly to Chrome's debugging infrastructure.

### Key Capabilities

Your AI can now:
- Launch browsers and navigate to applications
- Inspect network requests, headers, and responses
- Record performance traces and analyze Core Web Vitals
- Analyze console errors and warnings
- Execute JavaScript in browser context
- Take screenshots and DOM snapshots
- Simulate user interactions (clicks, form fills, drag-drop)
- Monitor real-time WebSocket traffic

### Architecture

```
┌─────────────────────────────────────────────────────┐
│ MCP Protocol Layer                                  │
│ (Standardized AI ↔ Server Communication)           │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│ Tool Adapter Layer                                  │
│ (Translates high-level MCP → browser actions)      │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│ Puppeteer Foundation                                │
│ (Reliable automation + automatic waiting)           │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│ Chrome DevTools Protocol (CDP)                      │
│ (Low-level browser control via WebSocket)           │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│ Chrome Runtime                                      │
│ (Actual browser instance)                           │
└─────────────────────────────────────────────────────┘
```

### 26 Available Tools (6 Categories)

| Category | Tools | Count |
|----------|-------|-------|
| **Input Automation** | click, drag, fill, fill_form, handle_dialog, hover, upload_file | 7 |
| **Navigation** | navigate_page, new_page, list_pages, select_page, close_page, navigate_page_history, wait_for | 7 |
| **Debugging** | evaluate_script, list_console_messages, take_screenshot, take_snapshot | 4 |
| **Network** | list_network_requests, get_network_request | 2 |
| **Performance** | performance_start_trace, performance_stop_trace, performance_analyze_insight | 3 |
| **Storage** | get_cookies, set_cookies, clear_cookies | 3 |

---

## Setup & Configuration

### Requirements

- **Node.js**: 22+ (required)
- **Chrome Browser**: Latest stable version
- **MCP Client**: Claude Code, Claude Desktop, Cursor, or Copilot

### Installation (Claude Code)

```bash
# Quick install via Claude Code CLI
claude mcp add chrome-devtools npx chrome-devtools-mcp@latest
```

### Manual Configuration

Add to your MCP configuration file (`claude_desktop_config.json` or similar):

```json
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "npx",
      "args": ["-y", "chrome-devtools-mcp@latest"]
    }
  }
}
```

### Advanced Configuration Options

#### Headless Mode (CI/CD)

```json
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "npx",
      "args": ["-y", "chrome-devtools-mcp@latest", "--headless"]
    }
  }
}
```

#### Connect to Existing Chrome Instance (WebSocket)

```json
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "npx",
      "args": [
        "-y",
        "chrome-devtools-mcp@latest",
        "--wsEndpoint=ws://127.0.0.1:9222/devtools/browser/<id>"
      ]
    }
  }
}
```

To get the WebSocket endpoint:
1. Launch Chrome with remote debugging: `chrome --remote-debugging-port=9222`
2. Visit: `http://127.0.0.1:9222/json/version`
3. Copy the `webSocketDebuggerUrl` value

#### Custom Headers for Authentication

```json
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "npx",
      "args": [
        "-y",
        "chrome-devtools-mcp@latest",
        "--wsHeaders={\"Authorization\":\"Bearer YOUR_TOKEN\"}"
      ]
    }
  }
}
```

---

## Integration Pattern 1: FastAPI Backend Debugging (Ziggie API)

**Service**: https://ziggie.cloud/api/

### Use Cases

1. **CORS Issue Diagnosis**
2. **API Response Validation**
3. **Request/Response Timing Analysis**
4. **Authentication Flow Debugging**

### Pattern: CORS Debugging

#### Problem Scenario
Frontend calls to `https://ziggie.cloud/api/` are blocked by CORS errors.

#### Claude Code Prompt

```
Using Chrome DevTools MCP:
1. Navigate to https://ziggie.cloud/api/docs (Swagger UI)
2. Open Network monitor
3. Trigger a test API call to /users endpoint
4. Inspect the preflight OPTIONS request
5. Check for Access-Control-Allow-Origin headers
6. Analyze the response headers and status codes
7. Provide recommendations for CORS configuration
```

#### Expected AI Workflow

```python
# AI will execute these MCP tools internally:

# 1. Navigate to API docs
navigate_page(url="https://ziggie.cloud/api/docs")

# 2. Wait for page load
wait_for(selector="div.swagger-ui", timeout=5000)

# 3. Monitor network requests
list_network_requests()

# 4. Simulate API call (via evaluate_script)
evaluate_script("""
  fetch('https://ziggie.cloud/api/users', {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' }
  })
""")

# 5. Get specific request details
get_network_request(url="https://ziggie.cloud/api/users")

# 6. Analyze headers
# AI will inspect: Access-Control-Allow-Origin, Access-Control-Allow-Headers, etc.
```

#### What to Look For

Chrome DevTools MCP will help diagnose:
- Missing `Access-Control-Allow-Origin` header
- Incorrect `Access-Control-Allow-Methods` configuration
- Preflight (OPTIONS) request failures
- Custom header blocking (e.g., `Authorization` not in `Access-Control-Allow-Headers`)

#### FastAPI CORS Fix Pattern

Based on findings, AI can suggest:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://ziggie.cloud"],  # Specific origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Pattern: API Performance Profiling

#### Claude Code Prompt

```
Using Chrome DevTools MCP, profile the performance of Ziggie API:
1. Navigate to https://ziggie.cloud/api/docs
2. Start a performance trace
3. Execute 5 sequential API calls to different endpoints
4. Stop the trace
5. Analyze: request timing, network waterfall, total blocking time
6. Identify the slowest endpoint and suggest optimizations
```

#### Expected AI Workflow

```python
# 1. Navigate
navigate_page(url="https://ziggie.cloud/api/docs")

# 2. Start performance trace
performance_start_trace()

# 3. Execute API calls
evaluate_script("""
  const endpoints = ['/users', '/projects', '/tasks', '/metrics', '/logs'];
  Promise.all(endpoints.map(ep =>
    fetch('https://ziggie.cloud/api' + ep)
  ));
""")

# 4. Stop trace after completion
performance_stop_trace()

# 5. Analyze insights
performance_analyze_insight()
```

#### Metrics Analyzed

- **First Byte Time (TTFB)**: Server response latency
- **Content Download Time**: Network bandwidth bottlenecks
- **Request Queuing**: Browser connection limits
- **DNS Lookup**: DNS resolution delays

---

## Integration Pattern 2: Real-Time Application Testing (n8n)

**Service**: https://ziggie.cloud/n8n/

### Use Cases

1. **Workflow Execution Monitoring**
2. **WebSocket Connection Debugging**
3. **Node Failure Detection**
4. **Performance Bottleneck Identification**

### Pattern: Workflow Execution Monitoring

#### Claude Code Prompt

```
Using Chrome DevTools MCP, monitor an n8n workflow execution:
1. Navigate to https://ziggie.cloud/n8n/
2. Open the "User Onboarding" workflow
3. Monitor console messages and network requests
4. Execute the workflow manually
5. Capture any errors or warnings
6. Take screenshots of each workflow step execution
7. Analyze execution timing between nodes
```

#### Expected AI Workflow

```python
# 1. Navigate to n8n
navigate_page(url="https://ziggie.cloud/n8n/")

# 2. Wait for editor load
wait_for(selector=".workflow-canvas", timeout=10000)

# 3. Start monitoring console
list_console_messages()

# 4. Monitor network (WebSocket connections for real-time updates)
list_network_requests()

# 5. Click execute button
click(selector="button[data-test-id='execute-workflow']")

# 6. Wait for execution completion
wait_for(selector=".execution-success", timeout=30000)

# 7. Take screenshot of results
take_screenshot(filename="workflow-execution-results.png")

# 8. List console errors
list_console_messages(level="error")
```

#### n8n-Specific Debugging Checklist

Chrome DevTools MCP helps identify:
- **Failed HTTP Request Nodes**: 4xx/5xx status codes in Network tab
- **Webhook Timeouts**: Long-running requests exceeding n8n timeout (120s default)
- **JSON Parsing Errors**: Console errors from malformed API responses
- **Rate Limiting**: 429 status codes from external APIs
- **Variable Resolution Issues**: Console warnings about undefined variables

### Pattern: WebSocket Connection Health

n8n uses WebSockets for real-time workflow updates. Monitor connection stability:

#### Claude Code Prompt

```
Using Chrome DevTools MCP:
1. Navigate to https://ziggie.cloud/n8n/
2. Monitor WebSocket connections in Network tab
3. Check for connection drops or reconnection attempts
4. Analyze WebSocket message frequency during workflow execution
5. Report on connection stability and latency
```

#### Expected AI Analysis

```
WebSocket Connections Found:
- wss://ziggie.cloud/n8n/push
  Status: Connected
  Messages Sent: 47
  Messages Received: 52
  Average Latency: 45ms
  Connection Drops: 0

Analysis:
✅ Stable WebSocket connection
✅ Low latency (<50ms)
⚠️  High message frequency (15 msg/sec) during large workflow execution
```

### Integration with n8n MCP Server

For deeper integration, combine Chrome DevTools MCP with [n8n's native MCP server](https://n8n.io/workflows/10779-monitor-and-debug-n8n-workflows-with-claude-ai-assistant-and-mcp-server/):

```json
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "npx",
      "args": ["-y", "chrome-devtools-mcp@latest"]
    },
    "n8n-monitoring": {
      "command": "python",
      "args": ["n8n_mcp_server.py"],
      "env": {
        "N8N_API_URL": "https://ziggie.cloud/n8n/api",
        "N8N_API_KEY": "${N8N_API_KEY}"
      }
    }
  }
}
```

**Combined Prompt**:
```
Using both Chrome DevTools MCP and n8n MCP server:
1. Query n8n MCP for recent workflow failures
2. For each failed execution, use Chrome DevTools MCP to:
   - Navigate to the execution detail page
   - Inspect network requests made during that execution
   - Capture console errors
   - Take screenshots of the error state
3. Correlate browser errors with n8n execution logs
4. Generate a root cause analysis report
```

---

## Integration Pattern 3: Performance Profiling SPAs (Flowise, Open WebUI)

**Services**:
- https://ziggie.cloud/flowise/
- https://ziggie.cloud/chat/

### Use Cases

1. **LLM Response Latency Measurement**
2. **Core Web Vitals Analysis**
3. **Memory Leak Detection**
4. **Bundle Size Optimization**

### Pattern: LLM Workflow Performance (Flowise)

#### Claude Code Prompt

```
Using Chrome DevTools MCP, profile Flowise LLM workflow performance:
1. Navigate to https://ziggie.cloud/flowise/
2. Open a complex RAG workflow (e.g., "Document Q&A with Vector Store")
3. Start performance trace
4. Execute a test query: "Summarize the key findings from document X"
5. Stop trace when response is complete
6. Analyze:
   - LCP (Largest Contentful Paint)
   - TBT (Total Blocking Time)
   - Network requests to LLM APIs (OpenAI, Anthropic, etc.)
   - Response streaming latency
7. Identify performance bottlenecks
```

#### Expected AI Workflow

```python
# 1. Navigate
navigate_page(url="https://ziggie.cloud/flowise/canvas/<workflow-id>")

# 2. Start trace
performance_start_trace()

# 3. Fill query input
fill(selector="textarea[placeholder='Type your message...']",
     value="Summarize the key findings from document X")

# 4. Submit query
click(selector="button[aria-label='Send message']")

# 5. Wait for response completion
wait_for(selector=".message-complete", timeout=60000)

# 6. Stop trace
performance_stop_trace()

# 7. Analyze
performance_analyze_insight()
```

#### Metrics for LLM Workflows

| Metric | What It Measures | Target |
|--------|------------------|--------|
| **Time to First Token** | Latency before streaming starts | <500ms |
| **Token Streaming Rate** | Tokens per second during generation | >50 tokens/s |
| **Vector Search Time** | Embedding + similarity search | <200ms |
| **Total Response Time** | End-to-end query → complete response | <5s |
| **Network Idle Time** | Gaps between network activity | Minimize |

### Pattern: Memory Leak Detection (Open WebUI)

Chat applications with infinite scroll can suffer from memory leaks.

#### Claude Code Prompt

```
Using Chrome DevTools MCP, detect memory leaks in Open WebUI:
1. Navigate to https://ziggie.cloud/chat/
2. Start a performance trace
3. Simulate a long chat session:
   - Send 20 sequential messages
   - Scroll through chat history
   - Switch between 3 different conversations
4. Stop trace
5. Analyze memory usage growth
6. Take heap snapshots before and after
7. Identify detached DOM nodes or event listener leaks
```

#### Expected AI Analysis

```
Memory Analysis Report:

Initial Memory: 45.2 MB
After 20 messages: 78.5 MB
After 50 messages: 142.1 MB

⚠️  Memory Growth: 96.9 MB (214% increase)
⚠️  Detached DOM Nodes: 347 found

Likely Causes:
1. Message components not properly unmounted when scrolled out of view
2. Event listeners on message elements not cleaned up
3. Large base64 image data retained in memory

Recommendations:
- Implement virtual scrolling (react-window or similar)
- Add cleanup in useEffect hooks
- Use lazy loading for images
- Clear old messages from DOM after 100 messages
```

### Pattern: Core Web Vitals Monitoring

#### Claude Code Prompt

```
Using Chrome DevTools MCP, measure Core Web Vitals for Flowise:
1. Navigate to https://ziggie.cloud/flowise/
2. Start performance trace
3. Simulate realistic user journey:
   - Land on homepage
   - Browse workflows
   - Open a workflow
   - Execute a test query
4. Stop trace
5. Extract and report:
   - LCP (Largest Contentful Paint)
   - CLS (Cumulative Layout Shift)
   - FID (First Input Delay) or INP (Interaction to Next Paint)
   - TTFB (Time to First Byte)
```

#### Expected Output

```
Core Web Vitals Report - Flowise
================================

✅ LCP: 1.2s (Good - <2.5s)
⚠️  CLS: 0.15 (Needs Improvement - target <0.1)
✅ INP: 85ms (Good - <200ms)
✅ TTFB: 320ms (Good - <800ms)

Issues Detected:
1. CLS: Layout shift caused by dynamic canvas sizing
   - Canvas container has no explicit height
   - Recommendation: Add min-height or skeleton loader

2. LCP Element: Hero section background image (1.8MB)
   - Recommendation: Use WebP format + compression (target <100KB)
```

### Integration with Langfuse/LangSmith (Flowise Monitoring)

For comprehensive Flowise monitoring, combine Chrome DevTools MCP with observability tools:

```json
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "npx",
      "args": ["-y", "chrome-devtools-mcp@latest"]
    }
  }
}
```

In Flowise, configure [Langfuse integration](https://langfuse.com/docs/integrations/flowise) for backend metrics:
- Token usage
- LLM latency
- Cost tracking
- Error rates

**Combined Analysis Prompt**:
```
Using Chrome DevTools MCP for frontend metrics and Langfuse for backend:
1. Chrome DevTools: Measure total response time from user perspective
2. Langfuse API: Query LLM processing time for the same request
3. Calculate frontend overhead: Total Time - LLM Time
4. Identify if bottleneck is frontend (network/rendering) or backend (LLM)
```

---

## Integration Pattern 4: Visual Regression Testing

### Use Cases

1. **UI Component Consistency Across Deployments**
2. **Cross-Browser Layout Verification**
3. **Responsive Design Testing**
4. **Brand Style Guide Compliance**

### Pattern: Automated Screenshot Comparison

#### Claude Code Prompt

```
Using Chrome DevTools MCP, perform visual regression testing:
1. Navigate to https://ziggie.cloud/chat/
2. Take baseline screenshots at 3 viewport sizes:
   - Desktop: 1920x1080
   - Tablet: 768x1024
   - Mobile: 375x667
3. Interact with key UI components:
   - Click "New Chat" button
   - Send a test message
   - Open settings panel
4. Take screenshots of each state
5. Compare with baseline images (if provided)
6. Report any visual differences
```

#### Expected AI Workflow

```python
viewports = [
    {"width": 1920, "height": 1080, "name": "desktop"},
    {"width": 768, "height": 1024, "name": "tablet"},
    {"width": 375, "height": 667, "name": "mobile"}
]

for viewport in viewports:
    # Set viewport
    evaluate_script(f"""
      window.resizeTo({viewport['width']}, {viewport['height']})
    """)

    # Navigate
    navigate_page(url="https://ziggie.cloud/chat/")

    # Wait for content
    wait_for(selector=".chat-interface", timeout=5000)

    # Take baseline
    take_screenshot(filename=f"baseline-{viewport['name']}.png")

    # Interact: New Chat
    click(selector="button[aria-label='New Chat']")
    wait_for(selector=".new-chat-modal", timeout=2000)
    take_screenshot(filename=f"new-chat-modal-{viewport['name']}.png")

    # Close modal, send message
    click(selector=".modal-close")
    fill(selector="textarea.message-input", value="Test message")
    click(selector="button.send-message")
    wait_for(selector=".message-sent", timeout=3000)
    take_screenshot(filename=f"message-sent-{viewport['name']}.png")
```

### Pattern: Component-Level Screenshot Testing

For design system components in isolation:

#### Claude Code Prompt

```
Using Chrome DevTools MCP, test UI components in Sim Studio:
1. Navigate to https://ziggie.cloud/sim/
2. Isolate each major component:
   - Agent card
   - Simulation timeline
   - Metric dashboard
3. For each component:
   - Take screenshot in default state
   - Trigger hover state, take screenshot
   - Trigger active/selected state, take screenshot
4. Verify consistent spacing, colors, fonts against design system
```

### CI/CD Integration for Visual Regression

See [Integration Pattern 5](#integration-pattern-5-cicd-integration) for automated regression testing in pipelines.

---

## Integration Pattern 5: CI/CD Integration

### Use Cases

1. **Automated Performance Regression Detection**
2. **Pre-Deployment Health Checks**
3. **Cross-Environment Validation**

### Pattern: GitHub Actions Performance Gate

#### Workflow File: `.github/workflows/performance-check.yml`

```yaml
name: Performance Regression Check

on:
  pull_request:
    branches: [main]

jobs:
  performance-check:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '22'

      - name: Install Chrome
        run: |
          wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
          sudo sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
          sudo apt-get update
          sudo apt-get install -y google-chrome-stable

      - name: Install Chrome DevTools MCP
        run: npm install -g chrome-devtools-mcp

      - name: Run Performance Tests
        run: |
          # Start Chrome in headless mode
          google-chrome-stable --headless --remote-debugging-port=9222 --disable-gpu &

          # Run performance test script via Claude API
          node performance-test.js
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}

      - name: Compare with Baseline
        run: node compare-metrics.js

      - name: Comment PR with Results
        uses: actions/github-script@v6
        with:
          script: |
            const fs = require('fs');
            const results = JSON.parse(fs.readFileSync('performance-results.json'));

            const comment = `## Performance Results

            | Metric | Baseline | Current | Change |
            |--------|----------|---------|--------|
            | LCP | ${results.baseline.lcp}ms | ${results.current.lcp}ms | ${results.change.lcp} |
            | TBT | ${results.baseline.tbt}ms | ${results.current.tbt}ms | ${results.change.tbt} |
            | FCP | ${results.baseline.fcp}ms | ${results.current.fcp}ms | ${results.change.fcp} |

            ${results.status === 'FAILED' ? '❌ Performance regression detected!' : '✅ Performance check passed'}
            `;

            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: comment
            });

      - name: Fail if Regression Detected
        run: |
          if [ "$(jq -r '.status' performance-results.json)" == "FAILED" ]; then
            echo "Performance regression detected!"
            exit 1
          fi
```

#### Performance Test Script: `performance-test.js`

```javascript
const Anthropic = require('@anthropic-ai/sdk');
const fs = require('fs');

const anthropic = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY,
});

async function runPerformanceTest() {
  const message = await anthropic.messages.create({
    model: 'claude-3-5-sonnet-20241022',
    max_tokens: 4096,
    tools: [], // MCP tools auto-loaded from config
    messages: [{
      role: 'user',
      content: `
        Using Chrome DevTools MCP in headless mode:
        1. Navigate to https://ziggie.cloud/flowise/
        2. Start performance trace
        3. Wait for page to fully load
        4. Stop trace
        5. Extract metrics: LCP, TBT, FCP, TTFB
        6. Output as JSON: {"lcp": X, "tbt": Y, "fcp": Z, "ttfb": W}
      `
    }]
  });

  // Parse metrics from AI response
  const metricsText = message.content.find(block =>
    block.type === 'text' && block.text.includes('{')
  ).text;

  const metrics = JSON.parse(metricsText.match(/\{[^}]+\}/)[0]);

  fs.writeFileSync('current-metrics.json', JSON.stringify(metrics, null, 2));
}

runPerformanceTest().catch(console.error);
```

#### Baseline Comparison Script: `compare-metrics.js`

```javascript
const fs = require('fs');

const baseline = JSON.parse(fs.readFileSync('baseline-metrics.json'));
const current = JSON.parse(fs.readFileSync('current-metrics.json'));

const THRESHOLDS = {
  lcp: 0.10,  // 10% regression allowed
  tbt: 0.15,  // 15% regression allowed
  fcp: 0.10,
  ttfb: 0.20
};

const results = {
  baseline,
  current,
  change: {},
  status: 'PASSED'
};

for (const [metric, threshold] of Object.entries(THRESHOLDS)) {
  const baselineValue = baseline[metric];
  const currentValue = current[metric];
  const percentChange = ((currentValue - baselineValue) / baselineValue);

  results.change[metric] = `${(percentChange * 100).toFixed(2)}%`;

  if (percentChange > threshold) {
    results.status = 'FAILED';
    results.change[metric] += ' ❌';
  } else {
    results.change[metric] += ' ✅';
  }
}

fs.writeFileSync('performance-results.json', JSON.stringify(results, null, 2));
console.log(JSON.stringify(results, null, 2));
```

### Pattern: Pre-Deployment Smoke Test

#### Claude Code Prompt (via API in CI)

```
Using Chrome DevTools MCP in headless mode:
1. Navigate to https://staging.ziggie.cloud/api/docs
2. Verify all critical endpoints return 200:
   - GET /health
   - GET /users
   - POST /auth/login
3. Navigate to https://staging.ziggie.cloud/chat/
4. Send a test message, verify response received
5. Navigate to https://staging.ziggie.cloud/n8n/
6. Verify workflow list loads successfully
7. Take screenshots of each service for manual review
8. Report: PASS if all checks succeed, FAIL otherwise
```

---

## Integration Pattern 6: WebSocket Debugging (MCP Gateway)

**Service**: https://ziggie.cloud/mcp/

### Use Cases

1. **JSON-RPC Message Inspection**
2. **Connection Stability Monitoring**
3. **Protocol Compliance Verification**
4. **Latency Analysis**

### Pattern: MCP Gateway WebSocket Monitoring

The MCP Gateway uses WebSocket for JSON-RPC 2.0 communication. Monitor this protocol-level traffic:

#### Claude Code Prompt

```
Using Chrome DevTools MCP, debug the MCP Gateway WebSocket connection:
1. Navigate to a client page that connects to wss://ziggie.cloud/mcp/
2. Monitor WebSocket connections in Network tab
3. Capture the initial handshake
4. Monitor JSON-RPC messages:
   - Request format validation
   - Response correlation (matching request IDs)
   - Error responses
5. Measure round-trip latency for 10 requests
6. Check for connection drops or reconnection attempts
7. Validate JSON-RPC 2.0 compliance:
   - All requests have: jsonrpc, method, id
   - All responses have: jsonrpc, id, result OR error
```

#### Expected AI Workflow

```python
# 1. Navigate to MCP client
navigate_page(url="https://ziggie.cloud/sim/")  # Example client

# 2. Wait for WebSocket connection
wait_for(script="""
  new Promise(resolve => {
    const interval = setInterval(() => {
      if (window.performance.getEntriesByType('resource')
          .some(r => r.name.includes('wss://ziggie.cloud/mcp/'))) {
        clearInterval(interval);
        resolve();
      }
    }, 100);
  })
""", timeout=10000)

# 3. Monitor network
list_network_requests(filter="WS")

# 4. Inspect WebSocket frames
get_network_request(url="wss://ziggie.cloud/mcp/")

# 5. Execute test RPC calls via browser console
evaluate_script("""
  const ws = new WebSocket('wss://ziggie.cloud/mcp/');
  const requests = [];

  ws.onopen = () => {
    for (let i = 0; i < 10; i++) {
      const request = {
        jsonrpc: '2.0',
        method: 'ping',
        id: i,
        params: { timestamp: Date.now() }
      };
      requests.push({ sent: Date.now(), id: i });
      ws.send(JSON.stringify(request));
    }
  };

  ws.onmessage = (event) => {
    const response = JSON.parse(event.data);
    const request = requests.find(r => r.id === response.id);
    if (request) {
      console.log(`Latency for request ${response.id}: ${Date.now() - request.sent}ms`);
    }
  };
""")

# 6. Collect console logs with latency measurements
list_console_messages()
```

#### JSON-RPC Validation Checklist

Chrome DevTools MCP helps verify:

```
✅ Request Structure:
   - "jsonrpc": "2.0" present
   - "method" is a string
   - "id" is unique (number or string)
   - "params" is object or array (optional)

✅ Response Structure:
   - "jsonrpc": "2.0" present
   - "id" matches request
   - Either "result" XOR "error" present
   - "error" has: code (number), message (string)

❌ Common Issues Detected:
   - Missing "jsonrpc" field
   - "id" mismatch between request/response
   - Both "result" and "error" present
   - Non-standard error codes
```

### Pattern: Connection Resilience Testing

Test WebSocket reconnection logic:

#### Claude Code Prompt

```
Using Chrome DevTools MCP, test MCP Gateway connection resilience:
1. Navigate to https://ziggie.cloud/sim/
2. Verify WebSocket connection established
3. Simulate network interruption:
   - Use Chrome DevTools to throttle network to "Offline"
   - Wait 5 seconds
   - Restore network to "Fast 3G"
4. Monitor reconnection attempts:
   - Time to detect disconnection
   - Number of reconnection attempts
   - Exponential backoff pattern
   - Success/failure of reconnection
5. Verify no message loss (if queuing is implemented)
```

#### Expected Analysis

```
Connection Resilience Report:

Initial Connection:
✅ Established in 245ms
✅ Initial handshake successful

Network Interruption Simulation:
- Offline at: T+5000ms
- Disconnection detected: T+5150ms (detection lag: 150ms)

Reconnection Attempts:
1. Attempt 1: T+5200ms (delay: 50ms) - FAILED (offline)
2. Attempt 2: T+5400ms (delay: 200ms) - FAILED (offline)
3. Attempt 3: T+5800ms (delay: 400ms) - FAILED (offline)
4. Network restored: T+10000ms
5. Attempt 4: T+10200ms (delay: 400ms) - SUCCESS

✅ Exponential backoff detected (50ms → 200ms → 400ms)
⚠️  No message queuing detected - 3 messages lost during offline period

Recommendations:
1. Implement client-side message queue for offline mode
2. Add retry mechanism with exponential backoff (already present)
3. Consider server-side message buffering for short disconnections
```

---

## Advanced Patterns

### Pattern: Multi-Service Health Dashboard

Monitor all Ziggie Cloud services in one session:

#### Claude Code Prompt

```
Using Chrome DevTools MCP, create a health status report for all Ziggie services:

For each service, navigate and check:
1. https://ziggie.cloud/api/ - API health endpoint responds
2. https://ziggie.cloud/sim/ - Page loads without console errors
3. https://ziggie.cloud/mcp/ - WebSocket connection succeeds
4. https://ziggie.cloud/n8n/ - Authentication works, workflow list loads
5. https://ziggie.cloud/flowise/ - Canvas renders, can create new workflow
6. https://ziggie.cloud/chat/ - Can send message, receive response

For each service, capture:
- Load time
- Console errors
- Failed network requests
- Performance metrics

Generate a summary dashboard report.
```

### Pattern: Cross-Service Integration Test

Test data flow across multiple services:

#### Claude Code Prompt

```
Using Chrome DevTools MCP, test end-to-end integration:
1. Navigate to https://ziggie.cloud/n8n/
2. Create a workflow that:
   - Triggers on webhook
   - Calls Ziggie API to fetch data
   - Sends data to Flowise for AI processing
3. Save the workflow and get webhook URL
4. Navigate to https://ziggie.cloud/api/docs
5. Use Swagger UI to POST to the webhook URL
6. Navigate back to n8n, verify workflow executed
7. Navigate to https://ziggie.cloud/flowise/
8. Verify the AI processing completed
9. Track total end-to-end time
10. Identify the slowest step in the pipeline
```

### Pattern: Security Audit

Use Chrome DevTools MCP for security checks:

#### Claude Code Prompt

```
Using Chrome DevTools MCP, perform security audit:
1. Navigate to https://ziggie.cloud/chat/
2. Check for security best practices:
   - HTTPS enforced (no mixed content warnings)
   - Security headers present:
     * Content-Security-Policy
     * X-Frame-Options
     * X-Content-Type-Options
     * Strict-Transport-Security
   - No sensitive data in localStorage/sessionStorage
   - Authentication tokens stored securely (httpOnly cookies)
   - No API keys exposed in client-side code
3. Test for common vulnerabilities:
   - XSS: Attempt to inject <script> in message input
   - CSRF: Check for CSRF token in forms
   - Clickjacking: Verify X-Frame-Options header
4. Generate security report with findings
```

---

## Example Prompts for Claude Code

### Debugging Session Prompts

#### 1. Diagnose Slow Page Load

```
I'm experiencing slow load times on https://ziggie.cloud/flowise/. Using Chrome DevTools MCP, please:

1. Navigate to the page
2. Record a performance trace
3. Identify the top 3 performance bottlenecks:
   - Long tasks blocking the main thread
   - Large JavaScript bundles
   - Slow network requests
4. Provide specific optimization recommendations with before/after metrics
```

#### 2. Debug API Integration Issue

```
My frontend at https://ziggie.cloud/chat/ is failing to connect to the API. Using Chrome DevTools MCP:

1. Navigate to the chat interface
2. Monitor network requests when I send a message
3. Check for:
   - CORS errors
   - 401/403 authentication failures
   - Malformed request payloads
   - Timeout issues
4. Show me the exact request/response headers
5. Suggest fixes for any issues found
```

#### 3. Validate n8n Workflow Execution

```
I have an n8n workflow at https://ziggie.cloud/n8n/ that sometimes fails silently. Using Chrome DevTools MCP:

1. Navigate to the workflow editor
2. Execute the "Data Pipeline" workflow
3. Monitor:
   - Console errors during execution
   - Network requests to external APIs
   - WebSocket messages between UI and backend
4. Capture screenshots of each node's execution status
5. Identify which node is failing and why
```

### Testing Session Prompts

#### 4. Cross-Browser Layout Verification

```
Using Chrome DevTools MCP, verify that https://ziggie.cloud/sim/ renders correctly at different viewport sizes:

1. Test at: 320px, 768px, 1024px, 1920px widths
2. For each size, take screenshots of:
   - Homepage
   - Simulation detail page
   - Settings modal
3. Check for:
   - Horizontal scroll (should not exist)
   - Overlapping elements
   - Truncated text
4. Report any layout issues with screenshots
```

#### 5. Performance Regression Test

```
I just deployed a new version of Flowise. Using Chrome DevTools MCP:

1. Navigate to https://ziggie.cloud/flowise/
2. Measure Core Web Vitals for the homepage
3. Open a workflow and measure:
   - Time to interactive
   - First contentful paint
   - Largest contentful paint
4. Compare with baseline metrics: LCP=1.8s, FCP=0.9s, TTI=2.5s
5. Flag any regressions >10%
6. Provide actionable recommendations if regressions detected
```

### Monitoring Session Prompts

#### 6. Real-Time Error Monitoring

```
Using Chrome DevTools MCP, monitor https://ziggie.cloud/chat/ for errors over a 10-minute session:

1. Navigate to the chat interface
2. Simulate realistic user behavior:
   - Send 20 messages
   - Switch between 3 conversations
   - Upload an image
   - Change settings
3. Monitor console for:
   - JavaScript errors
   - Network failures
   - React warnings
4. Capture and report all unique errors with:
   - Error message and stack trace
   - Steps to reproduce
   - Screenshot of UI state when error occurred
```

#### 7. WebSocket Connection Health

```
Using Chrome DevTools MCP, monitor WebSocket stability for https://ziggie.cloud/mcp/:

1. Navigate to a page using the MCP Gateway
2. Monitor the WebSocket connection for 15 minutes
3. Measure:
   - Connection uptime
   - Number of disconnections/reconnections
   - Average message round-trip latency
   - Peak latency
4. Alert if:
   - Connection drops more than 2 times
   - Average latency exceeds 200ms
   - Any messages fail to receive response within 5s
```

### Analysis Session Prompts

#### 8. Bundle Size Analysis

```
Using Chrome DevTools MCP, analyze JavaScript bundle size for https://ziggie.cloud/flowise/:

1. Navigate to the page
2. List all JavaScript resources loaded
3. For each bundle:
   - File size (compressed and uncompressed)
   - Load time
   - Coverage (% of code executed)
4. Identify:
   - Largest bundles (>500KB)
   - Low coverage bundles (<50% used)
5. Recommend code splitting or lazy loading strategies
```

#### 9. API Response Time Audit

```
Using Chrome DevTools MCP, audit API performance for Ziggie API:

1. Navigate to https://ziggie.cloud/api/docs
2. Test these endpoints:
   - GET /users (list)
   - GET /users/{id} (detail)
   - POST /users (create)
   - PUT /users/{id} (update)
   - DELETE /users/{id} (delete)
3. For each endpoint, measure:
   - Time to first byte (TTFB)
   - Total response time
   - Response size
4. Identify the slowest endpoint
5. Suggest optimizations (caching, pagination, query optimization)
```

### Automation Session Prompts

#### 10. Automated Smoke Test Suite

```
Using Chrome DevTools MCP, run automated smoke tests for all Ziggie services:

1. Test Ziggie API:
   - Health check returns 200
   - Authentication flow works
   - Can create, read, update, delete a test resource

2. Test Sim Studio:
   - Page loads without errors
   - Can create new simulation
   - Simulation runs successfully

3. Test n8n:
   - Can authenticate
   - Can create workflow
   - Can execute workflow

4. Test Flowise:
   - Canvas loads
   - Can create new chatflow
   - Can send test message

5. Test Open WebUI:
   - Chat interface loads
   - Can send message
   - Receives AI response

Generate a pass/fail report with screenshots for any failures.
```

---

## Best Practices

### 1. Use Headless Mode for CI/CD

```json
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "npx",
      "args": ["-y", "chrome-devtools-mcp@latest", "--headless"]
    }
  }
}
```

### 2. Set Explicit Timeouts

Always specify timeouts in prompts to prevent hanging:

```
wait_for(selector=".loaded", timeout=10000)  // 10 seconds
```

### 3. Isolated Browser Contexts for Security

Use `--isolated=true` flag when testing with sensitive data:

```bash
npx chrome-devtools-mcp@latest --isolated=true
```

### 4. Screenshot on Error

Always request screenshots when errors occur for debugging:

```
If any step fails, take a screenshot of the error state before reporting.
```

### 5. Measure Baseline First

Before optimization work, establish baseline metrics:

```
1. Run performance trace on current version
2. Save metrics to baseline.json
3. Make changes
4. Run trace again
5. Compare with baseline
```

### 6. Use Performance Budget

Define performance budgets in CI:

```javascript
const PERFORMANCE_BUDGET = {
  lcp: 2500,      // Max 2.5s
  fid: 100,       // Max 100ms
  cls: 0.1,       // Max 0.1
  ttfb: 800,      // Max 800ms
  bundleSize: 500000  // Max 500KB
};
```

### 7. Combine with Other MCP Servers

Leverage multiple MCP servers for comprehensive testing:

```json
{
  "mcpServers": {
    "chrome-devtools": { "command": "npx", "args": ["-y", "chrome-devtools-mcp@latest"] },
    "filesystem": { "command": "npx", "args": ["-y", "@modelcontextprotocol/server-filesystem"] },
    "database": { "command": "python", "args": ["db-mcp-server.py"] }
  }
}
```

**Combined workflow**:
1. Chrome DevTools MCP → Test frontend
2. Database MCP → Verify data persistence
3. Filesystem MCP → Check log files for errors

---

## Limitations & Workarounds

### Limitation 1: Chrome-Only

**Issue**: Chrome DevTools MCP only works with Chrome/Chromium browsers.

**Workaround**: For cross-browser testing, use [Playwright MCP](https://github.com/executeautomation/playwright-mcp-server) alongside Chrome DevTools MCP:

```json
{
  "mcpServers": {
    "chrome-devtools": { "command": "npx", "args": ["-y", "chrome-devtools-mcp@latest"] },
    "playwright": { "command": "npx", "args": ["-y", "playwright-mcp"] }
  }
}
```

### Limitation 2: WebSocket Frame Inspection

**Issue**: Chrome DevTools MCP doesn't provide direct access to WebSocket frame payloads.

**Workaround**: Use `evaluate_script` to tap into WebSocket events:

```javascript
evaluate_script("""
  const originalWebSocket = window.WebSocket;
  const messageLog = [];

  window.WebSocket = function(...args) {
    const ws = new originalWebSocket(...args);

    ws.addEventListener('message', (event) => {
      messageLog.push({
        type: 'received',
        data: event.data,
        timestamp: Date.now()
      });
      console.log('[WS RX]', event.data);
    });

    const originalSend = ws.send;
    ws.send = function(data) {
      messageLog.push({
        type: 'sent',
        data,
        timestamp: Date.now()
      });
      console.log('[WS TX]', data);
      return originalSend.call(this, data);
    };

    return ws;
  };
""")

// Then use list_console_messages() to see WebSocket traffic
```

### Limitation 3: No Backend Access

**Issue**: Chrome DevTools MCP operates at the browser level, cannot access server logs or databases.

**Workaround**: Combine with backend MCP servers:

```
# Terminal 1: Run backend MCP server
python ziggie-api-mcp-server.py

# Terminal 2: Use Claude Code with both MCP servers
# Claude can now correlate frontend errors with backend logs
```

---

## Troubleshooting

### Issue: Chrome DevTools MCP Not Connecting

**Symptoms**: MCP tools not showing up in Claude Code.

**Solutions**:

1. Check Node.js version:
   ```bash
   node --version  # Must be 22+
   ```

2. Verify Chrome is installed:
   ```bash
   google-chrome --version  # Linux
   # or
   "C:\Program Files\Google\Chrome\Application\chrome.exe" --version  # Windows
   ```

3. Test manual connection:
   ```bash
   npx chrome-devtools-mcp@latest
   # Should open Chrome and show "MCP Server Ready"
   ```

4. Check MCP config syntax:
   ```json
   {
     "mcpServers": {
       "chrome-devtools": {
         "command": "npx",
         "args": ["-y", "chrome-devtools-mcp@latest"]
       }
     }
   }
   ```

### Issue: Timeout Errors

**Symptoms**: `wait_for` commands timing out.

**Solutions**:

1. Increase timeout:
   ```
   wait_for(selector=".slow-loading-element", timeout=30000)
   ```

2. Use network idle instead of specific selector:
   ```
   navigate_page(url="...", wait_until="networkidle")
   ```

3. Check for infinite loaders (never resolves):
   ```
   // Replace wait_for with periodic check
   evaluate_script("""
     return new Promise((resolve, reject) => {
       let attempts = 0;
       const interval = setInterval(() => {
         if (document.querySelector('.loaded')) {
           clearInterval(interval);
           resolve(true);
         }
         if (++attempts > 50) {  // 5 seconds max
           clearInterval(interval);
           reject('Element not found');
         }
       }, 100);
     })
   """)
   ```

### Issue: Screenshots Not Capturing Full Page

**Symptoms**: Screenshots only show viewport, not full page.

**Solution**:

Use `take_snapshot` (DOM snapshot) instead of `take_screenshot`, or scroll before capturing:

```python
# Scroll to bottom
evaluate_script("window.scrollTo(0, document.body.scrollHeight)")
wait_for(timeout=1000)
take_screenshot(filename="bottom.png")

# Scroll back to top
evaluate_script("window.scrollTo(0, 0)")
wait_for(timeout=1000)
take_screenshot(filename="top.png")
```

---

## Resources

### Official Documentation

- [Chrome DevTools MCP - Official Blog Post](https://developer.chrome.com/blog/chrome-devtools-mcp)
- [GitHub Repository - ChromeDevTools/chrome-devtools-mcp](https://github.com/ChromeDevTools/chrome-devtools-mcp/)
- [Chrome DevTools Protocol Documentation](https://chromedevtools.github.io/devtools-protocol/)

### Integration Guides

- [Chrome DevTools MCP: Complete Guide 2025](https://vladimirsiedykh.com/blog/chrome-devtools-mcp-ai-browser-debugging-complete-guide-2025)
- [Chrome DevTools MCP: Bridging AI Assistants with Browser Reality](https://orchestrator.dev/blog/2025-12-13-chrome-devtools-mcp-article/)
- [Performance Debugging With Chrome DevTools MCP](https://www.debugbear.com/blog/chrome-devtools-mcp-performance-debugging)

### Service-Specific Resources

- [n8n: Monitor & Debug Workflows with Claude AI](https://n8n.io/workflows/10779-monitor-and-debug-n8n-workflows-with-claude-ai-assistant-and-mcp-server/)
- [Flowise: Observability and Tracing with Langfuse](https://langfuse.com/docs/integrations/flowise)
- [FastAPI CORS Documentation](https://fastapi.tiangolo.com/tutorial/cors/)

### Additional Tools

- [Playwright MCP Server](https://github.com/executeautomation/playwright-mcp-server) - Cross-browser testing
- [Langfuse](https://langfuse.com/) - LLM observability for Flowise
- [n8n Copilot Chrome Extension](https://chromewebstore.google.com/detail/n8n-copilot-generate-and/jkncjfiaifpdoemifnelilkikhbjfbhd) - AI workflow generation

---

## Conclusion

Chrome DevTools MCP transforms AI-assisted debugging from static code analysis to **dynamic, real-time browser inspection**. For Ziggie Cloud services, this enables:

1. **FastAPI Backend Debugging**: CORS issues, API performance, request validation
2. **Real-Time Application Testing**: n8n workflow monitoring, WebSocket debugging
3. **SPA Performance Profiling**: Flowise/Open WebUI optimization, Core Web Vitals
4. **Visual Regression Testing**: UI consistency across deployments
5. **CI/CD Integration**: Automated performance gates, pre-deployment smoke tests
6. **WebSocket Protocol Debugging**: MCP Gateway JSON-RPC validation

By combining Chrome DevTools MCP with other MCP servers (filesystem, database, n8n), you create a **comprehensive testing and debugging ecosystem** where AI assistants have full visibility into your application stack.

**Next Steps**:
1. Install Chrome DevTools MCP: `claude mcp add chrome-devtools npx chrome-devtools-mcp@latest`
2. Test a simple prompt: "Navigate to https://ziggie.cloud/api/ and check the health endpoint"
3. Integrate into CI/CD pipeline for automated performance regression detection
4. Combine with service-specific MCP servers for deeper integration

---

**Sources**:
- [Chrome DevTools MCP - Official Blog](https://developer.chrome.com/blog/chrome-devtools-mcp)
- [GitHub - ChromeDevTools/chrome-devtools-mcp](https://github.com/ChromeDevTools/chrome-devtools-mcp/)
- [Chrome DevTools MCP Guide 2025](https://vladimirsiedykh.com/blog/chrome-devtools-mcp-ai-browser-debugging-complete-guide-2025)
- [Orchestrator.dev - Chrome DevTools MCP Article](https://orchestrator.dev/blog/2025-12-13-chrome-devtools-mcp-article/)
- [Performance Debugging With Chrome DevTools MCP](https://www.debugbear.com/blog/chrome-devtools-mcp-performance-debugging)
- [FastAPI CORS Documentation](https://fastapi.tiangolo.com/tutorial/cors/)
- [n8n Workflow Debugging Guide](https://cyberincomeinnovators.com/mastering-n8n-workflow-debugging-from-common-errors-to-resilient-ai-automations)
- [n8n Claude AI Integration](https://n8n.io/workflows/10779-monitor-and-debug-n8n-workflows-with-claude-ai-assistant-and-mcp-server/)
- [Flowise Langfuse Integration](https://langfuse.com/docs/integrations/flowise)
- [Chrome DevTools Network Inspection](https://developer.chrome.com/docs/devtools/network)
