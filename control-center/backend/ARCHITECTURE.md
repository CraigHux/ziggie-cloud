# Control Center Backend - Architecture Overview

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         FRONTEND (React)                            │
│                    http://localhost:3000                            │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             │ HTTP/WebSocket
                             │ CORS Enabled
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    FASTAPI BACKEND SERVER                           │
│                   http://127.0.0.1:8080                             │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────┐     │
│  │                     main.py                               │     │
│  │  - FastAPI Application                                    │     │
│  │  - CORS Middleware                                        │     │
│  │  - Router Registration                                    │     │
│  │  - Lifespan Management                                    │     │
│  └──────────────────────────────────────────────────────────┘     │
│                             │                                       │
│         ┌───────────────────┼───────────────────┐                  │
│         ▼                   ▼                   ▼                  │
│  ┌──────────┐       ┌──────────┐       ┌──────────┐               │
│  │  System  │       │ Services │       │Knowledge │               │
│  │   API    │       │   API    │       │  Base    │               │
│  │          │       │          │       │   API    │               │
│  └────┬─────┘       └────┬─────┘       └────┬─────┘               │
│       │                  │                   │                     │
│       │ Uses             │ Uses              │ Uses                │
│       ▼                  ▼                   ▼                     │
│  ┌──────────┐       ┌──────────┐       ┌──────────┐               │
│  │  Port    │       │ Process  │       │   File   │               │
│  │ Scanner  │       │ Manager  │       │ Scanner  │               │
│  └──────────┘       └────┬─────┘       └──────────┘               │
│                           │                                        │
│                           │ Manages                                │
│                           ▼                                        │
│                    ┌──────────────┐                                │
│                    │  SERVICES    │                                │
│                    │              │                                │
│                    │  - ComfyUI   │                                │
│                    │  - KB Sched  │                                │
│                    └──────────────┘                                │
└─────────────────────────────────────────────────────────────────────┘
                             │
                             │ Reads/Writes
                             ▼
                    ┌──────────────┐
                    │   SQLite DB  │
                    │              │
                    │  - Services  │
                    │  - Agents    │
                    │  - KB Files  │
                    │  - API Usage │
                    │  - Jobs      │
                    └──────────────┘
```

## Request Flow

### REST API Request
```
Client Request
    ▼
FastAPI Router
    ▼
API Endpoint (system.py / services.py / knowledge.py)
    ▼
Service Layer (process_manager.py / port_scanner.py)
    ▼
External System (psutil / subprocess / file system)
    ▼
Response Formatting
    ▼
JSON Response to Client
```

### WebSocket Connection
```
Client WebSocket Connect
    ▼
Connection Manager (accepts connection)
    ▼
Add to Active Connections List
    ▼
Periodic Update Loop (every 2 seconds)
    ▼
Fetch Current Data (CPU, RAM, Services)
    ▼
Broadcast to All Connected Clients
    ▼
Client Receives Real-Time Update
```

## Module Structure

```
backend/
│
├── Application Layer
│   └── main.py
│       - FastAPI app initialization
│       - Middleware configuration
│       - Router registration
│       - Lifespan events
│
├── Configuration Layer
│   └── config.py
│       - Settings class (Pydantic)
│       - Service definitions
│       - Path configurations
│       - Environment variables
│
├── API Layer (api/)
│   ├── system.py
│   │   - System monitoring endpoints
│   │   - Process listing
│   │   - Port scanning
│   │   - WebSocket for real-time stats
│   │
│   ├── services.py
│   │   - Service control endpoints
│   │   - Start/stop services
│   │   - Status checks
│   │   - Log retrieval
│   │   - WebSocket for service status
│   │
│   └── knowledge.py
│       - Knowledge base endpoints
│       - File management
│       - Creator database
│       - Search functionality
│
├── Service Layer (services/)
│   ├── process_manager.py
│   │   - Start/stop processes
│   │   - Monitor process status
│   │   - Manage log files
│   │   - Track running processes
│   │
│   └── port_scanner.py
│       - Scan port range
│       - Identify port owners
│       - Check availability
│       - Resolve process names
│
└── Database Layer (database/)
    ├── db.py
    │   - Async engine creation
    │   - Session factory
    │   - Database initialization
    │   - Session dependency
    │
    └── models.py
        - SQLAlchemy models
        - Table definitions
        - Relationships
        - Timestamps
```

## Data Flow Diagrams

### System Monitoring Flow
```
┌─────────┐
│ Client  │
└────┬────┘
     │ GET /api/system/stats
     ▼
┌──────────────┐
│  system.py   │
└──────┬───────┘
       │
       ├── psutil.cpu_percent() ──────┐
       ├── psutil.virtual_memory() ───┤
       └── psutil.disk_usage() ────────┤
                                       │
                              ┌────────▼────────┐
                              │  Format Response │
                              │  {cpu, mem, disk}│
                              └────────┬─────────┘
                                       │
                                       ▼
                              ┌─────────────────┐
                              │  JSON Response  │
                              └─────────────────┘
```

### Service Control Flow
```
┌─────────┐
│ Client  │
└────┬────┘
     │ POST /api/services/comfyui/start
     ▼
┌──────────────┐
│ services.py  │
└──────┬───────┘
       │ ProcessManager.start_service()
       ▼
┌─────────────────┐
│process_manager.py│
└──────┬──────────┘
       │
       ├── Create log file handle
       ├── subprocess.Popen(command)
       ├── Track in _processes dict
       └── Verify process started
       │
       ▼
┌──────────────┐
│   ComfyUI    │  (External Process)
│  Running on  │
│  Port 8188   │
└──────────────┘
       │
       │ stdout/stderr
       ▼
┌──────────────┐
│  Log File    │
└──────────────┘
```

### WebSocket Real-Time Updates
```
┌─────────┐
│ Client  │
└────┬────┘
     │ WS Connect /api/system/ws
     ▼
┌──────────────┐
│ Connection   │
│  Manager     │
└──────┬───────┘
       │ Add to active_connections[]
       │
       ▼
┌──────────────┐
│ Update Loop  │ (Every 2 seconds)
└──────┬───────┘
       │
       ├── Fetch current stats
       ├── Create JSON message
       └── Broadcast to all clients
       │
       ▼
┌─────────┐
│ Client  │ (Receives update)
└─────────┘
```

## Database Schema

```
┌─────────────────────────┐
│       Services          │
├─────────────────────────┤
│ id (PK)                 │
│ name                    │
│ status                  │
│ port                    │
│ pid                     │
│ command                 │
│ created_at              │
│ updated_at              │
└─────────────────────────┘

┌─────────────────────────┐       ┌─────────────────────────┐
│        Agents           │       │   KnowledgeFiles        │
├─────────────────────────┤       ├─────────────────────────┤
│ id (PK)                 │───┐   │ id (PK)                 │
│ name                    │   │   │ agent_id (FK)           │
│ level                   │   └──▶│ file_path               │
│ category                │       │ confidence              │
│ created_at              │       │ created_at              │
└─────────────────────────┘       └─────────────────────────┘

┌─────────────────────────┐       ┌─────────────────────────┐
│       APIUsage          │       │      JobHistory         │
├─────────────────────────┤       ├─────────────────────────┤
│ id (PK)                 │       │ id (PK)                 │
│ service                 │       │ job_type                │
│ cost                    │       │ status                  │
│ calls                   │       │ started_at              │
│ date                    │       │ completed_at            │
└─────────────────────────┘       │ result                  │
                                  └─────────────────────────┘
```

## API Endpoint Map

```
http://127.0.0.1:8080
│
├── /                              [GET]  Root info
├── /health                        [GET]  Health check
├── /docs                          [GET]  Swagger UI
├── /redoc                         [GET]  ReDoc
│
├── /api/system/
│   ├── /stats                     [GET]  CPU, RAM, Disk
│   ├── /processes                 [GET]  Process list
│   ├── /ports                     [GET]  Port scan
│   └── /ws                        [WS]   Real-time stats
│
├── /api/services/
│   ├── /                          [GET]  List all services
│   ├── /{service_name}/start      [POST] Start service
│   ├── /{service_name}/stop       [POST] Stop service
│   ├── /{service_name}/status     [GET]  Service status
│   ├── /{service_name}/logs       [GET]  Service logs
│   └── /ws                        [WS]   Real-time status
│
└── /api/knowledge/
    ├── /stats                     [GET]  KB statistics
    ├── /files                     [GET]  File listing
    ├── /files/{file_id}           [GET]  File details
    ├── /creators                  [GET]  Creator list
    ├── /creators/{creator_id}     [GET]  Creator details
    ├── /scan                      [POST] Trigger scan
    ├── /jobs                      [GET]  Job history
    └── /search                    [GET]  Search KB
```

## Technology Stack

```
┌─────────────────────────────────────────────────────────┐
│                    PRESENTATION                         │
│                                                         │
│  FastAPI 0.109.0  │  Swagger UI  │  ReDoc              │
└─────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────┐
│                    APPLICATION                          │
│                                                         │
│  Python 3.8+  │  Async/Await  │  Type Hints            │
└─────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────┐
│                    MIDDLEWARE                           │
│                                                         │
│  CORS  │  WebSocket  │  Pydantic Validation           │
└─────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────┐
│                      SERVICES                           │
│                                                         │
│  psutil  │  subprocess  │  asyncio                     │
└─────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────┐
│                       DATA                              │
│                                                         │
│  SQLAlchemy 2.0  │  aiosqlite  │  SQLite              │
└─────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────┐
│                    INFRASTRUCTURE                       │
│                                                         │
│  Uvicorn  │  Windows OS  │  File System                │
└─────────────────────────────────────────────────────────┘
```

## Async Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  ASYNC EVENT LOOP                       │
│                  (asyncio)                              │
└─────────────────────────────────────────────────────────┘
            │                    │                    │
            ▼                    ▼                    ▼
    ┌─────────────┐      ┌─────────────┐     ┌─────────────┐
    │   HTTP      │      │  WebSocket  │     │  Database   │
    │  Requests   │      │ Connections │     │  Operations │
    └─────────────┘      └─────────────┘     └─────────────┘
            │                    │                    │
            ▼                    ▼                    ▼
    Non-blocking I/O     Non-blocking I/O    Non-blocking I/O
    await response       await broadcast     await query

    - No threads needed
    - High concurrency
    - Low memory footprint
    - Single-threaded efficiency
```

## Security Model

```
┌─────────────────────────────────────────────────────────┐
│                    SECURITY LAYERS                      │
└─────────────────────────────────────────────────────────┘

Layer 1: Network Isolation
    ├── Server binds to 127.0.0.1 only
    └── No external access possible

Layer 2: CORS Protection
    ├── Only localhost:3000 allowed
    └── Credentials restricted

Layer 3: Input Validation
    ├── Pydantic models validate all inputs
    └── Type checking enforced

Layer 4: Process Isolation
    ├── Services run in separate process groups
    └── Controlled subprocess management

Layer 5: Error Handling
    ├── No stack traces in production
    └── Sanitized error messages

Layer 6: Path Restrictions
    ├── Only configured paths accessible
    └── No arbitrary file access
```

## Performance Optimization

```
Optimization Strategies:

1. Async I/O
   - All I/O operations use async/await
   - No blocking calls
   - High concurrency

2. Connection Pooling
   - Database sessions managed efficiently
   - Connection reuse

3. Limited Data Sets
   - Process list capped at 50
   - Log tailing instead of full reads
   - Pagination on large results

4. Efficient Queries
   - Direct psutil calls
   - No unnecessary database hits
   - Cached configurations

5. WebSocket Throttling
   - Updates limited to 2 seconds
   - Prevents flooding clients
   - Configurable interval

6. Lazy Loading
   - Services loaded on demand
   - Database tables created only when needed
```

## Error Handling Strategy

```
┌─────────────┐
│   Request   │
└──────┬──────┘
       │
       ▼
┌──────────────┐
│  Try Block   │ ◄── All endpoint logic
└──────┬───────┘
       │
       ├── Success ──────────────────┐
       │                             │
       ├── Validation Error          │
       │   └── 422 Response          │
       │                             │
       ├── Not Found                 │
       │   └── 404 Response          │
       │                             │
       ├── Business Logic Error      │
       │   └── 400 Response          │
       │                             │
       └── Unexpected Error          │
           └── 500 Response          │
                                     │
                                     ▼
                            ┌─────────────────┐
                            │ Consistent JSON │
                            │   Response      │
                            │                 │
                            │ {               │
                            │   success: bool │
                            │   error?: str   │
                            │   data?: obj    │
                            │ }               │
                            └─────────────────┘
```

## Deployment Architecture

```
Development:
    python main.py
        │
        └── Uvicorn dev server
            - Auto-reload enabled
            - Debug logging
            - localhost:8080

Production:
    gunicorn main:app
        │
        ├── Worker 1 (Uvicorn)
        ├── Worker 2 (Uvicorn)
        ├── Worker 3 (Uvicorn)
        └── Worker 4 (Uvicorn)
            │
            └── Load balanced
                - Multiple processes
                - Better performance
                - Auto-restart on crash

Windows Service:
    NSSM wrapper
        │
        └── Control Center Backend
            - Auto-start on boot
            - Service recovery
            - Event log integration
```

## Monitoring Points

```
System Level:
    ├── CPU Usage (%)
    ├── Memory Usage (GB)
    ├── Disk Usage (GB)
    └── Process Count

Application Level:
    ├── Request Count
    ├── Response Times
    ├── Error Rates
    └── Active WebSocket Connections

Service Level:
    ├── Service Status (running/stopped)
    ├── Service PID
    ├── Service Logs
    └── Port Usage

Database Level:
    ├── Connection Count
    ├── Query Performance
    └── Database Size
```

---

This architecture provides:
- **Scalability**: Async design supports many concurrent connections
- **Maintainability**: Clear separation of concerns
- **Reliability**: Comprehensive error handling
- **Performance**: Optimized for local development use
- **Security**: Multiple layers of protection

