#!/bin/bash
# Run All Tests for Control Center Dashboard

echo "=========================================="
echo "Control Center - Complete Test Suite"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Track results
BACKEND_PASSED=0
FRONTEND_PASSED=0
E2E_PASSED=0
INTEGRATION_PASSED=0
PERFORMANCE_PASSED=0
SECURITY_PASSED=0

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo -e "${BLUE}Test Suite Directory: $SCRIPT_DIR${NC}"
echo ""

# 1. Backend Tests
echo -e "${YELLOW}[1/6] Running Backend Tests...${NC}"
echo "=========================================="
if [ -f "$SCRIPT_DIR/run_backend_tests.sh" ]; then
    bash "$SCRIPT_DIR/run_backend_tests.sh"
    if [ $? -eq 0 ]; then
        BACKEND_PASSED=1
        echo -e "${GREEN}✓ Backend tests passed${NC}"
    else
        echo -e "${RED}✗ Backend tests failed${NC}"
    fi
else
    echo -e "${YELLOW}⚠ Backend test script not found${NC}"
fi
echo ""

# 2. Frontend Tests
echo -e "${YELLOW}[2/6] Running Frontend Tests...${NC}"
echo "=========================================="
if [ -f "$SCRIPT_DIR/run_frontend_tests.sh" ]; then
    bash "$SCRIPT_DIR/run_frontend_tests.sh"
    if [ $? -eq 0 ]; then
        FRONTEND_PASSED=1
        echo -e "${GREEN}✓ Frontend tests passed${NC}"
    else
        echo -e "${RED}✗ Frontend tests failed${NC}"
    fi
else
    echo -e "${YELLOW}⚠ Frontend test script not found${NC}"
fi
echo ""

# 3. Integration Tests
echo -e "${YELLOW}[3/6] Running Integration Tests...${NC}"
echo "=========================================="
cd "$SCRIPT_DIR" || exit 1
if [ -d "tests/integration" ]; then
    python -m pytest tests/integration/ --verbose
    if [ $? -eq 0 ]; then
        INTEGRATION_PASSED=1
        echo -e "${GREEN}✓ Integration tests passed${NC}"
    else
        echo -e "${RED}✗ Integration tests failed${NC}"
    fi
else
    echo -e "${YELLOW}⚠ Integration tests not found${NC}"
fi
echo ""

# 4. End-to-End Tests
echo -e "${YELLOW}[4/6] Running End-to-End Tests...${NC}"
echo "=========================================="
if [ -d "tests/e2e" ]; then
    python -m pytest tests/e2e/ --verbose
    if [ $? -eq 0 ]; then
        E2E_PASSED=1
        echo -e "${GREEN}✓ E2E tests passed${NC}"
    else
        echo -e "${RED}✗ E2E tests failed${NC}"
    fi
else
    echo -e "${YELLOW}⚠ E2E tests not found${NC}"
fi
echo ""

# 5. Performance Tests
echo -e "${YELLOW}[5/6] Running Performance Tests...${NC}"
echo "=========================================="
if [ -d "tests/performance" ]; then
    python -m pytest tests/performance/ --verbose
    if [ $? -eq 0 ]; then
        PERFORMANCE_PASSED=1
        echo -e "${GREEN}✓ Performance tests passed${NC}"
    else
        echo -e "${RED}✗ Performance tests failed${NC}"
    fi
else
    echo -e "${YELLOW}⚠ Performance tests not found${NC}"
fi
echo ""

# 6. Security Tests
echo -e "${YELLOW}[6/6] Running Security Tests...${NC}"
echo "=========================================="
if [ -d "tests/security" ]; then
    python -m pytest tests/security/ --verbose
    if [ $? -eq 0 ]; then
        SECURITY_PASSED=1
        echo -e "${GREEN}✓ Security tests passed${NC}"
    else
        echo -e "${RED}✗ Security tests failed${NC}"
    fi
else
    echo -e "${YELLOW}⚠ Security tests not found${NC}"
fi
echo ""

# Summary
echo ""
echo "=========================================="
echo "Test Suite Summary"
echo "=========================================="
echo ""

TOTAL_PASSED=$((BACKEND_PASSED + FRONTEND_PASSED + E2E_PASSED + INTEGRATION_PASSED + PERFORMANCE_PASSED + SECURITY_PASSED))
TOTAL_TESTS=6

echo "Results:"
echo ""
[ $BACKEND_PASSED -eq 1 ] && echo -e "${GREEN}✓${NC} Backend Tests" || echo -e "${RED}✗${NC} Backend Tests"
[ $FRONTEND_PASSED -eq 1 ] && echo -e "${GREEN}✓${NC} Frontend Tests" || echo -e "${RED}✗${NC} Frontend Tests"
[ $INTEGRATION_PASSED -eq 1 ] && echo -e "${GREEN}✓${NC} Integration Tests" || echo -e "${RED}✗${NC} Integration Tests"
[ $E2E_PASSED -eq 1 ] && echo -e "${GREEN}✓${NC} End-to-End Tests" || echo -e "${RED}✗${NC} End-to-End Tests"
[ $PERFORMANCE_PASSED -eq 1 ] && echo -e "${GREEN}✓${NC} Performance Tests" || echo -e "${RED}✗${NC} Performance Tests"
[ $SECURITY_PASSED -eq 1 ] && echo -e "${GREEN}✓${NC} Security Tests" || echo -e "${RED}✗${NC} Security Tests"

echo ""
echo "Total: $TOTAL_PASSED/$TOTAL_TESTS test suites passed"
echo ""

if [ $TOTAL_PASSED -eq $TOTAL_TESTS ]; then
    echo -e "${GREEN}=========================================="
    echo "🎉 ALL TESTS PASSED! 🎉"
    echo "==========================================${NC}"
    exit 0
else
    echo -e "${RED}=========================================="
    echo "⚠ SOME TESTS FAILED"
    echo "==========================================${NC}"
    exit 1
fi
