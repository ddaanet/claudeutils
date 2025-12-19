"""Tests for the filtering module."""

from claudeutils.filtering import is_noise


def test_is_noise_command_output_detected() -> None:
    """Test that command output markers are detected as noise."""
    content = "<command-name>/clear</command-name>"
    assert is_noise(content) is True


def test_is_noise_bash_output_detected() -> None:
    """Test that bash output markers are detected as noise."""
    content = "<bash-stdout>test output</bash-stdout>"
    assert is_noise(content) is True


def test_is_noise_system_message_detected() -> None:
    """Test that system message markers are detected as noise."""
    content = "Caveat: The messages below"
    assert is_noise(content) is True


def test_is_noise_short_message_detected() -> None:
    """Test that short messages (< 10 chars) are detected as noise."""
    content = "hello"
    assert is_noise(content) is True
