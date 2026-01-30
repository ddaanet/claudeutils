"""Tests for Keychain wrapper."""

from unittest.mock import Mock, patch

from claudeutils.account import Keychain


def test_keychain_find_success() -> None:
    """Test that Keychain.find() returns password when keychain entry exists."""
    # Mock subprocess.run to return successful output from security command
    # Note: -w flag returns just the password without label
    mock_result = Mock()
    mock_result.stdout = b"test-password-value"
    mock_result.returncode = 0

    with patch("subprocess.run", return_value=mock_result) as mock_run:
        # Create Keychain instance and call find
        keychain = Keychain()
        password = keychain.find("test-account", "test-service")

        # Verify subprocess was called with correct arguments
        mock_run.assert_called_once_with(
            [
                "security",
                "find-generic-password",
                "-a",
                "test-account",
                "-s",
                "test-service",
                "-w",
            ],
            capture_output=True,
            text=False,
            check=False,
        )

        # Verify password is extracted and returned
        assert password == "test-password-value"  # noqa: S105
