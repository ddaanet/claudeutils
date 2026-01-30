"""Provider Protocol for account providers."""

from typing import Protocol


class Provider(Protocol):
    """Protocol defining the interface for account providers."""

    @property
    def name(self) -> str:
        """Get the provider name."""
        ...

    def claude_env_vars(self) -> dict[str, str]:
        """Get environment variables needed for this provider."""
        ...

    def validate(self) -> list[str]:
        """Validate provider configuration.

        Returns list of issues.
        """
        ...

    def settings_json_patch(self) -> dict[str, object]:
        """Get the patch to apply to settings.json for this provider."""
        ...
