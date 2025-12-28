"""Service control API endpoints."""
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Request, Query, Path, Depends
from typing import List, Optional
from datetime import datetime
from services.service_manager import ServiceManager
from config import settings
from database import get_db
from middleware.rate_limit import limiter
from utils.errors import UserFriendlyError, handle_service_error
from utils.pagination import paginate_list, PaginationParams
from utils.performance import track_performance
from sqlalchemy.ext.asyncio import AsyncSession
import re


router = APIRouter(prefix="/api/services", tags=["services"])


@router.get("")
@limiter.limit("60/minute")
@track_performance(endpoint="GET /api/services", query_type="service_status")
async def get_services(
    request: Request,
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=200, description="Items per page (max 200)"),
    offset: Optional[int] = Query(None, ge=0, description="Alternative to page: start offset")
):
    """
    Get list of all configured services and their status with pagination.

    - **page**: Page number (1-indexed)
    - **page_size**: Items per page (default 50, max 200)
    - **offset**: Alternative to page - start offset
    """
    try:
        # Get all services from database
        services = await ServiceManager.get_all_services(db)

        # Use pagination utility
        params = PaginationParams(page=page, page_size=page_size, offset=offset)
        result = paginate_list(services, params, cached=False)

        # Add success flag and rename items to services for backward compatibility
        result['success'] = True
        result['services'] = result.pop('items')
        result['count'] = result['meta']['total']

        return result

    except Exception as e:
        UserFriendlyError.handle_error(e, context="retrieving service status", status_code=500)


@router.post("/{service_name}/start")
@limiter.limit("10/minute")
async def start_service(
    request: Request,
    service_name: str = Path(
        ...,
        min_length=1,
        max_length=100,
        description="Name of the service to start",
        pattern=r'^[a-zA-Z0-9_-]+$'
    ),
    db: AsyncSession = Depends(get_db)
):
    """
    Start a service by name.

    **Validation:**
    - Service name: 1-100 characters, alphanumeric with hyphens/underscores only

    **Returns:**
    - Service start result with status
    """
    try:
        # Normalize service name
        service_name = service_name.lower().strip()

        result = await ServiceManager.start_service(db, service_name)
        return result

    except Exception as e:
        handle_service_error(e, service_name, "starting")


@router.post("/{service_name}/stop")
@limiter.limit("10/minute")
async def stop_service(
    request: Request,
    service_name: str = Path(
        ...,
        min_length=1,
        max_length=100,
        description="Name of the service to stop",
        pattern=r'^[a-zA-Z0-9_-]+$'
    ),
    timeout: int = Query(
        default=10,
        ge=1,
        le=300,
        description="Timeout in seconds before forcing stop"
    ),
    force: bool = Query(
        default=False,
        description="Force stop the service (SIGKILL)"
    ),
    db: AsyncSession = Depends(get_db)
):
    """
    Stop a running service.

    **Validation:**
    - Service name: 1-100 characters, alphanumeric with hyphens/underscores only
    - Timeout: 1-300 seconds
    - Force: boolean flag for SIGKILL

    **Returns:**
    - Service stop result with status
    """
    try:
        # Normalize service name
        service_name = service_name.lower().strip()

        result = await ServiceManager.stop_service(db, service_name, timeout)
        return result

    except Exception as e:
        handle_service_error(e, service_name, "stopping")


@router.get("/{service_name}/status")
@limiter.limit("60/minute")
async def get_service_status(
    request: Request,
    service_name: str = Path(
        ...,
        min_length=1,
        max_length=100,
        description="Name of the service",
        pattern=r'^[a-zA-Z0-9_-]+$'
    ),
    db: AsyncSession = Depends(get_db)
):
    """
    Get status of a specific service.

    **Validation:**
    - Service name: 1-100 characters, alphanumeric with hyphens/underscores only

    **Returns:**
    - Service status details including PID, uptime, and health
    """
    try:
        # Normalize service name
        service_name = service_name.lower().strip()

        status = await ServiceManager.get_service_status(db, service_name)
        return {
            "success": True,
            **status
        }

    except Exception as e:
        handle_service_error(e, service_name, "retrieving status for")


@router.post("/{service_name}/restart")
@limiter.limit("10/minute")
async def restart_service(
    request: Request,
    service_name: str = Path(
        ...,
        min_length=1,
        max_length=100,
        description="Name of the service to restart",
        pattern=r'^[a-zA-Z0-9_-]+$'
    ),
    db: AsyncSession = Depends(get_db)
):
    """
    Restart a service (stop and then start).

    **Validation:**
    - Service name: 1-100 characters, alphanumeric with hyphens/underscores only

    **Returns:**
    - Service restart result with status
    """
    try:
        # Normalize service name
        service_name = service_name.lower().strip()

        result = await ServiceManager.restart_service(db, service_name)
        return result

    except Exception as e:
        handle_service_error(e, service_name, "restarting")


@router.get("/{service_name}/logs")
@limiter.limit("30/minute")
async def get_service_logs(
    request: Request,
    service_name: str = Path(
        ...,
        min_length=1,
        max_length=100,
        description="Name of the service",
        pattern=r'^[a-zA-Z0-9_-]+$'
    ),
    lines: int = Query(
        default=100,
        ge=1,
        le=10000,
        description="Number of log lines to retrieve"
    )
):
    """
    Get recent logs from a service.

    **Validation:**
    - Service name: 1-100 characters, alphanumeric with hyphens/underscores only
    - Lines: 1-10,000 lines

    **Returns:**
    - Service logs with timestamps
    """
    try:
        # Normalize service name
        service_name = service_name.lower().strip()

        result = await ServiceManager.get_service_logs(service_name, lines)
        return result

    except Exception as e:
        handle_service_error(e, service_name, "retrieving logs for")


# WebSocket connection manager for services
class ServiceConnectionManager:
    """Manages WebSocket connections for service updates."""

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
                pass


# Connection manager instance
service_manager = ServiceConnectionManager()


@router.websocket("/ws")
async def websocket_service_status(websocket: WebSocket):
    """
    WebSocket endpoint for real-time service status updates.

    Requires authentication via token query parameter:
    ws://localhost:54112/api/services/ws?token=<your_jwt_token>
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
        await service_manager.connect(websocket)

        try:
            while True:
                # Get current service statuses from database
                services = await ServiceManager.get_all_services(db)

                status_update = {
                    "type": "service_status",
                    "timestamp": datetime.utcnow().isoformat(),
                    "services": services,
                    "authenticated_user": user.username
                }

                await websocket.send_json(status_update)
                await asyncio.sleep(settings.WS_UPDATE_INTERVAL)

        except WebSocketDisconnect:
            service_manager.disconnect(websocket)
        except Exception as e:
            print(f"WebSocket error: {e}")
            service_manager.disconnect(websocket)

        break  # Exit the async for loop
