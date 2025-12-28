# Ziggie Control Center - Backend API

**Version:** 1.0.0
**Architecture:** FastAPI with MongoDB backend
**Purpose:** RESTful API for Ziggie Control Center and workspace management
**Port:** 54112

---

## Overview

The Ziggie Control Center Backend is a high-performance FastAPI application that provides REST API endpoints for managing multiple workspaces, services, agents, and the knowledge base. It integrates with MongoDB for persistent storage and supports WebSocket connections for real-time updates.

## Features

- **System Monitoring**: Real-time CPU, RAM, and Disk usage monitoring
- **Service Control**: Start, stop, and monitor services (ComfyUI, Meow Ping RTS, etc.)
- **Process Management**: View running processes and their resource usage
- **Port Scanning**: Detect open ports and identify which processes are using them
- **WebSocket Support**: Real-time updates via WebSocket connections
- **MongoDB Integration**: Persistent data storage for services, agents, knowledge, API usage
- **Agent Management**: Track and invoke 584 AI agents
- **Knowledge Base Integration**: Manage automated learning system
- **Workspace Management**: Support for multiple integrated workspaces

## Installation & Setup

### Docker Setup (Recommended)

```bash
# From project root
docker-compose up -d

# Backend will be available at http://localhost:54112
```

### Local Development Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
# Create .env file
MONGODB_URI=mongodb://localhost:27017/ziggie
DATABASE_NAME=ziggie
PYTHONUNBUFFERED=1
LOG_LEVEL=INFO
```

3. Run the server:
```bash
python main.py
```

The server will start on `http://127.0.0.1:8080` (local development port)

## API Endpoints

### Root & Health

```
GET /              - API information and version
GET /health        - Health check endpoint
GET /docs          - OpenAPI/Swagger documentation
```

### System Monitoring

```
GET /api/system/stats           - Get current system statistics (CPU, RAM, Disk)
GET /api/system/processes       - List running processes
GET /api/system/ports           - List open ports and their processes
WS /api/system/ws               - WebSocket for real-time system updates (every 2 seconds)
```

### Service Control

```
GET /api/services                           - List all configured services and their status
POST /api/services/{service_name}/start     - Start a service
POST /api/services/{service_name}/stop      - Stop a service
GET /api/services/{service_name}/status     - Get service status
GET /api/services/{service_name}/logs       - Get recent service logs (query param: ?lines=100)
WS /api/services/ws                         - WebSocket for real-time service status updates
```

### Agent Management

```
GET /api/agents                      - List all agents
GET /api/agents/{agent_id}          - Get agent details
GET /api/agents/summary             - Get agent summary (tier breakdown)
POST /api/agents/{agent_id}/invoke  - Invoke an agent with a task
GET /api/agents/{agent_id}/logs     - Get agent execution logs
```

### Knowledge Base

```
GET /api/knowledge/recent                  - Get recent knowledge files
GET /api/knowledge/search?q=query          - Search knowledge base
POST /api/knowledge/update                 - Trigger knowledge base update
GET /api/knowledge/{file_id}               - Get knowledge file details
GET /api/knowledge/{file_id}/content       - Get knowledge file content
```

### Workspace Management

```
GET /api/workspaces                         - List available workspaces
GET /api/workspaces/{workspace_id}         - Get workspace details
POST /api/workspaces/{workspace_id}/sync   - Sync workspace
```

## Configuration

### Server Configuration (config.py)

```python
# Server settings
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 8080
LOG_LEVEL = "INFO"

# CORS settings
CORS_ORIGINS = ["http://localhost:3001", "http://localhost:5173"]

# Database
MONGODB_URI = "mongodb://mongo:27017/ziggie"
DATABASE_NAME = "ziggie"

# WebSocket
WS_UPDATE_INTERVAL = 2  # seconds

# Port scanning
PORT_SCAN_RANGE = (8000, 9000)
```

### Environment Variables

```bash
# Docker/Production
MONGODB_URI=mongodb://mongo:27017/ziggie
DATABASE_NAME=ziggie
PYTHONUNBUFFERED=1
LOG_LEVEL=INFO

# Local Development
MONGODB_URI=mongodb://localhost:27017/ziggie
DATABASE_NAME=ziggie_dev
LOG_LEVEL=DEBUG
```

## Managed Services

### Configured Services

1. **ComfyUI**
   - Purpose: AI image generation interface
   - Port: 8188
   - Status: Managed by Control Center

2. **Knowledge Base Scheduler**
   - Purpose: Background task scheduler for knowledge updates
   - Status: Optional background service

3. **Meow Ping RTS Backend**
   - Purpose: Game development backend
   - Port: (depends on configuration)
   - Status: Optional workspace integration

4. **Additional Workspaces**
   - Configurable in service definitions
   - Managed through Control Center UI

## Database Models

MongoDB collections for persistent data storage:

### Services Collection
```
{
  "_id": ObjectId,
  "name": "service_name",
  "display_name": "Service Display Name",
  "status": "running|stopped",
  "pid": 12345,
  "ports": [8188],
  "command": [...],
  "cwd": "/path/to/service",
  "created_at": ISODate,
  "updated_at": ISODate
}
```

### Agents Collection
```
{
  "_id": ObjectId,
  "agent_id": "01_ART_DIRECTOR",
  "name": "Art Director",
  "tier": "L1|L2|L3",
  "category": "art|design|code",
  "capabilities": [...],
  "status": "active|inactive",
  "last_invoked": ISODate,
  "invocation_count": 123
}
```

### Knowledge Files Collection
```
{
  "_id": ObjectId,
  "file_name": "knowledge_file.md",
  "source": "youtube|document|web",
  "source_id": "video_id",
  "title": "Knowledge Title",
  "content": "...",
  "tags": ["tag1", "tag2"],
  "routing": ["agent_id1", "agent_id2"],
  "created_at": ISODate,
  "updated_at": ISODate
}
```

### API Usage Collection
```
{
  "_id": ObjectId,
  "endpoint": "/api/system/stats",
  "method": "GET",
  "status_code": 200,
  "response_time_ms": 45,
  "user_agent": "Mozilla/5.0...",
  "ip_address": "127.0.0.1",
  "timestamp": ISODate
}
```

### Job History Collection
```
{
  "_id": ObjectId,
  "job_type": "knowledge_update|agent_invoke|service_start",
  "job_id": "uuid",
  "status": "pending|running|completed|failed",
  "started_at": ISODate,
  "completed_at": ISODate,
  "result": {...},
  "error": null
}
```

## WebSocket Usage

### System Stats WebSocket

```javascript
const ws = new WebSocket('ws://127.0.0.1:8080/api/system/ws');

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('System stats:', data);
};
```

### Service Status WebSocket

```javascript
const ws = new WebSocket('ws://127.0.0.1:8080/api/services/ws');

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Service status:', data);
};
```

## Development

### Project Structure

```
backend/
├── main.py                      # FastAPI application entry point
├── config.py                    # Configuration settings
├── requirements.txt             # Python dependencies
├── .env.example                 # Example environment variables
├── api/
│   ├── __init__.py
│   ├── system.py               # System monitoring endpoints
│   ├── services.py             # Service control endpoints
│   ├── agents.py               # Agent management endpoints
│   ├── knowledge.py            # Knowledge base endpoints
│   └── workspaces.py           # Workspace management endpoints
├── services/
│   ├── __init__.py
│   ├── process_manager.py      # Process control logic
│   ├── port_scanner.py         # Port scanning logic
│   ├── agent_service.py        # Agent management service
│   └── knowledge_service.py    # Knowledge base service
├── database/
│   ├── __init__.py
│   ├── db.py                   # MongoDB connection & session
│   ├── models.py               # Pydantic models
│   └── collections.py          # MongoDB collections
└── logs/                        # Service logs (created at runtime)
```

### Adding New API Endpoints

1. Create endpoint file in `api/`:
```python
# api/my_endpoint.py
from fastapi import APIRouter, HTTPException
from typing import List, Optional

router = APIRouter(prefix="/api/myendpoint", tags=["my-endpoint"])

@router.get("/")
async def get_data():
    return {"data": "value"}

@router.post("/{item_id}")
async def create_item(item_id: str):
    return {"item_id": item_id, "status": "created"}
```

2. Include router in `main.py`:
```python
from api import my_endpoint
app.include_router(my_endpoint.router)
```

### Adding New Services

Edit `config.py` and add to the services configuration:

```python
SERVICES = {
    "my_service": {
        "name": "My Service",
        "display_name": "My Custom Service",
        "command": ["python", "script.py"],
        "cwd": r"C:\path\to\service",
        "port": 3000,
        "log_file": "my_service.log"
    }
}
```

## Error Handling

All endpoints include proper error handling and return consistent responses:

### Success Response
```json
{
    "success": true,
    "data": {
        "id": "service_id",
        "status": "running",
        "port": 8188
    }
}
```

### Error Response
```json
{
    "success": false,
    "error": "Service not found",
    "status_code": 404
}
```

## Deployment

### Docker Production Deployment

```bash
# Build image
docker build -t ziggie-backend .

# Run container
docker run -p 54112:8080 \
  -e MONGODB_URI=mongodb://mongo:27017/ziggie \
  -e LOG_LEVEL=INFO \
  ziggie-backend
```

### Environment-Specific Configuration

```bash
# Development
export ENVIRONMENT=development
export LOG_LEVEL=DEBUG

# Production
export ENVIRONMENT=production
export LOG_LEVEL=INFO
```

## Troubleshooting

### MongoDB Connection Issues

```bash
# Check MongoDB connection
python -c "from pymongo import MongoClient; print(MongoClient('mongodb://localhost:27017').admin.command('ping'))"

# Reset MongoDB
docker-compose down -v
docker-compose up -d
```

### Port Already in Use

```bash
# Find process using port 54112
netstat -ano | findstr :54112

# Kill process
taskkill /PID <PID> /F
```

### Import Errors

```bash
# Reinstall dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Check Python version (must be 3.11+)
python --version
```

### WebSocket Connection Issues

```bash
# Check WebSocket connectivity
python -c "import asyncio; from fastapi import WebSocket; print('WebSocket module OK')"
```

## Performance Optimization

- Response times: <500ms for most endpoints
- WebSocket updates: Every 2 seconds
- Database queries: Indexed collections
- Process monitoring: Efficient subprocess handling
- Memory usage: Optimized for long-running processes

## Dependencies

Key Python packages:
- **fastapi** - Web framework
- **pymongo** - MongoDB driver
- **pydantic** - Data validation
- **python-multipart** - Form data handling
- **psutil** - System monitoring
- **python-socketio** - WebSocket support

See `requirements.txt` for complete list.

## API Rate Limiting (Future)

Consider implementing rate limiting for production:

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.get("/api/endpoint")
@limiter.limit("100/minute")
async def limited_endpoint():
    return {"status": "ok"}
```

## License

Part of Ziggie Control Center project. MIT License.

---

## Support & Resources

- **API Documentation:** http://localhost:54112/docs
- **Main Project:** `README.md` in project root
- **Control Center:** `control-center/README.md`
- **Frontend:** `control-center/frontend/README.md`

---

**Ziggie Control Center Backend API**

*For local development: `python main.py`*
*For Docker: `docker-compose up -d`*
*Access API docs: http://localhost:54112/docs*
