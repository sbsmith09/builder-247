import requests
import logging
from typing import Dict, Optional
from ..utils.cache import TTLCache  # Corrected import

logger = logging.getLogger(__name__)

class JokeService:
    """
    A service for retrieving jokes with built-in caching mechanism.
    
    Ensures efficient joke retrieval with reduced API calls and performance tracking.
    """
    def __init__(self, 
                 joke_api_url: str = "https://icanhazdadjoke.com/",
                 cache_size: int = 100, 
                 cache_ttl: int = 3600):  # 1-hour cache by default
        """
        Initialize the JokeService.
        
        Args:
            joke_api_url (str): URL for joke API
            cache_size (int): Maximum number of jokes to cache
            cache_ttl (int): Time-to-live for cached jokes in seconds
        """
        self.joke_api_url = joke_api_url
        self.cache = TTLCache(max_size=cache_size, default_ttl=cache_ttl)
        
        # API request headers
        self.headers = {
            'Accept': 'application/json',
            'User-Agent': 'PrometheusSwarm/1.0'
        }
    
    def get_joke(self, joke_id: Optional[str] = None) -> Dict[str, str]:
        """
        Retrieve a joke, using cache when possible.
        
        Args:
            joke_id (Optional[str]): Specific joke ID to retrieve
        
        Returns:
            Dict containing joke details
        """
        # Determine cache key
        cache_key = joke_id or 'random_joke'
        
        # Check cache first
        cached_joke = self.cache.get(cache_key)
        if cached_joke:
            logger.info(f"Retrieved joke {cache_key} from cache")
            return cached_joke
        
        try:
            # Fetch from API
            params = {'id': joke_id} if joke_id else {}
            response = requests.get(
                self.joke_api_url, 
                headers=self.headers, 
                params=params
            )
            response.raise_for_status()
            
            joke_data = response.json()
            
            # Cache the joke
            self.cache.set(cache_key, joke_data)
            
            logger.info(f"Retrieved and cached joke {cache_key}")
            return joke_data
        
        except requests.RequestException as e:
            logger.error(f"Error fetching joke: {e}")
            raise
    
    def get_cache_performance(self) -> Dict[str, float]:
        """
        Retrieve cache performance statistics.
        
        Returns:
            Dict with cache performance metrics
        """
        return self.cache.get_stats()