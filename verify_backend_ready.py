"""Quick verification that backend is ready for frontend integration."""
import requests
import json

BASE_URL = "http://127.0.0.1:54112"

print("=" * 80)
print("BACKEND READINESS VERIFICATION")
print("=" * 80)
print()

# Critical endpoints for dashboard
critical_endpoints = [
    ("System Stats", "/api/system/stats"),
    ("Agent Stats", "/api/agents/stats"),
    ("Services List", "/api/services"),
    ("Health Check", "/health")
]

all_passing = True

for name, endpoint in critical_endpoints:
    try:
        response = requests.get(f"{BASE_URL}{endpoint}", timeout=30)
        if response.status_code == 200:
            print(f"[OK] {name:20} - READY")
        else:
            print(f"[FAIL] {name:20} - FAILED ({response.status_code})")
            all_passing = False
    except Exception as e:
        print(f"[ERROR] {name:20} - ERROR: {str(e)[:40]}")
        all_passing = False

print()
print("=" * 80)

if all_passing:
    print("STATUS: BACKEND READY FOR FRONTEND INTEGRATION [OK]")
    print()
    print("Next steps:")
    print("1. Frontend team: Update API timeouts to 30+ seconds")
    print("2. Frontend team: Verify CORS origins include your dev server")
    print("3. Frontend team: Check authentication token handling")
    print("4. Test dashboard with: http://127.0.0.1:54112/api/system/stats")
else:
    print("STATUS: BACKEND NOT READY - CHECK ERRORS ABOVE")

print("=" * 80)
