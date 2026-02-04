"""Tests for statusline CLI command."""

from unittest.mock import patch

from click.testing import CliRunner

from claudeutils.statusline.cli import statusline
from claudeutils.statusline.models import (
    ContextUsage,
    ContextWindowInfo,
    CostInfo,
    ModelInfo,
    StatuslineInput,
    WorkspaceInfo,
)


def test_statusline_parses_json() -> None:
    """Test that statusline CLI parses JSON stdin into StatuslineInput model."""
    # Build valid StatuslineInput JSON
    input_data = StatuslineInput(
        model=ModelInfo(display_name="Claude Opus"),
        workspace=WorkspaceInfo(current_dir="/Users/david/code"),
        transcript_path="/path/to/transcript.md",
        context_window=ContextWindowInfo(
            current_usage=ContextUsage(
                input_tokens=1000,
                output_tokens=500,
                cache_creation_input_tokens=0,
                cache_read_input_tokens=0,
            ),
            context_window_size=200000,
        ),
        cost=CostInfo(total_cost_usd=0.05),
        version="1.0.0",
        session_id="test-session-123",
    )

    json_str = input_data.model_dump_json()

    runner = CliRunner()
    result = runner.invoke(statusline, input=json_str)

    # Should parse without error (exit code 0)
    assert result.exit_code == 0, f"CLI failed: {result.output}"
    # Should complete without raising a validation exception
    assert result.exception is None, f"JSON parsing failed: {result.exception}"


def test_statusline_calls_context_functions() -> None:
    """Test that statusline() calls all three context functions."""
    # Build valid StatuslineInput JSON
    input_data = StatuslineInput(
        model=ModelInfo(display_name="Claude Opus"),
        workspace=WorkspaceInfo(current_dir="/Users/david/code"),
        transcript_path="/path/to/transcript.md",
        context_window=ContextWindowInfo(
            current_usage=ContextUsage(
                input_tokens=1000,
                output_tokens=500,
                cache_creation_input_tokens=0,
                cache_read_input_tokens=0,
            ),
            context_window_size=200000,
        ),
        cost=CostInfo(total_cost_usd=0.05),
        version="1.0.0",
        session_id="test-session-123",
    )

    json_str = input_data.model_dump_json()

    runner = CliRunner()
    with (
        patch("claudeutils.statusline.cli.get_git_status") as mock_git,
        patch("claudeutils.statusline.cli.get_thinking_state") as mock_thinking,
        patch("claudeutils.statusline.cli.calculate_context_tokens") as mock_context,
    ):
        result = runner.invoke(statusline, input=json_str)

        # All three functions should be called
        assert mock_git.called, "get_git_status() was not called"
        assert mock_thinking.called, "get_thinking_state() was not called"
        assert mock_context.called, "calculate_context_tokens() was not called"
        # Should exit successfully
        assert result.exit_code == 0, f"CLI failed: {result.output}"
