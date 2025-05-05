import time
import pytest
from prometheus_swarm.utils.cache import TTLCache

def test_cache_basic_functionality():
    """Test basic caching functionality."""
    cache = TTLCache(max_size=10, default_ttl=5)
    
    # Set and retrieve a value
    cache.set('key1', 'value1')
    assert cache.get('key1') == 'value1'

def test_cache_expiration():
    """Test that values expire after TTL."""
    cache = TTLCache(max_size=10, default_ttl=1)
    
    cache.set('key1', 'value1')
    assert cache.get('key1') == 'value1'
    
    # Wait for expiration
    time.sleep(1.1)
    assert cache.get('key1') is None

def test_cache_decorator():
    """Test the caching decorator."""
    cache = TTLCache(max_size=10, default_ttl=5)
    
    @cache.cached()
    def expensive_function(x):
        return x * 2
    
    # First call should compute and cache
    result1 = expensive_function(5)
    assert result1 == 10
    
    # Second call should retrieve from cache
    result2 = expensive_function(5)
    assert result2 == 10

def test_cache_max_size():
    """Test that cache respects max size."""
    cache = TTLCache(max_size=3, default_ttl=5)
    
    # Add more items than max size
    for i in range(5):
        cache.set(f'key{i}', f'value{i}')
    
    # Ensure only the last 3 items are retained
    for i in range(2):
        assert cache.get(f'key{i}') is None
    for i in range(2, 5):
        assert cache.get(f'key{i}') is not None