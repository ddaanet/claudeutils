"""Custom exceptions for claudeutils."""


class ClaudeUtilsError(Exception):
    """Base exception for all claudeutils errors."""


class ApiAuthenticationError(ClaudeUtilsError):
    """Raised when Anthropic API authentication fails."""

    def __init__(self) -> None:
        """Initialize with default authentication error message."""
        super().__init__(
            "Authentication failed. Please set the "
            "ANTHROPIC_API_KEY environment variable."
        )


class ApiRateLimitError(ClaudeUtilsError):
    """Raised when Anthropic API rate limit is exceeded."""

    def __init__(self) -> None:
        """Initialize with default rate limit error message."""
        super().__init__("API rate limit exceeded. Please try again later.")


class ModelResolutionError(ClaudeUtilsError):
    """Raised when model alias cannot be resolved via API."""

    def __init__(self, alias: str) -> None:
        """Initialize with model alias in error message."""
        super().__init__(
            f"Models API is unreachable and cannot resolve alias '{alias}'. "
            "This is a transient failure. Please retry."
        )
