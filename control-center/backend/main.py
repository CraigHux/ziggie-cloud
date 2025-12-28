"""Main FastAPI application for Control Center backend."""
import sys
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from slowapi.middleware import SlowAPIMiddleware
from config import settings
from database import init_db
from api import system, services, knowledge, agents, comfyui, projects, usage, docker, cache, health, auth, llm
from middleware.rate_limit import limiter
from process_manager import ProcessManager
import psutil
from datetime import datetime
from typing import List


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    print("Initializing Control Center backend...")
    await init_db()
    print("Database initialized")
    print("Caching layer enabled (5-minute TTL)")
    print(f"Server starting on http://{settings.HOST}:{settings.PORT}")

    yield

    # Shutdown
    print("Shutting down Control Center backend...")
    # Process manager cleanup is handled by atexit registration


# Create FastAPI application
app = FastAPI(
    title="Control Center Backend",
    description="Backend API for Ziggie Control Center Dashboard",
    version="1.0.0",
    lifespan=lifespan
)

# Add rate limiter to app state (must be done before middleware)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add SlowAPI middleware (must be registered AFTER setting state)
app.add_middleware(SlowAPIMiddleware)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add gzip compression middleware
app.add_middleware(
    GZipMiddleware,
    minimum_size=1000,  # Only compress responses larger than 1KB
    compresslevel=6     # Balance between speed and compression (1-9)
)

# WebSocket connection manager for public system stats
class PublicConnectionManager:
    """Manages WebSocket connections for public system stats."""

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"WebSocket client connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        print(f"WebSocket client disconnected. Total connections: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        """Broadcast a message to all connected clients."""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"Failed to send message to client: {e}")
                disconnected.append(connection)

        # Remove disconnected clients
        for connection in disconnected:
            self.disconnect(connection)


# Connection manager instance for public WebSocket
public_manager = PublicConnectionManager()


@app.websocket("/ws")
async def websocket_public_system_stats(websocket: WebSocket):
    """
    Public WebSocket endpoint for real-time system statistics.
    No authentication required.

    Connects to: ws://127.0.0.1:54112/ws

    Broadcasts every 2 seconds:
    {
        "type": "system_stats",
        "timestamp": "2025-11-10T12:30:45.123456",
        "cpu": {"usage": 25.5},
        "memory": {"percent": 60.2, "used_gb": 15.5, "total_gb": 32.0},
        "disk": {"percent": 45.3, "used_gb": 234.5, "total_gb": 512.0}
    }
    """
    await public_manager.connect(websocket)

    try:
        while True:
            # Get current stats
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('C:\\')

            stats = {
                "type": "system_stats",
                "timestamp": datetime.utcnow().isoformat(),
                "cpu": {
                    "usage": round(cpu_percent, 2)
                },
                "memory": {
                    "percent": round(memory.percent, 2),
                    "used_gb": round(memory.used / (1024**3), 2),
                    "total_gb": round(memory.total / (1024**3), 2)
                },
                "disk": {
                    "percent": round(disk.percent, 2),
                    "used_gb": round(disk.used / (1024**3), 2),
                    "total_gb": round(disk.total / (1024**3), 2)
                }
            }

            await websocket.send_json(stats)
            await asyncio.sleep(settings.WS_UPDATE_INTERVAL)

    except WebSocketDisconnect:
        public_manager.disconnect(websocket)
        print("WebSocket client disconnected normally")
    except Exception as e:
        print(f"WebSocket error: {e}")
        public_manager.disconnect(websocket)


# Include routers
app.include_router(auth.router)  # Authentication routes (no auth required)
app.include_router(health.router)  # Health check endpoints (public)
app.include_router(system.router)
app.include_router(services.router)
app.include_router(knowledge.router)
app.include_router(agents.router)
app.include_router(comfyui.router)
app.include_router(projects.router)
app.include_router(usage.router)
app.include_router(docker.router)
app.include_router(cache.router)  # Cache management API
app.include_router(llm.router)  # LLM/AI endpoints


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Control Center Backend",
        "version": "1.0.0",
        "status": "running",
        "caching_enabled": True,
        "websocket_url": f"ws://{settings.HOST}:{settings.PORT}/ws"
    }


@app.get("/health")
@limiter.limit("100/minute")
async def health_basic(request):
    """Health check endpoint."""
    return {
        "status": "healthy",
        "database": "connected",
        "caching": "enabled",
        "websocket": "available at ws://{settings.HOST}:{settings.PORT}/ws"
    }


if __name__ == "__main__":
    import uvicorn

    # Initialize process manager and acquire singleton lock
    process_manager = ProcessManager("backend.pid")

    if not process_manager.acquire_lock():
        running_pid = process_manager.get_running_pid()
        print("\n" + "=" * 70)
        print("ERROR: Backend already running!")
        print("=" * 70)
        print(f"Another instance is running with PID: {running_pid}")
        print(f"\nTo stop the running instance:")
        print(f"  Windows: taskkill /F /PID {running_pid}")
        print(f"  Linux:   kill {running_pid}")
        print(f"\nPID file location: {process_manager.get_pid_file_path()}")
        print("=" * 70 + "\n")
        sys.exit(1)

    print(f"Process lock acquired (PID: {process_manager.get_running_pid()})")

    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
