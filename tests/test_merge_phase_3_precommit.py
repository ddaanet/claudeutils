"""Tests for worktree merge Phase 3 precommit validation."""

import subprocess
from pathlib import Path

import pytest
from click.testing import CliRunner

from claudeutils.worktree.cli import worktree
from claudeutils.worktree.merge_helpers import (
    apply_theirs_resolution,
    parse_precommit_failures,
)
from tests.conftest_git import run_git, setup_repo_with_submodule


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


def test_apply_theirs_resolution_replaces_merged_content_post_commit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Post-commit: replaces merged content with theirs (second parent) version."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)
    setup_repo_with_submodule(repo_path)

    # File with enough separation for clean three-way merge
    initial = "HEADER = 'original'\n" + "\n" * 8 + "def main():\n    pass\n"
    target = repo_path / "file1.py"
    target.write_text(initial)
    run_git(["add", "file1.py"], cwd=repo_path, check=True)
    run_git(["commit", "-m", "Add file1"], cwd=repo_path, check=True)

    # Feature branch modifies bottom (theirs)
    theirs_content = (
        "HEADER = 'original'\n" + "\n" * 8
        + "def main():\n    print('theirs')\n"
    )
    run_git(["checkout", "-b", "feature"], cwd=repo_path, check=True)
    target.write_text(theirs_content)
    run_git(["add", "file1.py"], cwd=repo_path, check=True)
    run_git(["commit", "-m", "Feature: fix main"], cwd=repo_path, check=True)

    # Main modifies top (ours) — merge will combine both non-overlapping changes
    run_git(["checkout", "main"], cwd=repo_path, check=True)
    ours_content = "HEADER = 'ours_dirty'\n" + "\n" * 8 + "def main():\n    pass\n"
    target.write_text(ours_content)
    run_git(["add", "file1.py"], cwd=repo_path, check=True)
    run_git(["commit", "-m", "Main: dirty header"], cwd=repo_path, check=True)

    # Merge commit — clean merge produces combined content (neither ours nor theirs)
    run_git(
        ["merge", "--no-ff", "feature", "-m", "Merge feature"],
        cwd=repo_path,
        check=True,
    )
    merged = target.read_text()
    assert "ours_dirty" in merged, "Sanity: merge has ours"
    assert "theirs" in merged, "Sanity: merge has theirs"

    # apply_theirs must replace with second parent's version
    assert apply_theirs_resolution(["file1.py"]) is True
    assert target.read_text() == theirs_content


def test_apply_theirs_resolution_fails_on_non_merge_commit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Returns False when HEAD is not a merge commit (no second parent)."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)
    setup_repo_with_submodule(repo_path)

    (repo_path / "file1.py").write_text("content\n")
    run_git(["add", "file1.py"], cwd=repo_path, check=True)
    run_git(["commit", "-m", "Add file"], cwd=repo_path, check=True)

    assert apply_theirs_resolution(["file1.py"]) is False


def test_merge_phase_3_precommit_fallback_applies_theirs_after_commit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """When precommit fails post-commit, fallback replaces with theirs and amends."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)
    setup_repo_with_submodule(repo_path)

    # File with enough separation for clean three-way merge
    initial_lines = [
        "HEADER = 'original'",
        "",
        "def setup():",
        "    pass",
        "",
        "",
        "",
        "",
        "",
        "",
        "def main():",
        "    pass",
        "",
    ]
    initial = "\n".join(initial_lines) + "\n"
    (repo_path / "module.py").write_text(initial)
    run_git(["add", "module.py"], cwd=repo_path, check=True)
    run_git(["commit", "-m", "Add module"], cwd=repo_path, check=True)

    runner = CliRunner()
    assert runner.invoke(worktree, ["new", "feat"]).exit_code == 0
    wt = repo_path / "wt" / "feat"

    # Worktree modifies bottom (theirs — "clean" version)
    theirs_lines = initial_lines.copy()
    theirs_lines[11] = "    print('theirs')"
    theirs = "\n".join(theirs_lines) + "\n"
    (wt / "module.py").write_text(theirs)
    run_git(["add", "module.py"], cwd=wt, check=True)
    run_git(["commit", "-m", "Fix main"], cwd=wt, check=True)

    # Parent modifies top (ours — will "fail" precommit)
    ours_lines = initial_lines.copy()
    ours_lines[0] = "HEADER = 'ours_dirty'"
    (repo_path / "module.py").write_text("\n".join(ours_lines) + "\n")
    run_git(["add", "module.py"], cwd=repo_path, check=True)
    run_git(["commit", "-m", "Dirty header"], cwd=repo_path, check=True)

    # Mock precommit: fail first (reports module.py), pass second
    original_run = subprocess.run
    precommit_calls: list[int] = []

    def mock_run(
        args: list[str], **kwargs: object
    ) -> subprocess.CompletedProcess[str]:
        if args == ["just", "precommit"]:
            precommit_calls.append(1)
            if len(precommit_calls) == 1:
                return subprocess.CompletedProcess(
                    args, 1, stdout="", stderr="module.py: FAILED"
                )
            return subprocess.CompletedProcess(
                args, 0, stdout="", stderr=""
            )
        return original_run(args, **kwargs)  # type: ignore[call-overload, no-any-return]

    monkeypatch.setattr(subprocess, "run", mock_run)

    result = runner.invoke(worktree, ["merge", "feat"])

    assert result.exit_code == 0, (
        f"Expected success via theirs fallback: {result.output}"
    )

    # File should have theirs content (not merged ours+theirs)
    assert (repo_path / "module.py").read_text() == theirs

    # Merge commit should contain theirs content
    committed = run_git(
        ["show", "HEAD:module.py"], cwd=repo_path, check=True
    ).stdout
    assert committed == theirs


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
