"""Shared test helpers for worktree merge tests."""

import subprocess
from pathlib import Path


def run_git(
    args: list[str], *, cwd: Path | None = None, check: bool = False
) -> subprocess.CompletedProcess[str]:
    """Run git command with common defaults."""
    return subprocess.run(
        ["git", *args],
        check=check,
        cwd=cwd,
        capture_output=True,
        text=True,
    )


def init_repo(repo_path: Path) -> None:
    """Initialize a basic git repository."""
    run_git(["init"], cwd=repo_path, check=True)
    run_git(["config", "user.email", "test@example.com"], cwd=repo_path, check=True)
    run_git(["config", "user.name", "Test User"], cwd=repo_path, check=True)


def setup_repo_with_submodule(repo_path: Path) -> None:
    """Set up test repo with simulated submodule."""
    init_repo(repo_path)

    (repo_path / "README.md").write_text("test")
    run_git(["add", "README.md"], cwd=repo_path, check=True)
    run_git(["commit", "-m", "Initial commit"], cwd=repo_path, check=True)

    agent_core_path = repo_path / "agent-core"
    agent_core_path.mkdir()
    init_repo(agent_core_path)

    (agent_core_path / "core.txt").write_text("core content")
    run_git(["add", "core.txt"], cwd=agent_core_path, check=True)
    run_git(["commit", "-m", "Initial core commit"], cwd=agent_core_path, check=True)

    commit_hash = run_git(
        ["rev-parse", "HEAD"], cwd=agent_core_path, check=True
    ).stdout.strip()

    run_git(
        ["update-index", "--add", "--cacheinfo", f"160000,{commit_hash},agent-core"],
        cwd=repo_path,
        check=True,
    )

    # Use absolute path for submodule URL to work correctly from worktrees
    submodule_url = str(agent_core_path.absolute())
    (repo_path / ".gitmodules").write_text(
        f'[submodule "agent-core"]\n\tpath = agent-core\n\turl = {submodule_url}\n'
    )
    run_git(["add", ".gitmodules"], cwd=repo_path, check=True)
    run_git(["commit", "-m", "Add submodule"], cwd=repo_path, check=True)

    (repo_path / ".gitignore").write_text("wt/\n")
    run_git(["add", ".gitignore"], cwd=repo_path, check=True)
    run_git(["commit", "-m", "Add gitignore"], cwd=repo_path, check=True)

    (repo_path / "justfile").write_text("precommit:\n    exit 0\n")
    run_git(["add", "justfile"], cwd=repo_path, check=True)
    run_git(["commit", "-m", "Add minimal justfile"], cwd=repo_path, check=True)
