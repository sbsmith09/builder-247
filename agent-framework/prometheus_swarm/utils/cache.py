from functools import wraps
import time
from typing import Any, Callable, Dict, Optional

class TTLCache:
    """
    A thread-safe time-based cache with configurable TTL (Time To Live).
    
    This cache stores function results and automatically expires entries
    after a specified time period.
    """
    def __init__(self, max_size: int = 128, default_ttl: int = 300):
        """
        Initialize the TTL Cache.
        
        Args:
            max_size (int): Maximum number of entries in the cache. Defaults to 128.
            default_ttl (int): Default time-to-live for cache entries in seconds. Defaults to 5 minutes.
        """
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._max_size = max_size
        self._default_ttl = default_ttl

    def _cleanup(self):
        """Remove expired entries from the cache."""
        current_time = time.time()
        expired_keys = [
            key for key, entry in self._cache.items() 
            if current_time > entry['expires']
        ]
        for key in expired_keys:
            del self._cache[key]

    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve a cached value.
        
        Args:
            key (str): The cache key to retrieve.
        
        Returns:
            The cached value if it exists and hasn't expired, otherwise None.
        """
        current_time = time.time()
        entry = self._cache.get(key)
        
        if entry is None:
            return None
        
        if current_time > entry['expires']:
            del self._cache[key]
            return None
        
        return entry['value']

    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """
        Set a value in the cache.
        
        Args:
            key (str): The cache key.
            value (Any): The value to cache.
            ttl (Optional[int]): Time-to-live in seconds. Uses default if not specified.
        """
        if len(self._cache) >= self._max_size:
            self._cleanup()
        
        expires = time.time() + (ttl or self._default_ttl)
        self._cache[key] = {
            'value': value,
            'expires': expires
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