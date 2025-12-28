"""
Test script for Agents API endpoints
Run this to verify all endpoints are working correctly
"""

import requests
import json
from typing import Dict, Any

API_BASE = "http://127.0.0.1:54112"

def test_endpoint(name: str, url: str, params: Dict = None) -> bool:
    """Test a single API endpoint"""
    try:
        print(f"\nTesting: {name}")
        print(f"URL: {url}")
        if params:
            print(f"Params: {params}")

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        print(f"Status: {response.status_code} OK")
        print(f"Response keys: {list(data.keys()) if isinstance(data, dict) else 'Array'}")

        if isinstance(data, dict):
            if 'agents' in data:
                print(f"Agents count: {len(data['agents'])}")
            if 'total' in data:
                print(f"Total: {data['total']}")

        return True
    except requests.exceptions.RequestException as e:
        print(f"FAILED: {str(e)}")
        return False
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return False


def main():
    print("=" * 60)
    print("AGENTS API INTEGRATION TEST")
    print("=" * 60)

    tests = []

    # Test 1: List all agents
    tests.append(test_endpoint(
        "List All Agents",
        f"{API_BASE}/api/agents"
    ))

    # Test 2: Get agent stats
    tests.append(test_endpoint(
        "Get Agent Stats",
        f"{API_BASE}/api/agents/stats"
    ))

    # Test 3: Filter by level - L1
    tests.append(test_endpoint(
        "Filter Agents - L1 Only",
        f"{API_BASE}/api/agents",
        {"level": "l1"}
    ))

    # Test 4: Filter by level - L2
    tests.append(test_endpoint(
        "Filter Agents - L2 Only",
        f"{API_BASE}/api/agents",
        {"level": "l2"}
    ))

    # Test 5: Filter by level - L3
    tests.append(test_endpoint(
        "Filter Agents - L3 Only",
        f"{API_BASE}/api/agents",
        {"level": "l3"}
    ))

    # Test 6: Search agents
    tests.append(test_endpoint(
        "Search Agents - 'art'",
        f"{API_BASE}/api/agents",
        {"search": "art"}
    ))

    # Test 7: Get specific agent details (try first L1 agent)
    tests.append(test_endpoint(
        "Get Agent Details - L1 Agent",
        f"{API_BASE}/api/agents/01_art_director"
    ))

    # Test 8: Get agent knowledge files
    tests.append(test_endpoint(
        "Get Agent Knowledge Files",
        f"{API_BASE}/api/agents/01_art_director/knowledge"
    ))

    # Test 9: Get agent hierarchy
    tests.append(test_endpoint(
        "Get Agent Hierarchy",
        f"{API_BASE}/api/agents/01_art_director/hierarchy"
    ))

    # Test 10: Pagination
    tests.append(test_endpoint(
        "Pagination - Limit 10, Offset 0",
        f"{API_BASE}/api/agents",
        {"limit": 10, "offset": 0}
    ))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    passed = sum(tests)
    total = len(tests)
    print(f"Passed: {passed}/{total}")
    print(f"Failed: {total - passed}/{total}")

    if passed == total:
        print("\nAll tests passed!")
        return 0
    else:
        print("\nSome tests failed. Please check the output above.")
        return 1


if __name__ == "__main__":
    exit(main())
