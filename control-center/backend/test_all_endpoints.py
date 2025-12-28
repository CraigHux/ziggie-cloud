"""
Comprehensive endpoint testing script for Control Center Backend
Tests all fixed and existing endpoints
"""
import requests
import json
import time
from typing import Dict, List, Tuple

BASE_URL = "http://127.0.0.1:54112"

class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_test(name: str, status: bool, message: str = "", data: dict = None):
    """Print test result with color coding"""
    symbol = f"{Colors.GREEN}[PASS]{Colors.END}" if status else f"{Colors.RED}[FAIL]{Colors.END}"
    print(f"{symbol} {name}")
    if message:
        print(f"  {Colors.YELLOW}>{Colors.END} {message}")
    if data:
        print(f"  {Colors.BLUE}Data:{Colors.END} {json.dumps(data, indent=2)[:200]}...")
    print()

def test_endpoint(method: str, endpoint: str, expected_keys: List[str] = None, params: Dict = None) -> Tuple[bool, str, dict]:
    """Test a single endpoint"""
    url = f"{BASE_URL}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url, params=params, timeout=5)
        elif method == "POST":
            response = requests.post(url, timeout=5)
        else:
            return False, f"Unsupported method: {method}", {}

        if response.status_code not in [200, 201]:
            return False, f"Status {response.status_code}", {}

        try:
            data = response.json()
        except:
            return False, "Invalid JSON response", {}

        # Check for expected keys
        if expected_keys:
            missing = [k for k in expected_keys if k not in data]
            if missing:
                return False, f"Missing keys: {missing}", data

        return True, f"Status {response.status_code}", data

    except requests.exceptions.Timeout:
        return False, "Request timeout", {}
    except requests.exceptions.ConnectionError:
        return False, "Connection refused - server not running?", {}
    except Exception as e:
        return False, f"Error: {str(e)}", {}

def main():
    print("=" * 80)
    print(f"{Colors.BLUE}Control Center Backend - Comprehensive Endpoint Tests{Colors.END}")
    print("=" * 80)
    print()

    # Test counters
    passed = 0
    failed = 0

    # Group 1: System Endpoints
    print(f"{Colors.BLUE}=== SYSTEM ENDPOINTS ==={Colors.END}")
    print()

    # Test 1: System Info (FIXED)
    success, msg, data = test_endpoint("GET", "/api/system/info",
                                       expected_keys=["os", "python", "hostname", "uptime"])
    print_test("System Info (/api/system/info)", success, msg, data if success else None)
    passed += success
    failed += not success

    # Test 2: System Stats
    success, msg, data = test_endpoint("GET", "/api/system/stats",
                                       expected_keys=["cpu", "memory", "disk"])
    print_test("System Stats (/api/system/stats)", success, msg, data if success else None)
    passed += success
    failed += not success

    # Test 3: System Processes
    success, msg, data = test_endpoint("GET", "/api/system/processes",
                                       expected_keys=["processes", "count"])
    print_test("System Processes (/api/system/processes)", success, msg)
    passed += success
    failed += not success

    # Test 4: System Ports
    success, msg, data = test_endpoint("GET", "/api/system/ports",
                                       expected_keys=["ports", "count"])
    print_test("System Ports (/api/system/ports)", success, msg)
    passed += success
    failed += not success

    # Group 2: Knowledge Base Endpoints
    print(f"{Colors.BLUE}=== KNOWLEDGE BASE ENDPOINTS ==={Colors.END}")
    print()

    # Test 5: KB Recent (FIXED)
    success, msg, data = test_endpoint("GET", "/api/knowledge/recent",
                                       expected_keys=["files", "count"],
                                       params={"limit": 5})
    print_test("KB Recent Files (/api/knowledge/recent?limit=5)", success, msg, data if success else None)
    passed += success
    failed += not success

    # Test 6: KB Stats
    success, msg, data = test_endpoint("GET", "/api/knowledge/stats",
                                       expected_keys=["total_files", "kb_status"])
    print_test("KB Stats (/api/knowledge/stats)", success, msg)
    passed += success
    failed += not success

    # Test 7: KB Files
    success, msg, data = test_endpoint("GET", "/api/knowledge/files",
                                       expected_keys=["files", "meta"])
    print_test("KB Files (/api/knowledge/files)", success, msg)
    passed += success
    failed += not success

    # Group 3: Service Endpoints
    print(f"{Colors.BLUE}=== SERVICE MANAGEMENT ENDPOINTS ==={Colors.END}")
    print()

    # Test 8: List Services
    success, msg, data = test_endpoint("GET", "/api/services",
                                       expected_keys=["services"])
    print_test("List Services (/api/services)", success, msg)
    passed += success
    failed += not success

    # Test 9: Service Status (comfyui as example)
    success, msg, data = test_endpoint("GET", "/api/services/comfyui/status",
                                       expected_keys=["name", "status"])
    print_test("Service Status (/api/services/comfyui/status)", success, msg)
    passed += success
    failed += not success

    # Test 10: Service Logs
    success, msg, data = test_endpoint("GET", "/api/services/comfyui/logs",
                                       expected_keys=["success"],
                                       params={"lines": 50})
    print_test("Service Logs (/api/services/comfyui/logs?lines=50)", success, msg)
    passed += success
    failed += not success

    # NOTE: Not testing start/stop/restart to avoid disrupting services
    print(f"{Colors.YELLOW}[INFO]{Colors.END} Skipping service start/stop/restart tests (would disrupt running services)")
    print()

    # Group 4: Health Endpoints
    print(f"{Colors.BLUE}=== HEALTH & STATUS ENDPOINTS ==={Colors.END}")
    print()

    # Test 11: Basic Health
    success, msg, data = test_endpoint("GET", "/health",
                                       expected_keys=["status"])
    print_test("Basic Health (/health)", success, msg)
    passed += success
    failed += not success

    # Test 12: Root Endpoint
    success, msg, data = test_endpoint("GET", "/",
                                       expected_keys=["name", "version", "status"])
    print_test("Root Endpoint (/)", success, msg)
    passed += success
    failed += not success

    # Group 5: WebSocket Info
    print(f"{Colors.BLUE}=== WEBSOCKET ENDPOINTS ==={Colors.END}")
    print()
    print(f"{Colors.YELLOW}[INFO]{Colors.END} WebSocket endpoints require manual testing:")
    print(f"  • Public (no auth): ws://127.0.0.1:54112/ws")
    print(f"  • Public metrics: ws://127.0.0.1:54112/api/system/metrics")
    print(f"  • Authenticated: ws://127.0.0.1:54112/api/system/ws?token=<JWT>")
    print()

    # Summary
    print("=" * 80)
    print(f"{Colors.BLUE}TEST SUMMARY{Colors.END}")
    print("=" * 80)
    print(f"{Colors.GREEN}Passed:{Colors.END} {passed}")
    print(f"{Colors.RED}Failed:{Colors.END} {failed}")
    print(f"Total: {passed + failed}")
    print()

    if failed == 0:
        print(f"{Colors.GREEN}[OK] All tests passed!{Colors.END}")
        print(f"{Colors.GREEN}Backend is ready for frontend integration.{Colors.END}")
    else:
        print(f"{Colors.RED}[ERROR] Some tests failed.{Colors.END}")
        print(f"{Colors.YELLOW}Possible causes:{Colors.END}")
        print(f"  1. Backend server not running on port 54112")
        print(f"  2. Old version of backend running (needs restart)")
        print(f"  3. Database not initialized")
        print(f"  4. Missing dependencies")
        print()
        print(f"{Colors.YELLOW}Solution:{Colors.END}")
        print(f"  Run: python restart_backend_clean.py")

    print()
    print("=" * 80)

if __name__ == "__main__":
    main()
