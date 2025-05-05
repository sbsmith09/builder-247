from functools import wraps
import time
import logging
from typing import Any, Callable, Dict, Optional
from collections import OrderedDict

logger = logging.getLogger(__name__)

class TTLCache:
    """
    A thread-safe time-based cache with configurable TTL (Time To Live).
    
    This cache stores function results and automatically expires entries
    after a specified time period. It uses an OrderedDict to manage max size.
    """
    def __init__(self, max_size: int = 128, default_ttl: int = 300):
        """
        Initialize the TTL Cache.
        
        Args:
            max_size (int): Maximum number of entries in the cache. Defaults to 128.
            default_ttl (int): Default time-to-live for cache entries in seconds. Defaults to 5 minutes.
        """
        self._cache: OrderedDict = OrderedDict()
        self._max_size = max_size
        self._default_ttl = default_ttl
        self._hits = 0
        self._misses = 0

    def _cleanup(self):
        """Remove expired entries from the cache, maintaining max_size."""
        current_time = time.time()
        
        # Remove expired entries
        for key in list(self._cache.keys()):
            if current_time > self._cache[key]['expires']:
                del self._cache[key]
        
        # If still over max_size, remove oldest non-expired entries
        while len(self._cache) > self._max_size:
            self._cache.popitem(last=False)

    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve a cached value.
        
        Args:
            key (str): The cache key to retrieve.
        
        Returns:
            The cached value if it exists and hasn't expired, otherwise None.
        """
        current_time = time.time()
        
        if key not in self._cache:
            self._misses += 1
            logger.info(f"Cache miss for key: {key}")
            return None
        
        entry = self._cache[key]
        
        if current_time > entry['expires']:
            del self._cache[key]
            self._misses += 1
            logger.info(f"Cache expired for key: {key}")
            return None
        
        # Move to end to show it's most recently used
        self._cache.move_to_end(key)
        self._hits += 1
        logger.info(f"Cache hit for key: {key}")
        return entry['value']

    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """
        Set a value in the cache.
        
        Args:
            key (str): The cache key.
            value (Any): The value to cache.
            ttl (Optional[int]): Time-to-live in seconds. Uses default if not specified.
        """
        # If the key already exists, remove it first
        if key in self._cache:
            del self._cache[key]
        
        # Add to the end (most recently used)
        expires = time.time() + (ttl or self._default_ttl)
        self._cache[key] = {
            'value': value,
            'expires': expires
        }
        
        # If over max size, remove oldest entries
        self._cleanup()
        logger.info(f"Cached value for key: {key}")

    def get_stats(self) -> Dict[str, int]:
        """
        Get cache hit/miss statistics.
        
        Returns:
            A dictionary with hit and miss counts.
        """
        total_requests = self._hits + self._misses
        return {
            'hits': self._hits,
            'misses': self._misses,
            'hit_rate': (self._hits / total_requests * 100) if total_requests > 0 else 0
        }

    def cached(self, ttl: Optional[int] = None):
        """
        A decorator to add caching to a function.
        
        Args:
            ttl (Optional[int]): Time-to-live for the cached results.
        
        Returns:
            A decorator function that caches results.
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Create a cache key based on function name and arguments
                key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
                
                # Try to retrieve cached result
                cached_result = self.get(key)
                if cached_result is not None:
                    return cached_result
                
                # Call the function and cache its result
                result = func(*args, **kwargs)
                self.set(key, result, ttl)
                
                return result
            return wrapper
        return decorator