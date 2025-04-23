"""
Cache manager for handling in-memory caching.

This module provides functionality for caching analysis results and other
frequently accessed data to improve performance.
"""

from typing import Any, Optional
import time

class CacheManager:
    """Manages caching operations for the application."""

    def __init__(self):
        """Initialize the cache manager."""
        self._cache = {}
        self._expiry_times = {}

    def set(self, key: str, value: Any, ttl: int = 3600) -> None:
        """
        Store a value in the cache.

        Args:
            key (str): Cache key
            value (Any): Value to store
            ttl (int): Time to live in seconds (default: 1 hour)
        """
        self._cache[key] = value
        self._expiry_times[key] = time.time() + ttl

    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve a value from the cache.

        Args:
            key (str): Cache key

        Returns:
            Optional[Any]: Cached value if found and not expired, None otherwise
        """
        if key not in self._cache:
            return None

        if time.time() > self._expiry_times[key]:
            del self._cache[key]
            del self._expiry_times[key]
            return None

        return self._cache[key]

    def exists(self, key: str) -> bool:
        """
        Check if a key exists in the cache and is not expired.

        Args:
            key (str): Cache key

        Returns:
            bool: True if key exists and is not expired, False otherwise
        """
        if key not in self._cache:
            return False

        if time.time() > self._expiry_times[key]:
            del self._cache[key]
            del self._expiry_times[key]
            return False

        return True

    def delete(self, key: str) -> None:
        """
        Delete a key from the cache.

        Args:
            key (str): Cache key to delete
        """
        if key in self._cache:
            del self._cache[key]
        if key in self._expiry_times:
            del self._expiry_times[key]

    def clear(self) -> None:
        """Clear all items from the cache."""
        self._cache.clear()
        self._expiry_times.clear() 