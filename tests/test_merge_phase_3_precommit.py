"""Tests for worktree merge Phase 3 precommit validation."""

from pathlib import Path

import pytest
from click.testing import CliRunner

from claudeutils.worktree.cli import worktree
from claudeutils.worktree.commands import (
    apply_theirs_resolution,
    parse_precommit_failures,
)
from tests.test_merge_helpers import run_git, setup_repo_with_submodule


def test_merge_phase_3_post_merge_precommit_gate(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify mandatory precommit validation after merge commit."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)

    setup_repo_with_submodule(repo_path)

    runner = CliRunner()
    result = runner.invoke(worktree, ["new", "test-feature"])
    assert result.exit_code == 0

    worktree_path = repo_path / "wt" / "test-feature"

    (worktree_path / "worktree_file.txt").write_text("worktree change")
    run_git(["add", "worktree_file.txt"], cwd=worktree_path, check=True)
    run_git(["commit", "-m", "Worktree change"], cwd=worktree_path, check=True)

    before_count = int(
        run_git(
            ["rev-list", "--count", "HEAD"], cwd=repo_path, check=True
        ).stdout.strip()
    )

    merge_result = runner.invoke(worktree, ["merge", "test-feature"])
    assert merge_result.exit_code == 0, f"Merge failed: {merge_result.output}"

    after_count = int(
        run_git(
            ["rev-list", "--count", "HEAD"], cwd=repo_path, check=True
        ).stdout.strip()
    )
    assert after_count > before_count, (
        f"Merge commit not created: before={before_count}, after={after_count}"
    )

    log_result = run_git(["log", "--oneline"], cwd=repo_path, check=True)
    assert "🔀 Merge wt/test-feature" in log_result.stdout


def test_merge_phase_3_precommit_gate_passes_with_clean_merge(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify precommit gate validates ours after take-ours resolution."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)

    setup_repo_with_submodule(repo_path)

    runner = CliRunner()
    result = runner.invoke(worktree, ["new", "test-feature"])
    assert result.exit_code == 0

    worktree_path = repo_path / "wt" / "test-feature"

    conflict_file = repo_path / "module.py"
    conflict_file.write_text("import os\n\nprint('hello')\n")
    run_git(["add", "module.py"], cwd=repo_path, check=True)
    run_git(["commit", "-m", "Add clean module"], cwd=repo_path, check=True)

    wt_conflict = worktree_path / "module.py"
    wt_conflict.write_text("import os\nimport sys\n\nprint('hello')\n")
    run_git(["add", "module.py"], cwd=worktree_path, check=True)
    run_git(
        ["commit", "-m", "Add module with unused import"],
        cwd=worktree_path,
        check=True,
    )

    (repo_path / "parent_only.txt").write_text("parent-only content")
    run_git(["add", "parent_only.txt"], cwd=repo_path, check=True)
    run_git(["commit", "-m", "Parent-only change"], cwd=repo_path, check=True)

    merge_result = runner.invoke(worktree, ["merge", "test-feature"])
    assert merge_result.exit_code == 1
    assert "Merge conflicts detected" in merge_result.output

    resolved_content = "import os\n\nprint('hello')\n"
    conflict_file.write_text(resolved_content)
    run_git(["add", "module.py"], cwd=repo_path, check=True)

    merge_result = runner.invoke(worktree, ["merge", "test-feature"])
    assert merge_result.exit_code == 0, (
        f"Merge after resolution failed: {merge_result.output}"
    )

    merge_commit = run_git(
        ["rev-parse", "HEAD"], cwd=repo_path, check=True
    ).stdout.strip()
    assert len(merge_commit) == 40, "Merge commit hash should be 40 hex chars"
    assert merge_commit in merge_result.output or len(merge_result.output.strip()) > 0

    status_result = run_git(["status", "--porcelain"], cwd=repo_path, check=True)
    assert status_result.stdout.strip() == "", (
        f"Working tree should be clean after merge, got: {status_result.stdout}"
    )

    log_result = run_git(["log", "--oneline", "-1"], cwd=repo_path, check=True)
    assert "🔀 Merge wt/test-feature" in log_result.stdout


def test_merge_phase_3_precommit_gate_fallback_to_theirs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify precommit fallback logic when both ours and theirs fail."""
    stderr_cases = [
        ("file1.py: FAILED", ["file1.py"]),
        ("file1.py: FAILED\nfile2.py: FAILED", ["file1.py", "file2.py"]),
        ("module/file.py: FAILED (format)", ["module/file.py"]),
        ("unparseable error output", []),
    ]

    for stderr, expected_files in stderr_cases:
        result = parse_precommit_failures(stderr)
        assert result == expected_files, (
            f"Parse failed for '{stderr}': got {result}, expected {expected_files}"
        )

    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)

    setup_repo_with_submodule(repo_path)

    conflict_file = repo_path / "file1.py"
    conflict_file.write_text("original\n")
    run_git(["add", "file1.py"], cwd=repo_path, check=True)
    run_git(["commit", "-m", "Add file1"], cwd=repo_path, check=True)

    runner = CliRunner()
    result = runner.invoke(worktree, ["new", "test-feature"])
    assert result.exit_code == 0

    worktree_path = repo_path / "wt" / "test-feature"

    conflict_file.write_text("ours version\n")
    run_git(["add", "file1.py"], cwd=repo_path, check=True)
    run_git(["commit", "-m", "Parent modifies"], cwd=repo_path, check=True)

    wt_file = worktree_path / "file1.py"
    wt_file.write_text("theirs version\n")
    run_git(["add", "file1.py"], cwd=worktree_path, check=True)
    run_git(["commit", "-m", "Worktree modifies"], cwd=worktree_path, check=True)

    (repo_path / "other.txt").write_text("content")
    run_git(["add", "other.txt"], cwd=repo_path, check=True)
    run_git(["commit", "-m", "Parent adds other"], cwd=repo_path, check=True)

    result = run_git(
        ["merge", "--no-commit", "--no-ff", "test-feature"], cwd=repo_path, check=False
    )
    assert result.returncode != 0

    conflict_check = run_git(
        ["diff", "--name-only", "--diff-filter=U"], cwd=repo_path, check=True
    )
    assert "file1.py" in conflict_check.stdout

    resolution_result = apply_theirs_resolution(["file1.py"])
    assert resolution_result is True

    file_content = conflict_file.read_text()
    assert "theirs version" in file_content

    conflict_check2 = run_git(
        ["diff", "--name-only", "--diff-filter=U"], cwd=repo_path, check=True
    )
    assert "file1.py" not in conflict_check2.stdout


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
