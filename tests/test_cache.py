"""
Tests for the CacheManager module.

This module contains tests for verifying the functionality of:
- Cache storage and retrieval
- Cache expiration
- Cache cleanup
- Error handling
"""

import pytest
import time
from datetime import datetime, timedelta
from core.cache import CacheManager

@pytest.fixture
def cache_manager():
    """Create a CacheManager instance for testing."""
    return CacheManager()

@pytest.fixture
def sample_data():
    """Create sample data for testing."""
    return {
        'table': [[1, 2], [3, 4]],
        'statistics': {'chi_square': 0.5, 'p_value': 0.05}
    }

def test_cache_set_get(cache_manager, sample_data):
    """Test basic cache set and get operations."""
    # Set data in cache
    cache_manager.set('test_key', sample_data)
    
    # Get data from cache
    cached_data = cache_manager.get('test_key')
    assert cached_data == sample_data

def test_cache_expiration(cache_manager, sample_data):
    """Test cache expiration."""
    # Set data with short expiration
    cache_manager.set('test_key', sample_data, ttl=1)
    assert cache_manager.exists('test_key')
    
    # Wait for expiration
    time.sleep(1.1)
    assert not cache_manager.exists('test_key')

def test_cache_cleanup(cache_manager, sample_data):
    """Test cache cleanup."""
    # Set multiple items
    cache_manager.set('key1', sample_data, ttl=1)
    cache_manager.set('key2', sample_data, ttl=2)
    cache_manager.set('key3', sample_data, ttl=3)
    
    # Wait for first item to expire
    time.sleep(1.1)
    assert not cache_manager.exists('key1')
    assert cache_manager.exists('key2')
    assert cache_manager.exists('key3')
    
    # Wait for second item to expire
    time.sleep(1)
    assert not cache_manager.exists('key2')
    assert cache_manager.exists('key3')
    
    # Wait for third item to expire
    time.sleep(1)
    assert not cache_manager.exists('key3')

def test_cache_clear(cache_manager, sample_data):
    """Test clearing the entire cache."""
    # Set multiple items
    cache_manager.set('key1', sample_data)
    cache_manager.set('key2', sample_data)
    
    # Clear cache
    cache_manager.clear()
    
    # All items should be gone
    assert cache_manager.get('key1') is None
    assert cache_manager.get('key2') is None

def test_cache_nonexistent_key(cache_manager):
    """Test getting nonexistent key."""
    assert cache_manager.get('nonexistent') is None

def test_cache_update(cache_manager, sample_data):
    """Test updating existing cache entry."""
    # Set initial data
    cache_manager.set('test_key', sample_data)
    
    # Update data
    new_data = {'table': [[5, 6], [7, 8]]}
    cache_manager.set('test_key', new_data)
    
    # Verify update
    assert cache_manager.get('test_key') == new_data

def test_cache_large_data(cache_manager):
    """Test caching large data."""
    large_data = {'data': [i for i in range(1000000)]}
    cache_manager.set('large_key', large_data)
    assert cache_manager.get('large_key') == large_data

def test_cache_multiple_types(cache_manager):
    """Test caching different data types."""
    # Test different data types
    test_cases = [
        ('string', 'test string'),
        ('number', 42),
        ('list', [1, 2, 3]),
        ('dict', {'key': 'value'}),
        ('none', None),
        ('bool', True)
    ]
    
    for key, value in test_cases:
        cache_manager.set(key, value)
        assert cache_manager.get(key) == value

def test_cache_concurrent_access(cache_manager, sample_data):
    """Test concurrent cache access."""
    import threading
    
    def worker():
        for i in range(100):
            cache_manager.set(f'key_{i}', sample_data)
            assert cache_manager.get(f'key_{i}') == sample_data
    
    # Create multiple threads
    threads = [threading.Thread(target=worker) for _ in range(5)]
    
    # Start threads
    for thread in threads:
        thread.start()
    
    # Wait for threads to complete
    for thread in threads:
        thread.join()
    
    # Verify all entries are present
    for i in range(100):
        assert cache_manager.get(f'key_{i}') == sample_data

def test_cache_memory_usage(cache_manager):
    """Test cache memory usage."""
    import sys
    
    # Get initial memory usage
    initial_memory = sys.getsizeof(cache_manager._cache)
    
    # Add some data
    for i in range(1000):
        cache_manager.set(f'key_{i}', {'data': [i] * 1000})
    
    # Get memory usage after adding data
    final_memory = sys.getsizeof(cache_manager._cache)
    
    # Memory usage should have increased
    assert final_memory > initial_memory
    
    # Clear cache
    cache_manager.clear()
    
    # Memory usage should be similar to initial
    assert sys.getsizeof(cache_manager._cache) <= initial_memory 