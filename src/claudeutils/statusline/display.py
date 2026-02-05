"""ANSI colored text formatter for statusline display."""

from typing import ClassVar

from claudeutils.statusline.models import PlanUsageData


class StatuslineFormatter:
    """Formats text with ANSI color codes for terminal display."""

    # ANSI color codes
    COLORS: ClassVar[dict[str, str]] = {
        "red": "\033[31m",
        "green": "\033[32m",
        "yellow": "\033[33m",
        "blue": "\033[34m",
        "magenta": "\033[35m",
        "cyan": "\033[36m",
        "white": "\033[37m",
    }
    RESET: ClassVar[str] = "\033[0m"

    # Model tier to emoji mapping
    MODEL_EMOJI: ClassVar[dict[str, str]] = {
        "opus": "🥇",
        "sonnet": "🥈",
        "haiku": "🥉",
    }

    # Model tier to color mapping
    MODEL_COLORS: ClassVar[dict[str, str]] = {
        "opus": "magenta",
        "sonnet": "yellow",
        "haiku": "green",
    }

    # Model tier to abbreviated name mapping
    MODEL_NAMES: ClassVar[dict[str, str]] = {
        "opus": "Opus",
        "sonnet": "Sonnet",
        "haiku": "Haiku",
    }

    def _extract_model_tier(self, display_name: str) -> str | None:
        """Extract model tier from display name.

        Args:
            display_name: Model display name (e.g., "Claude Opus 4")

        Returns:
            Model tier ("opus", "sonnet", "haiku") or None if not found
        """
        lower_name = display_name.lower()
        if "opus" in lower_name:
            return "opus"
        if "sonnet" in lower_name:
            return "sonnet"
        if "haiku" in lower_name:
            return "haiku"
        return None

    def format_model(self, display_name: str, *, thinking_enabled: bool = True) -> str:
        """Format model with emoji and color coding.

        Args:
            display_name: Model display name (e.g., "Claude Opus 4")
            thinking_enabled: Whether thinking mode is enabled (used in cycle 1.3)

        Returns:
            Formatted string with medal emoji, color, and abbreviated name
        """
        _ = thinking_enabled  # Used in cycle 1.3 for thinking indicator
        tier = self._extract_model_tier(display_name)
        if tier is None:
            return display_name

        emoji = self.MODEL_EMOJI[tier]
        color = self.MODEL_COLORS[tier]
        name = self.MODEL_NAMES[tier]

        colored_name = self.colored(name, color)
        return f"{emoji} {colored_name}"

    def colored(self, text: str, color: str) -> str:
        """Wrap text in ANSI color codes.

        Args:
            text: The text to colorize
            color: Color name (red, green, yellow, blue, magenta, cyan, white)

        Returns:
            Text wrapped with ANSI color codes
        """
        color_code = self.COLORS.get(color, "")
        return f"{color_code}{text}{self.RESET}"

    def token_bar(self, tokens: int, max_tokens: int) -> str:
        """Generate Unicode block progress bar for token usage.

        Args:
            tokens: Current token count
            max_tokens: Maximum token limit

        Returns:
            Progress bar using Unicode block characters
        """
        if max_tokens <= 0:
            return ""

        percentage = (tokens / max_tokens) * 100
        block_chars = "▁▂▃▄▅▆▇█"

        # Calculate which block character to use (0-8)
        block_index = int((percentage / 100) * len(block_chars))
        block_index = min(block_index, len(block_chars) - 1)

        return block_chars[block_index]

    def vertical_bar(self, percentage: int) -> str:
        """Generate vertical bar character for usage percentage display.

        Args:
            percentage: Usage percentage (0-100)

        Returns:
            Colored vertical bar character based on percentage
        """
        block_chars = "▁▂▃▄▅▆▇█"

        # Calculate which block character to use (0-8)
        block_index = int((percentage / 100) * len(block_chars))
        block_index = min(block_index, len(block_chars) - 1)
        block_index = max(block_index, 0)

        char = block_chars[block_index]

        # Color based on percentage
        if percentage < 50:
            color = "green"
        elif percentage < 80:
            color = "yellow"
        else:
            color = "red"

        return self.colored(char, color)

    def format_plan_limits(self, data: PlanUsageData) -> str:
        """Format plan usage limits for 5h and 7d on one line.

        Args:
            data: PlanUsageData with hour5_pct, hour5_reset, day7_pct

        Returns:
            Formatted string with "5h {pct}% {bar} {reset} / 7d {pct}% {bar}"
        """
        hour5_bar = self.vertical_bar(int(data.hour5_pct))
        day7_bar = self.vertical_bar(int(data.day7_pct))
        hour5_str = f"5h {int(data.hour5_pct)}% {hour5_bar} {data.hour5_reset}"
        day7_str = f"7d {int(data.day7_pct)}% {day7_bar}"
        return f"{hour5_str} / {day7_str}"

    def format_tokens(self, tokens: int) -> str:
        """Convert token count to human-readable string.

        Args:
            tokens: Token count to format

        Returns:
            Human-readable string (e.g., "1k", "1.5M", "100")
        """
        if tokens < 1000:
            return str(tokens)
        if tokens < 1000000:
            # Display as thousands
            k = tokens // 1000
            return f"{k}k"
        # Display as millions
        m = tokens / 1000000
        if m == int(m):
            return f"{int(m)}M"
        return f"{m:.1f}M"
