"""Process manager for controlling services."""
import asyncio
import psutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List
from config import settings


class ProcessManager:
    """Manages service processes (start, stop, monitor)."""

    # Track running processes
    _processes: Dict[str, subprocess.Popen] = {}
    _log_files: Dict[str, Path] = {}

    @classmethod
    async def start_service(cls, service_name: str) -> Dict:
        """
        Start a service by name.

        Args:
            service_name: Name of the service to start (e.g., 'comfyui')

        Returns:
            Dictionary with status and information.
        """
        if service_name not in settings.SERVICES:
            return {
                "success": False,
                "error": f"Unknown service: {service_name}"
            }

        # Check if already running
        if service_name in cls._processes and cls.is_process_running(cls._processes[service_name].pid):
            return {
                "success": False,
                "error": f"Service {service_name} is already running"
            }

        service_config = settings.SERVICES[service_name]

        try:
            # Prepare log file
            log_dir = Path(settings.BASE_DIR) / "logs"
            log_dir.mkdir(exist_ok=True)
            log_file = log_dir / service_config["log_file"]
            cls._log_files[service_name] = log_file

            # Open log file
            log_handle = open(log_file, "a", encoding="utf-8")

            # Start process
            process = subprocess.Popen(
                service_config["command"],
                cwd=service_config["cwd"],
                stdout=log_handle,
                stderr=subprocess.STDOUT,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if hasattr(subprocess, 'CREATE_NEW_PROCESS_GROUP') else 0
            )

            cls._processes[service_name] = process

            # Wait a moment to check if process started successfully
            await asyncio.sleep(1)

            if not cls.is_process_running(process.pid):
                return {
                    "success": False,
                    "error": "Process failed to start"
                }

            return {
                "success": True,
                "pid": process.pid,
                "message": f"Service {service_name} started successfully"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    @classmethod
    async def stop_service(cls, service_name: str) -> Dict:
        """
        Stop a running service.

        Args:
            service_name: Name of the service to stop

        Returns:
            Dictionary with status and information.
        """
        if service_name not in cls._processes:
            return {
                "success": False,
                "error": f"Service {service_name} is not tracked"
            }

        process = cls._processes[service_name]

        try:
            # Try graceful termination first
            process.terminate()

            # Wait up to 5 seconds for graceful shutdown
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                # Force kill if still running
                process.kill()
                process.wait()

            # Remove from tracking
            del cls._processes[service_name]

            return {
                "success": True,
                "message": f"Service {service_name} stopped successfully"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    @classmethod
    def get_service_status(cls, service_name: str) -> Dict:
        """
        Get status of a service.

        Args:
            service_name: Name of the service

        Returns:
            Dictionary with service status information.
        """
        if service_name not in settings.SERVICES:
            return {
                "name": service_name,
                "status": "unknown",
                "error": "Service not configured"
            }

        service_config = settings.SERVICES[service_name]

        # Check if process is tracked and running
        if service_name in cls._processes:
            process = cls._processes[service_name]
            if cls.is_process_running(process.pid):
                return {
                    "name": service_config["name"],
                    "status": "running",
                    "pid": process.pid,
                    "port": service_config.get("port")
                }

        return {
            "name": service_config["name"],
            "status": "stopped",
            "pid": None,
            "port": service_config.get("port")
        }

    @classmethod
    def get_all_services_status(cls) -> List[Dict]:
        """Get status of all configured services."""
        return [
            cls.get_service_status(service_name)
            for service_name in settings.SERVICES.keys()
        ]

    @classmethod
    async def get_service_logs(cls, service_name: str, lines: int = 100) -> Dict:
        """
        Get recent logs from a service.

        Args:
            service_name: Name of the service
            lines: Number of lines to retrieve from the end

        Returns:
            Dictionary with log content.
        """
        if service_name not in settings.SERVICES:
            return {
                "success": False,
                "error": "Unknown service"
            }

        log_file = cls._log_files.get(service_name)
        if not log_file:
            log_dir = Path(settings.BASE_DIR) / "logs"
            service_config = settings.SERVICES[service_name]
            log_file = log_dir / service_config["log_file"]

        if not log_file.exists():
            return {
                "success": True,
                "logs": [],
                "message": "No logs available yet"
            }

        try:
            with open(log_file, "r", encoding="utf-8") as f:
                all_lines = f.readlines()
                recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines

            return {
                "success": True,
                "logs": [line.rstrip() for line in recent_lines],
                "total_lines": len(all_lines)
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    @staticmethod
    def is_process_running(pid: int) -> bool:
        """Check if a process with given PID is running."""
        try:
            process = psutil.Process(pid)
            return process.is_running() and process.status() != psutil.STATUS_ZOMBIE
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return False
