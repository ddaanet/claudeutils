"""Tests for tasks validator."""

import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from claudeutils.validation.tasks import (
    check_history,
    extract_learning_keys,
    extract_task_names,
    get_merge_parents,
    get_new_tasks,
    get_session_from_commit,
    get_staged_session,
)


class TestExtractTaskNames:
    """Tests for extract_task_names function."""

    def test_extract_single_task(self) -> None:
        """Test extracting a single task."""
        lines = [
            "# Session Handoff",
            "",
            "## Pending Tasks",
            "",
            "- [ ] **Task One** — description here",
        ]
        tasks = extract_task_names(lines)
        assert tasks == [(5, "Task One")]

    def test_extract_multiple_tasks(self) -> None:
        """Test extracting multiple tasks."""
        lines = [
            "## Pending Tasks",
            "- [ ] **Task One** — description",
            "- [x] **Task Two** — done",
            "- [>] **Task Three** — in progress",
        ]
        tasks = extract_task_names(lines)
        assert len(tasks) == 3
        assert tasks[0] == (2, "Task One")
        assert tasks[1] == (3, "Task Two")
        assert tasks[2] == (4, "Task Three")

    def test_extract_tasks_with_special_characters(self) -> None:
        """Test extracting tasks with special characters in names."""
        lines = [
            "- [ ] **Task (With Parens)** — desc",
            "- [ ] **Task [With Brackets]** — desc",
        ]
        tasks = extract_task_names(lines)
        assert len(tasks) == 2
        assert tasks[0][1] == "Task (With Parens)"
        assert tasks[1][1] == "Task [With Brackets]"

    def test_no_tasks_returns_empty_list(self) -> None:
        """Test that file with no tasks returns empty list."""
        lines = [
            "# Session Handoff",
            "",
            "Some content",
            "More content",
        ]
        tasks = extract_task_names(lines)
        assert tasks == []

    def test_malformed_task_line_ignored(self) -> None:
        """Test that malformed task lines are ignored."""
        lines = [
            "- [ ] Task One — missing asterisks",
            "- [ ] **Task Two — missing closing asterisk",
            "- [ ] **Task Three** — valid",
        ]
        tasks = extract_task_names(lines)
        assert tasks == [(3, "Task Three")]


class TestExtractLearningKeys:
    """Tests for extract_learning_keys function."""

    def test_extract_learning_keys(self) -> None:
        """Test extracting learning keys from ## headers."""
        lines = [
            "# Learnings",
            "Intro text",
            "More intro",
            "## First Learning",
            "Content here",
            "## Second Learning",
            "More content",
        ]
        keys = extract_learning_keys(lines)
        assert keys == {"first learning", "second learning"}

    def test_learning_keys_lowercase(self) -> None:
        """Test that learning keys are lowercase."""
        lines = [
            "# Learnings",
            "## Capital Letters HERE",
            "content",
        ]
        keys = extract_learning_keys(lines)
        assert "capital letters here" in keys

    def test_no_h1_title_skip_keys(self) -> None:
        """Test that keys before H1 are skipped."""
        lines = [
            "## Should Not Match",
            "## Also Should Not Match",
            "# Main Title",
            "## Should Match",
            "content",
        ]
        keys = extract_learning_keys(lines)
        assert keys == {"should match"}

    def test_empty_file_no_keys(self) -> None:
        """Test that empty file returns no keys."""
        lines: list[str] = []
        keys = extract_learning_keys(lines)
        assert keys == set()


class TestGetSessionFromCommit:
    """Tests for get_session_from_commit function."""

    @patch("claudeutils.validation.tasks.subprocess.run")
    def test_get_session_from_commit_success(self, mock_run: MagicMock) -> None:
        """Test successful retrieval of session from commit."""
        mock_run.return_value = MagicMock(stdout="line 1\nline 2\nline 3", returncode=0)
        result = get_session_from_commit("HEAD", Path("agents/session.md"))
        assert result == ["line 1", "line 2", "line 3"]
        mock_run.assert_called_once()

    @patch("claudeutils.validation.tasks.subprocess.run")
    def test_get_session_from_commit_not_found(self, mock_run: MagicMock) -> None:
        """Test graceful handling when commit file not found."""
        mock_run.side_effect = subprocess.CalledProcessError(1, "git")
        result = get_session_from_commit("MISSING_REF", Path("agents/session.md"))
        assert result == []


class TestGetMergeParents:
    """Tests for get_merge_parents function."""

    @patch("claudeutils.validation.tasks.subprocess.run")
    def test_get_merge_parents_in_merge(self, mock_run: MagicMock) -> None:
        """Test detection of merge in progress."""
        # First call returns merge head, second returns head
        mock_run.side_effect = [
            MagicMock(returncode=0, stdout="merge_head_hash\n"),
            MagicMock(returncode=0, stdout="head_hash\n"),
        ]
        result = get_merge_parents()
        assert result == ("head_hash", "merge_head_hash")

    @patch("claudeutils.validation.tasks.subprocess.run")
    def test_get_merge_parents_not_in_merge(self, mock_run: MagicMock) -> None:
        """Test detection when not in a merge."""
        mock_run.return_value = MagicMock(returncode=1)
        result = get_merge_parents()
        assert result is None


class TestGetStagedSession:
    """Tests for get_staged_session function."""

    @patch("claudeutils.validation.tasks.subprocess.run")
    def test_get_staged_session_success(self, mock_run: MagicMock) -> None:
        """Test successful retrieval of staged session."""
        mock_run.return_value = MagicMock(
            stdout="staged line 1\nstaged line 2", returncode=0
        )
        result = get_staged_session(Path("agents/session.md"))
        assert result == ["staged line 1", "staged line 2"]

    @patch("claudeutils.validation.tasks.subprocess.run")
    def test_get_staged_session_not_staged(self, mock_run: MagicMock) -> None:
        """Test graceful handling when file not staged."""
        mock_run.side_effect = subprocess.CalledProcessError(1, "git")
        result = get_staged_session(Path("agents/session.md"))
        assert result == []


class TestGetNewTasks:
    """Tests for get_new_tasks function."""

    @patch("claudeutils.validation.tasks.get_staged_session")
    @patch("claudeutils.validation.tasks.get_merge_parents")
    @patch("claudeutils.validation.tasks.get_session_from_commit")
    def test_get_new_tasks_regular_commit(
        self,
        mock_get_session: MagicMock,
        mock_get_merge: MagicMock,
        mock_get_staged: MagicMock,
    ) -> None:
        """Test new task detection in regular commit."""
        lines: list[str] = [
            "- [ ] **Task One** — desc",
            "- [ ] **Task Two** — desc",
        ]
        mock_get_merge.return_value = None
        mock_get_staged.return_value = lines
        mock_get_session.return_value = [
            "- [ ] **Task One** — desc",
        ]
        result = get_new_tasks(Path("agents/session.md"))
        assert "Task Two" in result

    @patch("claudeutils.validation.tasks.subprocess.run")
    @patch("claudeutils.validation.tasks.get_staged_session")
    @patch("claudeutils.validation.tasks.get_merge_parents")
    @patch("claudeutils.validation.tasks.get_session_from_commit")
    def test_get_new_tasks_merge_commit(
        self,
        mock_get_session: MagicMock,
        mock_get_merge: MagicMock,
        mock_get_staged: MagicMock,
        mock_run: MagicMock,
    ) -> None:
        """Test new task detection in merge commit (C-1 constraint).

        A task is new only if absent from ALL parents.
        """
        mock_get_merge.return_value = ("parent1", "parent2")
        mock_run.return_value = MagicMock(
            returncode=0, stdout="commit parent1 parent2\n"
        )
        mock_get_staged.return_value = [
            "- [ ] **Task One** — desc",
            "- [ ] **Task Two** — desc",
            "- [ ] **Task Three** — desc",
        ]
        mock_get_session.side_effect = [
            # parent1 session
            ["- [ ] **Task One** — desc"],
            # parent2 session
            ["- [ ] **Task Two** — desc"],
        ]
        result = get_new_tasks(Path("agents/session.md"))
        # Task Three is absent from both parents, so it's new
        assert "Task Three" in result
        # Task One and Two are present in at least one parent
        assert "Task One" not in result
        assert "Task Two" not in result

    @patch("claudeutils.validation.tasks.subprocess.run")
    def test_get_new_tasks_octopus_merge_error(self, mock_run: MagicMock) -> None:
        """Test octopus merge detection raises error."""
        with (
            patch("claudeutils.validation.tasks.get_merge_parents") as mock_merge,
            patch("claudeutils.validation.tasks.get_staged_session") as mock_staged,
        ):
            mock_merge.return_value = ("p1", "p2")
            mock_staged.return_value = []
            # Simulate octopus merge with 3 parents
            mock_run.return_value = MagicMock(returncode=0, stdout="commit p1 p2 p3\n")
            with pytest.raises(SystemExit):
                get_new_tasks(Path("agents/session.md"))


class TestCheckHistory:
    """Tests for check_history function."""

    @patch("claudeutils.validation.tasks.subprocess.run")
    def test_check_history_found(self, mock_run: MagicMock) -> None:
        """Test task name found in history."""
        mock_run.return_value = MagicMock(stdout="hash1\nhash2", returncode=0)
        result = check_history("Task Name")
        assert result is True

    @patch("claudeutils.validation.tasks.subprocess.run")
    def test_check_history_not_found(self, mock_run: MagicMock) -> None:
        """Test task name not found in history."""
        mock_run.return_value = MagicMock(stdout="", returncode=0)
        result = check_history("Task Name")
        assert result is False

    @patch("claudeutils.validation.tasks.subprocess.run")
    def test_check_history_case_insensitive(self, mock_run: MagicMock) -> None:
        """Test history search is case-insensitive."""
        mock_run.return_value = MagicMock(stdout="hash1", returncode=0)
        result = check_history("task name")
        assert result is True
        # Verify --regexp-ignore-case was passed
        call_args = mock_run.call_args[0][0]
        assert "--regexp-ignore-case" in call_args
