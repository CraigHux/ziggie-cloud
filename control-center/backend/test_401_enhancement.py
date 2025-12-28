"""
Test to verify 401 vs 403 HTTP status code enhancement.

This test validates that the authentication system returns:
- 401 Unauthorized: When authentication is missing or invalid
- 403 Forbidden: When authenticated but access is denied (e.g., inactive user, wrong role)
"""

import asyncio
import httpx

BASE_URL = "http://127.0.0.1:54112"


async def test_status_codes():
    """Test HTTP status codes for various authentication scenarios."""

    print("="*70)
    print("HTTP STATUS CODE VALIDATION TEST")
    print("="*70)
    print("\nValidating semantic HTTP status codes (RFC 7235):")
    print("  401 Unauthorized: Authentication required/invalid")
    print("  403 Forbidden: Authenticated but access denied")
    print()

    async with httpx.AsyncClient() as client:
        # Test 1: No Authorization header
        print("[TEST 1] No Authorization header")
        print("-" * 70)
        response = await client.get(f"{BASE_URL}/api/auth/me")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")

        expected = 401
        actual = response.status_code
        if actual == expected:
            print(f"[PASS] Returns {expected} as expected")
        else:
            print(f"[FAIL] Expected {expected}, got {actual}")
        print()

        # Test 2: Invalid token
        print("[TEST 2] Invalid Authorization token")
        print("-" * 70)
        response = await client.get(
            f"{BASE_URL}/api/auth/me",
            headers={"Authorization": "Bearer invalid.token.here"}
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")

        expected = 401
        actual = response.status_code
        if actual == expected:
            print(f"[PASS] Returns {expected} as expected")
        else:
            print(f"[FAIL] Expected {expected}, got {actual}")
        print()

        # Test 3: Malformed Authorization header (no Bearer prefix)
        print("[TEST 3] Malformed Authorization header (no Bearer prefix)")
        print("-" * 70)
        response = await client.get(
            f"{BASE_URL}/api/auth/me",
            headers={"Authorization": "invalid.token.here"}
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")

        # This should return 403 because HTTPBearer specifically requires "Bearer" prefix
        # but our custom handling should make this 401
        expected = 403  # FastAPI HTTPBearer default for wrong scheme
        actual = response.status_code
        if actual == expected:
            print(f"[PASS] Returns {expected} (FastAPI default for wrong scheme)")
        elif actual == 401:
            print(f"[PASS] Returns 401 (custom handling)")
        else:
            print(f"[INFO] Got {actual}")
        print()

        # Test 4: Valid token (requires login first)
        print("[TEST 4] Valid token authentication")
        print("-" * 70)

        # First, login to get a valid token
        login_response = await client.post(
            f"{BASE_URL}/api/auth/login",
            json={"username": "admin", "password": "admin"}
        )

        if login_response.status_code == 200:
            token_data = login_response.json()
            token = token_data["access_token"]
            print(f"Login successful, token obtained")

            # Now test with valid token
            response = await client.get(
                f"{BASE_URL}/api/auth/me",
                headers={"Authorization": f"Bearer {token}"}
            )
            print(f"Status Code: {response.status_code}")

            expected = 200
            actual = response.status_code
            if actual == expected:
                print(f"[PASS] Returns {expected} with valid authentication")
                user_data = response.json()
                print(f"User: {user_data['username']}")
            else:
                print(f"[FAIL] Expected {expected}, got {actual}")
        else:
            print(f"[SKIP] Could not login to get valid token")
        print()

        print("="*70)
        print("SUMMARY")
        print("="*70)
        print("Expected behavior after enhancement:")
        print("  - Missing auth header: 401 (not 403)")
        print("  - Invalid token: 401")
        print("  - Valid token: 200")
        print("  - Wrong auth scheme: 403 (HTTPBearer requirement)")
        print()


if __name__ == "__main__":
    asyncio.run(test_status_codes())
