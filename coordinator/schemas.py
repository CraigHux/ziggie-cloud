"""
Agent Deployment Schemas
Data models for agent deployment requests and responses
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class AgentStatus(str, Enum):
    """Agent status states"""
    PENDING = "pending"
    SPAWNING = "spawning"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AgentType(str, Enum):
    """Agent hierarchy types"""
    L1 = "L1"
    L2 = "L2"
    L3 = "L3"


class DeploymentRequest(BaseModel):
    """Agent deployment request schema"""
    request_id: str = Field(..., description="Unique request ID")
    parent_agent_id: str = Field(..., description="ID of agent making request")
    agent_id: str = Field(..., description="ID for new agent")
    agent_name: str = Field(..., description="Human-readable agent name")
    agent_type: str = Field(..., description="Agent type (L1/L2/L3)")
    model: str = Field(default="haiku", description="Model to use (haiku/sonnet)")
    prompt: str = Field(..., description="Task prompt for agent")
    load_percentage: float = Field(..., description="% of total workload")
    estimated_duration: Optional[int] = Field(None, description="Estimated seconds")
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        json_schema_extra = {
            "example": {
                "request_id": "req_001",
                "parent_agent_id": "OVERWATCH-002",
                "agent_id": "L2.10.1",
                "agent_name": "Infrastructure Builder",
                "agent_type": "L2",
                "model": "haiku",
                "prompt": "Build infrastructure for monitoring system...",
                "load_percentage": 33.3,
                "estimated_duration": 300,
                "metadata": {"priority": "high"}
            }
        }


class DeploymentResponse(BaseModel):
    """Agent deployment response schema"""
    request_id: str
    agent_id: str
    status: AgentStatus
    pid: Optional[int] = None
    started_at: Optional[datetime] = None
    message: str = ""
    error: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "request_id": "req_001",
                "agent_id": "L2.10.1",
                "status": "running",
                "pid": 12345,
                "started_at": "2025-11-09T15:50:00",
                "message": "Agent deployed successfully"
            }
        }


class AgentStatusUpdate(BaseModel):
    """Agent status update from running agent"""
    agent_id: str
    status: AgentStatus
    progress: int = Field(0, ge=0, le=100, description="Progress percentage")
    current_task: str = ""
    tasks_completed: int = 0
    tasks_total: int = 0
    last_update: datetime = Field(default_factory=datetime.now)
    error: Optional[str] = None


class AgentCompletionReport(BaseModel):
    """Agent completion report summary"""
    agent_id: str
    agent_name: str
    status: AgentStatus
    start_time: datetime
    end_time: datetime
    duration_seconds: int
    tasks_completed: int
    tasks_total: int
    files_processed: List[str] = Field(default_factory=list)
    issues: List[str] = Field(default_factory=list)
    report_file: str = ""
