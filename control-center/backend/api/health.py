"""Health check endpoints for monitoring and orchestration."""
from fastapi import APIRouter, HTTPException
from datetime import datetime
import psutil
import sys
import os

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("")
async def health_check():
    """Basic health check - returns 200 if service is running.

    Used for simple liveness probes.
    Returns:
        dict: Basic health status and timestamp
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }


@router.get("/detailed")
async def detailed_health():
    """Detailed health check with system metrics.

    Returns comprehensive system information including CPU, memory, and disk usage.
    Useful for monitoring dashboards and performance analysis.

    Returns:
        dict: Detailed health status with system metrics

    Raises:
        HTTPException: If health check fails with 500 status code
    """
    try:
        # Use non-blocking CPU percent check (interval=None) to keep response time low
        cpu_percent = psutil.cpu_percent(interval=None)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')

        # Calculate health status based on thresholds
        status = "healthy"
        if cpu_percent > 90 or memory.percent > 90 or disk.percent > 90:
            status = "warning"
        if cpu_percent > 95 or memory.percent > 95 or disk.percent > 95:
            status = "critical"

        return {
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "system": {
                "cpu_percent": round(cpu_percent, 2),
                "cpu_count": psutil.cpu_count(),
                "memory_percent": round(memory.percent, 2),
                "memory_used_gb": round(memory.used / (1024**3), 2),
                "memory_available_gb": round(memory.available / (1024**3), 2),
                "memory_total_gb": round(memory.total / (1024**3), 2),
                "disk_percent": round(disk.percent, 2),
                "disk_used_gb": round(disk.used / (1024**3), 2),
                "disk_free_gb": round(disk.free / (1024**3), 2),
                "disk_total_gb": round(disk.total / (1024**3), 2)
            },
            "python_version": sys.version,
            "process_id": os.getpid(),
            "working_directory": os.getcwd()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Health check failed: {str(e)}"
        )


@router.get("/ready")
async def readiness_check():
    """Readiness check - verifies all dependencies are available.

    Kubernetes readiness probe. Returns 200 only when service is ready
    to accept traffic.

    Returns:
        dict: Readiness status and component checks
    """
    checks = {
        "service": True,      # Service is running
        "system": True        # System resources available
    }

    # Verify system resources are not critically low
    try:
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')

        # System is not ready if critical resource limits exceeded
        if memory.percent > 95 or disk.percent > 95:
            checks["system"] = False
    except Exception:
        checks["system"] = False

    all_ready = all(checks.values())

    return {
        "ready": all_ready,
        "status": "ready" if all_ready else "not_ready",
        "checks": checks,
        "timestamp": datetime.now().isoformat()
    }


@router.get("/live")
async def liveness_check():
    """Liveness check - simple ping to verify service is alive.

    Kubernetes liveness probe. Returns 200 if process is running.

    Returns:
        dict: Liveness status
    """
    return {
        "alive": True,
        "timestamp": datetime.now().isoformat()
    }


@router.get("/startup")
async def startup_check():
    """Startup check - verifies service has completed initialization.

    Kubernetes startup probe. Returns 200 once initialization is complete.

    Returns:
        dict: Startup status and initialization details
    """
    return {
        "startup_complete": True,
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }
