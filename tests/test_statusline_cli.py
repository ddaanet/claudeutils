"""Tests for statusline CLI command."""

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
