# backend/agents/backend_agent/utils/cache_manager.py
"""
Template caching with LRU and file-based cache
"""
import json
import hashlib
import os
import pickle
from pathlib import Path
from typing import Dict, Any, Optional
from functools import lru_cache, wraps
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class TemplateCache:
    """Multi-layer cache for templates"""
    
    def __init__(self, cache_dir: str = None, max_size: int = 100):
        self.memory_cache = LRUCache(max_size)
        self.cache_dir = Path(cache_dir or '/tmp/ai_devfactory/cache')
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl = 3600  # 1 hour TTL
    
    def get(self, key: str) -> Optional[Dict]:
        """Get template from cache (memory first, then disk)"""
        # Check memory cache
        value = self.memory_cache.get(key)
        if value is not None:
            logger.debug(f"Cache hit (memory): {key}")
            return value
        
        # Check disk cache
        cache_file = self.cache_dir / f"{key}.pkl"
        if cache_file.exists():
            try:
                with open(cache_file, 'rb') as f:
                    cached = pickle.load(f)
                    
                # Check TTL
                if datetime.now() - cached['timestamp'] < timedelta(seconds=self.ttl):
                    logger.debug(f"Cache hit (disk): {key}")
                    # Promote to memory
                    self.memory_cache.set(key, cached['data'])
                    return cached['data']
                else:
                    # Expired, remove
                    cache_file.unlink()
            except Exception as e:
                logger.warning(f"Failed to load cache: {e}")
        
        return None
    
    def set(self, key: str, value: Dict):
        """Store template in both memory and disk cache"""
        # Memory cache
        self.memory_cache.set(key, value)
        
        # Disk cache
        cache_file = self.cache_dir / f"{key}.pkl"
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump({
                    'data': value,
                    'timestamp': datetime.now()
                }, f)
        except Exception as e:
            logger.warning(f"Failed to write cache: {e}")
    
    def invalidate(self, key: str = None):
        """Invalidate cache for specific key or all"""
        if key:
            self.memory_cache.delete(key)
            cache_file = self.cache_dir / f"{key}.pkl"
            if cache_file.exists():
                cache_file.unlink()
        else:
            self.memory_cache.clear()
            for file in self.cache_dir.glob("*.pkl"):
                file.unlink()
    
    def get_template_hash(self, template_path: str) -> str:
        """Generate hash for template file for cache invalidation"""
        if not Path(template_path).exists():
            return ""
        
        with open(template_path, 'rb') as f:
            content = f.read()
        return hashlib.sha256(content).hexdigest()


class LRUCache:
    """Least Recently Used cache implementation"""
    
    def __init__(self, capacity: int = 100):
        self.cache = {}
        self.capacity = capacity
        self.order = []  # Track access order
    
    def get(self, key: str) -> Optional[Any]:
        if key in self.cache:
            # Move to end (most recently used)
            self.order.remove(key)
            self.order.append(key)
            return self.cache[key]
        return None
    
    def set(self, key: str, value: Any):
        if key in self.cache:
            # Update existing
            self.order.remove(key)
        elif len(self.cache) >= self.capacity:
            # Remove least recently used
            oldest = self.order.pop(0)
            del self.cache[oldest]
        
        self.cache[key] = value
        self.order.append(key)
    
    def delete(self, key: str):
        if key in self.cache:
            del self.cache[key]
            self.order.remove(key)
    
    def clear(self):
        self.cache.clear()
        self.order.clear()


# Decorator for caching template loads
def cache_template(func):
    """Decorator to cache template loading results"""
    cache = TemplateCache()
    
    @wraps(func)
    def wrapper(framework: str, *args, **kwargs):
        cache_key = f"template_{framework}"
        
        # Try to get from cache
        cached = cache.get(cache_key)
        if cached is not None:
            return cached
        
        # Load from disk
        result = func(framework, *args, **kwargs)
        
        # Store in cache
        cache.set(cache_key, result)
        
        return result
    
    return wrapper


# Updated agent_logic.py with caching
class BackendAgent:
    def __init__(self):
        self.configure_gemini()
        self.cache = TemplateCache(max_size=50)
        self.templates = self._load_all_templates()
    
    @cache_template
    def load_templates(self, framework: str) -> Dict:
        """Load templates with caching"""
        # Check for template changes
        template_path = f'framework_templates/{framework}/base'
        current_hash = self.cache.get_template_hash(template_path)
        
        cache_key = f"template_{framework}"
        cached = self.cache.get(cache_key)
        
        if cached and cached.get('hash') == current_hash:
            return cached['data']
        
        # Load fresh templates
        templates = self._load_framework_templates(framework)
        
        # Store in cache
        self.cache.set(cache_key, {
            'data': templates,
            'hash': current_hash
        })
        
        return templates
