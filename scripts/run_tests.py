#!/usr/bin/env python
"""
Ziggie Unified Test Runner
==========================

Run all test suites across the Ziggie ecosystem.

Usage:
    python scripts/run_tests.py              # Run all tests
    python scripts/run_tests.py --backend    # Run backend tests only
    python scripts/run_tests.py --api        # Run API endpoint tests
    python scripts/run_tests.py --quick      # Quick smoke tests
    python scripts/run_tests.py --coverage   # Run with coverage report

Created: 2025-12-28
"""

import argparse
import subprocess
import sys
import os
from pathlib import Path
from datetime import datetime


# Test configuration
ZIGGIE_ROOT = Path("C:/Ziggie")
BACKEND_PATH = ZIGGIE_ROOT / "control-center" / "backend"
TESTS_PATH = BACKEND_PATH / "tests"
REPORT_DIR = ZIGGIE_ROOT / "testing" / "reports"


def print_header(title: str):
    """Print a formatted header."""
    width = 70
    print("=" * width)
    print(f" {title}".center(width))
    print("=" * width)


def print_section(title: str):
    """Print a section header."""
    print(f"\n--- {title} ---\n")


def check_backend_running() -> bool:
    """Check if backend is running on port 54112."""
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', 54112))
    sock.close()
    return result == 0


def run_pytest(path: Path, extra_args: list = None, coverage: bool = False) -> int:
    """Run pytest on a given path."""
    cmd = [sys.executable, "-m", "pytest", str(path), "-v"]

    if coverage:
        cmd.extend(["--cov=.", "--cov-report=html", "--cov-report=term"])

    if extra_args:
        cmd.extend(extra_args)

    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=str(BACKEND_PATH))
    return result.returncode


def run_backend_tests(coverage: bool = False) -> int:
    """Run all backend tests."""
    print_section("Backend Unit Tests")
    return run_pytest(TESTS_PATH, coverage=coverage)


def run_api_tests() -> int:
    """Run API endpoint tests."""
    print_section("API Endpoint Tests")

    # Check backend is running
    if not check_backend_running():
        print("ERROR: Backend not running on port 54112")
        print("Start the backend first: python control-center/backend/main.py")
        return 1

    # Run API test files
    api_tests = [
        ZIGGIE_ROOT / "test_backend_endpoints.py",
        ZIGGIE_ROOT / "comprehensive_backend_test.py",
    ]

    total_result = 0
    for test_file in api_tests:
        if test_file.exists():
            print(f"\nRunning {test_file.name}...")
            result = subprocess.run(
                [sys.executable, str(test_file)],
                cwd=str(ZIGGIE_ROOT)
            )
            if result.returncode != 0:
                total_result = 1

    return total_result


def run_quick_tests() -> int:
    """Run quick smoke tests."""
    print_section("Quick Smoke Tests")

    smoke_tests = [
        TESTS_PATH / "test_system_api.py",
        TESTS_PATH / "test_services_api.py",
    ]

    for test_file in smoke_tests:
        if test_file.exists():
            result = run_pytest(test_file, extra_args=["-x"])  # Stop on first failure
            if result != 0:
                return result

    return 0


def run_qa_suite() -> int:
    """Run comprehensive QA suite."""
    print_section("Comprehensive QA Suite")

    qa_script = ZIGGIE_ROOT / "l2_qa_comprehensive_test.py"
    if qa_script.exists():
        result = subprocess.run(
            [sys.executable, str(qa_script)],
            cwd=str(ZIGGIE_ROOT)
        )
        return result.returncode
    else:
        print(f"QA script not found: {qa_script}")
        return 1


def generate_report(results: dict) -> None:
    """Generate test run report."""
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = REPORT_DIR / f"test_run_{timestamp}.txt"

    with open(report_file, "w") as f:
        f.write("Ziggie Test Run Report\n")
        f.write("=" * 50 + "\n")
        f.write(f"Timestamp: {datetime.now().isoformat()}\n\n")

        for suite, result in results.items():
            status = "PASSED" if result == 0 else "FAILED"
            f.write(f"{suite}: {status}\n")

        f.write("\n")
        all_passed = all(r == 0 for r in results.values())
        f.write(f"Overall: {'ALL TESTS PASSED' if all_passed else 'SOME TESTS FAILED'}\n")

    print(f"\nReport saved to: {report_file}")


def main():
    parser = argparse.ArgumentParser(description="Ziggie Unified Test Runner")
    parser.add_argument("--backend", action="store_true", help="Run backend tests only")
    parser.add_argument("--api", action="store_true", help="Run API endpoint tests")
    parser.add_argument("--quick", action="store_true", help="Run quick smoke tests")
    parser.add_argument("--qa", action="store_true", help="Run comprehensive QA suite")
    parser.add_argument("--coverage", action="store_true", help="Run with coverage report")
    parser.add_argument("--all", action="store_true", help="Run all tests")

    args = parser.parse_args()

    # If no specific option, run all
    run_all = args.all or not any([args.backend, args.api, args.quick, args.qa])

    print_header("ZIGGIE TEST RUNNER")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    results = {}

    if args.quick:
        results["Quick Tests"] = run_quick_tests()
    elif run_all or args.backend:
        results["Backend Tests"] = run_backend_tests(coverage=args.coverage)

    if run_all or args.api:
        results["API Tests"] = run_api_tests()

    if run_all or args.qa:
        results["QA Suite"] = run_qa_suite()

    # Print summary
    print_header("TEST SUMMARY")

    all_passed = True
    for suite, result in results.items():
        status = "PASSED" if result == 0 else "FAILED"
        marker = "[OK]" if result == 0 else "[FAIL]"
        print(f"  {marker} {suite}: {status}")
        if result != 0:
            all_passed = False

    generate_report(results)

    if all_passed:
        print("\n" + "=" * 70)
        print("  ALL TESTS PASSED!".center(70))
        print("=" * 70)
        return 0
    else:
        print("\n" + "=" * 70)
        print("  SOME TESTS FAILED - Review output above".center(70))
        print("=" * 70)
        return 1


if __name__ == "__main__":
    sys.exit(main())
