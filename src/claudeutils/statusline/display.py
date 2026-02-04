"""ANSI colored text formatter for statusline display."""

from typing import ClassVar


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

    def limit_display(self, name: str, pct: int, reset: str) -> str:
        """Format limit display with name, percentage, and reset time.

        Args:
            name: Limit name (e.g., "claude-opus")
            pct: Percentage used (0-100)
            reset: Reset time (e.g., "2026-02-01")

        Returns:
            Formatted limit display with vertical bar and reset time
        """
        bar = self.vertical_bar(pct)
        return f"{name} {bar} {pct}% │ resets {reset}"

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
