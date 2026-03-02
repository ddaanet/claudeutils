"""Tests for session_structure validator."""

from pathlib import Path

from claudeutils.validation.session_structure import (
    check_cross_section_uniqueness,
    check_reference_files,
    extract_section_tasks,
    parse_sections,
    validate,
)


class TestParseSections:
    """Tests for parse_sections."""

    def test_single_section(self) -> None:
        """Single section parsed correctly."""
        lines = ["# Title\n", "## In-tree Tasks\n", "- task 1\n", "- task 2\n"]
        sections = parse_sections(lines)
        assert "In-tree Tasks" in sections
        assert len(sections["In-tree Tasks"]) == 2

    def test_multiple_sections(self) -> None:
        """Multiple sections parsed into separate entries."""
        lines = [
            "# Session\n",
            "## In-tree Tasks\n",
            "- task\n",
            "## Worktree Tasks\n",
            "- wt task\n",
            "## Reference Files\n",
            "- ref\n",
        ]
        sections = parse_sections(lines)
        assert len(sections) == 3
        assert "In-tree Tasks" in sections
        assert "Worktree Tasks" in sections
        assert "Reference Files" in sections

    def test_empty_section(self) -> None:
        """Empty section has no content lines."""
        lines = ["## Empty Section\n", "## Next Section\n", "content\n"]
        sections = parse_sections(lines)
        assert sections["Empty Section"] == []
        assert len(sections["Next Section"]) == 1

    def test_content_before_sections_ignored(self) -> None:
        """Content before first ## section not captured."""
        lines = ["# Title\n", "Preamble\n", "## Section\n", "content\n"]
        sections = parse_sections(lines)
        assert "Section" in sections
        assert len(sections) == 1


class TestExtractSectionTasks:
    """Tests for extract_section_tasks."""

    def test_extract_tasks(self) -> None:
        """Tasks extracted from section lines with correct line numbers."""
        section = [
            (5, "- [ ] **Task One** \u2014 desc"),
            (6, "  - Sub-item"),
            (7, "- [x] **Task Two** \u2014 done"),
        ]
        tasks = extract_section_tasks(section)
        assert len(tasks) == 2
        assert tasks[0] == (5, "Task One")
        assert tasks[1] == (7, "Task Two")

    def test_blocked_failed_canceled_statuses(self) -> None:
        """Tasks with [!], [\u2020], [-] statuses extracted."""
        section = [
            (5, "- [!] **Blocked Task** \u2014 waiting"),
            (6, "- [\u2020] **Failed Task** \u2014 terminal"),
            (7, "- [-] **Canceled Task** \u2014 canceled"),
        ]
        tasks = extract_section_tasks(section)
        assert len(tasks) == 3
        assert tasks[0] == (5, "Blocked Task")
        assert tasks[1] == (6, "Failed Task")
        assert tasks[2] == (7, "Canceled Task")

    def test_no_tasks(self) -> None:
        """Non-task lines produce empty result."""
        section = [(1, "Just text"), (2, "More text")]
        assert extract_section_tasks(section) == []


class TestCheckCrossSectionUniqueness:
    """Tests for check_cross_section_uniqueness."""

    def test_no_overlap(self) -> None:
        """Disjoint task sets produce no errors."""
        pending = [(5, "Task A"), (6, "Task B")]
        worktree = [(10, "Task C"), (11, "Task D")]
        assert check_cross_section_uniqueness(pending, worktree) == []

    def test_overlap_detected(self) -> None:
        """Task appearing in both sections flagged."""
        pending = [(5, "Task A")]
        worktree = [(10, "Task A")]
        errors = check_cross_section_uniqueness(pending, worktree)
        assert len(errors) == 1
        assert "both In-tree" in errors[0]
        assert "Worktree" in errors[0]

    def test_case_insensitive(self) -> None:
        """Overlap detection is case-insensitive."""
        pending = [(5, "Task A")]
        worktree = [(10, "task a")]
        errors = check_cross_section_uniqueness(pending, worktree)
        assert len(errors) == 1

    def test_empty_sections(self) -> None:
        """Empty sections produce no errors."""
        assert check_cross_section_uniqueness([], []) == []


class TestCheckReferenceFiles:
    """Tests for check_reference_files."""

    def test_existing_file_ok(self, tmp_path: Path) -> None:
        """Existing reference file passes."""
        (tmp_path / "plans").mkdir()
        (tmp_path / "plans" / "report.md").write_text("content")
        section = [(10, "- `plans/report.md` \u2014 desc")]
        assert check_reference_files(section, tmp_path) == []

    def test_missing_file_error(self, tmp_path: Path) -> None:
        """Missing reference file flagged."""
        section = [(10, "- `plans/missing.md` \u2014 desc")]
        errors = check_reference_files(section, tmp_path)
        assert len(errors) == 1
        assert "not found" in errors[0]
        assert "plans/missing.md" in errors[0]

    def test_non_ref_lines_skipped(self, tmp_path: Path) -> None:
        """Lines without backtick paths not checked."""
        section = [(10, "Just text, no backtick path")]
        assert check_reference_files(section, tmp_path) == []

    def test_multiple_refs(self, tmp_path: Path) -> None:
        """Only missing refs flagged, existing ones pass."""
        (tmp_path / "exists.md").write_text("ok")
        section = [
            (10, "- `exists.md` \u2014 exists"),
            (11, "- `missing.md` \u2014 missing"),
        ]
        errors = check_reference_files(section, tmp_path)
        assert len(errors) == 1
        assert "missing.md" in errors[0]


class TestValidate:
    """Tests for validate function."""

    def test_clean_session(self, tmp_path: Path) -> None:
        """Valid session with in-tree tasks passes."""
        (tmp_path / "session.md").write_text(
            "# Session\n\n## In-tree Tasks\n\n- [ ] **Task One** \u2014 desc\n"
        )
        assert validate("session.md", tmp_path) == []

    def test_missing_session(self, tmp_path: Path) -> None:
        """Missing session file returns no errors."""
        assert validate("session.md", tmp_path) == []

    def test_worktree_task_without_slug_ok(self, tmp_path: Path) -> None:
        """Worktree task without slug is valid (pre-dispatch classification)."""
        (tmp_path / "session.md").write_text(
            "# Session\n\n## Worktree Tasks\n\n- [ ] **My Task** \u2014 pre-dispatch\n"
        )
        assert validate("session.md", tmp_path) == []

    def test_cross_section_duplicate(self, tmp_path: Path) -> None:
        """Task in both In-tree and Worktree detected."""
        (tmp_path / "session.md").write_text(
            "# Session\n\n"
            "## In-tree Tasks\n\n"
            "- [ ] **Dup Task** \u2014 in in-tree\n\n"
            "## Worktree Tasks\n\n"
            "- [ ] **Dup Task** \u2192 `slug` \u2014 in worktree\n"
        )
        errors = validate("session.md", tmp_path)
        assert len(errors) == 1
        assert "both In-tree" in errors[0]

    def test_reference_file_missing(self, tmp_path: Path) -> None:
        """Missing reference file detected."""
        (tmp_path / "session.md").write_text(
            "# Session\n\n"
            "## Reference Files\n\n"
            "- `plans/nonexistent.md` \u2014 missing\n"
        )
        errors = validate("session.md", tmp_path)
        assert len(errors) == 1
        assert "not found" in errors[0]

    def test_reference_file_exists(self, tmp_path: Path) -> None:
        """Existing reference file passes."""
        plans = tmp_path / "plans"
        plans.mkdir()
        (plans / "report.md").write_text("content")
        (tmp_path / "session.md").write_text(
            "# Session\n\n## Reference Files\n\n- `plans/report.md` \u2014 exists\n"
        )
        assert validate("session.md", tmp_path) == []

    def test_no_worktree_section_ok(self, tmp_path: Path) -> None:
        """No Worktree Tasks section is valid."""
        (tmp_path / "session.md").write_text(
            "# Session\n\n## In-tree Tasks\n\n- [ ] **Task** \u2014 desc\n"
        )
        assert validate("session.md", tmp_path) == []

    def test_multiple_error_types(self, tmp_path: Path) -> None:
        """All error types reported together."""
        (tmp_path / "session.md").write_text(
            "# Session\n\n"
            "## In-tree Tasks\n\n"
            "- [ ] **Shared** \u2014 in-tree\n\n"
            "## Worktree Tasks\n\n"
            "- [ ] **No Arrow** \u2014 pre-dispatch\n"
            "- [ ] **Shared** \u2192 `slug` \u2014 duplicate\n\n"
            "## Reference Files\n\n"
            "- `missing.md` \u2014 gone\n"
        )
        errors = validate("session.md", tmp_path)
        assert len(errors) == 2  # cross-section duplicate + missing ref
