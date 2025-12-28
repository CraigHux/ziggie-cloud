"""
Tests for pagination utilities and performance monitoring
"""

import pytest
from utils.pagination import (
    PaginationParams,
    paginate_list,
    create_pagination_response,
    paginate
)
from utils.performance import (
    monitor,
    QueryTimer,
    track_performance,
    get_performance_stats,
    reset_performance_stats
)


class TestPaginationParams:
    """Test PaginationParams model"""

    def test_default_values(self):
        """Test default pagination parameters"""
        params = PaginationParams()
        assert params.page == 1
        assert params.page_size == 50
        assert params.offset is None

    def test_skip_calculation_from_page(self):
        """Test skip calculation from page number"""
        params = PaginationParams(page=3, page_size=25)
        assert params.skip == 50  # (3-1) * 25

    def test_skip_calculation_from_offset(self):
        """Test skip calculation from offset"""
        params = PaginationParams(offset=100, page_size=25)
        assert params.skip == 100

    def test_limit_property(self):
        """Test limit property"""
        params = PaginationParams(page_size=75)
        assert params.limit == 75

    def test_page_size_validation(self):
        """Test page size validation"""
        with pytest.raises(Exception):  # ValidationError
            PaginationParams(page_size=0)  # Too small

        with pytest.raises(Exception):  # ValidationError
            PaginationParams(page_size=250)  # Too large


class TestPaginateList:
    """Test list pagination function"""

    def test_paginate_first_page(self):
        """Test pagination of first page"""
        items = list(range(100))
        params = PaginationParams(page=1, page_size=10)
        result = paginate_list(items, params)

        assert len(result['items']) == 10
        assert result['items'] == list(range(10))
        assert result['meta']['total'] == 100
        assert result['meta']['page'] == 1
        assert result['meta']['total_pages'] == 10
        assert result['meta']['has_next'] is True
        assert result['meta']['has_prev'] is False

    def test_paginate_middle_page(self):
        """Test pagination of middle page"""
        items = list(range(100))
        params = PaginationParams(page=5, page_size=10)
        result = paginate_list(items, params)

        assert len(result['items']) == 10
        assert result['items'] == list(range(40, 50))
        assert result['meta']['page'] == 5
        assert result['meta']['has_next'] is True
        assert result['meta']['has_prev'] is True
        assert result['meta']['next_page'] == 6
        assert result['meta']['prev_page'] == 4

    def test_paginate_last_page(self):
        """Test pagination of last page"""
        items = list(range(95))
        params = PaginationParams(page=10, page_size=10)
        result = paginate_list(items, params)

        assert len(result['items']) == 5  # Partial page
        assert result['items'] == list(range(90, 95))
        assert result['meta']['has_next'] is False
        assert result['meta']['has_prev'] is True
        assert result['meta']['next_page'] is None

    def test_paginate_with_offset(self):
        """Test pagination using offset instead of page"""
        items = list(range(100))
        params = PaginationParams(offset=25, page_size=10)
        result = paginate_list(items, params)

        assert len(result['items']) == 10
        assert result['items'] == list(range(25, 35))
        assert result['meta']['page'] == 3  # Calculated from offset

    def test_paginate_empty_list(self):
        """Test pagination of empty list"""
        items = []
        params = PaginationParams(page=1, page_size=10)
        result = paginate_list(items, params)

        assert len(result['items']) == 0
        assert result['meta']['total'] == 0
        assert result['meta']['total_pages'] == 0
        assert result['meta']['has_next'] is False
        assert result['meta']['has_prev'] is False

    def test_paginate_cached_flag(self):
        """Test cached flag in response"""
        items = list(range(10))
        params = PaginationParams(page=1, page_size=10)
        result = paginate_list(items, params, cached=True)

        assert result['cached'] is True


class TestCreatePaginationResponse:
    """Test pagination response creation"""

    def test_create_response(self):
        """Test creating pagination response from pre-sliced data"""
        items = list(range(10, 20))  # Second page of data
        result = create_pagination_response(
            items=items,
            total=100,
            page=2,
            page_size=10
        )

        assert len(result['items']) == 10
        assert result['meta']['total'] == 100
        assert result['meta']['page'] == 2
        assert result['meta']['total_pages'] == 10
        assert result['meta']['has_next'] is True
        assert result['meta']['has_prev'] is True


class TestBackwardCompatibility:
    """Test backward compatible pagination function"""

    def test_paginate_full_list(self):
        """Test pagination with full list"""
        items = list(range(100))
        result = paginate(items, page=3, page_size=20)

        assert len(result['items']) == 20
        assert result['items'] == list(range(40, 60))
        assert result['meta']['page'] == 3

    def test_paginate_pre_sliced(self):
        """Test pagination with pre-sliced list and total"""
        items = list(range(40, 60))  # Pre-sliced page 3
        result = paginate(items, page=3, page_size=20, total=100)

        assert len(result['items']) == 20
        assert result['meta']['total'] == 100
        assert result['meta']['page'] == 3


class TestPerformanceMonitoring:
    """Test performance monitoring utilities"""

    def setup_method(self):
        """Reset metrics before each test"""
        reset_performance_stats()

    def test_query_timer_context_manager(self):
        """Test QueryTimer context manager"""
        import time

        with QueryTimer("test_query") as timer:
            time.sleep(0.01)  # Simulate 10ms query

        assert timer.duration_ms >= 10
        assert timer.duration_ms < 50  # Should complete quickly

    def test_performance_tracking(self):
        """Test performance metric recording"""
        reset_performance_stats()

        monitor.record_query(
            endpoint="GET /api/test",
            duration_ms=150,
            query_type="test",
            cached=False
        )

        metrics = get_performance_stats()
        assert metrics['total_queries'] == 1
        assert metrics['slow_queries'] == 1  # 150ms > 100ms threshold
        assert metrics['total_query_time'] == 150

    def test_endpoint_metrics(self):
        """Test per-endpoint metrics"""
        reset_performance_stats()

        monitor.record_query("GET /api/agents", 50, "file_scan", False)
        monitor.record_query("GET /api/agents", 150, "file_scan", False)
        monitor.record_query("GET /api/knowledge", 75, "file_scan", False)

        metrics = get_performance_stats()
        endpoints = metrics['queries_by_endpoint']

        assert 'GET /api/agents' in endpoints
        assert endpoints['GET /api/agents']['count'] == 2
        assert endpoints['GET /api/agents']['avg_time'] == 100
        assert endpoints['GET /api/agents']['slow_count'] == 1

    def test_slow_query_threshold(self):
        """Test slow query threshold detection"""
        reset_performance_stats()

        # Query under threshold
        monitor.record_query("GET /api/fast", 50, "test", False)

        # Query over threshold
        monitor.record_query("GET /api/slow", 150, "test", False)

        metrics = get_performance_stats()
        assert metrics['total_queries'] == 2
        assert metrics['slow_queries'] == 1

    def test_track_performance_decorator(self):
        """Test track_performance decorator"""
        reset_performance_stats()

        @track_performance(endpoint="test_endpoint", query_type="test")
        def test_function():
            import time
            time.sleep(0.01)
            return {"cached": False}

        test_function()

        metrics = get_performance_stats()
        assert metrics['total_queries'] == 1
        assert 'test_endpoint' in metrics['queries_by_endpoint']


class TestPaginationIntegration:
    """Integration tests for pagination with realistic data"""

    def test_large_dataset_pagination(self):
        """Test pagination with large dataset"""
        # Simulate 1884 agents (12 L1 + 144 L2 + 1728 L3)
        items = [{"id": i, "name": f"Agent {i}"} for i in range(1884)]

        # First page
        params = PaginationParams(page=1, page_size=50)
        result = paginate_list(items, params)

        assert len(result['items']) == 50
        assert result['meta']['total'] == 1884
        assert result['meta']['total_pages'] == 38  # ceil(1884/50)

        # Last page (partial)
        params = PaginationParams(page=38, page_size=50)
        result = paginate_list(items, params)

        assert len(result['items']) == 34  # 1884 - (37 * 50)
        assert result['meta']['has_next'] is False

    def test_filtered_pagination(self):
        """Test pagination after filtering"""
        items = [
            {"id": i, "level": "L1" if i < 12 else "L2"}
            for i in range(156)  # 12 L1 + 144 L2
        ]

        # Filter to only L2
        filtered = [item for item in items if item["level"] == "L2"]

        params = PaginationParams(page=1, page_size=50)
        result = paginate_list(filtered, params)

        assert len(result['items']) == 50
        assert result['meta']['total'] == 144
        assert result['meta']['total_pages'] == 3


class TestEdgeCases:
    """Test edge cases and error conditions"""

    def test_page_beyond_range(self):
        """Test requesting page beyond available data"""
        items = list(range(50))
        params = PaginationParams(page=10, page_size=10)
        result = paginate_list(items, params)

        assert len(result['items']) == 0
        assert result['meta']['total'] == 50
        assert result['meta']['has_next'] is False

    def test_very_large_page_size(self):
        """Test with page size at maximum"""
        items = list(range(500))
        params = PaginationParams(page=1, page_size=200)
        result = paginate_list(items, params)

        assert len(result['items']) == 200
        assert result['meta']['total_pages'] == 3

    def test_single_item(self):
        """Test pagination with single item"""
        items = [{"id": 1}]
        params = PaginationParams(page=1, page_size=50)
        result = paginate_list(items, params)

        assert len(result['items']) == 1
        assert result['meta']['total_pages'] == 1
        assert result['meta']['has_next'] is False
        assert result['meta']['has_prev'] is False
