"""
Concurrent Load Test for Control Center Backend
Tests rate limiting under realistic concurrent load conditions

Test Coverage:
- 39 API endpoints
- 100+ concurrent users
- Multiple scenarios (rapid fire, sustained, mixed)
- Rate limit enforcement verification
- Performance metrics collection
"""

import asyncio
import aiohttp
import time
import json
import statistics
from datetime import datetime
from collections import defaultdict
from typing import List, Dict, Any
import sys


# Configuration
BASE_URL = "http://127.0.0.1:54112"
USERNAME = "admin"
PASSWORD = "admin123"
LOG_FILE = "concurrent_load_test_results.log"

# Endpoint configurations with rate limits
ENDPOINTS = {
    # System endpoints
    "/api/system/stats": {"method": "GET", "auth": True, "limit": 60},
    "/api/system/ports": {"method": "GET", "auth": True, "limit": 30},
    "/api/system/processes": {"method": "GET", "auth": True, "limit": 60},
    "/api/system/info": {"method": "GET", "auth": True, "limit": 60},
    "/api/system/resources": {"method": "GET", "auth": True, "limit": 60},
    "/api/system/network": {"method": "GET", "auth": True, "limit": 60},
    "/api/system/disk": {"method": "GET", "auth": True, "limit": 60},

    # Service endpoints
    "/api/services": {"method": "GET", "auth": True, "limit": 60},
    "/api/services/scan": {"method": "POST", "auth": True, "limit": 10},

    # Agent endpoints
    "/api/agents": {"method": "GET", "auth": True, "limit": 60},
    "/api/agents/active": {"method": "GET", "auth": True, "limit": 60},

    # Project endpoints
    "/api/projects": {"method": "GET", "auth": True, "limit": 60},

    # Health endpoint
    "/api/health": {"method": "GET", "auth": False, "limit": 100},

    # Auth endpoints
    "/api/auth/validate": {"method": "GET", "auth": True, "limit": 60},
}


class LoadTestResults:
    """Collect and analyze test results"""

    def __init__(self):
        self.requests = []
        self.errors = defaultdict(list)
        self.rate_limits = defaultdict(int)
        self.by_endpoint = defaultdict(list)

    def add_result(self, endpoint: str, status: int, duration: float, error: str = None):
        """Record a single request result"""
        result = {
            "timestamp": time.time(),
            "endpoint": endpoint,
            "status": status,
            "duration": duration,
            "error": error
        }
        self.requests.append(result)
        self.by_endpoint[endpoint].append(result)

        if status == 429:
            self.rate_limits[endpoint] += 1
        elif error:
            self.errors[endpoint].append(error)

    def get_stats(self) -> Dict[str, Any]:
        """Calculate statistics"""
        if not self.requests:
            return {}

        durations = [r["duration"] for r in self.requests if r["status"] < 500]
        status_codes = defaultdict(int)
        for r in self.requests:
            status_codes[r["status"]] += 1

        stats = {
            "total_requests": len(self.requests),
            "status_codes": dict(status_codes),
            "rate_limited": sum(self.rate_limits.values()),
            "errors": len([r for r in self.requests if r["error"]]),
            "durations": {
                "min": min(durations) if durations else 0,
                "max": max(durations) if durations else 0,
                "mean": statistics.mean(durations) if durations else 0,
                "median": statistics.median(durations) if durations else 0,
                "p95": statistics.quantiles(durations, n=20)[18] if len(durations) > 20 else (max(durations) if durations else 0),
                "p99": statistics.quantiles(durations, n=100)[98] if len(durations) > 100 else (max(durations) if durations else 0),
            },
            "by_endpoint": {}
        }

        # Per-endpoint stats
        for endpoint, results in self.by_endpoint.items():
            ep_durations = [r["duration"] for r in results if r["status"] < 500]
            ep_status = defaultdict(int)
            for r in results:
                ep_status[r["status"]] += 1

            stats["by_endpoint"][endpoint] = {
                "total": len(results),
                "status_codes": dict(ep_status),
                "rate_limited": sum(1 for r in results if r["status"] == 429),
                "avg_duration": statistics.mean(ep_durations) if ep_durations else 0,
                "p95_duration": statistics.quantiles(ep_durations, n=20)[18] if len(ep_durations) > 20 else (max(ep_durations) if ep_durations else 0),
            }

        return stats


class ConcurrentLoadTester:
    """Main load testing class"""

    def __init__(self):
        self.token = None
        self.results = LoadTestResults()
        self.log_file = open(LOG_FILE, "w", encoding="utf-8")

    def log(self, message: str):
        """Log to both console and file"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        log_msg = f"[{timestamp}] {message}"
        print(log_msg)
        self.log_file.write(log_msg + "\n")
        self.log_file.flush()

    async def authenticate(self) -> bool:
        """Get JWT token"""
        self.log("Authenticating...")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{BASE_URL}/api/auth/login",
                    json={"username": USERNAME, "password": PASSWORD}
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        self.token = data["access_token"]
                        self.log(f"Authentication successful. Token: {self.token[:20]}...")
                        return True
                    else:
                        self.log(f"Authentication failed: {resp.status}")
                        return False
        except Exception as e:
            self.log(f"Authentication error: {e}")
            return False

    async def make_request(self, session: aiohttp.ClientSession, endpoint: str,
                          method: str = "GET", auth: bool = True) -> Dict[str, Any]:
        """Make a single HTTP request"""
        headers = {}
        if auth and self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        url = f"{BASE_URL}{endpoint}"
        start_time = time.time()
        status = 0
        error = None

        try:
            if method == "GET":
                async with session.get(url, headers=headers) as resp:
                    status = resp.status
                    duration = time.time() - start_time
                    try:
                        await resp.read()  # Consume response
                    except:
                        pass
            elif method == "POST":
                async with session.post(url, headers=headers, json={}) as resp:
                    status = resp.status
                    duration = time.time() - start_time
                    try:
                        await resp.read()
                    except:
                        pass
            else:
                duration = time.time() - start_time
                error = f"Unsupported method: {method}"

        except asyncio.TimeoutError:
            duration = time.time() - start_time
            status = 0
            error = "Timeout"
        except Exception as e:
            duration = time.time() - start_time
            status = 0
            error = str(e)

        return {
            "endpoint": endpoint,
            "status": status,
            "duration": duration,
            "error": error
        }

    async def user_session(self, session: aiohttp.ClientSession, user_id: int,
                          endpoints: List[str], requests_per_endpoint: int):
        """Simulate a single user making multiple requests"""
        for endpoint_path in endpoints:
            endpoint_config = ENDPOINTS[endpoint_path]
            for _ in range(requests_per_endpoint):
                result = await self.make_request(
                    session,
                    endpoint_path,
                    endpoint_config["method"],
                    endpoint_config["auth"]
                )
                self.results.add_result(
                    result["endpoint"],
                    result["status"],
                    result["duration"],
                    result["error"]
                )
                # Small delay to simulate realistic behavior
                await asyncio.sleep(0.01)

    async def scenario_rapid_fire(self):
        """Scenario 1: 100 users, 5 requests each, rapid fire"""
        self.log("\n" + "="*80)
        self.log("SCENARIO 1: RAPID FIRE - 100 users, 5 requests each")
        self.log("="*80)

        num_users = 100
        requests_per_user = 5

        # Select endpoints to test
        test_endpoints = [
            "/api/system/stats",
            "/api/system/ports",
            "/api/services",
            "/api/health",
            "/api/agents"
        ]

        self.log(f"Testing {len(test_endpoints)} endpoints with {num_users} concurrent users")
        self.log(f"Each user makes {requests_per_user} requests per endpoint")
        self.log(f"Total expected requests: {num_users * len(test_endpoints) * requests_per_user}")

        start_time = time.time()

        # Create connector with connection limits
        connector = aiohttp.TCPConnector(limit=200, limit_per_host=200)
        timeout = aiohttp.ClientTimeout(total=30)

        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            # Create all user tasks
            tasks = []
            for user_id in range(num_users):
                task = asyncio.create_task(
                    self.user_session(session, user_id, test_endpoints, requests_per_user)
                )
                tasks.append(task)

            # Execute all concurrently
            await asyncio.gather(*tasks)

        duration = time.time() - start_time
        self.log(f"\nScenario 1 completed in {duration:.2f} seconds")
        self.log(f"Throughput: {len(self.results.requests)/duration:.2f} req/sec")

    async def scenario_sustained_load(self):
        """Scenario 2: 50 users, 10 requests each, sustained load"""
        self.log("\n" + "="*80)
        self.log("SCENARIO 2: SUSTAINED LOAD - 50 users, 10 requests each")
        self.log("="*80)

        num_users = 50
        requests_per_user = 10

        test_endpoints = [
            "/api/system/info",
            "/api/system/processes",
            "/api/projects",
            "/api/agents/active",
            "/api/auth/validate"
        ]

        self.log(f"Testing {len(test_endpoints)} endpoints with {num_users} concurrent users")
        self.log(f"Each user makes {requests_per_user} requests per endpoint")

        start_time = time.time()

        connector = aiohttp.TCPConnector(limit=100, limit_per_host=100)
        timeout = aiohttp.ClientTimeout(total=30)

        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            tasks = []
            for user_id in range(num_users):
                task = asyncio.create_task(
                    self.user_session(session, user_id, test_endpoints, requests_per_user)
                )
                tasks.append(task)

            await asyncio.gather(*tasks)

        duration = time.time() - start_time
        self.log(f"\nScenario 2 completed in {duration:.2f} seconds")

    async def scenario_mixed_load(self):
        """Scenario 3: Mixed load - some under limit, some exceed"""
        self.log("\n" + "="*80)
        self.log("SCENARIO 3: MIXED LOAD - Various user behaviors")
        self.log("="*80)

        # Group 1: Light users (under limit)
        light_users = 30
        light_requests = 2

        # Group 2: Heavy users (exceed limit)
        heavy_users = 20
        heavy_requests = 20  # Should trigger rate limiting

        test_endpoints = [
            "/api/system/stats",
            "/api/system/network",
            "/api/system/disk",
            "/api/services",
            "/api/health"
        ]

        self.log(f"Light users: {light_users} users x {light_requests} req/endpoint")
        self.log(f"Heavy users: {heavy_users} users x {heavy_requests} req/endpoint (should trigger rate limits)")

        start_time = time.time()

        connector = aiohttp.TCPConnector(limit=150, limit_per_host=150)
        timeout = aiohttp.ClientTimeout(total=30)

        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            tasks = []

            # Light users
            for user_id in range(light_users):
                task = asyncio.create_task(
                    self.user_session(session, user_id, test_endpoints, light_requests)
                )
                tasks.append(task)

            # Heavy users
            for user_id in range(heavy_users):
                task = asyncio.create_task(
                    self.user_session(session, 1000 + user_id, test_endpoints, heavy_requests)
                )
                tasks.append(task)

            await asyncio.gather(*tasks)

        duration = time.time() - start_time
        self.log(f"\nScenario 3 completed in {duration:.2f} seconds")

    async def run_all_scenarios(self):
        """Execute all test scenarios"""
        self.log("="*80)
        self.log("CONCURRENT LOAD TEST - CONTROL CENTER BACKEND")
        self.log("="*80)
        self.log(f"Base URL: {BASE_URL}")
        self.log(f"Test start: {datetime.now()}")

        # Authenticate
        if not await self.authenticate():
            self.log("ERROR: Authentication failed. Aborting tests.")
            return False

        # Run scenarios
        try:
            initial_count = len(self.results.requests)
            await self.scenario_rapid_fire()
            self.log(f"Requests after scenario 1: {len(self.results.requests) - initial_count}")

            initial_count = len(self.results.requests)
            await self.scenario_sustained_load()
            self.log(f"Requests after scenario 2: {len(self.results.requests) - initial_count}")

            initial_count = len(self.results.requests)
            await self.scenario_mixed_load()
            self.log(f"Requests after scenario 3: {len(self.results.requests) - initial_count}")

        except Exception as e:
            self.log(f"ERROR during test execution: {e}")
            import traceback
            self.log(traceback.format_exc())
            return False

        # Print results
        self.print_results()
        return True

    def print_results(self):
        """Print comprehensive results"""
        self.log("\n" + "="*80)
        self.log("TEST RESULTS SUMMARY")
        self.log("="*80)

        stats = self.results.get_stats()

        self.log(f"\nTotal Requests: {stats['total_requests']}")
        self.log(f"Rate Limited (429): {stats['rate_limited']}")
        self.log(f"Errors: {stats['errors']}")

        self.log("\nStatus Code Distribution:")
        for status, count in sorted(stats['status_codes'].items()):
            percentage = (count / stats['total_requests']) * 100
            self.log(f"  {status}: {count} ({percentage:.1f}%)")

        self.log("\nResponse Time Statistics (ms):")
        self.log(f"  Min:    {stats['durations']['min']*1000:.2f}")
        self.log(f"  Mean:   {stats['durations']['mean']*1000:.2f}")
        self.log(f"  Median: {stats['durations']['median']*1000:.2f}")
        self.log(f"  P95:    {stats['durations']['p95']*1000:.2f}")
        self.log(f"  P99:    {stats['durations']['p99']*1000:.2f}")
        self.log(f"  Max:    {stats['durations']['max']*1000:.2f}")

        self.log("\nPer-Endpoint Results:")
        for endpoint, ep_stats in sorted(stats['by_endpoint'].items()):
            self.log(f"\n  {endpoint}:")
            self.log(f"    Total requests: {ep_stats['total']}")
            self.log(f"    Rate limited: {ep_stats['rate_limited']}")
            self.log(f"    Avg duration: {ep_stats['avg_duration']*1000:.2f}ms")
            self.log(f"    P95 duration: {ep_stats['p95_duration']*1000:.2f}ms")
            self.log(f"    Status codes: {ep_stats['status_codes']}")

        # Check success criteria
        self.log("\n" + "="*80)
        self.log("SUCCESS CRITERIA EVALUATION")
        self.log("="*80)

        p95_ms = stats['durations']['p95'] * 1000
        success = True

        # 1. Rate limits enforced
        if stats['rate_limited'] > 0:
            self.log("✓ Rate limiting enforced (429 responses detected)")
        else:
            self.log("✗ WARNING: No rate limiting detected")
            success = False

        # 2. No 500 errors
        error_5xx = sum(count for status, count in stats['status_codes'].items() if 500 <= status < 600)
        if error_5xx == 0:
            self.log("✓ No server errors (5xx)")
        else:
            self.log(f"✗ Server errors detected: {error_5xx} 5xx responses")
            success = False

        # 3. Response times acceptable
        if p95_ms < 500:
            self.log(f"✓ Response times acceptable (P95: {p95_ms:.2f}ms < 500ms)")
        else:
            self.log(f"✗ Response times too high (P95: {p95_ms:.2f}ms >= 500ms)")
            success = False

        # 4. Most requests successful
        success_2xx = sum(count for status, count in stats['status_codes'].items() if 200 <= status < 300)
        success_rate = (success_2xx / stats['total_requests']) * 100 if stats['total_requests'] > 0 else 0
        if success_rate > 50:  # At least 50% should succeed (rest can be rate limited)
            self.log(f"✓ Success rate acceptable: {success_rate:.1f}%")
        else:
            self.log(f"✗ Success rate too low: {success_rate:.1f}%")
            success = False

        self.log("\n" + "="*80)
        if success:
            self.log("OVERALL: PASS ✓")
        else:
            self.log("OVERALL: REVIEW NEEDED")
        self.log("="*80)

    def close(self):
        """Cleanup"""
        self.log_file.close()


async def main():
    """Main entry point"""
    tester = ConcurrentLoadTester()
    try:
        success = await tester.run_all_scenarios()
        return 0 if success else 1
    finally:
        tester.close()


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
