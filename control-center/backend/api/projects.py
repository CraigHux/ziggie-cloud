"""
Projects and Git Integration API
Monitor git repositories and project status
"""

from fastapi import APIRouter, HTTPException, Query, Request, Path as PathParam
from typing import List, Dict, Optional
from datetime import datetime
import subprocess
import os
from pathlib import Path
import json
from middleware.rate_limit import limiter
from utils.errors import UserFriendlyError, handle_file_error
from utils.pagination import paginate_list, PaginationParams
from utils.performance import track_performance

router = APIRouter(prefix="/api/projects", tags=["projects"])

# Project directories to scan
PROJECT_DIRS = [
    Path("C:/meowping-rts"),
    Path("C:/ComfyUI"),
    Path("C:/meowping-rts/ai-agents")
]


def run_git_command(repo_path: Path, command: List[str]) -> Dict:
    """Run a git command in a repository"""
    try:
        result = subprocess.run(
            ["git"] + command,
            cwd=str(repo_path),
            capture_output=True,
            text=True,
            timeout=10
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


def is_git_repo(path: Path) -> bool:
    """Check if a directory is a git repository"""
    git_dir = path / ".git"
    return git_dir.exists()


def get_git_status(repo_path: Path) -> Dict:
    """Get git status for a repository"""
    if not is_git_repo(repo_path):
        return {"is_git_repo": False}

    status = {"is_git_repo": True}

    # Get current branch
    branch_result = run_git_command(repo_path, ["branch", "--show-current"])
    if branch_result["success"]:
        status["branch"] = branch_result["stdout"]

    # Get status --porcelain for uncommitted changes
    status_result = run_git_command(repo_path, ["status", "--porcelain"])
    if status_result["success"]:
        lines = status_result["stdout"].split('\n')
        uncommitted = [line for line in lines if line.strip()]

        status["uncommitted_files"] = len(uncommitted)
        status["has_uncommitted_changes"] = len(uncommitted) > 0

        # Categorize changes
        status["changes"] = {
            "modified": len([l for l in uncommitted if l.startswith(' M') or l.startswith('M')]),
            "added": len([l for l in uncommitted if l.startswith('A')]),
            "deleted": len([l for l in uncommitted if l.startswith(' D') or l.startswith('D')]),
            "untracked": len([l for l in uncommitted if l.startswith('??')])
        }

    # Get last commit
    log_result = run_git_command(repo_path, ["log", "-1", "--format=%H|%an|%ae|%at|%s"])
    if log_result["success"] and log_result["stdout"]:
        parts = log_result["stdout"].split('|')
        if len(parts) >= 5:
            status["last_commit"] = {
                "hash": parts[0][:8],
                "full_hash": parts[0],
                "author": parts[1],
                "email": parts[2],
                "timestamp": datetime.fromtimestamp(int(parts[3])).isoformat(),
                "message": parts[4]
            }

    # Get remote info
    remote_result = run_git_command(repo_path, ["remote", "-v"])
    if remote_result["success"]:
        remotes = {}
        for line in remote_result["stdout"].split('\n'):
            if line.strip():
                parts = line.split()
                if len(parts) >= 2:
                    remote_name = parts[0]
                    remote_url = parts[1]
                    remotes[remote_name] = remote_url
        status["remotes"] = remotes

    # Check if ahead/behind remote
    if status.get("branch"):
        ahead_behind = run_git_command(
            repo_path,
            ["rev-list", "--left-right", "--count", f"origin/{status['branch']}...HEAD"]
        )
        if ahead_behind["success"] and ahead_behind["stdout"]:
            parts = ahead_behind["stdout"].split()
            if len(parts) == 2:
                status["behind"] = int(parts[0])
                status["ahead"] = int(parts[1])

    return status


def scan_project(path: Path) -> Optional[Dict]:
    """Scan a directory and gather project information"""
    if not path.exists():
        return None

    project = {
        "name": path.name,
        "path": str(path),
        "exists": True
    }

    # Check if it's a git repo
    git_status = get_git_status(path)
    project["git"] = git_status

    # Count files
    try:
        file_count = sum(1 for _ in path.rglob("*") if _.is_file())
        project["file_count"] = file_count
    except Exception:
        project["file_count"] = 0

    # Check for package.json (Node.js project)
    package_json = path / "package.json"
    if package_json.exists():
        try:
            with open(package_json, 'r', encoding='utf-8') as f:
                pkg_data = json.load(f)
                project["type"] = "nodejs"
                project["package"] = {
                    "name": pkg_data.get("name"),
                    "version": pkg_data.get("version"),
                    "description": pkg_data.get("description")
                }
        except Exception:
            project["type"] = "nodejs"

    # Check for requirements.txt (Python project)
    requirements = path / "requirements.txt"
    if requirements.exists():
        project["type"] = project.get("type", "python")
        try:
            with open(requirements, 'r', encoding='utf-8') as f:
                deps = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                project["python_dependencies"] = len(deps)
        except Exception:
            pass

    # Check for docker-compose.yml
    docker_compose = path / "docker-compose.yml"
    if docker_compose.exists():
        project["has_docker"] = True

    # Get directory size (approximate)
    try:
        total_size = sum(f.stat().st_size for f in path.rglob("*") if f.is_file())
        project["size_bytes"] = total_size
        project["size_mb"] = round(total_size / (1024 * 1024), 2)
    except Exception:
        project["size_bytes"] = 0
        project["size_mb"] = 0

    return project


@router.get("")
@limiter.limit("60/minute")
@track_performance(endpoint="GET /api/projects", query_type="project_scan")
async def list_projects(
    request: Request,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=200, description="Items per page (max 200)"),
    offset: Optional[int] = Query(None, ge=0, description="Alternative to page: start offset")
):
    """
    List all monitored projects with pagination

    - **page**: Page number (1-indexed)
    - **page_size**: Items per page (default 50, max 200)
    - **offset**: Alternative to page - start offset
    """
    try:
        projects = []

        for project_dir in PROJECT_DIRS:
            project = scan_project(project_dir)
            if project:
                projects.append(project)

        # Use pagination utility
        params = PaginationParams(page=page, page_size=page_size, offset=offset)
        result = paginate_list(projects, params, cached=False)

        # Rename 'items' to 'projects' for backward compatibility
        result['projects'] = result.pop('items')
        result['total'] = result['meta']['total']

        return result

    except Exception as e:
        UserFriendlyError.handle_error(e, context="listing projects", status_code=500)


@router.get("/{project_name}/status")
@limiter.limit("60/minute")
async def get_project_status(
    request: Request,
    project_name: str = PathParam(
        ...,
        min_length=1,
        max_length=100,
        description="Name of the project",
        pattern=r'^[a-zA-Z0-9_-]+$'
    )
):
    """Get detailed status for a specific project"""
    try:
        # Find the project
        project_path = None
        for path in PROJECT_DIRS:
            if path.name == project_name:
                project_path = path
                break

        if not project_path or not project_path.exists():
            UserFriendlyError.not_found("Project", project_name)

        project = scan_project(project_path)

        if not project:
            UserFriendlyError.handle_error(
                Exception("Could not load project"),
                context=f"loading project '{project_name}'",
                status_code=500
            )

        # Add more detailed status
        if project.get("git", {}).get("is_git_repo"):
            # Get detailed file status
            result = run_git_command(project_path, ["status", "--porcelain", "-uall"])
            if result["success"]:
                files = []
                for line in result["stdout"].split('\n'):
                    if line.strip():
                        status_code = line[:2]
                        filename = line[3:].strip()

                        # Decode status
                        status_desc = "modified"
                        if status_code.startswith('??'):
                            status_desc = "untracked"
                        elif status_code.startswith('A'):
                            status_desc = "added"
                        elif status_code.startswith('D'):
                            status_desc = "deleted"
                        elif status_code.startswith('M'):
                            status_desc = "modified"

                        files.append({
                            "file": filename,
                            "status": status_desc,
                            "status_code": status_code
                        })

                project["uncommitted_files_details"] = files[:50]  # First 50 files

        return project

    except HTTPException:
        raise
    except Exception as e:
        UserFriendlyError.handle_error(e, context=f"retrieving status for project '{project_name}'", status_code=500)


@router.get("/{project_name}/files")
async def browse_project_files(
    project_name: str = PathParam(
        ...,
        min_length=1,
        max_length=100,
        description="Name of the project",
        pattern=r'^[a-zA-Z0-9_-]+$'
    ),
    path: str = Query(
        "",
        description="Subpath within project",
        pattern=r'^[a-zA-Z0-9_./-]*$'  # Basic safe chars only
    ),
    pattern: str = Query(
        "*",
        description="File pattern to match",
        pattern=r'^[a-zA-Z0-9_.*?\-\[\]]+$'  # Safe glob patterns only
    )
):
    """Browse files in a project"""
    try:
        # Validate path doesn't contain directory traversal sequences
        if '..' in path or path.startswith('/') or path.startswith('\\'):
            raise HTTPException(
                status_code=422,
                detail="Invalid path: directory traversal or absolute paths not allowed"
            )

        # Find the project
        project_path = None
        for p in PROJECT_DIRS:
            if p.name == project_name:
                project_path = p
                break

        if not project_path or not project_path.exists():
            UserFriendlyError.not_found("Project", project_name)

        # Construct full path
        browse_path = project_path / path if path else project_path

        if not browse_path.exists():
            UserFriendlyError.not_found("Path", path)

        # List files
        files = []
        directories = []

        for item in browse_path.glob(pattern):
            try:
                stat = item.stat()

                entry = {
                    "name": item.name,
                    "path": str(item.relative_to(project_path)),
                    "size": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "is_dir": item.is_dir()
                }

                if item.is_dir():
                    directories.append(entry)
                else:
                    files.append(entry)
            except Exception:
                continue

        # Sort
        directories.sort(key=lambda x: x["name"])
        files.sort(key=lambda x: x["name"])

        return {
            "project": project_name,
            "current_path": path or "/",
            "total_dirs": len(directories),
            "total_files": len(files),
            "directories": directories,
            "files": files
        }

    except HTTPException:
        raise
    except Exception as e:
        UserFriendlyError.handle_error(e, context=f"browsing files in project '{project_name}'", status_code=500)


@router.get("/{project_name}/commits")
@limiter.limit("30/minute")
async def get_project_commits(request: Request,
    project_name: str = PathParam(
        ...,
        min_length=1,
        max_length=100,
        description="Name of the project",
        pattern=r'^[a-zA-Z0-9_-]+$'
    ),
    limit: int = Query(20, ge=1, le=100)
):
    """Get recent commits for a project"""
    try:
        # Find the project
        project_path = None
        for path in PROJECT_DIRS:
            if path.name == project_name:
                project_path = path
                break

        if not project_path or not project_path.exists():
            UserFriendlyError.not_found("Project", project_name)

        if not is_git_repo(project_path):
            return {
                "project": project_name,
                "is_git_repo": False,
                "commits": []
            }

        # Get commit log
        result = run_git_command(
            project_path,
            ["log", f"-{limit}", "--format=%H|%an|%ae|%at|%s"]
        )

        commits = []

        if result["success"]:
            for line in result["stdout"].split('\n'):
                if line.strip():
                    parts = line.split('|')
                    if len(parts) >= 5:
                        commits.append({
                            "hash": parts[0][:8],
                            "full_hash": parts[0],
                            "author": parts[1],
                            "email": parts[2],
                            "timestamp": datetime.fromtimestamp(int(parts[3])).isoformat(),
                            "message": parts[4]
                        })

        return {
            "project": project_name,
            "is_git_repo": True,
            "total": len(commits),
            "commits": commits
        }

    except HTTPException:
        raise
    except Exception as e:
        UserFriendlyError.handle_error(e, context=f"retrieving commits for project '{project_name}'", status_code=500)


@router.get("/{project_name}/branches")
@limiter.limit("30/minute")
async def get_project_branches(request: Request, project_name: str):
    """Get all branches for a project"""
    try:
        # Find the project
        project_path = None
        for path in PROJECT_DIRS:
            if path.name == project_name:
                project_path = path
                break

        if not project_path or not project_path.exists():
            UserFriendlyError.not_found("Project", project_name)

        if not is_git_repo(project_path):
            return {
                "project": project_name,
                "is_git_repo": False,
                "branches": []
            }

        # Get all branches
        result = run_git_command(project_path, ["branch", "-a", "-v"])

        branches = []
        current_branch = None

        if result["success"]:
            for line in result["stdout"].split('\n'):
                if line.strip():
                    is_current = line.startswith('*')
                    line_clean = line.lstrip('* ').strip()

                    parts = line_clean.split()
                    if parts:
                        branch_name = parts[0]
                        commit_hash = parts[1] if len(parts) > 1 else ""

                        branch_info = {
                            "name": branch_name,
                            "commit": commit_hash,
                            "is_current": is_current
                        }

                        branches.append(branch_info)

                        if is_current:
                            current_branch = branch_name

        return {
            "project": project_name,
            "is_git_repo": True,
            "current_branch": current_branch,
            "total": len(branches),
            "branches": branches
        }

    except HTTPException:
        raise
    except Exception as e:
        UserFriendlyError.handle_error(e, context=f"retrieving branches for project '{project_name}'", status_code=500)


@router.post("/{project_name}/refresh")
async def refresh_project_status(project_name: str):
    """Refresh git status for a project (fetch from remote)"""
    try:
        # Find the project
        project_path = None
        for path in PROJECT_DIRS:
            if path.name == project_name:
                project_path = path
                break

        if not project_path or not project_path.exists():
            UserFriendlyError.not_found("Project", project_name)

        if not is_git_repo(project_path):
            UserFriendlyError.validation_error(
                f"Project '{project_name}' is not a git repository",
                field="project_name"
            )

        # Run git fetch
        result = run_git_command(project_path, ["fetch", "--all"])

        if result["success"]:
            # Get updated status
            status = get_git_status(project_path)

            return {
                "project": project_name,
                "status": "refreshed",
                "git_status": status,
                "message": "Successfully fetched from remote"
            }
        else:
            return {
                "project": project_name,
                "status": "failed",
                "error": result.get("stderr") or result.get("error"),
                "message": "Failed to fetch from remote"
            }

    except HTTPException:
        raise
    except Exception as e:
        UserFriendlyError.handle_error(e, context=f"refreshing project '{project_name}'", status_code=500)
