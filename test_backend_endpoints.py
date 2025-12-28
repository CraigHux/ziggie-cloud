"""Test all backend endpoints for Control Center."""
import requests
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:54112"

# Test results storage
results = {
    "timestamp": datetime.now().isoformat(),
    "endpoints_tested": 0,
    "endpoints_passed": 0,
    "endpoints_failed": 0,
    "details": []
}


def test_endpoint(method, endpoint, expected_status=200, description=""):
    """Test a single endpoint."""
    global results

    url = f"{BASE_URL}{endpoint}"

    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, timeout=10)
        else:
            raise ValueError(f"Unsupported method: {method}")

        results["endpoints_tested"] += 1

        # Check status code
        status_ok = response.status_code == expected_status

        # Try to parse JSON
        try:
            data = response.json()
            json_ok = True
        except:
            data = None
            json_ok = False

        # Overall pass/fail
        passed = status_ok and json_ok

        if passed:
            results["endpoints_passed"] += 1
            status = "PASS"
        else:
            results["endpoints_failed"] += 1
            status = "FAIL"

        result_entry = {
            "endpoint": endpoint,
            "method": method,
            "description": description,
            "status": status,
            "status_code": response.status_code,
            "expected_status": expected_status,
            "has_json": json_ok,
            "response_preview": str(data)[:200] if data else None
        }

        results["details"].append(result_entry)

        print(f"{status} | {method:4} {endpoint:40} | {response.status_code} | {description}")

        return response, data

    except Exception as e:
        results["endpoints_tested"] += 1
        results["endpoints_failed"] += 1

        result_entry = {
            "endpoint": endpoint,
            "method": method,
            "description": description,
            "status": "ERROR",
            "error": str(e)
        }

        results["details"].append(result_entry)

        print(f"ERROR | {method:4} {endpoint:40} | {str(e)[:50]}")

        return None, None


print("=" * 100)
print("CONTROL CENTER BACKEND API ENDPOINT TESTS")
print("=" * 100)
print()

# Test root endpoint
print("--- ROOT ENDPOINTS ---")
test_endpoint("GET", "/", description="Root endpoint")
test_endpoint("GET", "/health", description="Basic health check")
print()

# Test System API
print("--- SYSTEM API ---")
test_endpoint("GET", "/api/system/stats", description="System stats (CPU, RAM, Disk)")
test_endpoint("GET", "/api/system/processes", description="Running processes")
test_endpoint("GET", "/api/system/ports", description="Open ports")
print()

# Test Agents API
print("--- AGENTS API ---")
test_endpoint("GET", "/api/agents", description="List all agents")
test_endpoint("GET", "/api/agents/stats", description="Agent statistics")
test_endpoint("GET", "/api/agents?level=L1", description="Filter agents by level L1")
test_endpoint("GET", "/api/agents?level=L2", description="Filter agents by level L2")
test_endpoint("GET", "/api/agents?level=L3", description="Filter agents by level L3")
print()

# Test Services API
print("--- SERVICES API ---")
test_endpoint("GET", "/api/services", description="List all services")
print()

# Test Knowledge Base API
print("--- KNOWLEDGE BASE API ---")
test_endpoint("GET", "/api/knowledge/stats", description="Knowledge base statistics")
test_endpoint("GET", "/api/knowledge/files", description="Knowledge base files")
print()

# Test Health API
print("--- HEALTH API ---")
test_endpoint("GET", "/api/health/full", description="Full health check")
print()

# Summary
print()
print("=" * 100)
print("SUMMARY")
print("=" * 100)
print(f"Total Endpoints Tested: {results['endpoints_tested']}")
print(f"Passed: {results['endpoints_passed']}")
print(f"Failed: {results['endpoints_failed']}")
print(f"Success Rate: {(results['endpoints_passed'] / results['endpoints_tested'] * 100):.1f}%")
print()

# Save results to JSON
with open("C:/Ziggie/backend_test_results.json", "w") as f:
    json.dump(results, f, indent=2)

print("Full results saved to: C:/Ziggie/backend_test_results.json")
print()

# Show failed endpoints
if results["endpoints_failed"] > 0:
    print("FAILED ENDPOINTS:")
    for detail in results["details"]:
        if detail["status"] in ["FAIL", "ERROR"]:
            print(f"  - {detail['method']} {detail['endpoint']}")
            if "error" in detail:
                print(f"    Error: {detail['error']}")
            elif detail.get("status_code"):
                print(f"    Status: {detail['status_code']} (expected {detail.get('expected_status', 200)})")
    print()
