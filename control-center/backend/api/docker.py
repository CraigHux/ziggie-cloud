"""
Docker Integration API
Control and monitor Docker containers
"""

from fastapi import Request, APIRouter, HTTPException, Query, Path
from typing import List, Dict, Optional
from datetime import datetime
import subprocess
import json
from middleware.rate_limit import limiter

router = APIRouter(prefix="/api/docker", tags=["docker"])


def check_docker_installed() -> bool:
    """Check if Docker is installed and running"""
    try:
        result = subprocess.run(
            ["docker", "version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except Exception:
        return False


def run_docker_command(command: List[str]) -> Dict:
    """Run a docker command"""
    try:
        result = subprocess.run(
            ["docker"] + command,
            capture_output=True,
            text=True,
            timeout=30
        )

        return {
            "success": result.returncode == 0,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "returncode": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "Command timed out"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@router.get("/status")
@limiter.limit("60/minute")
async def get_docker_status(request: Request, ):
    """Check Docker installation and daemon status"""
    try:
        if not check_docker_installed():
            return {
                "installed": False,
                "running": False,
                "message": "Docker is not installed or not in PATH"
            }

        # Get Docker info
        info_result = run_docker_command(["info", "--format", "{{json .}}"])

        if not info_result["success"]:
            return {
                "installed": True,
                "running": False,
                "error": info_result.get("stderr") or info_result.get("error"),
                "message": "Docker is installed but daemon is not running"
            }

        # Parse info
        try:
            info_data = json.loads(info_result["stdout"])

            return {
                "installed": True,
                "running": True,
                "version": info_data.get("ServerVersion"),
                "containers": info_data.get("Containers", 0),
                "containers_running": info_data.get("ContainersRunning", 0),
                "containers_paused": info_data.get("ContainersPaused", 0),
                "containers_stopped": info_data.get("ContainersStopped", 0),
                "images": info_data.get("Images", 0),
                "driver": info_data.get("Driver"),
                "os": info_data.get("OperatingSystem")
            }
        except json.JSONDecodeError:
            return {
                "installed": True,
                "running": True,
                "message": "Docker is running but could not parse info"
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking Docker status: {str(e)}")


@router.get("/containers")
@limiter.limit("60/minute")
async def list_containers(request: Request, 
    all: bool = Query(True, description="Show all containers (default: running only)")
):
    """List Docker containers"""
    try:
        if not check_docker_installed():
            raise HTTPException(status_code=503, detail="Docker is not available")

        # Build command
        cmd = ["ps", "--format", "{{json .}}"]
        if all:
            cmd.append("--all")

        result = run_docker_command(cmd)

        if not result["success"]:
            raise HTTPException(
                status_code=500,
                detail=f"Error listing containers: {result.get('stderr') or result.get('error')}"
            )

        # Parse containers
        containers = []
        for line in result["stdout"].split('\n'):
            if line.strip():
                try:
                    container = json.loads(line)
                    containers.append({
                        "id": container.get("ID"),
                        "name": container.get("Names"),
                        "image": container.get("Image"),
                        "status": container.get("Status"),
                        "state": container.get("State"),
                        "ports": container.get("Ports"),
                        "created": container.get("CreatedAt")
                    })
                except json.JSONDecodeError:
                    continue

        return {
            "total": len(containers),
            "containers": containers
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing containers: {str(e)}")


@router.get("/container/{container_id}")
@limiter.limit("60/minute")
async def get_container_details(
    request: Request,
    container_id: str = Path(
        ...,
        min_length=1,
        max_length=100,
        description="Container ID or name",
        pattern=r'^[a-zA-Z0-9_.-]+$'
    )
):
    """Get detailed information about a container"""
    try:
        if not check_docker_installed():
            raise HTTPException(status_code=503, detail="Docker is not available")

        result = run_docker_command(["inspect", container_id])

        if not result["success"]:
            raise HTTPException(
                status_code=404,
                detail=f"Container not found or error: {result.get('stderr') or result.get('error')}"
            )

        # Parse inspect output
        try:
            inspect_data = json.loads(result["stdout"])

            if not inspect_data:
                raise HTTPException(status_code=404, detail="Container not found")

            container = inspect_data[0]

            # Extract key information
            state = container.get("State", {})
            config = container.get("Config", {})
            network_settings = container.get("NetworkSettings", {})

            return {
                "id": container.get("Id"),
                "name": container.get("Name", "").lstrip("/"),
                "image": config.get("Image"),
                "state": {
                    "status": state.get("Status"),
                    "running": state.get("Running"),
                    "paused": state.get("Paused"),
                    "restarting": state.get("Restarting"),
                    "pid": state.get("Pid"),
                    "started_at": state.get("StartedAt"),
                    "finished_at": state.get("FinishedAt")
                },
                "network": {
                    "ip_address": network_settings.get("IPAddress"),
                    "ports": network_settings.get("Ports", {}),
                    "networks": list(network_settings.get("Networks", {}).keys())
                },
                "mounts": container.get("Mounts", []),
                "config": {
                    "hostname": config.get("Hostname"),
                    "env": config.get("Env", []),
                    "cmd": config.get("Cmd"),
                    "working_dir": config.get("WorkingDir")
                }
            }

        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="Error parsing container details")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting container details: {str(e)}")


@router.post("/container/{container_id}/start")
@limiter.limit("10/minute")
async def start_container(
    request: Request,
    container_id: str = Path(
        ...,
        min_length=1,
        max_length=100,
        description="Container ID or name",
        pattern=r'^[a-zA-Z0-9_.-]+$'
    )
):
    """Start a Docker container"""
    try:
        if not check_docker_installed():
            raise HTTPException(status_code=503, detail="Docker is not available")

        result = run_docker_command(["start", container_id])

        if result["success"]:
            return {
                "status": "started",
                "container_id": container_id,
                "message": f"Container {container_id} started successfully"
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to start container: {result.get('stderr') or result.get('error')}"
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting container: {str(e)}")


@router.post("/container/{container_id}/stop")
@limiter.limit("10/minute")
async def stop_container(
    request: Request,
    container_id: str = Path(
        ...,
        min_length=1,
        max_length=100,
        description="Container ID or name",
        pattern=r'^[a-zA-Z0-9_.-]+$'
    ),
    timeout: int = Query(10, ge=1, le=300)
):
    """Stop a Docker container"""
    try:
        if not check_docker_installed():
            raise HTTPException(status_code=503, detail="Docker is not available")

        result = run_docker_command(["stop", "--time", str(timeout), container_id])

        if result["success"]:
            return {
                "status": "stopped",
                "container_id": container_id,
                "message": f"Container {container_id} stopped successfully"
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to stop container: {result.get('stderr') or result.get('error')}"
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error stopping container: {str(e)}")


@router.post("/container/{container_id}/restart")
@limiter.limit("10/minute")
async def restart_container(
    request: Request,
    container_id: str = Path(
        ...,
        min_length=1,
        max_length=100,
        description="Container ID or name",
        pattern=r'^[a-zA-Z0-9_.-]+$'
    )
):
    """Restart a Docker container"""
    try:
        if not check_docker_installed():
            raise HTTPException(status_code=503, detail="Docker is not available")

        result = run_docker_command(["restart", container_id])

        if result["success"]:
            return {
                "status": "restarted",
                "container_id": container_id,
                "message": f"Container {container_id} restarted successfully"
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to restart container: {result.get('stderr') or result.get('error')}"
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error restarting container: {str(e)}")


@router.get("/container/{container_id}/logs")
@limiter.limit("30/minute")
async def get_container_logs(
    request: Request,
    container_id: str = Path(
        ...,
        min_length=1,
        max_length=100,
        description="Container ID or name",
        pattern=r'^[a-zA-Z0-9_.-]+$'
    ),
    tail: int = Query(100, ge=1, le=1000),
    timestamps: bool = Query(False, description="Include timestamps in logs"),
    since: Optional[str] = Query(
        default=None,
        description="Show logs since timestamp (e.g., '10m', '1h', '2d')",
        pattern=r'^[0-9]+[smhd]$'
    ),
    follow: bool = False
):
    """Get logs from a Docker container"""
    try:
        if not check_docker_installed():
            raise HTTPException(status_code=503, detail="Docker is not available")

        cmd = ["logs", "--tail", str(tail)]
        if not follow:
            cmd.append("--timestamps")

        cmd.append(container_id)

        result = run_docker_command(cmd)

        if result["success"]:
            logs = result["stdout"].split('\n')

            return {
                "container_id": container_id,
                "total_lines": len(logs),
                "logs": logs
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get logs: {result.get('stderr') or result.get('error')}"
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting container logs: {str(e)}")


@router.get("/images")
@limiter.limit("60/minute")
async def list_images(request: Request, ):
    """List Docker images"""
    try:
        if not check_docker_installed():
            raise HTTPException(status_code=503, detail="Docker is not available")

        result = run_docker_command(["images", "--format", "{{json .}}"])

        if not result["success"]:
            raise HTTPException(
                status_code=500,
                detail=f"Error listing images: {result.get('stderr') or result.get('error')}"
            )

        # Parse images
        images = []
        for line in result["stdout"].split('\n'):
            if line.strip():
                try:
                    image = json.loads(line)
                    images.append({
                        "id": image.get("ID"),
                        "repository": image.get("Repository"),
                        "tag": image.get("Tag"),
                        "size": image.get("Size"),
                        "created": image.get("CreatedAt")
                    })
                except json.JSONDecodeError:
                    continue

        return {
            "total": len(images),
            "images": images
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing images: {str(e)}")


@router.get("/compose/projects")
@limiter.limit("60/minute")
async def list_compose_projects(request: Request, ):
    """List Docker Compose projects"""
    try:
        if not check_docker_installed():
            raise HTTPException(status_code=503, detail="Docker is not available")

        # Check if docker-compose is available
        compose_check = subprocess.run(
            ["docker-compose", "version"],
            capture_output=True,
            text=True,
            timeout=5
        )

        if compose_check.returncode != 0:
            # Try docker compose (v2)
            compose_check = subprocess.run(
                ["docker", "compose", "version"],
                capture_output=True,
                text=True,
                timeout=5
            )

            if compose_check.returncode != 0:
                return {
                    "available": False,
                    "message": "Docker Compose not available",
                    "projects": []
                }

        # List containers with compose project labels
        result = run_docker_command([
            "ps",
            "--filter", "label=com.docker.compose.project",
            "--format", "{{json .}}"
        ])

        projects = {}

        if result["success"]:
            for line in result["stdout"].split('\n'):
                if line.strip():
                    try:
                        container = json.loads(line)

                        # Extract project from labels
                        labels = container.get("Labels", "")
                        project_match = [l for l in labels.split(',') if 'com.docker.compose.project=' in l]

                        if project_match:
                            project_name = project_match[0].split('=')[1]

                            if project_name not in projects:
                                projects[project_name] = {
                                    "name": project_name,
                                    "containers": []
                                }

                            projects[project_name]["containers"].append({
                                "name": container.get("Names"),
                                "status": container.get("Status")
                            })
                    except json.JSONDecodeError:
                        continue

        return {
            "available": True,
            "total": len(projects),
            "projects": list(projects.values())
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing compose projects: {str(e)}")


@router.get("/stats")
@limiter.limit("30/minute")
async def get_docker_stats(request: Request, ):
    """Get Docker resource usage statistics"""
    try:
        if not check_docker_installed():
            raise HTTPException(status_code=503, detail="Docker is not available")

        result = run_docker_command([
            "stats",
            "--no-stream",
            "--format", "{{json .}}"
        ])

        if not result["success"]:
            raise HTTPException(
                status_code=500,
                detail=f"Error getting stats: {result.get('stderr') or result.get('error')}"
            )

        # Parse stats
        stats = []
        for line in result["stdout"].split('\n'):
            if line.strip():
                try:
                    stat = json.loads(line)
                    stats.append({
                        "container": stat.get("Name"),
                        "cpu_percent": stat.get("CPUPerc"),
                        "memory_usage": stat.get("MemUsage"),
                        "memory_percent": stat.get("MemPerc"),
                        "net_io": stat.get("NetIO"),
                        "block_io": stat.get("BlockIO")
                    })
                except json.JSONDecodeError:
                    continue

        return {
            "timestamp": datetime.now().isoformat(),
            "total_containers": len(stats),
            "stats": stats
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting Docker stats: {str(e)}")
