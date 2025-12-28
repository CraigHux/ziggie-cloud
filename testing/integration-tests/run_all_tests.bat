@echo off
REM Run All Tests for Control Center Dashboard (Windows)

echo ==========================================
echo Control Center - Complete Test Suite
echo ==========================================
echo.

REM Track results
set BACKEND_PASSED=0
set FRONTEND_PASSED=0
set INTEGRATION_PASSED=0
set E2E_PASSED=0
set PERFORMANCE_PASSED=0
set SECURITY_PASSED=0

REM Get script directory
set SCRIPT_DIR=%~dp0

echo Test Suite Directory: %SCRIPT_DIR%
echo.

REM 1. Backend Tests
echo [1/6] Running Backend Tests...
echo ==========================================
cd /d "%SCRIPT_DIR%backend"
if exist "tests" (
    python -m pytest tests\ --verbose --cov=. --cov-report=html
    if %ERRORLEVEL% EQU 0 (
        set BACKEND_PASSED=1
        echo [OK] Backend tests passed
    ) else (
        echo [FAIL] Backend tests failed
    )
) else (
    echo [WARN] Backend tests not found
)
echo.

REM 2. Frontend Tests
echo [2/6] Running Frontend Tests...
echo ==========================================
cd /d "%SCRIPT_DIR%frontend"
if exist "src\__tests__" (
    call npm test -- --coverage --ci
    if %ERRORLEVEL% EQU 0 (
        set FRONTEND_PASSED=1
        echo [OK] Frontend tests passed
    ) else (
        echo [FAIL] Frontend tests failed
    )
) else (
    echo [WARN] Frontend tests not found
)
echo.

REM 3. Integration Tests
echo [3/6] Running Integration Tests...
echo ==========================================
cd /d "%SCRIPT_DIR%"
if exist "tests\integration" (
    python -m pytest tests\integration\ --verbose
    if %ERRORLEVEL% EQU 0 (
        set INTEGRATION_PASSED=1
        echo [OK] Integration tests passed
    ) else (
        echo [FAIL] Integration tests failed
    )
) else (
    echo [WARN] Integration tests not found
)
echo.

REM 4. End-to-End Tests
echo [4/6] Running End-to-End Tests...
echo ==========================================
if exist "tests\e2e" (
    python -m pytest tests\e2e\ --verbose
    if %ERRORLEVEL% EQU 0 (
        set E2E_PASSED=1
        echo [OK] E2E tests passed
    ) else (
        echo [FAIL] E2E tests failed
    )
) else (
    echo [WARN] E2E tests not found
)
echo.

REM 5. Performance Tests
echo [5/6] Running Performance Tests...
echo ==========================================
if exist "tests\performance" (
    python -m pytest tests\performance\ --verbose
    if %ERRORLEVEL% EQU 0 (
        set PERFORMANCE_PASSED=1
        echo [OK] Performance tests passed
    ) else (
        echo [FAIL] Performance tests failed
    )
) else (
    echo [WARN] Performance tests not found
)
echo.

REM 6. Security Tests
echo [6/6] Running Security Tests...
echo ==========================================
if exist "tests\security" (
    python -m pytest tests\security\ --verbose
    if %ERRORLEVEL% EQU 0 (
        set SECURITY_PASSED=1
        echo [OK] Security tests passed
    ) else (
        echo [FAIL] Security tests failed
    )
) else (
    echo [WARN] Security tests not found
)
echo.

REM Summary
echo.
echo ==========================================
echo Test Suite Summary
echo ==========================================
echo.

set /a TOTAL_PASSED=%BACKEND_PASSED%+%FRONTEND_PASSED%+%INTEGRATION_PASSED%+%E2E_PASSED%+%PERFORMANCE_PASSED%+%SECURITY_PASSED%

echo Results:
echo.
if %BACKEND_PASSED%==1 (echo [OK] Backend Tests) else (echo [FAIL] Backend Tests)
if %FRONTEND_PASSED%==1 (echo [OK] Frontend Tests) else (echo [FAIL] Frontend Tests)
if %INTEGRATION_PASSED%==1 (echo [OK] Integration Tests) else (echo [FAIL] Integration Tests)
if %E2E_PASSED%==1 (echo [OK] End-to-End Tests) else (echo [FAIL] End-to-End Tests)
if %PERFORMANCE_PASSED%==1 (echo [OK] Performance Tests) else (echo [FAIL] Performance Tests)
if %SECURITY_PASSED%==1 (echo [OK] Security Tests) else (echo [FAIL] Security Tests)

echo.
echo Total: %TOTAL_PASSED%/6 test suites passed
echo.

if %TOTAL_PASSED%==6 (
    echo ==========================================
    echo ALL TESTS PASSED!
    echo ==========================================
    exit /b 0
) else (
    echo ==========================================
    echo SOME TESTS FAILED
    echo ==========================================
    exit /b 1
)
