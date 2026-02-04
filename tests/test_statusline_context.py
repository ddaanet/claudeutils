"""Tests for statusline context module."""

import json
import subprocess
from unittest.mock import MagicMock, patch

from claudeutils.statusline.context import (
    calculate_context_tokens,
    get_git_status,
    get_thinking_state,
)
from claudeutils.statusline.models import (
    ContextUsage,
    ContextWindowInfo,
    CostInfo,
    GitStatus,
    ModelInfo,
    StatuslineInput,
    ThinkingState,
    WorkspaceInfo,
)


def test_get_git_status_in_repo() -> None:
    """Test get_git_status returns GitStatus with branch when in git repo."""
    with patch("subprocess.run") as mock_run:
        # Mock git rev-parse --git-dir (succeeds, repo exists)
        git_dir_process = MagicMock()
        git_dir_process.returncode = 0
        git_dir_process.stdout = ".git\n"

        # Mock git branch --show-current (succeeds, returns branch)
        branch_process = MagicMock()
        branch_process.returncode = 0
        branch_process.stdout = "main\n"

        # Mock git status --porcelain (succeeds, empty output = clean)
        status_process = MagicMock()
        status_process.returncode = 0
        status_process.stdout = ""

        # Return different mocks for each call
        mock_run.side_effect = [git_dir_process, branch_process, status_process]

        result = get_git_status()

        # Verify result
        assert isinstance(result, GitStatus)
        assert result.branch == "main"
        assert result.dirty is False

        # Verify subprocess calls
        assert mock_run.call_count == 3
        calls = mock_run.call_args_list
        assert calls[0][0][0] == ["git", "rev-parse", "--git-dir"]
        assert calls[1][0][0] == ["git", "branch", "--show-current"]
        assert calls[2][0][0] == ["git", "status", "--porcelain"]


def test_get_git_status_dirty() -> None:
    """Test get_git_status detects dirty working tree with porcelain output."""
    with patch("subprocess.run") as mock_run:
        # Mock git rev-parse --git-dir (succeeds, repo exists)
        git_dir_process = MagicMock()
        git_dir_process.returncode = 0
        git_dir_process.stdout = ".git\n"

        # Mock git branch --show-current (succeeds, returns branch)
        branch_process = MagicMock()
        branch_process.returncode = 0
        branch_process.stdout = "main\n"

        # Mock git status --porcelain (succeeds, non-empty output = dirty)
        status_process = MagicMock()
        status_process.returncode = 0
        status_process.stdout = " M file.txt\n"

        # Return different mocks for each call
        mock_run.side_effect = [git_dir_process, branch_process, status_process]

        result = get_git_status()

        # Verify result
        assert isinstance(result, GitStatus)
        assert result.branch == "main"
        assert result.dirty is True

        # Verify subprocess calls
        assert mock_run.call_count == 3
        calls = mock_run.call_args_list
        assert calls[0][0][0] == ["git", "rev-parse", "--git-dir"]
        assert calls[1][0][0] == ["git", "branch", "--show-current"]
        assert calls[2][0][0] == ["git", "status", "--porcelain"]


def test_get_git_status_not_in_repo() -> None:
    """Test get_git_status returns defaults when not in git repo."""
    with patch("subprocess.run") as mock_run:
        # Mock subprocess to raise CalledProcessError (not in git repo)
        mock_run.side_effect = subprocess.CalledProcessError(128, "git")

        result = get_git_status()

        # Verify result has branch=None and dirty=False
        assert isinstance(result, GitStatus)
        assert result.branch is None
        assert result.dirty is False


def test_get_thinking_state_enabled() -> None:
    """Test get_thinking_state returns ThinkingState with enabled=True.

    When alwaysThinkingEnabled is true in settings.json.
    """
    settings_data = {"alwaysThinkingEnabled": True}

    with patch("pathlib.Path.open", create=True) as mock_open:
        # Mock file content as JSON string
        mock_file = MagicMock()
        mock_file.__enter__.return_value.read.return_value = json.dumps(settings_data)
        mock_open.return_value = mock_file

        result = get_thinking_state()

        # Verify result
        assert isinstance(result, ThinkingState)
        assert result.enabled is True


def test_get_thinking_state_missing_file() -> None:
    """Test get_thinking_state returns disabled when settings.json missing."""
    with patch("pathlib.Path.home") as mock_home:
        # Mock Path.home() and then the missing file
        mock_path = MagicMock()
        mock_path.__truediv__.return_value = mock_path
        mock_path.open.side_effect = FileNotFoundError(
            "[Errno 2] No such file or directory: '~/.claude/settings.json'"
        )
        mock_home.return_value = mock_path

        result = get_thinking_state()

        # Verify result
        assert isinstance(result, ThinkingState)
        assert result.enabled is False


def test_calculate_context_tokens_from_current_usage() -> None:
    """Test calculate_context_tokens sums 4 token fields from current_usage."""
    # Create StatuslineInput with current_usage containing 4 token values
    current_usage = ContextUsage(
        input_tokens=100,
        output_tokens=50,
        cache_creation_input_tokens=25,
        cache_read_input_tokens=25,
    )
    context_window = ContextWindowInfo(
        current_usage=current_usage, context_window_size=200000
    )
    input_data = StatuslineInput(
        model=ModelInfo(display_name="Claude 3"),
        workspace=WorkspaceInfo(current_dir="/home/user"),
        transcript_path="/home/user/.claude/transcript.md",
        context_window=context_window,
        cost=CostInfo(total_cost_usd=0.05),
        version="1.0.0",
        session_id="sess-123",
    )

    # Call calculate_context_tokens
    result = calculate_context_tokens(input_data)

    # Should sum to 100 + 50 + 25 + 25 = 200
    assert result == 200
