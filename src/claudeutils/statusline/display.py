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
