"""Test individual endpoints that are timing out."""
import requests
import json

BASE_URL = "http://127.0.0.1:54112"

# Test system stats (working)
print("Testing /api/system/stats...")
try:
    response = requests.get(f"{BASE_URL}/api/system/stats", timeout=15)
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"CPU Usage: {data['cpu']['usage_percent']}%")
    print(f"Memory Usage: {data['memory']['percent']}%")
    print(f"Disk Usage: {data['disk']['percent']}%")
    print()
except Exception as e:
    print(f"Error: {e}")
    print()

# Test processes (timing out)
print("Testing /api/system/processes...")
try:
    response = requests.get(f"{BASE_URL}/api/system/processes", timeout=30)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Process count: {data.get('count', 0)}")
        print(f"First 3 processes: {json.dumps(data.get('processes', [])[:3], indent=2)}")
    else:
        print(f"Response: {response.text[:500]}")
    print()
except Exception as e:
    print(f"Error: {e}")
    print()

# Test ports (timing out)
print("Testing /api/system/ports...")
try:
    response = requests.get(f"{BASE_URL}/api/system/ports", timeout=30)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Port count: {data.get('count', 0)}")
        print(f"Ports: {json.dumps(data.get('ports', [])[:5], indent=2)}")
    else:
        print(f"Response: {response.text[:500]}")
    print()
except Exception as e:
    print(f"Error: {e}")
    print()
