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
    validate,
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


class TestValidate:
    """Tests for validate function."""

    def test_valid_session_returns_no_errors(self, tmp_path: Path) -> None:
        """Test that valid session returns no errors."""
        session_file = tmp_path / "session.md"
        session_file.write_text("""# Session Handoff

## Pending Tasks

- [ ] **Task One** — description
- [ ] **Task Two** — another task
""")
        learnings_file = tmp_path / "learnings.md"
        learnings_file.write_text("""# Learnings

## Some Learning
""")
        errors = validate("session.md", "learnings.md", tmp_path)
        assert errors == []

    def test_duplicate_task_names_detected(self, tmp_path: Path) -> None:
        """Test that duplicate task names are detected."""
        session_file = tmp_path / "session.md"
        session_file.write_text("""# Session Handoff

## Pending Tasks

- [ ] **Task One** — first
- [ ] **Task Two** — second
- [ ] **Task One** — duplicate
""")
        learnings_file = tmp_path / "learnings.md"
        learnings_file.write_text("# Learnings\n")
        errors = validate("session.md", "learnings.md", tmp_path)
        assert len(errors) == 1
        assert "duplicate task name" in errors[0]
        assert "Task One" in errors[0]

    def test_duplicate_task_names_case_insensitive(self, tmp_path: Path) -> None:
        """Test that duplicate detection is case-insensitive."""
        session_file = tmp_path / "session.md"
        session_file.write_text("""# Session Handoff

## Pending Tasks

- [ ] **Task One** — first
- [ ] **task one** — duplicate
""")
        learnings_file = tmp_path / "learnings.md"
        learnings_file.write_text("# Learnings\n")
        errors = validate("session.md", "learnings.md", tmp_path)
        assert len(errors) == 1
        assert "duplicate" in errors[0]

    def test_task_conflicts_with_learning_key(self, tmp_path: Path) -> None:
        """Test that task names conflicting with learning keys are detected."""
        session_file = tmp_path / "session.md"
        session_file.write_text("""# Session Handoff

## Pending Tasks

- [ ] **Conflicting Task** — description
""")
        learnings_file = tmp_path / "learnings.md"
        learnings_file.write_text("""# Learnings

## Conflicting Task
Content here.
""")
        errors = validate("session.md", "learnings.md", tmp_path)
        assert len(errors) == 1
        assert "task name conflicts with learning key" in errors[0]
        assert "Conflicting Task" in errors[0]

    def test_task_conflict_case_insensitive(self, tmp_path: Path) -> None:
        """Test that conflict detection is case-insensitive."""
        session_file = tmp_path / "session.md"
        session_file.write_text("""# Session Handoff

## Pending Tasks

- [ ] **conflicting task** — description
""")
        learnings_file = tmp_path / "learnings.md"
        learnings_file.write_text("""# Learnings

## Conflicting Task
""")
        errors = validate("session.md", "learnings.md", tmp_path)
        assert len(errors) == 1
        assert "conflicts" in errors[0]

    @patch("claudeutils.validation.tasks.check_history")
    @patch("claudeutils.validation.tasks.get_new_tasks")
    def test_new_task_in_git_history_error(
        self,
        mock_get_new: MagicMock,
        mock_check_history: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Test that new task found in history is flagged."""
        session_file = tmp_path / "session.md"
        session_file.write_text("""# Session Handoff

## Pending Tasks

- [ ] **New Task** — description
""")
        learnings_file = tmp_path / "learnings.md"
        learnings_file.write_text("# Learnings\n")
        mock_get_new.return_value = ["New Task"]
        mock_check_history.return_value = True
        errors = validate("session.md", "learnings.md", tmp_path)
        assert len(errors) == 1
        assert "exists in git history" in errors[0]
        assert "New Task" in errors[0]

    def test_missing_session_file_returns_no_errors(self, tmp_path: Path) -> None:
        """Test that missing session file returns no errors.

        Graceful degradation behavior.
        """
        errors = validate("nonexistent.md", "nonexistent.md", tmp_path)
        assert errors == []

    def test_missing_learnings_file_still_validates_tasks(self, tmp_path: Path) -> None:
        """Test that missing learnings file validation continues.

        Missing learnings file doesn't prevent task validation.
        """
        session_file = tmp_path / "session.md"
        session_file.write_text("""# Session Handoff

## Pending Tasks

- [ ] **Task One** — description
- [ ] **Task One** — duplicate
""")
        errors = validate("session.md", "nonexistent.md", tmp_path)
        assert len(errors) == 1
        assert "duplicate" in errors[0]

    def test_multiple_errors_all_reported(self, tmp_path: Path) -> None:
        """Test that all errors are reported, not just first."""
        session_file = tmp_path / "session.md"
        session_file.write_text("""# Session Handoff

## Pending Tasks

- [ ] **Task One** — first
- [ ] **task one** — duplicate
- [ ] **Learning Key** — conflicts
""")
        learnings_file = tmp_path / "learnings.md"
        learnings_file.write_text("""# Learnings

## Learning Key
Content.
""")
        errors = validate("session.md", "learnings.md", tmp_path)
        assert len(errors) == 2
        assert any("duplicate" in e for e in errors)
        assert any("conflicts" in e for e in errors)

    def test_line_numbers_reported_correctly(self, tmp_path: Path) -> None:
        """Test that line numbers are reported correctly."""
        session_file = tmp_path / "session.md"
        session_file.write_text("""# Session Handoff

Line 3
Line 4
## Pending Tasks

Line 7
- [ ] **Task One** — line 8
- [ ] **Task Two** — line 9
- [ ] **Task One** — line 10 (duplicate)
""")
        learnings_file = tmp_path / "learnings.md"
        learnings_file.write_text("# Learnings\n")
        errors = validate("session.md", "learnings.md", tmp_path)
        assert len(errors) == 1
        assert "line 10" in errors[0]
        assert "first at line 8" in errors[0]
