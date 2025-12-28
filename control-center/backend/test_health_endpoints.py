"""Test health check endpoints."""
import asyncio
import sys
sys.path.insert(0, '.')

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_endpoints():
    """Test all health check endpoints."""
    print("\n" + "="*60)
    print("TESTING HEALTH CHECK ENDPOINTS")
    print("="*60)
    
    endpoints = [
        ("/health", "Basic Health Check"),
        ("/health/detailed", "Detailed Health Check"),
        ("/health/ready", "Readiness Check"),
        ("/health/live", "Liveness Check"),
        ("/health/startup", "Startup Check"),
    ]
    
    for endpoint, description in endpoints:
        try:
            response = client.get(endpoint)
            status = "PASS" if response.status_code == 200 else "FAIL"
            print(f"\n[{status}] {endpoint} - {description}")
            print(f"      Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"      Response: {data}")
                
                # Validate response structure
                if endpoint == "/health/detailed":
                    if "system" in data:
                        print(f"      System metrics present: YES")
                    if "process_id" in data:
                        print(f"      Process ID: {data['process_id']}")
                elif endpoint == "/health/ready":
                    if "checks" in data:
                        print(f"      Checks: {data['checks']}")
            else:
                print(f"      Error: {response.text}")
        except Exception as e:
            print(f"\n[ERROR] {endpoint} - {description}")
            print(f"        Error: {str(e)}")
    
    print("\n" + "="*60)
    print("TEST COMPLETE")
    print("="*60 + "\n")

if __name__ == "__main__":
    test_health_endpoints()
