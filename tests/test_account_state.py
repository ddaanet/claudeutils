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


def test_validate_consistency_valid_state() -> None:
    """Test that validate_consistency() returns empty list for valid state."""
    state = AccountState(
        mode="account",
        provider="anthropic",
        oauth_in_keychain=False,
        api_in_claude_env=False,
        base_url=None,
        has_api_key_helper=False,
        litellm_proxy_running=False,
    )
    assert state.validate_consistency() == []


def test_validate_plan_requires_oauth() -> None:
    """Test that plan mode requires OAuth credentials in keychain."""
    state = AccountState(
        mode="plan",
        provider="anthropic",
        oauth_in_keychain=False,
        api_in_claude_env=False,
        base_url=None,
        has_api_key_helper=False,
        litellm_proxy_running=False,
    )
    assert state.validate_consistency() == [
        "Plan mode requires OAuth credentials in keychain"
    ]


def test_validate_api_requires_key() -> None:
    """Test that API mode requires API key in environment or helper enabled."""
    state = AccountState(
        mode="api",
        provider="anthropic",
        oauth_in_keychain=False,
        api_in_claude_env=False,
        base_url=None,
        has_api_key_helper=False,
        litellm_proxy_running=False,
    )
    assert state.validate_consistency() == [
        "API mode requires API key in environment or helper enabled"
    ]


def test_validate_litellm_requires_proxy() -> None:
    """Test that LiteLLM provider requires proxy to be running."""
    state = AccountState(
        mode="account",
        provider="litellm",
        oauth_in_keychain=False,
        api_in_claude_env=False,
        base_url=None,
        has_api_key_helper=False,
        litellm_proxy_running=False,
    )
    assert state.validate_consistency() == [
        "LiteLLM provider requires proxy to be running"
    ]
