"""Merge phase implementations for worktree merge command."""

import subprocess
from pathlib import Path

import click

from claudeutils.worktree.git_utils import check_clean_tree, run_git
from claudeutils.worktree.merge_helpers import (
    apply_theirs_resolution,
    capture_untracked_files,
    parse_precommit_failures,
    resolve_conflicts,
)


def merge_phase_1_prechecks(slug: str) -> tuple[bool, Path]:
    """Phase 1: Pre-checks (clean tree, branch, worktree)."""
    merge_in_progress = (
        run_git(["rev-parse", "--verify", "MERGE_HEAD"], check=False).returncode == 0
    )

    if not merge_in_progress:
        check_clean_tree()

    if run_git(["rev-parse", "--verify", slug], check=False).returncode != 0:
        click.echo(f"Error: branch {slug} not found", err=True)
        raise SystemExit(1)

    worktree_path = Path(f"wt/{slug}")
    if not worktree_path.exists():
        click.echo(f"Warning: worktree directory {worktree_path} not found", err=True)

    return merge_in_progress, worktree_path


def submodule_merge_and_verify(wt_commit: str, local_commit: str, slug: str) -> None:
    """Merge submodule commits and verify ancestry."""
    run_git(["add", "agent-core"])

    if run_git(["diff", "--quiet", "--cached"], check=False).returncode != 0:
        run_git(["commit", "-m", f"🔀 Merge agent-core from {slug}"], check=False)

    final_head = run_git(["-C", "agent-core", "rev-parse", "HEAD"]).stdout.strip()

    wt_ok = (
        run_git(
            ["-C", "agent-core", "merge-base", "--is-ancestor", wt_commit, final_head],
            check=False,
        ).returncode
        == 0
    )
    local_ok = (
        run_git(
            [
                "-C",
                "agent-core",
                "merge-base",
                "--is-ancestor",
                local_commit,
                final_head,
            ],
            check=False,
        ).returncode
        == 0
    )

    if not wt_ok or not local_ok:
        click.echo("Error: merge verification failed", err=True)
        if not wt_ok:
            click.echo(
                f"  Worktree {wt_commit[:7]} not ancestor of {final_head[:7]}",
                err=True,
            )
        if not local_ok:
            click.echo(
                f"  Local {local_commit[:7]} not ancestor of {final_head[:7]}",
                err=True,
            )
        raise SystemExit(2)

    click.echo(
        f"Submodule agent-core: merged ({wt_commit[:7]} + {local_commit[:7]})",
        err=True,
    )


def merge_phase_2_submodule(slug: str, worktree_path: Path) -> None:
    """Phase 2: Submodule resolution with no-divergence optimization."""
    result = run_git(["ls-tree", slug, "--", "agent-core"], check=False)
    if result.returncode != 0 or not result.stdout.strip():
        return

    parts = result.stdout.strip().split()
    if len(parts) < 3 or parts[0] != "160000":
        return

    wt_commit = parts[2]
    result = run_git(["-C", "agent-core", "rev-parse", "HEAD"], check=False)
    if result.returncode != 0:
        return

    local_commit = result.stdout.strip()

    if wt_commit == local_commit:
        click.echo(
            f"Submodule agent-core: skipped (no divergence, {wt_commit[:7]})", err=True
        )
        return

    ancestry_check = run_git(
        ["-C", "agent-core", "merge-base", "--is-ancestor", wt_commit, local_commit],
        check=False,
    )
    if ancestry_check.returncode == 0:
        wt_short, local_short = wt_commit[:7], local_commit[:7]
        msg = f"Submodule agent-core: skipped (fast-forward, {wt_short} is ancestor of {local_short})"  # noqa: E501
        click.echo(msg, err=True)
        return

    worktree_ac_path = worktree_path / "agent-core"
    if not worktree_ac_path.exists():
        msg = f"Error: worktree submodule not found at {worktree_ac_path}"
        click.echo(msg, err=True)
        raise SystemExit(1)

    fetch_result = run_git(
        [
            "-c",
            "protocol.file.allow=always",
            "-C",
            "agent-core",
            "fetch",
            str(worktree_ac_path),
            "HEAD",
        ],
        check=False,
    )
    if fetch_result.returncode != 0:
        click.echo("Error: failed to fetch from worktree submodule", err=True)
        raise SystemExit(1)

    merge_result = run_git(
        ["-C", "agent-core", "merge", "--no-edit", wt_commit], check=False
    )
    if merge_result.returncode != 0:
        click.echo("Error: submodule merge conflict in agent-core", err=True)
        click.echo(merge_result.stderr, err=True)
        raise SystemExit(1)

    submodule_merge_and_verify(wt_commit, local_commit, slug)


def clean_merge_debris(incoming: set[str]) -> None:
    """Remove untracked files that would conflict with incoming merge."""
    untracked = capture_untracked_files()
    debris = untracked & incoming
    for filepath in debris:
        if Path(filepath).exists():
            Path(filepath).unlink()


def merge_phase_3_parent(slug: str) -> None:
    """Phase 3: Parent merge with conflict resolution."""
    merge_in_progress = (
        run_git(["rev-parse", "--verify", "MERGE_HEAD"], check=False).returncode == 0
    )

    if merge_in_progress:
        merge_returncode = 0
    else:
        diff_result = run_git(["diff", "--name-only", "HEAD", slug], check=False)
        incoming = (
            {f for f in diff_result.stdout.strip().split("\n") if f}
            if diff_result.returncode == 0
            else set()
        )

        clean_merge_debris(incoming)
        untracked_before = capture_untracked_files()

        merge_result = run_git(["merge", "--no-commit", "--no-ff", slug], check=False)
        merge_returncode = merge_result.returncode

        if merge_returncode != 0:
            untracked_after = capture_untracked_files()
            materialized = untracked_after - untracked_before
            for filepath in materialized:
                if Path(filepath).exists():
                    Path(filepath).unlink()

    if merge_returncode == 0:
        pass
    elif merge_returncode == 1:
        conflict_result = run_git(["diff", "--name-only", "--diff-filter=U"])
        conflict_files = (
            conflict_result.stdout.strip().split("\n")
            if conflict_result.stdout.strip()
            else []
        )

        if conflict_files and not resolve_conflicts(conflict_files, slug):
            click.echo("Merge conflicts detected:", err=True)
            for f in conflict_files:
                click.echo(f"  {f}", err=True)
            raise SystemExit(1)
    else:
        click.echo(f"Error: merge failed with exit code {merge_returncode}", err=True)
        raise SystemExit(2)


def merge_phase_3_commit_and_precommit(slug: str, message: str) -> None:
    """Create merge commit and validate with precommit."""
    commit_message = f"🔀 {message}" if message else f"🔀 Merge wt/{slug}"

    commit_result = run_git(["commit", "-m", commit_message], check=False)
    if commit_result.returncode != 0:
        click.echo("Error: failed to create merge commit", err=True)
        click.echo(commit_result.stderr, err=True)
        raise SystemExit(1)

    merge_commit = run_git(["rev-parse", "HEAD"]).stdout.strip()

    precommit_result = subprocess.run(
        ["just", "precommit"], capture_output=True, text=True, check=False
    )

    if precommit_result.returncode != 0:
        stderr_output = precommit_result.stderr + precommit_result.stdout
        failed_files = parse_precommit_failures(stderr_output)

        if not failed_files:
            click.echo(
                "Precommit failed with unparseable output. Manual resolution required.",
                err=True,
            )
            click.echo(
                "Run 'git reset HEAD~1' to undo the merge commit.",
                err=True,
            )
            run_git(["reset", "HEAD~1"], check=False)
            raise SystemExit(1)

        if not apply_theirs_resolution(failed_files):
            click.echo(
                "Source conflict resolution failed. Manual resolution required for:",
                err=True,
            )
            for filepath in failed_files:
                click.echo(f"  {filepath}", err=True)
            click.echo(
                "Run 'git reset HEAD~1' to undo the merge commit.",
                err=True,
            )
            run_git(["reset", "HEAD~1"], check=False)
            raise SystemExit(1)

        run_git(["commit", "--amend", "--no-edit"], check=False)

        precommit_retry = subprocess.run(
            ["just", "precommit"], capture_output=True, text=True, check=False
        )
        if precommit_retry.returncode != 0:
            click.echo(
                "Source conflict resolution failed. Manual resolution required for:",
                err=True,
            )
            for filepath in failed_files:
                click.echo(f"  {filepath}", err=True)
            click.echo(
                "Run 'git reset HEAD~1' to undo the merge commit.",
                err=True,
            )
            run_git(["reset", "HEAD~1"], check=False)
            raise SystemExit(1)

    click.echo(merge_commit)
