"""Tests for statusline CLI command."""

from unittest.mock import patch

from click.testing import CliRunner

from claudeutils.statusline.cli import statusline
from claudeutils.statusline.display import StatuslineFormatter
from claudeutils.statusline.models import (
    ContextUsage,
    ContextWindowInfo,
    CostInfo,
    GitStatus,
    ModelInfo,
    PythonEnv,
    StatuslineInput,
    ThinkingState,
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


def test_statusline_routes_to_plan_usage() -> None:
    """Test statusline() calls get_account_state and routes to plan_usage.

    When mode=plan, get_plan_usage() should be called and get_api_usage() should
    not be called.
    """
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
        patch("claudeutils.statusline.cli.get_git_status"),
        patch("claudeutils.statusline.cli.get_thinking_state"),
        patch("claudeutils.statusline.cli.calculate_context_tokens"),
        patch("claudeutils.statusline.cli.get_account_state") as mock_state,
        patch("claudeutils.statusline.cli.get_plan_usage") as mock_plan,
        patch("claudeutils.statusline.cli.get_api_usage") as mock_api,
    ):
        # Mock get_account_state to return mode="plan"
        mock_state.return_value.mode = "plan"

        result = runner.invoke(statusline, input=json_str)

        # Verify get_plan_usage was called
        assert mock_plan.called, "get_plan_usage() was not called"
        # Verify get_api_usage was NOT called
        assert not mock_api.called, (
            "get_api_usage() should not be called when mode=plan"
        )
        # Should exit successfully
        assert result.exit_code == 0, f"CLI failed: {result.output}"


def test_statusline_outputs_two_lines() -> None:
    """Test that statusline() formats and outputs two lines with real data."""
    # Build valid StatuslineInput JSON with all required fields
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
        patch("claudeutils.statusline.cli.get_account_state") as mock_account,
        patch("claudeutils.statusline.cli.get_plan_usage") as mock_plan,
    ):
        # Provide proper mock return values
        mock_git.return_value = GitStatus(branch="main", dirty=False)
        mock_thinking.return_value = ThinkingState(enabled=True)
        mock_context.return_value = 1500
        mock_account.return_value.mode = "plan"
        mock_plan.return_value = None

        result = runner.invoke(statusline, input=json_str)

        # Should exit successfully
        assert result.exit_code == 0, f"CLI failed: {result.output}"
        # Output should contain two lines
        lines = result.output.strip().split("\n")
        assert len(lines) == 2, f"Expected 2 lines, got {len(lines)}: {lines}"
        # Each line should have content (not empty)
        assert lines[0].strip(), "Line 1 is empty"
        assert lines[1].strip(), "Line 2 is empty"


def test_statusline_exits_zero_on_error() -> None:
    """Test that statusline CLI exits with code 0 even when an exception occurs.

    Mocks one of the data functions to raise an exception and verifies:
    1. CLI exits with code 0 (not 1)
    2. Error message is logged to stderr
    """
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
        patch("claudeutils.statusline.cli.get_thinking_state"),
        patch("claudeutils.statusline.cli.calculate_context_tokens"),
        patch("claudeutils.statusline.cli.get_account_state"),
        patch("claudeutils.statusline.cli.get_plan_usage"),
    ):
        # Mock get_git_status to raise an exception
        mock_git.side_effect = Exception("Test error: git command failed")

        result = runner.invoke(statusline, input=json_str)

        # Must exit with code 0 (not 1)
        assert result.exit_code == 0, (
            f"Expected exit code 0, got {result.exit_code}. Output: {result.output}"
        )
        # Error message must be in output (stderr via click.echo(err=True))
        assert "Error:" in result.output, (
            f"Error message should be present in output. Output: '{result.output}'"
        )


def test_cli_visual_line_structure() -> None:
    """Test that CLI outputs correct line structure with all visual elements."""
    input_data = StatuslineInput(
        model=ModelInfo(display_name="Claude Opus 4"),
        workspace=WorkspaceInfo(current_dir="/Users/david/code/claudeutils"),
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
        cost=CostInfo(total_cost_usd=1.23),
        version="1.0.0",
        session_id="test-session-123",
    )

    json_str = input_data.model_dump_json()
    runner = CliRunner()

    with (
        patch("claudeutils.statusline.cli.get_git_status") as mock_git,
        patch("claudeutils.statusline.cli.get_python_env") as mock_python,
        patch("claudeutils.statusline.cli.get_thinking_state") as mock_thinking,
        patch("claudeutils.statusline.cli.calculate_context_tokens") as mock_context,
        patch("claudeutils.statusline.cli.get_account_state") as mock_account,
        patch("claudeutils.statusline.cli.get_plan_usage") as mock_plan,
    ):
        mock_git.return_value = GitStatus(branch="main", dirty=False)
        mock_python.return_value = PythonEnv(name=".venv")
        mock_thinking.return_value = ThinkingState(enabled=True)
        mock_context.return_value = 50000
        mock_account.return_value.mode = "plan"
        mock_plan.return_value = None

        result = runner.invoke(statusline, input=json_str)

        assert result.exit_code == 0, f"CLI failed: {result.output}"
        lines = result.output.strip().split("\n")
        assert len(lines) == 2, f"Expected 2 lines, got {len(lines)}: {lines}"

        line1 = lines[0]
        line2 = lines[1]

        # Verify Line 1 has all required emoji
        assert "🥇" in line1, "Line 1 missing Opus medal emoji"
        assert "📁" in line1, "Line 1 missing directory emoji"
        assert "✅" in line1, "Line 1 missing clean git status emoji"
        assert "💰" in line1, "Line 1 missing cost emoji"
        assert "🧠" in line1, "Line 1 missing brain emoji"

        # Verify abbreviations and Opus bold styling
        assert "Opus" in line1, "Line 1 should contain 'Opus' abbreviation"
        assert "\033[1m" in line1, "Opus should be bold (matches shell)"

        # Verify no brackets around token bar (matches shell reference)
        # Token bar uses Unicode blocks directly without wrapping brackets
        assert "]" not in line1, "Line 1 should not have bracket (matches shell)"

        # Verify Line 2 structure
        has_mode_emoji = "🎫" in line2 or "💳" in line2
        assert has_mode_emoji, "Line 2 should contain mode emoji"


def test_cli_formatter_blink_code() -> None:
    """Test that formatter includes blink code for high token counts."""
    formatter = StatuslineFormatter()
    high_token_output = formatter.format_context(160000)
    has_blink_code = "\x1b[5m" in high_token_output
    assert has_blink_code, "Formatter should include blink for high token count"
    assert "160k" in high_token_output, "Formatter should display high token count"


def test_cli_double_space_separators() -> None:
    """Test that CLI line 1 sections are separated by double spaces.

    Verifies pattern: emoji text  emoji text  emoji text
    """
    input_data = StatuslineInput(
        model=ModelInfo(display_name="Claude Sonnet 4"),
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
        cost=CostInfo(total_cost_usd=0.50),
        version="1.0.0",
        session_id="test-session",
    )

    json_str = input_data.model_dump_json()
    runner = CliRunner()

    with (
        patch("claudeutils.statusline.cli.get_git_status") as mock_git,
        patch("claudeutils.statusline.cli.get_python_env") as mock_python,
        patch("claudeutils.statusline.cli.get_thinking_state") as mock_thinking,
        patch("claudeutils.statusline.cli.calculate_context_tokens") as mock_context,
        patch("claudeutils.statusline.cli.get_account_state") as mock_account,
        patch("claudeutils.statusline.cli.get_plan_usage") as mock_plan,
    ):
        mock_git.return_value = GitStatus(branch="main", dirty=False)
        mock_python.return_value = PythonEnv(name=None)
        mock_thinking.return_value = ThinkingState(enabled=True)
        mock_context.return_value = 1500
        mock_account.return_value.mode = "plan"
        mock_plan.return_value = None

        result = runner.invoke(statusline, input=json_str)

        assert result.exit_code == 0
        line1 = result.output.strip().split("\n")[0]

        # Remove ANSI codes to check spacing pattern
        import re

        clean_line = re.sub(r"\033\[[0-9;]+m", "", line1)

        # Verify double-space separators between sections
        # Pattern should have "  " (two spaces) between emoji sections
        assert "  " in clean_line, "Line 1 should have double-space separators"


def test_cli_python_env_conditional() -> None:
    """Test Python env conditional inclusion in line 1.

    With env: 🐍 and name appear in line 1
    Without env: 🐍 absent from line 1, no extra spacing
    """
    input_data = StatuslineInput(
        model=ModelInfo(display_name="Claude Sonnet 4"),
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
        cost=CostInfo(total_cost_usd=0.50),
        version="1.0.0",
        session_id="test-session",
    )

    json_str = input_data.model_dump_json()
    runner = CliRunner()

    # Test case 1: With Python env
    with (
        patch("claudeutils.statusline.cli.get_git_status") as mock_git,
        patch("claudeutils.statusline.cli.get_python_env") as mock_python,
        patch("claudeutils.statusline.cli.get_thinking_state") as mock_thinking,
        patch("claudeutils.statusline.cli.calculate_context_tokens") as mock_context,
        patch("claudeutils.statusline.cli.get_account_state") as mock_account,
        patch("claudeutils.statusline.cli.get_plan_usage") as mock_plan,
    ):
        mock_git.return_value = GitStatus(branch="main", dirty=False)
        mock_python.return_value = PythonEnv(name=".venv")
        mock_thinking.return_value = ThinkingState(enabled=True)
        mock_context.return_value = 1500
        mock_account.return_value.mode = "plan"
        mock_plan.return_value = None

        result = runner.invoke(statusline, input=json_str)

        assert result.exit_code == 0
        line1 = result.output.strip().split("\n")[0]

        # Should contain 🐍 and .venv
        assert "🐍" in line1
        assert ".venv" in line1

    # Test case 2: Without Python env
    with (
        patch("claudeutils.statusline.cli.get_git_status") as mock_git,
        patch("claudeutils.statusline.cli.get_python_env") as mock_python,
        patch("claudeutils.statusline.cli.get_thinking_state") as mock_thinking,
        patch("claudeutils.statusline.cli.calculate_context_tokens") as mock_context,
        patch("claudeutils.statusline.cli.get_account_state") as mock_account,
        patch("claudeutils.statusline.cli.get_plan_usage") as mock_plan,
    ):
        mock_git.return_value = GitStatus(branch="main", dirty=False)
        mock_python.return_value = PythonEnv(name=None)
        mock_thinking.return_value = ThinkingState(enabled=True)
        mock_context.return_value = 1500
        mock_account.return_value.mode = "plan"
        mock_plan.return_value = None

        result = runner.invoke(statusline, input=json_str)

        assert result.exit_code == 0
        line1 = result.output.strip().split("\n")[0]

        # Should NOT contain 🐍
        assert "🐍" not in line1


def test_cli_ansi_color_preservation() -> None:
    """Test that CLI output preserves ANSI escape sequences.

    Verifies that color codes survive click.echo(color=True).
    """
    input_data = StatuslineInput(
        model=ModelInfo(display_name="Claude Opus 4"),
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
        cost=CostInfo(total_cost_usd=0.50),
        version="1.0.0",
        session_id="test-session",
    )

    json_str = input_data.model_dump_json()
    runner = CliRunner()

    with (
        patch("claudeutils.statusline.cli.get_git_status") as mock_git,
        patch("claudeutils.statusline.cli.get_python_env") as mock_python,
        patch("claudeutils.statusline.cli.get_thinking_state") as mock_thinking,
        patch("claudeutils.statusline.cli.calculate_context_tokens") as mock_context,
        patch("claudeutils.statusline.cli.get_account_state") as mock_account,
        patch("claudeutils.statusline.cli.get_plan_usage") as mock_plan,
    ):
        mock_git.return_value = GitStatus(branch="main", dirty=False)
        mock_python.return_value = PythonEnv(name=None)
        mock_thinking.return_value = ThinkingState(enabled=True)
        mock_context.return_value = 1500
        mock_account.return_value.mode = "plan"
        mock_plan.return_value = None

        result = runner.invoke(statusline, input=json_str)

        assert result.exit_code == 0

        # CLI output should contain ANSI escape sequences
        assert "\033[" in result.output, "Output should contain ANSI codes"
