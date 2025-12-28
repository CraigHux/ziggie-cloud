#!/usr/bin/env python3
"""
L2 QA COMPREHENSIVE TESTING SUITE
Ziggie Control Center - Post-Deployment Validation
"""

import requests
import json
import time
import sys
from datetime import datetime
from typing import Dict, List, Tuple
from collections import defaultdict

BASE_URL = "http://127.0.0.1:54112"
TIMEOUT = 10

class Colors:
    """ANSI color codes"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

class TestResult:
    """Store test result data"""
    def __init__(self):
        self.total_tests = 0
        self.passed = 0
        self.failed = 0
        self.warnings = 0
        self.errors: List[Dict] = []
        self.performance: Dict[str, List[float]] = defaultdict(list)
        self.start_time = time.time()

    def record_test(self, name: str, passed: bool, duration: float, error: str = None, warning: str = None):
        """Record a test result"""
        self.total_tests += 1
        if passed:
            self.passed += 1
            print(f"{Colors.GREEN}[PASS]{Colors.END} {name} ({duration:.3f}s)")
        else:
            self.failed += 1
            print(f"{Colors.RED}[FAIL]{Colors.END} {name} ({duration:.3f}s)")
            if error:
                print(f"  {Colors.RED}Error: {error}{Colors.END}")
                self.errors.append({"test": name, "error": error})

        if warning:
            self.warnings += 1
            print(f"  {Colors.YELLOW}[WARN] {warning}{Colors.END}")

        self.performance[name].append(duration)

    def get_summary(self) -> Dict:
        """Get test summary"""
        total_time = time.time() - self.start_time
        return {
            "total_tests": self.total_tests,
            "passed": self.passed,
            "failed": self.failed,
            "warnings": self.warnings,
            "success_rate": f"{(self.passed/self.total_tests*100):.1f}%" if self.total_tests > 0 else "0%",
            "total_time": f"{total_time:.2f}s",
            "errors": self.errors
        }

def make_request(method: str, endpoint: str, **kwargs) -> Tuple[bool, Dict, float, str]:
    """Make HTTP request and measure time"""
    url = f"{BASE_URL}{endpoint}"
    start = time.time()
    error = None

    try:
        if method == "GET":
            response = requests.get(url, timeout=TIMEOUT, **kwargs)
        elif method == "POST":
            response = requests.post(url, timeout=TIMEOUT, **kwargs)
        else:
            return False, {}, 0, f"Unsupported method: {method}"

        duration = time.time() - start

        try:
            data = response.json()
        except:
            data = {"raw": response.text}

        success = response.status_code in [200, 201]
        if not success:
            error = f"HTTP {response.status_code}"

        return success, data, duration, error

    except requests.exceptions.Timeout:
        duration = time.time() - start
        return False, {}, duration, "Request timeout"
    except requests.exceptions.ConnectionError:
        duration = time.time() - start
        return False, {}, duration, "Connection refused"
    except Exception as e:
        duration = time.time() - start
        return False, {}, duration, str(e)

def test_health_endpoints(result: TestResult):
    """Test health check endpoints"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}=== Testing Health Endpoints ==={Colors.END}")

    # Test root endpoint
    success, data, duration, error = make_request("GET", "/")
    result.record_test(
        "GET /",
        success and data.get("status") == "running",
        duration,
        error
    )

    # Test health endpoint
    success, data, duration, error = make_request("GET", "/health")
    result.record_test(
        "GET /health",
        success and data.get("status") == "healthy",
        duration,
        error
    )

def test_system_endpoints(result: TestResult):
    """Test system monitoring endpoints"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}=== Testing System Endpoints ==={Colors.END}")

    # Test system stats
    success, data, duration, error = make_request("GET", "/api/system/stats")
    warning = None
    if duration > 0.5:
        warning = f"Slow response: {duration:.3f}s > 500ms threshold"
    result.record_test(
        "GET /api/system/stats",
        success and data.get("success") == True,
        duration,
        error,
        warning
    )

    # Test system info
    success, data, duration, error = make_request("GET", "/api/system/info")
    result.record_test(
        "GET /api/system/info",
        success and data.get("success") == True,
        duration,
        error
    )

    # Test system processes
    success, data, duration, error = make_request("GET", "/api/system/processes")
    result.record_test(
        "GET /api/system/processes",
        success and data.get("success") == True,
        duration,
        error
    )

    # Test system ports
    success, data, duration, error = make_request("GET", "/api/system/ports")
    result.record_test(
        "GET /api/system/ports",
        success and data.get("success") == True,
        duration,
        error
    )

def test_knowledge_endpoints(result: TestResult):
    """Test knowledge base endpoints"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}=== Testing Knowledge Base Endpoints ==={Colors.END}")

    # Test recent files
    success, data, duration, error = make_request("GET", "/api/knowledge/recent")
    result.record_test(
        "GET /api/knowledge/recent",
        success and data.get("success") == True,
        duration,
        error
    )

    # Test recent files with limit
    success, data, duration, error = make_request("GET", "/api/knowledge/recent?limit=5")
    result.record_test(
        "GET /api/knowledge/recent?limit=5",
        success and data.get("count") <= 5,
        duration,
        error
    )

    # Test KB stats
    success, data, duration, error = make_request("GET", "/api/knowledge/stats")
    result.record_test(
        "GET /api/knowledge/stats",
        success and "total_files" in data,
        duration,
        error
    )

    # Test KB files with pagination
    success, data, duration, error = make_request("GET", "/api/knowledge/files?page=1&page_size=10")
    result.record_test(
        "GET /api/knowledge/files",
        success and "files" in data,
        duration,
        error
    )

def test_agents_endpoints(result: TestResult):
    """Test agent system endpoints"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}=== Testing Agent Endpoints ==={Colors.END}")

    # Test agents list
    success, data, duration, error = make_request("GET", "/api/agents")
    result.record_test(
        "GET /api/agents",
        success,
        duration,
        error
    )

    # Test agents with pagination
    success, data, duration, error = make_request("GET", "/api/agents?page=1&page_size=5")
    result.record_test(
        "GET /api/agents?page=1&page_size=5",
        success,
        duration,
        error
    )

    # Test agents stats
    success, data, duration, error = make_request("GET", "/api/agents/stats")
    result.record_test(
        "GET /api/agents/stats",
        success,
        duration,
        error
    )

def test_services_endpoints(result: TestResult):
    """Test service management endpoints"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}=== Testing Service Endpoints ==={Colors.END}")

    # Test services list
    success, data, duration, error = make_request("GET", "/api/services")
    result.record_test(
        "GET /api/services",
        success and data.get("success") == True,
        duration,
        error
    )

    # Test services with pagination
    success, data, duration, error = make_request("GET", "/api/services?page=1&page_size=10")
    result.record_test(
        "GET /api/services?page=1&page_size=10",
        success,
        duration,
        error
    )

def test_rate_limiting(result: TestResult):
    """Test rate limiting functionality"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}=== Testing Rate Limiting ==={Colors.END}")

    # Send multiple rapid requests
    endpoint = "/api/system/stats"
    requests_sent = 0
    rate_limited = False

    for i in range(70):  # Try to exceed 60/minute limit
        success, data, duration, error = make_request("GET", endpoint)
        requests_sent += 1

        if not success and error and "429" in str(error):
            rate_limited = True
            break

        time.sleep(0.01)  # Small delay

    result.record_test(
        "Rate limiting (60/minute)",
        rate_limited,
        0,
        None if rate_limited else "Rate limiting may not be working - sent 70 requests without being rate limited"
    )

def test_error_handling(result: TestResult):
    """Test error handling for invalid requests"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}=== Testing Error Handling ==={Colors.END}")

    # Test invalid endpoint
    success, data, duration, error = make_request("GET", "/api/invalid/endpoint")
    result.record_test(
        "404 Error Handling",
        not success and "404" in str(error),
        duration
    )

    # Test invalid query parameters
    success, data, duration, error = make_request("GET", "/api/knowledge/recent?limit=999999")
    result.record_test(
        "Invalid Query Parameter Handling",
        not success or data.get("count", 0) <= 100,  # Should enforce max limit
        duration
    )

def test_performance_benchmarks(result: TestResult):
    """Test performance benchmarks"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}=== Performance Benchmarks ==={Colors.END}")

    critical_endpoints = [
        "/health",
        "/api/system/stats",
        "/api/system/info",
    ]

    for endpoint in critical_endpoints:
        times = []
        for _ in range(5):
            success, data, duration, error = make_request("GET", endpoint)
            if success:
                times.append(duration)
            time.sleep(0.1)

        if times:
            avg_time = sum(times) / len(times)
            p95_time = sorted(times)[int(len(times) * 0.95)]

            warning = None
            if p95_time > 0.5:
                warning = f"P95 response time {p95_time:.3f}s exceeds 500ms threshold"

            result.record_test(
                f"Performance: {endpoint}",
                True,
                avg_time,
                None,
                warning
            )

            print(f"  Avg: {avg_time:.3f}s, P95: {p95_time:.3f}s, Min: {min(times):.3f}s, Max: {max(times):.3f}s")

def print_summary(result: TestResult):
    """Print test summary"""
    summary = result.get_summary()

    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}TEST EXECUTION SUMMARY{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}")

    print(f"\nTotal Tests Run: {Colors.BOLD}{summary['total_tests']}{Colors.END}")
    print(f"Passed: {Colors.GREEN}{summary['passed']}{Colors.END}")
    print(f"Failed: {Colors.RED}{summary['failed']}{Colors.END}")
    print(f"Warnings: {Colors.YELLOW}{summary['warnings']}{Colors.END}")
    print(f"Success Rate: {Colors.BOLD}{summary['success_rate']}{Colors.END}")
    print(f"Total Time: {summary['total_time']}")

    if summary['errors']:
        print(f"\n{Colors.RED}{Colors.BOLD}DEFECTS FOUND:{Colors.END}")
        for i, error in enumerate(summary['errors'], 1):
            print(f"{i}. {error['test']}: {error['error']}")

    # Quality gate assessment
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}QUALITY GATE ASSESSMENT{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}")

    passed_gates = []
    failed_gates = []

    # Gate 1: All critical endpoints return 200
    if summary['failed'] == 0:
        passed_gates.append("All critical endpoints return 200")
    else:
        failed_gates.append(f"Critical endpoints failing ({summary['failed']} failures)")

    # Gate 2: Response times < 500ms (p95)
    slow_endpoints = [name for name, times in result.performance.items()
                      if times and max(times) > 0.5]
    if not slow_endpoints:
        passed_gates.append("Response times < 500ms (p95)")
    else:
        failed_gates.append(f"Performance degradation detected in {len(slow_endpoints)} endpoints")

    # Gate 3: Rate limiting works
    rate_limit_test = any("Rate limiting" in err['test'] for err in summary['errors'])
    if not rate_limit_test:
        passed_gates.append("Rate limiting functional")
    else:
        failed_gates.append("Rate limiting not working correctly")

    print(f"\n{Colors.GREEN}[+] PASSED GATES:{Colors.END}")
    for gate in passed_gates:
        print(f"  - {gate}")

    if failed_gates:
        print(f"\n{Colors.RED}[-] FAILED GATES:{Colors.END}")
        for gate in failed_gates:
            print(f"  - {gate}")

    # Final recommendation
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}SIGN-OFF RECOMMENDATION{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}\n")

    if summary['failed'] == 0 and not failed_gates:
        print(f"{Colors.GREEN}{Colors.BOLD}[APPROVED] READY FOR PRODUCTION{Colors.END}")
        print("All quality gates passed. System is stable and performant.")
    elif summary['failed'] <= 2 and len(failed_gates) <= 1:
        print(f"{Colors.YELLOW}{Colors.BOLD}[CONDITIONAL] CONDITIONAL PASS{Colors.END}")
        print("Minor issues detected. Review recommended but not blocking.")
    else:
        print(f"{Colors.RED}{Colors.BOLD}[REJECTED] NOT READY - FIXES REQUIRED{Colors.END}")
        print("Critical issues detected. Fixes required before production deployment.")

    # Save results to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"c:/Ziggie/qa_report_{timestamp}.json"

    with open(report_file, 'w') as f:
        json.dump({
            "summary": summary,
            "performance": {k: {"avg": sum(v)/len(v), "max": max(v), "min": min(v)}
                           for k, v in result.performance.items() if v},
            "passed_gates": passed_gates,
            "failed_gates": failed_gates,
            "timestamp": datetime.now().isoformat()
        }, f, indent=2)

    print(f"\nDetailed report saved to: {report_file}")

def main():
    """Run all tests"""
    print(f"{Colors.BOLD}{Colors.BLUE}")
    print("="*60)
    print("     L2 QA COMPREHENSIVE TESTING SUITE")
    print("     Ziggie Control Center - Post-Deployment")
    print("="*60)
    print(f"{Colors.END}\n")

    print(f"Testing server at: {BASE_URL}")
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    result = TestResult()

    try:
        # Run all test suites
        test_health_endpoints(result)
        test_system_endpoints(result)
        test_knowledge_endpoints(result)
        test_agents_endpoints(result)
        test_services_endpoints(result)
        test_rate_limiting(result)
        test_error_handling(result)
        test_performance_benchmarks(result)

        # Print summary
        print_summary(result)

        # Exit with appropriate code
        sys.exit(0 if result.failed == 0 else 1)

    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Testing interrupted by user{Colors.END}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}Fatal error: {e}{Colors.END}")
        sys.exit(1)

if __name__ == "__main__":
    main()
