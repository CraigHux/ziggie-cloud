"""
Test caching implementation

This script tests the caching layer to verify:
1. Cache functionality works correctly
2. TTL (Time To Live) is respected
3. Cache invalidation works
4. Performance improvements are measurable
"""

import sys
import time
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent))

from utils.cache import SimpleCache, cached


def test_simple_cache():
    """Test SimpleCache class basic functionality"""
    print("\n=== Testing SimpleCache ===")

    cache = SimpleCache(ttl=2)  # 2 second TTL for testing

    # Test set/get
    cache.set("test_key", "test_value")
    result = cache.get("test_key")
    assert result == "test_value", "Cache get failed"
    print("OK: Set/Get works")

    # Test expiration
    print("Waiting 3 seconds for cache to expire...")
    time.sleep(3)
    result = cache.get("test_key")
    assert result is None, "Cache didn't expire"
    print("OK: TTL expiration works")

    # Test invalidation
    cache.set("test_key2", "value2")
    cache.invalidate("test_key2")
    result = cache.get("test_key2")
    assert result is None, "Cache invalidation failed"
    print("OK: Manual invalidation works")

    # Test clear
    cache.set("key1", "val1")
    cache.set("key2", "val2")
    cache.clear()
    assert cache.get("key1") is None and cache.get("key2") is None
    print("OK: Clear all works")

    # Test stats
    cache.set("key1", "val1")
    cache.set("key2", "val2")
    stats = cache.get_stats()
    assert stats["total_entries"] == 2
    print(f"OK: Cache stats: {stats}")

    print("ALL SimpleCache tests passed!\n")


def test_cached_decorator():
    """Test @cached decorator"""
    print("\n=== Testing @cached Decorator ===")

    call_count = 0

    @cached(ttl=2)
    def expensive_function(x, y):
        nonlocal call_count
        call_count += 1
        time.sleep(0.1)  # Simulate expensive operation
        return x + y

    # First call - should execute
    start = time.time()
    result1 = expensive_function(5, 3)
    time1 = time.time() - start
    assert result1 == 8
    assert call_count == 1
    print(f"OK: First call executed (took {time1:.3f}s)")

    # Second call with same args - should be cached
    start = time.time()
    result2 = expensive_function(5, 3)
    time2 = time.time() - start
    assert result2 == 8
    assert call_count == 1  # Function wasn't called again
    print(f"OK: Second call was cached (took {time2:.3f}s, {time1/time2:.1f}x faster)")

    # Different args - should execute
    result3 = expensive_function(10, 20)
    assert result3 == 30
    assert call_count == 2
    print("OK: Different args triggered new execution")

    # Wait for expiration and call again
    print("Waiting 3 seconds for cache to expire...")
    time.sleep(3)
    result4 = expensive_function(5, 3)
    assert result4 == 8
    assert call_count == 3  # Function was called again after expiration
    print("OK: Cache expiration triggered re-execution")

    # Test manual invalidation
    expensive_function.invalidate()
    result5 = expensive_function(5, 3)
    assert call_count == 4
    print("OK: Manual invalidation works")

    print("ALL decorator tests passed!\n")


def test_performance_improvement():
    """Measure performance improvement from caching"""
    print("\n=== Performance Test ===")

    @cached(ttl=60)
    def simulate_file_scan():
        """Simulate expensive file scanning operation"""
        time.sleep(0.5)  # Simulate 500ms file scan
        return {"files": 1884, "scanned": True}

    # First call (uncached)
    print("First call (uncached)...")
    start = time.time()
    result1 = simulate_file_scan()
    uncached_time = time.time() - start
    print(f"  Time: {uncached_time:.3f}s")

    # Second call (cached)
    print("Second call (cached)...")
    start = time.time()
    result2 = simulate_file_scan()
    cached_time = time.time() - start
    print(f"  Time: {cached_time:.3f}s")

    # Calculate improvement
    improvement = uncached_time / cached_time
    print(f"\nPerformance improvement: {improvement:.1f}x faster")
    print(f"Time saved: {(uncached_time - cached_time) * 1000:.1f}ms per request")

    # Estimate savings for 100 requests
    print(f"\nFor 100 requests:")
    print(f"  Without cache: {uncached_time * 100:.2f}s")
    print(f"  With cache: {uncached_time + (cached_time * 99):.2f}s")
    print(f"  Time saved: {(uncached_time * 100) - (uncached_time + cached_time * 99):.2f}s")

    print("\nPerformance test complete!\n")


def test_cache_stats():
    """Test cache statistics"""
    print("\n=== Cache Statistics Test ===")

    cache = SimpleCache(ttl=60)

    # Add some entries
    for i in range(5):
        cache.set(f"key{i}", f"value{i}")

    stats = cache.get_stats()
    print(f"Cache stats after 5 entries:")
    print(f"  Total entries: {stats['total_entries']}")
    print(f"  Active entries: {stats['active_entries']}")
    print(f"  Expired entries: {stats['expired_entries']}")
    print(f"  TTL: {stats['ttl_seconds']}s")

    assert stats["total_entries"] == 5
    assert stats["active_entries"] == 5
    assert stats["expired_entries"] == 0

    print("\nCache statistics test passed!\n")


def main():
    """Run all tests"""
    print("=" * 60)
    print("CACHE IMPLEMENTATION TEST SUITE")
    print("=" * 60)

    try:
        test_simple_cache()
        test_cached_decorator()
        test_performance_improvement()
        test_cache_stats()

        print("=" * 60)
        print("ALL TESTS PASSED!")
        print("=" * 60)
        print("\nCaching layer is working correctly!")
        print("\nExpected benefits for Control Center:")
        print("  - Agents endpoint: ~100-500ms faster per request")
        print("  - KB files endpoint: ~200-1000ms faster per request")
        print("  - Stats endpoint: ~50-200ms faster per request")
        print("\nCache invalidation available at:")
        print("  - POST /api/cache/invalidate (all caches)")
        print("  - POST /api/cache/invalidate/agents")
        print("  - POST /api/cache/invalidate/knowledge")
        print("  - GET /api/cache/stats (view cache statistics)")
        print("  - GET /api/cache/health (check cache health)")

    except AssertionError as e:
        print(f"\nTEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
