"""System monitoring API endpoints."""
import asyncio
import psutil
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Request
from typing import List, Optional
from datetime import datetime
from services import PortScanner
from config import settings
from middleware.rate_limit import limiter
from utils.errors import UserFriendlyError


router = APIRouter(prefix="/api/system", tags=["system"])


@router.get("/stats")
@limiter.limit("60/minute")
async def get_system_stats(request: Request):
    """Get current system statistics (CPU, RAM, Disk)."""
    try:
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=0.1)
        cpu_count = psutil.cpu_count()
        cpu_freq = psutil.cpu_freq()

        # Memory usage
        memory = psutil.virtual_memory()

        # Disk usage
        disk = psutil.disk_usage('C:\\')

        return {
            "success": True,
            "timestamp": datetime.utcnow().isoformat(),
            "cpu": {
                "usage_percent": cpu_percent,
                "count": cpu_count,
                "frequency": {
                    "current": cpu_freq.current if cpu_freq else None,
                    "min": cpu_freq.min if cpu_freq else None,
                    "max": cpu_freq.max if cpu_freq else None
                }
            },
            "memory": {
                "total": memory.total,
                "available": memory.available,
                "used": memory.used,
                "percent": memory.percent,
                "total_gb": round(memory.total / (1024**3), 2),
                "used_gb": round(memory.used / (1024**3), 2),
                "available_gb": round(memory.available / (1024**3), 2)
            },
            "disk": {
                "total": disk.total,
                "used": disk.used,
                "free": disk.free,
                "percent": disk.percent,
                "total_gb": round(disk.total / (1024**3), 2),
                "used_gb": round(disk.used / (1024**3), 2),
                "free_gb": round(disk.free / (1024**3), 2)
            }
        }
    except Exception as e:
        UserFriendlyError.handle_error(e, context="retrieving system statistics", status_code=500)


@router.get("/processes")
@limiter.limit("60/minute")
async def get_processes(request: Request):
    """Get list of running processes."""
    try:
        processes = []

        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
            try:
                proc_info = proc.info
                processes.append({
                    "pid": proc_info['pid'],
                    "name": proc_info['name'],
                    "cpu_percent": proc_info['cpu_percent'],
                    "memory_percent": round(proc_info['memory_percent'], 2),
                    "status": proc_info['status']
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        # Sort by CPU usage
        processes.sort(key=lambda x: x['cpu_percent'] or 0, reverse=True)

        return {
            "success": True,
            "count": len(processes),
            "processes": processes[:50]  # Return top 50
        }

    except Exception as e:
        UserFriendlyError.handle_error(e, context="retrieving system processes", status_code=500)


@router.get("/ports")
@limiter.limit("30/minute")
async def get_ports(request: Request):
    """Get list of open ports and their processes."""
    try:
        ports = PortScanner.scan_ports()

        return {
            "success": True,
            "count": len(ports),
            "ports": ports
        }

    except Exception as e:
        UserFriendlyError.handle_error(e, context="scanning system ports", status_code=500)


@router.get("/info")
@limiter.limit("60/minute")
async def get_system_info(request: Request):
    """Get general system information."""
    try:
        import platform
        import socket
        import sys
        import time

        # Calculate uptime in seconds
        boot_time = psutil.boot_time()
        uptime_seconds = int(time.time() - boot_time)

        return {
            "success": True,
            "os": f"{platform.system()} {platform.release()}",
            "python": sys.version.split()[0],
            "hostname": socket.gethostname(),
            "uptime": uptime_seconds,
            # Additional details for compatibility
            "platform": platform.system(),
            "platform_release": platform.release(),
            "platform_version": platform.version(),
            "arch": platform.machine(),
            "processor": platform.processor(),
            "totalMemory": psutil.virtual_memory().total,
            "cpuCores": psutil.cpu_count(logical=True),
            "cpuCoresPhysical": psutil.cpu_count(logical=False),
            "boot_time": boot_time,
        }
    except Exception as e:
        UserFriendlyError.handle_error(e, context="retrieving system information", status_code=500)


# Public WebSocket connection manager (no authentication required)
class PublicMetricsConnectionManager:
    """Manages WebSocket connections for public metrics (no auth required)."""

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"Public WS client connected. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        print(f"Public WS client disconnected. Total: {len(self.active_connections)}")

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


# Public metrics connection manager instance
public_metrics_manager = PublicMetricsConnectionManager()


@router.websocket("/metrics")
async def websocket_public_metrics(websocket: WebSocket):
    """
    Public WebSocket endpoint for real-time system metrics.
    NO AUTHENTICATION REQUIRED.

    Streams every 1 second:
    {
        "cpu": 25.5,
        "memory": 60.2,
        "disk": 45.3,
        "timestamp": "2025-11-10T12:30:45.123456"
    }

    Connect with: ws://127.0.0.1:54112/api/system/metrics
    """
    await public_metrics_manager.connect(websocket)

    try:
        while True:
            try:
                # Collect metrics with error handling
                cpu_percent = psutil.cpu_percent(interval=0.1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('C:\\')

                metrics = {
                    "cpu": round(cpu_percent, 2),
                    "memory": round(memory.percent, 2),
                    "disk": round(disk.percent, 2),
                    "timestamp": datetime.utcnow().isoformat()
                }

                await websocket.send_json(metrics)
            except Exception as e:
                print(f"Error collecting metrics: {e}")
                # Send error message but continue streaming
                await websocket.send_json({
                    "error": f"Metric collection failed: {str(e)}",
                    "timestamp": datetime.utcnow().isoformat()
                })

            await asyncio.sleep(1)  # Stream every 1 second

    except WebSocketDisconnect:
        public_metrics_manager.disconnect(websocket)
        print("Public metrics WS client disconnected normally")
    except Exception as e:
        print(f"Public metrics WebSocket error: {e}")
        public_metrics_manager.disconnect(websocket)


# WebSocket connection manager
class ConnectionManager:
    """Manages WebSocket connections."""

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        """Broadcast a message to all connected clients."""
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                # Connection might be closed
                pass


# Connection manager instance
manager = ConnectionManager()


@router.websocket("/ws")
async def websocket_system_stats(websocket: WebSocket):
    """
    WebSocket endpoint for real-time system statistics.

    Requires authentication via token query parameter:
    ws://localhost:54112/api/system/ws?token=<your_jwt_token>
    """
    from database import get_db
    from middleware.auth import verify_websocket_token

    # Get token from query parameters
    token = websocket.query_params.get("token")

    if not token:
        await websocket.close(code=1008, reason="Authentication required: No token provided")
        return

    # Verify token and get user
    async for db in get_db():
        user = await verify_websocket_token(token, db)

        if not user:
            await websocket.close(code=1008, reason="Authentication failed: Invalid token")
            return

        # Accept connection after successful authentication
        await manager.connect(websocket)

        try:
            while True:
                # Get current stats
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('C:\\')

                stats = {
                    "type": "system_stats",
                    "timestamp": datetime.utcnow().isoformat(),
                    "cpu": {
                        "usage_percent": cpu_percent
                    },
                    "memory": {
                        "total": memory.total,
                        "used": memory.used,
                        "percent": memory.percent,
                        "used_gb": round(memory.used / (1024**3), 2),
                        "total_gb": round(memory.total / (1024**3), 2)
                    },
                    "disk": {
                        "total": disk.total,
                        "used": disk.used,
                        "percent": disk.percent,
                        "used_gb": round(disk.used / (1024**3), 2),
                        "total_gb": round(disk.total / (1024**3), 2)
                    },
                    "authenticated_user": user.username
                }

                await websocket.send_json(stats)
                await asyncio.sleep(settings.WS_UPDATE_INTERVAL)

        except WebSocketDisconnect:
            manager.disconnect(websocket)
        except Exception as e:
            print(f"WebSocket error: {e}")
            manager.disconnect(websocket)

        break  # Exit the async for loop
