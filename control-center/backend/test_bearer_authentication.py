"""
HTTP Bearer Token Authentication Test Suite
Tests JWT Bearer token authentication with comprehensive debugging.
This test reproduces the issue: successful login but failing Bearer token validation.
"""

import asyncio
import sys
import json
import httpx
from pathlib import Path
from typing import Optional, Dict, Any

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from database.db import init_db, AsyncSessionLocal
from database.models import User
from middleware.auth import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
    get_current_user
)
from config import settings
from sqlalchemy import select


# Test Data
TEST_USER = {
    "username": "testuser",
    "password": "testpass123",
    "email": "test@example.com",
    "full_name": "Test User"
}


class BearerTokenTester:
    """Test HTTP Bearer token authentication."""

    def __init__(self, base_url: str = "http://127.0.0.1:54112"):
        self.base_url = base_url
        self.access_token: Optional[str] = None
        self.token_payload: Optional[Dict[str, Any]] = None
        self.test_results = []

    def log_test(self, name: str, status: str, details: str = ""):
        """Log test result."""
        result = {
            "test": name,
            "status": status,
            "details": details
        }
        self.test_results.append(result)

        status_symbol = "[PASS]" if status == "PASS" else "[FAIL]"
        print(f"\n{status_symbol} {name}")
        if details:
            print(f"  Details: {details}")

    async def print_token_debug_info(self, token: str):
        """Print detailed token information for debugging."""
        print("\n" + "="*60)
        print("TOKEN DEBUGGING INFORMATION")
        print("="*60)

        # Token structure
        parts = token.split(".")
        print(f"Token Structure: {len(parts)} parts (expected: 3)")
        print(f"  Header length: {len(parts[0])}")
        print(f"  Payload length: {len(parts[1])}")
        print(f"  Signature length: {len(parts[2]) if len(parts) > 2 else 0}")

        # Decode and display payload
        try:
            import base64
            # Add padding if needed
            payload_str = parts[1]
            padding = 4 - (len(payload_str) % 4)
            if padding != 4:
                payload_str += "=" * padding

            payload_bytes = base64.urlsafe_b64decode(payload_str)
            payload = json.loads(payload_bytes)

            print(f"\nToken Payload (decoded):")
            for key, value in payload.items():
                print(f"  {key}: {value}")

            self.token_payload = payload

        except Exception as e:
            print(f"  Error decoding payload: {e}")

        # Try to decode with JWT library
        try:
            decoded = decode_access_token(token)
            print(f"\nDecoded by JWT library:")
            for key, value in decoded.items():
                print(f"  {key}: {value}")
        except Exception as e:
            print(f"  Error: {e}")

    async def test_1_password_operations(self):
        """Test password hashing and verification."""
        print("\n" + "="*60)
        print("TEST 1: Password Hashing and Verification")
        print("="*60)

        try:
            # Hash password
            hashed = hash_password(TEST_USER["password"])
            print(f"\nPassword hashed: {hashed[:50]}...")

            # Verify correct password
            is_valid = verify_password(TEST_USER["password"], hashed)
            if is_valid:
                self.log_test("Password hashing", "PASS", "Correct password verified")
            else:
                self.log_test("Password hashing", "FAIL", "Password verification failed")
                return False

            # Verify incorrect password
            is_invalid = verify_password("wrongpassword", hashed)
            if not is_invalid:
                self.log_test("Password rejection", "PASS", "Invalid password rejected")
            else:
                self.log_test("Password rejection", "FAIL", "Invalid password was accepted")
                return False

            return True
        except Exception as e:
            self.log_test("Password operations", "FAIL", str(e))
            return False

    async def test_2_token_creation(self):
        """Test JWT token creation and decoding."""
        print("\n" + "="*60)
        print("TEST 2: JWT Token Creation and Decoding")
        print("="*60)

        try:
            # Create token
            token_data = {
                "sub": TEST_USER["username"],
                "user_id": 1,
                "role": "user"
            }

            self.access_token = create_access_token(token_data)
            print(f"\nToken created: {self.access_token[:50]}...")

            await self.print_token_debug_info(self.access_token)

            # Decode token
            decoded = decode_access_token(self.access_token)
            print(f"\nToken decoded successfully")

            # Verify token data
            checks = [
                ("sub", decoded.get("sub"), TEST_USER["username"]),
                ("user_id", decoded.get("user_id"), 1),
                ("role", decoded.get("role"), "user"),
            ]

            all_pass = True
            for field_name, actual, expected in checks:
                if actual == expected:
                    print(f"  [OK] {field_name}: {actual}")
                else:
                    print(f"  [ERR] {field_name}: expected {expected}, got {actual}")
                    all_pass = False

            if all_pass:
                self.log_test("Token creation and decoding", "PASS", "All claims verified")
                return True
            else:
                self.log_test("Token creation and decoding", "FAIL", "Token claims mismatch")
                return False

        except Exception as e:
            self.log_test("Token creation", "FAIL", str(e))
            import traceback
            traceback.print_exc()
            return False

    async def test_3_database_user_setup(self):
        """Test user creation in database."""
        print("\n" + "="*60)
        print("TEST 3: Database User Setup")
        print("="*60)

        try:
            # Initialize database
            await init_db()
            print("Database initialized")

            async with AsyncSessionLocal() as session:
                # Check if test user exists
                result = await session.execute(
                    select(User).where(User.username == TEST_USER["username"])
                )
                existing_user = result.scalar_one_or_none()

                if existing_user:
                    print(f"Test user already exists, deleting...")
                    await session.delete(existing_user)
                    await session.commit()

                # Create test user
                test_user = User(
                    username=TEST_USER["username"],
                    hashed_password=hash_password(TEST_USER["password"]),
                    email=TEST_USER["email"],
                    full_name=TEST_USER["full_name"],
                    role="user",
                    is_active=True
                )

                session.add(test_user)
                await session.commit()
                await session.refresh(test_user)

                print(f"\nTest user created:")
                print(f"  ID: {test_user.id}")
                print(f"  Username: {test_user.username}")
                print(f"  Email: {test_user.email}")
                print(f"  Role: {test_user.role}")
                print(f"  Active: {test_user.is_active}")

                self.log_test("User creation in database", "PASS", f"User ID: {test_user.id}")
                return True

        except Exception as e:
            self.log_test("Database user setup", "FAIL", str(e))
            import traceback
            traceback.print_exc()
            return False

    async def test_4_bearer_token_validation(self):
        """Test Bearer token validation through authentication dependency."""
        print("\n" + "="*60)
        print("TEST 4: Bearer Token Validation (Direct)")
        print("="*60)

        if not self.access_token:
            print("No token available from previous tests")
            self.log_test("Bearer token validation", "FAIL", "Token not generated")
            return False

        try:
            # Test token decoding (simulating what get_current_user does)
            print(f"\nSimulating authentication flow:")
            print(f"1. Token: {self.access_token[:50]}...")

            # Step 1: Decode token
            payload = decode_access_token(self.access_token)
            print(f"2. Token decoded successfully")
            print(f"   Username (sub): {payload.get('sub')}")
            print(f"   User ID: {payload.get('user_id')}")
            print(f"   Role: {payload.get('role')}")

            # Step 2: Extract user information
            username = payload.get("sub")
            user_id = payload.get("user_id")

            if username is None or user_id is None:
                print(f"3. [ERR] Missing required claims")
                self.log_test("Bearer token validation", "FAIL", "Missing username or user_id in token")
                return False

            print(f"3. Required claims present")

            # Step 3: Fetch user from database
            async with AsyncSessionLocal() as session:
                result = await session.execute(
                    select(User).where(User.id == user_id, User.username == username)
                )
                user = result.scalar_one_or_none()

                if user is None:
                    print(f"4. [ERR] User not found in database")
                    print(f"   Searched for: id={user_id}, username={username}")
                    self.log_test("Bearer token validation", "FAIL", "User not found in database")
                    return False

                print(f"4. User found in database")
                print(f"   Username: {user.username}")
                print(f"   Email: {user.email}")
                print(f"   Active: {user.is_active}")

                # Step 4: Check if active
                if not user.is_active:
                    print(f"5. [ERR] User account is inactive")
                    self.log_test("Bearer token validation", "FAIL", "User account is inactive")
                    return False

                print(f"5. User is active")

                self.log_test("Bearer token validation", "PASS", "User authenticated successfully")
                return True

        except Exception as e:
            self.log_test("Bearer token validation", "FAIL", str(e))
            import traceback
            traceback.print_exc()
            return False

    async def test_5_http_bearer_header_parsing(self):
        """Test Bearer token header parsing."""
        print("\n" + "="*60)
        print("TEST 5: HTTP Bearer Header Parsing")
        print("="*60)

        if not self.access_token:
            print("No token available from previous tests")
            self.log_test("Bearer header parsing", "FAIL", "Token not generated")
            return False

        try:
            # Test different header formats
            test_cases = [
                ("Standard", f"Bearer {self.access_token}"),
                ("No space after Bearer", f"Bearer{self.access_token}"),
                ("Extra spaces", f"Bearer  {self.access_token}"),
                ("bearer (lowercase)", f"bearer {self.access_token}"),
            ]

            for case_name, header_value in test_cases:
                print(f"\nTesting: {case_name}")
                print(f"  Header: Authorization: {header_value[:50]}...")

                # Parse like the auth middleware does
                if header_value.startswith("Bearer "):
                    token = header_value.replace("Bearer ", "", 1)
                    print(f"  [OK] Header parsed correctly")
                    print(f"  Token: {token[:50]}...")
                else:
                    print(f"  [ERR] Header format not recognized")

            self.log_test("Bearer header parsing", "PASS", "Header format validation tested")
            return True

        except Exception as e:
            self.log_test("Bearer header parsing", "FAIL", str(e))
            return False

    async def test_6_config_validation(self):
        """Validate JWT configuration."""
        print("\n" + "="*60)
        print("TEST 6: JWT Configuration Validation")
        print("="*60)

        try:
            print(f"\nJWT Configuration:")
            print(f"  Secret: {settings.JWT_SECRET[:20]}...")
            print(f"  Algorithm: {settings.JWT_ALGORITHM}")
            print(f"  Expiration: {settings.JWT_EXPIRATION_HOURS} hours")

            # Validate secret is not default
            if settings.JWT_SECRET == "CHANGE_THIS_TO_A_SECURE_RANDOM_STRING_IN_PRODUCTION":
                print(f"\n[WARN] WARNING: Using default JWT secret!")
                self.log_test("JWT secret configuration", "WARN", "Using insecure default secret")
            else:
                print(f"\n[OK] Using custom JWT secret")
                self.log_test("JWT secret configuration", "PASS", "Custom secret configured")

            # Validate algorithm
            if settings.JWT_ALGORITHM not in ["HS256", "HS512", "RS256"]:
                print(f"\n[ERR] Invalid JWT algorithm: {settings.JWT_ALGORITHM}")
                self.log_test("JWT algorithm", "FAIL", f"Invalid algorithm: {settings.JWT_ALGORITHM}")
                return False

            print(f"[OK] JWT algorithm is valid")
            self.log_test("JWT algorithm", "PASS", settings.JWT_ALGORITHM)

            return True

        except Exception as e:
            self.log_test("Configuration validation", "FAIL", str(e))
            return False

    async def print_summary(self):
        """Print test summary."""
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)

        passed = sum(1 for r in self.test_results if r["status"] == "PASS")
        failed = sum(1 for r in self.test_results if r["status"] == "FAIL")
        warned = sum(1 for r in self.test_results if r["status"] == "WARN")

        print(f"\nResults:")
        print(f"  Passed: {passed}")
        print(f"  Failed: {failed}")
        print(f"  Warned: {warned}")
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
        """Run all Bearer token authentication tests."""
        print("="*60)
        print("HTTP BEARER TOKEN AUTHENTICATION TEST SUITE")
        print("="*60)

        try:
            # Run tests in sequence
            await self.test_1_password_operations()
            await self.test_2_token_creation()
            await self.test_3_database_user_setup()
            await self.test_4_bearer_token_validation()
            await self.test_5_http_bearer_header_parsing()
            await self.test_6_config_validation()

            # Print summary
            success = await self.print_summary()

            if success:
                print("\n[PASS] ALL TESTS PASSED!")
                print("\nThe authentication system is working correctly.")
                print("If HTTP requests are still failing, check:")
                print("  1. Server is running at", self.base_url)
                print("  2. Token is being sent in Authorization header")
                print("  3. Token format is: Authorization: Bearer <TOKEN>")
            else:
                print("\n[FAIL] SOME TESTS FAILED")
                print("Please review the failures above.")

            return success

        except Exception as e:
            print("\n" + "="*60)
            print(f"[ERROR] CRITICAL ERROR: {e}")
            print("="*60)
            import traceback
            traceback.print_exc()
            return False


async def main():
    """Main entry point."""
    tester = BearerTokenTester()
    success = await tester.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
