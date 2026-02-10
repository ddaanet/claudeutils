"""Worktree subcommand implementations."""

import os
import re
import subprocess
import tempfile
from pathlib import Path

import click

from claudeutils.worktree.conflicts import (
    resolve_jobs_conflict,
    resolve_learnings_conflict,
    resolve_session_conflict,
)


def run_git(
    args: list[str],
    *,
    check: bool = True,
    env: dict[str, str] | None = None,
    stdin_input: str | None = None,
) -> subprocess.CompletedProcess[str]:
    """Run git command with common defaults."""
    return subprocess.run(
        ["git", *args],
        capture_output=True,
        text=True,
        check=check,
        env=env,
        input=stdin_input,
    )


def get_dirty_files() -> str:
    """Return porcelain-format dirty files, excluding session context files."""
    parent_status = run_git(["status", "--porcelain"]).stdout
    result = run_git(["-C", "agent-core", "status", "--porcelain"], check=False)
    submodule_status = result.stdout if result.returncode == 0 else ""
    combined = parent_status + submodule_status

    exempt_filenames = {"session.md", "jobs.md", "learnings.md"}
    filtered_lines = []
    for line in combined.rstrip().split("\n"):
        if not line:
            continue
        tokens = line.split()
        if len(tokens) >= 2:
            filepath = tokens[-1]
            filename = Path(filepath).name
            if filename in exempt_filenames and filepath.startswith("agents/"):
                continue
        filtered_lines.append(line)
    return "\n".join(filtered_lines)


def check_clean_tree() -> None:
    """Validate clean tree, exempting session context files. Exits 1 if dirty."""
    dirty_files = get_dirty_files()
    if dirty_files:
        click.echo(
            "Error: uncommitted changes prevent merge (session files exempt):",
            err=True,
        )
        click.echo(dirty_files, err=True)
        raise SystemExit(1)


def create_session_commit(slug: str, base: str, session: str) -> str:
    """Pre-commit session.md via isolated temp index."""
    session_path = Path(session)
    try:
        session_content = session_path.read_text()
    except (FileNotFoundError, PermissionError) as e:
        click.echo(f"Error reading session file {session}: {e}", err=True)
        raise SystemExit(1) from e

    with tempfile.NamedTemporaryFile(delete=False, suffix=".index") as tmp_index:
        tmp_index_path = tmp_index.name

    try:
        env = {**os.environ, "GIT_INDEX_FILE": tmp_index_path}

        blob_hash = run_git(
            ["hash-object", "-w", "--stdin"], stdin_input=session_content
        ).stdout.strip()
        base_tree = run_git(["rev-parse", f"{base}^{{tree}}"]).stdout.strip()

        run_git(["read-tree", base_tree], env=env)
        run_git(
            [
                "update-index",
                "--add",
                "--cacheinfo",
                f"100644,{blob_hash},agents/session.md",
            ],
            env=env,
        )

        new_tree = run_git(["write-tree"], env=env).stdout.strip()
        return run_git(
            ["commit-tree", new_tree, "-p", base, "-m", f"Focused session for {slug}"]
        ).stdout.strip()
    finally:
        Path(tmp_index_path).unlink()


def cmd_ls() -> None:
    """List active worktrees."""
    main_path = run_git(["rev-parse", "--show-toplevel"]).stdout.strip()
    result = run_git(["worktree", "list", "--porcelain"])
    lines = result.stdout.strip().split("\n") if result.stdout.strip() else []

    entries = []
    i = 0
    while i < len(lines):
        if lines[i].startswith("worktree "):
            path = lines[i].split(maxsplit=1)[1]
            i += 1

            branch = ""
            while i < len(lines) and lines[i]:
                if lines[i].startswith("branch "):
                    branch = lines[i].split(maxsplit=1)[1]
                i += 1

            i += 1

            if path != main_path:
                slug = Path(path).name
                entries.append((slug, branch, path))
        else:
            i += 1

    for slug, branch, path in entries:
        click.echo(f"{slug}\t{branch}\t{path}")


def cmd_clean_tree() -> None:
    """Validate clean tree, excluding session files. Exit 0 if clean, 1 if dirty."""
    dirty_files = get_dirty_files()
    if dirty_files:
        click.echo(dirty_files)
        raise SystemExit(1)


def cmd_new(slug: str, base: str, session: str) -> None:
    """Create worktree with optional pre-committed session."""
    worktree_path = Path(f"wt/{slug}")

    if worktree_path.exists():
        click.echo(f"Error: existing directory {worktree_path}", err=True)
        raise SystemExit(1)

    if run_git(["rev-parse", "--verify", slug], check=False).returncode == 0:
        click.echo(f"Error: existing branch {slug}", err=True)
        raise SystemExit(1)

    try:
        if session:
            branch_commit = create_session_commit(slug, base, session)
            run_git(["branch", slug, branch_commit])
            run_git(["worktree", "add", str(worktree_path), slug])
        else:
            run_git(["worktree", "add", str(worktree_path), "-b", slug, base])

        project_root = run_git(["rev-parse", "--show-toplevel"]).stdout.strip()
        agent_core_local = Path(project_root) / "agent-core"

        if agent_core_local.exists() and (agent_core_local / ".git").exists():
            run_git(
                [
                    "-C",
                    str(worktree_path),
                    "submodule",
                    "update",
                    "--init",
                    "--reference",
                    str(agent_core_local),
                ],
                check=False,
            )

            submodule_path = worktree_path / "agent-core"
            if submodule_path.exists():
                result = run_git(
                    ["-C", str(submodule_path), "checkout", "-B", slug], check=False
                )
                if result.returncode != 0:
                    click.echo(result.stderr, err=True)
                    raise SystemExit(1)

        click.echo(str(worktree_path))
    except subprocess.CalledProcessError as e:
        click.echo(f"Error creating worktree: {e.stderr}", err=True)
        raise SystemExit(1) from e


def resolve_conflicts(conflict_files: list[str], slug: str) -> bool:
    """Resolve conflicts in session context files. Returns True if all resolved."""
    conflict_resolver_map = {
        "agents/session.md": lambda ours, theirs: resolve_session_conflict(
            ours, theirs, slug=slug
        ),
        "agents/learnings.md": resolve_learnings_conflict,
        "agents/jobs.md": resolve_jobs_conflict,
    }

    for filepath in conflict_files:
        resolver = conflict_resolver_map.get(filepath)
        if not resolver:
            return False

        ours_content = run_git(["show", f":2:{filepath}"]).stdout
        theirs_content = run_git(["show", f":3:{filepath}"]).stdout

        resolved = resolver(ours_content, theirs_content)
        Path(filepath).write_text(resolved)
        run_git(["add", filepath])

    return True


def cmd_add_commit(files: tuple[str, ...]) -> None:
    """Stage files and commit (idempotent). Reads message from stdin if staged."""
    run_git(["add", *list(files)])
    has_staged = run_git(["diff", "--quiet", "--cached"], check=False).returncode == 1

    if has_staged:
        message = click.get_text_stream("stdin").read()
        result = run_git(["commit", "-m", message])
        click.echo(result.stdout.strip())


def cmd_rm(slug: str) -> None:
    """Remove worktree and branch (forced). Handles branch-only cleanup."""
    worktree_path = Path(f"wt/{slug}")

    if worktree_path.exists():
        result = run_git(
            ["-C", str(worktree_path), "status", "--porcelain"], check=False
        )
        if result.stdout.strip():
            click.echo(f"Warning: {slug} has uncommitted changes")

        run_git(["worktree", "remove", "--force", str(worktree_path)])
    else:
        run_git(["worktree", "prune"])

    result = run_git(["branch", "-D", slug], check=False)
    if result.returncode != 0 and "not found" not in result.stderr.lower():
        click.echo(result.stderr)

    click.echo(f"Removed worktree {slug}")


def capture_untracked_files() -> set[str]:
    """Capture current untracked files."""
    result = run_git(["status", "--porcelain"])
    untracked = set()
    for line in result.stdout.strip().split("\n"):
        if line.startswith("??"):
            tokens = line.split()
            if len(tokens) >= 2:
                untracked.add(tokens[-1])
    return untracked


def parse_precommit_failures(stderr_output: str) -> list[str]:
    """Parse precommit stderr to extract failed file paths."""
    failed_files = []
    patterns = [
        r"^([^:]+):\s+FAILED",
        r"^([^:]+):\s+Error",
        r"^([^:]+)\s+\(.*\)\s+failed",
    ]

    for line in stderr_output.split("\n"):
        if not line.strip():
            continue
        for pattern in patterns:
            match = re.match(pattern, line)
            if match:
                filepath = match.group(1)
                if filepath and filepath not in failed_files:
                    failed_files.append(filepath)
                break

    return failed_files


def apply_theirs_resolution(failed_files: list[str]) -> bool:
    """Apply theirs resolution to failed files. Returns True if all resolved."""
    for filepath in failed_files:
        if run_git(["checkout", "--theirs", filepath], check=False).returncode != 0:
            return False
        if run_git(["add", filepath], check=False).returncode != 0:
            return False
    return True


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


def submodule_merge_and_verify(
    wt_commit: str, local_commit: str, slug: str
) -> None:
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
        ["-C", "agent-core", "fetch", str(worktree_ac_path), "HEAD"], check=False
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
            run_git(["merge", "--abort"], check=False)
            raise SystemExit(1)

        if not apply_theirs_resolution(failed_files):
            run_git(["merge", "--abort"], check=False)
            click.echo(
                "Source conflict resolution failed. Manual resolution required for:",
                err=True,
            )
            for filepath in failed_files:
                click.echo(f"  {filepath}", err=True)
            raise SystemExit(1)

        precommit_retry = subprocess.run(
            ["just", "precommit"], capture_output=True, text=True, check=False
        )
        if precommit_retry.returncode != 0:
            run_git(["merge", "--abort"], check=False)
            click.echo(
                "Source conflict resolution failed. Manual resolution required for:",
                err=True,
            )
            for filepath in failed_files:
                click.echo(f"  {filepath}", err=True)
            raise SystemExit(1)

    click.echo(merge_commit)


def cmd_merge(slug: str, message: str = "") -> None:
    """Merge worktree branch.

    Phase 1: clean tree, branch, worktree directory checks.
    Phase 2: submodule resolution with no-divergence optimization.
    Phase 3: parent merge with conflict resolution and precommit gate.
    """
    merge_in_progress, worktree_path = merge_phase_1_prechecks(slug)

    if not merge_in_progress:
        merge_phase_2_submodule(slug, worktree_path)

    merge_phase_3_parent(slug)
    merge_phase_3_commit_and_precommit(slug, message)
