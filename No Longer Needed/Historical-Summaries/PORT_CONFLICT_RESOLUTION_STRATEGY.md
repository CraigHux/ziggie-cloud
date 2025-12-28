# Port Conflict Resolution Strategy
## L1.9 Migration Agent - Post-Migration Configuration Fix

**Status:** ACTIVE RESOLUTION
**Date:** November 7, 2025
**Lead Agent:** L1.9 - Migration Agent (Coordination)
**Supporting Team:** L1.6 (Technical), L1.3 (Frontend), L1.5 (DevOps), L1.2 (Backend)

---

## Executive Summary

Post-migration to C:\Ziggie has revealed critical port conflicts preventing both the Game Frontend and Control Center Dashboard from running simultaneously. This document provides a unified strategy to resolve these conflicts and ensure both systems operate correctly.

**Current State:**
- Docker Game Frontend: Port 3000 (Meow Ping RTS - ACTIVE)
- Docker Game Backend: Port 8000 (FastAPI - ACTIVE)
- Control Center Backend: Port 54112 (FastAPI - ACTIVE, via VS Code)
- Control Center Frontend: Port 3000 (configured - BLOCKED by Game Frontend)
- Control Center Frontend proxy: Expects backend on port 8080 (MISMATCH)

**Root Causes Identified:**
1. Port 3000 claimed by both frontends
2. Backend running on 54112 instead of configured 8080
3. Frontend vite.config.js expects wrong port
4. Service configuration inconsistencies

---

## Current System Architecture

### Running Containers (Docker)
```
Container: meowping-frontend
  - Port: 3000:3000 (HOST:CONTAINER)
  - Image: Game React Frontend
  - Status: Running 5+ hours

Container: meowping-backend
  - Port: 8000:8000 (HOST:CONTAINER)
  - Image: FastAPI Backend
  - Status: Running 5+ hours (unhealthy)

Container: meowping-mongodb
  - Port: 27017:27017 (HOST:CONTAINER)
  - Database: MongoDB
  - Status: Running 5+ hours
```

### Control Center Backend (Python/FastAPI)
```
Location: C:\Ziggie\control-center\control-center\backend
Framework: FastAPI (uvicorn)
Configuration: config.py specifies PORT: 8080
Running Process: Python via port 54112
Status: Active and responding to API requests
```

### Control Center Frontend (React/Vite)
```
Location: C:\Ziggie\control-center\control-center\frontend
Framework: React + Vite
Configured Port: 3000
Proxy Target: http://localhost:8080 (Backend API)
Status: NOT STARTED (port 3000 conflict)
```

---

## Problem Analysis

### Issue 1: Port 3000 Conflict
**Problem:** Two separate frontends both configured for port 3000
- Game Frontend (Docker): Using port 3000 actively
- Control Center Frontend (Local): Wants port 3000

**Impact:** Cannot run Control Center Dashboard locally while game frontend container is running

**Solution:** Change Control Center Frontend to alternate port

### Issue 2: Backend Port Mismatch
**Problem:** Control Center backend running on port 54112 instead of 8080
- config.py specifies PORT: 8080
- Actual listening on: 54112 (VS Code's remote port)
- Frontend vite.config.js expects: 8080

**Impact:** Frontend cannot reach backend API at expected address

**Solution:** Update frontend configuration to point to actual backend location

### Issue 3: Configuration Inconsistency
**Problem:** Multiple inconsistent port references
- config.py: PORT = 8080 (configured)
- Actual: 54112 (running)
- vite.config.js: target: 'http://localhost:8080' (wrong)
- .env.example: VITE_API_URL=http://localhost:8080/api (wrong)

**Impact:** Services cannot find each other across development

---

## Recommended Solution: OPTION A (SELECTED)

### Strategy: Dedicate Port 3000 to Game, Move Control Center to Port 3001

**Rationale:**
1. **Game Frontend is Primary Production Asset**
   - Meow Ping RTS is the actual game product
   - Docker containerized (production-ready)
   - Should retain port 3000 (standard HTTP)

2. **Control Center is Development Tool**
   - Management interface for agents and knowledge base
   - Already on local machine
   - Can use alternate port 3001 (still standard HTTP range)

3. **Minimal Impact**
   - Only frontend port changes
   - Backend stays same
   - Easy to document and communicate

### Configuration Changes Required

#### 1. Update Control Center Frontend vite.config.js
**File:** `C:\Ziggie\control-center\control-center\frontend\vite.config.js`

Change from:
```javascript
server: {
  port: 3000,
  proxy: {
    '/api': {
      target: 'http://localhost:8080',
```

Change to:
```javascript
server: {
  port: 3001,
  proxy: {
    '/api': {
      target: 'http://localhost:54112',
```

**Rationale for Port 54112:**
- This is where the Control Center backend is actually running
- It's the current active port being used by FastAPI
- Rather than trying to move services, we align configuration with reality

#### 2. Update Control Center Frontend .env Files
**File:** `C:\Ziggie\control-center\control-center\frontend\.env.example`

Change from:
```
VITE_API_URL=http://localhost:8080/api
VITE_WS_URL=ws://localhost:8080/ws/system
```

Change to:
```
VITE_API_URL=http://localhost:54112/api
VITE_WS_URL=ws://localhost:54112/ws/system
```

If `.env` file exists, update it too.

#### 3. Update Control Center Backend config.py (Optional Enhancement)
**File:** `C:\Ziggie\control-center\control-center\backend\config.py`

Consider changing PORT configuration from 8080 to 54112:
```python
# Current
PORT: int = 8080

# Proposed (matches reality)
PORT: int = 54112
```

**Note:** This is optional if you want to standardize, but the backend is already working on 54112.

#### 4. Update CORS Configuration in Backend
**File:** `C:\Ziggie\control-center\control-center\backend\config.py`

Ensure CORS allows both ports:
```python
# Current - likely too restrictive
CORS_ORIGINS: list[str] = ["http://localhost:3000"]

# Updated - allows both services
CORS_ORIGINS: list[str] = [
    "http://localhost:3000",  # Game frontend
    "http://localhost:3001",  # Control Center frontend
    "http://localhost:54112"  # Backend API direct access
]
```

---

## Alternative Solutions (Not Recommended)

### Option B: Stop Docker Game Container
**Pros:**
- Simple port reassignment
- Existing config works

**Cons:**
- Loses production game access
- Defeats purpose of containerization
- User cannot test game and dashboard together

**Status:** NOT RECOMMENDED

### Option C: Change Backend to Port 8080
**Pros:**
- Matches original configuration intention

**Cons:**
- Port 8080 currently available but unclear if reserved for something else
- Requires stopping and restarting backend service
- May conflict with other services in future

**Status:** NOT RECOMMENDED (unless Option A fails)

---

## Step-by-Step Implementation Plan

### Phase 1: Assessment (5 minutes)
- [ ] Verify current port usage
- [ ] Confirm Docker containers running
- [ ] Check backend responsiveness
- [ ] Backup current configuration files

### Phase 2: Configuration Updates (10 minutes)
- [ ] Update vite.config.js
- [ ] Update .env files
- [ ] Update config.py (if proceeding with standardization)
- [ ] Update CORS configuration

### Phase 3: Testing (15 minutes)
- [ ] Start Control Center frontend on port 3001
- [ ] Verify frontend loads
- [ ] Test API connectivity
- [ ] Test WebSocket connections
- [ ] Confirm game frontend still works on 3000

### Phase 4: Documentation (10 minutes)
- [ ] Update startup scripts
- [ ] Document port mappings
- [ ] Create developer reference guide
- [ ] Update README files

### Phase 5: Verification (5 minutes)
- [ ] Test full stack together
- [ ] Verify both services accessible
- [ ] Check logs for errors
- [ ] Performance validation

---

## Detailed Implementation Commands

### Step 1: Backup Current Configuration
```bash
# Backup vite.config.js
copy "C:\Ziggie\control-center\control-center\frontend\vite.config.js" "C:\Ziggie\control-center\control-center\frontend\vite.config.js.backup"

# Backup config.py
copy "C:\Ziggie\control-center\control-center\backend\config.py" "C:\Ziggie\control-center\control-center\backend\config.py.backup"
```

### Step 2: Update vite.config.js
Replace the vite configuration with corrected ports.

### Step 3: Update Environment Files
Update all .env files to reflect correct backend port.

### Step 4: Start Services
```bash
# Keep Docker containers running (they provide game)
docker ps --all

# Start Control Center backend (if not already running)
cd "C:\Ziggie\control-center\control-center\backend"
python main.py

# In new terminal - Start Control Center frontend
cd "C:\Ziggie\control-center\control-center\frontend"
npm install  # if needed
npm run dev
```

### Step 5: Test Connectivity
```bash
# Test game frontend
curl http://localhost:3000

# Test Control Center frontend
curl http://localhost:3001

# Test Control Center backend
curl http://localhost:54112
curl http://localhost:54112/health
curl http://localhost:54112/api/services

# Test API connectivity from frontend
curl http://localhost:3001/api/services
```

---

## Final Port Mapping (After Implementation)

| Service | Host Port | Container Port | URL | Status |
|---------|-----------|-----------------|-----|--------|
| Game Frontend | 3000 | 3000 | http://localhost:3000 | Docker |
| Control Center Frontend | 3001 | N/A | http://localhost:3001 | Local Dev |
| Game Backend | 8000 | 8000 | http://localhost:8000 | Docker |
| Control Center Backend | 54112 | N/A | http://localhost:54112 | Local Dev |
| MongoDB | 27017 | 27017 | mongodb://localhost:27017 | Docker |

---

## Verification Checklist

- [ ] Game Frontend accessible at http://localhost:3000
- [ ] Control Center Dashboard accessible at http://localhost:3001
- [ ] Control Center Backend API responds at http://localhost:54112
- [ ] Frontend can fetch data from backend API
- [ ] WebSocket connections functional
- [ ] No port conflicts in netstat output
- [ ] CORS errors resolved
- [ ] Both systems can run simultaneously
- [ ] Agent management UI loads
- [ ] Services endpoint returns agent list

---

## Rollback Procedure

If issues occur:

```bash
# Restore from backup
copy "C:\Ziggie\control-center\control-center\frontend\vite.config.js.backup" "C:\Ziggie\control-center\control-center\frontend\vite.config.js"

# Restart services
# Kill existing node processes
# npm run dev (uses original config)
```

---

## Updated Documentation Files

After implementation, update these files:

1. **MIGRATION_COMPLETE.md**
   - Port configuration section
   - URLs after startup section

2. **README.md** (Control Center)
   - Port references
   - Startup instructions

3. **QUICK_START.md** (Ziggie)
   - Port information
   - Access URLs

4. **Start Scripts** (start_frontend.bat, etc.)
   - Updated port numbers
   - Updated API URLs

---

## Benefits of This Solution

1. **Minimal Changes**
   - Only frontend port and configuration updated
   - Backend continues operating
   - Game frontend completely unaffected

2. **Clear Port Allocation**
   - 3000: Game (production priority)
   - 3001: Control Center (development tool)
   - 8000: Game API (Docker)
   - 54112: Control Center API (current)

3. **Maintains Separation**
   - Different services on different ports
   - Easy to identify which service to access
   - Professional port allocation

4. **Scalable**
   - If more local services needed, can use 3002, 3003, etc.
   - Follows standard development practices

5. **Documented**
   - Clear mapping for all ports
   - Easy for team to understand
   - Prevents future conflicts

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| Port 3001 blocked | Low | Medium | Choose 3002, 3003 as fallback |
| Firewall blocks port | Low | Medium | Check Windows Firewall settings |
| Node crashes on start | Low | Low | Check logs, ensure dependencies installed |
| CORS still failing | Medium | Medium | Verify config.py CORS_ORIGINS updated |
| API unreachable | Medium | High | Verify backend running on 54112, test with curl |

---

## Success Metrics

After implementation, verify:

1. **Port Availability**
   - `netstat -ano | findstr ":3000 :3001 :8000 :54112"` shows correct usage
   - No unexpected processes on these ports

2. **Frontend Functionality**
   - Game loads at http://localhost:3000
   - Dashboard loads at http://localhost:3001

3. **Backend Connectivity**
   - Frontend successfully calls backend API
   - WebSocket connections established
   - No CORS errors in browser console

4. **Service Discovery**
   - `/api/services` endpoint returns agent list
   - `/api/agents` endpoint returns agents
   - `/health` endpoint responds healthy

5. **Simultaneous Operation**
   - Both services running together
   - Game frontend fully functional
   - Control Center dashboard fully functional

---

## Timeline

- **Assessment:** 5 minutes
- **Configuration:** 10 minutes
- **Testing:** 15 minutes
- **Documentation:** 10 minutes
- **Verification:** 5 minutes
- **Total:** ~45 minutes

---

## Support & Troubleshooting

If you encounter issues:

1. **Check Current Ports**
   ```bash
   netstat -ano | findstr "3000 3001 8000 8080 54112"
   ```

2. **Verify Backend Running**
   ```bash
   curl http://localhost:54112/health
   ```

3. **Check Frontend Logs**
   - Vite dev server console output
   - Browser developer console (F12)

4. **CORS Issues**
   - Update config.py CORS_ORIGINS
   - Ensure both hosts are listed

5. **WebSocket Errors**
   - Verify WS proxy target in vite.config.js
   - Check backend WebSocket support

---

## Conclusion

This solution provides a clean, minimal-disruption approach to resolving port conflicts post-migration. By allocating port 3001 to the Control Center Frontend and updating all configuration to reference port 54112 for the backend, both the Game Frontend and Control Center Dashboard can operate simultaneously without conflicts.

The strategy maintains system stability, preserves the game's production configuration, and provides clear port organization for future scalability.

**Next Steps:**
1. Execute Phase 1 (Assessment)
2. Execute Phase 2 (Configuration Updates)
3. Execute Phase 3-5 (Testing & Verification)
4. Update documentation files
5. Archive this strategy document for future reference

---

**Strategy Document Version:** 1.0
**Created by:** L1.9 - Migration Agent (Lead)
**Coordination Support:** L1.6, L1.3, L1.5, L1.2
**Status:** READY FOR IMPLEMENTATION
**Date:** November 7, 2025
