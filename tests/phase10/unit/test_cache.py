"""test_cache.py"""
import pytest
from nfops_inference.core.cache import SimpleCache


class TestCache:
    def test_cache_key_generation(self):
        """Test cache key generation"""
        cache = SimpleCache()
        
        key1 = cache.get_cache_key(
            model_name="model1",
            version=1,
            scenario_id="base",
            unique_id="A001",
            ds="2025-01-01"
        )
        
        key2 = cache.get_cache_key(
            model_name="model1",
            version=1,
            scenario_id="base",
            unique_id="A001",
            ds="2025-01-01"
        )
        
        # Same inputs should generate same key
        assert key1 == key2
    
    def test_cache_get_set(self):
        """Test cache get/set"""
        cache = SimpleCache()
        
        key = "test_key"
        value = {"data": "test"}
        
        # Miss
        result = cache.get(key)
        assert result is None
        
        # Set
        cache.set(key, value)
        
        # Hit
        result = cache.get(key)
        assert result == value
    
    def test_cache_stats(self):
        """Test cache statistics"""
        cache = SimpleCache()
        
        cache.get("key1")  # miss
        cache.set("key1", "value1")
        cache.get("key1")  # hit
        
        stats = cache.stats()
        
        assert stats['hits'] == 1
        assert stats['misses'] == 1
        assert stats['size'] == 1
