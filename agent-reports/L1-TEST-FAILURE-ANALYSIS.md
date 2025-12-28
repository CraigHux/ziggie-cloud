# L1 Test Failure Analysis Report

> **Agent**: L1 Research Agent
> **Date**: 2025-12-28
> **Scope**: C:\Ziggie\control-center\backend
> **Total Tests**: 121 (105 passing, 16 failing)

---

## Executive Summary

The 16 test failures fall into **3 distinct categories**, requiring different fix approaches:

| Category | Count | Fix Type | Effort |
|----------|-------|----------|--------|
| Response Format Mismatches | 2 | API alignment | Low |
| Validation Logic Gaps | 7 | Add path validation | Medium |
| WebSocket Protocol Issues | 7 | Protocol implementation | Medium |

**Key Finding**: The validation tests are NOT broken - they correctly identify that the API endpoints are missing input validation. The tests expect 422 (validation error) but receive 404 (not found) because validation is bypassed when project/service doesn't exist.

---

## Category 1: Response Format Mismatches (2 Failures)

### 1.1 test_agents_api.py::test_list_all_agents

**File**: `C:\Ziggie\control-center\backend\tests\test_agents_api.py:30`

**Error**:
```python
AssertionError: assert 'total' in {'agents': [...], 'cached': True, 'meta': {...}}
```

**Root Cause**: The API returns `meta.total` instead of a top-level `total` field.

**API Response Structure** (actual):
```json
{
  "agents": [...],
  "cached": true,
  "meta": {
    "total": 3,
    "page": 1,
    "has_next": false,
    ...
  }
}
```

**Test Expected**:
```python
assert "total" in data  # Expects top-level "total"
assert data["total"] == 3
```

**Fix Options**:
1. **Option A (Recommended)**: Update API to include top-level `total` for backward compatibility
   - Location: `api/agents.py` line 365-370
   - Add: `result['total'] = result['meta']['total']`

2. **Option B**: Update test to use `meta.total`
   - Change: `assert data["meta"]["total"] == 3`

**Priority**: HIGH (Quick fix - 5 minutes)

---

### 1.2 test_system_api.py::test_get_system_info

**File**: `C:\Ziggie\control-center\backend\tests\test_system_api.py:90`

**Error**:
```python
AttributeError: module 'api.system' has no attribute 'platform'
```

**Root Cause**: The mock path `api.system.platform` is incorrect because `platform` is imported locally inside the function, not at module level.

**Current API Code** (`api/system.py:119-125`):
```python
async def get_system_info(request: Request):
    try:
        import platform  # Local import!
        import socket
        import sys
        import time
```

**Test Attempts**:
```python
with patch('api.system.platform.system', return_value="Windows"):  # WRONG - module import not at top level
```

**Fix Options**:
1. **Option A (Recommended)**: Move imports to module level in `api/system.py`
   - Move `import platform, socket, time` to top of file
   - Then mocking `api.system.platform.system` will work

2. **Option B**: Use builtins mock
   - Change test to: `with patch('platform.system', return_value="Windows"):`
   - This patches the actual platform module

**Priority**: HIGH (Quick fix - 10 minutes)

---

## Category 2: Validation Logic Gaps (7 Failures)

These tests correctly identify missing input validation in the API. The API currently:
1. Does NOT validate path parameters for malicious patterns
2. Processes the request normally, then returns 404 when resource not found
3. Should return 422 BEFORE attempting to process malicious input

### 2.1 test_validation.py::test_start_service_invalid_characters

**File**: `C:\Ziggie\control-center\backend\tests\test_validation.py:47`

**Error**:
```python
AssertionError: Should reject: service/name
assert 404 == 422
```

**Root Cause**: The services API has proper `pattern=r'^[a-zA-Z0-9_-]+$'` validation on the `service_name` path parameter (line 65 in services.py), but the invalid name `service/name` is being URL-decoded as a path traversal before FastAPI validation kicks in.

**Analysis**: FastAPI's path validation only runs AFTER URL routing. When the URL is `/api/services/service/name/start`, it routes to a different (non-existent) endpoint entirely, hence 404.

**Fix**: Add explicit regex validation early in the request or use middleware to catch injection patterns.

**Priority**: MEDIUM

---

### 2.2 test_validation.py::test_browse_files_directory_traversal

**File**: `C:\Ziggie\control-center\backend\tests\test_validation.py:139`

**Error**:
```python
AssertionError: Should reject: ../../../etc/passwd
assert 404 == 422
```

**Root Cause**: The `browse_project_files` endpoint at `api/projects.py:299-345` does NOT validate the `path` query parameter for path traversal attacks. It simply:
1. Looks for project by name (returns 404 if not found)
2. Constructs `browse_path = project_path / path` without validation
3. The path traversal could escape the project directory

**Current Code** (`api/projects.py:317-318`):
```python
# Construct full path - NO VALIDATION!
browse_path = project_path / path if path else project_path
```

**Fix Required**: Add path traversal validation before processing:
```python
# Validate path for traversal attempts
if '..' in path or path.startswith('/') or path.startswith('\\'):
    raise HTTPException(status_code=422, detail="Invalid path: directory traversal not allowed")
```

**Priority**: HIGH (Security vulnerability)

---

### 2.3 test_validation.py::test_browse_files_invalid_pattern

**File**: `C:\Ziggie\control-center\backend\tests\test_validation.py:155`

**Error**:
```python
AssertionError: Should reject: *.tsx;rm -rf /
assert 404 == 422
```

**Root Cause**: The `pattern` query parameter is not validated for shell injection patterns.

**Current Code** (`api/projects.py:303`):
```python
pattern: str = Query("*", description="File pattern to match")
```

**Fix Required**: Add pattern validation:
```python
import re
SAFE_PATTERN = re.compile(r'^[a-zA-Z0-9_\-\.\*\?]+$')
if not SAFE_PATTERN.match(pattern):
    raise HTTPException(status_code=422, detail="Invalid pattern: contains unsafe characters")
```

**Priority**: HIGH (Security vulnerability)

---

### 2.4 test_validation.py::test_project_name_validation

**File**: `C:\Ziggie\control-center\backend\tests\test_validation.py:194`

**Error**:
```python
AssertionError: Should reject: project@name
assert 404 == 422
```

**Root Cause**: The `get_project_status` endpoint does NOT validate project names. Invalid names simply result in 404 because no matching project is found.

**Current Code** (`api/projects.py:237-251`):
```python
@router.get("/{project_name}/status")
async def get_project_status(request: Request, project_name: str):
    # No validation - directly searches for project
    for path in PROJECT_DIRS:
        if path.name == project_name:
            project_path = path
            break

    if not project_path:
        UserFriendlyError.not_found("Project", project_name)  # Returns 404
```

**Fix Required**: Add parameter validation:
```python
from fastapi import Path as FastPath

@router.get("/{project_name}/status")
async def get_project_status(
    request: Request,
    project_name: str = FastPath(
        ...,
        pattern=r'^[a-zA-Z0-9_-]+$',
        min_length=1,
        max_length=100
    )
):
```

**Priority**: MEDIUM

---

### 2.5 test_validation.py::test_start_container_invalid_id

**File**: `C:\Ziggie\control-center\backend\tests\test_validation.py:323`

**Error**:
```python
AssertionError: Should reject: container@name
assert 500 == 422
```

**Root Cause**: The `start_container` endpoint at `api/docker.py:226-249` has NO validation on `container_id`. It passes the raw ID directly to Docker, which causes Docker to fail with an error (hence 500).

**Current Code** (`api/docker.py:226-234`):
```python
@router.post("/container/{container_id}/start")
async def start_container(request: Request, container_id: str):
    # NO VALIDATION
    result = run_docker_command(["start", container_id])
```

**Fix Required**: Add FastAPI Path validation:
```python
from fastapi import Path as FastPath

@router.post("/container/{container_id}/start")
async def start_container(
    request: Request,
    container_id: str = FastPath(
        ...,
        pattern=r'^[a-zA-Z0-9][a-zA-Z0-9_.-]*$',
        min_length=1,
        max_length=128
    )
):
```

**Priority**: MEDIUM

---

### 2.6 test_validation.py::test_command_injection_attempts

**File**: `C:\Ziggie\control-center\backend\tests\test_validation.py:470`

**Error**:
```python
AssertionError: Should reject: test && cat /etc/passwd
assert 404 == 422
```

**Root Cause**: Same as 2.1 - the service name with shell metacharacters is URL-routed before validation.

**Priority**: MEDIUM (Handled by 2.1 fix)

---

### 2.7 test_validation.py::test_path_traversal_attempts

**File**: `C:\Ziggie\control-center\backend\tests\test_validation.py:486`

**Error**:
```python
AssertionError: Should reject: ../../../etc/passwd
assert 404 == 422
```

**Root Cause**: Same as 2.2 - path traversal not validated.

**Priority**: HIGH (Handled by 2.2 fix)

---

## Category 3: WebSocket Protocol Issues (7 Failures)

These failures indicate mismatches between test expectations and actual WebSocket protocol implementation.

### 3.1 test_websocket.py::test_websocket_authentication

**File**: `C:\Ziggie\control-center\backend\tests\test_websocket.py:25`

**Error**:
```python
AssertionError: assert ('status' in {...} or 'error' in {...})
# Actual response: system_stats data (cpu, memory, disk)
```

**Root Cause**: The WebSocket endpoint immediately sends system stats on connection, without authentication response. The test expects an auth status message first.

**Current Behavior** (`main.py:126-152`): WebSocket broadcasts stats every 2 seconds without waiting for any auth/subscription message.

**Fix Required**: Either:
1. Update test to expect system_stats on first message
2. Add initial connection acknowledgment before broadcasting stats

**Priority**: LOW (Test expectation mismatch)

---

### 3.2 test_websocket.py::test_system_stats_updates

**File**: `C:\Ziggie\control-center\backend\tests\test_websocket.py:30`

**Error**:
```python
AttributeError: module 'services' has no attribute 'system_monitor'
```

**Root Cause**: Mock path `services.system_monitor.get_system_stats` doesn't exist. The WebSocket handler uses `psutil` directly in `main.py`, not a service module.

**Fix Required**: Remove the mock or change test to not require mocking:
```python
# The endpoint uses psutil directly, no service layer
# Simply test that we receive stats, don't mock
```

**Priority**: LOW

---

### 3.3 test_websocket.py::test_service_status_updates

**File**: `C:\Ziggie\control-center\backend\tests\test_websocket.py:49`

**Error**:
```python
AttributeError: module 'services' has no attribute 'service_controller'
```

**Root Cause**: Same as 3.2 - mock path doesn't exist.

**Priority**: LOW

---

### 3.4 test_websocket.py::test_multiple_websocket_clients

**File**: `C:\Ziggie\control-center\backend\tests\test_websocket.py:78`

**Error**:
```python
AttributeError: 'WebSocketTestSession' object has no attribute 'portal'
```

**Root Cause**: Test uses `websocket_connect()` as context manager incorrectly. Connections stored in list, then `close()` called after context exits.

**Current Code**:
```python
connections = []
for i in range(3):
    ws = test_client.websocket_connect(f"/ws?client_id={i}")
    connections.append(ws)

for ws in connections:
    ws.close()  # FAILS - portal already closed
```

**Fix Required**: Use context managers properly:
```python
with test_client.websocket_connect("/ws?client_id=1") as ws1, \
     test_client.websocket_connect("/ws?client_id=2") as ws2, \
     test_client.websocket_connect("/ws?client_id=3") as ws3:
    # Test with all 3 connections
    pass
```

**Priority**: LOW

---

### 3.5 test_websocket.py::test_websocket_error_handling

**File**: `C:\Ziggie\control-center\backend\tests\test_websocket.py:90`

**Error**:
```python
AssertionError: assert ('error' in {...} or 'status' in {...})
# Actual: receives system_stats (cpu, memory, disk)
```

**Root Cause**: WebSocket doesn't send error response for invalid message type. It ignores client messages and just broadcasts stats.

**Fix Options**:
1. Update test expectation to ignore error handling requirement
2. Implement message handling in WebSocket endpoint

**Priority**: LOW

---

### 3.6 test_websocket.py::test_websocket_ping_pong

**File**: `C:\Ziggie\control-center\backend\tests\test_websocket.py:102`

**Error**:
```python
AssertionError: assert ('system_stats' == 'pong' or 'status' in {...})
```

**Root Cause**: WebSocket doesn't implement ping/pong protocol. Sends system_stats instead of pong response.

**Current WebSocket** (`main.py:126-159`): Only broadcasts stats, doesn't read client messages.

**Fix Required**: Add message handling to WebSocket:
```python
# Read client message
data = await websocket.receive_json()
if data.get("type") == "ping":
    await websocket.send_json({"type": "pong"})
```

**Priority**: LOW

---

### 3.7 test_websocket.py::test_websocket_message_queue

**File**: `C:\Ziggie\control-center\backend\tests\test_websocket.py:127`

**Error**:
```python
AssertionError: assert 0 > 0
# responses list is empty
```

**Root Cause**: Test sends 3 messages but gets 0 responses because WebSocket doesn't process client messages.

**Priority**: LOW

---

## Priority-Ordered Fix Plan

### Phase 1: Quick Wins (30 minutes)

| # | Test | Fix | Lines to Change |
|---|------|-----|-----------------|
| 1 | test_list_all_agents | Add `total` to response | api/agents.py:370 |
| 2 | test_get_system_info | Move imports to module level | api/system.py:1-10 |

### Phase 2: Security Fixes (2 hours)

| # | Test | Fix | Location |
|---|------|-----|----------|
| 3 | test_browse_files_directory_traversal | Add path validation | api/projects.py:300-320 |
| 4 | test_browse_files_invalid_pattern | Add pattern validation | api/projects.py:303 |
| 5 | test_project_name_validation | Add Path validation | api/projects.py:237-240 |
| 6 | test_start_container_invalid_id | Add Path validation | api/docker.py:226-228 |
| 7 | test_start_service_invalid_characters | Validate before routing | api/services.py |
| 8 | test_command_injection_attempts | (Same as #7) | - |
| 9 | test_path_traversal_attempts | (Same as #3) | - |

### Phase 3: WebSocket Protocol (1 hour)

| # | Test | Fix | Location |
|---|------|-----|----------|
| 10 | test_websocket_authentication | Add connection ack | main.py:124 |
| 11 | test_system_stats_updates | Remove invalid mock | test_websocket.py:30 |
| 12 | test_service_status_updates | Remove invalid mock | test_websocket.py:49 |
| 13 | test_multiple_websocket_clients | Fix context manager usage | test_websocket.py:66-78 |
| 14 | test_websocket_error_handling | Update expectation | test_websocket.py:90 |
| 15 | test_websocket_ping_pong | Implement ping/pong | main.py:126-159 |
| 16 | test_websocket_message_queue | Implement message handling | main.py:126-159 |

---

## Appendix: Test-to-Fix Matrix

| Test Name | Category | Status Code | Expected | Fix Type |
|-----------|----------|-------------|----------|----------|
| test_list_all_agents | Response | 200 | 200 + total | API change |
| test_get_system_info | Mock | Error | 200 | Move imports |
| test_start_service_invalid_characters | Validation | 404 | 422 | Add validation |
| test_browse_files_directory_traversal | Validation | 404 | 422 | Add validation |
| test_browse_files_invalid_pattern | Validation | 404 | 422 | Add validation |
| test_project_name_validation | Validation | 404 | 422 | Add validation |
| test_start_container_invalid_id | Validation | 500 | 422 | Add validation |
| test_command_injection_attempts | Validation | 404 | 422 | Add validation |
| test_path_traversal_attempts | Validation | 404 | 422 | Add validation |
| test_websocket_authentication | Protocol | - | status/error | Protocol impl |
| test_system_stats_updates | Mock | Error | - | Fix mock path |
| test_service_status_updates | Mock | Error | - | Fix mock path |
| test_multiple_websocket_clients | Test Bug | Error | - | Fix test code |
| test_websocket_error_handling | Protocol | - | error/status | Protocol impl |
| test_websocket_ping_pong | Protocol | - | pong | Protocol impl |
| test_websocket_message_queue | Protocol | 0 msgs | >0 msgs | Protocol impl |

---

## Conclusion

**Critical Findings**:
1. The validation tests are **correctly identifying security gaps** in the API
2. Path traversal and injection attacks are NOT being blocked with 422 - they either succeed or return 404
3. The WebSocket implementation is a **broadcast-only** design without client message handling

**Recommended Action**:
1. Implement Phase 1 fixes immediately (30 minutes)
2. Prioritize Phase 2 security fixes before any deployment
3. WebSocket protocol can be deferred if not user-facing

**Zero test.skip() Violations**: All tests are running; this report identifies implementation gaps, not test skips.

---

*Generated by L1 Research Agent - 2025-12-28*
