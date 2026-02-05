"""Tests for StatuslineFormatter - ANSI colored text output."""

from claudeutils.statusline import StatuslineFormatter
from claudeutils.statusline.models import GitStatus, PlanUsageData


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


def test_format_model_thinking_disabled() -> None:
    """Format model with thinking disabled indicator (😶 emoji).

    StatuslineFormatter.format_model() adds thinking indicator when
    thinking_enabled=False. When thinking disabled, output includes 😶 emoji
    after medal and before name. Format: {medal}{thinking_indicator} {name}
    """
    formatter = StatuslineFormatter()

    # Test Sonnet with thinking disabled
    sonnet_no_think = formatter.format_model("Claude Sonnet 4", thinking_enabled=False)
    assert "😶" in sonnet_no_think  # Thinking disabled indicator
    assert "🥈" in sonnet_no_think  # Silver medal emoji still present
    assert "Sonnet" in sonnet_no_think

    # Test Sonnet with thinking enabled (default)
    sonnet_think = formatter.format_model("Claude Sonnet 4", thinking_enabled=True)
    assert "😶" not in sonnet_think  # No thinking indicator
    assert "🥈" in sonnet_think  # Medal emoji present
    assert "Sonnet" in sonnet_think

    # Test Opus with thinking disabled
    opus_no_think = formatter.format_model("Claude Opus 4", thinking_enabled=False)
    assert "😶" in opus_no_think
    assert "🥇" in opus_no_think
    assert "Opus" in opus_no_think

    # Test Haiku with thinking disabled
    haiku_no_think = formatter.format_model("Claude Haiku 4", thinking_enabled=False)
    assert "😶" in haiku_no_think
    assert "🥉" in haiku_no_think
    assert "Haiku" in haiku_no_think


def test_format_directory() -> None:
    """Format directory with emoji and CYAN color.

    StatuslineFormatter.format_directory() returns directory display with 📁
    emoji prefix and CYAN color applied to the directory name. Format: {emoji}
    {colored_name}
    """
    formatter = StatuslineFormatter()

    # Test basic directory formatting
    result = formatter.format_directory("claudeutils")
    assert "📁" in result  # Directory emoji
    assert "claudeutils" in result  # Directory name
    assert "\033[36m" in result  # Cyan ANSI code
    assert "\033[0m" in result  # Reset code


def test_format_git_status() -> None:
    """Format git status with emoji and branch color.

    StatuslineFormatter.format_git_status() returns git status display with ✅
    emoji for clean state and 🟡 emoji for dirty state. Branch name is colored
    green for clean (✅) and yellow+bold for dirty (🟡). Format: {emoji}
    {colored_branch}
    """
    formatter = StatuslineFormatter()

    # Test clean state (dirty=False)
    clean_status = GitStatus(branch="main", dirty=False)
    result_clean = formatter.format_git_status(clean_status)
    assert "✅" in result_clean  # Clean status emoji
    assert "main" in result_clean  # Branch name
    assert "\033[32m" in result_clean  # Green ANSI code
    assert "\033[0m" in result_clean  # Reset code

    # Test dirty state (dirty=True)
    dirty_status = GitStatus(branch="feature", dirty=True)
    result_dirty = formatter.format_git_status(dirty_status)
    assert "🟡" in result_dirty  # Dirty status emoji
    assert "feature" in result_dirty  # Branch name
    assert "\033[33m" in result_dirty  # Yellow ANSI code
    assert "\033[1m" in result_dirty  # Bold ANSI code
    assert "\033[0m" in result_dirty  # Reset code


def test_format_mode() -> None:
    """Format mode with emoji and color.

    StatuslineFormatter.format_mode() returns mode display with 🎫 emoji for
    "plan" mode and 💳 emoji for "api" mode. Mode name is colored green for
    "plan" and yellow for "api". Format: {emoji} {colored_mode}
    """
    formatter = StatuslineFormatter()

    # Test "plan" mode
    plan_result = formatter.format_mode("plan")
    assert "🎫" in plan_result  # Plan emoji
    assert "Plan" in plan_result  # Capitalized mode name
    assert "\033[32m" in plan_result  # Green ANSI code
    assert plan_result.startswith("🎫")  # Emoji first

    # Test "api" mode
    api_result = formatter.format_mode("api")
    assert "💳" in api_result  # API emoji
    assert "API" in api_result  # Capitalized mode name
    assert "\033[33m" in api_result  # Yellow ANSI code
    assert api_result.startswith("💳")  # Emoji first


def test_format_cost() -> None:
    """Format cost with emoji and dollar amount.

    StatuslineFormatter.format_cost() returns cost display with 💰 emoji prefix
    and formatted dollar amount with 2 decimal places. Format: {emoji}
    ${amount:.2f}
    """
    formatter = StatuslineFormatter()

    # Test basic cost formatting
    result = formatter.format_cost(0.05)
    assert "💰" in result  # Cost emoji
    assert "$0.05" in result  # Formatted cost with 2 decimals
    assert result == "💰 $0.05"  # Exact format

    # Test rounding to 2 decimals
    result_rounded = formatter.format_cost(1.234)
    assert "💰" in result_rounded
    assert "$1.23" in result_rounded
    assert result_rounded == "💰 $1.23"
