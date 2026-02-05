"""Tests for StatuslineFormatter - ANSI colored text output."""

from claudeutils.statusline import StatuslineFormatter
from claudeutils.statusline.models import PlanUsageData


def test_colored_text() -> None:
    """StatuslineFormatter.colored() wraps text in ANSI color codes."""
    formatter = StatuslineFormatter()

    # Test red color
    red_text = formatter.colored("error", "red")
    assert "\033[31m" in red_text  # Red ANSI code
    assert "error" in red_text
    assert "\033[0m" in red_text  # Reset code

    # Test green color
    green_text = formatter.colored("success", "green")
    assert "\033[32m" in green_text  # Green ANSI code
    assert "success" in green_text
    assert "\033[0m" in green_text

    # Test yellow color
    yellow_text = formatter.colored("warning", "yellow")
    assert "\033[33m" in yellow_text  # Yellow ANSI code
    assert "warning" in yellow_text
    assert "\033[0m" in yellow_text


def test_token_bar() -> None:
    """Generate progress bar with Unicode blocks.

    StatuslineFormatter.token_bar() generates progress bar for token usage.
    """
    formatter = StatuslineFormatter()

    # Test with 50% usage (5 out of 10)
    bar = formatter.token_bar(5, 10)
    assert isinstance(bar, str)
    # Should contain Unicode block characters
    assert any(char in bar for char in "▁▂▃▄▅▆▇█")

    # Test with 0% usage
    bar_empty = formatter.token_bar(0, 10)
    assert isinstance(bar_empty, str)

    # Test with 100% usage
    bar_full = formatter.token_bar(10, 10)
    assert isinstance(bar_full, str)
    # Should contain full block character
    assert "█" in bar_full


def test_vertical_bar() -> None:
    """StatuslineFormatter.vertical_bar() generates vertical bar character.

    Vertical bar shows usage percentage with color based on severity.
    """
    formatter = StatuslineFormatter()

    # Test low usage (0%)
    bar_low = formatter.vertical_bar(0)
    assert isinstance(bar_low, str)
    assert "▁" in bar_low

    # Test medium usage (50%)
    bar_mid = formatter.vertical_bar(50)
    assert isinstance(bar_mid, str)
    assert any(char in bar_mid for char in "▁▂▃▄▅▆▇█")

    # Test high usage (100%)
    bar_high = formatter.vertical_bar(100)
    assert isinstance(bar_high, str)
    assert "█" in bar_high


def test_format_tokens() -> None:
    """StatuslineFormatter.format_tokens() converts token counts to humanized.

    Converts to human-readable strings (e.g., "1k", "1.5M", "100").
    """
    formatter = StatuslineFormatter()

    # Test small numbers (< 1k)
    assert formatter.format_tokens(100) == "100"
    assert formatter.format_tokens(999) == "999"

    # Test thousands (k)
    assert formatter.format_tokens(1000) == "1k"
    assert formatter.format_tokens(1234) == "1k"
    assert formatter.format_tokens(10000) == "10k"
    assert formatter.format_tokens(150000) == "150k"
    assert formatter.format_tokens(999999) == "999k"

    # Test millions (M)
    assert formatter.format_tokens(1000000) == "1M"
    assert formatter.format_tokens(1500000) == "1.5M"
    assert formatter.format_tokens(2500000) == "2.5M"
    assert formatter.format_tokens(10000000) == "10M"


def test_format_plan_limits() -> None:
    """StatuslineFormatter.format_plan_limits() formats plan usage with limits.

    Formats 5h and 7d limits on one line with percentages, bars, and reset time.
    """
    formatter = StatuslineFormatter()

    # Test basic formatting with specific percentages
    data = PlanUsageData(hour5_pct=87, hour5_reset="14:23", day7_pct=42)
    result = formatter.format_plan_limits(data)
    assert isinstance(result, str)

    # Must contain percentages
    assert "87" in result
    assert "42" in result

    # Must contain reset time
    assert "14:23" in result

    # Must contain vertical bars (at least 2)
    assert (
        result.count("▁")
        + result.count("▂")
        + result.count("▃")
        + result.count("▄")
        + result.count("▅")
        + result.count("▆")
        + result.count("▇")
        + result.count("█")
        >= 2
    )


def test_extract_model_tier() -> None:
    """Extract model tier from display name.

    StatuslineFormatter._extract_model_tier() extracts tier ("opus", "sonnet",
    "haiku") from model display names, case-insensitive. Returns None for
    unknown models.
    """
    formatter = StatuslineFormatter()

    # Test exact matches
    assert formatter._extract_model_tier("Claude Opus 4") == "opus"
    assert formatter._extract_model_tier("Claude Sonnet 4") == "sonnet"
    assert formatter._extract_model_tier("Claude Haiku 4") == "haiku"

    # Test case-insensitive matching
    assert formatter._extract_model_tier("claude opus 3.5") == "opus"

    # Test unknown model
    assert formatter._extract_model_tier("Unknown Model") is None


def test_format_model() -> None:
    """Format model with emoji and color coding.

    StatuslineFormatter.format_model() returns model display with medal emoji,
    color coding, and abbreviated name based on model tier.
    """
    formatter = StatuslineFormatter()

    # Test Sonnet: yellow color and silver medal emoji
    sonnet_result = formatter.format_model("Claude Sonnet 4")
    assert "🥈" in sonnet_result  # Silver medal emoji
    assert "Sonnet" in sonnet_result  # Abbreviated name
    assert "\033[33m" in sonnet_result  # Yellow ANSI code

    # Test Opus: magenta color and gold medal emoji
    opus_result = formatter.format_model("Claude Opus 4")
    assert "🥇" in opus_result  # Gold medal emoji
    assert "Opus" in opus_result  # Abbreviated name
    assert "\033[35m" in opus_result  # Magenta ANSI code

    # Test Haiku: green color and bronze medal emoji
    haiku_result = formatter.format_model("Claude Haiku 4")
    assert "🥉" in haiku_result  # Bronze medal emoji
    assert "Haiku" in haiku_result  # Abbreviated name
    assert "\033[32m" in haiku_result  # Green ANSI code

    # Test unknown model: no emoji, just full display name
    unknown_result = formatter.format_model("Unknown Model")
    assert "🥇" not in unknown_result
    assert "🥈" not in unknown_result
    assert "🥉" not in unknown_result
    assert "Unknown Model" in unknown_result
