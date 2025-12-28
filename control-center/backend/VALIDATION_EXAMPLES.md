# Input Validation Examples

Quick reference guide for API input validation.

---

## Service Management

### Start Service

**Valid:**
```bash
curl -X POST "http://localhost:54112/api/services/comfyui/start"
```

**Invalid - Special Characters:**
```bash
# Returns 422 Validation Error
curl -X POST "http://localhost:54112/api/services/invalid@service/start"
curl -X POST "http://localhost:54112/api/services/service name/start"
```

### Stop Service

**Valid:**
```bash
curl -X POST "http://localhost:54112/api/services/comfyui/stop?timeout=30&force=false"
```

**Invalid - Out of Range:**
```bash
# Returns 422 - timeout must be 1-300 seconds
curl -X POST "http://localhost:54112/api/services/comfyui/stop?timeout=500"
curl -X POST "http://localhost:54112/api/services/comfyui/stop?timeout=0"
```

### Get Service Logs

**Valid:**
```bash
curl "http://localhost:54112/api/services/comfyui/logs?lines=100"
```

**Invalid - Line Limit:**
```bash
# Returns 422 - lines must be 1-10,000
curl "http://localhost:54112/api/services/comfyui/logs?lines=20000"
curl "http://localhost:54112/api/services/comfyui/logs?lines=-1"
```

---

## Project Management

### Browse Project Files

**Valid:**
```bash
curl "http://localhost:54112/api/projects/meowping-rts/files?path=src/components&pattern=*.tsx"
```

**Invalid - Directory Traversal:**
```bash
# Returns 422 - path traversal blocked
curl "http://localhost:54112/api/projects/test/files?path=../../etc/passwd"
curl "http://localhost:54112/api/projects/test/files?path=/etc/passwd"
curl "http://localhost:54112/api/projects/test/files?path=..\\..\\windows\\system32"
```

**Invalid - Unsafe Pattern:**
```bash
# Returns 422 - invalid pattern characters
curl "http://localhost:54112/api/projects/test/files?pattern=*.tsx;rm -rf /"
curl "http://localhost:54112/api/projects/test/files?pattern=$(whoami)"
```

### Get Commits

**Valid:**
```bash
curl "http://localhost:54112/api/projects/meowping-rts/commits?limit=20"
```

**Invalid - Limit Out of Range:**
```bash
# Returns 422 - limit must be 1-100
curl "http://localhost:54112/api/projects/meowping-rts/commits?limit=0"
curl "http://localhost:54112/api/projects/meowping-rts/commits?limit=500"
```

---

## Knowledge Base

### Trigger Scan

**Valid:**
```bash
curl -X POST "http://localhost:54112/api/knowledge/scan?priority=high&max_videos=50"
curl -X POST "http://localhost:54112/api/knowledge/scan?creator_id=test-creator&max_videos=10"
```

**Invalid - Bad Priority:**
```bash
# Returns 422 - priority must be high/medium/low
curl -X POST "http://localhost:54112/api/knowledge/scan?priority=critical"
curl -X POST "http://localhost:54112/api/knowledge/scan?priority=urgent"
```

**Invalid - Max Videos:**
```bash
# Returns 422 - max_videos must be 1-100
curl -X POST "http://localhost:54112/api/knowledge/scan?max_videos=0"
curl -X POST "http://localhost:54112/api/knowledge/scan?max_videos=200"
```

**Invalid - Creator ID:**
```bash
# Returns 422 - invalid characters
curl -X POST "http://localhost:54112/api/knowledge/scan?creator_id=test@creator"
curl -X POST "http://localhost:54112/api/knowledge/scan?creator_id=../malicious"
```

### Search Knowledge Base

**Valid:**
```bash
curl "http://localhost:54112/api/knowledge/search?query=character+design&limit=20"
curl "http://localhost:54112/api/knowledge/search?query=animation&agent=art-director"
```

**Invalid - Query Too Short:**
```bash
# Returns 422 - query must be at least 2 characters
curl "http://localhost:54112/api/knowledge/search?query=a"
curl "http://localhost:54112/api/knowledge/search?query="
```

**Invalid - Query Too Long:**
```bash
# Returns 422 - query max 500 characters
LONG_QUERY=$(python -c "print('a' * 501)")
curl "http://localhost:54112/api/knowledge/search?query=$LONG_QUERY"
```

**Invalid - Agent Filter:**
```bash
# Returns 422 - invalid agent name
curl "http://localhost:54112/api/knowledge/search?query=test&agent=invalid@agent"
curl "http://localhost:54112/api/knowledge/search?query=test&agent=agent name"
```

---

## Docker Management

### Start Container

**Valid:**
```bash
curl -X POST "http://localhost:54112/api/docker/container/my-container/start"
curl -X POST "http://localhost:54112/api/docker/container/abc123/start"
```

**Invalid - Container ID:**
```bash
# Returns 422 - invalid container ID format
curl -X POST "http://localhost:54112/api/docker/container/invalid@container/start"
curl -X POST "http://localhost:54112/api/docker/container/container name/start"
curl -X POST "http://localhost:54112/api/docker/container/$(whoami)/start"
```

### Stop Container

**Valid:**
```bash
curl -X POST "http://localhost:54112/api/docker/container/my-container/stop?timeout=30"
```

**Invalid - Timeout:**
```bash
# Returns 422 - timeout must be 1-300 seconds
curl -X POST "http://localhost:54112/api/docker/container/test/stop?timeout=0"
curl -X POST "http://localhost:54112/api/docker/container/test/stop?timeout=500"
```

### Get Container Logs

**Valid:**
```bash
curl "http://localhost:54112/api/docker/container/my-container/logs?tail=100"
curl "http://localhost:54112/api/docker/container/my-container/logs?tail=50&since=10m"
curl "http://localhost:54112/api/docker/container/my-container/logs?since=1h"
```

**Invalid - Tail:**
```bash
# Returns 422 - tail must be 1-1000
curl "http://localhost:54112/api/docker/container/test/logs?tail=0"
curl "http://localhost:54112/api/docker/container/test/logs?tail=2000"
```

**Invalid - Since Format:**
```bash
# Returns 422 - invalid since format
curl "http://localhost:54112/api/docker/container/test/logs?since=invalid"
curl "http://localhost:54112/api/docker/container/test/logs?since=10x"
```

---

## Common Validation Patterns

### Alphanumeric with Hyphens/Underscores
**Pattern:** `^[a-zA-Z0-9_-]+$`
**Used for:** Service names, agent names, creator IDs, container IDs

**Valid:**
- `my-service`
- `test_agent`
- `service123`
- `ABC-123_test`

**Invalid:**
- `my service` (space)
- `test@service` (special char)
- `service/name` (slash)
- `../malicious` (traversal)

### Safe Path Pattern
**Pattern:** `^[a-zA-Z0-9._/-]*$` (with additional checks)
**Used for:** File paths, directory browsing

**Valid:**
- `src/components`
- `lib/utils/helpers.ts`
- `data.json`

**Invalid:**
- `../../../etc/passwd` (traversal)
- `/etc/passwd` (absolute path)
- `path;rm -rf /` (command injection)

### Safe File Pattern
**Pattern:** `^[a-zA-Z0-9.*_-]+$`
**Used for:** Glob patterns

**Valid:**
- `*.tsx`
- `test-*.js`
- `*.component.ts`

**Invalid:**
- `*.tsx;rm -rf /` (command injection)
- `$(malicious)` (command substitution)

---

## Validation Error Response Format

### Single Error
```json
{
  "detail": [
    {
      "type": "string_pattern_mismatch",
      "loc": ["path", "service_name"],
      "msg": "String should match pattern '^[a-zA-Z0-9_-]+$'",
      "input": "invalid@service"
    }
  ]
}
```

### Multiple Errors
```json
{
  "detail": [
    {
      "type": "string_pattern_mismatch",
      "loc": ["path", "service_name"],
      "msg": "String should match pattern '^[a-zA-Z0-9_-]+$'",
      "input": "invalid@service"
    },
    {
      "type": "less_than_equal",
      "loc": ["query", "timeout"],
      "msg": "Input should be less than or equal to 300",
      "input": "500"
    }
  ]
}
```

---

## Testing Validation

### Using curl

```bash
# Test valid request
curl -X POST "http://localhost:54112/api/services/test-service/start" \
  -w "\nHTTP Status: %{http_code}\n"

# Test invalid request
curl -X POST "http://localhost:54112/api/services/invalid@service/start" \
  -w "\nHTTP Status: %{http_code}\n"

# Expected: HTTP Status: 422
```

### Using Python

```python
import requests

# Valid request
response = requests.post(
    "http://localhost:54112/api/services/test-service/start"
)
print(f"Status: {response.status_code}")
# Expected: Status: 200 or 404 (not 422)

# Invalid request
response = requests.post(
    "http://localhost:54112/api/services/invalid@service/start"
)
print(f"Status: {response.status_code}")
print(f"Error: {response.json()}")
# Expected: Status: 422
# Expected: Error details with validation message
```

### Using pytest

```python
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_service_validation():
    # Valid
    response = client.post("/api/services/test-service/start")
    assert response.status_code != 422

    # Invalid
    response = client.post("/api/services/invalid@service/start")
    assert response.status_code == 422
    assert "detail" in response.json()
```

---

## Best Practices

### 1. Always Validate User Input
```python
# ✅ Good - Validated
service_name: str = Field(pattern=r'^[a-zA-Z0-9_-]+$')

# ❌ Bad - No validation
service_name: str
```

### 2. Use Appropriate Limits
```python
# ✅ Good - Reasonable limits
lines: int = Query(default=100, ge=1, le=10000)

# ❌ Bad - No limits (DoS risk)
lines: int
```

### 3. Prevent Path Traversal
```python
# ✅ Good - Blocks traversal
@field_validator('path')
def validate_path(cls, v: str) -> str:
    if '..' in v or v.startswith('/'):
        raise ValueError("Path traversal not allowed")
    return v

# ❌ Bad - No traversal check
path: str
```

### 4. Use Enums for Fixed Values
```python
# ✅ Good - Type-safe enum
priority: Literal["high", "medium", "low"]

# ❌ Bad - Free-form string
priority: str
```

### 5. Provide Clear Error Messages
```python
# ✅ Good - Helpful message
raise ValueError(
    "Service name must contain only alphanumeric characters, "
    "hyphens, and underscores"
)

# ❌ Bad - Vague message
raise ValueError("Invalid service name")
```

---

## Troubleshooting

### Common Issues

**Issue:** Getting 422 for what seems valid

**Solution:** Check the exact validation rules in schemas.py
```python
# Example: Service name validation
pattern=r'^[a-zA-Z0-9_-]+$'  # Only alphanumeric, hyphen, underscore
```

**Issue:** Validation passing but logic failing

**Solution:** Validation only checks format, not existence
```python
# Validation: ✅ Format is valid
# Logic: ❌ Service doesn't exist -> 404 Not Found
```

**Issue:** Response is 500 instead of 422

**Solution:** Error might be happening after validation. Check logs.

---

**Reference:** See `C:\Ziggie\control-center\backend\models\schemas.py` for complete validation schemas.

**Test Suite:** Run `pytest tests/test_validation.py -v` to verify all validation rules.
