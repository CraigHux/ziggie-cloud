#!/usr/bin/env python3
"""
Sim Studio Comprehensive Audit Script
Tests all endpoints and workflows against specification
"""

import requests
import json
import time
from typing import Dict, List, Any

BASE_URL = "https://ziggie.cloud/sim"
API_BASE = f"{BASE_URL}/api"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def print_test(name: str):
    print(f"\n{Colors.BLUE}{'='*80}{Colors.RESET}")
    print(f"{Colors.BLUE}TEST: {name}{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*80}{Colors.RESET}")

def print_pass(msg: str):
    print(f"{Colors.GREEN}[PASS] {msg}{Colors.RESET}")

def print_fail(msg: str):
    print(f"{Colors.RED}[FAIL] {msg}{Colors.RESET}")

def print_info(msg: str):
    print(f"{Colors.YELLOW}[INFO] {msg}{Colors.RESET}")

def print_json(data: Any):
    print(json.dumps(data, indent=2))

def test_health():
    """Test health endpoint"""
    print_test("Health Check")
    try:
        resp = requests.get(f"{BASE_URL}/health")
        resp.raise_for_status()
        data = resp.json()

        assert data.get("status") == "ok", "Status should be 'ok'"
        assert data.get("service") == "sim-studio", "Service should be 'sim-studio'"
        assert data.get("version") == "1.0.0", "Version should be '1.0.0'"

        print_pass("Health check endpoint working")
        print_json(data)
        return True
    except Exception as e:
        print_fail(f"Health check failed: {e}")
        return False

def test_root():
    """Test root endpoint"""
    print_test("Root Endpoint")
    try:
        resp = requests.get(BASE_URL)
        resp.raise_for_status()
        data = resp.json()

        assert data.get("service") == "Ziggie Sim Studio"
        assert data.get("version") == "1.0.0"
        assert "endpoints" in data

        endpoints = data["endpoints"]
        assert endpoints.get("agents") == "/api/agents"
        assert endpoints.get("simulations") == "/api/simulations"
        assert endpoints.get("scenarios") == "/api/scenarios"
        assert endpoints.get("templates") == "/api/templates"

        print_pass("Root endpoint returns correct information")
        print_json(data)
        return True
    except Exception as e:
        print_fail(f"Root endpoint failed: {e}")
        return False

def test_scenarios():
    """Test scenarios endpoint"""
    print_test("Scenarios Endpoint")
    try:
        resp = requests.get(f"{API_BASE}/scenarios")
        resp.raise_for_status()
        data = resp.json()

        scenarios = data.get("scenarios", [])
        assert len(scenarios) == 4, f"Should have 4 scenarios, got {len(scenarios)}"

        scenario_ids = [s["id"] for s in scenarios]
        expected_ids = ["customer_support", "code_review", "creative_writing", "problem_solving"]

        for expected_id in expected_ids:
            assert expected_id in scenario_ids, f"Missing scenario: {expected_id}"

        print_pass(f"All 4 scenarios present: {scenario_ids}")
        print_json(data)
        return True
    except Exception as e:
        print_fail(f"Scenarios endpoint failed: {e}")
        return False

def test_templates():
    """Test templates endpoint"""
    print_test("Templates Endpoint")
    try:
        resp = requests.get(f"{API_BASE}/templates")
        resp.raise_for_status()
        data = resp.json()

        templates = data.get("templates", [])
        assert len(templates) == 3, f"Should have 3 templates, got {len(templates)}"

        template_ids = [t["id"] for t in templates]
        expected_ids = ["assistant", "coder", "analyst"]

        for expected_id in expected_ids:
            assert expected_id in template_ids, f"Missing template: {expected_id}"

        for template in templates:
            assert "name" in template
            assert "model" in template
            assert "system_prompt" in template

        print_pass(f"All 3 templates present: {template_ids}")
        print_json(data)
        return True
    except Exception as e:
        print_fail(f"Templates endpoint failed: {e}")
        return False

def test_agent_crud():
    """Test agent CRUD operations"""
    print_test("Agent CRUD Operations")

    # 1. List agents (should be empty or have existing)
    print_info("Step 1: List all agents")
    try:
        resp = requests.get(f"{API_BASE}/agents")
        resp.raise_for_status()
        data = resp.json()
        initial_count = len(data.get("agents", []))
        print_pass(f"Initial agent count: {initial_count}")
        print_json(data)
    except Exception as e:
        print_fail(f"List agents failed: {e}")
        return False

    # 2. Create new agent
    print_info("Step 2: Create new agent")
    agent_payload = {
        "name": "Test Agent Alpha",
        "description": "Audit test agent for comprehensive testing",
        "model": "mistral:7b",
        "system_prompt": "You are Test Agent Alpha, a friendly and helpful assistant created for testing purposes. Be concise and clear.",
        "personality": {
            "friendliness": 0.9,
            "formality": 0.5
        },
        "tools": ["calculator", "search"]
    }

    try:
        resp = requests.post(f"{API_BASE}/agents", json=agent_payload)
        resp.raise_for_status()
        agent = resp.json()

        assert "id" in agent, "Agent should have an ID"
        assert agent["name"] == agent_payload["name"]
        assert agent["description"] == agent_payload["description"]
        assert agent["system_prompt"] == agent_payload["system_prompt"]
        assert "created_at" in agent

        agent_id = agent["id"]
        print_pass(f"Created agent with ID: {agent_id}")
        print_json(agent)
    except Exception as e:
        print_fail(f"Create agent failed: {e}")
        return False

    # 3. Get specific agent
    print_info(f"Step 3: Get agent {agent_id}")
    try:
        resp = requests.get(f"{API_BASE}/agents/{agent_id}")
        resp.raise_for_status()
        retrieved_agent = resp.json()

        assert retrieved_agent["id"] == agent_id
        assert retrieved_agent["name"] == agent_payload["name"]

        print_pass(f"Retrieved agent: {retrieved_agent['name']}")
        print_json(retrieved_agent)
    except Exception as e:
        print_fail(f"Get agent failed: {e}")
        return False

    # 4. List agents again (should have one more)
    print_info("Step 4: List agents again")
    try:
        resp = requests.get(f"{API_BASE}/agents")
        resp.raise_for_status()
        data = resp.json()
        new_count = len(data.get("agents", []))

        assert new_count == initial_count + 1, f"Expected {initial_count + 1} agents, got {new_count}"
        print_pass(f"Agent count increased to {new_count}")
    except Exception as e:
        print_fail(f"List agents (2nd time) failed: {e}")
        return False

    # 5. Delete agent
    print_info(f"Step 5: Delete agent {agent_id}")
    try:
        resp = requests.delete(f"{API_BASE}/agents/{agent_id}")
        resp.raise_for_status()
        result = resp.json()

        assert "message" in result
        print_pass(f"Deleted agent: {result['message']}")
        print_json(result)
    except Exception as e:
        print_fail(f"Delete agent failed: {e}")
        return False

    # 6. Verify deletion
    print_info(f"Step 6: Verify agent {agent_id} is deleted")
    try:
        resp = requests.get(f"{API_BASE}/agents/{agent_id}")
        if resp.status_code == 404:
            print_pass("Agent correctly returns 404 after deletion")
        else:
            print_fail(f"Expected 404, got {resp.status_code}")
            return False
    except Exception as e:
        print_fail(f"Verify deletion failed: {e}")
        return False

    print_pass("All agent CRUD operations passed")
    return True

def test_edge_case_nonexistent_agent():
    """Test edge case: get/delete non-existent agent"""
    print_test("Edge Case: Non-existent Agent")

    fake_id = "agent_nonexistent"

    # Test GET
    print_info(f"Testing GET on non-existent agent: {fake_id}")
    try:
        resp = requests.get(f"{API_BASE}/agents/{fake_id}")
        if resp.status_code == 404:
            print_pass("GET correctly returns 404 for non-existent agent")
        else:
            print_fail(f"Expected 404, got {resp.status_code}")
            return False
    except Exception as e:
        print_fail(f"Test failed: {e}")
        return False

    # Test DELETE
    print_info(f"Testing DELETE on non-existent agent: {fake_id}")
    try:
        resp = requests.delete(f"{API_BASE}/agents/{fake_id}")
        if resp.status_code == 404:
            print_pass("DELETE correctly returns 404 for non-existent agent")
        else:
            print_fail(f"Expected 404, got {resp.status_code}")
            return False
    except Exception as e:
        print_fail(f"Test failed: {e}")
        return False

    print_pass("Non-existent agent edge cases handled correctly")
    return True

def test_full_simulation_workflow():
    """Test complete simulation workflow"""
    print_test("Full Simulation Workflow")

    # Step 1: Create an agent
    print_info("Step 1: Create agent for simulation")
    agent_payload = {
        "name": "Simulation Test Agent",
        "description": "Agent for testing full simulation workflow",
        "model": "mistral:7b",
        "system_prompt": "You are a helpful assistant. Provide brief, informative responses.",
        "personality": {},
        "tools": []
    }

    try:
        resp = requests.post(f"{API_BASE}/agents", json=agent_payload)
        resp.raise_for_status()
        agent = resp.json()
        agent_id = agent["id"]
        print_pass(f"Created agent: {agent_id}")
    except Exception as e:
        print_fail(f"Failed to create agent: {e}")
        return False

    # Step 2: Create simulation
    print_info("Step 2: Create simulation with max_turns=3")
    sim_payload = {
        "agent_id": agent_id,
        "scenario": "customer_support",
        "max_turns": 3,
        "temperature": 0.7
    }

    try:
        resp = requests.post(f"{API_BASE}/simulations", json=sim_payload)
        resp.raise_for_status()
        sim = resp.json()

        assert "id" in sim
        assert sim["agent_id"] == agent_id
        assert sim["scenario"] == "customer_support"
        assert sim["max_turns"] == 3
        assert sim["status"] == "created"
        assert sim["turns"] == 0

        sim_id = sim["id"]
        print_pass(f"Created simulation: {sim_id}")
        print_json(sim)
    except Exception as e:
        print_fail(f"Failed to create simulation: {e}")
        return False

    # Step 3: Send chat messages and verify turn counting
    print_info("Step 3: Send chat messages (3 turns)")

    messages = [
        "Hello, I need help with my account",
        "Can you explain your pricing plans?",
        "Thank you for the information"
    ]

    for i, msg_content in enumerate(messages, 1):
        print_info(f"Turn {i}/{len(messages)}: Sending message")
        try:
            resp = requests.post(
                f"{API_BASE}/simulations/{sim_id}/chat",
                json={"role": "user", "content": msg_content}
            )
            resp.raise_for_status()
            result = resp.json()

            assert "user" in result
            assert "agent" in result
            assert "simulation" in result

            sim_status = result["simulation"]
            assert sim_status["turns"] == i, f"Expected turn {i}, got {sim_status['turns']}"

            expected_status = "completed" if i == 3 else "running"
            assert sim_status["status"] == expected_status, \
                f"Expected status '{expected_status}', got '{sim_status['status']}'"

            print_pass(f"Turn {i}: User message sent, agent responded")
            print_info(f"User: {result['user']['content']}")
            print_info(f"Agent: {result['agent']['content']}")
            print_info(f"Status: {sim_status['status']}, Turns: {sim_status['turns']}/{sim_status['max_turns']}")

        except Exception as e:
            print_fail(f"Chat failed on turn {i}: {e}")
            return False

    # Step 4: Verify simulation is completed
    print_info("Step 4: Verify simulation reached max_turns and status='completed'")
    try:
        resp = requests.get(f"{API_BASE}/simulations/{sim_id}")
        resp.raise_for_status()
        data = resp.json()

        sim_final = data["simulation"]
        conversation = data["conversation"]

        assert sim_final["status"] == "completed", "Should be completed"
        assert sim_final["turns"] == 3, "Should have 3 turns"
        assert len(conversation) == 6, "Should have 6 messages (3 user + 3 agent)"

        print_pass("Simulation completed correctly")
        print_info(f"Final conversation length: {len(conversation)} messages")

    except Exception as e:
        print_fail(f"Failed to verify simulation: {e}")
        return False

    # Step 5: Cleanup
    print_info("Step 5: Cleanup - delete agent")
    try:
        requests.delete(f"{API_BASE}/agents/{agent_id}")
        print_pass("Cleaned up test agent")
    except Exception as e:
        print_fail(f"Cleanup failed: {e}")

    print_pass("Full simulation workflow completed successfully")
    return True

def test_edge_case_nonexistent_simulation():
    """Test edge cases for simulations"""
    print_test("Edge Case: Non-existent Simulation")

    fake_sim_id = "sim_nonexistent"

    # Test GET
    print_info(f"Testing GET on non-existent simulation: {fake_sim_id}")
    try:
        resp = requests.get(f"{API_BASE}/simulations/{fake_sim_id}")
        if resp.status_code == 404:
            print_pass("GET correctly returns 404 for non-existent simulation")
        else:
            print_fail(f"Expected 404, got {resp.status_code}")
            return False
    except Exception as e:
        print_fail(f"Test failed: {e}")
        return False

    # Test CHAT
    print_info(f"Testing CHAT on non-existent simulation: {fake_sim_id}")
    try:
        resp = requests.post(
            f"{API_BASE}/simulations/{fake_sim_id}/chat",
            json={"role": "user", "content": "test"}
        )
        if resp.status_code == 404:
            print_pass("CHAT correctly returns 404 for non-existent simulation")
        else:
            print_fail(f"Expected 404, got {resp.status_code}")
            return False
    except Exception as e:
        print_fail(f"Test failed: {e}")
        return False

    print_pass("Non-existent simulation edge cases handled correctly")
    return True

def test_edge_case_simulation_with_nonexistent_agent():
    """Test creating simulation with non-existent agent"""
    print_test("Edge Case: Create Simulation with Non-existent Agent")

    sim_payload = {
        "agent_id": "agent_doesnotexist",
        "scenario": "customer_support",
        "max_turns": 5,
        "temperature": 0.7
    }

    try:
        resp = requests.post(f"{API_BASE}/simulations", json=sim_payload)
        if resp.status_code == 404:
            print_pass("Correctly returns 404 when creating simulation with non-existent agent")
            return True
        else:
            print_fail(f"Expected 404, got {resp.status_code}")
            return False
    except Exception as e:
        print_fail(f"Test failed: {e}")
        return False

def run_all_tests():
    """Run all tests and report results"""
    print(f"\n{Colors.BLUE}{'='*80}{Colors.RESET}")
    print(f"{Colors.BLUE}SIM STUDIO COMPREHENSIVE AUDIT{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*80}{Colors.RESET}")
    print(f"Testing: {BASE_URL}")
    print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    tests = [
        ("Health Check", test_health),
        ("Root Endpoint", test_root),
        ("Scenarios Endpoint", test_scenarios),
        ("Templates Endpoint", test_templates),
        ("Agent CRUD Operations", test_agent_crud),
        ("Edge Case: Non-existent Agent", test_edge_case_nonexistent_agent),
        ("Edge Case: Non-existent Simulation", test_edge_case_nonexistent_simulation),
        ("Edge Case: Simulation with Non-existent Agent", test_edge_case_simulation_with_nonexistent_agent),
        ("Full Simulation Workflow", test_full_simulation_workflow),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print_fail(f"Test '{name}' crashed: {e}")
            results.append((name, False))

    # Summary
    print(f"\n{Colors.BLUE}{'='*80}{Colors.RESET}")
    print(f"{Colors.BLUE}AUDIT SUMMARY{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*80}{Colors.RESET}")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = f"{Colors.GREEN}[PASS]{Colors.RESET}" if result else f"{Colors.RED}[FAIL]{Colors.RESET}"
        print(f"{status}: {name}")

    print(f"\n{Colors.BLUE}{'='*80}{Colors.RESET}")
    pass_rate = (passed / total * 100) if total > 0 else 0

    if pass_rate == 100:
        print(f"{Colors.GREEN}RESULT: {passed}/{total} tests passed ({pass_rate:.0f}%){Colors.RESET}")
        print(f"{Colors.GREEN}[SUCCESS] All tests passed! Sim Studio is fully functional.{Colors.RESET}")
    else:
        print(f"{Colors.YELLOW}RESULT: {passed}/{total} tests passed ({pass_rate:.0f}%){Colors.RESET}")
        print(f"{Colors.RED}[FAILURE] Some tests failed. Review failures above.{Colors.RESET}")

    print(f"{Colors.BLUE}{'='*80}{Colors.RESET}\n")

if __name__ == "__main__":
    run_all_tests()
