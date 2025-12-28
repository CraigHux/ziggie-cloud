"""
ZIGGIE Agent Deployment Coordinator
File-Based MVP for hierarchical agent deployment
"""

__version__ = "1.0.0"
__author__ = "ZIGGIE AI System"

from .client import AgentDeploymentClient
from .watcher import DeploymentWatcher
from .schemas import (
    DeploymentRequest,
    DeploymentResponse,
    AgentStatus,
    AgentType
)

__all__ = [
    "AgentDeploymentClient",
    "DeploymentWatcher",
    "DeploymentRequest",
    "DeploymentResponse",
    "AgentStatus",
    "AgentType",
]
