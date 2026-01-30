"""AccountState Pydantic model for representing account configuration state."""

from pydantic import BaseModel


class AccountState(BaseModel):
    """Represents the current state of a Claude account configuration.

    Fields track various configuration aspects: authentication method
    (oauth vs api key), environment variables, base URL overrides, and
    proxy status.
    """

    mode: str
    provider: str
    oauth_in_keychain: bool
    api_in_claude_env: bool
    base_url: str | None = None
    has_api_key_helper: bool
    litellm_proxy_running: bool
