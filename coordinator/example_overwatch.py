"""
Example Overwatch Agent Implementation
Demonstrates how an Overwatch agent would deploy L2 workers using the client library
"""

from pathlib import Path
from coordinator.client import AgentDeploymentClient


def overwatch_mission(mission_data: dict):
    """
    Example Overwatch mission that deploys L2 worker agents

    Args:
        mission_data: Dictionary containing:
            - task_description: Main task to accomplish
            - subtasks: List of subtasks to delegate
            - parent_agent_id: ID of this Overwatch agent
    """
    print("=" * 60)
    print("OVERWATCH AGENT - Mission Execution")
    print("=" * 60)

    # Initialize deployment client
    deployment_dir = Path("C:/Ziggie/agent-deployment")
    client = AgentDeploymentClient(
        deployment_dir=deployment_dir,
        parent_agent_id=mission_data["parent_agent_id"]
    )

    print(f"\nMission: {mission_data['task_description']}")
    print(f"Subtasks: {len(mission_data['subtasks'])}")
    print(f"Parent Agent: {mission_data['parent_agent_id']}")

    # Deploy L2 workers for each subtask
    deployed_agents = []

    for i, subtask in enumerate(mission_data["subtasks"], 1):
        agent_id = f"L2.{mission_data['parent_agent_id'].split('.')[1]}.{i}"

        print(f"\n[{i}] Deploying {agent_id}: {subtask['name']}")

        response = client.deploy_agent(
            agent_id=agent_id,
            agent_name=subtask["name"],
            agent_type="L2",
            prompt=subtask["prompt"],
            model=subtask.get("model", "haiku"),
            load_percentage=subtask.get("load_percentage", 0.0),
            estimated_duration=subtask.get("estimated_duration"),
            metadata={
                "overwatch_agent": mission_data["parent_agent_id"],
                "subtask_index": i,
                "mission": mission_data["task_description"]
            }
        )

        if response.status in ["running", "completed"]:
            print(f"    ✓ Deployed successfully (PID: {response.pid})")
            deployed_agents.append(response)
        else:
            print(f"    ✗ Deployment failed: {response.error}")

    # Monitor deployed agents
    print(f"\n{'=' * 60}")
    print("Monitoring deployed agents...")
    print(f"{'=' * 60}")

    for agent in deployed_agents:
        status = client.get_agent_status(agent.agent_id)
        if status:
            print(f"  {agent.agent_id}: {status['status']}")

    return deployed_agents


# Example mission data
example_mission = {
    "parent_agent_id": "L1.OVERWATCH.1",
    "task_description": "Optimize Control Center performance and fix UI bugs",
    "subtasks": [
        {
            "name": "Backend Performance Analyzer",
            "prompt": "Analyze Control Center backend performance. Check database query times, API response times, and identify bottlenecks. Generate performance report.",
            "model": "haiku",
            "load_percentage": 30.0,
            "estimated_duration": 120
        },
        {
            "name": "Frontend UI Bug Fixer",
            "prompt": "Review Control Center frontend console errors. Fix any React warnings, CSS issues, or component rendering problems. Verify all pages load correctly.",
            "model": "haiku",
            "load_percentage": 40.0,
            "estimated_duration": 180
        },
        {
            "name": "Database Query Optimizer",
            "prompt": "Analyze MongoDB queries in Control Center backend. Add indexes where needed, optimize slow queries, and verify connection pooling is configured correctly.",
            "model": "haiku",
            "load_percentage": 30.0,
            "estimated_duration": 150
        }
    ]
}


if __name__ == "__main__":
    # Run example mission
    deployed = overwatch_mission(example_mission)
    print(f"\n✓ Mission complete - deployed {len(deployed)} agents")
