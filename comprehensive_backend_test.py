"""Comprehensive backend test with all required endpoints."""
import requests
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:54112"

def test_endpoint(name, endpoint, timeout=30):
    """Test an endpoint and return results."""
    try:
        response = requests.get(f"{BASE_URL}{endpoint}", timeout=timeout)
        data = response.json()
        return {
            "name": name,
            "endpoint": endpoint,
            "status": "PASS" if response.status_code == 200 else "FAIL",
            "status_code": response.status_code,
            "response": data
        }
    except Exception as e:
        return {
            "name": name,
            "endpoint": endpoint,
            "status": "ERROR",
            "error": str(e)
        }

print("=" * 100)
print("COMPREHENSIVE BACKEND API TEST")
print("=" * 100)
print()

results = []

# System API Tests
print("TESTING SYSTEM API...")
results.append(test_endpoint("System Stats", "/api/system/stats"))
results.append(test_endpoint("System Processes", "/api/system/processes"))
results.append(test_endpoint("System Ports", "/api/system/ports"))
print()

# Agents API Tests
print("TESTING AGENTS API...")
results.append(test_endpoint("List All Agents", "/api/agents"))
results.append(test_endpoint("Agent Stats", "/api/agents/stats"))
results.append(test_endpoint("L1 Agents", "/api/agents?level=L1"))
results.append(test_endpoint("L2 Agents", "/api/agents?level=L2"))
results.append(test_endpoint("L3 Agents", "/api/agents?level=L3"))
print()

# Services API Tests
print("TESTING SERVICES API...")
results.append(test_endpoint("List Services", "/api/services"))
print()

# Knowledge Base API Tests
print("TESTING KNOWLEDGE BASE API...")
results.append(test_endpoint("KB Stats", "/api/knowledge/stats"))
results.append(test_endpoint("KB Files", "/api/knowledge/files"))
print()

# Health API Tests
print("TESTING HEALTH API...")
results.append(test_endpoint("Basic Health", "/health"))
results.append(test_endpoint("Detailed Health", "/health/detailed"))
results.append(test_endpoint("Readiness Check", "/health/ready"))
results.append(test_endpoint("Liveness Check", "/health/live"))
results.append(test_endpoint("Startup Check", "/health/startup"))
print()

# Print summary
passed = sum(1 for r in results if r["status"] == "PASS")
failed = sum(1 for r in results if r["status"] in ["FAIL", "ERROR"])

print("=" * 100)
print("SUMMARY")
print("=" * 100)
for result in results:
    status_symbol = "[PASS]" if result["status"] == "PASS" else "[FAIL]"
    print(f"{status_symbol} {result['name']:30} - {result['endpoint']:40} - {result.get('status_code', 'N/A')}")

print()
print(f"Total: {len(results)} | Passed: {passed} | Failed: {failed}")
print(f"Success Rate: {(passed/len(results)*100):.1f}%")
print()

# Sample data from key endpoints
print("=" * 100)
print("SAMPLE DATA")
print("=" * 100)

for result in results:
    if result["status"] == "PASS" and "response" in result:
        print(f"\n{result['name']}:")
        data = result["response"]

        if result["name"] == "System Stats":
            print(f"  CPU: {data['cpu']['usage_percent']}%")
            print(f"  Memory: {data['memory']['percent']}%")
            print(f"  Disk: {data['disk']['percent']}%")

        elif result["name"] == "Agent Stats":
            print(f"  Total Agents: {data['total']}")
            print(f"  L1: {data['by_level']['L1']}")
            print(f"  L2: {data['by_level']['L2']}")
            print(f"  L3: {data['by_level']['L3']}")

        elif result["name"] == "System Processes":
            print(f"  Total Processes: {data['count']}")
            print(f"  Top Process: {data['processes'][0]['name']} ({data['processes'][0]['cpu_percent']}% CPU)")

        elif result["name"] == "System Ports":
            print(f"  Open Ports: {data['count']}")
            if data['ports']:
                print(f"  First Port: {data['ports'][0]['port']} ({data['ports'][0].get('process_name', 'Unknown')})")

        elif result["name"] == "List Services":
            print(f"  Services: {data['meta']['total']}")
            for svc in data['services']:
                print(f"    - {svc['name']}: {svc['status']}")

        elif result["name"] == "KB Stats":
            print(f"  Total Files: {data['total_files']}")
            print(f"  Total Size: {data['total_size_mb']} MB")
            print(f"  Creators: {data['total_creators']}")

print()

# Save full results
with open("C:/Ziggie/comprehensive_test_results.json", "w") as f:
    json.dump({
        "timestamp": datetime.now().isoformat(),
        "total": len(results),
        "passed": passed,
        "failed": failed,
        "success_rate": f"{(passed/len(results)*100):.1f}%",
        "results": results
    }, f, indent=2)

print("Full results saved to: C:/Ziggie/comprehensive_test_results.json")
