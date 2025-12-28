#!/bin/bash
###############################################################################
# Ziggie Control Center - Health Check Script
# Purpose: Comprehensive health monitoring for the Control Center
# Version: 1.0
# Author: Monitoring Specialist (L3.MONITORING.SETUP)
# Date: 2025-11-10
#
# Usage: ./health_check.sh
# Exit Codes:
#   0 = All checks passed, system is healthy
#   1 = One or more checks failed, issues detected
#
# Description:
# This script performs comprehensive health checks on the Ziggie Control Center,
# including backend service connectivity, configuration validation, system stats
# verification, and frontend environment configuration checks.
###############################################################################

set -e

# Configuration
BACKEND_URL="http://127.0.0.1:54112"
BACKEND_HOST="127.0.0.1"
BACKEND_PORT="54112"
FRONTEND_CONFIG_PATH="C:\\Ziggie\\control-center\\frontend\\.env"
COMFYUI_DIR="C:\\ComfyUI"
AI_AGENTS_DIR="C:\\Ziggie\\ai-agents"
MEOWPING_DIR="C:\\Ziggie"
CURL_TIMEOUT=5
MAX_RESPONSE_TIME_MS=5000

# State variables
FAILED_CHECKS=0
WARNINGS=0
PASSED_CHECKS=0
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# ANSI color codes (for terminal output)
COLOR_GREEN='\033[0;32m'
COLOR_RED='\033[0;31m'
COLOR_YELLOW='\033[1;33m'
COLOR_BLUE='\033[0;34m'
COLOR_RESET='\033[0m'

###############################################################################
# Helper Functions
###############################################################################

# Print colored status message
print_status() {
  local status=$1
  local message=$2

  if [ "$status" = "PASS" ]; then
    echo -e "${COLOR_GREEN}✓ PASS:${COLOR_RESET} $message"
    PASSED_CHECKS=$((PASSED_CHECKS + 1))
  elif [ "$status" = "FAIL" ]; then
    echo -e "${COLOR_RED}✗ FAIL:${COLOR_RESET} $message"
    FAILED_CHECKS=$((FAILED_CHECKS + 1))
  elif [ "$status" = "WARN" ]; then
    echo -e "${COLOR_YELLOW}⚠ WARN:${COLOR_RESET} $message"
    WARNINGS=$((WARNINGS + 1))
  else
    echo -e "${COLOR_BLUE}→${COLOR_RESET} $message"
  fi
}

# Print section header
print_section() {
  echo ""
  echo -e "${COLOR_BLUE}========================================${COLOR_RESET}"
  echo -e "${COLOR_BLUE}$1${COLOR_RESET}"
  echo -e "${COLOR_BLUE}========================================${COLOR_RESET}"
}

# Print final summary
print_summary() {
  echo ""
  echo -e "${COLOR_BLUE}========================================${COLOR_RESET}"
  echo -e "${COLOR_BLUE}HEALTH CHECK SUMMARY${COLOR_RESET}"
  echo -e "${COLOR_BLUE}========================================${COLOR_RESET}"
  echo "Timestamp: $TIMESTAMP"
  echo -e "${COLOR_GREEN}Passed:${COLOR_RESET} $PASSED_CHECKS"
  echo -e "${COLOR_YELLOW}Warnings:${COLOR_RESET} $WARNINGS"
  echo -e "${COLOR_RED}Failed:${COLOR_RESET} $FAILED_CHECKS"
  echo ""
}

###############################################################################
# Check Functions
###############################################################################

# Check 1: Backend Service Health Endpoint
check_backend_health() {
  print_section "BACKEND HEALTH CHECK"

  echo "Testing: GET $BACKEND_URL/api/health"

  local response
  local http_code

  # Use curl to test the health endpoint with timeout
  response=$(curl -s -w "\n%{http_code}" \
    --max-time "$CURL_TIMEOUT" \
    "$BACKEND_URL/api/health" 2>/dev/null || echo "")

  # Extract HTTP code (last line)
  http_code=$(echo "$response" | tail -n1)

  # Check if we got a response
  if [ -z "$http_code" ] || [ "$http_code" = "000" ]; then
    print_status "FAIL" "Backend not responding (timeout or connection refused)"
    return 1
  elif [ "$http_code" = "200" ]; then
    print_status "PASS" "Backend healthy (HTTP $http_code)"
    return 0
  else
    print_status "FAIL" "Backend unhealthy (HTTP $http_code)"
    return 1
  fi
}

# Check 2: Backend Service Port Listening
check_backend_port() {
  print_section "BACKEND PORT LISTENING CHECK"

  echo "Testing: Is port $BACKEND_PORT listening on $BACKEND_HOST?"

  # For cross-platform compatibility, use netstat
  if command -v netstat &> /dev/null; then
    if netstat -an | grep -q "$BACKEND_PORT"; then
      print_status "PASS" "Backend port $BACKEND_PORT is listening"
      return 0
    else
      print_status "FAIL" "Backend port $BACKEND_PORT is not listening"
      return 1
    fi
  else
    print_status "WARN" "netstat not available, skipping port check"
    return 0
  fi
}

# Check 3: System Stats Endpoint - Real Data Validation
check_system_stats() {
  print_section "SYSTEM STATS VALIDATION"

  echo "Testing: GET $BACKEND_URL/api/system/stats"

  local stats_response
  local cpu_usage

  # Fetch system stats
  stats_response=$(curl -s \
    --max-time "$CURL_TIMEOUT" \
    "$BACKEND_URL/api/system/stats" 2>/dev/null || echo "{}")

  # Check if response is valid JSON
  if ! echo "$stats_response" | grep -q '"cpu"'; then
    print_status "FAIL" "System stats endpoint not returning valid data"
    return 1
  fi

  # Extract CPU usage percentage
  cpu_usage=$(echo "$stats_response" | grep -o '"usage_percent":[0-9.]*' | head -1 | cut -d':' -f2)

  # Validate that we're getting real data (not all zeros)
  if [ "$cpu_usage" = "0.0" ] || [ -z "$cpu_usage" ]; then
    print_status "FAIL" "System stats returning mock data (CPU: $cpu_usage%) - backend may need restart"
    return 1
  elif [ -z "$(echo "$cpu_usage" | grep -E '^[0-9]+\.[0-9]$|^[0-9]+$')" ]; then
    print_status "WARN" "System stats CPU value may be invalid (CPU: $cpu_usage%)"
    return 0
  else
    print_status "PASS" "System stats returning real data (CPU: $cpu_usage%)"
    return 0
  fi
}

# Check 4: Backend Configuration File
check_backend_config() {
  print_section "BACKEND CONFIGURATION CHECK"

  local backend_env="C:\\Ziggie\\control-center\\backend\\.env"

  echo "Checking: $backend_env"

  if [ -f "$backend_env" ]; then
    print_status "PASS" "Backend .env configuration file exists"

    # Check for required variables
    if grep -q "PORT=54112" "$backend_env"; then
      print_status "PASS" "Backend PORT configured correctly (54112)"
    else
      print_status "WARN" "Backend PORT not set to 54112"
    fi

    if grep -q "HOST=127.0.0.1" "$backend_env"; then
      print_status "PASS" "Backend HOST configured correctly (127.0.0.1)"
    else
      print_status "WARN" "Backend HOST not set to 127.0.0.1"
    fi

    return 0
  else
    print_status "FAIL" "Backend .env configuration file missing"
    return 1
  fi
}

# Check 5: Frontend Configuration File
check_frontend_config() {
  print_section "FRONTEND CONFIGURATION CHECK"

  local frontend_env="C:\\Ziggie\\control-center\\frontend\\.env"

  echo "Checking: $frontend_env"

  if [ ! -f "$frontend_env" ]; then
    print_status "FAIL" "Frontend .env configuration file missing"
    return 1
  fi

  print_status "PASS" "Frontend .env configuration file exists"

  # Check VITE_API_URL
  if grep -q "VITE_API_URL=http://127.0.0.1:54112/api" "$frontend_env"; then
    print_status "PASS" "VITE_API_URL configured correctly"
  else
    local actual_url
    actual_url=$(grep "VITE_API_URL" "$frontend_env" 2>/dev/null || echo "not found")
    print_status "FAIL" "VITE_API_URL mismatch - Expected: http://127.0.0.1:54112/api, Found: $actual_url"
    return 1
  fi

  # Check VITE_WS_URL
  if grep -q "VITE_WS_URL=ws://127.0.0.1:54112/api/system/ws" "$frontend_env"; then
    print_status "PASS" "VITE_WS_URL configured correctly"
  else
    local actual_ws_url
    actual_ws_url=$(grep "VITE_WS_URL" "$frontend_env" 2>/dev/null || echo "not found")
    print_status "WARN" "VITE_WS_URL mismatch - Expected: ws://127.0.0.1:54112/api/system/ws, Found: $actual_ws_url"
  fi

  return 0
}

# Check 6: Critical Paths Existence
check_critical_paths() {
  print_section "CRITICAL PATHS VALIDATION"

  # Check ComfyUI directory
  if [ -d "$COMFYUI_DIR" ]; then
    print_status "PASS" "ComfyUI directory exists: $COMFYUI_DIR"
  else
    print_status "WARN" "ComfyUI directory not found: $COMFYUI_DIR"
  fi

  # Check AI Agents directory
  if [ -d "$AI_AGENTS_DIR" ]; then
    print_status "PASS" "AI Agents directory exists: $AI_AGENTS_DIR"
  else
    print_status "WARN" "AI Agents directory not found: $AI_AGENTS_DIR"
  fi

  # Check Ziggie root directory
  if [ -d "$MEOWPING_DIR" ]; then
    print_status "PASS" "Ziggie root directory exists: $MEOWPING_DIR"
  else
    print_status "FAIL" "Ziggie root directory not found: $MEOWPING_DIR"
    return 1
  fi

  return 0
}

# Check 7: Database/Backend Data Connection
check_database_connectivity() {
  print_section "DATABASE CONNECTIVITY CHECK"

  echo "Testing: Backend database connectivity via stats endpoint"

  local stats_response
  stats_response=$(curl -s \
    --max-time "$CURL_TIMEOUT" \
    "$BACKEND_URL/api/system/stats" 2>/dev/null || echo "{}")

  # If we can get stats, database is likely connected
  if echo "$stats_response" | grep -q '"memory"'; then
    print_status "PASS" "Database/Backend data connection working"
    return 0
  else
    print_status "WARN" "Cannot verify database connectivity"
    return 0
  fi
}

###############################################################################
# Main Execution
###############################################################################

main() {
  echo ""
  echo -e "${COLOR_BLUE}╔════════════════════════════════════════╗${COLOR_RESET}"
  echo -e "${COLOR_BLUE}║ Ziggie Control Center - Health Check   ║${COLOR_RESET}"
  echo -e "${COLOR_BLUE}║ Started: $TIMESTAMP         ║${COLOR_RESET}"
  echo -e "${COLOR_BLUE}╚════════════════════════════════════════╝${COLOR_RESET}"

  # Run all checks
  check_backend_health
  check_backend_port
  check_system_stats
  check_backend_config
  check_frontend_config
  check_critical_paths
  check_database_connectivity

  # Print summary
  print_summary

  # Determine exit code
  if [ $FAILED_CHECKS -eq 0 ]; then
    echo -e "${COLOR_GREEN}Status: HEALTHY - System is operational${COLOR_RESET}"
    echo "All critical checks passed. No immediate action required."
    exit 0
  else
    echo -e "${COLOR_RED}Status: UNHEALTHY - Issues detected${COLOR_RESET}"
    echo "$FAILED_CHECKS critical check(s) failed. Immediate investigation required."
    if [ $WARNINGS -gt 0 ]; then
      echo "$WARNINGS warning(s) detected. Please review."
    fi
    exit 1
  fi
}

# Execute main function
main
