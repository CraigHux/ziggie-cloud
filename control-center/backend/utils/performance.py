"""
Performance monitoring utilities for Control Center backend

Provides tools for:
- Query execution time tracking
- Slow query logging
- Query count monitoring
- Performance metrics collection
"""

import time
import logging
from typing import Any, Callable, Dict, Optional
from functools import wraps
from datetime import datetime
from pathlib import Path
import json

# Configure logging
logger = logging.getLogger("performance")
logger.setLevel(logging.INFO)

# Create logs directory
LOGS_DIR = Path(__file__).parent.parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# File handler for slow queries
slow_query_handler = logging.FileHandler(LOGS_DIR / "slow_queries.log")
slow_query_handler.setLevel(logging.WARNING)
slow_query_formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
slow_query_handler.setFormatter(slow_query_formatter)
logger.addHandler(slow_query_handler)

# Console handler for development
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(slow_query_formatter)
logger.addHandler(console_handler)


class PerformanceMonitor:
    """
    Global performance monitoring and metrics collection
    """

    def __init__(self):
        self._metrics = {
            "total_queries": 0,
            "slow_queries": 0,
            "total_query_time": 0.0,
            "queries_by_endpoint": {},
            "slow_queries_log": []
        }
        self._slow_query_threshold_ms = 100  # Log queries slower than 100ms

    def record_query(
        self,
        endpoint: str,
        duration_ms: float,
        query_type: str = "unknown",
        cached: bool = False
    ):
        """Record a query execution"""
        self._metrics["total_queries"] += 1
        self._metrics["total_query_time"] += duration_ms

        # Track by endpoint
        if endpoint not in self._metrics["queries_by_endpoint"]:
            self._metrics["queries_by_endpoint"][endpoint] = {
                "count": 0,
                "total_time": 0.0,
                "avg_time": 0.0,
                "slow_count": 0
            }

        ep_metrics = self._metrics["queries_by_endpoint"][endpoint]
        ep_metrics["count"] += 1
        ep_metrics["total_time"] += duration_ms
        ep_metrics["avg_time"] = ep_metrics["total_time"] / ep_metrics["count"]

        # Log slow queries
        if duration_ms > self._slow_query_threshold_ms:
            self._metrics["slow_queries"] += 1
            ep_metrics["slow_count"] += 1

            slow_query_info = {
                "timestamp": datetime.now().isoformat(),
                "endpoint": endpoint,
                "duration_ms": round(duration_ms, 2),
                "query_type": query_type,
                "cached": cached
            }

            self._metrics["slow_queries_log"].append(slow_query_info)

            # Keep only last 100 slow queries
            if len(self._metrics["slow_queries_log"]) > 100:
                self._metrics["slow_queries_log"] = self._metrics["slow_queries_log"][-100:]

            logger.warning(
                f"Slow query detected: {endpoint} took {duration_ms:.2f}ms "
                f"(type: {query_type}, cached: {cached})"
            )

    def get_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics"""
        metrics = self._metrics.copy()

        # Calculate averages
        if metrics["total_queries"] > 0:
            metrics["avg_query_time"] = round(
                metrics["total_query_time"] / metrics["total_queries"], 2
            )
        else:
            metrics["avg_query_time"] = 0.0

        return metrics

    def reset_metrics(self):
        """Reset all metrics"""
        self._metrics = {
            "total_queries": 0,
            "slow_queries": 0,
            "total_query_time": 0.0,
            "queries_by_endpoint": {},
            "slow_queries_log": []
        }

    def set_slow_query_threshold(self, threshold_ms: int):
        """Set the slow query threshold in milliseconds"""
        self._slow_query_threshold_ms = threshold_ms
        logger.info(f"Slow query threshold set to {threshold_ms}ms")

    def get_slow_queries(self, limit: int = 50) -> list:
        """Get recent slow queries"""
        return self._metrics["slow_queries_log"][-limit:]

    def export_metrics(self, filepath: Optional[Path] = None) -> str:
        """Export metrics to JSON file"""
        if filepath is None:
            filepath = LOGS_DIR / f"performance_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        metrics = self.get_metrics()
        metrics["exported_at"] = datetime.now().isoformat()

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(metrics, f, indent=2)

        return str(filepath)


# Global monitor instance
monitor = PerformanceMonitor()


def track_performance(
    endpoint: Optional[str] = None,
    query_type: str = "query"
):
    """
    Decorator to track query/function performance

    Usage:
        @track_performance(endpoint="GET /api/agents", query_type="file_scan")
        def load_agents():
            # ... expensive operation
            return agents

        @track_performance(endpoint="GET /api/agents")
        async def list_agents():
            # ... async operation
            return result
    """
    def decorator(func: Callable):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()

            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                duration_ms = (time.time() - start_time) * 1000
                endpoint_name = endpoint or func.__name__

                # Check if result indicates cached data
                cached = False
                if isinstance(result, dict) and result.get("cached"):
                    cached = True

                monitor.record_query(
                    endpoint=endpoint_name,
                    duration_ms=duration_ms,
                    query_type=query_type,
                    cached=cached
                )

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()

            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration_ms = (time.time() - start_time) * 1000
                endpoint_name = endpoint or func.__name__

                # Check if result indicates cached data
                cached = False
                if isinstance(result, dict) and result.get("cached"):
                    cached = True

                monitor.record_query(
                    endpoint=endpoint_name,
                    duration_ms=duration_ms,
                    query_type=query_type,
                    cached=cached
                )

        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


class QueryTimer:
    """
    Context manager for timing query execution

    Usage:
        with QueryTimer("load_agents") as timer:
            agents = load_agents()

        print(f"Query took {timer.duration_ms}ms")
    """

    def __init__(self, name: str, query_type: str = "query"):
        self.name = name
        self.query_type = query_type
        self.start_time = None
        self.end_time = None
        self.duration_ms = 0.0

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        self.duration_ms = (self.end_time - self.start_time) * 1000

        monitor.record_query(
            endpoint=self.name,
            duration_ms=self.duration_ms,
            query_type=self.query_type
        )


def add_performance_headers(response_dict: Dict[str, Any], duration_ms: float) -> Dict[str, Any]:
    """
    Add performance metadata to API response

    Args:
        response_dict: Response dictionary
        duration_ms: Query duration in milliseconds

    Returns:
        Response dictionary with performance metadata
    """
    if "meta" in response_dict:
        # Add to existing meta
        response_dict["meta"]["query_time_ms"] = round(duration_ms, 2)
    else:
        # Add performance info at top level
        response_dict["performance"] = {
            "query_time_ms": round(duration_ms, 2)
        }

    return response_dict


def get_performance_stats() -> Dict[str, Any]:
    """
    Get current performance statistics

    Returns:
        Dictionary with performance metrics
    """
    return monitor.get_metrics()


def reset_performance_stats():
    """Reset performance statistics"""
    monitor.reset_metrics()


def get_slow_queries(limit: int = 50) -> list:
    """
    Get recent slow queries

    Args:
        limit: Maximum number of queries to return

    Returns:
        List of slow query information
    """
    return monitor.get_slow_queries(limit)


def set_slow_query_threshold(threshold_ms: int):
    """
    Set the slow query threshold

    Args:
        threshold_ms: Threshold in milliseconds
    """
    monitor.set_slow_query_threshold(threshold_ms)


def export_metrics(filepath: Optional[Path] = None) -> str:
    """
    Export performance metrics to file

    Args:
        filepath: Optional custom filepath

    Returns:
        Path to exported file
    """
    return monitor.export_metrics(filepath)
