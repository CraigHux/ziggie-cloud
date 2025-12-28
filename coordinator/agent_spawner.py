"""
Agent Spawner
Handles spawning and managing Claude Code CLI processes
"""

import subprocess
import psutil
import os
import json
import time
import logging
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime
from .schemas import DeploymentRequest, DeploymentResponse, AgentStatus
from .state_manager import StateManager

logger = logging.getLogger(__name__)


class AgentSpawner:
    """Spawns and manages agent processes"""

    def __init__(self, deployment_dir: Path, state_manager: Optional[StateManager] = None):
        self.deployment_dir = deployment_dir
        self.processes: Dict[str, subprocess.Popen] = {}
        self.agent_info: Dict[str, Dict] = {}
        self.state_manager = state_manager or StateManager(deployment_dir)

    def spawn_agent(self, request: DeploymentRequest) -> DeploymentResponse:
        """
        Spawn a new agent process with robust error handling and process tracking

        Args:
            request: Deployment request with agent configuration

        Returns:
            Deployment response with status
        """
        process = None
        agent_dir = None

        try:
            # Update state to SPAWNING
            self.state_manager.save_agent_state(request.agent_id, {
                "agent_id": request.agent_id,
                "status": AgentStatus.SPAWNING.value,
                "started_at": datetime.now().isoformat()
            })

            # Create working directory for agent
            agent_dir = self.deployment_dir / "agents" / request.agent_id
            agent_dir.mkdir(parents=True, exist_ok=True)

            # Write prompt to file
            prompt_file = agent_dir / "prompt.txt"
            prompt_file.write_text(request.prompt)

            # Prepare environment variables for the subprocess
            env = os.environ.copy()
            env["AGENT_ID"] = request.agent_id
            env["AGENT_NAME"] = request.agent_name
            env["PARENT_AGENT_ID"] = request.parent_agent_id
            env["AGENT_TYPE"] = request.agent_type
            env["MODEL"] = request.model
            env["AGENT_WORKING_DIR"] = str(agent_dir)
            env["PYTHONIOENCODING"] = "utf-8"  # Force UTF-8 encoding for Python subprocess

            # Ensure ANTHROPIC_API_KEY is available
            # Priority: 1) Environment, 2) Keys-api directory, 3) SDK default locations
            if "ANTHROPIC_API_KEY" not in env:
                # Try loading from Keys-api directory first
                keys_dir = Path("C:/Ziggie/Keys-api")
                key_files = ["anthropic-api.txt", "claude-api.txt", "anthropic.txt"]

                api_key = None
                for key_file in key_files:
                    key_path = keys_dir / key_file
                    if key_path.exists():
                        try:
                            api_key = key_path.read_text().strip()
                            if api_key:
                                env["ANTHROPIC_API_KEY"] = api_key
                                logger.info(f"Loaded API key from {key_file}")
                                break
                        except Exception as e:
                            logger.warning(f"Failed to read {key_file}: {e}")

                # If still not found, try SDK's default auth
                if "ANTHROPIC_API_KEY" not in env:
                    try:
                        from anthropic import Anthropic
                        client = Anthropic()
                        if hasattr(client, 'api_key') and client.api_key:
                            env["ANTHROPIC_API_KEY"] = client.api_key
                            logger.info("Extracted API key from Anthropic SDK")
                    except Exception as e:
                        logger.error(f"ANTHROPIC_API_KEY not found. Please create C:/Ziggie/Keys-api/anthropic-api.txt: {e}")

            # Prepare log files for stdout/stderr
            stdout_log = agent_dir / "stdout.log"
            stderr_log = agent_dir / "stderr.log"

            # Spawn REAL agent using Anthropic SDK runner
            # This creates an independent Python process that uses the Anthropic API
            # to execute the agent's task with actual Claude LLM calls
            runner_script = Path(__file__).parent / "claude_agent_runner.py"

            if not runner_script.exists():
                raise FileNotFoundError(f"Agent runner script not found: {runner_script}")

            process = subprocess.Popen(
                ["python", str(runner_script)],
                env=env,
                cwd=str(agent_dir),
                stdout=open(stdout_log, 'w', encoding='utf-8'),
                stderr=open(stderr_log, 'w', encoding='utf-8'),
                start_new_session=True  # Create new process group for independence
            )

            # Wait briefly to ensure process started successfully
            time.sleep(0.1)

            # Check if process is still alive (didn't immediately crash)
            if process.poll() is not None:
                # Process already exited - this is a failure
                raise RuntimeError(f"Process exited immediately with code {process.returncode}")

            # Get the actual PID
            pid = process.pid

            # Verify process exists using psutil
            try:
                proc = psutil.Process(pid)
                if not proc.is_running():
                    raise RuntimeError(f"Process {pid} is not running")
            except psutil.NoSuchProcess:
                raise RuntimeError(f"Process {pid} does not exist")

            # Store process handle and info
            self.processes[request.agent_id] = process

            # Create status file
            status_file = agent_dir / "status.json"
            status_data = {
                "agent_id": request.agent_id,
                "status": "running",
                "started_at": datetime.now().isoformat(),
                "pid": pid,
                "progress": 0
            }
            status_file.write_text(json.dumps(status_data, indent=2))

            # Store agent info
            self.agent_info[request.agent_id] = {
                "request": request.dict(),
                "started_at": datetime.now(),
                "agent_dir": str(agent_dir),
                "status_file": str(status_file),
                "stdout_log": str(stdout_log),
                "stderr_log": str(stderr_log),
                "pid": pid
            }

            # Create successful response
            response = DeploymentResponse(
                request_id=request.request_id,
                agent_id=request.agent_id,
                status=AgentStatus.RUNNING,
                pid=pid,
                started_at=datetime.now(),
                message=f"Agent {request.agent_id} deployed successfully (PID: {pid})"
            )

            # Save running state for persistence
            running_state = self.state_manager.create_agent_state(request, response)
            self.state_manager.save_agent_state(request.agent_id, running_state)

            return response

        except subprocess.SubprocessError as e:
            # Subprocess-specific errors
            error_msg = f"Failed to spawn subprocess: {str(e)}"
            self._handle_spawn_failure(request, error_msg, process, agent_dir)
            return DeploymentResponse(
                request_id=request.request_id,
                agent_id=request.agent_id,
                status=AgentStatus.FAILED,
                message="Subprocess spawn failed",
                error=error_msg
            )

        except psutil.Error as e:
            # Process monitoring errors
            error_msg = f"Process monitoring error: {str(e)}"
            self._handle_spawn_failure(request, error_msg, process, agent_dir)
            return DeploymentResponse(
                request_id=request.request_id,
                agent_id=request.agent_id,
                status=AgentStatus.FAILED,
                message="Process monitoring failed",
                error=error_msg
            )

        except OSError as e:
            # File system or OS-level errors
            error_msg = f"OS error during spawn: {str(e)}"
            self._handle_spawn_failure(request, error_msg, process, agent_dir)
            return DeploymentResponse(
                request_id=request.request_id,
                agent_id=request.agent_id,
                status=AgentStatus.FAILED,
                message="OS error during deployment",
                error=error_msg
            )

        except Exception as e:
            # Catch-all for unexpected errors
            error_msg = f"Unexpected error: {str(e)}"
            self._handle_spawn_failure(request, error_msg, process, agent_dir)
            return DeploymentResponse(
                request_id=request.request_id,
                agent_id=request.agent_id,
                status=AgentStatus.FAILED,
                message="Deployment failed",
                error=error_msg
            )

    def _handle_spawn_failure(self, request: DeploymentRequest, error_msg: str,
                             process: Optional[subprocess.Popen], agent_dir: Optional[Path]):
        """
        Handle cleanup when agent spawn fails

        Args:
            request: The deployment request that failed
            error_msg: Error message to log
            process: Process handle (if created)
            agent_dir: Agent directory path (if created)
        """
        # Try to kill the process if it exists
        if process is not None:
            try:
                if process.poll() is None:  # Still running
                    process.kill()
                    process.wait(timeout=5)
            except Exception as e:
                print(f"Error killing failed process: {e}")

        # Update state to FAILED
        self.state_manager.mark_agent_failed(request.agent_id, error_msg)

        # Write error log if directory exists
        if agent_dir and agent_dir.exists():
            error_log = agent_dir / "error.log"
            try:
                error_log.write_text(f"{datetime.now().isoformat()}: {error_msg}\n")
            except Exception as e:
                print(f"Could not write error log: {e}")

    def get_agent_status(self, agent_id: str) -> Optional[Dict]:
        """
        Get comprehensive status of an agent including process health

        Checks:
        - Process existence and state via psutil
        - Memory and CPU usage
        - Exit code (if terminated)
        - Zombie/defunct status
        - File-based status updates

        Args:
            agent_id: Unique agent identifier

        Returns:
            Dictionary with comprehensive status info or None if not found
        """
        if agent_id not in self.agent_info:
            return None

        info = self.agent_info[agent_id]
        status = {
            "agent_id": agent_id,
            "process_alive": False,
            "process_status": "unknown",
            "exit_code": None,
            "is_zombie": False,
            "cpu_percent": 0.0,
            "memory_mb": 0.0,
            "runtime_seconds": 0,
        }

        # Check if we have a process handle
        process = self.processes.get(agent_id)

        if process is not None:
            # Check if process has terminated
            poll_result = process.poll()

            if poll_result is None:
                # Process is still running - get detailed health info
                try:
                    proc = psutil.Process(process.pid)

                    # Check if process is actually running (not zombie)
                    if proc.is_running():
                        proc_status = proc.status()

                        status["process_alive"] = True
                        status["process_status"] = proc_status
                        status["is_zombie"] = (proc_status == psutil.STATUS_ZOMBIE)

                        # Get resource usage (only if not zombie)
                        if not status["is_zombie"]:
                            try:
                                # CPU usage (returns 0.0 on first call, requires interval)
                                status["cpu_percent"] = proc.cpu_percent(interval=0.1)

                                # Memory usage in MB
                                mem_info = proc.memory_info()
                                status["memory_mb"] = mem_info.rss / (1024 * 1024)

                                # Runtime duration
                                create_time = proc.create_time()
                                status["runtime_seconds"] = int(time.time() - create_time)

                                # Thread count
                                status["num_threads"] = proc.num_threads()

                                # Command line
                                status["cmdline"] = " ".join(proc.cmdline())

                            except (psutil.AccessDenied, psutil.NoSuchProcess) as e:
                                status["process_error"] = f"Cannot access process info: {str(e)}"

                    else:
                        # Process exists but not running (shouldn't happen)
                        status["process_alive"] = False
                        status["process_status"] = "not_running"

                except psutil.NoSuchProcess:
                    # Process no longer exists but poll() hasn't detected it yet
                    status["process_alive"] = False
                    status["process_status"] = "terminated"
                    status["exit_code"] = process.wait()  # Get exit code

                except psutil.Error as e:
                    status["process_error"] = f"psutil error: {str(e)}"

            else:
                # Process has terminated
                status["process_alive"] = False
                status["process_status"] = "exited"
                status["exit_code"] = poll_result

                # Update state manager if process failed
                if poll_result != 0:
                    self.state_manager.mark_agent_failed(
                        agent_id,
                        f"Process exited with code {poll_result}"
                    )
                else:
                    # Successful exit
                    self.state_manager.mark_agent_completed(agent_id)

        # Load file-based status if available
        status_file = Path(info["status_file"])
        if status_file.exists():
            try:
                file_status = json.loads(status_file.read_text())
                status.update(file_status)
            except Exception as e:
                status["status_file_error"] = f"Could not read status file: {str(e)}"

        # Load persistent state
        persistent_state = self.state_manager.load_agent_state(agent_id)
        if persistent_state:
            status["persistent_status"] = persistent_state.get("status")
            status["started_at"] = persistent_state.get("started_at")
            status["progress"] = persistent_state.get("progress", 0)

        # Determine overall health status
        if status["is_zombie"]:
            status["health"] = "zombie"
        elif status["process_alive"]:
            status["health"] = "healthy"
        elif status.get("exit_code") == 0:
            status["health"] = "completed"
        elif status.get("exit_code") is not None:
            status["health"] = "failed"
        else:
            status["health"] = "unknown"

        return status

    def list_agents(self) -> Dict[str, Dict]:
        """List all managed agents"""
        result = {}
        for agent_id, info in self.agent_info.items():
            status = self.get_agent_status(agent_id)
            result[agent_id] = {
                **info,
                "current_status": status
            }
        return result

    def cleanup(self, agent_id: Optional[str] = None, force: bool = False):
        """
        Cleanup agent processes with graceful shutdown procedure

        Implements three-stage termination:
        1. SIGTERM - Request graceful shutdown (wait up to 10s)
        2. SIGTERM again - Give process another chance (wait up to 5s)
        3. SIGKILL - Force termination

        Also handles:
        - Zombie process reaping
        - Child process cleanup
        - State updates
        - Resource cleanup

        Args:
            agent_id: Specific agent to cleanup (None = all agents)
            force: If True, skip graceful shutdown and kill immediately
        """
        agents_to_cleanup = [agent_id] if agent_id else list(self.processes.keys())

        for current_agent_id in agents_to_cleanup:
            process = self.processes.get(current_agent_id)

            if process is None:
                continue

            print(f"Cleaning up agent {current_agent_id} (PID: {process.pid})")

            # Check if process already exited
            if process.poll() is not None:
                exit_code = process.returncode
                print(f"  Process already exited with code {exit_code}")

                # Update state based on exit code
                if exit_code == 0:
                    self.state_manager.mark_agent_completed(current_agent_id)
                else:
                    self.state_manager.mark_agent_failed(
                        current_agent_id,
                        f"Process exited with code {exit_code}"
                    )

                # Remove from tracking
                del self.processes[current_agent_id]
                continue

            try:
                # Get psutil Process object for advanced operations
                try:
                    proc = psutil.Process(process.pid)
                except psutil.NoSuchProcess:
                    print(f"  Process {process.pid} no longer exists")
                    del self.processes[current_agent_id]
                    continue

                # Check if it's a zombie - zombies can't be killed, only reaped
                if proc.status() == psutil.STATUS_ZOMBIE:
                    print(f"  Process is zombie - reaping")
                    try:
                        process.wait(timeout=1)
                    except subprocess.TimeoutExpired:
                        print(f"  Warning: Could not reap zombie process {process.pid}")
                    del self.processes[current_agent_id]
                    continue

                # Get all child processes before terminating parent
                children = []
                try:
                    children = proc.children(recursive=True)
                    print(f"  Found {len(children)} child processes")
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

                if force:
                    # Force kill immediately
                    print(f"  Force killing process {process.pid}")
                    try:
                        proc.kill()
                        process.wait(timeout=5)
                        print(f"  Process {process.pid} killed")
                    except subprocess.TimeoutExpired:
                        print(f"  Warning: Process {process.pid} did not die after SIGKILL")
                else:
                    # Stage 1: Graceful termination with SIGTERM
                    print(f"  Sending SIGTERM to process {process.pid}")
                    try:
                        proc.terminate()

                        # Wait up to 10 seconds for graceful shutdown
                        try:
                            process.wait(timeout=10)
                            print(f"  Process {process.pid} terminated gracefully")
                        except subprocess.TimeoutExpired:
                            print(f"  Process did not terminate after 10s")

                            # Stage 2: Send SIGTERM again (sometimes processes need it)
                            if proc.is_running():
                                print(f"  Sending SIGTERM again")
                                proc.terminate()
                                try:
                                    process.wait(timeout=5)
                                    print(f"  Process {process.pid} terminated")
                                except subprocess.TimeoutExpired:
                                    print(f"  Process still running after second SIGTERM")

                                    # Stage 3: Force kill with SIGKILL
                                    if proc.is_running():
                                        print(f"  Force killing with SIGKILL")
                                        proc.kill()
                                        try:
                                            process.wait(timeout=5)
                                            print(f"  Process {process.pid} killed")
                                        except subprocess.TimeoutExpired:
                                            print(f"  ERROR: Process {process.pid} did not die after SIGKILL")

                    except psutil.NoSuchProcess:
                        print(f"  Process {process.pid} already gone")

                # Cleanup child processes
                for child in children:
                    try:
                        if child.is_running():
                            print(f"  Terminating child process {child.pid}")
                            child.terminate()
                            try:
                                child.wait(timeout=3)
                            except psutil.TimeoutExpired:
                                child.kill()
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass

                # Update state to cancelled
                self.state_manager.save_agent_state(current_agent_id, {
                    "agent_id": current_agent_id,
                    "status": AgentStatus.CANCELLED.value,
                    "terminated_at": datetime.now().isoformat(),
                    "exit_code": process.returncode
                })

            except Exception as e:
                print(f"  Error during cleanup of {current_agent_id}: {str(e)}")

                # Try one last kill attempt
                try:
                    if process.poll() is None:
                        process.kill()
                        process.wait(timeout=3)
                except Exception as e2:
                    print(f"  Final kill attempt failed: {str(e2)}")

            finally:
                # Always remove from tracking dict
                if current_agent_id in self.processes:
                    del self.processes[current_agent_id]

        print(f"Cleanup complete. {len(self.processes)} processes still running")

    def monitor_all_agents(self) -> Dict[str, Dict]:
        """
        Monitor health of all running agents

        Returns:
            Dictionary with agent_id -> status for all agents
        """
        results = {}

        for agent_id in list(self.processes.keys()):
            try:
                status = self.get_agent_status(agent_id)
                results[agent_id] = status
            except Exception as e:
                results[agent_id] = {
                    "agent_id": agent_id,
                    "error": f"Failed to get status: {str(e)}",
                    "health": "error"
                }

        return results

    def reap_zombies(self) -> List[str]:
        """
        Find and reap any zombie processes

        Returns:
            List of agent IDs that were zombies and have been reaped
        """
        reaped = []

        for agent_id, process in list(self.processes.items()):
            try:
                proc = psutil.Process(process.pid)

                if proc.status() == psutil.STATUS_ZOMBIE:
                    print(f"Reaping zombie process {agent_id} (PID: {process.pid})")

                    # Try to reap the zombie
                    try:
                        process.wait(timeout=1)
                        reaped.append(agent_id)

                        # Update state
                        exit_code = process.returncode
                        if exit_code == 0:
                            self.state_manager.mark_agent_completed(agent_id)
                        else:
                            self.state_manager.mark_agent_failed(
                                agent_id,
                                f"Process became zombie with exit code {exit_code}"
                            )

                        # Remove from tracking
                        del self.processes[agent_id]

                    except subprocess.TimeoutExpired:
                        print(f"  Warning: Could not reap zombie {agent_id}")

            except psutil.NoSuchProcess:
                # Process gone - clean up tracking
                if agent_id in self.processes:
                    del self.processes[agent_id]
            except Exception as e:
                print(f"Error checking zombie status for {agent_id}: {e}")

        return reaped

    def get_process_summary(self) -> Dict:
        """
        Get summary statistics of all managed processes

        Returns:
            Dictionary with summary stats
        """
        summary = {
            "total_agents": len(self.processes),
            "running": 0,
            "zombie": 0,
            "completed": 0,
            "failed": 0,
            "total_memory_mb": 0.0,
            "total_cpu_percent": 0.0,
            "agents": []
        }

        for agent_id in list(self.processes.keys()):
            try:
                status = self.get_agent_status(agent_id)

                # Count by health status
                health = status.get("health", "unknown")
                if health == "healthy":
                    summary["running"] += 1
                elif health == "zombie":
                    summary["zombie"] += 1
                elif health == "completed":
                    summary["completed"] += 1
                elif health == "failed":
                    summary["failed"] += 1

                # Sum resource usage
                summary["total_memory_mb"] += status.get("memory_mb", 0.0)
                summary["total_cpu_percent"] += status.get("cpu_percent", 0.0)

                # Add to agents list
                summary["agents"].append({
                    "agent_id": agent_id,
                    "health": health,
                    "pid": status.get("pid"),
                    "memory_mb": status.get("memory_mb", 0.0),
                    "cpu_percent": status.get("cpu_percent", 0.0),
                    "runtime_seconds": status.get("runtime_seconds", 0)
                })

            except Exception as e:
                print(f"Error getting summary for {agent_id}: {e}")

        return summary

    def check_process_health(self, agent_id: str) -> bool:
        """
        Quick health check - returns True if process is alive and healthy

        Args:
            agent_id: Agent to check

        Returns:
            True if healthy, False otherwise
        """
        if agent_id not in self.processes:
            return False

        process = self.processes[agent_id]

        # Quick poll check
        if process.poll() is not None:
            return False

        # Check with psutil
        try:
            proc = psutil.Process(process.pid)
            return proc.is_running() and proc.status() != psutil.STATUS_ZOMBIE
        except (psutil.NoSuchProcess, psutil.Error):
            return False

    def kill_agent(self, agent_id: str, force: bool = False) -> bool:
        """
        Kill a specific agent process

        Args:
            agent_id: Agent to kill
            force: If True, use SIGKILL immediately

        Returns:
            True if successfully killed, False otherwise
        """
        if agent_id not in self.processes:
            return False

        try:
            self.cleanup(agent_id=agent_id, force=force)
            return True
        except Exception as e:
            print(f"Error killing agent {agent_id}: {e}")
            return False
