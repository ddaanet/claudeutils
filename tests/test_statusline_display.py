"""Tests for StatuslineFormatter - ANSI colored text output."""

from claudeutils.statusline import StatuslineFormatter


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


def test_limit_display() -> None:
    """StatuslineFormatter.limit_display() formats limit info.

    Displays name, percentage used, and reset time with colors.
    """
    formatter = StatuslineFormatter()

    # Test basic formatting
    result = formatter.limit_display("claude-opus", 75, "2026-02-01")
    assert isinstance(result, str)
    assert "claude-opus" in result
    assert "75" in result
    assert "2026-02-01" in result
    # Should contain vertical bar separator
    assert "│" in result


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
