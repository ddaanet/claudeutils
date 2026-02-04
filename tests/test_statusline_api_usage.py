"""Tests for API usage parsing from stats-cache.json."""

import json
from unittest.mock import patch

from claudeutils.statusline.api_usage import get_api_usage
from claudeutils.statusline.models import ApiUsageData


def test_get_api_usage() -> None:
    """get_api_usage() reads stats-cache.json and aggregates tokens by tier.

    Mocks Path.open to return stats-cache.json with dailyModelTokens, verifies
    get_api_usage() returns ApiUsageData with today_opus, today_sonnet,
    today_haiku counts correctly aggregated from model tokens.
    """
    # Sample stats-cache.json structure with dailyModelTokens
    stats_cache_data = {
        "dailyModelTokens": {
            "2026-02-04": {
                "claude-3-5-sonnet-20241022": 1500,
                "claude-3-opus-20250219": 2000,
                "claude-3-5-haiku-20241022": 500,
            },
            "2026-01-31": {
                "claude-3-5-sonnet-20241022": 1000,
                "claude-3-opus-20250219": 1500,
                "claude-3-5-haiku-20241022": 300,
            },
            "2026-01-30": {
                "claude-3-5-sonnet-20241022": 800,
                "claude-3-opus-20250219": 1200,
                "claude-3-5-haiku-20241022": 200,
            },
        }
    }

    # Mock Path.open to return the stats-cache data
    mock_open_data = json.dumps(stats_cache_data)
    with patch("pathlib.Path.open", create=True) as mock_file:
        # Configure mock to return file-like object with JSON data
        mock_file.return_value.__enter__.return_value.read.return_value = mock_open_data

        # Call get_api_usage
        result = get_api_usage()

        # Verify result is ApiUsageData with correct aggregations
        assert isinstance(result, ApiUsageData)
        assert result.today_opus == 2000
        assert result.today_sonnet == 1500
        assert result.today_haiku == 500


def test_get_api_usage_week_aggregation() -> None:
    """get_api_usage() sums last 7 days of token counts for week_* fields.

    Mocks stats-cache.json with 7 days of data, asserts get_api_usage() returns
    week_opus, week_sonnet, week_haiku as sum of all 7 days.
    """
    # Sample stats-cache.json with 7 days of data (each day has 100 tokens per tier)
    stats_cache_data = {
        "dailyModelTokens": {
            "2026-02-04": {
                "claude-3-5-sonnet-20241022": 100,
                "claude-3-opus-20250219": 100,
                "claude-3-5-haiku-20241022": 100,
            },
            "2026-02-03": {
                "claude-3-5-sonnet-20241022": 100,
                "claude-3-opus-20250219": 100,
                "claude-3-5-haiku-20241022": 100,
            },
            "2026-02-02": {
                "claude-3-5-sonnet-20241022": 100,
                "claude-3-opus-20250219": 100,
                "claude-3-5-haiku-20241022": 100,
            },
            "2026-02-01": {
                "claude-3-5-sonnet-20241022": 100,
                "claude-3-opus-20250219": 100,
                "claude-3-5-haiku-20241022": 100,
            },
            "2026-01-31": {
                "claude-3-5-sonnet-20241022": 100,
                "claude-3-opus-20250219": 100,
                "claude-3-5-haiku-20241022": 100,
            },
            "2026-01-30": {
                "claude-3-5-sonnet-20241022": 100,
                "claude-3-opus-20250219": 100,
                "claude-3-5-haiku-20241022": 100,
            },
            "2026-01-29": {
                "claude-3-5-sonnet-20241022": 100,
                "claude-3-opus-20250219": 100,
                "claude-3-5-haiku-20241022": 100,
            },
        }
    }

    # Mock Path.open to return the stats-cache data
    mock_open_data = json.dumps(stats_cache_data)
    with patch("pathlib.Path.open", create=True) as mock_file:
        # Configure mock to return file-like object with JSON data
        mock_file.return_value.__enter__.return_value.read.return_value = mock_open_data

        # Call get_api_usage
        result = get_api_usage()

        # Verify result is ApiUsageData with week counts as sum of all 7 days
        assert isinstance(result, ApiUsageData)
        assert result.week_opus == 700  # 7 days * 100
        assert result.week_sonnet == 700  # 7 days * 100
        assert result.week_haiku == 700  # 7 days * 100
