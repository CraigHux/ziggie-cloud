#!/usr/bin/env python3
"""Script to add rate limiting to all API endpoints."""
import re
from pathlib import Path

# Base directory
API_DIR = Path(__file__).parent / "api"

# Rate limit configurations
RATE_LIMITS = {
    # agents.py
    "agents.py": {
        "list_all_agents": "60/minute",
        "get_agent_stats": "60/minute",
        "get_agent_details": "60/minute",
        "get_agent_knowledge": "30/minute",
        "get_agent_hierarchy": "60/minute",
        "invalidate_agents_cache": "10/minute",
        "get_cache_stats": "30/minute",
    },

    # services.py
    "services.py": {
        "get_services": "60/minute",
        "start_service": "10/minute",
        "stop_service": "10/minute",
        "get_service_status": "60/minute",
        "get_service_logs": "30/minute",
    },

    # docker.py
    "docker.py": {
        "get_docker_status": "60/minute",
        "list_containers": "60/minute",
        "get_container_details": "60/minute",
        "start_container": "10/minute",
        "stop_container": "10/minute",
        "restart_container": "10/minute",
        "get_container_logs": "30/minute",
        "list_images": "60/minute",
        "list_compose_projects": "60/minute",
        "get_docker_stats": "30/minute",
    },

    # system.py
    "system.py": {
        "get_system_stats": "60/minute",
        "get_processes": "60/minute",
        "get_ports": "30/minute",
    },

    # knowledge.py
    "knowledge.py": {
        "get_knowledge_stats": "60/minute",
        "get_knowledge_files": "60/minute",
        "get_file_details": "60/minute",
        "get_creators": "60/minute",
        "get_creator_details": "60/minute",
        "scan_knowledge_base": "10/minute",
        "get_scan_jobs": "30/minute",
        "search_knowledge": "30/minute",
    },

    # projects.py
    "projects.py": {
        "list_projects": "60/minute",
        "get_project_status": "60/minute",
        "get_project_files": "60/minute",
        "get_project_commits": "30/minute",
        "get_project_branches": "30/minute",
        "refresh_project": "10/minute",
    },

    # usage.py
    "usage.py": {
        "get_usage_stats": "60/minute",
        "get_usage_history": "60/minute",
        "track_usage": "30/minute",
        "get_pricing": "60/minute",
        "estimate_cost": "30/minute",
        "get_usage_summary": "60/minute",
    },

    # comfyui.py
    "comfyui.py": {
        "get_comfyui_status": "60/minute",
        "get_comfyui_port": "60/minute",
        "start_comfyui": "10/minute",
        "stop_comfyui": "10/minute",
        "get_comfyui_logs": "30/minute",
        "get_comfyui_config": "60/minute",
        "get_workflows": "60/minute",
        "get_comfyui_health": "100/minute",
    },
}

def add_rate_limits_to_file(filepath, limits_dict):
    """Add rate limiting decorators to a Python file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Find import lines and add rate limiter if needed
    import_added = False
    request_added = False

    for i, line in enumerate(lines):
        if "from fastapi import" in line and not import_added:
            if "Request" not in line:
                lines[i] = line.rstrip() + ", Request\n"
                request_added = True
            import_added = True

        if "from middleware.rate_limit import limiter" not in ''.join(lines[:min(i+10, len(lines))]):
            if "from utils.cache" in line or ("from api import" in line):
                lines.insert(i+1, "from middleware.rate_limit import limiter\n")
                break

    # Add decorators before functions
    i = 0
    while i < len(lines):
        line = lines[i]

        # Look for @router.get, @router.post, etc.
        if '@router.' in line and i + 1 < len(lines):
            next_line = lines[i + 1]

            # Find the function name
            for func_name, limit in limits_dict.items():
                if f'async def {func_name}(' in next_line or f'def {func_name}(' in next_line:
                    # Check if limiter already applied
                    if i > 0 and '@limiter.limit' not in lines[i]:
                        # Add limiter decorator and request parameter
                        lines.insert(i + 1, f'@limiter.limit("{limit}")\n')

                        # Add request parameter if not present
                        func_line_idx = i + 2
                        if f'async def {func_name}(' in lines[func_line_idx]:
                            if 'request: Request' not in lines[func_line_idx]:
                                # Find opening parenthesis
                                lines[func_line_idx] = lines[func_line_idx].replace(
                                    f'async def {func_name}(',
                                    f'async def {func_name}(request: Request, '
                                )
                        break
        i += 1

    return ''.join(lines)


# Process each file
for filename, limits in RATE_LIMITS.items():
    filepath = API_DIR / filename
    if filepath.exists():
        print(f"Processing {filename}...")
        try:
            updated_content = add_rate_limits_to_file(filepath, limits)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            print(f"  Successfully updated {filename}")
        except Exception as e:
            print(f"  Error updating {filename}: {e}")
    else:
        print(f"  File not found: {filename}")

print("\nRate limiting updates complete!")
