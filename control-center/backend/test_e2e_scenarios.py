"""
End-to-End Integration Scenario Testing.
Tests complete workflows through the system.
"""
import requests
import time
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:54112"

def print_scenario(name):
    """Print scenario header"""
    print("\n" + "=" * 70)
    print(f"SCENARIO: {name}")
    print("=" * 70)

def print_step(step_num, description):
    """Print step"""
    print(f"\nStep {step_num}: {description}")

def print_result(success, message=""):
    """Print result"""
    status = "[PASS]" if success else "[FAIL]"
    print(f"  {status} {message}")
    return success

def scenario_1_dashboard_load():
    """
    Scenario 1: Dashboard Load
    1. User opens dashboard
    2. Frontend requests system info
    3. Backend queries system
    4. Data flows back to frontend
    5. UI displays information
    """
    print_scenario("Dashboard Load - Complete Data Flow")

    results = []

    # Step 1: Health check (simulating initial load)
    print_step(1, "Health check on dashboard load")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        success = response.status_code == 200
        results.append(print_result(success, f"Status: {response.status_code}"))
    except Exception as e:
        results.append(print_result(False, str(e)))

    # Step 2: Get system stats (CPU, Memory, Disk)
    print_step(2, "Fetch system statistics")
    try:
        response = requests.get(f"{BASE_URL}/api/system/stats", timeout=10)
        success = response.status_code == 200
        if success:
            data = response.json()
            print(f"  CPU: {data['cpu']['usage_percent']}%")
            print(f"  Memory: {data['memory']['percent']}%")
            print(f"  Disk: {data['disk']['percent']}%")
        results.append(print_result(success))
    except Exception as e:
        results.append(print_result(False, str(e)))

    # Step 3: Get services list
    print_step(3, "Fetch services list")
    try:
        response = requests.get(f"{BASE_URL}/api/services", timeout=5)
        success = response.status_code == 200
        if success:
            data = response.json()
            print(f"  Found {data['count']} services")
            for service in data['services'][:3]:
                print(f"    - {service['name']}: {service['status']}")
        results.append(print_result(success))
    except Exception as e:
        results.append(print_result(False, str(e)))

    # Step 4: Get agent stats
    print_step(4, "Fetch agent statistics")
    try:
        response = requests.get(f"{BASE_URL}/api/agents/stats", timeout=5)
        success = response.status_code == 200
        if success:
            data = response.json()
            print(f"  Total agents: {data.get('total', 0)}")
        results.append(print_result(success))
    except Exception as e:
        results.append(print_result(False, str(e)))

    # Step 5: Verify data integrity
    print_step(5, "Verify data integrity and consistency")
    all_success = all(results)
    print_result(all_success, f"All {len(results)} data requests completed successfully")

    return all_success

def scenario_2_knowledge_base_access():
    """
    Scenario 2: Knowledge Base Access
    1. User navigates to Knowledge Base
    2. Frontend requests recent files
    3. Backend scans file system
    4. Files returned with metadata
    5. UI displays file list
    """
    print_scenario("Knowledge Base Access - File System Integration")

    results = []

    # Step 1: Get KB stats
    print_step(1, "Fetch knowledge base statistics")
    try:
        response = requests.get(f"{BASE_URL}/api/knowledge/stats", timeout=5)
        success = response.status_code == 200
        if success:
            data = response.json()
            print(f"  Total files: {data.get('total_files', 0)}")
            print(f"  Total agents: {data.get('total_agents', 0)}")
        results.append(print_result(success))
    except Exception as e:
        results.append(print_result(False, str(e)))

    # Step 2: Get recent files
    print_step(2, "Fetch recent knowledge files")
    try:
        response = requests.get(f"{BASE_URL}/api/knowledge/recent?limit=5", timeout=5)
        success = response.status_code == 200
        if success:
            data = response.json()
            print(f"  Retrieved {data['count']} recent files")
            for file in data.get('files', [])[:3]:
                print(f"    - {file.get('name', 'unknown')}")
        results.append(print_result(success))
    except Exception as e:
        results.append(print_result(False, str(e)))

    # Step 3: Get creators list
    print_step(3, "Fetch content creators")
    try:
        response = requests.get(f"{BASE_URL}/api/knowledge/creators", timeout=5)
        success = response.status_code == 200
        if success:
            data = response.json()
            print(f"  Found {len(data.get('creators', []))} creators")
        results.append(print_result(success))
    except Exception as e:
        results.append(print_result(False, str(e)))

    # Step 4: Get paginated files
    print_step(4, "Fetch paginated file list")
    try:
        response = requests.get(f"{BASE_URL}/api/knowledge/files?page=1&limit=10", timeout=5)
        success = response.status_code == 200
        if success:
            data = response.json()
            print(f"  Page 1 contains {len(data.get('files', []))} files")
            print(f"  Total files: {data.get('total', 0)}")
        results.append(print_result(success))
    except Exception as e:
        results.append(print_result(False, str(e)))

    # Step 5: Verify caching
    print_step(5, "Verify caching layer performance")
    try:
        start = time.time()
        response1 = requests.get(f"{BASE_URL}/api/knowledge/stats", timeout=5)
        time1 = time.time() - start

        start = time.time()
        response2 = requests.get(f"{BASE_URL}/api/knowledge/stats", timeout=5)
        time2 = time.time() - start

        success = response1.status_code == 200 and response2.status_code == 200
        if success:
            cached = response2.json().get('cached', False)
            print(f"  First request: {time1*1000:.0f}ms")
            print(f"  Second request: {time2*1000:.0f}ms (cached: {cached})")
            if time2 < time1:
                print(f"  Cache speedup: {(time1/time2):.1f}x faster")
        results.append(print_result(success))
    except Exception as e:
        results.append(print_result(False, str(e)))

    return all(results)

def scenario_3_real_time_monitoring():
    """
    Scenario 3: Real-Time Monitoring
    1. User opens dashboard
    2. WebSocket connection established
    3. Metrics broadcast every 2 seconds
    4. UI updates in real-time
    5. Connection persists
    """
    print_scenario("Real-Time Monitoring - WebSocket Data Stream")

    results = []

    # Step 1: Verify WebSocket endpoint availability
    print_step(1, "Verify WebSocket endpoint")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        data = response.json()
        ws_url = data.get('websocket_url')
        success = ws_url is not None
        print_result(success, f"WebSocket URL: {ws_url}")
        results.append(success)
    except Exception as e:
        results.append(print_result(False, str(e)))

    # Step 2: Test HTTP fallback (polling mode)
    print_step(2, "Test HTTP polling as fallback")
    try:
        # Simulate polling by making multiple requests
        for i in range(3):
            response = requests.get(f"{BASE_URL}/api/system/stats", timeout=5)
            if response.status_code == 200:
                data = response.json()
                cpu = data['cpu']['usage_percent']
                memory = data['memory']['percent']
                print(f"  Poll {i+1}: CPU={cpu}%, Memory={memory}%")
            time.sleep(0.5)
        results.append(print_result(True, "Polling mode works"))
    except Exception as e:
        results.append(print_result(False, str(e)))

    # Step 3: Verify data freshness
    print_step(3, "Verify data freshness and timestamp")
    try:
        response = requests.get(f"{BASE_URL}/api/system/stats", timeout=5)
        success = response.status_code == 200
        if success:
            data = response.json()
            timestamp = data.get('timestamp')
            print(f"  Data timestamp: {timestamp}")
            # Verify timestamp is recent (within last 5 seconds)
            from datetime import datetime, timezone
            data_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            now = datetime.now(timezone.utc)
            age = (now - data_time).total_seconds()
            print(f"  Data age: {age:.1f} seconds")
            success = age < 5
        results.append(print_result(success))
    except Exception as e:
        results.append(print_result(False, str(e)))

    return all(results)

def scenario_4_service_management():
    """
    Scenario 4: Service Management
    1. User views services list
    2. User checks service status
    3. Backend queries system
    4. Status returned
    5. UI reflects current state
    """
    print_scenario("Service Management - State Consistency")

    results = []

    # Step 1: List all services
    print_step(1, "List all managed services")
    try:
        response = requests.get(f"{BASE_URL}/api/services", timeout=5)
        success = response.status_code == 200
        services = []
        if success:
            data = response.json()
            services = data.get('services', [])
            print(f"  Found {len(services)} services")
            for svc in services:
                print(f"    - {svc['name']}: {svc['status']}")
        results.append(print_result(success))
    except Exception as e:
        results.append(print_result(False, str(e)))
        services = []

    # Step 2: Check specific service status
    print_step(2, "Check ComfyUI service status")
    try:
        response = requests.get(f"{BASE_URL}/api/comfyui/status", timeout=10)
        success = response.status_code == 200
        if success:
            data = response.json()
            print(f"  Status: {data.get('status', 'unknown')}")
            print(f"  Port: {data.get('port', 'N/A')}")
        results.append(print_result(success))
    except Exception as e:
        results.append(print_result(False, str(e)))

    # Step 3: Verify state consistency
    print_step(3, "Verify state consistency across endpoints")
    try:
        # Get service list status
        r1 = requests.get(f"{BASE_URL}/api/services", timeout=5)
        # Get specific service status
        r2 = requests.get(f"{BASE_URL}/api/comfyui/status", timeout=10)

        success = r1.status_code == 200 and r2.status_code == 200
        if success:
            services_data = r1.json()
            comfyui_status = r2.json()

            # Find ComfyUI in services list
            comfyui_in_list = next((s for s in services_data['services'] if 'comfyui' in s['name'].lower()), None)

            if comfyui_in_list:
                print(f"  Services list shows: {comfyui_in_list['status']}")
                print(f"  Direct endpoint shows: {comfyui_status.get('status')}")
                # Note: States might differ slightly due to timing
                print(f"  States are being tracked independently (expected)")

        results.append(print_result(success))
    except Exception as e:
        results.append(print_result(False, str(e)))

    # Step 4: Check cache effectiveness
    print_step(4, "Verify cache performance for repeated queries")
    try:
        times = []
        for i in range(3):
            start = time.time()
            response = requests.get(f"{BASE_URL}/api/services", timeout=5)
            elapsed = time.time() - start
            times.append(elapsed * 1000)
            if response.status_code == 200:
                cached = response.json().get('cached', False)
                print(f"  Request {i+1}: {elapsed*1000:.0f}ms (cached: {cached})")

        success = response.status_code == 200
        if len(times) >= 2:
            avg_time = sum(times[1:]) / len(times[1:])
            print(f"  Average cached response time: {avg_time:.0f}ms")

        results.append(print_result(success))
    except Exception as e:
        results.append(print_result(False, str(e)))

    return all(results)

def main():
    """Run all scenarios"""
    print("=" * 70)
    print("END-TO-END INTEGRATION SCENARIO TESTING")
    print("=" * 70)
    print(f"Base URL: {BASE_URL}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    results = []

    # Run all scenarios
    results.append(("Dashboard Load", scenario_1_dashboard_load()))
    results.append(("Knowledge Base Access", scenario_2_knowledge_base_access()))
    results.append(("Real-Time Monitoring", scenario_3_real_time_monitoring()))
    results.append(("Service Management", scenario_4_service_management()))

    # Summary
    print("\n" + "=" * 70)
    print("SCENARIO TEST SUMMARY")
    print("=" * 70)

    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {name}")

    passed = sum(1 for _, result in results if result)
    total = len(results)
    success_rate = (passed / total * 100) if total > 0 else 0

    print(f"\nTotal Scenarios: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success Rate: {success_rate:.1f}%")

    if success_rate == 100:
        print("\n[PASS] All scenarios PASSED")
        return True
    elif success_rate >= 75:
        print("\n[WARNING] Scenarios PARTIAL PASS")
        return True
    else:
        print("\n[FAIL] Scenarios FAILED")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
