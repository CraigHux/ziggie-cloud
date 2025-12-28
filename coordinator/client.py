"""
Agent Deployment Client
Library for agents to deploy sub-agents
"""

import json
import time
import uuid
from pathlib import Path
from typing import Optional
from datetime import datetime
from .schemas import DeploymentRequest, DeploymentResponse, AgentStatus


class AgentDeploymentClient:
    """Client for deploying agents from within an agent"""

    def __init__(self, deployment_dir: Path, parent_agent_id: str):
        self.deployment_dir = Path(deployment_dir)
        self.parent_agent_id = parent_agent_id
        self.requests_dir = self.deployment_dir / "requests"
        self.responses_dir = self.deployment_dir / "responses"

        # Ensure directories exist
        self.requests_dir.mkdir(parents=True, exist_ok=True)
        self.responses_dir.mkdir(parents=True, exist_ok=True)

    def deploy_agent(
        self,
        agent_id: str,
        agent_name: str,
        agent_type: str,
        prompt: str,
        model: str = "haiku",
        load_percentage: float = 0.0,
        estimated_duration: Optional[int] = None,
        metadata: Optional[dict] = None,
        timeout: int = 30
    ) -> DeploymentResponse:
        """
        Deploy a new agent

        Args:
            agent_id: Unique ID for the agent (e.g., "L2.10.1")
            agent_name: Human-readable name
            agent_type: Agent type (L1/L2/L3)
            prompt: Task prompt for the agent
            model: Model to use (haiku/sonnet)
            load_percentage: % of total workload
            estimated_duration: Estimated seconds to complete
            metadata: Additional metadata
            timeout: Seconds to wait for response

        Returns:
            DeploymentResponse with status
        """
        # Generate request ID
        request_id = f"req_{uuid.uuid4().hex[:8]}"

        # Create request
        request = DeploymentRequest(
            request_id=request_id,
            parent_agent_id=self.parent_agent_id,
            agent_id=agent_id,
            agent_name=agent_name,
            agent_type=agent_type,
            model=model,
            prompt=prompt,
            load_percentage=load_percentage,
            estimated_duration=estimated_duration,
            metadata=metadata or {}
        )

        # Write request file
        request_file = self.requests_dir / f"{request_id}.json"
        request_file.write_text(request.model_dump_json(indent=2), encoding='utf-8')

        print(f"[{datetime.now().strftime('%H:%M:%S')}] Deployment request submitted: {agent_id}")

        # Wait for response
        response_file = self.responses_dir / f"{request_id}_response.json"
        start_time = time.time()

        while time.time() - start_time < timeout:
            if response_file.exists():
                response_data = json.loads(response_file.read_text())
                response = DeploymentResponse(**response_data)
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Deployment response received: {agent_id} - {response.status}")
                return response

            time.sleep(0.5)

        # Timeout
        return DeploymentResponse(
            request_id=request_id,
            agent_id=agent_id,
            status=AgentStatus.FAILED,
            message="Deployment timeout",
            error=f"No response received within {timeout} seconds"
        )

    def get_agent_status(self, agent_id: str) -> Optional[dict]:
        """Get status of a deployed agent"""
        # Check if agent status file exists
        agent_dir = self.deployment_dir / "agents" / agent_id
        status_file = agent_dir / "status.json"

        if status_file.exists():
            return json.loads(status_file.read_text())
        return None

    def list_my_agents(self):
        """List all agents deployed by this parent"""
        agents_dir = self.deployment_dir / "agents"
        if not agents_dir.exists():
            return []

        my_agents = []
        for agent_dir in agents_dir.iterdir():
            if agent_dir.is_dir():
                status = self.get_agent_status(agent_dir.name)
                if status:
                    my_agents.append(status)

        return my_agents
