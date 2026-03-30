"""Tests for stop hook status display module."""

import pytest

from claudeutils.hooks.stop_status_display import (
    process_hook,
    should_trigger,
)


class TestShouldTrigger:
    """Parametrized tests for trigger detection."""

    @pytest.mark.parametrize(
        ("message", "expected"),
        [
            ("Status.", True),
            ("Check the Status.", False),
            ("Status", False),
            ("Status.\nMore text", False),
            ("", False),
        ],
    )
    def test_should_trigger(
        self,
        message: str,
        expected: bool,  # noqa: FBT001
    ) -> None:
        """Test trigger detection with various inputs."""
        assert should_trigger(message) is expected


class TestProcessHookLoopGuard:
    """Test loop guard in process_hook."""

    def test_process_hook_loop_guard_active(self) -> None:
        """Returns None when stop_hook_active is True."""
        result = process_hook(
            {
                "last_assistant_message": "Status.",
                "stop_hook_active": True,
            }
        )
        assert result is None

    def test_process_hook_triggered_with_status(self) -> None:
        """Returns systemMessage when triggered.

        Uses mock status_fn to avoid CLI dependency.
        """
        result = process_hook(
            {
                "last_assistant_message": "Status.",
                "stop_hook_active": False,
            },
            status_fn=lambda: "mock status output",
        )
        assert result is not None
        assert "systemMessage" in result
