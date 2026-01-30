"""Tests for Provider Protocol."""

from unittest.mock import Mock

from claudeutils.account import AnthropicProvider, Provider


def test_provider_protocol_exists() -> None:
    """Test that Provider protocol can be used in type annotation."""

    # This test verifies that Provider protocol exists and can be imported
    # and used as a type annotation target
    def process_provider(provider: Provider) -> None:
        """Use Provider as a type annotation."""

    assert True


def test_anthropic_provider_env_vars() -> None:
    """Test that AnthropicProvider.claude_env_vars returns ANTHROPIC_API_KEY."""
    # Create a mock KeyStore that returns a test API key
    mock_keystore = Mock()
    mock_keystore.get_anthropic_api_key.return_value = "test-anthropic-key"

    # Create AnthropicProvider with mock keystore
    provider = AnthropicProvider(mock_keystore)

    # Get environment variables
    env_vars = provider.claude_env_vars()

    # Verify ANTHROPIC_API_KEY is present and correct
    assert "ANTHROPIC_API_KEY" in env_vars
    assert env_vars["ANTHROPIC_API_KEY"] == "test-anthropic-key"
