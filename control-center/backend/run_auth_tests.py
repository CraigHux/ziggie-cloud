"""
Authentication Test Suite Runner
Orchestrates running all authentication tests in proper sequence.
"""

import subprocess
import sys
import time
import asyncio
from pathlib import Path


class TestRunner:
    """Run authentication test suite."""

    def __init__(self):
        self.backend_dir = Path(__file__).parent
        self.test_results = []

    def run_command(self, command: list, description: str, timeout: int = 300) -> bool:
        """Run a command and track results."""
        print("\n" + "="*60)
        print(f"{description}")
        print("="*60)
        print(f"Command: {' '.join(command)}\n")

        try:
            result = subprocess.run(
                command,
                cwd=self.backend_dir,
                timeout=timeout,
                capture_output=False,
                text=True
            )

            success = result.returncode == 0
            status = "PASS" if success else "FAIL"

            self.test_results.append({
                "test": description,
                "status": status,
                "returncode": result.returncode
            })

            return success

        except subprocess.TimeoutExpired:
            print(f"\n✗ Test timed out after {timeout} seconds")
            self.test_results.append({
                "test": description,
                "status": "TIMEOUT",
                "returncode": -1
            })
            return False

        except Exception as e:
            print(f"\n✗ Error running test: {e}")
            self.test_results.append({
                "test": description,
                "status": "ERROR",
                "returncode": -1
            })
            return False

    def print_summary(self):
        """Print test summary."""
        print("\n\n" + "="*60)
        print("AUTHENTICATION TEST SUITE SUMMARY")
        print("="*60)

        passed = sum(1 for r in self.test_results if r["status"] == "PASS")
        failed = sum(1 for r in self.test_results if r["status"] == "FAIL")
        errors = sum(1 for r in self.test_results if r["status"] in ["TIMEOUT", "ERROR"])

        print(f"\nResults:")
        print(f"  Passed: {passed}")
        print(f"  Failed: {failed}")
        print(f"  Errors: {errors}")
        print(f"  Total:  {len(self.test_results)}")

        print(f"\nDetailed Results:")
        for result in self.test_results:
            status_symbol = "[PASS]" if result["status"] == "PASS" else "[FAIL]"
            print(f"  {status_symbol} {result['test']}: {result['status']}")

        if failed > 0 or errors > 0:
            print(f"\n[FAIL] SOME TESTS FAILED")
            print(f"\nNext steps:")
            print(f"  1. Review failures above")
            print(f"  2. Check authentication logs")
            print(f"  3. Consult AUTHENTICATION_DEBUG_GUIDE.md")
            return False
        else:
            print(f"\n[PASS] ALL TESTS PASSED!")
            print(f"\nAuthentication system is working correctly!")
            return True

    def run_all(self, include_http_tests: bool = True):
        """Run all tests."""
        print("\n" + "="*70)
        print(" CONTROL CENTER AUTHENTICATION TEST SUITE")
        print("="*70)

        # Test 1: Local authentication tests
        print("\n" + "="*70)
        print("PHASE 1: LOCAL AUTHENTICATION TESTS")
        print("(Tests components without HTTP)")
        print("="*70)

        self.run_command(
            [sys.executable, "test_bearer_authentication.py"],
            "TEST 1: Bearer Token Authentication (Local Components)"
        )

        # Test 2: HTTP integration tests (if server is available)
        if include_http_tests:
            print("\n" + "="*70)
            print("PHASE 2: HTTP INTEGRATION TESTS")
            print("(Tests actual HTTP endpoints - requires running server)")
            print("="*70)

            print("\nChecking if server is running...")
            print("If server is not running, start it in another terminal:")
            print("  cd C:\\Ziggie\\control-center\\backend")
            print("  python main.py")
            print("\nWaiting 3 seconds before attempting connection...")
            time.sleep(3)

            self.run_command(
                [sys.executable, "test_http_bearer.py"],
                "TEST 2: HTTP Bearer Token Integration Tests",
                timeout=120
            )

        # Print summary
        self.print_summary()


def print_instructions():
    """Print usage instructions."""
    print("""
AUTHENTICATION TEST SUITE

This test suite validates HTTP Bearer token authentication across the entire
authentication system: from password hashing through JWT token validation to
HTTP endpoint security.

USAGE:
    python run_auth_tests.py [options]

OPTIONS:
    --no-http       Skip HTTP integration tests (run local tests only)
    --help          Show this help message

WHAT GETS TESTED:

LOCAL TESTS (Always Run):
    1. Password hashing and verification
    2. JWT token creation and decoding
    3. Database user operations
    4. Bearer token validation
    5. HTTP Bearer header parsing
    6. JWT configuration validation

HTTP INTEGRATION TESTS (Requires running server):
    1. Server availability
    2. Login endpoint
    3. Unauthenticated access rejection
    4. Authenticated access with Bearer token
    5. Invalid token rejection
    6. Malformed header handling
    7. Token expiration information
    8. Protected endpoint access

PREREQUISITES:

1. Navigate to backend directory:
   cd C:\\Ziggie\\control-center\\backend

2. Start the server in another terminal:
   python main.py

3. Run tests:
   python run_auth_tests.py

DEBUGGING:

If tests fail:
    1. Review the failed test output
    2. Check AUTHENTICATION_DEBUG_GUIDE.md
    3. Review server logs
    4. Check middleware/auth.py for issues
    5. Verify JWT_SECRET configuration

COMMON ISSUES:

Q: HTTP tests fail but local tests pass?
A: The authentication logic is correct but the HTTP layer has an issue.
   Check middleware ordering and CORS configuration.

Q: All tests fail?
A: Check JWT_SECRET in config.py and verify database is initialized.

Q: Token validation error "Invalid authentication token"?
A: The token signature is not matching. Check JWT_SECRET is consistent.

For detailed troubleshooting, see AUTHENTICATION_DEBUG_GUIDE.md
    """)


if __name__ == "__main__":
    import sys

    # Parse arguments
    include_http_tests = True

    if "--help" in sys.argv or "-h" in sys.argv:
        print_instructions()
        sys.exit(0)

    if "--no-http" in sys.argv:
        include_http_tests = False

    # Run tests
    runner = TestRunner()
    success = runner.run_all(include_http_tests=include_http_tests)

    sys.exit(0 if success else 1)
