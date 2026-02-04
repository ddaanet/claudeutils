"""Tests for statusline context module."""

from unittest.mock import MagicMock, patch

from claudeutils.statusline.context import get_git_status
from claudeutils.statusline.models import GitStatus


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

        # Return different mocks for each call
        mock_run.side_effect = [git_dir_process, branch_process]

        result = get_git_status()

        # Verify result
        assert isinstance(result, GitStatus)
        assert result.branch == "main"
        assert result.dirty is False

        # Verify subprocess calls
        assert mock_run.call_count == 2
        calls = mock_run.call_args_list
        assert calls[0][0][0] == ["git", "rev-parse", "--git-dir"]
        assert calls[1][0][0] == ["git", "branch", "--show-current"]
