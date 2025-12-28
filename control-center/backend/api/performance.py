"""
Performance Monitoring API
Exposes performance metrics and query statistics
"""

from fastapi import APIRouter, Query, Request
from typing import Optional
from datetime import datetime
from pathlib import Path
from middleware.rate_limit import limiter
from utils.performance import (
    get_performance_stats,
    reset_performance_stats,
    get_slow_queries,
    set_slow_query_threshold,
    export_metrics
)
from utils.errors import UserFriendlyError

router = APIRouter(prefix="/api/performance", tags=["performance"])


@router.get("/metrics")
@limiter.limit("60/minute")
async def get_metrics(request: Request):
    """
    Get current performance metrics

    Returns statistics including:
    - Total query count
    - Slow query count
    - Average query time
    - Metrics by endpoint
    - Recent slow queries
    """
    try:
        metrics = get_performance_stats()

        return {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "metrics": metrics
        }
    except Exception as e:
        UserFriendlyError.handle_error(e, context="retrieving performance metrics", status_code=500)


@router.get("/slow-queries")
@limiter.limit("60/minute")
async def get_slow_query_log(
    request: Request,
    limit: int = Query(50, ge=1, le=500, description="Number of slow queries to return")
):
    """
    Get recent slow queries

    - **limit**: Number of queries to return (default 50, max 500)
    """
    try:
        slow_queries = get_slow_queries(limit)

        return {
            "success": True,
            "count": len(slow_queries),
            "slow_queries": slow_queries
        }
    except Exception as e:
        UserFriendlyError.handle_error(e, context="retrieving slow queries", status_code=500)


@router.post("/reset")
@limiter.limit("10/minute")
async def reset_metrics(request: Request):
    """
    Reset all performance metrics

    Use with caution - this clears all collected statistics
    """
    try:
        reset_performance_stats()

        return {
            "success": True,
            "message": "Performance metrics reset successfully",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        UserFriendlyError.handle_error(e, context="resetting performance metrics", status_code=500)


@router.put("/threshold")
@limiter.limit("10/minute")
async def update_slow_query_threshold(
    request: Request,
    threshold_ms: int = Query(..., ge=1, le=10000, description="Threshold in milliseconds")
):
    """
    Update the slow query threshold

    - **threshold_ms**: Threshold in milliseconds (1-10000)

    Queries taking longer than this threshold will be logged as slow
    """
    try:
        set_slow_query_threshold(threshold_ms)

        return {
            "success": True,
            "message": f"Slow query threshold updated to {threshold_ms}ms",
            "threshold_ms": threshold_ms
        }
    except Exception as e:
        UserFriendlyError.handle_error(e, context="updating slow query threshold", status_code=500)


@router.post("/export")
@limiter.limit("10/minute")
async def export_performance_metrics(request: Request):
    """
    Export performance metrics to JSON file

    Creates a timestamped file in the logs directory
    """
    try:
        filepath = export_metrics()

        return {
            "success": True,
            "message": "Metrics exported successfully",
            "filepath": filepath,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        UserFriendlyError.handle_error(e, context="exporting performance metrics", status_code=500)


@router.get("/summary")
@limiter.limit("60/minute")
async def get_performance_summary(request: Request):
    """
    Get a summary of performance metrics

    Provides a high-level overview of system performance
    """
    try:
        metrics = get_performance_stats()

        # Calculate summary statistics
        total_queries = metrics.get("total_queries", 0)
        slow_queries = metrics.get("slow_queries", 0)
        avg_time = metrics.get("avg_query_time", 0)

        # Calculate slow query percentage
        slow_percentage = 0.0
        if total_queries > 0:
            slow_percentage = (slow_queries / total_queries) * 100

        # Find slowest endpoint
        endpoints = metrics.get("queries_by_endpoint", {})
        slowest_endpoint = None
        slowest_avg_time = 0

        for endpoint, stats in endpoints.items():
            if stats.get("avg_time", 0) > slowest_avg_time:
                slowest_avg_time = stats["avg_time"]
                slowest_endpoint = endpoint

        # Performance grade
        grade = "A"
        if avg_time > 500:
            grade = "F"
        elif avg_time > 300:
            grade = "D"
        elif avg_time > 200:
            grade = "C"
        elif avg_time > 100:
            grade = "B"

        return {
            "success": True,
            "summary": {
                "total_queries": total_queries,
                "slow_queries": slow_queries,
                "slow_query_percentage": round(slow_percentage, 2),
                "avg_query_time_ms": avg_time,
                "performance_grade": grade,
                "slowest_endpoint": {
                    "name": slowest_endpoint,
                    "avg_time_ms": round(slowest_avg_time, 2)
                } if slowest_endpoint else None
            },
            "recommendations": generate_recommendations(metrics)
        }
    except Exception as e:
        UserFriendlyError.handle_error(e, context="generating performance summary", status_code=500)


def generate_recommendations(metrics: dict) -> list:
    """Generate performance optimization recommendations"""
    recommendations = []

    avg_time = metrics.get("avg_query_time", 0)
    slow_queries = metrics.get("slow_queries", 0)
    total_queries = metrics.get("total_queries", 0)
    endpoints = metrics.get("queries_by_endpoint", {})

    # Check average query time
    if avg_time > 200:
        recommendations.append({
            "severity": "high",
            "message": f"Average query time is {avg_time:.2f}ms. Consider implementing caching for frequently accessed data.",
            "action": "Review endpoints with high average response times and add caching where appropriate."
        })
    elif avg_time > 100:
        recommendations.append({
            "severity": "medium",
            "message": f"Average query time is {avg_time:.2f}ms. Some queries could be optimized.",
            "action": "Review slow query log and optimize N+1 queries."
        })

    # Check slow query percentage
    if total_queries > 0:
        slow_percentage = (slow_queries / total_queries) * 100
        if slow_percentage > 20:
            recommendations.append({
                "severity": "high",
                "message": f"{slow_percentage:.1f}% of queries are slow. This indicates a performance issue.",
                "action": "Review slow query log and implement database indexes or query optimizations."
            })
        elif slow_percentage > 10:
            recommendations.append({
                "severity": "medium",
                "message": f"{slow_percentage:.1f}% of queries are slow.",
                "action": "Monitor slow queries and optimize where possible."
            })

    # Check for endpoints with high slow query counts
    for endpoint, stats in endpoints.items():
        slow_count = stats.get("slow_count", 0)
        total_count = stats.get("count", 0)

        if total_count > 0:
            endpoint_slow_pct = (slow_count / total_count) * 100
            if endpoint_slow_pct > 50:
                recommendations.append({
                    "severity": "high",
                    "message": f"Endpoint '{endpoint}' has {endpoint_slow_pct:.1f}% slow queries.",
                    "action": f"Optimize the '{endpoint}' endpoint - consider adding pagination, caching, or eager loading."
                })

    # Check for file scanning operations
    for endpoint, stats in endpoints.items():
        if "file_scan" in endpoint.lower() or stats.get("avg_time", 0) > 500:
            recommendations.append({
                "severity": "medium",
                "message": f"Endpoint '{endpoint}' performs file scanning operations ({stats.get('avg_time', 0):.2f}ms avg).",
                "action": "Consider implementing a file system watcher or caching layer to avoid repeated scans."
            })

    if not recommendations:
        recommendations.append({
            "severity": "info",
            "message": "Performance is good. No immediate optimizations needed.",
            "action": "Continue monitoring for any degradation."
        })

    return recommendations
