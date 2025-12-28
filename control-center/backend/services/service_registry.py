"""
Service Registry
Centralized configuration for all external services
"""

from pathlib import Path
from typing import Dict, List
from enum import Enum


class ServiceStatus(str, Enum):
    """Service status enumeration"""
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"
    UNKNOWN = "unknown"
    STARTING = "starting"
    STOPPING = "stopping"


class ServiceType(str, Enum):
    """Service type enumeration"""
    PROCESS = "process"
    CONTAINER = "container"
    API = "api"
    SYSTEM = "system"


# Service definitions
SERVICES = {
    "comfyui": {
        "name": "ComfyUI",
        "type": ServiceType.PROCESS,
        "description": "AI image generation workflow system",
        "command": "cd /c/ComfyUI && ./python_embeded/python.exe -s ComfyUI/main.py --windows-standalone-build --cpu",
        "working_dir": "C:/ComfyUI",
        "executable": "C:/ComfyUI/python_embeded/python.exe",
        "script": "C:/ComfyUI/ComfyUI/main.py",
        "port": 8188,
        "url": "http://localhost:8188",
        "log_file": "C:/ComfyUI/logs/comfyui.log",
        "process_pattern": "ComfyUI/main.py",
        "health_check": {
            "endpoint": "/system_stats",
            "timeout": 5
        },
        "startup_time": 30,
        "shutdown_timeout": 10,
        "priority": "high",
        "auto_start": False,
        "dependencies": []
    },

    "kb_scheduler": {
        "name": "Knowledge Base Scheduler",
        "type": ServiceType.PROCESS,
        "description": "Automated YouTube content scanning and knowledge extraction",
        "command": "python manage.py schedule",
        "working_dir": "C:/Ziggie/ai-agents/knowledge-base",
        "executable": "python",
        "script": "C:/Ziggie/ai-agents/knowledge-base/manage.py",
        "port": None,
        "url": None,
        "log_file": "C:/Ziggie/ai-agents/knowledge-base/logs/scheduler.log",
        "process_pattern": "manage.py schedule",
        "health_check": None,
        "startup_time": 5,
        "shutdown_timeout": 5,
        "priority": "medium",
        "auto_start": False,
        "dependencies": []
    },

    "control_center_backend": {
        "name": "Control Center Backend",
        "type": ServiceType.API,
        "description": "FastAPI backend for Ziggie Control Center dashboard",
        "command": "uvicorn main:app --host 0.0.0.0 --port 8000 --reload",
        "working_dir": "C:/Ziggie/control-center/backend",
        "executable": "uvicorn",
        "script": None,
        "port": 8000,
        "url": "http://localhost:8000",
        "log_file": "C:/Ziggie/control-center/backend/logs/backend.log",
        "process_pattern": "uvicorn main:app",
        "health_check": {
            "endpoint": "/health",
            "timeout": 2
        },
        "startup_time": 10,
        "shutdown_timeout": 5,
        "priority": "critical",
        "auto_start": True,
        "dependencies": []
    },

    "control_center_frontend": {
        "name": "Control Center Frontend",
        "type": ServiceType.PROCESS,
        "description": "React/Vite frontend for Ziggie Control Center",
        "command": "npm run dev",
        "working_dir": "C:/Ziggie/control-center/frontend",
        "executable": "npm",
        "script": None,
        "port": 3000,
        "url": "http://localhost:3000",
        "log_file": "C:/Ziggie/control-center/frontend/logs/frontend.log",
        "process_pattern": "next dev",
        "health_check": None,
        "startup_time": 15,
        "shutdown_timeout": 5,
        "priority": "high",
        "auto_start": True,
        "dependencies": ["control_center_backend"]
    },

    "game_backend": {
        "name": "Meow Ping RTS Backend",
        "type": ServiceType.API,
        "description": "FastAPI backend for Meow Ping RTS game",
        "command": "uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload",
        "working_dir": "C:/meowping-rts/backend",
        "executable": "uvicorn",
        "script": None,
        "port": 8001,
        "url": "http://localhost:8001",
        "log_file": "C:/meowping-rts/backend/logs/backend.log",
        "process_pattern": "uvicorn app.main:app",
        "health_check": {
            "endpoint": "/health",
            "timeout": 2
        },
        "startup_time": 10,
        "shutdown_timeout": 5,
        "priority": "high",
        "auto_start": False,
        "dependencies": []
    },

    "game_frontend": {
        "name": "Meow Ping RTS Frontend",
        "type": ServiceType.PROCESS,
        "description": "React frontend for Meow Ping RTS game",
        "command": "npm run dev",
        "working_dir": "C:/meowping-rts/frontend",
        "executable": "npm",
        "script": None,
        "port": 3001,
        "url": "http://localhost:3001",
        "log_file": "C:/meowping-rts/frontend/logs/frontend.log",
        "process_pattern": "react-scripts start",
        "health_check": None,
        "startup_time": 20,
        "shutdown_timeout": 5,
        "priority": "high",
        "auto_start": False,
        "dependencies": ["game_backend"]
    },

    "postgres": {
        "name": "PostgreSQL Database",
        "type": ServiceType.CONTAINER,
        "description": "PostgreSQL database for game data",
        "command": "docker-compose up postgres -d",
        "working_dir": "C:/meowping-rts",
        "executable": "docker-compose",
        "script": None,
        "port": 5432,
        "url": "postgresql://localhost:5432",
        "log_file": None,
        "process_pattern": None,
        "container_name": "meowping-postgres",
        "health_check": {
            "command": "pg_isready",
            "timeout": 5
        },
        "startup_time": 10,
        "shutdown_timeout": 10,
        "priority": "critical",
        "auto_start": False,
        "dependencies": []
    },

    "redis": {
        "name": "Redis Cache",
        "type": ServiceType.CONTAINER,
        "description": "Redis for caching and session management",
        "command": "docker-compose up redis -d",
        "working_dir": "C:/meowping-rts",
        "executable": "docker-compose",
        "script": None,
        "port": 6379,
        "url": "redis://localhost:6379",
        "log_file": None,
        "process_pattern": None,
        "container_name": "meowping-redis",
        "health_check": {
            "command": "redis-cli ping",
            "timeout": 2
        },
        "startup_time": 5,
        "shutdown_timeout": 5,
        "priority": "medium",
        "auto_start": False,
        "dependencies": []
    }
}


# Service groups for easy management
SERVICE_GROUPS = {
    "essential": [
        "control_center_backend",
        "control_center_frontend"
    ],
    "game": [
        "game_backend",
        "game_frontend",
        "postgres",
        "redis"
    ],
    "ai_tools": [
        "comfyui",
        "kb_scheduler"
    ],
    "all": list(SERVICES.keys())
}


def get_service(service_id: str) -> Dict:
    """Get service configuration by ID"""
    return SERVICES.get(service_id)


def get_all_services() -> Dict[str, Dict]:
    """Get all service configurations"""
    return SERVICES


def get_services_by_type(service_type: ServiceType) -> Dict[str, Dict]:
    """Get services filtered by type"""
    return {
        sid: svc for sid, svc in SERVICES.items()
        if svc["type"] == service_type
    }


def get_services_by_priority(priority: str) -> Dict[str, Dict]:
    """Get services filtered by priority"""
    return {
        sid: svc for sid, svc in SERVICES.items()
        if svc["priority"] == priority
    }


def get_auto_start_services() -> List[str]:
    """Get list of services that should auto-start"""
    return [
        sid for sid, svc in SERVICES.items()
        if svc.get("auto_start", False)
    ]


def get_service_dependencies(service_id: str) -> List[str]:
    """Get dependencies for a service"""
    service = SERVICES.get(service_id)
    if not service:
        return []
    return service.get("dependencies", [])


def get_startup_order() -> List[str]:
    """Get recommended startup order based on dependencies"""
    ordered = []
    remaining = list(SERVICES.keys())

    # Simple topological sort
    while remaining:
        # Find services with no unmet dependencies
        ready = [
            sid for sid in remaining
            if all(dep in ordered for dep in get_service_dependencies(sid))
        ]

        if not ready:
            # Circular dependency or error - just add remaining
            ordered.extend(remaining)
            break

        # Add ready services
        ordered.extend(ready)

        # Remove from remaining
        for sid in ready:
            remaining.remove(sid)

    return ordered


def validate_service_paths() -> Dict[str, Dict]:
    """Validate that service paths exist"""
    validation = {}

    for service_id, service in SERVICES.items():
        validation[service_id] = {
            "valid": True,
            "issues": []
        }

        # Check working directory
        working_dir = service.get("working_dir")
        if working_dir and not Path(working_dir).exists():
            validation[service_id]["valid"] = False
            validation[service_id]["issues"].append(f"Working directory not found: {working_dir}")

        # Check executable (for file-based executables)
        executable = service.get("executable")
        if executable and executable.startswith("C:/") and not Path(executable).exists():
            validation[service_id]["valid"] = False
            validation[service_id]["issues"].append(f"Executable not found: {executable}")

        # Check script
        script = service.get("script")
        if script and not Path(script).exists():
            validation[service_id]["valid"] = False
            validation[service_id]["issues"].append(f"Script not found: {script}")

        # Check log file directory
        log_file = service.get("log_file")
        if log_file:
            log_dir = Path(log_file).parent
            if not log_dir.exists():
                # Not critical, can be created
                validation[service_id]["issues"].append(f"Log directory will be created: {log_dir}")

    return validation


# Default ports mapping
DEFAULT_PORTS = {
    "comfyui": 8188,
    "control_center_backend": 8000,
    "control_center_frontend": 3000,
    "game_backend": 8001,
    "game_frontend": 3001,
    "postgres": 5432,
    "redis": 6379
}


def get_service_port(service_id: str) -> int:
    """Get default port for a service"""
    service = SERVICES.get(service_id)
    if service:
        return service.get("port")
    return DEFAULT_PORTS.get(service_id)


def get_service_url(service_id: str) -> str:
    """Get URL for a service"""
    service = SERVICES.get(service_id)
    if service:
        return service.get("url")
    return None
