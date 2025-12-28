"""
Test script for Control Center Backend
Tests all API endpoints to ensure they're working correctly
"""
import asyncio
import httpx
from datetime import datetime


BASE_URL = "http://127.0.0.1:8080"


async def test_endpoint(client: httpx.AsyncClient, method: str, endpoint: str, description: str):
    """Test a single endpoint."""
    try:
        if method.upper() == "GET":
            response = await client.get(f"{BASE_URL}{endpoint}")
        elif method.upper() == "POST":
            response = await client.post(f"{BASE_URL}{endpoint}")

        status = "PASS" if response.status_code < 400 else "FAIL"
        print(f"[{status}] {method} {endpoint} - {description}")
        print(f"      Status: {response.status_code}")

        if response.status_code < 400:
            try:
                data = response.json()
                if isinstance(data, dict):
                    # Print some key fields
                    for key in list(data.keys())[:3]:
                        print(f"      {key}: {str(data[key])[:60]}")
            except:
                pass

        print()
        return response.status_code < 400

    except Exception as e:
        print(f"[ERROR] {method} {endpoint} - {description}")
        print(f"        {str(e)}")
        print()
        return False


async def run_tests():
    """Run all API tests."""
    print("=" * 70)
    print("Control Center Backend API Test Suite")
    print("=" * 70)
    print(f"Testing server at: {BASE_URL}")
    print(f"Test started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print()

    async with httpx.AsyncClient(timeout=30.0) as client:
        passed = 0
        failed = 0

        # Basic endpoints
        print("BASIC ENDPOINTS")
        print("-" * 70)
        if await test_endpoint(client, "GET", "/", "Root endpoint"):
            passed += 1
        else:
            failed += 1

        if await test_endpoint(client, "GET", "/health", "Health check"):
            passed += 1
        else:
            failed += 1

        # System endpoints
        print("\nSYSTEM MONITORING ENDPOINTS")
        print("-" * 70)
        if await test_endpoint(client, "GET", "/api/system/stats", "System statistics"):
            passed += 1
        else:
            failed += 1

        if await test_endpoint(client, "GET", "/api/system/processes", "Process list"):
            passed += 1
        else:
            failed += 1

        if await test_endpoint(client, "GET", "/api/system/ports", "Port scan"):
            passed += 1
        else:
            failed += 1

        # Service endpoints
        print("\nSERVICE CONTROL ENDPOINTS")
        print("-" * 70)
        if await test_endpoint(client, "GET", "/api/services", "List services"):
            passed += 1
        else:
            failed += 1

        if await test_endpoint(client, "GET", "/api/services/comfyui/status", "ComfyUI status"):
            passed += 1
        else:
            failed += 1

        if await test_endpoint(client, "GET", "/api/services/comfyui/logs?lines=10", "ComfyUI logs"):
            passed += 1
        else:
            failed += 1

        # Knowledge base endpoints
        print("\nKNOWLEDGE BASE ENDPOINTS")
        print("-" * 70)
        if await test_endpoint(client, "GET", "/api/knowledge/stats", "KB statistics"):
            passed += 1
        else:
            failed += 1

        if await test_endpoint(client, "GET", "/api/knowledge/files?limit=5", "KB files list"):
            passed += 1
        else:
            failed += 1

        if await test_endpoint(client, "GET", "/api/knowledge/creators", "Creators list"):
            passed += 1
        else:
            failed += 1

        if await test_endpoint(client, "GET", "/api/knowledge/jobs", "Scan jobs"):
            passed += 1
        else:
            failed += 1

        # Summary
        print("\n" + "=" * 70)
        print("TEST SUMMARY")
        print("=" * 70)
        print(f"Total Tests: {passed + failed}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")

        if failed == 0:
            print("\nResult: ALL TESTS PASSED")
        else:
            print(f"\nResult: {failed} TEST(S) FAILED")

        print("=" * 70)

        return failed == 0


async def main():
    """Main test runner."""
    try:
        success = await run_tests()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\nFATAL ERROR: {str(e)}")
        exit(1)


if __name__ == "__main__":
    asyncio.run(main())
