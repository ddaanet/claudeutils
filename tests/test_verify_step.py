"""Tests for verify-step.sh script."""

import subprocess
from pathlib import Path

import pytest

SCRIPT = (
    Path(__file__).parent.parent
    / "agent-core"
    / "skills"
    / "orchestrate"
    / "scripts"
    / "verify-step.sh"
)


def _setup_git_repo(repo_path: Path) -> None:
    """Initialize a git repo with an initial commit."""
    subprocess.run(
        ["git", "init"],
        cwd=repo_path,
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=repo_path,
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=repo_path,
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "commit", "--allow-empty", "-m", "init"],
        cwd=repo_path,
        capture_output=True,
        check=True,
    )


def _create_justfile(repo_path: Path) -> None:
    """Create a minimal justfile with precommit recipe."""
    justfile = repo_path / "justfile"
    justfile.write_text("precommit:\n\t@echo 'ok'\n")
    subprocess.run(
        ["git", "add", "justfile"],
        cwd=repo_path,
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "add justfile"],
        cwd=repo_path,
        capture_output=True,
        check=True,
    )


def test_verify_step_clean_state(tmp_path: Path) -> None:
    """verify-step.sh exits with 0 and prints CLEAN on clean repo."""
    _setup_git_repo(tmp_path)
    _create_justfile(tmp_path)

    result = subprocess.run(
        [str(SCRIPT)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, (
        f"Expected exit 0, got {result.returncode}. "
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
    assert "CLEAN" in result.stdout or "CLEAN" in result.stderr, (
        f"Expected 'CLEAN' in output. stdout: {result.stdout}\nstderr: {result.stderr}"
    )


@pytest.mark.parametrize(
    "scenario",
    ["uncommitted", "untracked"],
)
def test_verify_step_dirty_states(tmp_path: Path, scenario: str) -> None:
    """verify-step.sh detects dirty states and non-zero exit."""
    if scenario == "uncommitted":
        _setup_git_repo(tmp_path)
        _create_justfile(tmp_path)

        test_file = tmp_path / "test.txt"
        test_file.write_text("uncommitted content")
        subprocess.run(
            ["git", "add", "test.txt"],
            cwd=tmp_path,
            capture_output=True,
            check=True,
        )

        result = subprocess.run(
            [str(SCRIPT)],
            cwd=tmp_path,
            capture_output=True,
            text=True,
            check=False,
        )

        assert result.returncode != 0, (
            f"Expected non-zero exit, got {result.returncode}. "
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        assert "DIRTY" in result.stdout or "DIRTY" in result.stderr, (
            f"Expected 'DIRTY' in output. "
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

    elif scenario == "untracked":
        _setup_git_repo(tmp_path)
        _create_justfile(tmp_path)

        test_file = tmp_path / "untracked.txt"
        test_file.write_text("untracked content")

        result = subprocess.run(
            [str(SCRIPT)],
            cwd=tmp_path,
            capture_output=True,
            text=True,
            check=False,
        )

        assert result.returncode != 0, (
            f"Expected non-zero exit, got {result.returncode}. "
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        assert "DIRTY" in result.stdout or "DIRTY" in result.stderr, (
            f"Expected 'DIRTY' in output. "
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
