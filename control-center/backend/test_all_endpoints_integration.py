"""
Comprehensive endpoint integration testing.
Tests all API endpoints for correct data flow and integration.
"""
import requests
import json
import time
from datetime import datetime

BASE_URL = "http://127.0.0.1:54112"

class Colors:
    """Terminal colors for Windows"""
    PASS = ""
    FAIL = ""
    INFO = ""
    RESET = ""

def test_endpoint(name, method, url, expected_status=200, data=None, headers=None):
    """Test a single endpoint"""
    full_url = f"{BASE_URL}{url}"
    print(f"\nTesting: {name}")
    print(f"  URL: {method} {url}")

    start_time = time.time()

    try:
        if method == "GET":
            response = requests.get(full_url, headers=headers, timeout=10)
        elif method == "POST":
            response = requests.post(full_url, json=data, headers=headers, timeout=10)
        else:
            print(f"  [SKIP] Unsupported method: {method}")
            return False

        elapsed = (time.time() - start_time) * 1000

        if response.status_code == expected_status:
            print(f"  [PASS] Status: {response.status_code}, Time: {elapsed:.0f}ms")

            # Try to parse JSON response
            try:
                json_data = response.json()
                if isinstance(json_data, dict):
                    if 'success' in json_data:
                        print(f"  Response: success={json_data['success']}")
                    if 'count' in json_data:
                        print(f"  Response: count={json_data['count']}")
                    if 'cached' in json_data:
                        print(f"  Response: cached={json_data['cached']}")
            except:
                pass

            return True
        else:
            print(f"  [FAIL] Expected {expected_status}, got {response.status_code}")
            print(f"  Response: {response.text[:200]}")
            return False

    except requests.exceptions.Timeout:
        print(f"  [FAIL] Request timeout")
        return False
    except Exception as e:
        print(f"  [FAIL] Error: {e}")
        return False

def main():
    """Run all endpoint tests"""
    print("=" * 70)
    print("ENDPOINT INTEGRATION TESTING")
    print("=" * 70)
    print(f"Base URL: {BASE_URL}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    results = []

    # Core endpoints
    print("\n" + "=" * 70)
    print("CORE ENDPOINTS")
    print("=" * 70)

    results.append(test_endpoint("Root", "GET", "/"))
    results.append(test_endpoint("Health (basic)", "GET", "/health"))
    results.append(test_endpoint("Health (detailed)", "GET", "/api/health"))
    results.append(test_endpoint("Health with details", "GET", "/api/health/details"))

    # System endpoints
    print("\n" + "=" * 70)
    print("SYSTEM ENDPOINTS")
    print("=" * 70)

    results.append(test_endpoint("System Stats", "GET", "/api/system/stats"))
    results.append(test_endpoint("System Processes", "GET", "/api/system/processes"))
    results.append(test_endpoint("System Ports", "GET", "/api/system/ports"))

    # Services endpoints
    print("\n" + "=" * 70)
    print("SERVICES ENDPOINTS")
    print("=" * 70)

    results.append(test_endpoint("List Services", "GET", "/api/services"))
    results.append(test_endpoint("Services (page 1)", "GET", "/api/services?page=1&page_size=10"))

    # Knowledge base endpoints
    print("\n" + "=" * 70)
    print("KNOWLEDGE BASE ENDPOINTS")
    print("=" * 70)

    results.append(test_endpoint("KB Recent Files", "GET", "/api/knowledge/recent?limit=5"))
    results.append(test_endpoint("KB Stats", "GET", "/api/knowledge/stats"))
    results.append(test_endpoint("KB Creators", "GET", "/api/knowledge/creators"))
    results.append(test_endpoint("KB Files", "GET", "/api/knowledge/files?page=1&limit=10"))

    # Agents endpoints
    print("\n" + "=" * 70)
    print("AGENTS ENDPOINTS")
    print("=" * 70)

    results.append(test_endpoint("Agent Stats", "GET", "/api/agents/stats"))
    results.append(test_endpoint("List Agents", "GET", "/api/agents"))
    results.append(test_endpoint("Cache Stats (Agents)", "GET", "/api/agents/cache/stats"))

    # Cache endpoints
    print("\n" + "=" * 70)
    print("CACHE ENDPOINTS")
    print("=" * 70)

    results.append(test_endpoint("Cache Stats", "GET", "/api/cache/stats"))
    results.append(test_endpoint("Cache Health", "GET", "/api/cache/health"))

    # Docker endpoints
    print("\n" + "=" * 70)
    print("DOCKER ENDPOINTS")
    print("=" * 70)

    results.append(test_endpoint("Docker Projects", "GET", "/api/docker/compose/projects"))

    # ComfyUI endpoints
    print("\n" + "=" * 70)
    print("COMFYUI ENDPOINTS")
    print("=" * 70)

    results.append(test_endpoint("ComfyUI Health", "GET", "/api/comfyui/health"))
    results.append(test_endpoint("ComfyUI Status", "GET", "/api/comfyui/status"))

    # Authentication endpoints (public)
    print("\n" + "=" * 70)
    print("AUTH ENDPOINTS (Public)")
    print("=" * 70)

    results.append(test_endpoint("Auth Stats", "GET", "/api/auth/stats"))

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    passed = sum(results)
    failed = len(results) - passed
    success_rate = (passed / len(results) * 100) if results else 0

    print(f"\nTotal Tests: {len(results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success Rate: {success_rate:.1f}%")

    if success_rate >= 90:
        print("\n[PASS] Integration test suite PASSED")
        return True
    elif success_rate >= 70:
        print("\n[WARNING] Integration test suite PARTIAL PASS")
        return True
    else:
        print("\n[FAIL] Integration test suite FAILED")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
