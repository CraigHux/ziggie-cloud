"""
File Watcher
Monitors deployment request directory and processes new requests
"""

import time
import json
from pathlib import Path
from typing import Callable
from watchdog.observers.polling import PollingObserver
from watchdog.events import FileSystemEventHandler, FileCreatedEvent
from .schemas import DeploymentRequest, DeploymentResponse
from .agent_spawner import AgentSpawner
from .state_manager import StateManager


class DeploymentRequestHandler(FileSystemEventHandler):
    """Handles new deployment request files"""

    def __init__(self, requests_dir: Path, responses_dir: Path, spawner: AgentSpawner, log_callback: Callable = None):
        self.requests_dir = requests_dir
        self.responses_dir = responses_dir
        self.spawner = spawner
        self.log = log_callback or print
        self.processed_files = set()

    def on_created(self, event):
        """Handle new file creation"""
        if event.is_directory:
            return

        file_path = Path(event.src_path)

        # Only process JSON files
        if file_path.suffix != ".json":
            return

        # Avoid processing the same file twice
        if str(file_path) in self.processed_files:
            return

        self.processed_files.add(str(file_path))

        # Small delay to ensure file is fully written
        time.sleep(0.1)

        try:
            self.process_request(file_path)
        except Exception as e:
            self.log(f"[ERROR] Failed to process {file_path.name}: {e}")

    def process_request(self, request_file: Path):
        """Process a deployment request file"""
        self.log(f"[INFO] Processing deployment request: {request_file.name}")

        try:
            # Parse request
            request_data = json.loads(request_file.read_text())
            request = DeploymentRequest(**request_data)

            self.log(f"[INFO] Deploying agent {request.agent_id} ({request.agent_name})")

            # Spawn agent
            response = self.spawner.spawn_agent(request)

            # Write response
            response_file = self.responses_dir / f"{request.request_id}_response.json"
            response_file.write_text(response.model_dump_json(indent=2))

            self.log(f"[SUCCESS] Agent {request.agent_id} deployed - PID: {response.pid}")

        except Exception as e:
            self.log(f"[ERROR] Deployment failed: {e}")

            # Write error response
            try:
                error_response = DeploymentResponse(
                    request_id=request_data.get("request_id", "unknown"),
                    agent_id=request_data.get("agent_id", "unknown"),
                    status="failed",
                    message="Deployment failed",
                    error=str(e)
                )
                response_file = self.responses_dir / f"{request_data.get('request_id', 'unknown')}_response.json"
                response_file.write_text(error_response.model_dump_json(indent=2))
            except:
                pass


class DeploymentWatcher:
    """Watches deployment directory for new requests"""

    def __init__(self, deployment_dir: Path, log_callback: Callable = None):
        self.deployment_dir = deployment_dir
        self.requests_dir = deployment_dir / "requests"
        self.responses_dir = deployment_dir / "responses"
        self.log = log_callback or print

        # Ensure directories exist
        self.requests_dir.mkdir(parents=True, exist_ok=True)
        self.responses_dir.mkdir(parents=True, exist_ok=True)

        # Create state manager
        self.state_manager = StateManager(deployment_dir)

        # Create spawner with state manager
        self.spawner = AgentSpawner(deployment_dir, self.state_manager)

        # Create event handler
        self.event_handler = DeploymentRequestHandler(
            self.requests_dir,
            self.responses_dir,
            self.spawner,
            self.log
        )

        # Create observer (using PollingObserver for better cross-platform compatibility)
        self.observer = PollingObserver()
        self.observer.schedule(self.event_handler, str(self.requests_dir), recursive=False)

    def start(self):
        """Start watching for deployment requests"""
        self.log(f"[COORDINATOR] Starting deployment watcher...")
        self.log(f"[COORDINATOR] Monitoring: {self.requests_dir}")

        # Check for incomplete agents (recovery)
        recovery_summary = self.state_manager.get_recovery_summary()
        if recovery_summary["total_incomplete"] > 0:
            self.log(f"[RECOVERY] Found {recovery_summary['total_incomplete']} incomplete agents")
            for status, count in recovery_summary["by_status"].items():
                self.log(f"[RECOVERY]   - {status}: {count}")
            for agent_type, count in recovery_summary["by_type"].items():
                self.log(f"[RECOVERY]   - {agent_type}: {count}")
            self.log(f"[RECOVERY] Agent states preserved for resumption")
        else:
            self.log(f"[RECOVERY] No incomplete agents found")

        self.observer.start()
        self.log(f"[COORDINATOR] Watcher started successfully")

    def stop(self):
        """Stop watching"""
        self.log(f"[COORDINATOR] Stopping watcher...")
        self.observer.stop()
        self.observer.join()
        self.spawner.cleanup()
        self.log(f"[COORDINATOR] Watcher stopped")

    def run(self):
        """Run watcher (blocking)"""
        self.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()
