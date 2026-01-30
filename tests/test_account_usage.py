"""Tests for Usage API caching."""

from claudeutils.account import UsageCache


def test_usage_cache_get_stale() -> None:
    """Test that UsageCache.get() returns None when cache missing or stale.

    Tests cache behavior when file doesn't exist or is stale.
    """
    cache = UsageCache()
    result = cache.get()
    assert result is None
