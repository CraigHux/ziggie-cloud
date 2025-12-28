# Port Conflict Fix - Quick Start Guide

## Problem Resolved
Game Frontend (port 3000) and Control Center Dashboard (port 3001) can now run together.

## What Changed
- **Control Center Frontend:** Moved from port 3000 to **3001**
- **Backend API Target:** Changed from port 8080 to **54112**
- **CORS Configuration:** Now allows both ports 3000 and 3001

## How to Use

### Start Control Center Dashboard
```bash
cd "C:\Ziggie\control-center\control-center\frontend"
npm install    # if needed
npm run dev
```

**Access at:** http://localhost:3001

### Verify Both Services Running
```bash
# Check ports in use
netstat -ano | findstr "3000 3001 8000 54112"

# Test backend
curl http://localhost:54112/health

# Test Game (if Docker running)
curl http://localhost:3000

# Test Control Center
curl http://localhost:3001
```

## Access URLs
| Service | URL |
|---------|-----|
| Game Frontend | http://localhost:3000 |
| Control Center | http://localhost:3001 |
| Backend API | http://localhost:54112 |
| API Docs | http://localhost:54112/docs |

## Troubleshooting

**Control Center won't start?**
- Check if port 3001 is free: `netstat -ano | findstr :3001`
- Clear node_modules: `rm -r node_modules && npm install`

**Can't reach backend?**
- Verify it's running: `curl http://localhost:54112/health`
- Check frontend proxy in vite.config.js points to 54112

**CORS errors?**
- Check config.py includes http://localhost:3001 in CORS_ORIGINS
- Restart backend if changed

## Files Modified
1. `C:\Ziggie\control-center\control-center\frontend\vite.config.js`
2. `C:\Ziggie\control-center\control-center\frontend\.env.example`
3. `C:\Ziggie\control-center\control-center\backend\config.py`

## Detailed Documentation
- Full strategy: `C:\Ziggie\PORT_CONFLICT_RESOLUTION_STRATEGY.md`
- Implementation: `C:\Ziggie\PORT_CONFLICT_IMPLEMENTATION_COMPLETE.md`
- Coordination: `C:\Ziggie\L1.9_MIGRATION_COORDINATION_REPORT.md`

---
**Status:** ✓ READY TO USE
**Last Updated:** November 7, 2025
