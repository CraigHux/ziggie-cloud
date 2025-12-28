# Control Center Dashboard - Testing Quick Start

Quick reference guide for running tests on the Control Center Dashboard.

---

## Installation

### Backend Tests

```bash
cd C:\meowping-rts\control-center\backend
pip install -r tests/requirements.txt
```

### Frontend Tests

```bash
cd C:\meowping-rts\control-center\frontend
npm install
```

---

## Running Tests

### Quick Commands

**Run Everything (Windows):**
```batch
cd C:\meowping-rts\control-center
run_all_tests.bat
```

**Run Everything (Git Bash/Unix):**
```bash
cd /c/meowping-rts/control-center
bash run_all_tests.sh
```

### Individual Test Suites

**Backend Tests:**
```bash
cd C:\meowping-rts\control-center\backend
pytest tests/ -v
```

**Frontend Tests:**
```bash
cd C:\meowping-rts\control-center\frontend
npm test
```

**Integration Tests:**
```bash
cd C:\meowping-rts\control-center
pytest tests/integration/ -v
```

**E2E Tests:**
```bash
pytest tests/e2e/ -v
```

**Performance Tests:**
```bash
pytest tests/performance/ -v
```

**Security Tests:**
```bash
pytest tests/security/ -v
```

---

## Coverage Reports

**Backend Coverage:**
```bash
cd backend
pytest tests/ --cov=. --cov-report=html
# Open: backend/htmlcov/index.html
```

**Frontend Coverage:**
```bash
cd frontend
npm test -- --coverage
# Open: frontend/coverage/lcov-report/index.html
```

---

## Test Status

### Current State

The test infrastructure is **COMPLETE and READY** for execution.

Tests will automatically skip features that are not yet implemented and execute as components become available.

### Test Statistics

- **Total Test Files:** 14
- **Total Test Cases:** 159
- **Categories:** 6 (Backend, Frontend, E2E, Integration, Performance, Security)
- **Automation Scripts:** 4

---

## Expected Results

When the system is fully implemented, all tests should pass:

```
==========================================
Test Suite Summary
==========================================

✓ Backend Tests (57 tests)
✓ Frontend Tests (51 tests)
✓ Integration Tests (20 tests)
✓ End-to-End Tests (7 tests)
✓ Performance Tests (11 tests)
✓ Security Tests (13 tests)

Total: 6/6 test suites passed
==========================================
🎉 ALL TESTS PASSED! 🎉
==========================================
```

---

## Troubleshooting

**Tests Skip with "Not implemented":**
- This is expected until other agents complete their work
- Tests will automatically execute when features are available

**Backend not running error:**
- Start the backend: `cd backend && python main.py`
- Or skip with: `pytest -k "not backend"`

**Frontend not running error:**
- Start the frontend: `cd frontend && npm start`
- Or skip with: `pytest -k "not frontend"`

**Module not found:**
- Install dependencies: `pip install -r tests/requirements.txt`
- For frontend: `npm install`

---

## Contact

**Created by:** L1.8 - Quality Assurance Agent
**Date:** November 7, 2025

For detailed information, see `TESTING_REPORT.md`

---
