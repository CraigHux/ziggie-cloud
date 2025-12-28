"""
Recovery Tool for Agent Coordinator
Check and manage incomplete agents after interruptions
"""

import argparse
from pathlib import Path
from state_manager import StateManager


def main():
    """Main entry point for recovery tool"""
    parser = argparse.ArgumentParser(description="Agent Coordinator Recovery Tool")
    parser.add_argument(
        "--deployment-dir",
        type=str,
        default="agent-deployment",
        help="Deployment directory path"
    )
    parser.add_argument(
        "--action",
        choices=["check", "list", "clear"],
        default="check",
        help="Action to perform"
    )
    parser.add_argument(
        "--agent-id",
        type=str,
        help="Specific agent ID to operate on"
    )

    args = parser.parse_args()

    # Resolve deployment directory
    deployment_dir = Path(__file__).parent.parent / args.deployment_dir
    if not deployment_dir.exists():
        print(f"Deployment directory not found: {deployment_dir}")
        return

    # Initialize state manager
    state_manager = StateManager(deployment_dir)

    # Perform action
    if args.action == "check":
        check_recovery(state_manager)
    elif args.action == "list":
        list_incomplete(state_manager)
    elif args.action == "clear":
        clear_incomplete(state_manager, args.agent_id)


def check_recovery(state_manager: StateManager):
    """Check recovery status"""
    print("=" * 60)
    print("AGENT COORDINATOR RECOVERY CHECK")
    print("=" * 60)

    summary = state_manager.get_recovery_summary()

    print(f"\nTotal Incomplete Agents: {summary['total_incomplete']}")

    if summary['total_incomplete'] > 0:
        print("\nBy Status:")
        for status, count in summary['by_status'].items():
            print(f"  - {status}: {count}")

        print("\nBy Type:")
        for agent_type, count in summary['by_type'].items():
            print(f"  - {agent_type}: {count}")

        print("\n" + "=" * 60)
        print("RECOVERY ACTIONS:")
        print("=" * 60)
        print("1. Restart coordinator - agents will be detected on startup")
        print("2. Review agent states: python -m coordinator.recovery --action list")
        print("3. Clear states if needed: python -m coordinator.recovery --action clear")
    else:
        print("\nNo incomplete agents found.")
        print("All agents completed successfully or no agents have run.")

    print("\n" + "=" * 60)


def list_incomplete(state_manager: StateManager):
    """List all incomplete agents with details"""
    print("=" * 60)
    print("INCOMPLETE AGENTS")
    print("=" * 60)

    incomplete = state_manager.get_incomplete_agents()

    if not incomplete:
        print("\nNo incomplete agents found.")
        return

    for i, agent in enumerate(incomplete, 1):
        print(f"\n[{i}] Agent ID: {agent.get('agent_id')}")
        print(f"    Name: {agent.get('agent_name')}")
        print(f"    Type: {agent.get('agent_type')}")
        print(f"    Status: {agent.get('status')}")
        print(f"    Started: {agent.get('started_at')}")
        print(f"    Progress: {agent.get('progress', 0)}%")
        print(f"    Parent: {agent.get('parent_agent_id')}")

        if agent.get('progress_message'):
            print(f"    Message: {agent.get('progress_message')}")

    print("\n" + "=" * 60)
    print(f"Total: {len(incomplete)} incomplete agents")
    print("=" * 60)


def clear_incomplete(state_manager: StateManager, agent_id: str = None):
    """Clear incomplete agent states"""
    if agent_id:
        # Clear specific agent
        state = state_manager.load_agent_state(agent_id)
        if state:
            if state.get('status') in ['pending', 'spawning', 'running']:
                state_manager.delete_agent_state(agent_id)
                print(f"Cleared state for agent: {agent_id}")
            else:
                print(f"Agent {agent_id} is already {state.get('status')}")
        else:
            print(f"Agent {agent_id} not found")
    else:
        # Clear all incomplete agents
        incomplete = state_manager.get_incomplete_agents()

        if not incomplete:
            print("No incomplete agents to clear.")
            return

        print(f"Found {len(incomplete)} incomplete agents.")
        confirm = input("Clear all incomplete agent states? (yes/no): ")

        if confirm.lower() == "yes":
            for agent in incomplete:
                agent_id = agent.get('agent_id')
                state_manager.delete_agent_state(agent_id)
                print(f"Cleared state for agent: {agent_id}")
            print(f"\nCleared {len(incomplete)} agent states.")
        else:
            print("Cancelled.")


if __name__ == "__main__":
    main()
