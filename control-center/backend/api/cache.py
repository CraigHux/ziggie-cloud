"""
Cache Management API
Centralized cache control for the Control Center backend
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path for utils import
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.cache import SimpleCache

router = APIRouter(prefix="/api/cache", tags=["cache"])


@router.post("/invalidate")
async def invalidate_all_caches():
    """
    Invalidate all caches across the Control Center backend

    This endpoint clears all cached data for:
    - Agents (L1, L2, L3)
    - Knowledge Base files
    - Creator database
    - Usage statistics

    Use this after:
    - Adding new agent files
    - Updating agent definitions
    - Running KB scans
    - Modifying creator database
    """
    try:
        invalidated = []

        # Import and invalidate agents cache
        try:
            from api.agents import load_l1_agents, load_l2_agents, load_l3_agents, agents_cache
            load_l1_agents.invalidate()
            load_l2_agents.invalidate()
            load_l3_agents.invalidate()
            agents_cache.clear()
            invalidated.append("agents")
        except Exception as e:
            invalidated.append(f"agents (error: {str(e)})")

        # Import and invalidate knowledge cache
        try:
            from api.knowledge import load_creator_database, scan_kb_files, kb_cache
            load_creator_database.invalidate()
            scan_kb_files.invalidate()
            kb_cache.clear()
            invalidated.append("knowledge")
        except Exception as e:
            invalidated.append(f"knowledge (error: {str(e)})")

        return {
            "status": "success",
            "message": "All caches invalidated",
            "invalidated": invalidated,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error invalidating caches: {str(e)}")


@router.post("/invalidate/agents")
async def invalidate_agents_cache():
    """Invalidate only agents cache"""
    try:
        from api.agents import load_l1_agents, load_l2_agents, load_l3_agents, agents_cache

        load_l1_agents.invalidate()
        load_l2_agents.invalidate()
        load_l3_agents.invalidate()
        agents_cache.clear()

        return {
            "status": "success",
            "message": "Agents cache invalidated",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error invalidating agents cache: {str(e)}")


@router.post("/invalidate/knowledge")
async def invalidate_knowledge_cache():
    """Invalidate only knowledge base cache"""
    try:
        from api.knowledge import load_creator_database, scan_kb_files, kb_cache

        load_creator_database.invalidate()
        scan_kb_files.invalidate()
        kb_cache.clear()

        return {
            "status": "success",
            "message": "Knowledge base cache invalidated",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error invalidating knowledge cache: {str(e)}")


@router.get("/stats")
async def get_all_cache_stats():
    """
    Get statistics for all caches

    Returns cache hit rates, sizes, and TTL information
    """
    try:
        stats = {
            "timestamp": datetime.now().isoformat(),
            "caches": {}
        }

        # Agents cache stats
        try:
            from api.agents import load_l1_agents, load_l2_agents, load_l3_agents, agents_cache
            stats["caches"]["agents"] = {
                "l1_agents": load_l1_agents.cache.get_stats(),
                "l2_agents": load_l2_agents.cache.get_stats(),
                "l3_agents": load_l3_agents.cache.get_stats(),
                "global": agents_cache.get_stats()
            }
        except Exception as e:
            stats["caches"]["agents"] = {"error": str(e)}

        # Knowledge cache stats
        try:
            from api.knowledge import load_creator_database, scan_kb_files, kb_cache
            stats["caches"]["knowledge"] = {
                "creator_database": load_creator_database.cache.get_stats(),
                "kb_files": scan_kb_files.cache.get_stats(),
                "global": kb_cache.get_stats()
            }
        except Exception as e:
            stats["caches"]["knowledge"] = {"error": str(e)}

        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting cache stats: {str(e)}")


@router.get("/health")
async def check_cache_health():
    """
    Check cache system health

    Returns information about cache effectiveness and recommendations
    """
    try:
        health = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "recommendations": []
        }

        # Get all cache stats
        try:
            from api.agents import load_l1_agents, load_l2_agents, load_l3_agents
            from api.knowledge import load_creator_database, scan_kb_files

            caches = [
                ("L1 Agents", load_l1_agents.cache),
                ("L2 Agents", load_l2_agents.cache),
                ("L3 Agents", load_l3_agents.cache),
                ("Creator DB", load_creator_database.cache),
                ("KB Files", scan_kb_files.cache)
            ]

            cache_info = []
            total_expired = 0
            total_active = 0

            for name, cache in caches:
                stats = cache.get_stats()
                cache_info.append({
                    "name": name,
                    **stats
                })
                total_expired += stats["expired_entries"]
                total_active += stats["active_entries"]

            health["cache_info"] = cache_info
            health["total_expired"] = total_expired
            health["total_active"] = total_active

            # Recommendations
            if total_expired > total_active:
                health["recommendations"].append(
                    "High number of expired entries detected. Consider invalidating caches manually."
                )

            if total_active == 0:
                health["recommendations"].append(
                    "No active cache entries. Caches will populate on first request."
                )

            if total_active > 10:
                health["status"] = "optimal"
                health["recommendations"].append(
                    "Caches are being utilized effectively. Performance should be improved."
                )

        except Exception as e:
            health["status"] = "error"
            health["error"] = str(e)

        return health
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking cache health: {str(e)}")
