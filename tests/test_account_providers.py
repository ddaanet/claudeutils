"""Tests for Provider Protocol."""

from claudeutils.account import Provider


def test_provider_protocol_exists() -> None:
    """Test that Provider protocol can be used in type annotation."""

    # This test verifies that Provider protocol exists and can be imported
    # and used as a type annotation target
    def process_provider(provider: Provider) -> None:
        """Use Provider as a type annotation."""

    assert True
