"""Test statusline plan_usage module."""

from unittest.mock import MagicMock, patch

from claudeutils.account.usage import UsageCache
from claudeutils.statusline.plan_usage import get_plan_usage


def test_usage_cache_ttl() -> None:
    """Verify UsageCache TTL is set to 10 seconds (R4 requirement)."""
    assert UsageCache.TTL_SECONDS == 10


def test_get_plan_usage() -> None:
    """Test get_plan_usage returns PlanUsageData with percentages."""
    # Mock UsageCache.get() to return usage data
    mock_usage_data = {
        "usage_5h_percent": 87,
        "usage_5h_reset": "14:23",
        "usage_7d_percent": 42,
    }

    with patch("claudeutils.statusline.plan_usage.UsageCache") as mock_cache_class:
        mock_instance = MagicMock()
        mock_cache_class.return_value = mock_instance
        mock_instance.get.return_value = mock_usage_data

        result = get_plan_usage()

        assert result is not None
        assert result.hour5_pct == 87
        assert result.hour5_reset == "14:23"
        assert result.day7_pct == 42
