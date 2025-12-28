"""
Rate Limiting Verification Test Script
Tests that rate limiting is properly enforced after SlowAPI middleware fix

L3.SECURITY.TESTER
"""

import requests
import time
from datetime import datetime
from typing import Dict, List

BASE_URL = "http://127.0.0.1:54112"

class RateLimitTester:
    """Test rate limiting on various endpoints"""

    def __init__(self):
        self.results = {
            "tests_passed": 0,
            "tests_failed": 0,
            "test_details": []
        }

    def test_endpoint(self, endpoint: str, limit: int, test_requests: int = 70) -> Dict:
        """
        Test rate limiting on a single endpoint

        Args:
            endpoint: API endpoint to test
            limit: Expected rate limit (requests per minute)
            test_requests: Number of requests to send

        Returns:
            Test results dictionary
        """
        print(f"\n{'='*80}")
        print(f"Testing: {endpoint}")
        print(f"Expected Limit: {limit}/minute")
        print(f"Sending {test_requests} requests...")
        print(f"{'='*80}\n")

        responses_200 = []
        responses_429 = []
        errors = []

        start_time = time.time()

        for i in range(1, test_requests + 1):
            try:
                response = requests.get(f"{BASE_URL}{endpoint}", timeout=5)

                if response.status_code == 200:
                    responses_200.append(i)
                    print(f"Request {i:3d}: HTTP 200 ✓", end="\r")
                elif response.status_code == 429:
                    responses_429.append(i)
                    print(f"\nRequest {i:3d}: HTTP 429 - RATE LIMITED ✓")

                    # Check for rate limit headers
                    headers = response.headers
                    if 'Retry-After' in headers:
                        print(f"             Retry-After: {headers['Retry-After']}s")
                else:
                    errors.append((i, response.status_code))
                    print(f"\nRequest {i:3d}: HTTP {response.status_code} - UNEXPECTED")

            except requests.exceptions.RequestException as e:
                errors.append((i, str(e)))
                print(f"\nRequest {i:3d}: ERROR - {str(e)}")

        end_time = time.time()
        duration = end_time - start_time

        # Analyze results
        total_200 = len(responses_200)
        total_429 = len(responses_429)
        total_errors = len(errors)
        first_429 = responses_429[0] if responses_429 else None

        print(f"\n{'='*80}")
        print(f"RESULTS FOR {endpoint}")
        print(f"{'='*80}")
        print(f"Total Requests:    {test_requests}")
        print(f"HTTP 200:          {total_200}")
        print(f"HTTP 429:          {total_429}")
        print(f"Errors:            {total_errors}")
        print(f"First 429 at:      Request #{first_429}" if first_429 else "First 429 at:      NONE")
        print(f"Duration:          {duration:.2f}s")
        print(f"Avg Request Time:  {(duration/test_requests)*1000:.1f}ms")

        # Determine pass/fail
        # We expect roughly 'limit' successful requests before rate limiting kicks in
        # Allow 10% margin due to timing variations
        expected_min = int(limit * 0.9)
        expected_max = int(limit * 1.1)

        passed = (
            total_429 > 0 and  # At least some requests were rate limited
            expected_min <= total_200 <= expected_max and  # Approximately correct number of allowed requests
            total_errors == 0  # No errors occurred
        )

        if passed:
            print(f"\n✓ TEST PASSED")
            self.results["tests_passed"] += 1
        else:
            print(f"\n✗ TEST FAILED")
            if total_429 == 0:
                print(f"  - No HTTP 429 responses (rate limiting not working)")
            if not (expected_min <= total_200 <= expected_max):
                print(f"  - HTTP 200 count outside expected range ({expected_min}-{expected_max})")
            if total_errors > 0:
                print(f"  - {total_errors} errors occurred")
            self.results["tests_failed"] += 1

        result = {
            "endpoint": endpoint,
            "expected_limit": limit,
            "total_requests": test_requests,
            "http_200_count": total_200,
            "http_429_count": total_429,
            "error_count": total_errors,
            "first_429_at": first_429,
            "duration_seconds": duration,
            "passed": passed,
            "timestamp": datetime.now().isoformat()
        }

        self.results["test_details"].append(result)

        return result

    def run_all_tests(self):
        """Run comprehensive rate limit tests"""
        print("\n" + "="*80)
        print("RATE LIMITING VERIFICATION TEST SUITE")
        print("="*80)
        print(f"Backend URL: {BASE_URL}")
        print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)

        # Check if backend is running
        try:
            response = requests.get(f"{BASE_URL}/", timeout=5)
            if response.status_code == 200:
                print("✓ Backend is running\n")
            else:
                print(f"✗ Backend returned HTTP {response.status_code}\n")
                return
        except requests.exceptions.RequestException as e:
            print(f"✗ Cannot connect to backend: {e}\n")
            print("Please ensure backend is running on port 54112")
            return

        # Test 1: System Stats (60/minute limit)
        print("\n" + "="*80)
        print("TEST 1: /api/system/stats (60/minute limit)")
        print("="*80)
        self.test_endpoint("/api/system/stats", limit=60, test_requests=70)

        # Wait a moment before next test to avoid cross-test interference
        print("\nWaiting 2 seconds before next test...")
        time.sleep(2)

        # Test 2: System Ports (30/minute limit)
        print("\n" + "="*80)
        print("TEST 2: /api/system/ports (30/minute limit)")
        print("="*80)
        self.test_endpoint("/api/system/ports", limit=30, test_requests=40)

        # Wait before next test
        print("\nWaiting 2 seconds before next test...")
        time.sleep(2)

        # Test 3: Services List (60/minute limit)
        print("\n" + "="*80)
        print("TEST 3: /api/services (60/minute limit)")
        print("="*80)
        self.test_endpoint("/api/services", limit=60, test_requests=70)

        # Print final summary
        self.print_summary()

    def print_summary(self):
        """Print final test summary"""
        print("\n" + "="*80)
        print("FINAL TEST SUMMARY")
        print("="*80)

        total_tests = self.results["tests_passed"] + self.results["tests_failed"]

        print(f"Total Tests:  {total_tests}")
        print(f"Passed:       {self.results['tests_passed']} ✓")
        print(f"Failed:       {self.results['tests_failed']} ✗")

        if self.results["tests_failed"] == 0:
            print("\n" + "="*80)
            print("✓✓✓ ALL TESTS PASSED - RATE LIMITING IS WORKING ✓✓✓")
            print("="*80)
        else:
            print("\n" + "="*80)
            print("✗✗✗ SOME TESTS FAILED - RATE LIMITING HAS ISSUES ✗✗✗")
            print("="*80)

        # Detailed breakdown
        print("\nDetailed Results:")
        print("-" * 80)
        for test in self.results["test_details"]:
            status = "PASS ✓" if test["passed"] else "FAIL ✗"
            print(f"{status} | {test['endpoint']:30s} | 200: {test['http_200_count']:3d} | 429: {test['http_429_count']:3d} | Limit: {test['expected_limit']}/min")

        print("\n" + "="*80)
        print("Test completed at:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        print("="*80)


if __name__ == "__main__":
    tester = RateLimitTester()
    tester.run_all_tests()
