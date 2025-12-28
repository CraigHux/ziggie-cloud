"""
Basic Integration Test
Tests the File-Based MVP deployment flow
"""

import json
import time
from pathlib import Path
from coordinator.client import AgentDeploymentClient
from coordinator.schemas import AgentStatus


def test_basic_deployment():
    """Test basic agent deployment flow"""
    print("=" * 60)
    print("ZIGGIE Agent Deployment - Basic Integration Test")
    print("=" * 60)

    # Setup
    deployment_dir = Path(__file__).parent.parent / "agent-deployment"
    parent_agent_id = "TEST_PARENT"

    # Create client
    client = AgentDeploymentClient(
        deployment_dir=deployment_dir,
        parent_agent_id=parent_agent_id
    )

    print(f"\n[1] Client initialized")
    print(f"    Deployment dir: {deployment_dir}")
    print(f"    Parent agent: {parent_agent_id}")

    # Deploy test agent
    print(f"\n[2] Deploying test agent...")
    response = client.deploy_agent(
        agent_id="L2.TEST.1",
        agent_name="Test Worker Agent",
        agent_type="L2",
        prompt="This is a test deployment. Verify you can read this prompt and respond with a simple acknowledgment.",
        model="haiku",
        load_percentage=10.0,
        estimated_duration=30,
        metadata={"test": True, "purpose": "MVP validation"},
        timeout=30
    )

    print(f"\n[3] Deployment response received:")
    print(f"    Request ID: {response.request_id}")
    print(f"    Agent ID: {response.agent_id}")
    print(f"    Status: {response.status}")
    print(f"    Message: {response.message}")
    if response.pid:
        print(f"    PID: {response.pid}")
    if response.error:
        print(f"    Error: {response.error}")

    # Check status
    if response.status == AgentStatus.RUNNING:
        print(f"\n[4] Checking agent status...")
        status = client.get_agent_status("L2.TEST.1")
        if status:
            print(f"    Status file found:")
            print(f"    {json.dumps(status, indent=6)}")
        else:
            print(f"    No status file found")

    # List deployed agents
    print(f"\n[5] Listing all deployed agents...")
    agents = client.list_my_agents()
    print(f"    Found {len(agents)} agent(s)")
    for agent in agents:
        print(f"    - {agent.get('agent_id', 'unknown')}: {agent.get('status', 'unknown')}")

    print("\n" + "=" * 60)
    print("Test completed")
    print("=" * 60)


if __name__ == "__main__":
    test_basic_deployment()
