#!/usr/bin/env python3
"""
Direct test of chat endpoint with extended timeout
"""

import requests
import json
import time

BASE_URL = "https://ziggie.cloud/sim/api"

# Get or create agent
print("Step 1: Checking for existing agent...")
resp = requests.get(f"{BASE_URL}/agents")
agents = resp.json()["agents"]

if agents:
    agent_id = agents[0]["id"]
    print(f"Using existing agent: {agent_id}")
else:
    print("Creating new agent...")
    agent_payload = {
        "name": "Direct Test Agent",
        "description": "For direct chat testing",
        "model": "mistral:7b",
        "system_prompt": "You are a helpful assistant. Keep responses brief.",
        "personality": {},
        "tools": []
    }
    resp = requests.post(f"{BASE_URL}/agents", json=agent_payload)
    agent = resp.json()
    agent_id = agent["id"]
    print(f"Created agent: {agent_id}")

# Create simulation
print("\nStep 2: Creating simulation...")
sim_payload = {
    "agent_id": agent_id,
    "scenario": "customer_support",
    "max_turns": 2,
    "temperature": 0.7
}
resp = requests.post(f"{BASE_URL}/simulations", json=sim_payload)
sim = resp.json()
sim_id = sim["id"]
print(f"Created simulation: {sim_id}")
print(json.dumps(sim, indent=2))

# Test chat with extended timeout
print("\nStep 3: Testing chat with 120s timeout...")
print("Sending message: 'Hello'")
start = time.time()

try:
    resp = requests.post(
        f"{BASE_URL}/simulations/{sim_id}/chat",
        json={"role": "user", "content": "Hello"},
        timeout=120  # 2 minute timeout
    )
    elapsed = time.time() - start

    print(f"\nResponse received in {elapsed:.2f}s")
    print(f"Status code: {resp.status_code}")

    if resp.status_code == 200:
        result = resp.json()
        print("\nSuccess! Response:")
        print(json.dumps(result, indent=2))
    else:
        print(f"\nError response:")
        print(resp.text)

except requests.Timeout:
    print(f"\nTimeout after {time.time() - start:.2f}s")
except Exception as e:
    print(f"\nError: {e}")

# Check simulation state
print("\n\nStep 4: Checking simulation state...")
resp = requests.get(f"{BASE_URL}/simulations/{sim_id}")
data = resp.json()
print(json.dumps(data, indent=2))
