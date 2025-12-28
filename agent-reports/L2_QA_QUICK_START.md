# L2.QA.VERIFICATION - Quick Start Testing Guide

**Location:** `c:\Ziggie\agent-reports\BRAINSTORM_L2_QA_VERIFICATION.md` (44KB, comprehensive)

## TL;DR - Run These 15 Tests

### Frontend Tests (30 min)
```
F1: Dashboard page loads               http://localhost:3001
F2: System stats show real values      CPU/Memory/Disk not 0.0%
F3: Services widget displays           Check list shows running services
F4: Agent counts are real              > 0 agents, math checks out
F5: All 5 pages load without errors    /, /services, /knowledge, /agents, /performance
F6: Browser console = zero errors      F12 → Console → must be empty
F7: Auth headers sent correctly        F12 → Network → check Authorization header
F8: Auth token in localStorage         F12 → Application → localStorage has token
```

### Backend Tests (15 min)
```
B1: curl -X GET http://localhost:54112/api/health
    Must return: HTTP 200, status="healthy"

B2: curl -X GET http://localhost:54112/api/system/stats \
      -H "Authorization: Bearer <token>"
    Must return: real metrics (0-100%), not 0.0%

B3: curl -X GET http://localhost:54112/api/services
    Must return: service list or empty array, pagination metadata

B4: curl -X POST http://localhost:54112/api/auth/login \
      -H "Content-Type: application/json" \
      -d '{"username":"admin","password":"admin"}'
    Must return: JWT token (not "token123", real JWT)
```

### Integration Tests (20 min)
```
I1: Login flow end-to-end              Clear cookies → Login → Dashboard
I2: Data flows from API to UI          Check API response matches displayed values
I3: Backend offline handling           Stop backend → see error → Start → reconnect
```

## Critical Success Factors

1. **Real Data, Not Mock**
   - CPU% not 0.0%, not hardcoded, between 0-100%
   - Memory, Disk same rules
   - Agent counts > 0

2. **Zero Console Errors**
   - F12 → Console → RED must be 0
   - Yellow warnings OK
   - This catches silent failures

3. **Authentication Working**
   - Login returns real JWT (not "token123")
   - Bearer token sent with requests
   - Token format: eyJhbGc... (3 dots inside)

4. **Frontend-Backend Integration**
   - Frontend can reach backend (no CORS errors)
   - Frontend uses auth token correctly
   - Data displayed matches API response

## Automated Tests (Optional but Recommended)

See **Section 5** of main document for:
- Vitest + React Testing Library setup
- Pytest backend test templates
- Playwright E2E test examples
- GitHub Actions CI/CD config

## Sign-Off

Only mark system as "READY" if:
- [x] All 15 tests pass
- [x] No critical issues
- [x] Performance acceptable (< 3s page load)
- [x] Zero false "success" claims

---

**Full details:** See BRAINSTORM_L2_QA_VERIFICATION.md (sections 1-10)
