"""
ComfyUI Integration API
Control and monitor ComfyUI server
"""

from fastapi import Request, APIRouter, HTTPException
from typing import Optional, Dict
from datetime import datetime
import subprocess
import psutil
import socket
import os
from pathlib import Path
import json
from middleware.rate_limit import limiter

router = APIRouter(prefix="/api/comfyui", tags=["comfyui"])

# ComfyUI configuration
COMFYUI_ROOT = Path("C:/ComfyUI")
COMFYUI_PYTHON = COMFYUI_ROOT / "python_embeded" / "python.exe"
COMFYUI_MAIN = COMFYUI_ROOT / "ComfyUI" / "main.py"
COMFYUI_DEFAULT_PORT = 8188
COMFYUI_LOG_FILE = COMFYUI_ROOT / "logs" / "comfyui.log"


def find_comfyui_process() -> Optional[psutil.Process]:
    """Find running ComfyUI process"""
    try:
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info.get('cmdline', [])
                if cmdline and any('ComfyUI' in arg and 'main.py' in arg for arg in cmdline):
                    return proc
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    except Exception:
        pass
    return None


def check_port_in_use(port: int) -> bool:
    """Check if a port is in use"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) == 0
    except Exception:
        return False


def get_comfyui_api_status(port: int) -> Dict:
    """Check if ComfyUI API is responding"""
    try:
        import requests
        response = requests.get(f"http://localhost:{port}/system_stats", timeout=2)
        if response.status_code == 200:
            return {
                "api_responding": True,
                "api_data": response.json()
            }
    except Exception as e:
        return {
            "api_responding": False,
            "error": str(e)
        }

    return {"api_responding": False}


@router.get("/status")
@limiter.limit("60/minute")
async def get_comfyui_status(request: Request, ):
    """Check ComfyUI server status"""
    try:
        process = find_comfyui_process()

        if process:
            try:
                # Get process info
                cpu_percent = process.cpu_percent(interval=0.1)
                memory_info = process.memory_info()

                # Check if API is responding
                port = COMFYUI_DEFAULT_PORT
                api_status = get_comfyui_api_status(port)

                return {
                    "running": True,
                    "pid": process.pid,
                    "status": "running",
                    "port": port,
                    "url": f"http://localhost:{port}",
                    "cpu_percent": cpu_percent,
                    "memory_mb": round(memory_info.rss / (1024 * 1024), 2),
                    "api_responding": api_status.get('api_responding', False),
                    "uptime_seconds": (datetime.now().timestamp() - process.create_time()),
                    "system_stats": api_status.get('api_data', None)
                }
            except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                return {
                    "running": False,
                    "status": "process_found_but_no_access",
                    "error": str(e)
                }
        else:
            # Check if port is in use (might be running but not detected)
            port_in_use = check_port_in_use(COMFYUI_DEFAULT_PORT)

            return {
                "running": False,
                "status": "not_running",
                "port_in_use": port_in_use,
                "message": "ComfyUI process not found" if not port_in_use else "Port in use but process not detected"
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking ComfyUI status: {str(e)}")


@router.get("/port")
@limiter.limit("60/minute")
async def get_comfyui_port(request: Request, ):
    """Get ComfyUI server port"""
    try:
        # First check default port
        if check_port_in_use(COMFYUI_DEFAULT_PORT):
            return {
                "port": COMFYUI_DEFAULT_PORT,
                "url": f"http://localhost:{COMFYUI_DEFAULT_PORT}",
                "in_use": True
            }

        # Check alternative ports
        alternative_ports = [8189, 8190, 8191, 8080, 3000]

        for port in alternative_ports:
            if check_port_in_use(port):
                # Try to verify it's ComfyUI
                api_status = get_comfyui_api_status(port)
                if api_status.get('api_responding'):
                    return {
                        "port": port,
                        "url": f"http://localhost:{port}",
                        "in_use": True,
                        "note": "ComfyUI detected on alternative port"
                    }

        return {
            "port": COMFYUI_DEFAULT_PORT,
            "url": f"http://localhost:{COMFYUI_DEFAULT_PORT}",
            "in_use": False,
            "message": "ComfyUI not detected on any port"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting ComfyUI port: {str(e)}")


@router.post("/start")
@limiter.limit("10/minute")
async def start_comfyui(request: Request, 
    cpu_only: bool = True,
    port: Optional[int] = None
):
    """Start ComfyUI server"""
    try:
        # Check if already running
        if find_comfyui_process():
            return {
                "status": "already_running",
                "message": "ComfyUI is already running",
                "port": port or COMFYUI_DEFAULT_PORT
            }

        # Verify paths exist
        if not COMFYUI_PYTHON.exists():
            raise HTTPException(
                status_code=404,
                detail=f"ComfyUI Python not found at {COMFYUI_PYTHON}"
            )

        if not COMFYUI_MAIN.exists():
            raise HTTPException(
                status_code=404,
                detail=f"ComfyUI main.py not found at {COMFYUI_MAIN}"
            )

        # Build command
        cmd = [
            str(COMFYUI_PYTHON),
            "-s",
            str(COMFYUI_MAIN),
            "--windows-standalone-build"
        ]

        if cpu_only:
            cmd.append("--cpu")

        if port:
            cmd.extend(["--port", str(port)])

        # Create logs directory
        COMFYUI_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

        # Start process in background
        with open(COMFYUI_LOG_FILE, 'w') as log_file:
            process = subprocess.Popen(
                cmd,
                cwd=str(COMFYUI_ROOT),
                stdout=log_file,
                stderr=subprocess.STDOUT,
                creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
            )

        # Give it a moment to start
        import time
        time.sleep(2)

        # Verify it started
        if find_comfyui_process():
            return {
                "status": "started",
                "pid": process.pid,
                "port": port or COMFYUI_DEFAULT_PORT,
                "url": f"http://localhost:{port or COMFYUI_DEFAULT_PORT}",
                "command": " ".join(cmd),
                "log_file": str(COMFYUI_LOG_FILE),
                "message": "ComfyUI started successfully. Check log file for details."
            }
        else:
            return {
                "status": "start_failed",
                "message": "Process started but not detected running. Check logs.",
                "log_file": str(COMFYUI_LOG_FILE)
            }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting ComfyUI: {str(e)}")


@router.post("/stop")
@limiter.limit("10/minute")
async def stop_comfyui(request: Request, ):
    """Stop ComfyUI server"""
    try:
        process = find_comfyui_process()

        if not process:
            return {
                "status": "not_running",
                "message": "ComfyUI is not running"
            }

        pid = process.pid

        # Try graceful shutdown first
        try:
            process.terminate()

            # Wait up to 10 seconds for graceful shutdown
            import time
            for _ in range(10):
                if not find_comfyui_process():
                    return {
                        "status": "stopped",
                        "pid": pid,
                        "message": "ComfyUI stopped gracefully"
                    }
                time.sleep(1)

            # Force kill if still running
            if find_comfyui_process():
                process.kill()

                # Wait 2 more seconds
                time.sleep(2)

                if not find_comfyui_process():
                    return {
                        "status": "stopped",
                        "pid": pid,
                        "message": "ComfyUI force stopped",
                        "note": "Had to use force kill"
                    }
                else:
                    raise HTTPException(
                        status_code=500,
                        detail="Failed to stop ComfyUI process"
                    )

        except psutil.NoSuchProcess:
            return {
                "status": "stopped",
                "pid": pid,
                "message": "Process already stopped"
            }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error stopping ComfyUI: {str(e)}")


@router.get("/logs")
@limiter.limit("30/minute")
async def get_comfyui_logs(request: Request, lines: int = 50):
    """Get recent ComfyUI log entries"""
    try:
        if not COMFYUI_LOG_FILE.exists():
            return {
                "message": "Log file not found",
                "log_file": str(COMFYUI_LOG_FILE),
                "logs": []
            }

        # Read last N lines
        with open(COMFYUI_LOG_FILE, 'r', encoding='utf-8', errors='ignore') as f:
            all_lines = f.readlines()
            recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines

        return {
            "log_file": str(COMFYUI_LOG_FILE),
            "total_lines": len(all_lines),
            "returned_lines": len(recent_lines),
            "logs": [line.strip() for line in recent_lines]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading logs: {str(e)}")


@router.get("/config")
@limiter.limit("60/minute")
async def get_comfyui_config(request: Request, ):
    """Get ComfyUI configuration"""
    try:
        config = {
            "comfyui_root": str(COMFYUI_ROOT),
            "python_path": str(COMFYUI_PYTHON),
            "main_script": str(COMFYUI_MAIN),
            "default_port": COMFYUI_DEFAULT_PORT,
            "log_file": str(COMFYUI_LOG_FILE),
            "paths_exist": {
                "root": COMFYUI_ROOT.exists(),
                "python": COMFYUI_PYTHON.exists(),
                "main": COMFYUI_MAIN.exists()
            }
        }

        # Check for custom_nodes
        custom_nodes_dir = COMFYUI_ROOT / "ComfyUI" / "custom_nodes"
        if custom_nodes_dir.exists():
            custom_nodes = [
                d.name for d in custom_nodes_dir.iterdir()
                if d.is_dir() and not d.name.startswith('.')
            ]
            config["custom_nodes"] = custom_nodes
            config["custom_nodes_count"] = len(custom_nodes)

        # Check for models
        models_dir = COMFYUI_ROOT / "ComfyUI" / "models"
        if models_dir.exists():
            model_types = [
                d.name for d in models_dir.iterdir()
                if d.is_dir()
            ]
            config["model_types"] = model_types

        return config

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting config: {str(e)}")


@router.get("/workflows")
async def list_workflows():
    """List available ComfyUI workflows"""
    try:
        workflows_dir = COMFYUI_ROOT / "ComfyUI" / "user" / "default" / "workflows"

        if not workflows_dir.exists():
            return {
                "message": "Workflows directory not found",
                "workflows": []
            }

        workflows = []

        for file_path in workflows_dir.glob("*.json"):
            try:
                stat = os.stat(file_path)

                # Try to load workflow metadata
                with open(file_path, 'r', encoding='utf-8') as f:
                    workflow_data = json.load(f)

                workflows.append({
                    "name": file_path.stem,
                    "filename": file_path.name,
                    "path": str(file_path),
                    "size": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "nodes_count": len(workflow_data.get("nodes", [])) if isinstance(workflow_data, dict) else 0
                })
            except Exception:
                continue

        return {
            "workflows_dir": str(workflows_dir),
            "total": len(workflows),
            "workflows": workflows
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing workflows: {str(e)}")


@router.get("/health")
async def check_comfyui_health():
    """Comprehensive health check for ComfyUI"""
    try:
        health = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "unknown"
        }

        # Check process
        process = find_comfyui_process()
        health["process_running"] = process is not None

        if process:
            health["pid"] = process.pid

        # Check port
        port_status = check_port_in_use(COMFYUI_DEFAULT_PORT)
        health["port_accessible"] = port_status

        # Check API
        if port_status:
            api_status = get_comfyui_api_status(COMFYUI_DEFAULT_PORT)
            health["api_responding"] = api_status.get('api_responding', False)
        else:
            health["api_responding"] = False

        # Check paths
        health["paths_valid"] = {
            "root": COMFYUI_ROOT.exists(),
            "python": COMFYUI_PYTHON.exists(),
            "main": COMFYUI_MAIN.exists()
        }

        # Determine overall status
        if process and health["api_responding"]:
            health["overall_status"] = "healthy"
        elif process and not health["api_responding"]:
            health["overall_status"] = "starting"
        elif not process and port_status:
            health["overall_status"] = "unknown_process"
        else:
            health["overall_status"] = "not_running"

        return health

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking health: {str(e)}")
