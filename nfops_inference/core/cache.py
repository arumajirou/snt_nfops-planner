"""cache.py - キャッシュ"""
from typing import Optional, Dict, Any
import hashlib
import json
from loguru import logger


class SimpleCache:
    """Simple in-memory cache"""
    
    def __init__(self, max_size: int = 1000, ttl: int = 3600):
        """
        Args:
            max_size: Maximum cache size
            ttl: Time to live in seconds (not enforced in this simple version)
        """
        self.max_size = max_size
        self.ttl = ttl
        self.cache: Dict[str, Any] = {}
        self.hit_count = 0
        self.miss_count = 0
    
    def get_cache_key(
        self,
        model_name: str,
        version: int,
        scenario_id: str,
        unique_id: str,
        ds: str,
        exog: Optional[Dict] = None
    ) -> str:
        """Generate cache key"""
        key_parts = [
            model_name,
            str(version),
            scenario_id,
            unique_id,
            ds
        ]
        
        if exog:
            # Sort to ensure consistent hashing
            exog_str = json.dumps(exog, sort_keys=True)
            key_parts.append(exog_str)
        
        key_str = "|".join(key_parts)
        cache_key = hashlib.sha256(key_str.encode()).hexdigest()[:16]
        
        return cache_key
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if key in self.cache:
            self.hit_count += 1
            logger.debug(f"Cache hit: {key}")
            return self.cache[key]
        else:
            self.miss_count += 1
            logger.debug(f"Cache miss: {key}")
            return None
    
    def set(self, key: str, value: Any):
        """Set value in cache"""
        if len(self.cache) >= self.max_size:
            # Simple eviction: remove first item
            first_key = next(iter(self.cache))
            del self.cache[first_key]
            logger.debug(f"Cache evicted: {first_key}")
        
        self.cache[key] = value
        logger.debug(f"Cache set: {key}")
    
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total = self.hit_count + self.miss_count
        hit_rate = self.hit_count / total if total > 0 else 0.0
        
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "hits": self.hit_count,
            "misses": self.miss_count,
            "hit_rate": hit_rate
        }
