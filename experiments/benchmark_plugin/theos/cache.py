"""
THEOS Plugin - WisdomCache Module
LRU cache with TTL expiration for reasoning state reuse

Author: Frederick Davis Stalnecker & Manus AI
License: MIT
Version: 1.0.0
"""

import json
import logging
from collections import OrderedDict
from typing import Optional, Dict, Any, List
from .core import CachedState


logger = logging.getLogger(__name__)


class WisdomCache:
    """
    LRU cache with TTL expiration for caching refined reasoning states.
    
    Features:
    - LRU eviction when cache is full
    - TTL-based expiration for stale entries
    - Persistence (save/load to JSON)
    - Access tracking and statistics
    """
    
    def __init__(self, max_size: int = 1000, ttl: int = 3600):
        """
        Initialize WisdomCache.
        
        Args:
            max_size: Maximum number of cached states
            ttl: Time-to-live in seconds (default: 1 hour)
        """
        self.max_size = max_size
        self.ttl = ttl
        self.cache: OrderedDict[str, CachedState] = OrderedDict()
        self.hits = 0
        self.misses = 0
        logger.debug(f"WisdomCache initialized: max_size={max_size}, ttl={ttl}s")
    
    def get(self, key: str) -> Optional[CachedState]:
        """
        Retrieve cached state by key.
        
        Args:
            key: Cache key (typically the prompt)
        
        Returns:
            CachedState if found and not expired, None otherwise
        """
        if key in self.cache:
            state = self.cache[key]
            
            # Check expiration
            if state.is_expired(self.ttl):
                logger.debug(f"Cache expired for key: {key[:50]}...")
                del self.cache[key]
                self.misses += 1
                return None
            
            # Move to end (most recently used)
            self.cache.move_to_end(key)
            
            # Increment access count
            state.access_count += 1
            
            self.hits += 1
            logger.debug(f"Cache hit for key: {key[:50]}...")
            return state
        
        self.misses += 1
        logger.debug(f"Cache miss for key: {key[:50]}...")
        return None
    
    def put(self, state: CachedState):
        """
        Store cached state.
        
        Args:
            state: CachedState to cache
        """
        # If key exists, remove it first (will be re-added at end)
        if state.key in self.cache:
            del self.cache[state.key]
        
        # Add new state
        self.cache[state.key] = state
        
        # Evict oldest if over capacity (LRU)
        if len(self.cache) > self.max_size:
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
            logger.debug(f"LRU eviction: {oldest_key[:50]}...")
        
        logger.debug(f"Cached state for key: {state.key[:50]}...")
    
    def clear(self):
        """Clear all cached states."""
        self.cache.clear()
        logger.info("Cache cleared")
    
    def prune_expired(self):
        """Remove all expired entries from cache."""
        expired_keys = [
            key for key, state in self.cache.items()
            if state.is_expired(self.ttl)
        ]
        
        for key in expired_keys:
            del self.cache[key]
        
        if expired_keys:
            logger.info(f"Pruned {len(expired_keys)} expired entries")
    
    def save(self, filepath: str):
        """
        Save cache to JSON file.
        
        Args:
            filepath: Path to save cache
        """
        data = {
            'max_size': self.max_size,
            'ttl': self.ttl,
            'hits': self.hits,
            'misses': self.misses,
            'states': [state.to_dict() for state in self.cache.values()]
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Cache saved to {filepath} ({len(self.cache)} states)")
    
    def load(self, filepath: str):
        """
        Load cache from JSON file.
        
        Args:
            filepath: Path to load cache from
        """
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        self.max_size = data.get('max_size', self.max_size)
        self.ttl = data.get('ttl', self.ttl)
        self.hits = data.get('hits', 0)
        self.misses = data.get('misses', 0)
        
        self.cache.clear()
        for state_dict in data.get('states', []):
            state = CachedState.from_dict(state_dict)
            self.cache[state.key] = state
        
        logger.info(f"Cache loaded from {filepath} ({len(self.cache)} states)")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache metrics
        """
        total_requests = self.hits + self.misses
        hit_rate = self.hits / total_requests if total_requests > 0 else 0.0
        
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': hit_rate,
            'ttl': self.ttl
        }
    
    def get_top_accessed(self, n: int = 10) -> List[CachedState]:
        """
        Get top N most accessed cached states.
        
        Args:
            n: Number of top states to return
        
        Returns:
            List of CachedState objects sorted by access count
        """
        sorted_states = sorted(
            self.cache.values(),
            key=lambda s: s.access_count,
            reverse=True
        )
        return sorted_states[:n]
    
    def __len__(self) -> int:
        """Return number of cached states."""
        return len(self.cache)
    
    def __contains__(self, key: str) -> bool:
        """Check if key exists in cache."""
        return key in self.cache
    
    def __repr__(self) -> str:
        """String representation of cache."""
        return f"WisdomCache(size={len(self.cache)}/{self.max_size}, hits={self.hits}, misses={self.misses})"
