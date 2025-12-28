"""Process management using PID file singleton pattern.

This module ensures only one backend instance runs at a time by using
a PID file-based singleton lock. It handles stale PID detection and
graceful cleanup on exit.
"""
import os
import sys
import atexit
import psutil
from pathlib import Path
from typing import Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProcessManager:
    """Ensures only one backend instance runs at a time using PID file singleton pattern."""

    def __init__(self, pid_file_path: str = "backend.pid"):
        """Initialize process manager.

        Args:
            pid_file_path: Path to PID file (relative to backend directory)
        """
        # Ensure we use absolute path relative to this file's directory
        backend_dir = Path(__file__).parent.resolve()
        self.pid_file = backend_dir / pid_file_path
        self._lock_acquired = False
        logger.info(f"ProcessManager initialized with PID file: {self.pid_file}")

    def _is_process_running(self, pid: int) -> bool:
        """Check if a process with given PID is still running.

        Args:
            pid: Process ID to check

        Returns:
            True if process exists and is running, False otherwise
        """
        try:
            if not psutil.pid_exists(pid):
                return False

            # Additional check: ensure it's actually a Python process
            # This prevents false positives from PID reuse
            try:
                process = psutil.Process(pid)
                # Check if it's a Python process
                process_name = process.name().lower()
                if 'python' in process_name:
                    return True
                else:
                    logger.warning(f"PID {pid} exists but is not a Python process ({process_name})")
                    return False
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                return False

        except Exception as e:
            logger.warning(f"Error checking if PID {pid} is running: {e}")
            return False

    def _read_pid_file(self) -> Optional[int]:
        """Read PID from file.

        Returns:
            PID as integer if valid, None otherwise
        """
        try:
            if not self.pid_file.exists():
                return None

            pid_content = self.pid_file.read_text().strip()

            if not pid_content:
                logger.warning("PID file is empty")
                return None

            try:
                pid = int(pid_content)
                return pid
            except ValueError:
                logger.error(f"PID file contains invalid content: {pid_content}")
                return None

        except PermissionError:
            logger.error(f"Permission denied reading PID file: {self.pid_file}")
            return None
        except Exception as e:
            logger.error(f"Error reading PID file: {e}")
            return None

    def _write_pid_file(self, pid: int) -> bool:
        """Write PID to file.

        Args:
            pid: Process ID to write

        Returns:
            True if successful, False otherwise
        """
        try:
            # Create parent directory if it doesn't exist
            self.pid_file.parent.mkdir(parents=True, exist_ok=True)

            # Write PID to file
            self.pid_file.write_text(str(pid))
            logger.info(f"Wrote PID {pid} to {self.pid_file}")
            return True

        except PermissionError:
            logger.error(f"Permission denied writing PID file: {self.pid_file}")
            return False
        except Exception as e:
            logger.error(f"Error writing PID file: {e}")
            return False

    def _remove_pid_file(self):
        """Remove PID file."""
        try:
            if self.pid_file.exists():
                self.pid_file.unlink()
                logger.info(f"Removed PID file: {self.pid_file}")
        except PermissionError:
            logger.error(f"Permission denied removing PID file: {self.pid_file}")
        except Exception as e:
            logger.error(f"Error removing PID file: {e}")

    def acquire_lock(self) -> bool:
        """Acquire singleton lock.

        Returns:
            True if lock acquired successfully, False if another instance is running
        """
        try:
            # Check if PID file exists
            existing_pid = self._read_pid_file()

            if existing_pid is not None:
                # Check if process is still running
                if self._is_process_running(existing_pid):
                    logger.warning(f"Backend already running with PID {existing_pid}")
                    return False
                else:
                    # Stale PID file - process not running
                    logger.info(f"Found stale PID file (PID {existing_pid} not running), removing...")
                    self._remove_pid_file()

            # Write current PID to file
            current_pid = os.getpid()
            if not self._write_pid_file(current_pid):
                logger.error("Failed to write PID file, but continuing anyway")
                # Continue anyway - graceful degradation
                # This allows the backend to run even if PID file creation fails

            # Register cleanup on exit
            atexit.register(self.release_lock)
            self._lock_acquired = True
            logger.info(f"Successfully acquired process lock (PID: {current_pid})")
            return True

        except Exception as e:
            logger.error(f"Error acquiring process lock: {e}")
            # Graceful degradation - allow backend to start even if locking fails
            logger.warning("Continuing without process lock (graceful degradation)")
            return True

    def release_lock(self):
        """Release singleton lock on shutdown."""
        if self._lock_acquired:
            logger.info("Releasing process lock...")
            self._remove_pid_file()
            self._lock_acquired = False

    def get_running_pid(self) -> Optional[int]:
        """Get PID of running backend instance, if any.

        Returns:
            PID of running instance, or None if no instance running
        """
        existing_pid = self._read_pid_file()

        if existing_pid is None:
            return None

        if self._is_process_running(existing_pid):
            return existing_pid

        return None

    def get_pid_file_path(self) -> Path:
        """Get the absolute path to the PID file.

        Returns:
            Absolute path to PID file
        """
        return self.pid_file


# Convenience function for checking if backend is running
def is_backend_running(pid_file_path: str = "backend.pid") -> tuple[bool, Optional[int]]:
    """Check if backend is currently running.

    Args:
        pid_file_path: Path to PID file

    Returns:
        Tuple of (is_running, pid)
    """
    manager = ProcessManager(pid_file_path)
    pid = manager.get_running_pid()
    return (pid is not None, pid)
