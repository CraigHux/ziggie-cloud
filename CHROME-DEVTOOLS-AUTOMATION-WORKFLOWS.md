# Chrome DevTools MCP Automation Workflows

> **Complete Guide to Automated Testing, Performance Monitoring, Visual Regression, Security Scanning, and Accessibility Testing**
>
> **Last Updated**: 2025-12-23
> **Source**: Chrome DevTools Protocol (CDP) + Chrome DevTools MCP (2025 Public Preview)

---

## Table of Contents

1. [Introduction](#introduction)
2. [Workflow 1: Automated E2E Testing with AI](#workflow-1-automated-e2e-testing-with-ai)
3. [Workflow 2: Continuous Performance Monitoring](#workflow-2-continuous-performance-monitoring)
4. [Workflow 3: Visual Regression Testing](#workflow-3-visual-regression-testing)
5. [Workflow 4: Security Scanning (XSS, Console Errors)](#workflow-4-security-scanning-xss-console-errors)
6. [Workflow 5: Accessibility Testing](#workflow-5-accessibility-testing)
7. [n8n Integration Patterns](#n8n-integration-patterns)
8. [Reporting and Alerting](#reporting-and-alerting)
9. [CI/CD Integration](#cicd-integration)
10. [Best Practices](#best-practices)

---

## Introduction

### What is Chrome DevTools MCP?

Released in **public preview by Google's Chrome DevTools team on September 23, 2025**, [Chrome DevTools MCP](https://github.com/ChromeDevTools/chrome-devtools-mcp/) is an official Model Context Protocol server that connects AI assistants directly to Chrome's debugging infrastructure.

**Key Capabilities**:
- Launch browsers and control via Chrome DevTools Protocol (CDP)
- Inspect network requests, DOM, and CSS
- Record performance traces and analyze Core Web Vitals
- Capture screenshots, console logs, and accessibility trees
- Execute JavaScript and automate user interactions
- Iterate on fixes using real runtime data

**27 Professional-Grade Tools** across 6 categories:
1. **Navigation**: navigate_page, new_page, close_page, wait_for
2. **Input**: click, fill, drag, hover, keyboard actions
3. **Emulation**: device emulation, geolocation, network throttling
4. **Performance**: trace recording, Core Web Vitals, metrics analysis
5. **Network**: request inspection, HAR capture, response mocking
6. **Debugging**: console messages, script evaluation, DOM inspection

### Chrome DevTools MCP vs Playwright MCP

| Dimension | Chrome DevTools MCP | Playwright MCP |
|-----------|---------------------|----------------|
| **Use Case** | Developer debugging in Chrome | QA testing across browsers |
| **Browser Support** | Chrome/Chromium only | Chrome, Firefox, Safari, Edge |
| **Depth** | Full DevTools access (CDP) | High-level automation API |
| **Performance** | Native performance traces | Basic metrics |
| **Accessibility** | Full a11y tree inspection | Basic a11y checks |
| **Best For** | AI acts like developer | AI acts like QA engineer |

**Rule of Thumb**: Use **Chrome DevTools MCP** when you need AI to think like a developer debugging in Chrome's inspector. Use **Playwright MCP** for cross-browser QA testing.

---

## Workflow 1: Automated E2E Testing with AI

### Overview

AI agents run user flows, screenshot failures, and iterate on fixes using real runtime data. According to [Chrome DevTools MCP documentation](https://orchestrator.dev/blog/2025-12-13-chrome-devtools-mcp-article/), this approach **beats Playwright for agentic speed** because the AI can inspect DOMs, trace performance, click buttons, and debug in real-time.

### Step-by-Step Workflow

#### Phase 1: Setup and Navigation

1. **Launch Chrome with DevTools MCP**
   ```bash
   # Ensure chrome-devtools-mcp server is running
   # In Claude Desktop config (claude_desktop_config.json):
   {
     "mcpServers": {
       "chrome-devtools": {
         "command": "npx",
         "args": ["-y", "@executeautomation/chrome-devtools-mcp"]
       }
     }
   }
   ```

2. **Navigate to Application**
   ```typescript
   // Claude Code prompt:
   "Use chrome-devtools-mcp to navigate to https://example.com/app and wait for page load"

   // Behind the scenes (CDP):
   await navigate_page({
     url: "https://example.com/app",
     wait_until: "networkidle"
   })
   ```

#### Phase 2: Test Execution

3. **Execute User Flow**
   ```typescript
   // Claude Code prompt:
   "Login with email 'test@example.com' and password 'test123', then navigate to dashboard"

   // Behind the scenes:
   await fill({ selector: "#email", value: "test@example.com" })
   await fill({ selector: "#password", value: "test123" })
   await click({ selector: "button[type='submit']" })
   await wait_for({ selector: ".dashboard-container", timeout: 5000 })
   ```

4. **Validate Expected State**
   ```typescript
   // Claude Code prompt:
   "Take a snapshot and verify the dashboard shows user profile with name 'Test User'"

   // Behind the scenes:
   const snapshot = await take_snapshot({ verbose: true })
   // AI analyzes snapshot.accessibility_tree to verify content
   ```

5. **Capture Failures**
   ```typescript
   // Claude Code prompt:
   "If login fails, take a screenshot and capture console errors"

   // Behind the scenes:
   const screenshot = await take_screenshot({ format: "png" })
   const consoleMessages = await list_console_messages()
   const networkErrors = await list_network_requests({ failed_only: true })
   ```

#### Phase 3: AI-Driven Debugging

6. **Analyze and Fix**
   ```typescript
   // Claude Code prompt:
   "Analyze the failure - check console errors, network requests, and DOM state. Suggest fixes."

   // AI reviews:
   // - consoleMessages for JavaScript errors
   // - networkErrors for failed API calls
   // - DOM snapshot for missing elements
   // - Screenshots for visual issues

   // AI suggests code fixes and iterates
   ```

### Example Claude Code Prompts

#### Prompt 1: Basic E2E Test
```
Use chrome-devtools-mcp to test the login flow:
1. Navigate to https://myapp.com/login
2. Fill email field with "test@example.com"
3. Fill password field with "password123"
4. Click the "Login" button
5. Wait for redirect to dashboard
6. Take a snapshot and verify the user's name appears as "Test User"
7. If any step fails, capture screenshot + console errors and report
```

#### Prompt 2: Form Validation Test
```
Test form validation on https://myapp.com/signup:
1. Navigate to signup page
2. Try submitting empty form
3. Verify error messages appear
4. Fill only email field
5. Submit and verify password validation error
6. Fill invalid email
7. Verify email format error
8. Take screenshots at each validation state
9. Report all validation messages found
```

#### Prompt 3: Shopping Cart Flow
```
Test e-commerce checkout flow on https://shop.example.com:
1. Navigate to product page
2. Add 3 items to cart
3. Navigate to cart
4. Verify cart total is correct
5. Click checkout
6. Fill shipping form
7. Select payment method
8. Complete order
9. At each step: take screenshot, verify page state, capture network requests
10. If any step fails, analyze console errors and suggest fixes
```

### Integration with Test Frameworks

#### Pattern 1: Claude as Test Case Generator
```typescript
// Prompt: "Generate Playwright test cases for the login flow"
// Claude generates:

import { test, expect } from '@playwright/test'

test.describe('Login Flow', () => {
  test('successful login redirects to dashboard', async ({ page }) => {
    await page.goto('https://myapp.com/login')
    await page.fill('#email', 'test@example.com')
    await page.fill('#password', 'password123')
    await page.click('button[type="submit"]')
    await page.waitForURL('**/dashboard')
    await expect(page.locator('.user-name')).toHaveText('Test User')
  })

  test('invalid credentials show error', async ({ page }) => {
    await page.goto('https://myapp.com/login')
    await page.fill('#email', 'wrong@example.com')
    await page.fill('#password', 'wrong')
    await page.click('button[type="submit"]')
    await expect(page.locator('.error-message')).toBeVisible()
  })
})
```

#### Pattern 2: Claude as Test Debugger
```typescript
// When Playwright test fails:
// 1. Share error logs with Claude
// 2. Claude uses chrome-devtools-mcp to reproduce issue
// 3. Claude inspects DOM, console, network
// 4. Claude suggests fix

// Example:
"This Playwright test is failing with 'Element not found: .user-name'.
Use chrome-devtools-mcp to navigate to the dashboard and inspect the DOM.
Find the actual selector for the user's name element."
```

### Reporting

**Test Report Structure** (JSON):
```json
{
  "test_suite": "Login Flow E2E",
  "timestamp": "2025-12-23T10:30:00Z",
  "results": [
    {
      "test_name": "Successful Login",
      "status": "PASSED",
      "duration_ms": 2341,
      "steps": [
        { "action": "navigate", "url": "https://myapp.com/login", "status": "OK" },
        { "action": "fill", "selector": "#email", "status": "OK" },
        { "action": "click", "selector": "button[type='submit']", "status": "OK" },
        { "action": "verify", "expected": "Dashboard visible", "status": "OK" }
      ],
      "screenshots": ["login_success.png"],
      "console_errors": 0,
      "network_errors": 0
    },
    {
      "test_name": "Invalid Credentials",
      "status": "FAILED",
      "duration_ms": 1823,
      "error": "Expected error message not found",
      "screenshots": ["login_fail.png"],
      "console_errors": ["TypeError: Cannot read property 'message' of undefined"],
      "network_errors": [],
      "ai_suggestion": "Error message element selector changed from '.error' to '.error-message'"
    }
  ],
  "summary": {
    "total": 2,
    "passed": 1,
    "failed": 1,
    "pass_rate": "50%"
  }
}
```

---

## Workflow 2: Continuous Performance Monitoring

### Overview

Automated performance testing detects regressions that manual testing misses. [Chrome DevTools MCP](https://docs.continue.dev/guides/chrome-devtools-mcp-performance) provides continuous, comprehensive performance monitoring that catches regressions early and provides actionable optimization insights.

### Step-by-Step Workflow

#### Phase 1: Baseline Establishment

1. **Record Baseline Performance Trace**
   ```typescript
   // Claude Code prompt:
   "Navigate to https://myapp.com and record a performance trace for 10 seconds. Report Core Web Vitals."

   // Behind the scenes:
   await navigate_page({ url: "https://myapp.com" })
   await start_trace()
   await wait_for({ timeout: 10000 })
   const trace = await stop_trace()

   // AI extracts metrics:
   // - LCP (Largest Contentful Paint)
   // - FID/INP (Interaction to Next Paint)
   // - CLS (Cumulative Layout Shift)
   // - TTFB (Time to First Byte)
   ```

2. **Define Performance Budgets**
   ```json
   {
     "budgets": {
       "LCP": { "max": 2500, "unit": "ms" },
       "INP": { "max": 200, "unit": "ms" },
       "CLS": { "max": 0.1, "unit": "score" },
       "TTFB": { "max": 800, "unit": "ms" },
       "Total Page Size": { "max": 2048, "unit": "KB" },
       "JavaScript Size": { "max": 512, "unit": "KB" }
     }
   }
   ```

#### Phase 2: Continuous Monitoring

3. **Scheduled Performance Checks**
   ```typescript
   // Claude Code prompt (run via cron/n8n every 6 hours):
   "Run performance test on https://myapp.com:
   1. Record trace for homepage, dashboard, and checkout pages
   2. Extract Core Web Vitals for each page
   3. Compare against budgets defined in performance-budgets.json
   4. If any metric exceeds budget, capture detailed trace and alert
   5. Generate performance report"
   ```

4. **Network Performance Analysis**
   ```typescript
   // Claude Code prompt:
   "Analyze network performance for https://myapp.com:
   1. Navigate to page
   2. Capture all network requests
   3. Identify slow requests (>1s)
   4. Check for large resources (>500KB)
   5. Verify compression is enabled
   6. Report waterfall chart insights"

   // Behind the scenes:
   const requests = await list_network_requests()
   const slowRequests = requests.filter(r => r.duration > 1000)
   const largeResources = requests.filter(r => r.size > 500 * 1024)
   const uncompressed = requests.filter(r => !r.headers['content-encoding'])
   ```

#### Phase 3: Regression Detection

5. **Compare with Baseline**
   ```typescript
   // AI compares current metrics with baseline:
   const regression = {
     "LCP": { baseline: 1800, current: 3200, delta: "+77%", status: "REGRESSION" },
     "INP": { baseline: 120, current: 110, delta: "-8%", status: "IMPROVED" },
     "CLS": { baseline: 0.05, current: 0.18, delta: "+260%", status: "REGRESSION" }
   }

   // If regression detected:
   // 1. Capture detailed trace
   // 2. Analyze flamegraph for bottlenecks
   // 3. Identify specific functions causing slowdown
   // 4. Generate actionable report
   ```

6. **Automated Performance Profiling**
   ```typescript
   // Claude Code prompt:
   "Performance regression detected in LCP (1800ms → 3200ms).
   Record detailed trace, analyze the flamegraph, and identify the bottleneck."

   // AI analyzes trace:
   // - Long tasks blocking main thread
   // - Large layout shifts
   // - Render-blocking resources
   // - Slow JavaScript execution
   ```

### Example Claude Code Prompts

#### Prompt 1: Core Web Vitals Report
```
Generate a Core Web Vitals report for https://myapp.com:
1. Navigate to homepage
2. Record performance trace for 15 seconds
3. Extract LCP, INP, CLS, TTFB
4. Compare against these budgets:
   - LCP < 2.5s
   - INP < 200ms
   - CLS < 0.1
   - TTFB < 800ms
5. If any budget is exceeded, provide optimization recommendations
6. Generate a markdown report with before/after comparison
```

#### Prompt 2: Page Load Waterfall Analysis
```
Analyze page load performance for https://myapp.com/dashboard:
1. Navigate to page with network recording
2. Capture all network requests
3. Generate waterfall analysis:
   - Total page load time
   - DNS lookup time
   - Time to first byte (TTFB)
   - DOM content loaded
   - Load event fired
4. Identify top 5 slowest resources
5. Check for render-blocking CSS/JS
6. Recommend performance optimizations
```

#### Prompt 3: JavaScript Performance Analysis
```
Profile JavaScript performance on https://myapp.com:
1. Navigate to page
2. Record CPU profile for 10 seconds while interacting with the page
3. Identify long tasks (>50ms)
4. Analyze flamegraph for hot functions
5. Report top 10 most expensive functions
6. Suggest code-level optimizations
```

### Performance Budget Validation Script

```typescript
// performance-budget-checker.ts
import fs from 'fs'

interface PerformanceBudgets {
  budgets: Record<string, { max: number; unit: string }>
}

interface PerformanceMetrics {
  LCP: number
  INP: number
  CLS: number
  TTFB: number
}

async function validatePerformanceBudgets(
  metrics: PerformanceMetrics,
  budgets: PerformanceBudgets
): Promise<{ passed: boolean; violations: string[] }> {
  const violations: string[] = []

  for (const [metric, value] of Object.entries(metrics)) {
    const budget = budgets.budgets[metric]
    if (!budget) continue

    if (value > budget.max) {
      violations.push(
        `${metric}: ${value}${budget.unit} exceeds budget of ${budget.max}${budget.unit}`
      )
    }
  }

  return {
    passed: violations.length === 0,
    violations
  }
}

// Claude Code prompt:
"Run this performance budget checker after recording trace. If any budget is exceeded, exit with code 1 for CI/CD failure."
```

### CI/CD Integration (GitHub Actions)

```yaml
# .github/workflows/performance-check.yml
name: Performance Check

on:
  push:
    branches: [main]
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours

jobs:
  performance:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '20'

      - name: Install Chrome DevTools MCP
        run: npm install -g @executeautomation/chrome-devtools-mcp

      - name: Run Performance Tests
        run: |
          # Use Claude Code with chrome-devtools-mcp to:
          # 1. Navigate to staging site
          # 2. Record performance trace
          # 3. Validate against budgets
          # 4. Generate report
          npx claude-code run performance-test.md

      - name: Check Performance Budgets
        run: node performance-budget-checker.js

      - name: Upload Performance Report
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: performance-report
          path: performance-report.json

      - name: Comment PR with Results
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v6
        with:
          script: |
            const report = require('./performance-report.json')
            const comment = `## Performance Report\n\n${report.summary}`
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: comment
            })
```

### Reporting

**Performance Report Structure** (JSON):
```json
{
  "url": "https://myapp.com",
  "timestamp": "2025-12-23T10:30:00Z",
  "core_web_vitals": {
    "LCP": { "value": 2100, "unit": "ms", "rating": "GOOD", "budget": 2500, "status": "PASS" },
    "INP": { "value": 150, "unit": "ms", "rating": "GOOD", "budget": 200, "status": "PASS" },
    "CLS": { "value": 0.08, "unit": "score", "rating": "GOOD", "budget": 0.1, "status": "PASS" },
    "TTFB": { "value": 650, "unit": "ms", "rating": "GOOD", "budget": 800, "status": "PASS" }
  },
  "network_analysis": {
    "total_requests": 42,
    "total_size_kb": 1823,
    "total_duration_ms": 3421,
    "slow_requests": [
      { "url": "https://cdn.example.com/bundle.js", "duration_ms": 1823, "size_kb": 512 }
    ],
    "large_resources": [
      { "url": "https://cdn.example.com/image.jpg", "size_kb": 847, "type": "image" }
    ]
  },
  "recommendations": [
    "Compress bundle.js with gzip/brotli (potential savings: 384KB)",
    "Optimize image.jpg - reduce quality or use WebP format (potential savings: 623KB)",
    "Defer non-critical JavaScript to improve LCP"
  ],
  "regression_analysis": {
    "baseline_date": "2025-12-20T10:00:00Z",
    "changes": [
      { "metric": "LCP", "baseline": 1800, "current": 2100, "delta": "+16.7%", "status": "ACCEPTABLE" }
    ]
  }
}
```

---

## Workflow 3: Visual Regression Testing

### Overview

[Visual regression testing](https://vladimirsiedykh.com/blog/chrome-devtools-mcp-ai-browser-debugging-complete-guide-2025) captures and compares UI snapshots across commits to detect unintended visual changes. Chrome DevTools MCP provides screenshot and DOM snapshot utilities to support visual diffs.

### Step-by-Step Workflow

#### Phase 1: Baseline Screenshot Capture

1. **Capture Baseline Screenshots**
   ```typescript
   // Claude Code prompt:
   "Capture baseline screenshots for visual regression testing:
   1. Navigate to these pages: homepage, dashboard, profile, settings
   2. For each page:
      - Wait for page to fully load
      - Take full-page screenshot
      - Save as baseline-{page-name}.png
   3. Store screenshots in ./visual-baselines/ directory"

   // Behind the scenes:
   const pages = ['/', '/dashboard', '/profile', '/settings']

   for (const page of pages) {
     await navigate_page({ url: `https://myapp.com${page}` })
     await wait_for({ selector: 'body', timeout: 5000 })
     const screenshot = await take_screenshot({
       format: 'png',
       full_page: true
     })
     // Save to ./visual-baselines/${page.replace('/', '')}.png
   }
   ```

2. **Capture Responsive Screenshots**
   ```typescript
   // Claude Code prompt:
   "Capture responsive screenshots for mobile, tablet, desktop:
   1. Set viewport to 375x667 (mobile)
   2. Capture screenshots of all pages
   3. Set viewport to 768x1024 (tablet)
   4. Capture screenshots of all pages
   5. Set viewport to 1920x1080 (desktop)
   6. Capture screenshots of all pages
   7. Save as baseline-{page}-{device}.png"

   // Behind the scenes:
   const viewports = [
     { name: 'mobile', width: 375, height: 667 },
     { name: 'tablet', width: 768, height: 1024 },
     { name: 'desktop', width: 1920, height: 1080 }
   ]

   for (const viewport of viewports) {
     await set_viewport({ width: viewport.width, height: viewport.height })
     // Capture all pages...
   }
   ```

#### Phase 2: Regression Detection

3. **Capture Current Screenshots**
   ```typescript
   // Claude Code prompt (run on every commit/PR):
   "Capture current screenshots and compare with baseline:
   1. Navigate to all pages and capture screenshots
   2. Save as current-{page-name}.png
   3. Compare pixel-by-pixel with baseline screenshots
   4. If differences detected, generate diff image highlighting changes
   5. Report all visual changes detected"
   ```

4. **Pixel-Diff Comparison**
   ```typescript
   // Using pixelmatch library for comparison
   import pixelmatch from 'pixelmatch'
   import { PNG } from 'pngjs'
   import fs from 'fs'

   function compareScreenshots(baselinePath: string, currentPath: string): {
     mismatchedPixels: number
     diffPercentage: number
     diffImagePath: string
   } {
     const baseline = PNG.sync.read(fs.readFileSync(baselinePath))
     const current = PNG.sync.read(fs.readFileSync(currentPath))
     const { width, height } = baseline
     const diff = new PNG({ width, height })

     const mismatchedPixels = pixelmatch(
       baseline.data,
       current.data,
       diff.data,
       width,
       height,
       { threshold: 0.1 }  // 10% tolerance
     )

     const totalPixels = width * height
     const diffPercentage = (mismatchedPixels / totalPixels) * 100

     const diffImagePath = currentPath.replace('current-', 'diff-')
     fs.writeFileSync(diffImagePath, PNG.sync.write(diff))

     return { mismatchedPixels, diffPercentage, diffImagePath }
   }

   // Claude Code prompt:
   "Run pixel-diff comparison for all screenshots. If diff > 1%, flag as visual regression."
   ```

#### Phase 3: DOM Snapshot Comparison

5. **Capture DOM Snapshots**
   ```typescript
   // Claude Code prompt:
   "Capture DOM snapshot for structural comparison:
   1. Navigate to page
   2. Take snapshot with verbose=true to get full accessibility tree
   3. Extract all element roles, labels, and hierarchy
   4. Save as baseline-{page}-dom.json
   5. Compare current DOM snapshot with baseline
   6. Report structural changes (added/removed/modified elements)"

   // Behind the scenes:
   const snapshot = await take_snapshot({ verbose: true })
   const domStructure = extractDOMStructure(snapshot.accessibility_tree)

   // Compare with baseline:
   const changes = compareDOM(baselineDOM, currentDOM)
   // changes = { added: [...], removed: [...], modified: [...] }
   ```

#### Phase 4: Visual Approval Workflow

6. **Review and Approve Changes**
   ```typescript
   // When visual changes detected:
   // 1. Generate visual regression report
   // 2. Display side-by-side comparison (baseline vs current vs diff)
   // 3. Allow developer to approve/reject changes
   // 4. If approved, update baseline screenshots

   // Claude Code prompt:
   "Visual changes detected in 3 pages. Generate comparison report with:
   1. Side-by-side baseline vs current screenshots
   2. Diff image highlighting changed pixels
   3. Percentage of pixels changed
   4. Ask: Should these changes be approved as new baseline?"
   ```

### Example Claude Code Prompts

#### Prompt 1: Initial Baseline Capture
```
Set up visual regression testing baseline:
1. Navigate to https://myapp.com
2. Capture screenshots for these pages:
   - Homepage (/)
   - Login (/login)
   - Dashboard (/dashboard)
   - Profile (/profile)
   - Settings (/settings)
3. For each page:
   - Wait for "networkidle" state
   - Take full-page screenshot
   - Save as ./visual-baselines/{page-name}.png
4. Also capture at mobile (375x667) and tablet (768x1024) viewports
5. Generate baseline manifest JSON with metadata
```

#### Prompt 2: Visual Regression Check
```
Run visual regression check for PR #123:
1. Capture current screenshots for all baseline pages
2. Compare each screenshot with baseline using pixelmatch
3. If diff > 0.5%, generate diff image and flag as regression
4. Generate HTML report with:
   - Side-by-side comparison (baseline, current, diff)
   - Diff percentage for each page
   - List of pages with changes
5. Save report as ./visual-regression-report.html
6. Exit with code 1 if any regressions detected
```

#### Prompt 3: Responsive Visual Testing
```
Test responsive design for https://myapp.com/dashboard:
1. Capture screenshots at these viewports:
   - Mobile: 375x667, 414x896 (iPhone)
   - Tablet: 768x1024, 1024x768 (iPad)
   - Desktop: 1920x1080, 2560x1440
2. For each viewport:
   - Check for layout issues (overflow, clipping)
   - Verify all interactive elements are accessible
   - Capture screenshot
3. Compare with responsive baselines
4. Report any layout breakpoints issues
```

### Integration with Vitest 4.0

[Vitest 4.0](https://www.infoq.com/news/2025/12/vitest-4-browser-mode/) includes built-in visual regression testing support:

```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    browser: {
      enabled: true,
      name: 'chromium',
      provider: 'playwright'
    }
  }
})

// visual-regression.test.ts
import { test, expect } from 'vitest'

test('homepage visual regression', async ({ page }) => {
  await page.goto('https://myapp.com')
  await expect(page).toHaveScreenshot('homepage.png', {
    maxDiffPixels: 100  // Allow 100 pixels difference
  })
})

test('responsive mobile layout', async ({ page }) => {
  await page.setViewportSize({ width: 375, height: 667 })
  await page.goto('https://myapp.com')
  await expect(page).toHaveScreenshot('homepage-mobile.png')
})
```

### CI/CD Integration

```yaml
# .github/workflows/visual-regression.yml
name: Visual Regression Testing

on:
  pull_request:
    branches: [main]

jobs:
  visual-regression:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0  # Fetch baseline screenshots from main

      - name: Checkout Baseline Screenshots
        run: |
          git checkout origin/main -- visual-baselines/

      - name: Install Dependencies
        run: |
          npm install -g @executeautomation/chrome-devtools-mcp
          npm install pixelmatch pngjs

      - name: Capture Current Screenshots
        run: |
          npx claude-code run visual-capture.md

      - name: Compare with Baseline
        id: compare
        run: |
          node visual-diff-checker.js
        continue-on-error: true

      - name: Upload Diff Images
        if: steps.compare.outcome == 'failure'
        uses: actions/upload-artifact@v3
        with:
          name: visual-diffs
          path: visual-diffs/

      - name: Comment PR with Visual Changes
        if: steps.compare.outcome == 'failure'
        uses: actions/github-script@v6
        with:
          script: |
            const report = require('./visual-regression-report.json')
            const comment = `## 🎨 Visual Regression Detected\n\n${report.summary}\n\nView diff images in the artifacts.`
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: comment
            })

      - name: Fail if Visual Regressions Detected
        if: steps.compare.outcome == 'failure'
        run: exit 1
```

### Reporting

**Visual Regression Report** (HTML):
```html
<!DOCTYPE html>
<html>
<head>
  <title>Visual Regression Report - PR #123</title>
  <style>
    .comparison { display: flex; gap: 20px; margin: 20px 0; }
    .screenshot { text-align: center; }
    .screenshot img { max-width: 400px; border: 1px solid #ccc; }
    .diff-high { background: #fee; }
    .diff-low { background: #efe; }
  </style>
</head>
<body>
  <h1>Visual Regression Report</h1>
  <p>Generated: 2025-12-23 10:30:00</p>
  <p>Commit: abc123def</p>

  <h2>Summary</h2>
  <ul>
    <li>Total Pages Tested: 5</li>
    <li>Pages with Changes: 2</li>
    <li>Pass Rate: 60%</li>
  </ul>

  <h2>Visual Changes Detected</h2>

  <div class="comparison diff-high">
    <div class="screenshot">
      <h3>Baseline</h3>
      <img src="baseline-dashboard.png" alt="Baseline">
    </div>
    <div class="screenshot">
      <h3>Current</h3>
      <img src="current-dashboard.png" alt="Current">
    </div>
    <div class="screenshot">
      <h3>Diff (2.3%)</h3>
      <img src="diff-dashboard.png" alt="Diff">
    </div>
  </div>

  <p><strong>Changes:</strong> Header background color changed from #ffffff to #f5f5f5</p>

  <!-- More comparisons... -->

</body>
</html>
```

---

## Workflow 4: Security Scanning (XSS, Console Errors)

### Overview

Chrome DevTools Protocol enables [automated security scanning](https://developer.chrome.com/blog/self-xss) including XSS detection, console error monitoring, and vulnerability assessment. This workflow focuses on detecting client-side security issues.

### Step-by-Step Workflow

#### Phase 1: Console Error Monitoring

1. **Capture Console Messages**
   ```typescript
   // Claude Code prompt:
   "Navigate to https://myapp.com and monitor console for errors:
   1. Navigate to page
   2. Capture all console messages (log, warn, error)
   3. Filter for JavaScript errors, failed network requests, CSP violations
   4. Report all security-related warnings
   5. Categorize by severity (critical, high, medium, low)"

   // Behind the scenes:
   await navigate_page({ url: "https://myapp.com" })
   const consoleMessages = await list_console_messages()

   const errors = consoleMessages.filter(m => m.level === 'error')
   const cspViolations = errors.filter(m => m.text.includes('Content Security Policy'))
   const xssWarnings = errors.filter(m => m.text.includes('unsafe-inline') || m.text.includes('eval'))
   ```

2. **Monitor Network Security Headers**
   ```typescript
   // Claude Code prompt:
   "Check security headers for all requests:
   1. Navigate to page and capture network traffic
   2. For each response, check for:
      - Content-Security-Policy
      - X-Frame-Options
      - X-Content-Type-Options
      - Strict-Transport-Security (HSTS)
      - X-XSS-Protection
   3. Flag missing or weak security headers
   4. Report all insecure resources (HTTP not HTTPS)"

   // Behind the scenes:
   const requests = await list_network_requests()
   const securityIssues = requests.map(req => ({
     url: req.url,
     missingHeaders: checkSecurityHeaders(req.response.headers),
     insecure: req.url.startsWith('http://')
   }))
   ```

#### Phase 2: XSS Detection

3. **Test for Reflected XSS**
   ```typescript
   // Claude Code prompt:
   "Test for reflected XSS vulnerabilities:
   1. Navigate to search page
   2. Inject test payloads into search field:
      - <script>alert('XSS')</script>
      - <img src=x onerror=alert('XSS')>
      - javascript:alert('XSS')
   3. Submit form
   4. Check if payload is reflected in page without sanitization
   5. Monitor console for script execution
   6. Report vulnerable input fields"

   // Behind the scenes:
   const payloads = [
     "<script>alert('XSS')</script>",
     "<img src=x onerror=alert('XSS')>",
     "javascript:alert('XSS')",
     "<svg onload=alert('XSS')>"
   ]

   for (const payload of payloads) {
     await fill({ selector: '#search', value: payload })
     await click({ selector: 'button[type="submit"]' })

     const pageContent = await evaluate_script({ script: 'document.body.innerHTML' })
     const reflected = pageContent.includes(payload)
     const sanitized = pageContent.includes('&lt;script&gt;')

     if (reflected && !sanitized) {
       // VULNERABILITY DETECTED!
     }
   }
   ```

4. **Test for DOM-Based XSS**
   ```typescript
   // Claude Code prompt:
   "Test for DOM-based XSS:
   1. Navigate to page with URL parameters
   2. Test payloads in URL parameters:
      - ?search=<script>alert('XSS')</script>
      - ?redirect=javascript:alert('XSS')
   3. Check if JavaScript executes from URL params
   4. Monitor document.location, document.referrer usage
   5. Report vulnerable parameter handling"

   // Behind the scenes:
   const urls = [
     "https://myapp.com?search=<script>alert('XSS')</script>",
     "https://myapp.com?redirect=javascript:alert('XSS')"
   ]

   for (const url of urls) {
     await navigate_page({ url })
     const consoleErrors = await list_console_messages()
     const scriptExecuted = consoleErrors.some(m => m.text.includes('XSS'))

     if (scriptExecuted) {
       // VULNERABILITY DETECTED!
     }
   }
   ```

#### Phase 3: Content Security Policy (CSP) Validation

5. **Validate CSP Configuration**
   ```typescript
   // Claude Code prompt:
   "Validate Content Security Policy:
   1. Navigate to page
   2. Extract CSP header from response
   3. Check for:
      - 'unsafe-inline' in script-src (HIGH RISK)
      - 'unsafe-eval' in script-src (HIGH RISK)
      - Missing default-src
      - Overly permissive * wildcards
   4. Report CSP weaknesses
   5. Suggest hardened CSP policy"

   // Behind the scenes:
   const requests = await list_network_requests()
   const mainRequest = requests.find(r => r.url === 'https://myapp.com')
   const csp = mainRequest.response.headers['content-security-policy']

   const weaknesses = []
   if (csp.includes("'unsafe-inline'")) {
     weaknesses.push("CRITICAL: 'unsafe-inline' allows inline scripts (XSS risk)")
   }
   if (csp.includes("'unsafe-eval'")) {
     weaknesses.push("HIGH: 'unsafe-eval' allows eval() (XSS risk)")
   }
   if (!csp.includes('default-src')) {
     weaknesses.push("MEDIUM: Missing default-src fallback")
   }
   ```

#### Phase 4: Third-Party Script Analysis

6. **Audit Third-Party Scripts**
   ```typescript
   // Claude Code prompt:
   "Audit all third-party scripts:
   1. Navigate to page
   2. Capture all script tags and network requests
   3. Identify external scripts (not from myapp.com)
   4. Check for:
      - Scripts loaded over HTTP (insecure)
      - Scripts from unknown domains
      - Scripts with integrity hashes (SRI)
   5. Report all third-party scripts with risk assessment"

   // Behind the scenes:
   const snapshot = await take_snapshot()
   const scripts = await evaluate_script({
     script: `Array.from(document.querySelectorAll('script[src]')).map(s => ({
       src: s.src,
       integrity: s.integrity,
       crossOrigin: s.crossOrigin
     }))`
   })

   const thirdPartyScripts = scripts.filter(s =>
     !s.src.includes('myapp.com')
   )

   const insecureScripts = thirdPartyScripts.filter(s =>
     s.src.startsWith('http://')
   )

   const scriptsWithoutSRI = thirdPartyScripts.filter(s =>
     !s.integrity
   )
   ```

### Example Claude Code Prompts

#### Prompt 1: Comprehensive Security Scan
```
Run a comprehensive security scan on https://myapp.com:
1. Console Error Detection:
   - Navigate to all major pages
   - Capture console errors, warnings, CSP violations
   - Report JavaScript errors that could expose vulnerabilities

2. Security Headers Check:
   - Validate CSP, X-Frame-Options, HSTS, X-Content-Type-Options
   - Flag missing or weak headers

3. XSS Testing:
   - Test search, login, comment forms with XSS payloads
   - Check for reflected and DOM-based XSS

4. Mixed Content Detection:
   - Identify HTTP resources on HTTPS pages
   - Report insecure resource loads

5. Third-Party Script Audit:
   - List all external scripts
   - Check for SRI (Subresource Integrity)
   - Identify scripts from unknown domains

6. Generate security report with:
   - Severity ratings (Critical, High, Medium, Low)
   - Actionable remediation steps
   - OWASP Top 10 alignment
```

#### Prompt 2: XSS Vulnerability Scan
```
Test for XSS vulnerabilities on https://myapp.com:
1. Identify all input fields:
   - Search boxes
   - Login forms
   - Comment/message forms
   - Profile edit fields

2. For each input, test these payloads:
   - <script>alert('XSS')</script>
   - <img src=x onerror=alert('XSS')>
   - <svg onload=alert('XSS')>
   - javascript:alert('XSS')
   - "><script>alert('XSS')</script>

3. For each payload:
   - Fill input field
   - Submit form
   - Check if payload appears unsanitized in DOM
   - Monitor console for script execution

4. Test URL parameters for DOM-based XSS
5. Generate vulnerability report with:
   - Vulnerable endpoints
   - Successful payloads
   - Proof-of-concept screenshots
   - Remediation recommendations
```

#### Prompt 3: CSP Hardening Recommendations
```
Analyze Content Security Policy for https://myapp.com:
1. Extract current CSP from response headers
2. Identify weaknesses:
   - 'unsafe-inline' or 'unsafe-eval' usage
   - Overly permissive wildcards (*)
   - Missing directives (default-src, script-src, style-src)

3. Analyze actual resource usage:
   - Capture all script, style, image, font, media sources
   - Identify inline scripts/styles that need hashes/nonces

4. Generate hardened CSP policy:
   - Remove 'unsafe-inline' with nonces
   - Whitelist specific trusted domains
   - Add default-src fallback

5. Provide implementation guide:
   - Suggested CSP header
   - Code changes needed for nonces
   - Testing checklist
```

### Security Scanning Tools Integration

#### Chrome DevTools Security Panel

```typescript
// Access Security panel data via CDP
const securityState = await page.evaluateHandle(() => {
  return {
    protocol: window.location.protocol,
    securityState: document.securityState,
    mixedContent: performance.getEntriesByType('resource')
      .filter(r => r.name.startsWith('http:'))
  }
})

// Claude analyzes security state and reports issues
```

#### Integration with OWASP ZAP

```yaml
# Combined workflow: Chrome DevTools MCP + OWASP ZAP
steps:
  - name: Dynamic Security Scan
    run: |
      # Use Chrome DevTools MCP to:
      # 1. Navigate and authenticate
      # 2. Record all navigation paths
      # 3. Export HAR file with all requests

      # Feed HAR to OWASP ZAP for deeper scanning
      docker run owasp/zap2docker-stable zap-baseline.py \
        -t https://myapp.com \
        -r zap-report.html
```

### CI/CD Integration

```yaml
# .github/workflows/security-scan.yml
name: Security Scan

on:
  push:
    branches: [main]
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Install Chrome DevTools MCP
        run: npm install -g @executeautomation/chrome-devtools-mcp

      - name: Run Security Scan
        run: |
          npx claude-code run security-scan.md

      - name: Check for Critical Issues
        id: check
        run: |
          CRITICAL=$(jq '.issues[] | select(.severity=="CRITICAL")' security-report.json | wc -l)
          if [ $CRITICAL -gt 0 ]; then
            echo "critical_found=true" >> $GITHUB_OUTPUT
          fi

      - name: Upload Security Report
        uses: actions/upload-artifact@v3
        with:
          name: security-report
          path: security-report.json

      - name: Create Security Issue
        if: steps.check.outputs.critical_found == 'true'
        uses: actions/github-script@v6
        with:
          script: |
            const report = require('./security-report.json')
            const criticalIssues = report.issues.filter(i => i.severity === 'CRITICAL')
            const body = `# 🚨 Critical Security Issues Detected\n\n${criticalIssues.map(i => `- ${i.description}`).join('\n')}`

            github.rest.issues.create({
              owner: context.repo.owner,
              repo: context.repo.repo,
              title: '🚨 Critical Security Vulnerabilities Detected',
              body: body,
              labels: ['security', 'critical']
            })

      - name: Fail if Critical Issues Found
        if: steps.check.outputs.critical_found == 'true'
        run: exit 1
```

### Reporting

**Security Report Structure** (JSON):
```json
{
  "scan_date": "2025-12-23T10:30:00Z",
  "url": "https://myapp.com",
  "summary": {
    "total_issues": 8,
    "critical": 2,
    "high": 3,
    "medium": 2,
    "low": 1
  },
  "issues": [
    {
      "id": "XSS-001",
      "severity": "CRITICAL",
      "category": "Cross-Site Scripting (XSS)",
      "description": "Reflected XSS in search parameter",
      "location": "https://myapp.com/search?q=<payload>",
      "payload": "<script>alert('XSS')</script>",
      "evidence": "Payload reflected unsanitized in <div class='search-results'>",
      "remediation": "Sanitize user input before rendering. Use DOMPurify or encode HTML entities.",
      "owasp": "A03:2021 – Injection",
      "cwe": "CWE-79: Improper Neutralization of Input During Web Page Generation"
    },
    {
      "id": "CSP-001",
      "severity": "HIGH",
      "category": "Content Security Policy",
      "description": "CSP allows 'unsafe-inline' scripts",
      "location": "Response headers",
      "evidence": "Content-Security-Policy: script-src 'self' 'unsafe-inline'",
      "remediation": "Remove 'unsafe-inline' and use nonces or hashes for inline scripts",
      "suggested_csp": "script-src 'self' 'nonce-{random}'",
      "owasp": "A05:2021 – Security Misconfiguration"
    },
    {
      "id": "SEC-001",
      "severity": "HIGH",
      "category": "Mixed Content",
      "description": "HTTP resources loaded on HTTPS page",
      "location": "https://myapp.com/dashboard",
      "insecure_resources": [
        "http://cdn.example.com/script.js",
        "http://analytics.example.com/tracker.js"
      ],
      "remediation": "Update all resource URLs to use HTTPS",
      "owasp": "A02:2021 – Cryptographic Failures"
    }
  ],
  "security_headers": {
    "content-security-policy": {
      "present": true,
      "status": "WEAK",
      "issues": ["'unsafe-inline' detected"]
    },
    "x-frame-options": {
      "present": true,
      "value": "SAMEORIGIN",
      "status": "OK"
    },
    "strict-transport-security": {
      "present": false,
      "status": "MISSING",
      "remediation": "Add 'Strict-Transport-Security: max-age=31536000; includeSubDomains'"
    },
    "x-content-type-options": {
      "present": true,
      "value": "nosniff",
      "status": "OK"
    }
  },
  "third_party_scripts": [
    {
      "src": "https://analytics.google.com/analytics.js",
      "integrity": null,
      "risk": "MEDIUM",
      "recommendation": "Add SRI hash for integrity verification"
    },
    {
      "src": "http://cdn.example.com/widget.js",
      "integrity": null,
      "risk": "CRITICAL",
      "recommendation": "Change to HTTPS and add SRI hash"
    }
  ]
}
```

---

## Workflow 5: Accessibility Testing

### Overview

Chrome DevTools Protocol's [Accessibility domain](https://dev.to/josefine/accessibility-testing-with-chrome-devtools-2bl4) enables full accessibility tree inspection and WCAG compliance checking. This workflow ensures web applications are accessible to users with disabilities.

### Step-by-Step Workflow

#### Phase 1: Accessibility Tree Inspection

1. **Capture Accessibility Tree**
   ```typescript
   // Claude Code prompt:
   "Analyze accessibility tree for https://myapp.com:
   1. Navigate to page
   2. Take snapshot with verbose=true to get full accessibility tree
   3. Extract all element roles, names, ARIA attributes
   4. Identify missing alt text on images
   5. Find buttons/links without accessible names
   6. Report all accessibility issues"

   // Behind the scenes:
   await navigate_page({ url: "https://myapp.com" })
   const snapshot = await take_snapshot({ verbose: true })

   const a11yTree = snapshot.accessibility_tree
   const issues = []

   // Check for images without alt text
   const imagesWithoutAlt = a11yTree.filter(node =>
     node.role === 'image' && !node.name
   )

   // Check for buttons without accessible names
   const buttonsWithoutName = a11yTree.filter(node =>
     node.role === 'button' && !node.name
   )

   // Check for form inputs without labels
   const inputsWithoutLabels = a11yTree.filter(node =>
     node.role === 'textbox' && !node.labeledBy
   )
   ```

2. **Validate ARIA Attributes**
   ```typescript
   // Claude Code prompt:
   "Validate ARIA usage:
   1. Find all elements with ARIA roles
   2. Check for:
      - Invalid ARIA roles
      - Conflicting roles (e.g., role='button' on <button>)
      - Required ARIA properties (aria-label, aria-labelledby)
      - Invalid ARIA attribute values
   3. Report ARIA violations with remediation"

   // Behind the scenes:
   const ariaElements = await evaluate_script({
     script: `Array.from(document.querySelectorAll('[role], [aria-label], [aria-labelledby]')).map(el => ({
       tag: el.tagName,
       role: el.getAttribute('role'),
       ariaLabel: el.getAttribute('aria-label'),
       ariaLabelledBy: el.getAttribute('aria-labelledby')
     }))`
   })

   const validRoles = ['button', 'link', 'navigation', 'main', 'complementary', ...]
   const invalidRoles = ariaElements.filter(el =>
     el.role && !validRoles.includes(el.role)
   )
   ```

#### Phase 2: Keyboard Navigation Testing

3. **Test Keyboard Accessibility**
   ```typescript
   // Claude Code prompt:
   "Test keyboard navigation:
   1. Navigate to page
   2. Simulate Tab key to navigate through focusable elements
   3. Verify focus order is logical (top to bottom, left to right)
   4. Test Enter/Space on buttons and links
   5. Test Escape to close modals
   6. Identify keyboard traps (elements you can't tab out of)
   7. Report keyboard accessibility issues"

   // Behind the scenes:
   await navigate_page({ url: "https://myapp.com" })

   // Get all focusable elements
   const focusableElements = await evaluate_script({
     script: `Array.from(document.querySelectorAll('a, button, input, textarea, select, [tabindex]')).map((el, index) => ({
       index,
       tag: el.tagName,
       text: el.textContent?.trim(),
       tabIndex: el.tabIndex,
       focusable: el.tabIndex >= 0
     }))`
   })

   // Simulate Tab navigation
   for (let i = 0; i < focusableElements.length; i++) {
     await press_key({ key: 'Tab' })
     const focusedElement = await evaluate_script({
       script: 'document.activeElement.outerHTML'
     })
     // Verify expected element is focused
   }
   ```

4. **Test Screen Reader Compatibility**
   ```typescript
   // Claude Code prompt:
   "Analyze screen reader compatibility:
   1. Take accessibility snapshot
   2. For each interactive element, verify:
      - Semantic HTML (<button> not <div onclick>)
      - Accessible names are descriptive
      - State changes are announced (aria-live)
      - Form errors are associated with inputs (aria-describedby)
   3. Check heading hierarchy (h1 > h2 > h3, no skipped levels)
   4. Verify landmark roles (main, navigation, complementary)
   5. Report screen reader issues"

   // Behind the scenes:
   const snapshot = await take_snapshot({ verbose: true })

   // Check heading hierarchy
   const headings = await evaluate_script({
     script: `Array.from(document.querySelectorAll('h1, h2, h3, h4, h5, h6')).map(h => ({
       level: parseInt(h.tagName[1]),
       text: h.textContent.trim()
     }))`
   })

   const hierarchyIssues = []
   for (let i = 1; i < headings.length; i++) {
     const levelJump = headings[i].level - headings[i-1].level
     if (levelJump > 1) {
       hierarchyIssues.push(`Heading level skipped: ${headings[i-1].level} to ${headings[i].level}`)
     }
   }
   ```

#### Phase 3: Color Contrast Analysis

5. **Check Color Contrast Ratios**
   ```typescript
   // Claude Code prompt:
   "Analyze color contrast for WCAG AA compliance:
   1. Navigate to page
   2. For all text elements, calculate contrast ratio between text and background
   3. Check against WCAG standards:
      - Normal text: 4.5:1 minimum
      - Large text (18pt+): 3:1 minimum
      - UI components: 3:1 minimum
   4. Take screenshot with contrast violations highlighted
   5. Report all contrast failures with remediation"

   // Behind the scenes:
   const contrastIssues = await evaluate_script({
     script: `
       function getContrastRatio(fg, bg) {
         const getLuminance = (rgb) => {
           const [r, g, b] = rgb.map(v => {
             v /= 255
             return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4)
           })
           return 0.2126 * r + 0.7152 * g + 0.0722 * b
         }

         const l1 = getLuminance(fg)
         const l2 = getLuminance(bg)
         return (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05)
       }

       const textElements = Array.from(document.querySelectorAll('p, span, a, button, h1, h2, h3, h4, h5, h6'))
       return textElements.map(el => {
         const style = window.getComputedStyle(el)
         const fgColor = style.color
         const bgColor = style.backgroundColor
         // Parse RGB and calculate contrast...
       })
     `
   })
   ```

6. **Emulate Vision Deficiencies**
   ```typescript
   // Claude Code prompt:
   "Test with vision deficiency emulation:
   1. Navigate to page
   2. Enable each vision deficiency emulation:
      - Protanopia (red-blind)
      - Deuteranopia (green-blind)
      - Tritanopia (blue-blind)
      - Achromatopsia (no color)
   3. For each mode, capture screenshot
   4. Verify color is not the only means of conveying information
   5. Report color-dependent UI elements"

   // Behind the scenes (using CDP Emulation domain):
   const deficiencies = ['protanopia', 'deuteranopia', 'tritanopia', 'achromatopsia']

   for (const deficiency of deficiencies) {
     await emulateVisionDeficiency({ type: deficiency })
     const screenshot = await take_screenshot({ format: 'png' })
     // Save screenshot for comparison
   }
   ```

#### Phase 4: Automated Lighthouse Audit

7. **Run Lighthouse Accessibility Audit**
   ```typescript
   // Claude Code prompt:
   "Run Lighthouse accessibility audit:
   1. Navigate to page
   2. Run Lighthouse audit with 'accessibility' category
   3. Extract accessibility score (0-100)
   4. List all failed audits with descriptions
   5. Generate detailed report with remediation steps
   6. Verify Core Web Vitals don't negatively impact accessibility"

   // Behind the scenes (Lighthouse via CDP):
   const lighthouseReport = await runLighthouseAudit({
     url: "https://myapp.com",
     categories: ['accessibility']
   })

   const score = lighthouseReport.categories.accessibility.score * 100
   const failedAudits = lighthouseReport.audits.filter(audit =>
     audit.score < 1 && audit.category === 'accessibility'
   )
   ```

### Example Claude Code Prompts

#### Prompt 1: Comprehensive Accessibility Audit
```
Run a comprehensive accessibility audit for https://myapp.com:

1. Accessibility Tree Analysis:
   - Capture full accessibility tree
   - Find images without alt text
   - Find buttons/links without accessible names
   - Find form inputs without associated labels

2. ARIA Validation:
   - Check for invalid ARIA roles
   - Verify required ARIA attributes
   - Identify redundant ARIA (role='button' on <button>)

3. Keyboard Navigation:
   - Test Tab key navigation through all interactive elements
   - Verify focus order is logical
   - Test Escape key for modal dismissal
   - Identify keyboard traps

4. Color Contrast:
   - Calculate contrast ratios for all text
   - Flag violations of WCAG AA (4.5:1 for normal text)
   - Suggest color adjustments to meet standards

5. Heading Hierarchy:
   - Verify heading levels don't skip (h1 > h3)
   - Check for multiple h1 tags
   - Ensure headings describe content

6. Landmark Roles:
   - Verify <main>, <nav>, <aside> or role equivalents
   - Check for proper page structure

7. Run Lighthouse accessibility audit

8. Generate report with:
   - Accessibility score (0-100)
   - List of violations (Critical, High, Medium, Low)
   - Screenshots demonstrating issues
   - Remediation steps for each issue
   - WCAG 2.1 Level AA compliance status
```

#### Prompt 2: Form Accessibility Testing
```
Test form accessibility for https://myapp.com/signup:

1. Navigate to signup form
2. For each input field, verify:
   - Associated <label> element (for attribute matches input id)
   - Or valid aria-label or aria-labelledby
   - Placeholder is not the only label (WCAG violation)

3. Test error handling:
   - Submit invalid form
   - Verify error messages are:
     - Announced to screen readers (aria-live or focus)
     - Associated with inputs (aria-describedby)
     - Specific and actionable

4. Test required fields:
   - Verify required attribute or aria-required="true"
   - Check visual indication beyond color (asterisk, "required" text)

5. Test keyboard navigation:
   - Tab through all form fields in logical order
   - Verify focus indicators are visible
   - Test form submission with Enter key

6. Take screenshots showing:
   - Form with labels highlighted
   - Error states
   - Focus indicators

7. Generate accessibility report for form
```

#### Prompt 3: Screen Reader Simulation
```
Simulate screen reader experience for https://myapp.com/dashboard:

1. Capture accessibility tree
2. Generate "screen reader narration" for the page:
   - Page title
   - Main landmark content
   - Navigation structure
   - Interactive elements in focus order

3. For each interactive element, report what screen reader would announce:
   - Role (button, link, checkbox, etc.)
   - Accessible name
   - State (expanded, selected, checked)
   - Description (if aria-describedby)

4. Identify silent elements:
   - Clickable divs without role
   - Icons without alt text or aria-label
   - Dynamically changing content without aria-live

5. Test dynamic content:
   - Trigger actions (open modal, submit form)
   - Verify state changes are announced
   - Check focus management (focus moves to modal)

6. Generate report with:
   - Full screen reader narration sequence
   - Silent/confusing elements
   - Suggested ARIA improvements
```

### Integration with LambdaTest Accessibility DevTools

[LambdaTest's Accessibility DevTools](https://www.globenewswire.com/news-release/2024/04/24/2868920/0/en/LambdaTest-Releases-Accessibility-DevTools-Chrome-Extension-to-Enhance-Web-Inclusivity.html) offers automated multi-page scans and workflow scans:

```typescript
// Claude Code prompt:
"Use LambdaTest Accessibility DevTools to scan entire site:
1. Install LambdaTest extension via chrome-devtools-mcp
2. Configure multi-page scan for:
   - Homepage
   - Login
   - Dashboard
   - Profile
   - Settings
3. Run automated scan
4. Export results
5. Generate consolidated report"
```

### CI/CD Integration

```yaml
# .github/workflows/accessibility.yml
name: Accessibility Testing

on:
  pull_request:
    branches: [main]

jobs:
  a11y:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Install Chrome DevTools MCP
        run: npm install -g @executeautomation/chrome-devtools-mcp

      - name: Install Lighthouse
        run: npm install -g lighthouse

      - name: Run Accessibility Audit
        run: |
          npx claude-code run a11y-audit.md

      - name: Check Lighthouse Score
        id: check
        run: |
          SCORE=$(jq '.categories.accessibility.score' lighthouse-report.json)
          MIN_SCORE=0.90  # 90% minimum

          if (( $(echo "$SCORE < $MIN_SCORE" | bc -l) )); then
            echo "a11y_failed=true" >> $GITHUB_OUTPUT
            echo "Accessibility score $SCORE is below minimum $MIN_SCORE"
          fi

      - name: Upload Accessibility Report
        uses: actions/upload-artifact@v3
        with:
          name: a11y-report
          path: |
            a11y-report.json
            lighthouse-report.html

      - name: Comment PR with A11y Issues
        if: steps.check.outputs.a11y_failed == 'true'
        uses: actions/github-script@v6
        with:
          script: |
            const report = require('./a11y-report.json')
            const criticalIssues = report.issues.filter(i => i.severity === 'CRITICAL')
            const comment = `## ♿ Accessibility Issues Detected\n\nScore: ${report.score}/100\n\nCritical Issues:\n${criticalIssues.map(i => `- ${i.description}`).join('\n')}`

            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: comment
            })

      - name: Fail if A11y Score Below Threshold
        if: steps.check.outputs.a11y_failed == 'true'
        run: exit 1
```

### Reporting

**Accessibility Report Structure** (JSON):
```json
{
  "url": "https://myapp.com",
  "scan_date": "2025-12-23T10:30:00Z",
  "lighthouse_score": 87,
  "wcag_level": "AA",
  "compliance_status": "PARTIAL",
  "summary": {
    "total_issues": 12,
    "critical": 2,
    "high": 4,
    "medium": 4,
    "low": 2
  },
  "issues": [
    {
      "id": "A11Y-001",
      "severity": "CRITICAL",
      "wcag": "1.1.1 Non-text Content (Level A)",
      "description": "Images missing alt text",
      "location": "Homepage hero section",
      "affected_elements": [
        "<img src='hero.jpg' class='hero-image'>",
        "<img src='feature1.png' class='feature-icon'>"
      ],
      "impact": "Screen reader users cannot understand image content",
      "remediation": "Add descriptive alt text to all images. Example: <img src='hero.jpg' alt='Team collaborating in modern office'>",
      "code_example": "<img src='hero.jpg' alt='Team collaborating in modern office' class='hero-image'>"
    },
    {
      "id": "A11Y-002",
      "severity": "CRITICAL",
      "wcag": "4.1.2 Name, Role, Value (Level A)",
      "description": "Button without accessible name",
      "location": "Navigation menu - mobile toggle",
      "affected_elements": [
        "<button class='menu-toggle'><span class='hamburger-icon'></span></button>"
      ],
      "impact": "Screen readers announce 'button' without describing its purpose",
      "remediation": "Add aria-label to button",
      "code_example": "<button class='menu-toggle' aria-label='Open navigation menu'><span class='hamburger-icon'></span></button>"
    },
    {
      "id": "A11Y-003",
      "severity": "HIGH",
      "wcag": "1.4.3 Contrast (Minimum) (Level AA)",
      "description": "Insufficient color contrast",
      "location": "Footer links",
      "affected_elements": [
        "a.footer-link { color: #999; background: #fff; }"
      ],
      "contrast_ratio": "2.8:1",
      "required_ratio": "4.5:1",
      "impact": "Users with low vision cannot read link text",
      "remediation": "Darken link color to #767676 for 4.5:1 contrast",
      "code_example": "a.footer-link { color: #767676; background: #fff; }"
    },
    {
      "id": "A11Y-004",
      "severity": "HIGH",
      "wcag": "2.4.6 Headings and Labels (Level AA)",
      "description": "Heading levels skipped",
      "location": "Blog post page",
      "heading_structure": ["h1: Blog Post Title", "h3: Section Title", "h3: Another Section"],
      "impact": "Screen reader users relying on heading navigation get confused",
      "remediation": "Change h3 to h2 for section headings",
      "code_example": "<h2>Section Title</h2>"
    }
  ],
  "keyboard_navigation": {
    "focus_order_issues": 0,
    "keyboard_traps": 0,
    "missing_focus_indicators": 2,
    "details": "Focus indicators missing on custom dropdown components"
  },
  "screen_reader_simulation": {
    "unlabeled_controls": 3,
    "silent_dynamic_content": 1,
    "details": "Modal opening does not announce to screen reader (missing aria-live)"
  },
  "recommendations": [
    "Add alt text to 5 images",
    "Fix color contrast on footer links and secondary buttons",
    "Correct heading hierarchy (h1 > h2 > h3)",
    "Add aria-label to icon-only buttons",
    "Implement aria-live for dynamic content updates"
  ],
  "estimated_effort": "4-6 hours",
  "next_audit_date": "2025-12-30"
}
```

---

## n8n Integration Patterns

### Overview

[n8n](https://n8n.io/) is a workflow automation platform that can integrate with Chrome DevTools Protocol via **Browserless** or **Puppeteer nodes** to schedule and orchestrate testing workflows.

### Integration Options

#### Option 1: Browserless Integration

[Browserless](https://n8n.io/integrations/browserless/) provides Chrome DevTools Protocol access through n8n:

```json
{
  "nodes": [
    {
      "type": "n8n-nodes-base.browserless",
      "name": "Launch Chrome",
      "parameters": {
        "operation": "screenshot",
        "url": "https://myapp.com",
        "fullPage": true,
        "options": {
          "waitUntil": "networkidle"
        }
      }
    }
  ]
}
```

**Capabilities**:
- Scrape content from webpages
- Generate PDFs from URLs using Chrome
- Analyze webpage performance
- Take screenshots using Chrome browser
- Connect via Chrome DevTools Protocol WebSocket

#### Option 2: n8n-nodes-puppeteer (Community Node)

[n8n-nodes-puppeteer](https://github.com/drudge/n8n-nodes-puppeteer) provides full Puppeteer API access:

```bash
# Install community node
npm install n8n-nodes-puppeteer
```

**Features**:
- Execute custom Puppeteer scripts
- Capture screenshots and PDFs
- Scrape content
- Automate web interactions using CDP
- Remote browser support (WebSocket endpoint)

**Example Workflow**:
```json
{
  "nodes": [
    {
      "type": "n8n-nodes-puppeteer.puppeteer",
      "name": "Run E2E Test",
      "parameters": {
        "operation": "executeScript",
        "script": "const page = await browser.newPage();\nawait page.goto('https://myapp.com/login');\nawait page.type('#email', 'test@example.com');\nawait page.type('#password', 'password');\nawait page.click('button[type=submit]');\nawait page.waitForNavigation();\nreturn { success: true };"
      }
    }
  ]
}
```

### Scheduled Automation Patterns

#### Pattern 1: Scheduled Performance Monitoring

```json
{
  "name": "Hourly Performance Check",
  "nodes": [
    {
      "type": "n8n-nodes-base.scheduleTrigger",
      "name": "Every Hour",
      "parameters": {
        "rule": {
          "interval": [{ "field": "hours", "hoursInterval": 1 }]
        }
      }
    },
    {
      "type": "n8n-nodes-base.httpRequest",
      "name": "Trigger Claude Code Performance Test",
      "parameters": {
        "method": "POST",
        "url": "http://localhost:3000/run-performance-test",
        "body": {
          "url": "https://myapp.com"
        }
      }
    },
    {
      "type": "n8n-nodes-base.if",
      "name": "Check Performance Budget",
      "parameters": {
        "conditions": {
          "number": [
            {
              "value1": "={{ $json.lcp }}",
              "operation": "larger",
              "value2": 2500
            }
          ]
        }
      }
    },
    {
      "type": "n8n-nodes-base.slack",
      "name": "Alert on Regression",
      "parameters": {
        "channel": "#performance-alerts",
        "text": "⚠️ Performance regression detected: LCP={{ $json.lcp }}ms (budget: 2500ms)"
      }
    }
  ]
}
```

#### Pattern 2: Nightly Security Scan

```json
{
  "name": "Nightly Security Scan",
  "nodes": [
    {
      "type": "n8n-nodes-base.scheduleTrigger",
      "name": "Daily at 2 AM",
      "parameters": {
        "rule": {
          "interval": [{ "field": "hours", "hoursInterval": 24 }],
          "atTime": "02:00"
        }
      }
    },
    {
      "type": "n8n-nodes-puppeteer.puppeteer",
      "name": "Run Security Scan",
      "parameters": {
        "operation": "executeScript",
        "script": "// Navigate to app\nconst page = await browser.newPage();\nawait page.goto('https://myapp.com');\n\n// Capture console errors\nconst errors = [];\npage.on('console', msg => {\n  if (msg.type() === 'error') errors.push(msg.text());\n});\n\n// Navigate through app\nawait page.click('a[href=\"/dashboard\"]');\nawait page.waitForTimeout(2000);\n\nreturn { errors, count: errors.length };"
      }
    },
    {
      "type": "n8n-nodes-base.if",
      "name": "Check for Errors",
      "parameters": {
        "conditions": {
          "number": [
            {
              "value1": "={{ $json.count }}",
              "operation": "larger",
              "value2": 0
            }
          ]
        }
      }
    },
    {
      "type": "n8n-nodes-base.emailSend",
      "name": "Email Security Report",
      "parameters": {
        "toEmail": "security@myapp.com",
        "subject": "Security Scan Report - {{ $now.format('YYYY-MM-DD') }}",
        "text": "Console errors detected:\n{{ $json.errors.join('\\n') }}"
      }
    }
  ]
}
```

#### Pattern 3: Weekly Visual Regression Check

```json
{
  "name": "Weekly Visual Regression",
  "nodes": [
    {
      "type": "n8n-nodes-base.scheduleTrigger",
      "name": "Every Sunday",
      "parameters": {
        "rule": {
          "interval": [{ "field": "weeks", "weeksInterval": 1 }],
          "dayOfWeek": 0,
          "atTime": "03:00"
        }
      }
    },
    {
      "type": "n8n-nodes-base.browserless",
      "name": "Capture Current Screenshots",
      "parameters": {
        "operation": "screenshot",
        "url": "https://myapp.com",
        "fullPage": true
      }
    },
    {
      "type": "n8n-nodes-base.httpRequest",
      "name": "Compare with Baseline",
      "parameters": {
        "method": "POST",
        "url": "http://localhost:3000/compare-screenshots",
        "body": {
          "current": "={{ $binary.data }}"
        }
      }
    },
    {
      "type": "n8n-nodes-base.if",
      "name": "Visual Changes Detected",
      "parameters": {
        "conditions": {
          "number": [
            {
              "value1": "={{ $json.diffPercentage }}",
              "operation": "larger",
              "value2": 1
            }
          ]
        }
      }
    },
    {
      "type": "n8n-nodes-base.discord",
      "name": "Post to Discord",
      "parameters": {
        "webhook": "https://discord.com/api/webhooks/...",
        "text": "🎨 Visual changes detected ({{ $json.diffPercentage }}% difference). Review: {{ $json.reportUrl }}"
      }
    }
  ]
}
```

#### Pattern 4: Pre-Deployment Validation

```json
{
  "name": "Pre-Deployment Test Suite",
  "nodes": [
    {
      "type": "n8n-nodes-base.webhook",
      "name": "GitHub Webhook (PR Opened)",
      "parameters": {
        "path": "github-pr-webhook",
        "httpMethod": "POST"
      }
    },
    {
      "type": "n8n-nodes-base.function",
      "name": "Extract PR URL",
      "parameters": {
        "functionCode": "return [{\n  json: {\n    prUrl: $input.item.json.pull_request.html_url,\n    deployUrl: `https://preview-${$input.item.json.pull_request.number}.myapp.com`\n  }\n}];"
      }
    },
    {
      "type": "n8n-nodes-base.httpRequest",
      "name": "Run E2E Tests",
      "parameters": {
        "method": "POST",
        "url": "http://localhost:3000/run-e2e-tests",
        "body": {
          "url": "={{ $json.deployUrl }}"
        }
      }
    },
    {
      "type": "n8n-nodes-base.httpRequest",
      "name": "Run Performance Tests",
      "parameters": {
        "method": "POST",
        "url": "http://localhost:3000/run-performance-tests",
        "body": {
          "url": "={{ $json.deployUrl }}"
        }
      }
    },
    {
      "type": "n8n-nodes-base.httpRequest",
      "name": "Run Security Scan",
      "parameters": {
        "method": "POST",
        "url": "http://localhost:3000/run-security-scan",
        "body": {
          "url": "={{ $json.deployUrl }}"
        }
      }
    },
    {
      "type": "n8n-nodes-base.httpRequest",
      "name": "Run Accessibility Audit",
      "parameters": {
        "method": "POST",
        "url": "http://localhost:3000/run-a11y-audit",
        "body": {
          "url": "={{ $json.deployUrl }}"
        }
      }
    },
    {
      "type": "n8n-nodes-base.function",
      "name": "Aggregate Results",
      "parameters": {
        "functionCode": "const results = $input.all();\nconst passed = results.every(r => r.json.passed);\nreturn [{\n  json: {\n    passed,\n    e2e: results[0].json,\n    performance: results[1].json,\n    security: results[2].json,\n    a11y: results[3].json\n  }\n}];"
      }
    },
    {
      "type": "n8n-nodes-base.github",
      "name": "Comment on PR",
      "parameters": {
        "operation": "createComment",
        "issueNumber": "={{ $json.prNumber }}",
        "body": "## 🤖 Automated Test Results\\n\\n✅ E2E: {{ $json.e2e.passed ? 'PASSED' : 'FAILED' }}\\n✅ Performance: {{ $json.performance.passed ? 'PASSED' : 'FAILED' }}\\n✅ Security: {{ $json.security.passed ? 'PASSED' : 'FAILED' }}\\n✅ Accessibility: {{ $json.a11y.passed ? 'PASSED' : 'FAILED' }}"
      }
    }
  ]
}
```

### Remote Browser Pattern

For production n8n instances, use remote browser to avoid Chrome dependencies:

```json
{
  "nodes": [
    {
      "type": "n8n-nodes-puppeteer.puppeteer",
      "name": "Connect to Remote Chrome",
      "parameters": {
        "browserWebSocketEndpoint": "wss://chrome.browserless.io?token=YOUR_TOKEN",
        "script": "const page = await browser.newPage();\n// Your automation script..."
      }
    }
  ]
}
```

### Integration with Claude Code

**Pattern**: n8n triggers Claude Code via HTTP API:

```json
{
  "nodes": [
    {
      "type": "n8n-nodes-base.httpRequest",
      "name": "Trigger Claude Code Test",
      "parameters": {
        "method": "POST",
        "url": "http://localhost:3000/claude-code/run",
        "body": {
          "prompt": "Use chrome-devtools-mcp to test login flow on {{ $json.url }}. Take screenshots if any step fails.",
          "mcp_server": "chrome-devtools"
        }
      }
    }
  ]
}
```

**Claude Code API Endpoint** (Express.js):
```typescript
// server.ts
import express from 'express'
import { exec } from 'child_process'
import fs from 'fs'

const app = express()
app.use(express.json())

app.post('/claude-code/run', async (req, res) => {
  const { prompt, mcp_server } = req.body

  // Write prompt to temporary file
  const promptFile = `/tmp/prompt-${Date.now()}.md`
  fs.writeFileSync(promptFile, prompt)

  // Execute Claude Code
  exec(`npx claude-code run ${promptFile}`, (error, stdout, stderr) => {
    if (error) {
      return res.status(500).json({ error: stderr })
    }

    // Parse results from stdout
    const results = parseClaudeCodeOutput(stdout)
    res.json(results)
  })
})

app.listen(3000, () => console.log('Claude Code API listening on port 3000'))
```

---

## Reporting and Alerting

### Multi-Channel Alerting Strategy

| Channel | Use Case | Urgency |
|---------|----------|---------|
| **Slack** | Team notifications, daily summaries | Medium |
| **Email** | Detailed reports, weekly digests | Low |
| **Discord** | Developer community alerts | Medium |
| **PagerDuty** | Critical failures (production down) | Critical |
| **GitHub Issues** | Automated bug creation for failures | Medium |
| **Dashboard** | Real-time monitoring, trend analysis | Low |

### Slack Integration

```typescript
// slack-notifier.ts
import { WebClient } from '@slack/web-api'

const slack = new WebClient(process.env.SLACK_BOT_TOKEN)

async function sendPerformanceAlert(report: PerformanceReport) {
  const regressions = report.core_web_vitals.filter(m => m.status === 'REGRESSION')

  if (regressions.length === 0) return

  await slack.chat.postMessage({
    channel: '#performance-alerts',
    text: '⚠️ Performance Regression Detected',
    blocks: [
      {
        type: 'section',
        text: {
          type: 'mrkdwn',
          text: `*Performance Regression Detected*\n${report.url}\n\nRegressions:\n${regressions.map(r => `• ${r.metric}: ${r.current}ms (baseline: ${r.baseline}ms, +${r.delta})`).join('\n')}`
        }
      },
      {
        type: 'actions',
        elements: [
          {
            type: 'button',
            text: { type: 'plain_text', text: 'View Report' },
            url: report.report_url
          }
        ]
      }
    ]
  })
}
```

### Email Reporting

```typescript
// email-reporter.ts
import nodemailer from 'nodemailer'

const transporter = nodemailer.createTransport({
  host: process.env.SMTP_HOST,
  port: 587,
  auth: {
    user: process.env.SMTP_USER,
    pass: process.env.SMTP_PASS
  }
})

async function sendWeeklyDigest(reports: TestReport[]) {
  const summary = {
    total_tests: reports.length,
    passed: reports.filter(r => r.status === 'PASSED').length,
    failed: reports.filter(r => r.status === 'FAILED').length
  }

  const html = `
    <h1>Weekly Test Report</h1>
    <p>Period: ${reports[0].date} - ${reports[reports.length - 1].date}</p>

    <h2>Summary</h2>
    <ul>
      <li>Total Tests: ${summary.total_tests}</li>
      <li>Passed: ${summary.passed} (${(summary.passed / summary.total_tests * 100).toFixed(1)}%)</li>
      <li>Failed: ${summary.failed}</li>
    </ul>

    <h2>Failed Tests</h2>
    <ul>
      ${reports.filter(r => r.status === 'FAILED').map(r => `<li>${r.test_name}: ${r.error}</li>`).join('')}
    </ul>

    <a href="${process.env.DASHBOARD_URL}">View Full Dashboard</a>
  `

  await transporter.sendMail({
    from: 'testing@myapp.com',
    to: 'team@myapp.com',
    subject: `Weekly Test Report - ${summary.passed}/${summary.total_tests} passed`,
    html
  })
}
```

### PagerDuty Integration (Critical Alerts)

```typescript
// pagerduty-alerter.ts
import { event } from '@pagerduty/pdjs'

async function triggerCriticalAlert(issue: SecurityIssue) {
  if (issue.severity !== 'CRITICAL') return

  await event({
    data: {
      routing_key: process.env.PAGERDUTY_ROUTING_KEY,
      event_action: 'trigger',
      payload: {
        summary: `CRITICAL: ${issue.description}`,
        severity: 'critical',
        source: issue.location,
        custom_details: {
          category: issue.category,
          owasp: issue.owasp,
          remediation: issue.remediation
        }
      }
    }
  })
}
```

### GitHub Issue Creation

```typescript
// github-issue-creator.ts
import { Octokit } from '@octokit/rest'

const octokit = new Octokit({ auth: process.env.GITHUB_TOKEN })

async function createIssueForFailure(testReport: TestReport) {
  if (testReport.status !== 'FAILED') return

  await octokit.issues.create({
    owner: 'myorg',
    repo: 'myapp',
    title: `[Automated Test Failure] ${testReport.test_name}`,
    body: `## Test Failure Report\n\n**Test:** ${testReport.test_name}\n**Date:** ${testReport.timestamp}\n**Error:** ${testReport.error}\n\n### Steps to Reproduce:\n${testReport.steps.map((s, i) => `${i + 1}. ${s.action} (${s.status})`).join('\n')}\n\n### Screenshots:\n${testReport.screenshots.map(s => `![Screenshot](${s})`).join('\n')}\n\n### AI Suggestion:\n${testReport.ai_suggestion}`,
    labels: ['automated-test-failure', 'bug']
  })
}
```

### Real-Time Dashboard

```typescript
// dashboard-api.ts
import express from 'express'
import WebSocket from 'ws'

const app = express()
const wss = new WebSocket.Server({ port: 8080 })

// Store test results
const testResults: TestReport[] = []

// Broadcast updates to all connected clients
function broadcastUpdate(report: TestReport) {
  testResults.push(report)

  wss.clients.forEach(client => {
    if (client.readyState === WebSocket.OPEN) {
      client.send(JSON.stringify({
        type: 'TEST_RESULT',
        data: report
      }))
    }
  })
}

// API endpoint to receive test results
app.post('/api/test-results', (req, res) => {
  const report = req.body as TestReport
  broadcastUpdate(report)
  res.json({ success: true })
})

// Dashboard stats endpoint
app.get('/api/stats', (req, res) => {
  const last24h = testResults.filter(r =>
    Date.now() - new Date(r.timestamp).getTime() < 24 * 60 * 60 * 1000
  )

  res.json({
    total: last24h.length,
    passed: last24h.filter(r => r.status === 'PASSED').length,
    failed: last24h.filter(r => r.status === 'FAILED').length,
    pass_rate: (last24h.filter(r => r.status === 'PASSED').length / last24h.length * 100).toFixed(1)
  })
})
```

**Dashboard UI** (React):
```typescript
// Dashboard.tsx
import React, { useEffect, useState } from 'react'

export function Dashboard() {
  const [stats, setStats] = useState({ total: 0, passed: 0, failed: 0, pass_rate: 0 })
  const [recentTests, setRecentTests] = useState<TestReport[]>([])

  useEffect(() => {
    // Fetch initial stats
    fetch('/api/stats')
      .then(r => r.json())
      .then(setStats)

    // Connect to WebSocket for real-time updates
    const ws = new WebSocket('ws://localhost:8080')
    ws.onmessage = (event) => {
      const { type, data } = JSON.parse(event.data)
      if (type === 'TEST_RESULT') {
        setRecentTests(prev => [data, ...prev.slice(0, 9)])
      }
    }

    return () => ws.close()
  }, [])

  return (
    <div>
      <h1>Automated Testing Dashboard</h1>

      <div className="stats">
        <div className="stat">
          <h2>{stats.total}</h2>
          <p>Tests (24h)</p>
        </div>
        <div className="stat">
          <h2>{stats.passed}</h2>
          <p>Passed</p>
        </div>
        <div className="stat">
          <h2>{stats.failed}</h2>
          <p>Failed</p>
        </div>
        <div className="stat">
          <h2>{stats.pass_rate}%</h2>
          <p>Pass Rate</p>
        </div>
      </div>

      <h2>Recent Tests</h2>
      <table>
        <thead>
          <tr>
            <th>Test Name</th>
            <th>Status</th>
            <th>Duration</th>
            <th>Timestamp</th>
          </tr>
        </thead>
        <tbody>
          {recentTests.map(test => (
            <tr key={test.id} className={test.status === 'FAILED' ? 'failed' : 'passed'}>
              <td>{test.test_name}</td>
              <td>{test.status}</td>
              <td>{test.duration_ms}ms</td>
              <td>{new Date(test.timestamp).toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
```

---

## CI/CD Integration

### GitHub Actions Complete Workflow

```yaml
# .github/workflows/complete-test-suite.yml
name: Complete Automated Test Suite

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours

jobs:
  e2e-tests:
    name: E2E Tests
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '20'

      - name: Install Chrome DevTools MCP
        run: npm install -g @executeautomation/chrome-devtools-mcp

      - name: Run E2E Tests
        run: npx claude-code run e2e-tests.md

      - name: Upload Test Results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: e2e-results
          path: e2e-report.json

  performance-tests:
    name: Performance Tests
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '20'

      - name: Install Chrome DevTools MCP
        run: npm install -g @executeautomation/chrome-devtools-mcp

      - name: Run Performance Tests
        run: npx claude-code run performance-tests.md

      - name: Check Performance Budgets
        run: node performance-budget-checker.js

      - name: Upload Performance Report
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: performance-report
          path: performance-report.json

  visual-regression:
    name: Visual Regression Tests
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0

      - name: Checkout Baseline Screenshots
        run: git checkout origin/main -- visual-baselines/

      - name: Install Dependencies
        run: |
          npm install -g @executeautomation/chrome-devtools-mcp
          npm install pixelmatch pngjs

      - name: Capture Current Screenshots
        run: npx claude-code run visual-capture.md

      - name: Compare with Baseline
        id: compare
        run: node visual-diff-checker.js
        continue-on-error: true

      - name: Upload Diff Images
        if: steps.compare.outcome == 'failure'
        uses: actions/upload-artifact@v3
        with:
          name: visual-diffs
          path: visual-diffs/

  security-scan:
    name: Security Scan
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Install Chrome DevTools MCP
        run: npm install -g @executeautomation/chrome-devtools-mcp

      - name: Run Security Scan
        run: npx claude-code run security-scan.md

      - name: Check for Critical Issues
        id: check
        run: |
          CRITICAL=$(jq '.issues[] | select(.severity=="CRITICAL")' security-report.json | wc -l)
          echo "critical_count=$CRITICAL" >> $GITHUB_OUTPUT
          if [ $CRITICAL -gt 0 ]; then
            exit 1
          fi

      - name: Upload Security Report
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: security-report
          path: security-report.json

  accessibility-audit:
    name: Accessibility Audit
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Install Dependencies
        run: |
          npm install -g @executeautomation/chrome-devtools-mcp
          npm install -g lighthouse

      - name: Run Accessibility Audit
        run: npx claude-code run a11y-audit.md

      - name: Check Lighthouse Score
        id: check
        run: |
          SCORE=$(jq '.categories.accessibility.score' lighthouse-report.json)
          MIN_SCORE=0.90
          if (( $(echo "$SCORE < $MIN_SCORE" | bc -l) )); then
            echo "a11y_failed=true" >> $GITHUB_OUTPUT
            exit 1
          fi

      - name: Upload A11y Report
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: a11y-report
          path: |
            a11y-report.json
            lighthouse-report.html

  aggregate-results:
    name: Aggregate and Report
    runs-on: ubuntu-latest
    needs: [e2e-tests, performance-tests, visual-regression, security-scan, accessibility-audit]
    if: always()
    steps:
      - uses: actions/checkout@v3

      - name: Download All Reports
        uses: actions/download-artifact@v3

      - name: Aggregate Results
        run: node aggregate-reports.js

      - name: Upload Combined Report
        uses: actions/upload-artifact@v3
        with:
          name: combined-report
          path: combined-report.json

      - name: Comment on PR
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v6
        with:
          script: |
            const report = require('./combined-report.json')
            const fs = require('fs')
            const template = fs.readFileSync('.github/pr-comment-template.md', 'utf8')
            const comment = template
              .replace('{{E2E_STATUS}}', report.e2e.passed ? '✅ PASSED' : '❌ FAILED')
              .replace('{{PERF_STATUS}}', report.performance.passed ? '✅ PASSED' : '❌ FAILED')
              .replace('{{VISUAL_STATUS}}', report.visual.passed ? '✅ PASSED' : '⚠️ CHANGES')
              .replace('{{SECURITY_STATUS}}', report.security.passed ? '✅ PASSED' : '❌ FAILED')
              .replace('{{A11Y_STATUS}}', report.a11y.passed ? '✅ PASSED' : '❌ FAILED')

            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: comment
            })

      - name: Send Slack Notification
        if: failure()
        uses: slackapi/slack-github-action@v1
        with:
          payload: |
            {
              "text": "❌ Automated tests failed in ${{ github.repository }}",
              "blocks": [
                {
                  "type": "section",
                  "text": {
                    "type": "mrkdwn",
                    "text": "*Automated Test Suite Failed*\n\nRepository: ${{ github.repository }}\nBranch: ${{ github.ref_name }}\nCommit: ${{ github.sha }}\n\n<${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}|View Run>"
                  }
                }
              ]
            }
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
```

### GitLab CI/CD

```yaml
# .gitlab-ci.yml
stages:
  - test
  - report

variables:
  CHROME_DEVTOOLS_MCP: "@executeautomation/chrome-devtools-mcp"

e2e-tests:
  stage: test
  image: node:20
  before_script:
    - npm install -g $CHROME_DEVTOOLS_MCP
  script:
    - npx claude-code run e2e-tests.md
  artifacts:
    paths:
      - e2e-report.json
    when: always

performance-tests:
  stage: test
  image: node:20
  before_script:
    - npm install -g $CHROME_DEVTOOLS_MCP
  script:
    - npx claude-code run performance-tests.md
    - node performance-budget-checker.js
  artifacts:
    paths:
      - performance-report.json
    when: always

security-scan:
  stage: test
  image: node:20
  before_script:
    - npm install -g $CHROME_DEVTOOLS_MCP
  script:
    - npx claude-code run security-scan.md
  artifacts:
    paths:
      - security-report.json
    when: always
  allow_failure: false

aggregate-reports:
  stage: report
  image: node:20
  dependencies:
    - e2e-tests
    - performance-tests
    - security-scan
  script:
    - node aggregate-reports.js
  artifacts:
    paths:
      - combined-report.json
    reports:
      junit: combined-report.xml
```

---

## Best Practices

### 1. Workflow Organization

**DO**:
- Separate concerns: one workflow per testing type
- Use reusable workflow components
- Store prompts in version-controlled markdown files
- Maintain baseline data (screenshots, performance metrics)

**DON'T**:
- Mix multiple testing types in one workflow
- Hardcode test URLs or credentials
- Store sensitive data in prompts
- Skip documentation of workflow changes

### 2. Prompt Engineering for Automation

**DO**:
```
✅ "Navigate to https://myapp.com/login, fill email with 'test@example.com',
   fill password with 'test123', click submit button, wait for redirect
   to /dashboard. If any step fails, take screenshot and capture console errors."
```

**DON'T**:
```
❌ "Test the login" (too vague)
❌ "Login and do stuff" (no verification)
❌ "Check if login works" (no specific actions)
```

**Best Practices**:
- Be explicit about actions (navigate, fill, click, wait)
- Define success/failure criteria
- Specify what to capture on failure
- Include timeout expectations
- Request structured output (JSON, screenshots)

### 3. Error Handling

**Pattern**:
```typescript
// Claude Code prompt with error handling:
"Run this test with error recovery:
1. Navigate to https://myapp.com
2. If navigation fails (timeout), retry once with 30s timeout
3. Click login button
4. If button not found, take screenshot and search for alternative selectors
5. Fill credentials
6. If submit fails, capture console errors and network errors
7. Return structured JSON with success/failure and all captured data"
```

### 4. Performance Optimization

**DO**:
- Run tests in parallel when possible
- Use headless mode in CI/CD
- Cache dependencies (Chrome DevTools MCP, Puppeteer)
- Set appropriate timeouts
- Use page load strategies (domcontentloaded vs networkidle)

**DON'T**:
- Run all tests sequentially
- Use excessive wait times
- Re-install dependencies on every run
- Use infinite timeouts

### 5. Security

**DO**:
- Use environment variables for credentials
- Rotate test account passwords regularly
- Use Chrome for Testing (turns off self-XSS warnings)
- Implement rate limiting on test endpoints
- Sanitize logs before sharing

**DON'T**:
- Store credentials in prompts or code
- Use production accounts for testing
- Share screenshots containing sensitive data
- Log authentication tokens

### 6. Maintenance

**DO**:
- Review test results weekly
- Update baselines when intentional changes occur
- Prune old test data (screenshots, traces)
- Monitor test execution time trends
- Document workflow changes

**DON'T**:
- Ignore flaky tests
- Let baselines become outdated
- Accumulate test artifacts indefinitely
- Make workflow changes without documentation

### 7. Reporting

**DO**:
- Generate actionable reports
- Include screenshots and traces
- Provide remediation steps
- Track trends over time
- Send alerts to appropriate channels

**DON'T**:
- Generate reports without context
- Flood channels with noise
- Alert for every minor issue
- Ignore historical data

---

## Sources

- [Chrome DevTools MCP: Bridging AI Assistants with Browser Reality](https://orchestrator.dev/blog/2025-12-13-chrome-devtools-mcp-article/)
- [Chrome DevTools MCP Unleashed: AI Agents Debug, Test, and Auto-Fix Code](https://lalatenduswain.medium.com/chrome-devtools-mcp-unleashed-ai-agents-debug-test-and-auto-fix-code-right-in-your-browser-af00440fa670)
- [GitHub: Chrome DevTools MCP](https://github.com/ChromeDevTools/chrome-devtools-mcp/)
- [GitHub: cc_chrome_devtools_mcp_skill](https://github.com/justfinethanku/cc_chrome_devtools_mcp_skill)
- [Chrome DevTools Protocol Documentation](https://chromedevtools.github.io/devtools-protocol/)
- [Automated Performance Testing with Playwright and Chrome DevTools](https://medium.com/@aishahsofea/automated-performance-testing-with-playwright-and-chrome-devtools-a-deep-dive-52e8b240b00d)
- [Chrome DevTools Performance Optimization Cookbook](https://docs.continue.dev/guides/chrome-devtools-mcp-performance)
- [Chrome DevTools MCP: AI browser debugging complete guide 2025](https://vladimirsiedykh.com/blog/chrome-devtools-mcp-ai-browser-debugging-complete-guide-2025)
- [Vitest 4.0 with Stable Browser Mode and Visual Regression Testing](https://www.infoq.com/news/2025/12/vitest-4-browser-mode/)
- [How Chrome DevTools helps to defend against self-XSS attacks](https://developer.chrome.com/blog/self-xss)
- [How to Use Chrome DevTools for Web Vulnerability Scanning](https://www.fromdev.com/2025/12/how-to-use-chrome-devtools-for-web-vulnerability-scanning.html)
- [Accessibility Testing with Chrome DevTools](https://dev.to/josefine/accessibility-testing-with-chrome-devtools-2bl4)
- [LambdaTest Releases Accessibility DevTools Chrome Extension](https://www.globenewswire.com/news-release/2024/04/24/2868920/0/en/LambdaTest-Releases-Accessibility-DevTools-Chrome-Extension-to-Enhance-Web-Inclusivity.html)
- [n8n Browserless Integration](https://n8n.io/integrations/browserless/)
- [GitHub: n8n-nodes-puppeteer](https://github.com/drudge/n8n-nodes-puppeteer)
