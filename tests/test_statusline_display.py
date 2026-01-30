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
