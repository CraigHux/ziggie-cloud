"""Service management for controlling and monitoring services."""
import asyncio
import psutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from config import settings
from database.models import Service


class ServiceManager:
    """Manages service lifecycle (start, stop, restart, monitor)."""

    # Track running processes
    _processes: Dict[str, subprocess.Popen] = {}
    _log_files: Dict[str, Path] = {}

    @classmethod
    async def start_service(cls, db: AsyncSession, service_name: str) -> Dict:
        """
        Start a service by name.

        Args:
            db: Database session
            service_name: Name of the service to start

        Returns:
            Dictionary with status and information.
        """
        # Get service from database
        stmt = select(Service).where(Service.name == service_name)
        result = await db.execute(stmt)
        service = result.scalar()

        if not service:
            return {
                "success": False,
                "error": f"Service '{service_name}' not found in database"
            }

        # Check if already running
        if service.pid and cls.is_process_running(service.pid):
            return {
                "success": False,
                "error": f"Service '{service_name}' is already running (PID: {service.pid})"
            }

        try:
            # Prepare log directory
            log_dir = Path(settings.BASE_DIR) / "logs"
            log_dir.mkdir(exist_ok=True)
            log_file = log_dir / f"{service_name}.log"
            cls._log_files[service_name] = log_file

            # Open log file
            log_handle = open(log_file, "a", encoding="utf-8")

            # Parse command (handle both string and list formats)
            if isinstance(service.command, str):
                command = service.command.split()
            else:
                command = service.command

            # Start process
            cwd = service.cwd or str(settings.BASE_DIR)
            process = subprocess.Popen(
                command,
                cwd=cwd,
                stdout=log_handle,
                stderr=subprocess.STDOUT,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if hasattr(subprocess, 'CREATE_NEW_PROCESS_GROUP') else 0
            )

            cls._processes[service_name] = process

            # Wait a moment to check if process started successfully
            await asyncio.sleep(1)

            if not cls.is_process_running(process.pid):
                service.status = "failed"
                service.updated_at = datetime.utcnow()
                db.add(service)
                await db.commit()
                return {
                    "success": False,
                    "error": "Process failed to start"
                }

            # Update service in database
            service.status = "running"
            service.pid = process.pid
            service.health = "unknown"
            service.updated_at = datetime.utcnow()
            db.add(service)
            await db.commit()

            return {
                "success": True,
                "pid": process.pid,
                "message": f"Service '{service_name}' started successfully"
            }

        except Exception as e:
            service.status = "failed"
            service.updated_at = datetime.utcnow()
            db.add(service)
            await db.commit()
            return {
                "success": False,
                "error": str(e)
            }

    @classmethod
    async def stop_service(cls, db: AsyncSession, service_name: str, timeout: int = 10) -> Dict:
        """
        Stop a running service.

        Args:
            db: Database session
            service_name: Name of the service to stop
            timeout: Timeout in seconds before forcing stop

        Returns:
            Dictionary with status and information.
        """
        # Get service from database
        stmt = select(Service).where(Service.name == service_name)
        result = await db.execute(stmt)
        service = result.scalar()

        if not service:
            return {
                "success": False,
                "error": f"Service '{service_name}' not found in database"
            }

        if not service.pid:
            service.status = "stopped"
            service.health = "unknown"
            service.updated_at = datetime.utcnow()
            db.add(service)
            await db.commit()
            return {
                "success": True,
                "message": f"Service '{service_name}' is not running"
            }

        try:
            process = cls._processes.get(service_name)
            if not process:
                try:
                    process = psutil.Process(service.pid)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    process = None

            if process:
                try:
                    # Try graceful termination first
                    if hasattr(process, 'terminate'):
                        process.terminate()
                    else:
                        process.kill()

                    # Wait for graceful shutdown
                    try:
                        process.wait(timeout=timeout)
                    except subprocess.TimeoutExpired:
                        # Force kill if still running
                        process.kill()
                        process.wait()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

            # Remove from tracking
            if service_name in cls._processes:
                del cls._processes[service_name]

            # Update service in database
            service.status = "stopped"
            service.pid = None
            service.health = "unknown"
            service.updated_at = datetime.utcnow()
            db.add(service)
            await db.commit()

            return {
                "success": True,
                "message": f"Service '{service_name}' stopped successfully"
            }

        except Exception as e:
            service.status = "stopped"
            service.pid = None
            service.updated_at = datetime.utcnow()
            db.add(service)
            await db.commit()
            return {
                "success": False,
                "error": f"Failed to stop service: {str(e)}"
            }

    @classmethod
    async def restart_service(cls, db: AsyncSession, service_name: str) -> Dict:
        """
        Restart a service.

        Args:
            db: Database session
            service_name: Name of the service to restart

        Returns:
            Dictionary with status and information.
        """
        # Stop the service
        stop_result = await cls.stop_service(db, service_name)
        if not stop_result.get("success"):
            return stop_result

        # Wait a moment before starting
        await asyncio.sleep(2)

        # Start the service
        return await cls.start_service(db, service_name)

    @classmethod
    async def get_service_status(cls, db: AsyncSession, service_name: str) -> Dict:
        """
        Get status of a service.

        Args:
            db: Database session
            service_name: Name of the service

        Returns:
            Dictionary with service status information.
        """
        stmt = select(Service).where(Service.name == service_name)
        result = await db.execute(stmt)
        service = result.scalar()

        if not service:
            return {
                "name": service_name,
                "status": "unknown",
                "health": "unknown",
                "error": "Service not found in database"
            }

        # Check if PID is still running
        if service.pid and service.status == "running":
            if not cls.is_process_running(service.pid):
                # Process is no longer running, update database
                service.status = "stopped"
                service.pid = None
                service.health = "unknown"
                service.updated_at = datetime.utcnow()
                db.add(service)
                await db.commit()

        return {
            "id": service.id,
            "name": service.name,
            "description": service.description,
            "status": service.status,
            "health": service.health,
            "pid": service.pid,
            "port": service.port,
            "is_system": service.is_system,
            "created_at": service.created_at.isoformat() if service.created_at else None,
            "updated_at": service.updated_at.isoformat() if service.updated_at else None
        }

    @classmethod
    async def get_all_services(cls, db: AsyncSession) -> List[Dict]:
        """Get status of all services from database."""
        stmt = select(Service).order_by(Service.name)
        result = await db.execute(stmt)
        services = result.scalars().all()

        service_list = []
        for service in services:
            # Check if PID is still running
            if service.pid and service.status == "running":
                if not cls.is_process_running(service.pid):
                    # Process is no longer running, update database
                    service.status = "stopped"
                    service.pid = None
                    service.health = "unknown"
                    service.updated_at = datetime.utcnow()
                    db.add(service)

            service_list.append({
                "id": service.id,
                "name": service.name,
                "description": service.description,
                "status": service.status,
                "health": service.health,
                "pid": service.pid,
                "port": service.port,
                "is_system": service.is_system,
                "created_at": service.created_at.isoformat() if service.created_at else None,
                "updated_at": service.updated_at.isoformat() if service.updated_at else None
            })

        await db.commit()
        return service_list

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
        log_dir = Path(settings.BASE_DIR) / "logs"
        log_file = log_dir / f"{service_name}.log"

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

    @staticmethod
    async def check_port_availability(port: int) -> bool:
        """Check if a port is available (not in use)."""
        try:
            for conn in psutil.net_connections():
                if conn.laddr.port == port:
                    return False
            return True
        except Exception:
            return True
