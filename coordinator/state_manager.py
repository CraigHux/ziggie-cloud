"""
State Manager for Agent Coordinator
Handles persistence and recovery of agent state across restarts
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from .schemas import DeploymentRequest, DeploymentResponse, AgentStatus


class StateManager:
    """Manages persistent state for agents"""

    def __init__(self, deployment_dir: Path):
        self.deployment_dir = deployment_dir
        self.state_dir = deployment_dir / "state"
        self.state_dir.mkdir(parents=True, exist_ok=True)

        # Active agents tracking
        self.active_agents: Dict[str, dict] = {}

    def save_agent_state(self, agent_id: str, state_data: dict):
        """
        Save agent state to persistent storage

        Args:
            agent_id: Unique agent identifier
            state_data: Dictionary containing agent state
        """
        state_file = self.state_dir / f"{agent_id}.json"

        # Add timestamp
        state_data["last_updated"] = datetime.now().isoformat()

        # Write to file
        state_file.write_text(json.dumps(state_data, indent=2))

        # Update in-memory cache
        self.active_agents[agent_id] = state_data

    def load_agent_state(self, agent_id: str) -> Optional[dict]:
        """
        Load agent state from persistent storage

        Args:
            agent_id: Unique agent identifier

        Returns:
            Agent state dictionary or None if not found
        """
        state_file = self.state_dir / f"{agent_id}.json"

        if not state_file.exists():
            return None

        try:
            state_data = json.loads(state_file.read_text())
            return state_data
        except Exception as e:
            print(f"Error loading state for {agent_id}: {e}")
            return None

    def get_all_agent_states(self) -> Dict[str, dict]:
        """
        Load all agent states from persistent storage

        Returns:
            Dictionary mapping agent_id to state data
        """
        all_states = {}

        for state_file in self.state_dir.glob("*.json"):
            agent_id = state_file.stem
            state_data = self.load_agent_state(agent_id)
            if state_data:
                all_states[agent_id] = state_data

        return all_states

    def get_incomplete_agents(self) -> List[dict]:
        """
        Find agents that didn't complete (for recovery)

        Returns:
            List of agent state dictionaries that are incomplete
        """
        all_states = self.get_all_agent_states()
        incomplete = []

        for agent_id, state in all_states.items():
            status = state.get("status", "")
            if status in ["pending", "spawning", "running"]:
                incomplete.append(state)

        return incomplete

    def mark_agent_completed(self, agent_id: str):
        """
        Mark agent as completed in persistent storage

        Args:
            agent_id: Unique agent identifier
        """
        state = self.load_agent_state(agent_id)
        if state:
            state["status"] = "completed"
            state["completed_at"] = datetime.now().isoformat()
            self.save_agent_state(agent_id, state)

    def mark_agent_failed(self, agent_id: str, error: str):
        """
        Mark agent as failed in persistent storage

        Args:
            agent_id: Unique agent identifier
            error: Error message
        """
        state = self.load_agent_state(agent_id)
        if state:
            state["status"] = "failed"
            state["error"] = error
            state["failed_at"] = datetime.now().isoformat()
            self.save_agent_state(agent_id, state)

    def update_agent_progress(self, agent_id: str, progress: int, message: str = ""):
        """
        Update agent progress

        Args:
            agent_id: Unique agent identifier
            progress: Progress percentage (0-100)
            message: Optional progress message
        """
        state = self.load_agent_state(agent_id)
        if state:
            state["progress"] = progress
            if message:
                state["progress_message"] = message
            self.save_agent_state(agent_id, state)

    def delete_agent_state(self, agent_id: str):
        """
        Delete agent state (cleanup after completion)

        Args:
            agent_id: Unique agent identifier
        """
        state_file = self.state_dir / f"{agent_id}.json"
        if state_file.exists():
            state_file.unlink()

        if agent_id in self.active_agents:
            del self.active_agents[agent_id]

    def create_agent_state(self, request: DeploymentRequest, response: DeploymentResponse) -> dict:
        """
        Create initial agent state from deployment request/response

        Args:
            request: Deployment request
            response: Deployment response

        Returns:
            Initial state dictionary
        """
        state = {
            "agent_id": request.agent_id,
            "agent_name": request.agent_name,
            "agent_type": request.agent_type,
            "parent_agent_id": request.parent_agent_id,
            "model": request.model,
            "prompt": request.prompt,
            "load_percentage": request.load_percentage,
            "estimated_duration": request.estimated_duration,
            "metadata": request.metadata,
            "status": response.status.value,
            "pid": response.pid,
            "started_at": response.started_at.isoformat() if response.started_at else None,
            "progress": 0,
            "created_at": datetime.now().isoformat(),
        }

        return state

    def get_recovery_summary(self) -> dict:
        """
        Get summary of agents that need recovery

        Returns:
            Dictionary with recovery statistics
        """
        incomplete = self.get_incomplete_agents()

        summary = {
            "total_incomplete": len(incomplete),
            "by_status": {},
            "by_type": {},
            "agents": incomplete
        }

        # Count by status
        for agent in incomplete:
            status = agent.get("status", "unknown")
            summary["by_status"][status] = summary["by_status"].get(status, 0) + 1

            agent_type = agent.get("agent_type", "unknown")
            summary["by_type"][agent_type] = summary["by_type"].get(agent_type, 0) + 1

        return summary

    def cleanup_completed_agents(self, keep_days: int = 7):
        """
        Clean up state files for completed agents older than keep_days

        Args:
            keep_days: Number of days to keep completed agent states
        """
        from datetime import timedelta

        cutoff_date = datetime.now() - timedelta(days=keep_days)

        for state_file in self.state_dir.glob("*.json"):
            try:
                state = json.loads(state_file.read_text())

                # Only delete completed or failed agents
                if state.get("status") not in ["completed", "failed"]:
                    continue

                # Check completion date
                completed_at = state.get("completed_at") or state.get("failed_at")
                if completed_at:
                    completed_date = datetime.fromisoformat(completed_at)
                    if completed_date < cutoff_date:
                        state_file.unlink()
                        print(f"Cleaned up state for {state.get('agent_id')}")

            except Exception as e:
                print(f"Error cleaning up {state_file}: {e}")
