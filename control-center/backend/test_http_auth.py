"""
Test the actual HTTP authentication flow using TestClient
"""
from fastapi.testclient import TestClient
from main import app
import jwt
from config import settings

# Create test client
client = TestClient(app)

print("=" * 80)
print("HTTP AUTHENTICATION FLOW TEST")
print("=" * 80)

# Test 1: Login to get token
print("\n1. Testing Login")
print("-" * 80)
response = client.post(
    "/api/auth/login",
    json={"username": "admin", "password": "admin123"}
)
print(f"Status Code: {response.status_code}")
print(f"Response: {response.json()}")

if response.status_code == 200:
    token_data = response.json()
    access_token = token_data["access_token"]
    print(f"[OK] Login successful")
    print(f"Token (first 50 chars): {access_token[:50]}...")

    # Decode token to see payload
    payload = jwt.decode(access_token, options={"verify_signature": False})
    print(f"Token payload: {payload}")
else:
    print(f"[FAIL] Login failed")
    exit(1)

# Test 2: Try to access /api/auth/me with token
print("\n2. Testing /api/auth/me with Bearer token")
print("-" * 80)

# Test different header formats
test_cases = [
    ("Bearer format", f"Bearer {access_token}"),
    ("Token only (no Bearer)", access_token),
]

for test_name, auth_value in test_cases:
    print(f"\n  Testing: {test_name}")
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": auth_value}
    )
    print(f"  Status Code: {response.status_code}")
    if response.status_code == 200:
        print(f"  [OK] Authentication successful")
        print(f"  Response: {response.json()}")
    else:
        print(f"  [FAIL] Authentication failed")
        print(f"  Response: {response.text}")

# Test 3: Test without Authorization header
print("\n3. Testing /api/auth/me WITHOUT token")
print("-" * 80)
response = client.get("/api/auth/me")
print(f"Status Code: {response.status_code}")
print(f"Response: {response.text}")

# Test 4: Test with invalid token
print("\n4. Testing /api/auth/me with INVALID token")
print("-" * 80)
response = client.get(
    "/api/auth/me",
    headers={"Authorization": "Bearer invalid_token_here"}
)
print(f"Status Code: {response.status_code}")
print(f"Response: {response.text}")

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)
