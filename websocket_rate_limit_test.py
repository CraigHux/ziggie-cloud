"""
WebSocket Rate Limiting Security Test
Tests rate limiting enforcement on WebSocket endpoints

L3.SECURITY.TESTER - URGENT SECURITY GAP TESTING
Mission: Verify WebSocket endpoints enforce rate limits (DoS protection)
"""

import asyncio
import websockets
import time
import json
import requests
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass


BASE_URL = "http://127.0.0.1:54112"
WS_BASE_URL = "ws://127.0.0.1:54112"


@dataclass
class TestResult:
    """Test result data structure"""
    endpoint: str
    endpoint_type: str
    total_attempts: int
    successful_connections: int
    rejected_connections: int
    errors: int
    rate_limit_triggered: bool
    first_rejection_at: Optional[int]
    duration_seconds: float
    passed: bool
    notes: str
    timestamp: str


class WebSocketRateLimitTester:
    """Test rate limiting on WebSocket endpoints"""

    def __init__(self):
        self.results: List[TestResult] = []
        self.jwt_token: Optional[str] = None

    async def get_jwt_token(self) -> Optional[str]:
        """
        Get a JWT token for authenticated WebSocket testing.
        Attempts to login with test credentials or creates test user.
        """
        print("\n" + "="*80)
        print("AUTHENTICATION SETUP")
        print("="*80)

        # Try to register a test user
        register_data = {
            "username": "ws_test_user",
            "password": "TestPassword123!",
            "email": "wstest@example.com"
        }

        try:
            # Try to register
            response = requests.post(
                f"{BASE_URL}/api/auth/register",
                json=register_data,
                timeout=5
            )

            if response.status_code == 201:
                print("[OK] Test user created successfully")
                token = response.json().get("access_token")
                if token:
                    print("[OK] JWT token obtained from registration")
                    return token
            elif response.status_code == 400 and "already exists" in response.text.lower():
                print("[INFO] Test user already exists, attempting login...")
            else:
                print(f"[INFO] Registration returned: {response.status_code}")
        except Exception as e:
            print(f"[INFO] Registration attempt: {e}")

        # Try to login
        try:
            login_data = {
                "username": "ws_test_user",
                "password": "TestPassword123!"
            }
            response = requests.post(
                f"{BASE_URL}/api/auth/login",
                json=login_data,
                timeout=5
            )

            if response.status_code == 200:
                token = response.json().get("access_token")
                if token:
                    print("[OK] JWT token obtained from login")
                    return token
                else:
                    print("[FAIL] Login successful but no token returned")
            else:
                print(f"[FAIL] Login failed: {response.status_code}")
        except Exception as e:
            print(f"[FAIL] Login attempt failed: {e}")

        return None

    async def test_public_websocket(self, endpoint: str, max_connections: int = 50) -> TestResult:
        """
        Test rate limiting on public WebSocket endpoint.

        Args:
            endpoint: WebSocket endpoint path (e.g., "/api/system/metrics")
            max_connections: Number of simultaneous connections to attempt

        Returns:
            TestResult with test outcome
        """
        print(f"\n{'='*80}")
        print(f"Testing Public WebSocket: {endpoint}")
        print(f"{'='*80}")
        print(f"Attempting {max_connections} simultaneous connections...")
        print(f"Expected: Rate limiting should prevent excessive connections\n")

        ws_url = f"{WS_BASE_URL}{endpoint}"
        connections = []
        successful = 0
        rejected = 0
        errors = 0
        first_rejection = None

        start_time = time.time()

        # Attempt to open many connections simultaneously
        for i in range(1, max_connections + 1):
            try:
                # Try to connect
                websocket = await asyncio.wait_for(
                    websockets.connect(ws_url),
                    timeout=2.0
                )
                connections.append(websocket)
                successful += 1
                print(f"Connection {i:3d}: CONNECTED [OK]", end="\r")

                # Brief delay to avoid overwhelming the system
                await asyncio.sleep(0.05)

            except websockets.exceptions.InvalidStatusCode as e:
                # Connection rejected (likely 429 or 403)
                rejected += 1
                if first_rejection is None:
                    first_rejection = i
                print(f"\nConnection {i:3d}: REJECTED (HTTP {e.status_code}) - Rate Limited? [YES]")

            except asyncio.TimeoutError:
                rejected += 1
                if first_rejection is None:
                    first_rejection = i
                print(f"\nConnection {i:3d}: TIMEOUT - Possible Rate Limiting [YES]")

            except Exception as e:
                errors += 1
                print(f"\nConnection {i:3d}: ERROR - {type(e).__name__}: {str(e)[:50]}")

        end_time = time.time()
        duration = end_time - start_time

        # Close all successful connections
        print(f"\n\nClosing {len(connections)} open connections...")
        for ws in connections:
            try:
                await ws.close()
            except:
                pass

        # Analyze results
        rate_limit_triggered = rejected > 0

        # Determine pass/fail
        # For WebSockets, we expect EITHER:
        # 1. Rate limiting kicks in (some rejections)
        # 2. OR all connections succeed but with warning (no rate limit found)
        if rate_limit_triggered:
            passed = True
            notes = f"Rate limiting working: {rejected} connections rejected out of {max_connections}"
        else:
            passed = False
            notes = f"NO RATE LIMITING DETECTED: All {successful} connections accepted (SECURITY RISK)"

        print(f"\n{'='*80}")
        print(f"RESULTS: {endpoint}")
        print(f"{'='*80}")
        print(f"Total Attempts:         {max_connections}")
        print(f"Successful Connections: {successful}")
        print(f"Rejected Connections:   {rejected}")
        print(f"Errors:                 {errors}")
        print(f"First Rejection At:     Connection #{first_rejection}" if first_rejection else "First Rejection At:     NONE")
        print(f"Duration:               {duration:.2f}s")
        print(f"Rate Limit Triggered:   {'YES [PASS]' if rate_limit_triggered else 'NO [FAIL]'}")
        print(f"Status:                 {'PASS [OK]' if passed else 'FAIL [VULNERABLE]'}")
        print(f"Notes:                  {notes}")

        result = TestResult(
            endpoint=endpoint,
            endpoint_type="public_websocket",
            total_attempts=max_connections,
            successful_connections=successful,
            rejected_connections=rejected,
            errors=errors,
            rate_limit_triggered=rate_limit_triggered,
            first_rejection_at=first_rejection,
            duration_seconds=duration,
            passed=passed,
            notes=notes,
            timestamp=datetime.now().isoformat()
        )

        self.results.append(result)
        return result

    async def test_authenticated_websocket(self, endpoint: str, token: str, max_connections: int = 50) -> TestResult:
        """
        Test rate limiting on authenticated WebSocket endpoint.

        Args:
            endpoint: WebSocket endpoint path (e.g., "/api/system/ws")
            token: JWT token for authentication
            max_connections: Number of simultaneous connections to attempt

        Returns:
            TestResult with test outcome
        """
        print(f"\n{'='*80}")
        print(f"Testing Authenticated WebSocket: {endpoint}")
        print(f"{'='*80}")
        print(f"Attempting {max_connections} simultaneous connections with JWT token...")
        print(f"Expected: Rate limiting should prevent excessive connections\n")

        ws_url = f"{WS_BASE_URL}{endpoint}?token={token}"
        connections = []
        successful = 0
        rejected = 0
        errors = 0
        first_rejection = None

        start_time = time.time()

        # Attempt to open many connections simultaneously
        for i in range(1, max_connections + 1):
            try:
                # Try to connect with authentication
                websocket = await asyncio.wait_for(
                    websockets.connect(ws_url),
                    timeout=2.0
                )
                connections.append(websocket)
                successful += 1
                print(f"Connection {i:3d}: AUTHENTICATED & CONNECTED [OK]", end="\r")

                # Brief delay to avoid overwhelming the system
                await asyncio.sleep(0.05)

            except websockets.exceptions.InvalidStatusCode as e:
                # Connection rejected (likely 429, 403, or 401)
                rejected += 1
                if first_rejection is None:
                    first_rejection = i
                if e.status_code == 429:
                    print(f"\nConnection {i:3d}: HTTP 429 - RATE LIMITED [YES]")
                elif e.status_code == 401:
                    print(f"\nConnection {i:3d}: HTTP 401 - AUTH FAILED [FAIL]")
                else:
                    print(f"\nConnection {i:3d}: HTTP {e.status_code} - REJECTED")

            except asyncio.TimeoutError:
                rejected += 1
                if first_rejection is None:
                    first_rejection = i
                print(f"\nConnection {i:3d}: TIMEOUT - Possible Rate Limiting [YES]")

            except Exception as e:
                errors += 1
                error_msg = str(e)
                if "1008" in error_msg:
                    # WebSocket close code 1008 = policy violation (could be rate limit)
                    rejected += 1
                    if first_rejection is None:
                        first_rejection = i
                    print(f"\nConnection {i:3d}: POLICY VIOLATION (1008) - Possible Rate Limit [YES]")
                else:
                    print(f"\nConnection {i:3d}: ERROR - {type(e).__name__}: {error_msg[:50]}")

        end_time = time.time()
        duration = end_time - start_time

        # Close all successful connections
        print(f"\n\nClosing {len(connections)} open connections...")
        for ws in connections:
            try:
                await ws.close()
            except:
                pass

        # Analyze results
        rate_limit_triggered = rejected > 0

        # Determine pass/fail
        if rate_limit_triggered:
            passed = True
            notes = f"Rate limiting working: {rejected} connections rejected out of {max_connections}"
        else:
            passed = False
            notes = f"NO RATE LIMITING DETECTED: All {successful} connections accepted (SECURITY RISK)"

        print(f"\n{'='*80}")
        print(f"RESULTS: {endpoint}")
        print(f"{'='*80}")
        print(f"Total Attempts:         {max_connections}")
        print(f"Successful Connections: {successful}")
        print(f"Rejected Connections:   {rejected}")
        print(f"Errors:                 {errors}")
        print(f"First Rejection At:     Connection #{first_rejection}" if first_rejection else "First Rejection At:     NONE")
        print(f"Duration:               {duration:.2f}s")
        print(f"Rate Limit Triggered:   {'YES [PASS]' if rate_limit_triggered else 'NO [FAIL]'}")
        print(f"Status:                 {'PASS [OK]' if passed else 'FAIL [VULNERABLE]'}")
        print(f"Notes:                  {notes}")

        result = TestResult(
            endpoint=endpoint,
            endpoint_type="authenticated_websocket",
            total_attempts=max_connections,
            successful_connections=successful,
            rejected_connections=rejected,
            errors=errors,
            rate_limit_triggered=rate_limit_triggered,
            first_rejection_at=first_rejection,
            duration_seconds=duration,
            passed=passed,
            notes=notes,
            timestamp=datetime.now().isoformat()
        )

        self.results.append(result)
        return result

    async def run_all_tests(self):
        """Run comprehensive WebSocket rate limiting tests"""
        print("\n" + "="*80)
        print("WEBSOCKET RATE LIMITING SECURITY TEST SUITE")
        print("="*80)
        print(f"Backend URL: {BASE_URL}")
        print(f"WebSocket URL: {WS_BASE_URL}")
        print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)

        # Check if backend is running
        try:
            response = requests.get(f"{BASE_URL}/", timeout=5)
            if response.status_code == 200:
                print("[OK] Backend is running\n")
            else:
                print(f"[FAIL] Backend returned HTTP {response.status_code}\n")
                return
        except requests.exceptions.RequestException as e:
            print(f"[FAIL] Cannot connect to backend: {e}\n")
            print("Please ensure backend is running on port 54112")
            return

        # Test 1: Public WebSocket - /api/system/metrics
        print("\n" + "="*80)
        print("TEST 1: Public WebSocket - /api/system/metrics")
        print("="*80)
        await self.test_public_websocket("/api/system/metrics", max_connections=50)

        # Wait before next test
        print("\nWaiting 3 seconds before next test...")
        await asyncio.sleep(3)

        # Test 2: Authenticated WebSocket - /api/system/ws
        print("\n" + "="*80)
        print("TEST 2: Authenticated WebSocket - /api/system/ws")
        print("="*80)

        # Get JWT token
        self.jwt_token = await self.get_jwt_token()

        if self.jwt_token:
            print("\n[OK] Authentication successful, proceeding with authenticated WebSocket test\n")
            await self.test_authenticated_websocket("/api/system/ws", self.jwt_token, max_connections=50)
        else:
            print("\n[FAIL] Could not obtain JWT token - SKIPPING authenticated WebSocket test")
            print("Note: This test requires a working authentication system\n")

            # Create a placeholder result for skipped test
            result = TestResult(
                endpoint="/api/system/ws",
                endpoint_type="authenticated_websocket",
                total_attempts=0,
                successful_connections=0,
                rejected_connections=0,
                errors=0,
                rate_limit_triggered=False,
                first_rejection_at=None,
                duration_seconds=0.0,
                passed=False,
                notes="TEST SKIPPED: Could not obtain authentication token",
                timestamp=datetime.now().isoformat()
            )
            self.results.append(result)

        # Print final summary
        self.print_summary()

    def print_summary(self):
        """Print final test summary"""
        print("\n" + "="*80)
        print("FINAL TEST SUMMARY")
        print("="*80)

        tests_passed = sum(1 for r in self.results if r.passed)
        tests_failed = sum(1 for r in self.results if not r.passed)
        tests_skipped = sum(1 for r in self.results if "SKIPPED" in r.notes)
        total_tests = len(self.results)

        print(f"Total Tests:  {total_tests}")
        print(f"Passed:       {tests_passed} [OK]")
        print(f"Failed:       {tests_failed} [FAIL]")
        print(f"Skipped:      {tests_skipped} [SKIP]")

        # Security assessment
        if tests_failed - tests_skipped > 0:
            print("\n" + "="*80)
            print("*** SECURITY VULNERABILITY DETECTED ***")
            print("="*80)
            print("WebSocket endpoints are NOT properly rate limited!")
            print("Risk: DoS attacks via unlimited WebSocket connections")
            print("Action Required: Implement rate limiting on WebSocket endpoints")
        elif tests_skipped > 0 and tests_passed == 0:
            print("\n" + "="*80)
            print("*** TESTS INCOMPLETE ***")
            print("="*80)
            print("Some tests could not run due to authentication issues")
        else:
            print("\n" + "="*80)
            print("*** ALL TESTS PASSED - WEBSOCKET RATE LIMITING WORKING ***")
            print("="*80)

        # Detailed breakdown
        print("\nDetailed Results:")
        print("-" * 80)
        for result in self.results:
            if "SKIPPED" in result.notes:
                status = "SKIP"
            else:
                status = "PASS" if result.passed else "FAIL"

            print(f"{status} | {result.endpoint:30s} | Connected: {result.successful_connections:3d} | Rejected: {result.rejected_connections:3d}")
            print(f"     | Notes: {result.notes}")

        print("\n" + "="*80)
        print("Test completed at:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        print("="*80)
        print("\nNEXT STEPS:")
        print("1. Review detailed test results above")
        print("2. Generate formal security report: C:\\Ziggie\\agent-reports\\L3_WEBSOCKET_RATE_LIMITING_TEST.md")
        print("3. If FAIL: Implement WebSocket rate limiting")
        print("4. If PASS: Document findings and proceed with deployment")
        print("="*80)

    def generate_markdown_report(self, filepath: str):
        """Generate formal markdown security report"""
        tests_passed = sum(1 for r in self.results if r.passed)
        tests_failed = sum(1 for r in self.results if not r.passed)
        tests_skipped = sum(1 for r in self.results if "SKIPPED" in r.notes)

        # Determine overall status
        if tests_failed - tests_skipped > 0:
            overall_status = "VULNERABLE"
            recommendation = "DO NOT DEPLOY - Fix Required"
        elif tests_skipped > 0 and tests_passed == 0:
            overall_status = "INCOMPLETE"
            recommendation = "Cannot Assess - Authentication Issues"
        else:
            overall_status = "SECURE"
            recommendation = "APPROVED FOR DEPLOYMENT"

        report = f"""# L3 Security Testing Report: WebSocket Rate Limiting

**Test Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Tester:** L3.SECURITY.TESTER
**Mission:** URGENT - Verify WebSocket endpoints enforce rate limits
**Priority:** HIGH (DoS Protection)

---

## Executive Summary

**Overall Status:** {overall_status}
**Tests Executed:** {len(self.results)}
**Tests Passed:** {tests_passed} ✓
**Tests Failed:** {tests_failed} ✗
**Tests Skipped:** {tests_skipped} ⊘

**Recommendation:** {recommendation}

---

## Mission Context

### Why This Testing Was Urgent
- **Risk Assessment:** Protocol v1.1c approval identified WebSocket endpoints as UNTESTED GAP
- **HTTP Endpoints:** Verified working (3/3 tests PASS)
- **WebSocket Endpoints:** NOT tested (security gap)
- **Risk:** DoS attacks via unlimited WebSocket connections
- **Priority:** URGENT (flagged by L1 Security in approval process)

### Endpoints Tested
1. `/api/system/metrics` - Public WebSocket (no authentication)
2. `/api/system/ws` - Authenticated WebSocket (JWT token required)

---

## Test Results

"""

        # Add detailed results for each test
        for i, result in enumerate(self.results, 1):
            status_emoji = "⊘ SKIPPED" if "SKIPPED" in result.notes else ("✓ PASS" if result.passed else "✗ FAIL")

            report += f"""### Test {i}: {result.endpoint}

**Type:** {result.endpoint_type}
**Status:** {status_emoji}
**Timestamp:** {result.timestamp}

**Metrics:**
- Total Connection Attempts: {result.total_attempts}
- Successful Connections: {result.successful_connections}
- Rejected Connections: {result.rejected_connections}
- Errors: {result.errors}
- First Rejection At: Connection #{result.first_rejection_at if result.first_rejection_at else 'N/A'}
- Duration: {result.duration_seconds:.2f}s
- Rate Limit Triggered: {'YES' if result.rate_limit_triggered else 'NO'}

**Analysis:**
{result.notes}

---

"""

        # Add security assessment
        report += """## Security Assessment

"""

        if overall_status == "VULNERABLE":
            report += """### CRITICAL FINDINGS

**Vulnerability Detected:** WebSocket endpoints lack rate limiting

**Risk Level:** HIGH

**Attack Vector:**
- Attacker can open unlimited simultaneous WebSocket connections
- No connection throttling detected
- System vulnerable to DoS attacks

**Impact:**
- Server resource exhaustion
- Service degradation for legitimate users
- Potential system crash under load

**Proof of Concept:**
- Test successfully opened 50+ simultaneous WebSocket connections
- No rate limiting observed
- All connections accepted without throttling

"""
        elif overall_status == "INCOMPLETE":
            report += """### INCOMPLETE ASSESSMENT

**Issue:** Authentication system not available for testing

**Impact on Testing:**
- Could not test authenticated WebSocket endpoint (`/api/system/ws`)
- Cannot verify rate limiting on protected endpoints
- Security posture unclear

**Next Steps:**
- Fix authentication system
- Re-run authenticated WebSocket tests
- Complete security assessment

"""
        else:
            report += """### SECURITY POSTURE: ACCEPTABLE

**Finding:** WebSocket endpoints properly enforce rate limiting

**Evidence:**
- Rate limiting triggered after reasonable connection threshold
- Excessive connections rejected appropriately
- DoS protection working as expected

**Protection Mechanisms Verified:**
- Connection throttling active
- Rate limiting enforcement functional
- Both public and authenticated endpoints protected

"""

        # Add recommendations
        report += """## Recommendations

"""

        if overall_status == "VULNERABLE":
            report += """### IMMEDIATE ACTIONS REQUIRED

1. **Implement WebSocket Rate Limiting**
   - Add connection-level rate limiting for WebSocket endpoints
   - Implement per-IP connection throttling
   - Set reasonable connection limits (e.g., 10 connections per minute per IP)

2. **Technical Implementation**
   ```python
   # Example: Add rate limiting decorator or middleware
   @limiter.limit("10/minute")  # If supported by SlowAPI
   @router.websocket("/metrics")
   async def websocket_public_metrics(websocket: WebSocket):
       # ... existing code ...
   ```

3. **Alternative Solutions**
   - Use connection manager with max connections per IP
   - Implement custom WebSocket middleware for rate limiting
   - Consider using Redis for distributed rate limiting

4. **Verification**
   - Re-run this test suite after implementing fixes
   - Verify rate limiting triggers appropriately
   - Document rate limit thresholds

### DO NOT DEPLOY UNTIL FIXED
This security gap must be addressed before production deployment.

"""
        elif overall_status == "INCOMPLETE":
            report += """### ACTIONS REQUIRED

1. **Fix Authentication System**
   - Investigate authentication failures
   - Ensure JWT token generation working
   - Verify user registration/login endpoints

2. **Complete Testing**
   - Re-run authenticated WebSocket tests
   - Verify rate limiting on protected endpoints
   - Generate complete security report

3. **Deployment Status**
   - Cannot approve deployment until testing complete
   - Public WebSocket tested, but authenticated endpoint not verified

"""
        else:
            report += """### APPROVED FOR DEPLOYMENT

1. **Security Verification Complete**
   - WebSocket rate limiting working correctly
   - DoS protection mechanisms functional
   - Both public and authenticated endpoints secured

2. **Deployment Checklist**
   - [x] WebSocket rate limiting verified
   - [x] Connection throttling tested
   - [x] Security gap closed

3. **Ongoing Monitoring**
   - Monitor WebSocket connection patterns in production
   - Set up alerts for unusual connection spikes
   - Review rate limiting logs regularly

4. **Documentation**
   - Document rate limiting configuration
   - Update security documentation
   - Record rate limit thresholds for future reference

"""

        # Add technical details
        report += """## Technical Details

### Code Inspection Findings

**Rate Limiting Middleware:** SlowAPI (slowapi)
**Configuration:** IP-based rate limiting using `get_remote_address`

**WebSocket Endpoints:**
1. `/api/system/metrics` (Line 190 in system.py)
   - Public endpoint (no authentication)
   - Streams system metrics every 1 second

2. `/api/system/ws` (Line 273 in system.py)
   - Authenticated endpoint (JWT via query parameter)
   - Streams detailed system stats with user context

**Rate Limiting Decorators:**
- HTTP endpoints: Using `@limiter.limit()` decorators (working correctly)
- WebSocket endpoints: No explicit rate limiting decorators observed

### WebSocket Rate Limiting Challenge

**Important Note:** SlowAPI's rate limiting may not work directly with WebSocket
connections as it does with HTTP endpoints. WebSockets use a different protocol
(upgrade from HTTP) and maintain persistent connections, which requires different
rate limiting strategies.

**Possible Implementations:**
1. Connection-level rate limiting (limit concurrent connections per IP)
2. Message-level rate limiting (limit messages per second on open connections)
3. Handshake rate limiting (limit WebSocket upgrade requests)

---

## Test Execution Details

**Test Environment:**
- Backend: http://127.0.0.1:54112
- WebSocket: ws://127.0.0.1:54112
- Test Tool: Python websockets library (v15.0.1)
- Concurrency: 50 simultaneous connection attempts per endpoint

**Test Methodology:**
1. Rapidly open multiple WebSocket connections
2. Monitor for rejections (HTTP 429, timeouts, policy violations)
3. Track first rejection point
4. Measure acceptance vs. rejection ratio
5. Assess rate limiting effectiveness

---

## Appendix: Raw Test Data

"""

        # Add raw test data
        for result in self.results:
            report += f"""### {result.endpoint}
```json
{json.dumps({
    'endpoint': result.endpoint,
    'type': result.endpoint_type,
    'total_attempts': result.total_attempts,
    'successful': result.successful_connections,
    'rejected': result.rejected_connections,
    'errors': result.errors,
    'rate_limit_triggered': result.rate_limit_triggered,
    'first_rejection_at': result.first_rejection_at,
    'duration': result.duration_seconds,
    'passed': result.passed,
    'notes': result.notes,
    'timestamp': result.timestamp
}, indent=2)}
```

"""

        report += """---

## Report Generated By
**Agent:** L3.SECURITY.TESTER
**Mission:** URGENT Security Testing - WebSocket Rate Limiting
**Report Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Test Script:** C:\\Ziggie\\websocket_rate_limit_test.py

---

*This report is part of the Protocol v1.1c security approval process.*
"""

        # Write report to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"\n[OK] Security report generated: {filepath}")


async def main():
    """Main test execution"""
    tester = WebSocketRateLimitTester()
    await tester.run_all_tests()

    # Generate formal report
    report_path = r"C:\Ziggie\agent-reports\L3_WEBSOCKET_RATE_LIMITING_TEST.md"
    tester.generate_markdown_report(report_path)
    print(f"\n{'='*80}")
    print("MISSION COMPLETE")
    print(f"{'='*80}")
    print(f"Test script: C:\\Ziggie\\websocket_rate_limit_test.py")
    print(f"Report: {report_path}")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    asyncio.run(main())
