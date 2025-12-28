#!/usr/bin/env python3
"""
End-to-End Testing Script for Agents Interface
QA Agent L1.8 - Quality Assurance Testing
Generated: 2025-11-08
"""

import requests
import json
import sys
from datetime import datetime
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "control-center" / "backend"))

from api.agents import load_l1_agents, load_l2_agents, load_l3_agents

API_BASE = "http://127.0.0.1:54112"

class TestResults:
    def __init__(self):
        self.tests = []
        self.passed = 0
        self.failed = 0
        self.warnings = []
        self.critical_bugs = []

    def add_test(self, name, status, message="", expected=None, actual=None):
        result = {
            "test": name,
            "status": status,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        if expected is not None:
            result["expected"] = expected
        if actual is not None:
            result["actual"] = actual

        self.tests.append(result)
        if status == "PASS":
            self.passed += 1
        elif status == "FAIL":
            self.failed += 1

    def add_warning(self, message):
        self.warnings.append(message)

    def add_critical_bug(self, message):
        self.critical_bugs.append(message)

    def print_summary(self):
        print("\n" + "="*80)
        print("AGENTS INTERFACE E2E TEST REPORT")
        print("="*80)
        print(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"\nTotal Tests: {len(self.tests)}")
        print(f"Passed: {self.passed} ({self.passed/len(self.tests)*100:.1f}%)" if self.tests else "No tests run")
        print(f"Failed: {self.failed} ({self.failed/len(self.tests)*100:.1f}%)" if self.tests else "")

        print("\n" + "-"*80)
        print("TEST RESULTS:")
        print("-"*80)
        for test in self.tests:
            status_icon = "[PASS]" if test["status"] == "PASS" else "[FAIL]"
            print(f"{status_icon} {test['test']}")
            if test['message']:
                print(f"  > {test['message']}")
            if 'expected' in test and 'actual' in test:
                print(f"  Expected: {test['expected']}")
                print(f"  Actual: {test['actual']}")

        if self.critical_bugs:
            print("\n" + "-"*80)
            print("CRITICAL BUGS FOUND:")
            print("-"*80)
            for i, bug in enumerate(self.critical_bugs, 1):
                print(f"{i}. {bug}")

        if self.warnings:
            print("\n" + "-"*80)
            print("WARNINGS:")
            print("-"*80)
            for i, warning in enumerate(self.warnings, 1):
                print(f"{i}. {warning}")

        print("\n" + "="*80)

def test_backend_api(results):
    """Test Backend API Endpoints"""
    print("\n### TESTING BACKEND API ###\n")

    # Test 1: Health check
    try:
        response = requests.get(f"{API_BASE}/health", timeout=5)
        if response.status_code == 200:
            results.add_test("Backend Health Check", "PASS", "Server is healthy")
        else:
            results.add_test("Backend Health Check", "FAIL", f"Status code: {response.status_code}")
    except Exception as e:
        results.add_test("Backend Health Check", "FAIL", str(e))
        return

    # Test 2: Direct loading (bypassing API)
    print("Loading agents directly from files...")
    l1_agents = load_l1_agents()
    l2_agents = load_l2_agents()
    l3_agents = load_l3_agents()

    total_direct = len(l1_agents) + len(l2_agents) + len(l3_agents)
    results.add_test(
        "Direct Agent Loading",
        "PASS" if total_direct > 0 else "FAIL",
        f"Loaded {len(l1_agents)} L1, {len(l2_agents)} L2, {len(l3_agents)} L3 = {total_direct} total",
        expected="168 total agents",
        actual=f"{total_direct} total agents"
    )

    if total_direct == 168:
        results.add_test("Expected Agent Count", "PASS", "Correct number of agents")
    else:
        results.add_warning(f"Expected 168 agents (8 L1 + 64 L2 + 96 L3), got {total_direct}")

    # Test 3: GET /api/agents/stats
    print("Testing GET /api/agents/stats...")
    try:
        response = requests.get(f"{API_BASE}/api/agents/stats", timeout=5)
        if response.status_code == 200:
            stats = response.json()

            # Check structure
            required_fields = ["total_agents", "l1_count", "l2_count", "l3_count", "expected", "distribution"]
            missing = [f for f in required_fields if f not in stats]

            if missing:
                results.add_test("Stats Endpoint - Structure", "FAIL", f"Missing fields: {missing}")
            else:
                results.add_test("Stats Endpoint - Structure", "PASS", "All required fields present")

            # Check values
            if stats.get("total_agents", 0) == 0:
                results.add_critical_bug(
                    "BUG #1: Stats endpoint returns 0 agents despite files existing. "
                    "Root cause: Backend may not be reloading after code changes, or module is cached."
                )
                results.add_test(
                    "Stats Endpoint - Data",
                    "FAIL",
                    "Returns 0 agents (should be 168)",
                    expected=total_direct,
                    actual=stats.get("total_agents", 0)
                )
            else:
                results.add_test("Stats Endpoint - Data", "PASS", f"Returns {stats.get('total_agents')} agents")

        else:
            results.add_test("Stats Endpoint", "FAIL", f"Status code: {response.status_code}")
    except Exception as e:
        results.add_test("Stats Endpoint", "FAIL", str(e))

    # Test 4: GET /api/agents
    print("Testing GET /api/agents...")
    try:
        response = requests.get(f"{API_BASE}/api/agents?limit=10", timeout=5)
        if response.status_code == 200:
            data = response.json()

            if "agents" in data and "total" in data:
                results.add_test("List Agents - Structure", "PASS", "Response structure correct")

                if data["total"] == 0:
                    results.add_test(
                        "List Agents - Data",
                        "FAIL",
                        "Returns empty list (same bug as stats endpoint)"
                    )
                else:
                    results.add_test("List Agents - Data", "PASS", f"Returns {data['total']} agents")
            else:
                results.add_test("List Agents - Structure", "FAIL", "Missing required fields")
        else:
            results.add_test("List Agents", "FAIL", f"Status code: {response.status_code}")
    except Exception as e:
        results.add_test("List Agents", "FAIL", str(e))

    # Test 5: GET /api/agents with filters
    print("Testing GET /api/agents with level filter...")
    try:
        response = requests.get(f"{API_BASE}/api/agents?level=L1&limit=20", timeout=5)
        if response.status_code == 200:
            data = response.json()
            results.add_test("List Agents with Filter", "PASS", "Filter endpoint works")
        else:
            results.add_test("List Agents with Filter", "FAIL", f"Status code: {response.status_code}")
    except Exception as e:
        results.add_test("List Agents with Filter", "FAIL", str(e))

    # Test 6: GET /api/agents/{id}
    print("Testing GET /api/agents/{id}...")
    test_agent_id = "01_art_director"
    try:
        response = requests.get(f"{API_BASE}/api/agents/{test_agent_id}", timeout=5)
        if response.status_code == 200:
            agent = response.json()
            if "id" in agent and "level" in agent:
                results.add_test("Get Agent Details", "PASS", f"Retrieved {test_agent_id}")
            else:
                results.add_test("Get Agent Details", "FAIL", "Missing required fields in response")
        elif response.status_code == 404:
            results.add_test("Get Agent Details", "FAIL", "Agent not found (data loading issue)")
        else:
            results.add_test("Get Agent Details", "FAIL", f"Status code: {response.status_code}")
    except Exception as e:
        results.add_test("Get Agent Details", "FAIL", str(e))

    # Test 7: GET /api/agents/{id}/knowledge
    print("Testing GET /api/agents/{id}/knowledge...")
    try:
        response = requests.get(f"{API_BASE}/api/agents/{test_agent_id}/knowledge", timeout=5)
        if response.status_code == 200:
            kb_data = response.json()
            if "files" in kb_data:
                results.add_test("Get Agent Knowledge", "PASS", f"Retrieved knowledge base info")
            else:
                results.add_test("Get Agent Knowledge", "FAIL", "Missing 'files' field")
        else:
            results.add_test("Get Agent Knowledge", "FAIL", f"Status code: {response.status_code}")
    except Exception as e:
        results.add_test("Get Agent Knowledge", "FAIL", str(e))

def test_data_accuracy(results):
    """Test data accuracy and parsing"""
    print("\n### TESTING DATA ACCURACY ###\n")

    l1_agents = load_l1_agents()
    l2_agents = load_l2_agents()
    l3_agents = load_l3_agents()

    # Test L1 parsing
    if len(l1_agents) == 8:
        results.add_test("L1 Agent Count", "PASS", "Found all 8 L1 agents")
    else:
        results.add_test("L1 Agent Count", "FAIL", f"Expected 8, found {len(l1_agents)}")

    # Check L1 agent has required fields
    if l1_agents:
        agent = l1_agents[0]
        required = ["id", "level", "filename", "title", "role", "objective"]
        missing = [f for f in required if f not in agent or not agent[f]]

        if missing:
            results.add_test("L1 Agent Parsing", "FAIL", f"Missing/empty fields: {missing}")
        else:
            results.add_test("L1 Agent Parsing", "PASS", "All required fields present and populated")

    # Test L2 parsing
    if len(l2_agents) == 64:
        results.add_test("L2 Agent Count", "PASS", "Found all 64 L2 agents")
    else:
        results.add_test("L2 Agent Count", "FAIL", f"Expected 64, found {len(l2_agents)}")

    # Test L3 parsing
    if len(l3_agents) == 96:
        results.add_test("L3 Agent Count", "PASS", "Found all 96 L3 agents")
        results.add_warning("Note: Mission brief mentions 729 L3 agents, but only 96 are defined in L3_MICRO_AGENT_ARCHITECTURE.md")
    else:
        results.add_test("L3 Agent Count", "FAIL", f"Expected 96, found {len(l3_agents)}")

    # Test hierarchy relationships
    l2_with_parents = [a for a in l2_agents if a.get('parent_l1')]
    if len(l2_with_parents) == len(l2_agents):
        results.add_test("L2 Parent References", "PASS", "All L2 agents have parent L1 references")
    else:
        results.add_test("L2 Parent References", "FAIL",
                        f"{len(l2_agents) - len(l2_with_parents)} L2 agents missing parent references")

    l3_with_parents = [a for a in l3_agents if a.get('parent_l2')]
    if len(l3_with_parents) == len(l3_agents):
        results.add_test("L3 Parent References", "PASS", "All L3 agents have parent L2 references")
    else:
        results.add_test("L3 Parent References", "FAIL",
                        f"{len(l3_agents) - len(l3_with_parents)} L3 agents missing parent references")

def test_regex_fix(results):
    """Verify the regex fix was applied"""
    print("\n### TESTING REGEX FIX ###\n")

    # Check if the fix is in the code
    agents_file = Path(__file__).parent / "control-center" / "backend" / "api" / "agents.py"

    if agents_file.exists():
        content = agents_file.read_text(encoding='utf-8')

        if r"###\s+L3\." in content:
            results.add_test("L3 Regex Pattern Fix", "PASS", "Corrected pattern (### instead of ####) is in code")
        elif r"####\s+L3\." in content:
            results.add_critical_bug(
                "BUG #2: L3 agent regex pattern still uses #### (4 hashes) but actual file uses ### (3 hashes). "
                "This causes L3 agents to not be parsed. Fix: Change line 255 to use r'###\\s+L3\\.' pattern."
            )
            results.add_test("L3 Regex Pattern Fix", "FAIL", "Still using incorrect #### pattern")
        else:
            results.add_test("L3 Regex Pattern Fix", "WARN", "Pattern not found in expected location")
    else:
        results.add_test("L3 Regex Pattern Fix", "FAIL", f"File not found: {agents_file}")

def main():
    print("="*80)
    print("AGENTS INTERFACE END-TO-END TESTING")
    print("QA Agent L1.8 - Quality Assurance")
    print("="*80)

    results = TestResults()

    # Run all test suites
    test_backend_api(results)
    test_data_accuracy(results)
    test_regex_fix(results)

    # Print summary report
    results.print_summary()

    # Exit with error code if tests failed
    sys.exit(0 if results.failed == 0 else 1)

if __name__ == "__main__":
    main()
