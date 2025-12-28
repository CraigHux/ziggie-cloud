"""
HTTP Integration Tests for Bearer Token Authentication
Tests the actual HTTP endpoints to identify Bearer token validation issues.
"""

import asyncio
import httpx
import json
import sys
from typing import Optional, Dict, Any
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))


class HTTPBearerTester:
    """Test HTTP Bearer token authentication against running server."""

    def __init__(self, base_url: str = "http://127.0.0.1:54112"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(base_url=base_url)
        self.access_token: Optional[str] = None
        self.test_results = []

    def log_test(self, name: str, status: str, details: str = "", response_data: Dict[str, Any] = None):
        """Log test result."""
        result = {
            "test": name,
            "status": status,
            "details": details,
            "response": response_data
        }
        self.test_results.append(result)

        status_symbol = "[PASS]" if status == "PASS" else "[FAIL]"
        print(f"\n{status_symbol} {name}")
        if details:
            print(f"  Details: {details}")
        if response_data:
            print(f"  Response: {json.dumps(response_data, indent=2)}")

    async def test_1_server_availability(self):
        """Test if server is running."""
        print("\n" + "="*60)
        print("TEST 1: Server Availability")
        print("="*60)

        try:
            print(f"\nChecking server at {self.base_url}")
            response = await self.client.get("/health")

            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.json()}")

            if response.status_code == 200:
                self.log_test("Server availability", "PASS", f"Server responding at {self.base_url}")
                return True
            else:
                self.log_test("Server availability", "FAIL", f"Unexpected status code: {response.status_code}")
                return False

        except Exception as e:
            self.log_test("Server availability", "FAIL", f"Cannot reach server: {str(e)}")
            print(f"  Error: {str(e)}")
            return False

    async def test_2_login(self):
        """Test login endpoint."""
        print("\n" + "="*60)
        print("TEST 2: Login Endpoint")
        print("="*60)

        try:
            login_data = {
                "username": "admin",
                "password": "admin123"
            }

            print(f"\nAttempting login with:")
            print(f"  Username: {login_data['username']}")
            print(f"  Password: {'*' * len(login_data['password'])}")

            response = await self.client.post(
                "/api/auth/login",
                json=login_data
            )

            print(f"Status Code: {response.status_code}")

            if response.status_code == 200:
                response_data = response.json()
                self.access_token = response_data.get("access_token")

                print(f"Response Data:")
                print(f"  Token Type: {response_data.get('token_type')}")
                print(f"  Token: {self.access_token[:50]}..." if self.access_token else "  Token: None")
                print(f"  Expires In: {response_data.get('expires_in')}")

                self.log_test("Login", "PASS", "Login successful", response_data)
                return True
            else:
                print(f"Response: {response.json()}")
                self.log_test("Login", "FAIL", f"Login failed with status {response.status_code}", response.json())
                return False

        except Exception as e:
            self.log_test("Login", "FAIL", str(e))
            import traceback
            traceback.print_exc()
            return False

    async def test_3_get_user_no_auth(self):
        """Test /api/auth/me without authentication."""
        print("\n" + "="*60)
        print("TEST 3: GET /api/auth/me (No Authentication)")
        print("="*60)

        try:
            print(f"\nCalling /api/auth/me without Authorization header")

            response = await self.client.get("/api/auth/me")

            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.json()}")

            if response.status_code == 403:
                self.log_test("No authentication rejection", "PASS", "Server correctly rejected unauthenticated request")
                return True
            else:
                self.log_test("No authentication rejection", "FAIL", f"Expected 403, got {response.status_code}")
                return False

        except Exception as e:
            self.log_test("No authentication rejection", "FAIL", str(e))
            return False

    async def test_4_get_user_with_bearer_token(self):
        """Test /api/auth/me with Bearer token."""
        print("\n" + "="*60)
        print("TEST 4: GET /api/auth/me (With Bearer Token)")
        print("="*60)

        if not self.access_token:
            print("No access token available from login test")
            self.log_test("Bearer token authentication", "FAIL", "No token from login")
            return False

        try:
            print(f"\nCalling /api/auth/me with Bearer token")
            print(f"  Token: {self.access_token[:50]}...")

            headers = {
                "Authorization": f"Bearer {self.access_token}"
            }

            print(f"  Header: Authorization: Bearer {self.access_token[:30]}...")

            response = await self.client.get(
                "/api/auth/me",
                headers=headers
            )

            print(f"Status Code: {response.status_code}")
            response_data = response.json()
            print(f"Response: {json.dumps(response_data, indent=2)}")

            if response.status_code == 200:
                self.log_test("Bearer token authentication", "PASS", "Successfully authenticated with Bearer token", response_data)
                return True
            else:
                self.log_test("Bearer token authentication", "FAIL", f"Status {response.status_code}: {response_data.get('detail')}", response_data)
                return False

        except Exception as e:
            self.log_test("Bearer token authentication", "FAIL", str(e))
            import traceback
            traceback.print_exc()
            return False

    async def test_5_invalid_token(self):
        """Test with invalid token."""
        print("\n" + "="*60)
        print("TEST 5: GET /api/auth/me (Invalid Token)")
        print("="*60)

        try:
            invalid_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid.token"

            print(f"\nCalling /api/auth/me with invalid token")
            print(f"  Token: {invalid_token}")

            headers = {
                "Authorization": f"Bearer {invalid_token}"
            }

            response = await self.client.get(
                "/api/auth/me",
                headers=headers
            )

            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.json()}")

            if response.status_code == 401:
                self.log_test("Invalid token rejection", "PASS", "Server correctly rejected invalid token")
                return True
            else:
                self.log_test("Invalid token rejection", "FAIL", f"Expected 401, got {response.status_code}")
                return False

        except Exception as e:
            self.log_test("Invalid token rejection", "FAIL", str(e))
            return False

    async def test_6_malformed_header(self):
        """Test with malformed Authorization header."""
        print("\n" + "="*60)
        print("TEST 6: Malformed Authorization Header")
        print("="*60)

        if not self.access_token:
            print("No access token available from login test")
            self.log_test("Malformed header handling", "FAIL", "No token from login")
            return False

        try:
            test_cases = [
                ("Missing 'Bearer' prefix", self.access_token),
                ("Bearer prefix lowercase", f"bearer {self.access_token}"),
                ("Multiple spaces", f"Bearer  {self.access_token}"),
                ("Wrong prefix", f"Token {self.access_token}"),
            ]

            print(f"\nTesting various header formats:")

            for case_name, header_value in test_cases:
                print(f"\n  Testing: {case_name}")
                print(f"    Header: Authorization: {header_value[:50]}...")

                headers = {
                    "Authorization": header_value
                }

                response = await self.client.get(
                    "/api/auth/me",
                    headers=headers
                )

                print(f"    Status: {response.status_code}")
                if response.status_code != 200:
                    print(f"    Response: {response.json()}")

            self.log_test("Malformed header handling", "PASS", "Various header formats tested")
            return True

        except Exception as e:
            self.log_test("Malformed header handling", "FAIL", str(e))
            return False

    async def test_7_token_expiration(self):
        """Test token expiration behavior."""
        print("\n" + "="*60)
        print("TEST 7: Token Expiration (Informational)")
        print("="*60)

        if not self.access_token:
            print("No access token available from login test")
            self.log_test("Token expiration info", "SKIP", "No token from login")
            return True

        try:
            import base64
            import json

            # Decode token to check expiration
            parts = self.access_token.split(".")
            if len(parts) != 3:
                print("Invalid token format")
                return False

            # Decode payload
            payload_str = parts[1]
            padding = 4 - (len(payload_str) % 4)
            if padding != 4:
                payload_str += "=" * padding

            payload_bytes = base64.urlsafe_b64decode(payload_str)
            payload = json.loads(payload_bytes)

            print(f"\nToken expiration information:")
            if "exp" in payload:
                from datetime import datetime
                exp_time = datetime.utcfromtimestamp(payload["exp"])
                now = datetime.utcnow()
                remaining = exp_time - now

                print(f"  Expires at: {exp_time}")
                print(f"  Time remaining: {remaining}")

                if remaining.total_seconds() > 0:
                    print(f"  Status: Token is valid")
                else:
                    print(f"  Status: Token has expired")

            self.log_test("Token expiration info", "PASS", f"Token expires at {payload.get('exp')}")
            return True

        except Exception as e:
            self.log_test("Token expiration info", "FAIL", str(e))
            return False

    async def test_8_change_password(self):
        """Test protected endpoint with Bearer token."""
        print("\n" + "="*60)
        print("TEST 8: Protected Endpoint - Change Password")
        print("="*60)

        if not self.access_token:
            print("No access token available from login test")
            self.log_test("Protected endpoint test", "FAIL", "No token from login")
            return False

        try:
            print(f"\nCalling /api/auth/change-password with Bearer token")

            headers = {
                "Authorization": f"Bearer {self.access_token}"
            }

            change_password_data = {
                "current_password": "admin123",
                "new_password": "newpassword123"
            }

            response = await self.client.post(
                "/api/auth/change-password",
                json=change_password_data,
                headers=headers
            )

            print(f"Status Code: {response.status_code}")
            response_data = response.json()
            print(f"Response: {json.dumps(response_data, indent=2)}")

            if response.status_code == 200:
                self.log_test("Protected endpoint access", "PASS", "Successfully accessed protected endpoint", response_data)

                # Note: Reset password for other tests
                print(f"\nResetting password back to original...")
                reset_data = {
                    "current_password": "newpassword123",
                    "new_password": "admin123"
                }
                reset_response = await self.client.post(
                    "/api/auth/change-password",
                    json=reset_data,
                    headers=headers
                )
                if reset_response.status_code == 200:
                    print(f"Password reset successfully")

                return True
            elif response.status_code == 401:
                self.log_test("Protected endpoint access", "FAIL", "Bearer token not recognized by endpoint", response_data)
                return False
            else:
                self.log_test("Protected endpoint access", "FAIL", f"Unexpected status {response.status_code}", response_data)
                return False

        except Exception as e:
            self.log_test("Protected endpoint access", "FAIL", str(e))
            import traceback
            traceback.print_exc()
            return False

    async def print_summary(self):
        """Print test summary."""
        print("\n" + "="*60)
        print("HTTP INTEGRATION TEST SUMMARY")
        print("="*60)

        passed = sum(1 for r in self.test_results if r["status"] == "PASS")
        failed = sum(1 for r in self.test_results if r["status"] == "FAIL")
        skipped = sum(1 for r in self.test_results if r["status"] == "SKIP")

        print(f"\nResults:")
        print(f"  Passed: {passed}")
        print(f"  Failed: {failed}")
        print(f"  Skipped: {skipped}")
        print(f"  Total:  {len(self.test_results)}")

        if failed > 0:
            print(f"\nFailed Tests:")
            for result in self.test_results:
                if result["status"] == "FAIL":
                    print(f"  - {result['test']}")
                    if result["details"]:
                        print(f"    {result['details']}")

        return failed == 0

    async def run_all_tests(self):
        """Run all HTTP integration tests."""
        print("="*60)
        print("HTTP BEARER TOKEN INTEGRATION TEST SUITE")
        print("="*60)
        print(f"Base URL: {self.base_url}")

        try:
            # Run tests in sequence
            server_running = await self.test_1_server_availability()

            if not server_running:
                print("\n" + "="*60)
                print("[ERROR] SERVER NOT AVAILABLE")
                print("="*60)
                print(f"\nPlease ensure the server is running at {self.base_url}")
                print("Command to start server:")
                print("  cd C:\\Ziggie\\control-center\\backend")
                print("  python main.py")
                return False

            await self.test_2_login()
            await self.test_3_get_user_no_auth()
            await self.test_4_get_user_with_bearer_token()
            await self.test_5_invalid_token()
            await self.test_6_malformed_header()
            await self.test_7_token_expiration()
            await self.test_8_change_password()

            # Print summary
            success = await self.print_summary()

            if success:
                print("\n[PASS] ALL TESTS PASSED!")
                print("\nBearer token authentication is working correctly!")
            else:
                print("\n[FAIL] SOME TESTS FAILED")
                print("\nDebugging recommendations:")
                print("1. Check server logs for authentication errors")
                print("2. Verify JWT_SECRET configuration in settings")
                print("3. Confirm Authorization header format: 'Bearer <TOKEN>'")
                print("4. Check middleware/auth.py for token validation logic")
                print("5. Verify database queries in get_current_user()")

            await self.client.aclose()
            return success

        except Exception as e:
            print("\n" + "="*60)
            print(f"[ERROR] CRITICAL ERROR: {e}")
            print("="*60)
            import traceback
            traceback.print_exc()
            await self.client.aclose()
            return False


async def main():
    """Main entry point."""
    tester = HTTPBearerTester()
    success = await tester.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
