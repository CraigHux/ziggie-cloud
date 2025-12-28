"""
Knowledge Base Integration API
Connects Control Center to the Knowledge Base system

PERFORMANCE OPTIMIZED VERSION WITH CACHING
"""

from fastapi import APIRouter, HTTPException, Query, Request
from typing import List, Dict, Optional, Literal
from datetime import datetime
import json
import os
from pathlib import Path
import glob
import subprocess
import sys
import re

# Add parent directory to path for utils import
from middleware.rate_limit import limiter
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.cache import SimpleCache, cached
from utils.errors import UserFriendlyError, handle_file_error
from utils.pagination import paginate_list, PaginationParams
from utils.performance import track_performance, QueryTimer

router = APIRouter(prefix="/api/knowledge", tags=["knowledge"])

# Paths
KB_ROOT = Path("C:/meowping-rts/ai-agents/knowledge-base")
CREATOR_DB = KB_ROOT / "metadata" / "creator-database.json"
AI_AGENTS_ROOT = Path("C:/meowping-rts/ai-agents")
MANAGE_PY = KB_ROOT / "manage.py"

# Global cache instance (5 minute TTL)
kb_cache = SimpleCache(ttl=300)


@cached(ttl=300)  # Cache for 5 minutes
def load_creator_database() -> Dict:
    """Load the creator database JSON (CACHED)"""
    try:
        with open(CREATOR_DB, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        return {
            "metadata": {"total_creators": 0, "status": "error"},
            "creators": [],
            "error": str(e)
        }


@cached(ttl=300)  # Cache for 5 minutes
def scan_kb_files() -> List[Dict]:
    """Scan all markdown files in the knowledge base (CACHED)"""
    kb_files = []

    # Scan ai-agents subdirectories
    agent_dirs = [
        "art-director",
        "character-pipeline",
        "environment-pipeline",
        "game-systems",
        "ui-ux",
        "content-designer",
        "integration",
        "qa-testing"
    ]

    for agent_dir in agent_dirs:
        pattern = str(AI_AGENTS_ROOT / "ai-agents" / agent_dir / "**" / "*.md")
        files = glob.glob(pattern, recursive=True)

        for file_path in files:
            try:
                stat = os.stat(file_path)
                kb_files.append({
                    "path": file_path,
                    "name": os.path.basename(file_path),
                    "agent": agent_dir,
                    "size": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "category": Path(file_path).parent.name
                })
            except Exception:
                continue

    # Also scan L1 knowledge base directories
    pattern = str(KB_ROOT / "L1-*" / "**" / "*.md")
    files = glob.glob(pattern, recursive=True)

    for file_path in files:
        try:
            stat = os.stat(file_path)
            kb_files.append({
                "path": file_path,
                "name": os.path.basename(file_path),
                "agent": "knowledge-base",
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "category": Path(file_path).parts[-2] if len(Path(file_path).parts) > 1 else "root"
            })
        except Exception:
            continue

    return kb_files


def parse_markdown_insights(file_path: str) -> Dict:
    """Parse a markdown file for key insights"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract basic metadata
        lines = content.split('\n')
        title = lines[0].strip('# ').strip() if lines else "Untitled"

        # Count sections (## headers)
        sections = len([l for l in lines if l.startswith('## ')])

        # Word count
        word_count = len(content.split())

        # Look for confidence scores in the content
        confidence = None
        for line in lines:
            if 'confidence' in line.lower() and '%' in line:
                try:
                    # Try to extract percentage
                    import re
                    match = re.search(r'(\d+)%', line)
                    if match:
                        confidence = int(match.group(1))
                except:
                    pass

        return {
            "title": title,
            "sections": sections,
            "word_count": word_count,
            "confidence": confidence,
            "has_code": "```" in content,
            "has_links": "http" in content or "www." in content
        }
    except Exception as e:
        return {"error": str(e)}


@router.get("/recent")
@limiter.limit("60/minute")
async def get_recent_kb_files(
    request: Request,
    limit: int = Query(10, ge=1, le=100, description="Number of recent files to return")
):
    """Get recently modified knowledge base files (CACHED)"""
    try:
        kb_files = scan_kb_files()

        # Sort by modified date (most recent first)
        sorted_files = sorted(
            kb_files,
            key=lambda f: f.get('modified', ''),
            reverse=True
        )

        # Return only the requested number
        recent_files = sorted_files[:limit]

        # Ensure each file has required fields with proper format
        formatted_files = []
        for idx, file in enumerate(recent_files):
            formatted_files.append({
                "id": str(idx + 1),  # Use index as ID
                "name": file.get('name', 'Unknown'),
                "path": file.get('path', 'Unknown'),
                "modified": file.get('modified', datetime.now().isoformat()),
                "size": file.get('size', 0),
                "agent": file.get('agent', 'unknown'),
                "category": file.get('category', 'general')
            })

        return {
            "success": True,
            "count": len(formatted_files),
            "files": formatted_files
        }
    except Exception as e:
        UserFriendlyError.handle_error(e, context="retrieving recent knowledge base files", status_code=500)


@router.get("/stats")
async def get_kb_stats():
    """Get overall knowledge base statistics (CACHED)"""
    try:
        creator_db = load_creator_database()
        kb_files = scan_kb_files()

        # Calculate stats
        total_files = len(kb_files)
        total_size = sum(f.get('size', 0) for f in kb_files)

        # Get recent files (last 7 days)
        from datetime import timedelta
        week_ago = datetime.now() - timedelta(days=7)
        recent_files = [
            f for f in kb_files
            if datetime.fromisoformat(f['modified']) > week_ago
        ]

        # Group by agent
        files_by_agent = {}
        for f in kb_files:
            agent = f.get('agent', 'unknown')
            files_by_agent[agent] = files_by_agent.get(agent, 0) + 1

        return {
            "total_creators": creator_db.get("metadata", {}).get("total_creators", 0),
            "total_files": total_files,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "recent_files_7d": len(recent_files),
            "files_by_agent": files_by_agent,
            "last_scan": datetime.now().isoformat(),
            "kb_status": "active" if total_files > 0 else "empty",
            "cached": True  # Indicate data is cached
        }
    except Exception as e:
        UserFriendlyError.handle_error(e, context="retrieving knowledge base statistics", status_code=500)


@router.get("/files")
@track_performance(endpoint="GET /api/knowledge/files", query_type="file_scan")
async def get_kb_files(
    agent: Optional[str] = None,
    category: Optional[str] = None,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=200, description="Items per page (max 200)"),
    offset: Optional[int] = Query(None, ge=0, description="Alternative to page: start offset")
):
    """
    List all knowledge base files with pagination (CACHED)

    - **agent**: Filter by agent name
    - **category**: Filter by category
    - **page**: Page number (1-indexed)
    - **page_size**: Items per page (default 50, max 200)
    - **offset**: Alternative to page - start offset
    """
    try:
        with QueryTimer("scan_kb_files"):
            kb_files = scan_kb_files()

        # Filter by agent if specified
        if agent:
            kb_files = [f for f in kb_files if f.get('agent') == agent]

        # Filter by category if specified
        if category:
            kb_files = [f for f in kb_files if f.get('category') == category]

        # Sort by modified date (newest first)
        kb_files.sort(key=lambda x: x.get('modified', ''), reverse=True)

        # Use new pagination utility
        params = PaginationParams(page=page, page_size=page_size, offset=offset)
        result = paginate_list(kb_files, params, cached=True)

        # Rename 'items' to 'files' for backward compatibility
        result['files'] = result.pop('items')

        return result
    except Exception as e:
        UserFriendlyError.handle_error(e, context="listing knowledge base files", status_code=500)


@router.get("/files/{file_id}")
async def get_kb_file_details(file_id: str):
    """Get detailed information about a specific KB file"""
    try:
        # Decode file_id (base64 encoded path)
        import base64
        decoded_path = base64.b64decode(file_id).decode('utf-8')

        # Resolve the path to prevent path traversal attacks
        file_path = Path(decoded_path).resolve()

        # Define allowed directories
        allowed_dirs = [
            AI_AGENTS_ROOT.resolve(),
            KB_ROOT.resolve()
        ]

        # Verify file is within allowed directories
        is_allowed = False
        for allowed_dir in allowed_dirs:
            try:
                # Check if file_path is relative to allowed_dir
                file_path.relative_to(allowed_dir)
                is_allowed = True
                break
            except ValueError:
                # file_path is not relative to this allowed_dir
                continue

        if not is_allowed:
            UserFriendlyError.forbidden("File path is outside allowed directories")

        if not file_path.exists():
            UserFriendlyError.not_found("File")

        # Get file stats
        stat = os.stat(file_path)

        # Parse insights
        insights = parse_markdown_insights(str(file_path))

        return {
            "path": str(file_path),
            "name": file_path.name,
            "size": stat.st_size,
            "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "insights": insights
        }
    except HTTPException:
        raise
    except Exception as e:
        UserFriendlyError.handle_error(e, context="retrieving file details", status_code=500)


@router.get("/creators")
@limiter.limit("60/minute")
async def get_creators(request: Request, 
    priority: Optional[str] = None,
    search: Optional[str] = None
):
    """List YouTube creators from the database (CACHED)"""
    try:
        creator_db = load_creator_database()
        creators = creator_db.get("creators", [])

        # Filter by priority
        if priority:
            creators = [c for c in creators if c.get('priority') == priority]

        # Search by name or focus
        if search:
            search_lower = search.lower()
            creators = [
                c for c in creators
                if search_lower in c.get('name', '').lower()
                or search_lower in c.get('focus', '').lower()
            ]

        return {
            "total": len(creators),
            "creators": creators,
            "priority_tiers": creator_db.get("priority_tiers", {}),
            "cached": True  # Indicate data is cached
        }
    except Exception as e:
        UserFriendlyError.handle_error(e, context="listing creators", status_code=500)


@router.get("/creators/{creator_id}")
@limiter.limit("60/minute")
async def get_creator_details(request: Request, creator_id: str):
    """Get detailed information about a specific creator"""
    try:
        creator_db = load_creator_database()
        creators = creator_db.get("creators", [])

        creator = next((c for c in creators if c.get('id') == creator_id), None)

        if not creator:
            UserFriendlyError.not_found("Creator", creator_id)

        # Find related KB files (CACHED)
        kb_files = scan_kb_files()
        creator_files = [
            f for f in kb_files
            if creator_id in f.get('name', '').lower() or creator_id in f.get('path', '').lower()
        ]

        return {
            **creator,
            "related_files": len(creator_files),
            "files": creator_files[:10]  # First 10 files
        }
    except HTTPException:
        raise
    except Exception as e:
        UserFriendlyError.handle_error(e, context=f"retrieving details for creator '{creator_id}'", status_code=500)


@router.post("/scan")
async def trigger_manual_scan(
    creator_id: Optional[str] = Query(
        default=None,
        max_length=100,
        description="Specific creator ID to scan",
        pattern=r'^[a-zA-Z0-9_-]*$'
    ),
    priority: Optional[Literal["high", "medium", "low"]] = Query(
        default=None,
        description="Scan creators by priority level"
    ),
    force_rescan: bool = Query(
        default=False,
        description="Force rescan even if recently scanned"
    ),
    max_videos: int = Query(
        default=10,
        ge=1,
        le=100,
        description="Maximum videos to process per creator"
    )
):
    """
    Trigger a manual knowledge base scan.

    **Validation:**
    - Creator ID: Optional, alphanumeric with hyphens/underscores, max 100 chars
    - Priority: Optional, one of: high, medium, low
    - Max videos: 1-100 per creator

    **Returns:**
    - Scan job details including PID and command
    """
    try:
        # Validate creator_id format if provided
        if creator_id:
            creator_id = creator_id.strip()
            if not re.match(r'^[a-zA-Z0-9_-]+$', creator_id):
                raise ValueError(
                    "Creator ID must contain only alphanumeric characters, "
                    "hyphens, and underscores"
                )

        # Check if manage.py exists
        if not MANAGE_PY.exists():
            UserFriendlyError.handle_error(
                FileNotFoundError("manage.py not found"),
                context="starting knowledge base scan",
                status_code=404
            )

        # Build command
        cmd = ["python", str(MANAGE_PY), "scan"]

        if creator_id:
            cmd.extend(["--creator", creator_id])
        elif priority:
            cmd.extend(["--priority", priority])

        if force_rescan:
            cmd.append("--force")

        cmd.extend(["--max-videos", str(max_videos)])

        # Execute scan in background
        result = subprocess.Popen(
            cmd,
            cwd=str(KB_ROOT),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        return {
            "status": "started",
            "pid": result.pid,
            "command": " ".join(cmd),
            "message": "Scan job started. Check /api/knowledge/jobs for status.",
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except ValueError as e:
        UserFriendlyError.validation_error(str(e), field="creator_id")
    except Exception as e:
        UserFriendlyError.handle_error(e, context="starting knowledge base scan", status_code=500)


@router.get("/jobs")
@limiter.limit("30/minute")
async def get_scan_jobs(request: Request, ):
    """Get knowledge base scan job history"""
    try:
        # Check for logs directory
        logs_dir = KB_ROOT / "logs"

        if not logs_dir.exists():
            return {
                "total": 0,
                "jobs": [],
                "message": "No logs directory found"
            }

        # Scan log files
        log_files = list(logs_dir.glob("scan_*.log"))

        jobs = []
        for log_file in sorted(log_files, reverse=True)[:20]:  # Last 20 jobs
            try:
                stat = os.stat(log_file)

                # Try to read job status from log
                with open(log_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')

                    # Determine status
                    if "ERROR" in content or "FAILED" in content:
                        status = "failed"
                    elif "SUCCESS" in content or "COMPLETE" in content:
                        status = "completed"
                    else:
                        status = "unknown"

                    # Extract summary info
                    videos_processed = content.count("Processing video:")
                    insights_extracted = content.count("Insight extracted:")

                jobs.append({
                    "log_file": log_file.name,
                    "timestamp": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "size": stat.st_size,
                    "status": status,
                    "videos_processed": videos_processed,
                    "insights_extracted": insights_extracted
                })
            except Exception:
                continue

        return {
            "total": len(jobs),
            "jobs": jobs
        }
    except Exception as e:
        UserFriendlyError.handle_error(e, context="retrieving scan job history", status_code=500)


@router.get("/search")
@limiter.limit("30/minute")
async def search_knowledge(
    request: Request,
    query: str = Query(
        ...,
        min_length=2,
        max_length=500,
        description="Search query"
    ),
    agent: Optional[str] = Query(
        default=None,
        max_length=100,
        description="Filter by specific agent",
        pattern=r'^[a-zA-Z0-9_-]*$'
    ),
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
        description="Maximum number of results"
    )
):
    """
    Search knowledge base content.

    **Validation:**
    - Query: 2-500 characters
    - Agent filter: Optional, alphanumeric with hyphens/underscores
    - Limit: 1-100 results

    **Returns:**
    - Matching files with preview and match count
    """
    try:
        # Normalize query
        query = ' '.join(query.split())

        if len(query) < 2:
            raise ValueError("Search query must be at least 2 characters")

        # Normalize agent name
        if agent:
            agent = agent.lower().strip()
            if not re.match(r'^[a-zA-Z0-9_-]+$', agent):
                raise ValueError(
                    "Agent name must contain only alphanumeric characters, "
                    "hyphens, and underscores"
                )

        kb_files = scan_kb_files()

        if agent:
            kb_files = [f for f in kb_files if f.get('agent') == agent]

        query_lower = query.lower()
        matches = []

        for file_info in kb_files[:200]:  # Limit files to search
            try:
                with open(file_info['path'], 'r', encoding='utf-8') as f:
                    content = f.read()

                if query_lower in content.lower():
                    # Find context around match
                    lines = content.split('\n')
                    matching_lines = [
                        (i, line) for i, line in enumerate(lines)
                        if query_lower in line.lower()
                    ]

                    matches.append({
                        **file_info,
                        "match_count": len(matching_lines),
                        "preview": matching_lines[0][1][:200] if matching_lines else ""
                    })
            except Exception:
                continue

        # Sort by match count
        matches.sort(key=lambda x: x.get('match_count', 0), reverse=True)

        return {
            "query": query,
            "total_matches": len(matches),
            "results": matches[:limit]
        }
    except ValueError as e:
        UserFriendlyError.validation_error(str(e), field="query" if "query" in str(e) else "agent")
    except Exception as e:
        UserFriendlyError.handle_error(e, context=f"searching knowledge base for '{query}'", status_code=500)


# Cache management endpoints
@router.post("/cache/invalidate")
async def invalidate_kb_cache():
    """Invalidate all knowledge base caches"""
    try:
        # Invalidate function caches
        load_creator_database.invalidate()
        scan_kb_files.invalidate()

        # Also clear global cache
        kb_cache.clear()

        return {
            "status": "success",
            "message": "All knowledge base caches cleared",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        UserFriendlyError.handle_error(e, context="clearing knowledge base cache", status_code=500)


@router.get("/cache/stats")
async def get_kb_cache_stats():
    """Get knowledge base cache statistics"""
    try:
        return {
            "creator_database": load_creator_database.cache.get_stats(),
            "kb_files": scan_kb_files.cache.get_stats(),
            "global_cache": kb_cache.get_stats(),
            "ttl_seconds": 300
        }
    except Exception as e:
        UserFriendlyError.handle_error(e, context="retrieving knowledge base cache statistics", status_code=500)
