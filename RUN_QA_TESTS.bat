@echo off
REM Ziggie Control Center - QA Testing Suite
REM Run this batch file to execute comprehensive QA tests

echo ================================================================================
echo                    ZIGGIE CONTROL CENTER - QA TESTING
echo ================================================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ and try again
    pause
    exit /b 1
)

REM Check if backend is running
echo Checking if backend is running on port 54112...
netstat -ano | findstr ":54112" | findstr "LISTENING" >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo WARNING: Backend does not appear to be running on port 54112
    echo Please start the backend first:
    echo    cd control-center\backend
    echo    python main.py
    echo.
    pause
    exit /b 1
)

echo Backend is running ✓
echo.

REM Run the test suite
echo Running comprehensive QA test suite...
echo.
python l2_qa_comprehensive_test.py

REM Check exit code
if %errorlevel% equ 0 (
    echo.
    echo ================================================================================
    echo                        ALL TESTS PASSED!
    echo ================================================================================
    echo.
    echo System is ready for production deployment.
    echo.
) else (
    echo.
    echo ================================================================================
    echo                        TESTS FAILED
    echo ================================================================================
    echo.
    echo Some tests failed. Review the output above for details.
    echo Check the following reports:
    echo   - QA_QUICK_STATUS.txt
    echo   - QA_EXECUTIVE_SUMMARY.md
    echo   - L2_QA_COMPREHENSIVE_REPORT.md
    echo.
)

echo Press any key to view quick status...
pause >nul
type QA_QUICK_STATUS.txt
echo.

echo Press any key to exit...
pause >nul
