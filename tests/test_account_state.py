"""Tests for AccountState model."""

from claudeutils.account import AccountState


def test_account_state_creation() -> None:
    """Test that AccountState model can be instantiated with required fields."""
    state = AccountState(
        mode="account",
        provider="anthropic",
        oauth_in_keychain=False,
        api_in_claude_env=False,
        base_url=None,
        has_api_key_helper=False,
        litellm_proxy_running=False,
    )
    assert state.mode == "account"
    assert state.provider == "anthropic"
    assert state.oauth_in_keychain is False
    assert state.api_in_claude_env is False
    assert state.base_url is None
    assert state.has_api_key_helper is False
    assert state.litellm_proxy_running is False
