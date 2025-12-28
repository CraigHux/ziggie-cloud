#!/bin/bash
# Run Backend Tests for Control Center Dashboard

echo "=========================================="
echo "Control Center - Backend Tests"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Change to backend directory
cd "$(dirname "$0")/backend" || exit 1

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python -m venv venv
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
if [ -f "venv/Scripts/activate" ]; then
    source venv/Scripts/activate  # Windows Git Bash
elif [ -f "venv/bin/activate" ]; then
    source venv/bin/activate  # Unix/Linux/Mac
fi

# Install test requirements
echo -e "${YELLOW}Installing test dependencies...${NC}"
pip install -q -r tests/requirements.txt

echo ""
echo "=========================================="
echo "Running Backend Tests"
echo "=========================================="
echo ""

# Run pytest with coverage
pytest tests/ \
    --verbose \
    --cov=. \
    --cov-report=html \
    --cov-report=term-missing \
    --cov-report=json \
    --junit-xml=test-results.xml

TEST_EXIT_CODE=$?

echo ""
echo "=========================================="
echo "Test Results"
echo "=========================================="
echo ""

if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✓ All backend tests passed!${NC}"
else
    echo -e "${RED}✗ Some backend tests failed${NC}"
fi

echo ""
echo "Coverage report generated in: backend/htmlcov/index.html"
echo "JUnit XML report: backend/test-results.xml"
echo ""

exit $TEST_EXIT_CODE
