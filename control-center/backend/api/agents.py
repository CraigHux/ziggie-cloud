"""
Agent System Integration API
Manages the AI agents hierarchy (L1 + L2 + L3)

PERFORMANCE OPTIMIZED VERSION WITH CACHING
"""

from fastapi import APIRouter, HTTPException, Query, Request
from typing import List, Dict, Optional
from datetime import datetime
import json
import os
from pathlib import Path
import glob
import re
import sys

# Add parent directory to path for utils import
from middleware.rate_limit import limiter
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.cache import SimpleCache, cached
from utils.errors import UserFriendlyError, handle_file_error
from utils.pagination import paginate_list, PaginationParams
from utils.performance import track_performance, QueryTimer

router = APIRouter(prefix="/api/agents", tags=["agents"])

# Paths
AI_AGENTS_ROOT = Path("C:/Ziggie/ai-agents")
KB_ROOT = Path("C:/Ziggie/ai-agents/knowledge-base")

# Global cache instance for manual invalidation (5 minute TTL)
agents_cache = SimpleCache(ttl=300)


def parse_agent_markdown(file_path: str) -> Dict:
    """Parse agent definition from markdown file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        lines = content.split('\n')

        # Extract title (first # header)
        title = ""
        for line in lines:
            if line.startswith('# '):
                title = line.strip('# ').strip()
                break

        # Extract role
        role = ""
        for i, line in enumerate(lines):
            if line.startswith('## ROLE') or line.startswith('## Role'):
                if i + 1 < len(lines):
                    role = lines[i + 1].strip()
                break

        # Extract primary objective
        objective = ""
        for i, line in enumerate(lines):
            if line.startswith('## PRIMARY OBJECTIVE') or line.startswith('## Primary Objective'):
                if i + 1 < len(lines):
                    objective = lines[i + 1].strip()
                break

        # Extract responsibilities (count ## headers in CORE RESPONSIBILITIES section)
        responsibilities = []
        in_responsibilities = False
        for line in lines:
            if 'CORE RESPONSIBILITIES' in line or 'RESPONSIBILITIES' in line:
                in_responsibilities = True
                continue
            if in_responsibilities and line.startswith('## '):
                if 'RESPONSIBILITIES' not in line:
                    break
            if in_responsibilities and line.startswith('### '):
                resp = line.strip('# ').strip()
                responsibilities.append(resp)

        # Extract access permissions
        permissions = {
            "read_write": [],
            "read_only": []
        }

        in_permissions = False
        current_perm_type = None

        for line in lines:
            if 'ACCESS PERMISSIONS' in line:
                in_permissions = True
                continue
            if in_permissions:
                if line.startswith('## '):
                    break
                if 'Read/Write' in line or 'Read-Write' in line:
                    current_perm_type = "read_write"
                elif 'Read-Only' in line or 'Read Only' in line:
                    current_perm_type = "read_only"
                elif line.strip().startswith('-') and current_perm_type:
                    path = line.strip('- ').strip()
                    if path:
                        permissions[current_perm_type].append(path)

        # Extract tools
        tools = []
        in_tools = False
        for line in lines:
            if 'TOOLS' in line and 'REFERENCES' in line:
                in_tools = True
                continue
            if in_tools:
                if line.startswith('## '):
                    break
                if line.startswith('### '):
                    tool = line.strip('# ').strip()
                    tools.append(tool)

        return {
            "title": title,
            "role": role,
            "objective": objective,
            "responsibilities": responsibilities,
            "permissions": permissions,
            "tools": tools,
            "has_content": len(content) > 0,
            "word_count": len(content.split()),
            "sections": len([l for l in lines if l.startswith('## ')])
        }
    except Exception as e:
        return {"error": str(e)}


@cached(ttl=300)  # Cache for 5 minutes
def load_l1_agents() -> List[Dict]:
    """Load all L1 main agents (CACHED)"""
    agents = []

    # L1 agent files (12 agents for 12x12x12 structure)
    l1_files = [
        "01_ART_DIRECTOR_AGENT.md",
        "02_CHARACTER_PIPELINE_AGENT.md",
        "03_ENVIRONMENT_PIPELINE_AGENT.md",
        "04_GAME_SYSTEMS_DEVELOPER_AGENT.md",
        "05_UI_UX_DEVELOPER_AGENT.md",
        "06_CONTENT_DESIGNER_AGENT.md",
        "07_INTEGRATION_AGENT.md",
        "08_QA_TESTING_AGENT.md",
        "09_MIGRATION_AGENT.md",
        "10_DIRECTOR_AGENT.md",
        "11_STORYBOARD_CREATOR_AGENT.md",
        "12_COPYWRITER_SCRIPTER_AGENT.md"
    ]

    for filename in l1_files:
        file_path = AI_AGENTS_ROOT / filename

        if file_path.exists():
            try:
                agent_data = parse_agent_markdown(str(file_path))

                # Extract ID from filename
                agent_id = filename.replace('_AGENT.md', '').lower()

                stat = os.stat(file_path)

                agents.append({
                    "id": agent_id,
                    "level": "L1",
                    "name": agent_data.get('title', filename.replace('_AGENT.md', '').replace('_', ' ').title()),
                    "filename": filename,
                    "path": str(file_path),
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    **agent_data
                })
            except Exception as e:
                agents.append({
                    "id": filename.replace('.md', '').lower(),
                    "level": "L1",
                    "filename": filename,
                    "error": str(e)
                })

    return agents


@cached(ttl=300)  # Cache for 5 minutes
def load_l2_agents() -> List[Dict]:
    """Load all 144 L2 sub-agents from SUB_AGENT_ARCHITECTURE.md (CACHED)"""
    agents = []

    sub_agent_file = AI_AGENTS_ROOT / "SUB_AGENT_ARCHITECTURE.md"

    if not sub_agent_file.exists():
        return agents

    try:
        with open(sub_agent_file, 'r', encoding='utf-8') as f:
            content = f.read()

        lines = content.split('\n')

        # Parse sub-agents (format: ### Sub-Agent X.Y: **Name**)
        pattern = re.compile(r'###\s+Sub-Agent\s+(\d+)\.(\d+):\s+\*\*(.+?)\*\*')

        current_l1 = None

        for i, line in enumerate(lines):
            # Track which L1 agent we're under
            if line.startswith('# ') and 'AGENT' in line.upper():
                # Extract L1 number
                match = re.search(r'(\d+)\.', line)
                if match:
                    current_l1 = match.group(1)

            # Find sub-agent definitions
            match = pattern.search(line)
            if match:
                l1_num = match.group(1)
                l2_num = match.group(2)
                name = match.group(3)

                agent_id = f"L2.{l1_num}.{l2_num}"

                # Extract role (next line usually)
                role = ""
                if i + 1 < len(lines) and lines[i + 1].startswith('**Role:**'):
                    role = lines[i + 1].replace('**Role:**', '').strip()

                # Extract capabilities (look ahead for **Capabilities:** section)
                capabilities = []
                for j in range(i + 1, min(i + 20, len(lines))):
                    if '**Capabilities:**' in lines[j]:
                        # Read bullet points
                        for k in range(j + 1, min(j + 10, len(lines))):
                            if lines[k].startswith('- '):
                                capabilities.append(lines[k].strip('- ').strip())
                            elif lines[k].startswith('#'):
                                break
                        break

                agents.append({
                    "id": agent_id,
                    "level": "L2",
                    "name": name,
                    "role": role,
                    "parent_l1": l1_num,
                    "capabilities": capabilities,
                    "source": "SUB_AGENT_ARCHITECTURE.md"
                })

    except Exception as e:
        pass

    return agents


@cached(ttl=300)  # Cache for 5 minutes
def load_l3_agents() -> List[Dict]:
    """Load all L3 micro-agents from L3_MICRO_AGENT_ARCHITECTURE.md (CACHED)"""
    agents = []

    l3_file = AI_AGENTS_ROOT / "L3_MICRO_AGENT_ARCHITECTURE.md"

    if not l3_file.exists():
        return agents

    try:
        with open(l3_file, 'r', encoding='utf-8') as f:
            content = f.read()

        lines = content.split('\n')

        # Parse L3 agents (format: #### L3.X.Y.Z: Name - note 4 hashes)
        pattern = re.compile(r'####\s+L3\.(\d+)\.(\d+)\.(\d+):\s+(.+)')

        for i, line in enumerate(lines):
            match = pattern.search(line)
            if match:
                l1_num = match.group(1)
                l2_num = match.group(2)
                l3_num = match.group(3)
                name = match.group(4)

                agent_id = f"L3.{l1_num}.{l2_num}.{l3_num}"

                # Extract task (next line usually)
                task = ""
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if next_line and not next_line.startswith('#'):
                        task = next_line

                agents.append({
                    "id": agent_id,
                    "level": "L3",
                    "name": name,
                    "task": task,
                    "parent_l1": l1_num,
                    "parent_l2": f"L2.{l1_num}.{l2_num}",
                    "source": "L3_MICRO_AGENT_ARCHITECTURE.md"
                })

    except Exception as e:
        pass

    return agents


@router.get("")
@limiter.limit("60/minute")
@track_performance(endpoint="GET /api/agents", query_type="file_scan")
async def list_all_agents(request: Request,
    level: Optional[str] = None,
    parent: Optional[str] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=200, description="Items per page (max 200)"),
    offset: Optional[int] = Query(None, ge=0, description="Alternative to page: start offset")
):
    """
    List all agents with filtering and pagination

    - **level**: Filter by agent level (L1, L2, L3, or 'all')
    - **parent**: Filter by parent agent ID (for L2/L3)
    - **search**: Search in name, role, title, or ID
    - **page**: Page number (1-indexed)
    - **page_size**: Items per page (default 50, max 200)
    - **offset**: Alternative to page - start offset
    """
    try:
        with QueryTimer("load_agents"):
            # Load all agents (CACHED)
            l1_agents = load_l1_agents()
            l2_agents = load_l2_agents()
            l3_agents = load_l3_agents()

            all_agents = l1_agents + l2_agents + l3_agents

        # Filter by level (case-insensitive)
        if level and level.lower() != 'all':
            all_agents = [a for a in all_agents if a.get('level') == level.upper()]

        # Filter by parent (for L2/L3)
        if parent:
            all_agents = [
                a for a in all_agents
                if a.get('parent_l1') == parent or a.get('parent_l2') == parent
            ]

        # Search by name, role, or title
        if search:
            search_lower = search.lower()
            all_agents = [
                a for a in all_agents
                if search_lower in str(a.get('name', '')).lower()
                or search_lower in str(a.get('title', '')).lower()
                or search_lower in str(a.get('role', '')).lower()
                or search_lower in str(a.get('id', '')).lower()
            ]

        # Use new pagination utility
        params = PaginationParams(page=page, page_size=page_size, offset=offset)
        result = paginate_list(all_agents, params, cached=True)

        # Rename 'items' to 'agents' for backward compatibility
        result['agents'] = result.pop('items')
        # Add 'total' at root level for test compatibility (mirrors projects.py pattern)
        result['total'] = result['meta']['total']

        return result
    except Exception as e:
        UserFriendlyError.handle_error(e, context="listing agents", status_code=500)


@router.get("/stats")
async def get_agent_stats(request: Request, ):
    """Get agent system statistics (CACHED)"""
    try:
        l1_agents = load_l1_agents()
        l2_agents = load_l2_agents()
        l3_agents = load_l3_agents()

        # Count by L1 parent
        l1_distribution = {}
        for agent in l1_agents:
            agent_id = agent.get('id', 'unknown')
            l1_distribution[agent_id] = {
                "name": agent.get('title', agent_id),
                "l2_count": 0,
                "l3_count": 0
            }

        # Count L2 under each L1
        for agent in l2_agents:
            parent = agent.get('parent_l1')
            if parent:
                key = f"{parent.zfill(2)}_" + l1_agents[int(parent) - 1].get('id', 'unknown') if int(parent) <= len(l1_agents) else 'unknown'
                if key in l1_distribution:
                    l1_distribution[key]["l2_count"] += 1

        # Count L3 under each L1
        for agent in l3_agents:
            parent = agent.get('parent_l1')
            if parent:
                key = f"{parent.zfill(2)}_" + l1_agents[int(parent) - 1].get('id', 'unknown') if int(parent) <= len(l1_agents) else 'unknown'
                if key in l1_distribution:
                    l1_distribution[key]["l3_count"] += 1

        # Return format matching frontend expectations
        return {
            "total": len(l1_agents) + len(l2_agents) + len(l3_agents),
            "by_level": {
                "L1": len(l1_agents),
                "L2": len(l2_agents),
                "L3": len(l3_agents)
            },
            "l1_count": len(l1_agents),
            "l2_count": len(l2_agents),
            "l3_count": len(l3_agents),
            "expected": {
                "l1": 12,
                "l2": 144,
                "l3": 1728,
                "total": 1884
            },
            "actual": {
                "l1": len(l1_agents),
                "l2": len(l2_agents),
                "l3": len(l3_agents),
                "total": len(l1_agents) + len(l2_agents) + len(l3_agents)
            },
            "distribution": l1_distribution,
            "last_updated": datetime.now().isoformat(),
            "cached": True  # Indicate data is cached
        }
    except Exception as e:
        UserFriendlyError.handle_error(e, context="retrieving agent statistics", status_code=500)


@router.get("/{agent_id}")
async def get_agent_details(request: Request, agent_id: str):
    """Get detailed information about a specific agent"""
    try:
        # Load all agents (CACHED)
        l1_agents = load_l1_agents()
        l2_agents = load_l2_agents()
        l3_agents = load_l3_agents()

        all_agents = l1_agents + l2_agents + l3_agents

        # Find the agent
        agent = next((a for a in all_agents if a.get('id') == agent_id), None)

        if not agent:
            UserFriendlyError.not_found("Agent", agent_id)

        # If L1, find its sub-agents
        if agent.get('level') == 'L1':
            # Extract L1 number from id
            l1_num = agent_id.split('_')[0]
            sub_agents = [
                a for a in l2_agents
                if a.get('parent_l1') == l1_num
            ]
            agent['sub_agents'] = sub_agents

        # If L2, find its L3 agents
        if agent.get('level') == 'L2':
            l3_children = [
                a for a in l3_agents
                if a.get('parent_l2') == agent_id
            ]
            agent['micro_agents'] = l3_children

        return agent
    except HTTPException:
        raise
    except Exception as e:
        UserFriendlyError.handle_error(e, context="retrieving agent details", status_code=500)


@router.get("/{agent_id}/knowledge")
@limiter.limit("30/minute")
async def get_agent_knowledge(request: Request, agent_id: str):
    """Get knowledge base files for a specific agent"""
    try:
        # Map agent ID to KB directory
        agent_mapping = {
            "01_art_director": "art-director",
            "02_character_pipeline": "character-pipeline",
            "03_environment_pipeline": "environment-pipeline",
            "04_game_systems_developer": "game-systems",
            "05_ui_ux_developer": "ui-ux",
            "06_content_designer": "content-designer",
            "07_integration": "integration",
            "08_qa_testing": "qa-testing"
        }

        # Get directory name
        dir_name = agent_mapping.get(agent_id)

        if not dir_name:
            # Try to extract from L2/L3 agent
            return {"message": "Knowledge mapping not available for sub-agents", "files": []}

        # Scan for files
        kb_files = []

        # Search in ai-agents subdirectories
        agent_dir = AI_AGENTS_ROOT / "ai-agents" / dir_name
        if agent_dir.exists():
            for file_path in agent_dir.rglob("*.md"):
                try:
                    stat = os.stat(file_path)
                    kb_files.append({
                        "path": str(file_path),
                        "name": file_path.name,
                        "category": file_path.parent.name,
                        "size": stat.st_size,
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                    })
                except Exception:
                    continue

        # Also check knowledge-base L1 directories
        kb_dir_pattern = KB_ROOT / f"L1-{dir_name}"
        if kb_dir_pattern.exists():
            for file_path in kb_dir_pattern.rglob("*.md"):
                try:
                    stat = os.stat(file_path)
                    kb_files.append({
                        "path": str(file_path),
                        "name": file_path.name,
                        "category": file_path.parent.name,
                        "size": stat.st_size,
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                    })
                except Exception:
                    continue

        return {
            "agent_id": agent_id,
            "total_files": len(kb_files),
            "files": kb_files
        }
    except Exception as e:
        UserFriendlyError.handle_error(e, context=f"retrieving knowledge for agent '{agent_id}'", status_code=500)


@router.get("/{agent_id}/hierarchy")
async def get_agent_hierarchy(request: Request, agent_id: str):
    """Get the full hierarchy for an agent (parent and children)"""
    try:
        l1_agents = load_l1_agents()
        l2_agents = load_l2_agents()
        l3_agents = load_l3_agents()

        all_agents = l1_agents + l2_agents + l3_agents

        # Find the agent
        agent = next((a for a in all_agents if a.get('id') == agent_id), None)

        if not agent:
            UserFriendlyError.not_found("Agent", agent_id)

        hierarchy = {
            "agent": agent,
            "parent": None,
            "children": []
        }

        level = agent.get('level')

        # Get parent and children based on level
        if level == 'L2':
            # Find L1 parent
            parent_l1_num = agent.get('parent_l1')
            if parent_l1_num:
                hierarchy['parent'] = next(
                    (a for a in l1_agents if parent_l1_num in a.get('id', '')),
                    None
                )

            # Find L3 children
            hierarchy['children'] = [
                a for a in l3_agents
                if a.get('parent_l2') == agent_id
            ]

        elif level == 'L3':
            # Find L2 parent
            parent_l2_id = agent.get('parent_l2')
            if parent_l2_id:
                hierarchy['parent'] = next(
                    (a for a in l2_agents if a.get('id') == parent_l2_id),
                    None
                )

        elif level == 'L1':
            # Find L2 children
            l1_num = agent_id.split('_')[0]
            hierarchy['children'] = [
                a for a in l2_agents
                if a.get('parent_l1') == l1_num
            ]

        return hierarchy
    except HTTPException:
        raise
    except Exception as e:
        UserFriendlyError.handle_error(e, context=f"retrieving hierarchy for agent '{agent_id}'", status_code=500)


# Cache management endpoints
@router.post("/cache/invalidate")
@limiter.limit("10/minute")
async def invalidate_agents_cache(request: Request, ):
    """Invalidate all agents cache"""
    try:
        # Invalidate function caches
        load_l1_agents.invalidate()
        load_l2_agents.invalidate()
        load_l3_agents.invalidate()

        # Also clear global cache
        agents_cache.clear()

        return {
            "status": "success",
            "message": "All agents caches cleared",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        UserFriendlyError.handle_error(e, context="clearing agent cache", status_code=500)


@router.get("/cache/stats")
async def get_cache_stats(request: Request, ):
    """Get cache statistics"""
    try:
        return {
            "l1_agents": load_l1_agents.cache.get_stats(),
            "l2_agents": load_l2_agents.cache.get_stats(),
            "l3_agents": load_l3_agents.cache.get_stats(),
            "global_cache": agents_cache.get_stats(),
            "ttl_seconds": 300
        }
    except Exception as e:
        UserFriendlyError.handle_error(e, context="retrieving cache statistics", status_code=500)
