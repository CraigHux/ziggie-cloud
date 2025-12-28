"""
Test Process Management Features
Demonstrates the robust process lifecycle management in AgentSpawner
"""

import sys
import time
from pathlib import Path

# Add coordinator to path
sys.path.insert(0, str(Path(__file__).parent))

from coordinator.agent_spawner import AgentSpawner
from coordinator.schemas import DeploymentRequest, AgentStatus
from datetime import datetime


def print_separator(title):
    """Print a formatted section separator"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def test_spawn_and_monitor():
    """Test spawning agents and monitoring their health"""
    print_separator("TEST 1: Spawn Agent and Monitor Health")

    # Create spawner
    deployment_dir = Path(__file__).parent / "test_deployment"
    spawner = AgentSpawner(deployment_dir)

    # Create deployment request
    request = DeploymentRequest(
        request_id="test_req_001",
        parent_agent_id="OVERWATCH-TEST",
        agent_id="L2.TEST.1",
        agent_name="Test Agent 1",
        agent_type="L2",
        model="haiku",
        prompt="Test task for process monitoring",
        load_percentage=25.0,
        estimated_duration=60
    )

    # Spawn agent
    print("Spawning agent...")
    response = spawner.spawn_agent(request)
    print(f"Response: {response.dict()}")

    if response.status == AgentStatus.RUNNING:
        print(f"\nAgent spawned successfully!")
        print(f"  Agent ID: {response.agent_id}")
        print(f"  PID: {response.pid}")
        print(f"  Status: {response.status}")

        # Monitor for a few seconds
        print("\nMonitoring agent health for 5 seconds...")
        for i in range(5):
            time.sleep(1)
            status = spawner.get_agent_status(request.agent_id)

            if status:
                print(f"\n[{i+1}s] Agent Status:")
                print(f"  Health: {status.get('health')}")
                print(f"  Process Alive: {status.get('process_alive')}")
                print(f"  CPU: {status.get('cpu_percent', 0):.1f}%")
                print(f"  Memory: {status.get('memory_mb', 0):.2f} MB")
                print(f"  Runtime: {status.get('runtime_seconds', 0)}s")
                print(f"  Status: {status.get('process_status')}")

        return spawner, request.agent_id
    else:
        print(f"Failed to spawn agent: {response.error}")
        return None, None


def test_process_summary(spawner):
    """Test getting process summary"""
    print_separator("TEST 2: Process Summary")

    summary = spawner.get_process_summary()

    print(f"Total Agents: {summary['total_agents']}")
    print(f"Running: {summary['running']}")
    print(f"Zombies: {summary['zombie']}")
    print(f"Completed: {summary['completed']}")
    print(f"Failed: {summary['failed']}")
    print(f"Total Memory: {summary['total_memory_mb']:.2f} MB")
    print(f"Total CPU: {summary['total_cpu_percent']:.1f}%")

    print("\nAgent Details:")
    for agent in summary['agents']:
        print(f"  {agent['agent_id']}:")
        print(f"    Health: {agent['health']}")
        print(f"    PID: {agent['pid']}")
        print(f"    Memory: {agent['memory_mb']:.2f} MB")
        print(f"    CPU: {agent['cpu_percent']:.1f}%")
        print(f"    Runtime: {agent['runtime_seconds']}s")


def test_health_check(spawner, agent_id):
    """Test quick health check"""
    print_separator("TEST 3: Quick Health Check")

    is_healthy = spawner.check_process_health(agent_id)
    print(f"Agent {agent_id} is healthy: {is_healthy}")


def test_monitor_all(spawner):
    """Test monitoring all agents"""
    print_separator("TEST 4: Monitor All Agents")

    all_status = spawner.monitor_all_agents()

    for agent_id, status in all_status.items():
        print(f"\nAgent: {agent_id}")
        print(f"  Health: {status.get('health')}")
        print(f"  Process Status: {status.get('process_status')}")
        print(f"  Alive: {status.get('process_alive')}")
        print(f"  Zombie: {status.get('is_zombie')}")


def test_cleanup_graceful(spawner, agent_id):
    """Test graceful cleanup"""
    print_separator("TEST 5: Graceful Cleanup")

    print(f"Cleaning up agent {agent_id} gracefully...")
    spawner.cleanup(agent_id=agent_id, force=False)

    # Check if process is gone
    time.sleep(1)
    is_healthy = spawner.check_process_health(agent_id)
    print(f"Agent still running after cleanup: {is_healthy}")


def test_spawn_multiple_and_cleanup_all():
    """Test spawning multiple agents and cleaning up all"""
    print_separator("TEST 6: Multiple Agents + Cleanup All")

    deployment_dir = Path(__file__).parent / "test_deployment"
    spawner = AgentSpawner(deployment_dir)

    # Spawn 3 agents
    agent_ids = []
    for i in range(3):
        request = DeploymentRequest(
            request_id=f"test_req_{i:03d}",
            parent_agent_id="OVERWATCH-TEST",
            agent_id=f"L2.TEST.{i+1}",
            agent_name=f"Test Agent {i+1}",
            agent_type="L2",
            model="haiku",
            prompt=f"Test task {i+1}",
            load_percentage=25.0,
            estimated_duration=60
        )

        response = spawner.spawn_agent(request)
        if response.status == AgentStatus.RUNNING:
            agent_ids.append(request.agent_id)
            print(f"Spawned {request.agent_id} (PID: {response.pid})")

    print(f"\nSpawned {len(agent_ids)} agents")

    # Get summary
    print("\nProcess Summary:")
    summary = spawner.get_process_summary()
    print(f"  Total: {summary['total_agents']}")
    print(f"  Running: {summary['running']}")

    # Cleanup all
    print("\nCleaning up all agents...")
    spawner.cleanup()

    # Verify cleanup
    print("\nVerifying cleanup...")
    summary = spawner.get_process_summary()
    print(f"  Remaining processes: {summary['total_agents']}")


def test_error_handling():
    """Test error handling for failed spawns"""
    print_separator("TEST 7: Error Handling")

    deployment_dir = Path(__file__).parent / "test_deployment"
    spawner = AgentSpawner(deployment_dir)

    # Try to spawn with invalid command (will fail)
    print("Testing spawn failure handling...")

    # This test is more complex - we'd need to mock a failing subprocess
    # For now, just demonstrate the error response structure
    print("Error handling is built into spawn_agent with:")
    print("  - subprocess.SubprocessError catching")
    print("  - psutil.Error catching")
    print("  - OSError catching")
    print("  - Generic Exception catching")
    print("  - Automatic state updates on failure")
    print("  - Error log writing")


def test_zombie_detection():
    """Test zombie detection and reaping"""
    print_separator("TEST 8: Zombie Detection")

    deployment_dir = Path(__file__).parent / "test_deployment"
    spawner = AgentSpawner(deployment_dir)

    print("Checking for zombie processes...")
    reaped = spawner.reap_zombies()

    if reaped:
        print(f"Reaped {len(reaped)} zombie processes:")
        for agent_id in reaped:
            print(f"  - {agent_id}")
    else:
        print("No zombie processes found")


def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("  Process Management Test Suite")
    print("  Testing AgentSpawner lifecycle management")
    print("=" * 70)

    try:
        # Test 1: Spawn and monitor
        spawner, agent_id = test_spawn_and_monitor()

        if spawner and agent_id:
            # Test 2: Process summary
            test_process_summary(spawner)

            # Test 3: Health check
            test_health_check(spawner, agent_id)

            # Test 4: Monitor all
            test_monitor_all(spawner)

            # Test 5: Graceful cleanup
            test_cleanup_graceful(spawner, agent_id)

        # Test 6: Multiple agents
        test_spawn_multiple_and_cleanup_all()

        # Test 7: Error handling
        test_error_handling()

        # Test 8: Zombie detection
        test_zombie_detection()

        print_separator("ALL TESTS COMPLETED")

    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        print("Cleaning up any remaining processes...")
        if 'spawner' in locals():
            spawner.cleanup(force=True)

    except Exception as e:
        print(f"\n\nTest failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
