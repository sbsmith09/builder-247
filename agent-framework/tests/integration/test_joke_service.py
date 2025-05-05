import pytest
import time
from prometheus_swarm.src.services.joke_service import JokeService
from prometheus_swarm.src.utils.cache import TTLCache

@pytest.fixture
def joke_service():
    """Create a JokeService instance for testing."""
    return JokeService(cache_size=10, cache_ttl=5)

def test_joke_retrieval(joke_service):
    """Test basic joke retrieval."""
    joke1 = joke_service.get_joke()
    assert 'joke' in joke1
    assert isinstance(joke1['joke'], str)

def test_joke_caching(joke_service):
    """Test that jokes are cached and subsequent retrieval uses cache."""
    joke_service.get_joke()  # First retrieval
    cache_performance_before = joke_service.get_cache_performance()
    
    # Second retrieval
    joke_service.get_joke()
    cache_performance_after = joke_service.get_cache_performance()
    
    assert cache_performance_after['hits'] > cache_performance_before['hits']

def test_joke_cache_expiration(joke_service):
    """Test that cache entries expire after TTL."""
    joke_service.cache = TTLCache(default_ttl=1)  # Set very short TTL
    joke1 = joke_service.get_joke()
    
    # Wait for cache to expire
    time.sleep(2)
    
    joke2 = joke_service.get_joke()
    cache_performance = joke_service.get_cache_performance()
    
    # Expect a cache miss
    assert cache_performance['misses'] > 0

def test_specific_joke_retrieval(joke_service):
    """Test retrieving a random joke, then attempting to retrieve it from cache."""
    # First, get a random joke
    initial_joke = joke_service.get_joke()
    joke_id = initial_joke.get('id')
    initial_text = initial_joke.get('joke')
    
    # Retrieve the joke again from cache
    cached_joke = joke_service.get_joke(joke_id)
    
    # Verify the cached joke matches the initial joke
    assert cached_joke.get('id') == joke_id
    assert cached_joke.get('joke') == initial_text

def test_cache_performance_tracking(joke_service):
    """Verify cache performance tracking."""
    for _ in range(5):
        joke_service.get_joke()
    
    performance = joke_service.get_cache_performance()
    
    assert 'hits' in performance
    assert 'misses' in performance
    assert 'hit_rate' in performance
    assert 0 <= performance['hit_rate'] <= 100