# ZIGGIE Agent Deployment Coordinator

**File-Based MVP v1.0**

Enables hierarchical agent deployment where Overwatch agents can deploy L2 worker agents.

## Architecture

```
Ziggie (Top-Level - Strategic Analysis)
    ↓
Overwatch Agent (Tactical Coordination)
    ↓
File-Based Coordinator Service
    ↓
L2 Worker Agents (Task Execution)
```

## How It Works

1. **Overwatch agent** uses `AgentDeploymentClient` to create deployment requests
2. **Coordinator service** watches the `requests/` directory using `watchdog`
3. When a new request JSON file appears, **coordinator spawns the agent**
4. **Response** is written to `responses/` directory
5. **Overwatch agent** receives the deployment response and continues coordination

## Installation

```bash
cd C:\Ziggie\coordinator
pip install -r requirements.txt
```

## Usage

### 1. Start the Coordinator Service

```bash
python -m coordinator.main
```

You should see:
```
============================================================
ZIGGIE Agent Deployment Coordinator
File-Based MVP v1.0
============================================================
Deployment Directory: C:\Ziggie\agent-deployment
Log Directory: C:\Ziggie\agent-deployment\logs
[COORDINATOR] Starting deployment watcher...
[COORDINATOR] Monitoring: C:\Ziggie\agent-deployment\requests
[COORDINATOR] Watcher started successfully
```

### 2. Deploy Agents from Overwatch

In your Overwatch agent code:

```python
from coordinator.client import AgentDeploymentClient

# Initialize client
client = AgentDeploymentClient(
    deployment_dir=Path("C:/Ziggie/agent-deployment"),
    parent_agent_id="L1.OVERWATCH.1"
)

# Deploy L2 worker
response = client.deploy_agent(
    agent_id="L2.1.1",
    agent_name="Configuration Fixer",
    agent_type="L2",
    prompt="Fix the Control Center configuration files...",
    model="haiku",
    load_percentage=33.3,
    estimated_duration=60
)

if response.status == "running":
    print(f"✓ Agent deployed successfully (PID: {response.pid})")
else:
    print(f"✗ Deployment failed: {response.error}")
```

### 3. Monitor Agent Status

```python
# Check specific agent status
status = client.get_agent_status("L2.1.1")
print(status)

# List all deployed agents
agents = client.list_my_agents()
for agent in agents:
    print(f"{agent['agent_id']}: {agent['status']}")
```

## Testing

### Basic Integration Test

```bash
# Start coordinator in one terminal
python -m coordinator.main

# Run test in another terminal
python coordinator/test_basic.py
```

### Example Overwatch Mission

```bash
python coordinator/example_overwatch.py
```

## File Structure

```
C:\Ziggie\
├── coordinator/
│   ├── __init__.py           # Package initialization
│   ├── main.py               # Entry point
│   ├── schemas.py            # Pydantic data models
│   ├── agent_spawner.py      # Process management
│   ├── watcher.py            # File monitoring
│   ├── client.py             # Deployment client library
│   ├── requirements.txt      # Dependencies
│   ├── test_basic.py         # Basic integration test
│   ├── example_overwatch.py  # Example Overwatch usage
│   └── README.md             # This file
│
└── agent-deployment/
    ├── requests/              # Deployment requests (JSON)
    ├── responses/             # Deployment responses (JSON)
    ├── agents/                # Agent working directories
    │   └── {agent_id}/
    │       ├── prompt.txt     # Agent task prompt
    │       └── status.json    # Agent status
    └── logs/                  # Coordinator logs
```

## Data Models

### DeploymentRequest

```python
{
    "request_id": "req_a1b2c3d4",
    "parent_agent_id": "L1.OVERWATCH.1",
    "agent_id": "L2.1.1",
    "agent_name": "Configuration Fixer",
    "agent_type": "L2",
    "model": "haiku",
    "prompt": "Fix the configuration...",
    "load_percentage": 33.3,
    "estimated_duration": 60,
    "metadata": {}
}
```

### DeploymentResponse

```python
{
    "request_id": "req_a1b2c3d4",
    "agent_id": "L2.1.1",
    "status": "running",
    "pid": 12345,
    "started_at": "2025-01-15T14:30:00",
    "message": "Agent deployed successfully",
    "error": null
}
```

## Agent Status Values

- `pending` - Request submitted, not yet processed
- `spawning` - Agent process is being created
- `running` - Agent is actively working
- `completed` - Agent finished successfully
- `failed` - Agent encountered an error
- `cancelled` - Deployment was cancelled

## Protocol v1.3 Integration

This MVP supports Protocol v1.3 hierarchical deployment:

- **Phase 6b:** Overwatch uses `deploy_agent()` to spawn L2 workers
- **Phase 7:** L2 workers execute tasks independently
- **Phase 8:** Overwatch monitors status via `get_agent_status()`
- **Phase 9a:** Overwatch aggregates results from all L2 workers

## Future: REST API Version

After MVP validation, the production version will include:

- FastAPI REST endpoints (`POST /agents/deploy`, `GET /agents/{id}`)
- Control Center dashboard integration
- MongoDB state persistence
- WebSocket real-time updates
- Enhanced process monitoring with `psutil`

## Troubleshooting

**Coordinator not detecting requests:**
- Verify coordinator is running: Check for "Watcher started successfully"
- Check file permissions on `agent-deployment/` directory
- Ensure watchdog is installed: `pip install watchdog`

**Deployment timeout:**
- Increase timeout parameter: `deploy_agent(..., timeout=60)`
- Check coordinator logs in `agent-deployment/logs/`
- Verify no Python errors in coordinator terminal

**Agent not spawning:**
- Check `agent_spawner.py` is creating directories correctly
- Verify Claude Code CLI is accessible (for production version)
- Review error in deployment response: `response.error`

## Contributing

This is the File-Based MVP. Production version will be developed after validation.

For questions or issues, check coordinator logs or agent completion reports.

---

**Built by:** ZIGGIE AI System (L1.1, L1.2, L1.3 Architecture Team)
**Version:** 1.0.0 (File-Based MVP)
**Date:** January 2025
