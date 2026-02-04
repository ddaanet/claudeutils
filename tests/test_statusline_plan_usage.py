"""Test statusline plan_usage module."""

from claudeutils.account.usage import UsageCache


def test_usage_cache_ttl() -> None:
    """Verify UsageCache TTL is set to 10 seconds (R4 requirement)."""
    assert UsageCache.TTL_SECONDS == 10
