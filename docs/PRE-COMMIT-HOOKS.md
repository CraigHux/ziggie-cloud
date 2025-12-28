# Pre-Commit Hooks Configuration

> **Last Updated**: 2025-12-27
> **Scope**: Ziggie Ecosystem and MeowPing RTS

---

## Overview

Pre-commit hooks enforce code quality and security standards automatically before each commit. This configuration implements the quality gates from CLAUDE.md, including the critical "No test.skip()" rule (Know Thyself Principle #2).

---

## Installation

### Prerequisites

1. **Python 3.8+** installed
2. **Git** installed

### Install pre-commit framework

```bash
# Install pre-commit globally
pip install pre-commit

# Verify installation
pre-commit --version
```

### Install hooks in repository

```bash
# For Ziggie
cd C:\Ziggie
pre-commit install

# For MeowPing RTS
cd C:\meowping-rts
pre-commit install
```

### Initial run on all files

```bash
# Run all hooks on entire codebase
pre-commit run --all-files
```

---

## Hook Categories

### 1. Standard Hooks (pre-commit-hooks)

| Hook | Purpose | Files Affected |
|------|---------|----------------|
| `trailing-whitespace` | Remove trailing whitespace | All text files |
| `end-of-file-fixer` | Ensure files end with newline | All text files |
| `check-yaml` | Validate YAML syntax | *.yaml, *.yml |
| `check-json` | Validate JSON syntax | *.json |
| `check-added-large-files` | Block files > 1MB (2MB for game assets) | All files |
| `detect-private-key` | Block private key commits | All files |
| `check-merge-conflict` | Detect merge conflict markers | All text files |
| `check-case-conflict` | Detect case-only filename conflicts | All files |
| `mixed-line-ending` | Normalize to LF line endings | All text files |

### 2. Python Hooks

| Hook | Purpose | Configuration |
|------|---------|---------------|
| `black` | Code formatting | Line length: 88 (default) |
| `isort` | Import sorting | Profile: black |
| `flake8` | Linting | Max line: 120, ignore E203, E501, W503 |

### 3. JavaScript/TypeScript Hooks

| Hook | Purpose | Files |
|------|---------|-------|
| `prettier` | Code formatting | js, jsx, ts, tsx, json, yaml, md, css |
| `eslint` | Linting (meowping-rts) | ts, tsx in frontend/ |

### 4. Security Hooks

| Hook | Purpose | Severity |
|------|---------|----------|
| `detect-private-key` | Block SSH/API keys | CRITICAL |
| `detect-secrets` | Scan for secrets | CRITICAL |

### 5. Custom Hooks

| Hook | Purpose | Enforcement |
|------|---------|-------------|
| `no-test-skip` | Block test.skip() | MANDATORY |
| `typescript-check` | TypeScript validation | OPTIONAL |

---

## Custom Hook: no-test-skip

This hook enforces **Know Thyself Principle #2**:

> "NO test.skip() in codebase - Zero `test.skip()` in codebase = Sprint FAILURE"

### Patterns Detected

```text
JavaScript/TypeScript:
- test.skip()
- test.todo()
- it.skip()
- describe.skip()
- xit()
- xdescribe()
- xtest()
- test.only() (focused tests)
- it.only() (focused tests)
- describe.only() (focused tests)

Python:
- @pytest.mark.skip
- @pytest.mark.skipif
- pytest.skip()
- @unittest.skip
- @unittest.skipIf
- @unittest.skipUnless
```

### Example Output

```
======================================================================
KNOW THYSELF PRINCIPLE #2 VIOLATION: test.skip() detected!
======================================================================

Per CLAUDE.md: 'NO test.skip() in codebase = Sprint FAILURE'

Violations found:

  File: tests/unit/test_feature.py
    Line 42: [@pytest.mark.skip]
      @pytest.mark.skip(reason="TODO: implement later")

----------------------------------------------------------------------
Total violations: 1

REMEDIATION:
  1. IMPLEMENT the feature to make tests pass
  2. Or REMOVE the test if no longer applicable
  3. NEVER skip tests to make the build pass
----------------------------------------------------------------------
```

### Remediation

**DO NOT**:
```python
@pytest.mark.skip(reason="Not implemented yet")
def test_feature():
    pass
```

**DO**:
```python
def test_feature():
    # Implement the actual test
    result = feature_function()
    assert result == expected_value
```

---

## Configuration Files

### C:\Ziggie\.pre-commit-config.yaml

- Standard hooks + Python + Prettier
- Custom test.skip detection
- Large file limit: 1MB
- Excludes: node_modules, dist, build, venv

### C:\meowping-rts\.pre-commit-config.yaml

- Standard hooks + Python + Prettier + ESLint
- Custom test.skip detection
- TypeScript type checking
- Large file limit: 2MB (game assets)
- Excludes: node_modules, dist, build, venv, frontend/node_modules

### scripts/check_test_skip.py

Python script for test.skip detection. Located in both repositories.

---

## Commands Reference

### Daily Usage

```bash
# Run on staged files only (automatic on commit)
pre-commit run

# Run on specific files
pre-commit run --files path/to/file.py

# Run specific hook
pre-commit run black

# Skip hooks for emergency (USE SPARINGLY)
git commit --no-verify -m "Emergency fix"
```

### Maintenance

```bash
# Update hooks to latest versions
pre-commit autoupdate

# Clean cached environments
pre-commit clean

# Uninstall hooks
pre-commit uninstall
```

### CI/CD Integration

```yaml
# GitHub Actions example
- name: Run pre-commit
  uses: pre-commit/action@v3.0.0
  with:
    extra_args: --all-files
```

---

## Troubleshooting

### Hook fails on first run

Many hooks auto-fix issues. Re-stage and retry:
```bash
git add -A
git commit -m "message"
```

### Black/Prettier conflict

Both are configured but operate on different file types. If conflict occurs:
1. Run Prettier first: `pre-commit run prettier`
2. Then Black: `pre-commit run black`

### Large file blocked

Legitimate large files can be excluded:
```yaml
# In .pre-commit-config.yaml
- id: check-added-large-files
  args: ['--maxkb=2048']
  exclude: ^(assets/textures/)
```

### Secrets false positive

Create `.secrets.baseline` to allow known non-secrets:
```bash
detect-secrets scan > .secrets.baseline
git add .secrets.baseline
```

---

## Quality Gates Summary

| Gate | Hook | Enforcement |
|------|------|-------------|
| No test.skip() | `no-test-skip` | MANDATORY |
| TypeScript errors | `typescript-check` | OPTIONAL |
| Code formatting | `black`, `prettier` | AUTO-FIX |
| Import sorting | `isort` | AUTO-FIX |
| Linting | `flake8`, `eslint` | BLOCK |
| Security | `detect-secrets`, `detect-private-key` | BLOCK |
| File size | `check-added-large-files` | BLOCK |

---

## Related Documentation

- `C:\Users\minin\.claude\CLAUDE.md` - Global quality standards
- `C:\Ziggie\CLAUDE.md` - Project-specific standards
- `C:\Ziggie\ZIGGIE-ECOSYSTEM-MASTER-STATUS-V5.md` - Infrastructure status

---

*Pre-commit hooks enforcing CLAUDE.md quality gates*
*Created: 2025-12-27 by DevOps Agent*
