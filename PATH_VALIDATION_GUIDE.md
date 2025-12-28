# Path Validation Security Guide

## Quick Reference for Developers

This guide explains how to safely handle file paths in API endpoints to prevent path traversal vulnerabilities.

---

## The Problem: Path Traversal Attacks

**Never trust user-provided file paths directly!**

### Vulnerable Code Example (DON'T DO THIS)

```python
@router.get("/files/{file_id}")
async def get_file(file_id: str):
    # VULNERABLE - No validation!
    file_path = base64.b64decode(file_id).decode('utf-8')
    with open(file_path, 'r') as f:
        return f.read()
```

### Why It's Dangerous

Attackers can use `../` sequences to escape allowed directories:

```
Input:  ../../etc/passwd
Result: /etc/passwd (system file exposed!)

Input:  ../../../Windows/System32/config/SAM
Result: C:\Windows\System32\config\SAM (Windows password hashes exposed!)
```

---

## The Solution: Secure Path Validation

### Step-by-Step Implementation

#### 1. Define Allowed Directories

```python
from pathlib import Path

# Define allowed base directories
ALLOWED_DIRS = [
    Path("C:/meowping-rts/ai-agents").resolve(),
    Path("C:/meowping-rts/ai-agents/knowledge-base").resolve()
]
```

#### 2. Resolve and Validate Paths

```python
from fastapi import HTTPException
from pathlib import Path

def validate_file_path(user_path: str) -> Path:
    """
    Validate that a user-provided path is within allowed directories.

    Args:
        user_path: Path string from user input

    Returns:
        Validated Path object

    Raises:
        HTTPException: If path is outside allowed directories
    """
    # Resolve to absolute path (removes ../, symlinks, etc.)
    resolved_path = Path(user_path).resolve()

    # Check if path is within any allowed directory
    for allowed_dir in ALLOWED_DIRS:
        try:
            # This will raise ValueError if path is not within allowed_dir
            resolved_path.relative_to(allowed_dir)
            return resolved_path  # Valid path!
        except ValueError:
            continue  # Try next allowed directory

    # Path is not within any allowed directory
    raise HTTPException(
        status_code=403,
        detail="Access denied: File path is outside allowed directories"
    )
```

#### 3. Use in Your Endpoint

```python
@router.get("/files/{file_id}")
async def get_file(file_id: str):
    import base64

    # Decode user input
    decoded_path = base64.b64decode(file_id).decode('utf-8')

    # Validate and resolve path
    safe_path = validate_file_path(decoded_path)

    # Check if file exists
    if not safe_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    # Now safe to read
    with open(safe_path, 'r') as f:
        return {"content": f.read()}
```

---

## Complete Secure Example

```python
from fastapi import APIRouter, HTTPException
from pathlib import Path
import base64

router = APIRouter()

# Define allowed directories (at module level)
AI_AGENTS_ROOT = Path("C:/meowping-rts/ai-agents")
KB_ROOT = Path("C:/meowping-rts/ai-agents/knowledge-base")

@router.get("/files/{file_id}")
async def get_kb_file_details(file_id: str):
    """
    Get file details with secure path validation.

    Security: Only allows access to files within allowed directories.
    """
    try:
        # Decode file_id (base64 encoded path)
        decoded_path = base64.b64decode(file_id).decode('utf-8')

        # Resolve the path to prevent path traversal attacks
        file_path = Path(decoded_path).resolve()

        # Define allowed directories
        allowed_dirs = [
            AI_AGENTS_ROOT.resolve(),
            KB_ROOT.resolve()
        ]

        # Verify file is within allowed directories
        is_allowed = False
        for allowed_dir in allowed_dirs:
            try:
                # Check if file_path is relative to allowed_dir
                file_path.relative_to(allowed_dir)
                is_allowed = True
                break
            except ValueError:
                # file_path is not relative to this allowed_dir
                continue

        if not is_allowed:
            raise HTTPException(
                status_code=403,
                detail="Access denied: File path is outside allowed directories"
            )

        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")

        # Safe to proceed with file operations
        return {
            "path": str(file_path),
            "name": file_path.name,
            "size": file_path.stat().st_size
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
```

---

## Key Security Principles

### 1. Always Use `Path().resolve()`

```python
# Good
file_path = Path(user_input).resolve()

# Bad - doesn't handle ../, symlinks
file_path = user_input
```

### 2. Use Whitelist Validation

```python
# Good - Explicit allow list
allowed_dirs = [Path("/allowed/dir1"), Path("/allowed/dir2")]

# Bad - Blacklist (easy to bypass)
if "../" in user_input:  # Can be bypassed with URL encoding, etc.
    raise Error()
```

### 3. Validate Before Operations

```python
# Good - Validate first
safe_path = validate_path(user_input)
if safe_path.exists():
    with open(safe_path) as f:
        ...

# Bad - Check then operate (race condition)
if os.path.exists(user_input):  # File could change here
    with open(user_input) as f:  # Opening different file
        ...
```

### 4. Return Appropriate HTTP Codes

```python
# 403 Forbidden - Path outside allowed directories
raise HTTPException(status_code=403, detail="Access denied")

# 404 Not Found - File doesn't exist
raise HTTPException(status_code=404, detail="File not found")

# 500 Internal Server Error - Unexpected errors
raise HTTPException(status_code=500, detail="Internal error")
```

---

## Common Pitfalls to Avoid

### ❌ DON'T: String-based validation

```python
# BAD - Can be bypassed
if user_path.startswith("/allowed/"):
    # Attacker can use: /allowed/../../../etc/passwd
```

### ❌ DON'T: Only check for "../"

```python
# BAD - Can be bypassed with encoding
if "../" not in user_path:
    # Attacker can use: ..%2F or URL encoding
```

### ❌ DON'T: Trust normalized paths without validation

```python
# BAD - os.path.normpath doesn't prevent escaping
normalized = os.path.normpath(user_path)
# /allowed/../etc/passwd -> /etc/passwd (still outside allowed!)
```

### ✅ DO: Use Path().resolve() + relative_to()

```python
# GOOD - Cryptographically safe
resolved = Path(user_path).resolve()
resolved.relative_to(allowed_dir)  # Raises ValueError if outside
```

---

## Testing Your Implementation

### Test Cases to Include

```python
def test_path_validation():
    # Should ALLOW
    assert validate_path("C:/meowping-rts/ai-agents/file.txt") == Path(...)

    # Should BLOCK with 403
    with pytest.raises(HTTPException) as exc:
        validate_path("C:/meowping-rts/ai-agents/../../etc/passwd")
    assert exc.value.status_code == 403

    # Should BLOCK direct system access
    with pytest.raises(HTTPException) as exc:
        validate_path("C:/Windows/System32/config/SAM")
    assert exc.value.status_code == 403
```

### Manual Testing

```bash
# Test with curl
# Valid file (should work)
curl http://localhost:8000/api/knowledge/files/$(echo "C:/meowping-rts/ai-agents/file.txt" | base64)

# Path traversal (should return 403)
curl http://localhost:8000/api/knowledge/files/$(echo "../../../etc/passwd" | base64)

# Should return: {"detail": "Access denied: File path is outside allowed directories"}
```

---

## Quick Checklist

Before deploying any file access endpoint, verify:

- [ ] User input is NEVER used directly in file operations
- [ ] All paths go through `Path().resolve()`
- [ ] Paths are validated against a whitelist using `relative_to()`
- [ ] HTTP 403 is returned for unauthorized paths
- [ ] HTTP 404 is returned for non-existent files
- [ ] Exceptions are properly handled
- [ ] Test cases include path traversal attempts
- [ ] Test cases include legitimate file access
- [ ] No symlink bypasses are possible
- [ ] No race conditions exist

---

## Additional Resources

- [OWASP Path Traversal](https://owasp.org/www-community/attacks/Path_Traversal)
- [CWE-22: Path Traversal](https://cwe.mitre.org/data/definitions/22.html)
- [Python pathlib Documentation](https://docs.python.org/3/library/pathlib.html)
- [FastAPI Security Guide](https://fastapi.tiangolo.com/tutorial/security/)

---

## Questions?

If you're unsure about implementing path validation:

1. Review this guide
2. Check the fixed `knowledge.py` endpoint as a reference
3. Run the test suite: `python test_path_traversal_fix.py`
4. Ask the security team for a code review

**Remember: When in doubt, validate!**
