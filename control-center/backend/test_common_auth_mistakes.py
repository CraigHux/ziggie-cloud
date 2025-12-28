"""
Demonstrates common authentication mistakes and their solutions
"""
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

# Get a valid token first
print("Getting valid token...")
response = client.post("/api/auth/login", json={"username": "admin", "password": "admin123"})
token = response.json()["access_token"]
print(f"Token obtained: {token[:50]}...")

print("\n" + "=" * 80)
print("TESTING COMMON AUTHENTICATION MISTAKES")
print("=" * 80)

# Test cases
test_cases = [
    {
        "name": "[OK] CORRECT: Bearer token",
        "headers": {"Authorization": f"Bearer {token}"},
        "expected": 200,
        "description": "Standard OAuth2/JWT format with 'Bearer ' prefix"
    },
    {
        "name": "[FAIL] MISTAKE #1: Missing 'Bearer ' prefix",
        "headers": {"Authorization": token},
        "expected": 403,
        "description": "Token sent directly without 'Bearer ' scheme"
    },
    {
        "name": "[FAIL] MISTAKE #2: Double 'Bearer ' prefix",
        "headers": {"Authorization": f"Bearer Bearer {token}"},
        "expected": 401,
        "description": "Token already had 'Bearer ' when stored, added again"
    },
    {
        "name": "[FAIL] MISTAKE #3: Wrong scheme name",
        "headers": {"Authorization": f"Token {token}"},
        "expected": 403,
        "description": "Using 'Token' instead of 'Bearer'"
    },
    {
        "name": "[FAIL] MISTAKE #4: Lowercase 'bearer'",
        "headers": {"Authorization": f"bearer {token}"},
        "expected": 403,
        "description": "HTTPBearer expects 'Bearer' with capital B"
    },
    {
        "name": "[FAIL] MISTAKE #5: No Authorization header",
        "headers": {},
        "expected": 403,
        "description": "Authorization header completely missing"
    },
    {
        "name": "[FAIL] MISTAKE #6: Wrong header name",
        "headers": {"Authentication": f"Bearer {token}"},
        "expected": 403,
        "description": "Using 'Authentication' instead of 'Authorization'"
    },
    {
        "name": "[FAIL] MISTAKE #7: Custom header name",
        "headers": {"X-Auth-Token": token},
        "expected": 403,
        "description": "Using custom header instead of standard Authorization"
    },
]

for i, test in enumerate(test_cases, 1):
    print(f"\n{i}. {test['name']}")
    print("-" * 80)
    print(f"Description: {test['description']}")
    print(f"Headers: {test['headers']}")

    response = client.get("/api/auth/me", headers=test['headers'])

    print(f"Expected Status: {test['expected']}")
    print(f"Actual Status: {response.status_code}")

    if response.status_code == test['expected']:
        print("Result: [OK] BEHAVED AS EXPECTED")
    else:
        print("Result: [WARNING] UNEXPECTED BEHAVIOR")

    if response.status_code == 200:
        user_data = response.json()
        print(f"User: {user_data['username']} (ID: {user_data['id']})")
    else:
        print(f"Error: {response.json()}")

print("\n" + "=" * 80)
print("KEY TAKEAWAYS")
print("=" * 80)
print("""
1. ALWAYS use the format: Authorization: Bearer <token>
2. The word 'Bearer' must have a capital 'B'
3. There must be exactly ONE space after 'Bearer'
4. Do NOT include 'Bearer ' when storing the token
5. ADD 'Bearer ' when sending the request

CORRECT CLIENT CODE:
    // When storing after login
    localStorage.setItem('token', response.data.access_token)  // NO "Bearer " here

    // When making authenticated request
    headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`  // ADD "Bearer " here
    }
""")
