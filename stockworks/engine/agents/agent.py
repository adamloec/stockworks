import abc
from typing import Dict, Any, Optional
from datetime import timedelta, datetime
import logging

from utils import RateLimiter

class Agent(abc.ABC):
    """
    Purpose: 
        - Abstract class for all agents
        - All agents should inherit from this class

    Attributes:
    
    """
    def __init__(self, name: str, cache_duration: int = 300):
        self.name = name
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.cache_duration = timedelta(seconds=cache_duration)
        self.rate_limiter = RateLimiter()
        self.logger = logging.getLogger(f"agent.{name}")

    async def _get_from_cache(self, key: str) -> Optional[Dict[str, Any]]:
        if key in self.cache:
            cache_entry = self.cache[key]
            if datetime.now() - cache_entry["timestamp"] < self.cache_duration:
                self.logger.debug(f"Cache hit for key: {key}")
                return cache_entry["data"]
        return None
    
    def _update_cache(self, key: str, data: Dict[str, Any]):
        self.cache[key] = {"timestamp": datetime.now(), "data": data}

    def _clear_cache(self):
        self.cache.clear()

    async def fetch_with_retry(self, key: str) -> Dict[str, Any]:
        cached_data = await self._get_from_cache(key)
        if cached_data:
            return cached_data
        
        await self.rate_limiter.acquire()

        try:
            data = await self._fetch_data(key)
            self._update_cache(key, data)
            return data
        except Exception as e:
            self.logger.error(f"Error fetching data for key: {key}")
            raise

    async def process(self, key: str) -> Dict[str, Any]:
        try:
            data = await self.fetch_with_retry(key)
            processed_data = self._process_data(data)
            return {
                'status': 'success',
                'timestamp': datetime.now(),
                'data': processed_data,
            }
        except Exception as e:
            self.logger.error(f"Error processing data for key: {key}")
            return {
                'status': 'error',
                'timestamp': datetime.now(),
                'error': str(e),
            }
        
    @abc.abstractmethod
    async def _fetch_data(self, key: str) -> Dict[str, Any]:
        pass

    @abc.abstractmethod
    def _process_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @abc.abstractmethod
    async def health_check(self) -> bool:
        pass