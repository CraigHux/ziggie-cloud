#!/usr/bin/env python3
"""Apply rate limiting decorators to all API endpoint files."""

import os
import re
import platform

def update_file_with_rate_limits(filepath, decorators_config):
    """Update a file with rate limiting decorators."""

    if not os.path.exists(filepath):
        print(f"  SKIP: {filepath} not found")
        return False

    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    modified = False

    # Process the file
    for func_name, limit in decorators_config.items():
        for i, line in enumerate(lines):
            # Look for async def or def with the function name
            if f'def {func_name}(' in line:
                # Look backward for @router decorator
                for j in range(i - 1, max(0, i - 10), -1):
                    if '@router.' in lines[j]:
                        # Check if limiter decorator already exists
                        decorator_exists = False
                        for k in range(j + 1, min(j + 5, i)):
                            if '@limiter.limit' in lines[k]:
                                decorator_exists = True
                                break

                        if not decorator_exists:
                            # Insert the decorator after the @router line
                            lines.insert(j + 1, f'@limiter.limit("{limit}")\n')
                            modified = True

                            # Now add request parameter if missing
                            # Find the actual def line again (it shifted)
                            for m, def_line in enumerate(lines[j:j+10]):
                                if f'def {func_name}(' in def_line:
                                    if 'request: Request' not in def_line:
                                        lines[j + m] = def_line.replace(
                                            f'def {func_name}(',
                                            f'def {func_name}(request: Request, '
                                        )
                                        modified = True
                                    break
                        break

    if modified:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        return True

    return False

# Use Windows paths on Windows
if platform.system() == 'Windows' or 'win' in platform.system().lower():
    base_path = r'C:\Ziggie\control-center\backend\api'
else:
    base_path = '/c/Ziggie/control-center/backend/api'

# Configuration for all API files
FILES_CONFIG = {
    os.path.join(base_path, 'services.py'): {
        'get_services': '60/minute',
        'start_service': '10/minute',
        'stop_service': '10/minute',
        'get_service_status': '60/minute',
        'get_service_logs': '30/minute',
    },
    os.path.join(base_path, 'docker.py'): {
        'get_docker_status': '60/minute',
        'list_containers': '60/minute',
        'get_container_details': '60/minute',
        'start_container': '10/minute',
        'stop_container': '10/minute',
        'restart_container': '10/minute',
        'get_container_logs': '30/minute',
        'list_images': '60/minute',
        'list_compose_projects': '60/minute',
        'get_docker_stats': '30/minute',
    },
    os.path.join(base_path, 'system.py'): {
        'get_system_stats': '60/minute',
        'get_processes': '60/minute',
        'get_ports': '30/minute',
    },
    os.path.join(base_path, 'knowledge.py'): {
        'get_knowledge_stats': '60/minute',
        'get_knowledge_files': '60/minute',
        'get_file_details': '60/minute',
        'get_creators': '60/minute',
        'get_creator_details': '60/minute',
        'scan_knowledge_base': '10/minute',
        'get_scan_jobs': '30/minute',
        'search_knowledge': '30/minute',
    },
    os.path.join(base_path, 'projects.py'): {
        'list_projects': '60/minute',
        'get_project_status': '60/minute',
        'get_project_files': '60/minute',
        'get_project_commits': '30/minute',
        'get_project_branches': '30/minute',
        'refresh_project': '10/minute',
    },
    os.path.join(base_path, 'usage.py'): {
        'get_usage_stats': '60/minute',
        'get_usage_history': '60/minute',
        'track_usage': '30/minute',
        'get_pricing': '60/minute',
        'estimate_cost': '30/minute',
        'get_usage_summary': '60/minute',
    },
    os.path.join(base_path, 'comfyui.py'): {
        'get_comfyui_status': '60/minute',
        'get_comfyui_port': '60/minute',
        'start_comfyui': '10/minute',
        'stop_comfyui': '10/minute',
        'get_comfyui_logs': '30/minute',
        'get_comfyui_config': '60/minute',
        'get_workflows': '60/minute',
        'get_comfyui_health': '100/minute',
    },
}

print("Applying rate limiting to all API endpoints...\n")

for filepath, decorators in FILES_CONFIG.items():
    filename = os.path.basename(filepath)
    print(f"Processing {filename}...", end=' ')

    if update_file_with_rate_limits(filepath, decorators):
        print("UPDATED")
    else:
        print("checked")

print("\nDone!")
