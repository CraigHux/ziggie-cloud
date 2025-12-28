#!/bin/bash
# Run Frontend Tests for Control Center Dashboard

echo "=========================================="
echo "Control Center - Frontend Tests"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Change to frontend directory
cd "$(dirname "$0")/frontend" || exit 1

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}Installing dependencies...${NC}"
    npm install
fi

# Install test dependencies if needed
echo -e "${YELLOW}Installing test dependencies...${NC}"
npm install --save-dev \
    @testing-library/react \
    @testing-library/jest-dom \
    @testing-library/user-event \
    @babel/preset-env \
    @babel/preset-react \
    babel-jest \
    jest \
    jest-environment-jsdom \
    identity-obj-proxy

echo ""
echo "=========================================="
echo "Running Frontend Tests"
echo "=========================================="
echo ""

# Run Jest tests
npm test -- \
    --coverage \
    --verbose \
    --ci \
    --json \
    --outputFile=test-results.json

TEST_EXIT_CODE=$?

echo ""
echo "=========================================="
echo "Test Results"
echo "=========================================="
echo ""

if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✓ All frontend tests passed!${NC}"
else
    echo -e "${RED}✗ Some frontend tests failed${NC}"
fi

echo ""
echo "Coverage report generated in: frontend/coverage/"
echo "Test results: frontend/test-results.json"
echo ""

exit $TEST_EXIT_CODE
