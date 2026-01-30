"""Usage API caching with 30-second TTL."""

import time
from pathlib import Path


class UsageCache:
    """Cache for Usage API responses with time-to-live (TTL) handling."""

    TTL_SECONDS = 30

    def __init__(self) -> None:
        """Initialize UsageCache."""
        self.cache_dir = Path.home() / ".claude"
        self.cache_file = self.cache_dir / "usage_cache.json"

    def get(self) -> None | dict[str, object]:
        """Get cached data if fresh, else return None.

        Returns None if cache file doesn't exist or data is stale (older than
        TTL).
        """
        if not self.cache_file.exists():
            return None

        file_mtime = self.cache_file.stat().st_mtime
        current_time = time.time()

        if current_time - file_mtime > self.TTL_SECONDS:
            return None

        return None
