"""Worktree subcommand implementations."""

import os
import subprocess
import tempfile
from pathlib import Path

import click

from claudeutils.worktree.conflicts import (
    resolve_jobs_conflict,
    resolve_learnings_conflict,
    resolve_session_conflict,
)


def get_dirty_files() -> str:
    """Return porcelain-format dirty files, excluding session context files."""
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True,
        text=True,
        check=True,
    )
    parent_status = result.stdout

    # Graceful degradation: if agent-core doesn't exist, treat as clean
    result = subprocess.run(
        ["git", "-C", "agent-core", "status", "--porcelain"],
        capture_output=True,
        text=True,
        check=False,
    )
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
    """Validate clean tree, exempting session context files.

    Exits 1 if dirty.
    """
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

        result = subprocess.run(
            ["git", "hash-object", "-w", "--stdin"],
            input=session_content,
            capture_output=True,
            text=True,
            check=True,
        )
        blob_hash = result.stdout.strip()

        result = subprocess.run(
            ["git", "rev-parse", f"{base}^{{tree}}"],
            capture_output=True,
            text=True,
            check=True,
        )
        base_tree = result.stdout.strip()

        subprocess.run(
            ["git", "read-tree", base_tree],
            env=env,
            check=True,
            capture_output=True,
        )

        subprocess.run(
            [
                "git",
                "update-index",
                "--add",
                "--cacheinfo",
                f"100644,{blob_hash},agents/session.md",
            ],
            env=env,
            check=True,
            capture_output=True,
        )

        result = subprocess.run(
            ["git", "write-tree"],
            env=env,
            capture_output=True,
            text=True,
            check=True,
        )
        new_tree = result.stdout.strip()

        result = subprocess.run(
            [
                "git",
                "commit-tree",
                new_tree,
                "-p",
                base,
                "-m",
                f"Focused session for {slug}",
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    finally:
        Path(tmp_index_path).unlink()


def cmd_ls() -> None:
    """List active worktrees."""
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        check=True,
    )
    main_path = result.stdout.strip()

    result = subprocess.run(
        ["git", "worktree", "list", "--porcelain"],
        capture_output=True,
        text=True,
        check=True,
    )
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
    """Validate clean tree, excluding session files.

    Exit 0 if clean, 1 if dirty.
    """
    dirty_files = get_dirty_files()
    if dirty_files:
        click.echo(dirty_files)
        raise SystemExit(1)


def cmd_new(slug: str, base: str, session: str) -> None:
    """Create worktree with optional pre-committed session."""
    worktree_path = Path(f"wt/{slug}")

    # Check for directory collision
    if worktree_path.exists():
        click.echo(f"Error: existing directory {worktree_path}", err=True)
        raise SystemExit(1)

    # Check for branch collision
    result = subprocess.run(
        ["git", "rev-parse", "--verify", slug],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        click.echo(f"Error: existing branch {slug}", err=True)
        raise SystemExit(1)

    try:
        if session:
            branch_commit = create_session_commit(slug, base, session)
            subprocess.run(
                ["git", "branch", slug, branch_commit],
                check=True,
                capture_output=True,
            )
            subprocess.run(
                ["git", "worktree", "add", str(worktree_path), slug],
                check=True,
                capture_output=True,
            )
        else:
            subprocess.run(
                ["git", "worktree", "add", str(worktree_path), "-b", slug, base],
                check=True,
                capture_output=True,
            )

        # Initialize submodules in the new worktree
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True,
        )
        project_root = result.stdout.strip()

        # Get the agent-core path (if submodule exists in parent)
        agent_core_local = Path(project_root) / "agent-core"
        if agent_core_local.exists() and (agent_core_local / ".git").exists():
            # Use git submodule update with --reference to use local objects
            # This avoids fetching from remote
            subprocess.run(
                [
                    "git",
                    "-C",
                    str(worktree_path),
                    "submodule",
                    "update",
                    "--init",
                    "--reference",
                    str(agent_core_local),
                ],
                check=False,
                capture_output=True,
            )

            # Create and checkout branch in submodule matching the worktree slug
            submodule_path = worktree_path / "agent-core"
            if submodule_path.exists():
                result = subprocess.run(
                    ["git", "-C", str(submodule_path), "checkout", "-B", slug],
                    check=False,
                    capture_output=True,
                    text=True,
                )
                if result.returncode != 0:
                    click.echo(result.stderr, err=True)
                    raise SystemExit(1)

        click.echo(str(worktree_path))
    except subprocess.CalledProcessError as e:
        click.echo(f"Error creating worktree: {e.stderr}", err=True)
        raise SystemExit(1) from e


def resolve_conflicts(conflict_files: list[str], slug: str) -> bool:
    """Resolve conflicts in session context files.

    Args:
        conflict_files: List of conflicted file paths
        slug: Worktree slug (used for session conflict resolution)

    Returns:
        True if all conflicts resolved, False if any remain
    """
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
            # Not a known conflict type - exit for manual resolution
            return False

        # Extract conflict sides via git show
        result_ours = subprocess.run(
            ["git", "show", f":2:{filepath}"],
            capture_output=True,
            text=True,
            check=True,
        )
        ours_content = result_ours.stdout

        result_theirs = subprocess.run(
            ["git", "show", f":3:{filepath}"],
            capture_output=True,
            text=True,
            check=True,
        )
        theirs_content = result_theirs.stdout

        # Resolve conflict
        resolved = resolver(ours_content, theirs_content)

        # Write result to working tree
        Path(filepath).write_text(resolved)

        # Stage the resolved file
        subprocess.run(
            ["git", "add", filepath],
            check=True,
            capture_output=True,
        )

    return True


def cmd_add_commit(files: tuple[str, ...]) -> None:
    """Stage files and commit (idempotent).

    Reads message from stdin if staged.
    """
    subprocess.run(
        ["git", "add", *list(files)],
        check=True,
    )

    result = subprocess.run(
        ["git", "diff", "--quiet", "--cached"],
        check=False,
    )
    has_staged = result.returncode == 1

    if has_staged:
        message = click.get_text_stream("stdin").read()
        result = subprocess.run(
            ["git", "commit", "-m", message],
            capture_output=True,
            text=True,
            check=True,
        )
        click.echo(result.stdout.strip())


def cmd_rm(slug: str) -> None:
    """Remove worktree and branch (forced).

    Handles branch-only cleanup (idempotent).
    """
    worktree_path = Path(f"wt/{slug}")

    if worktree_path.exists():
        result = subprocess.run(
            ["git", "-C", str(worktree_path), "status", "--porcelain"],
            check=False,
            capture_output=True,
            text=True,
        )
        has_uncommitted = bool(result.stdout.strip())
        if has_uncommitted:
            click.echo(f"Warning: {slug} has uncommitted changes")

        subprocess.run(
            ["git", "worktree", "remove", "--force", str(worktree_path)],
            check=True,
            capture_output=True,
        )
    else:
        # Worktree directory doesn't exist; prune stale registration
        subprocess.run(
            ["git", "worktree", "prune"],
            check=True,
            capture_output=True,
        )

    result = subprocess.run(
        ["git", "branch", "-D", slug],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0 and "not found" not in result.stderr.lower():
        click.echo(result.stderr)

    click.echo(f"Removed worktree {slug}")


def capture_untracked_files() -> set[str]:
    """Capture current untracked files."""
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True,
        text=True,
        check=True,
    )
    untracked = set()
    for line in result.stdout.strip().split("\n"):
        if line.startswith("??"):
            tokens = line.split()
            if len(tokens) >= 2:
                untracked.add(tokens[-1])
    return untracked


def cmd_merge(slug: str, message: str = "") -> None:
    """Merge worktree branch.

    Phase 1: clean tree, branch, worktree directory checks.
    Phase 2: submodule resolution with no-divergence optimization.
    Phase 3: parent merge with conflict resolution and precommit gate.
    """
    # Phase 1: Pre-checks
    # Check if merge is already in progress (idempotent resume)
    merge_in_progress = (
        subprocess.run(
            ["git", "rev-parse", "--verify", "MERGE_HEAD"],
            check=False,
            capture_output=True,
        ).returncode
        == 0
    )

    # If merge not in progress, require clean tree
    if not merge_in_progress:
        check_clean_tree()

    # Validate branch exists
    result = subprocess.run(
        ["git", "rev-parse", "--verify", slug],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        click.echo(f"Error: branch {slug} not found", err=True)
        raise SystemExit(1)

    # Warn if worktree directory missing but continue
    worktree_path = Path(f"wt/{slug}")
    if not worktree_path.exists():
        click.echo(f"Warning: worktree directory {worktree_path} not found", err=True)

    # Phase 2: Submodule resolution with no-divergence optimization
    # Extract worktree submodule commit pointer using git ls-tree
    result = subprocess.run(
        ["git", "ls-tree", slug, "--", "agent-core"],
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode == 0 and result.stdout.strip():
        # Parse "160000 commit <sha>    agent-core"
        parts = result.stdout.strip().split()
        if len(parts) >= 3 and parts[0] == "160000":
            wt_submodule_commit = parts[2]

            # Extract local submodule commit using git -C agent-core rev-parse HEAD
            result = subprocess.run(
                ["git", "-C", "agent-core", "rev-parse", "HEAD"],
                capture_output=True,
                text=True,
                check=False,
            )

            if result.returncode == 0:
                local_submodule_commit = result.stdout.strip()

                # Compare commits - if equal, skip to Phase 3
                if wt_submodule_commit == local_submodule_commit:
                    short_sha = wt_submodule_commit[:7]
                    msg = f"Submodule agent-core: skipped (no divergence, {short_sha})"
                    click.echo(msg, err=True)
                else:
                    # Ancestry check: skip merge if worktree is ancestor of local
                    ancestry_result = subprocess.run(
                        [
                            "git",
                            "-C",
                            "agent-core",
                            "merge-base",
                            "--is-ancestor",
                            wt_submodule_commit,
                            local_submodule_commit,
                        ],
                        check=False,
                        capture_output=True,
                    )

                    if ancestry_result.returncode == 0:
                        # Worktree commit is ancestor - local already includes changes
                        wt_short = wt_submodule_commit[:7]
                        local_short = local_submodule_commit[:7]
                        msg = (
                            f"Submodule agent-core: skipped (fast-forward, "
                            f"{wt_short} is ancestor of {local_short})"
                        )
                        click.echo(msg, err=True)
                    else:
                        # Diverged commits: fetch from worktree, merge, stage, commit
                        worktree_ac_path = worktree_path / "agent-core"
                        if worktree_ac_path.exists():
                            # Fetch from worktree's submodule
                            fetch_result = subprocess.run(
                                [
                                    "git",
                                    "-C",
                                    "agent-core",
                                    "fetch",
                                    str(worktree_ac_path),
                                    "HEAD",
                                ],
                                capture_output=True,
                                text=True,
                                check=False,
                            )
                            if fetch_result.returncode == 0:
                                # Merge the fetched commit
                                merge_result = subprocess.run(
                                    [
                                        "git",
                                        "-C",
                                        "agent-core",
                                        "merge",
                                        "--no-edit",
                                        wt_submodule_commit,
                                    ],
                                    capture_output=True,
                                    text=True,
                                    check=False,
                                )
                                if merge_result.returncode == 0:
                                    # Stage the merged submodule pointer
                                    subprocess.run(
                                        ["git", "add", "agent-core"],
                                        capture_output=True,
                                        text=True,
                                        check=True,
                                    )
                                    # Create merge commit if staged (idempotent)
                                    # Guard: git diff --quiet --cached
                                    diff_result = subprocess.run(
                                        ["git", "diff", "--quiet", "--cached"],
                                        capture_output=True,
                                        check=False,
                                    )
                                    # If diff returned non-zero (changes staged), commit
                                    if diff_result.returncode != 0:
                                        result = subprocess.run(
                                            [
                                                "git",
                                                "commit",
                                                "-m",
                                                f"🔀 Merge agent-core from {slug}",
                                            ],
                                            capture_output=True,
                                            text=True,
                                            check=False,
                                        )
                                    else:
                                        result = subprocess.run(
                                            ["git", "rev-parse", "HEAD"],
                                            capture_output=True,
                                            check=False,
                                        )

                                    if result.returncode == 0:
                                        wt_short = wt_submodule_commit[:7]
                                        local_short = local_submodule_commit[:7]
                                        msg = (
                                            f"Submodule agent-core: merged "
                                            f"({wt_short} + {local_short})"
                                        )
                                        click.echo(msg, err=True)

                                        # Verify both original commits are ancestors
                                        final_head_result = subprocess.run(
                                            [
                                                "git",
                                                "-C",
                                                "agent-core",
                                                "rev-parse",
                                                "HEAD",
                                            ],
                                            capture_output=True,
                                            text=True,
                                            check=False,
                                        )
                                        if final_head_result.returncode == 0:
                                            final_head = (
                                                final_head_result.stdout.strip()
                                            )

                                            # Verify worktree commit is ancestor
                                            wt_ancestor_result = subprocess.run(
                                                [
                                                    "git",
                                                    "-C",
                                                    "agent-core",
                                                    "merge-base",
                                                    "--is-ancestor",
                                                    wt_submodule_commit,
                                                    final_head,
                                                ],
                                                check=False,
                                                capture_output=True,
                                            )

                                            # Verify local commit is ancestor
                                            local_ancestor_result = subprocess.run(
                                                [
                                                    "git",
                                                    "-C",
                                                    "agent-core",
                                                    "merge-base",
                                                    "--is-ancestor",
                                                    local_submodule_commit,
                                                    final_head,
                                                ],
                                                check=False,
                                                capture_output=True,
                                            )

                                            if (
                                                wt_ancestor_result.returncode != 0
                                                or local_ancestor_result.returncode != 0
                                            ):
                                                click.echo(
                                                    "Error: merge verification failed",
                                                    err=True,
                                                )
                                                if wt_ancestor_result.returncode != 0:
                                                    wt_msg = (
                                                        f"  Worktree {wt_short} not "
                                                        f"ancestor of {final_head[:7]}"
                                                    )
                                                    click.echo(wt_msg, err=True)
                                                if (
                                                    local_ancestor_result.returncode
                                                    != 0
                                                ):
                                                    local_msg = (
                                                        f"  Local {local_short} not "
                                                        f"ancestor of {final_head[:7]}"
                                                    )
                                                    click.echo(local_msg, err=True)
                                                raise SystemExit(2)
                                else:
                                    click.echo(
                                        "Error: submodule merge conflict in agent-core",
                                        err=True,
                                    )
                                    click.echo(merge_result.stderr, err=True)
                                    raise SystemExit(1)
                            else:
                                click.echo(
                                    "Error: failed to fetch from worktree submodule",
                                    err=True,
                                )
                                click.echo(fetch_result.stderr, err=True)
                                raise SystemExit(1)
                        else:
                            msg = (
                                f"Error: worktree submodule not found "
                                f"at {worktree_ac_path}"
                            )
                            click.echo(msg, err=True)
                            raise SystemExit(1)

    # Phase 3: Parent merge
    # Check if merge is already in progress (MERGE_HEAD exists)
    # If so, skip git merge and proceed directly to conflict checking
    merge_in_progress_phase3 = (
        subprocess.run(
            ["git", "rev-parse", "--verify", "MERGE_HEAD"],
            check=False,
            capture_output=True,
        ).returncode
        == 0
    )

    if merge_in_progress_phase3:
        # Merge already in progress - skip git merge command
        merge_result_returncode = 0
        merge_result_stderr = ""
    else:
        # Before merge attempt, clean up debris from previous failed merge
        # Get files that differ between HEAD and the branch being merged
        diff_result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD", slug],
            capture_output=True,
            text=True,
            check=False,
        )
        incoming_files = (
            {f for f in diff_result.stdout.strip().split("\n") if f}
            if diff_result.returncode == 0
            else set()
        )

        # Remove any untracked files that would come from the merge
        # (these are debris from a previous failed attempt)
        untracked_now = capture_untracked_files()
        debris = untracked_now & incoming_files
        for filepath in debris:
            path_obj = Path(filepath)
            if path_obj.exists():
                path_obj.unlink()

        # Capture untracked files after cleanup
        untracked_before = capture_untracked_files()

        # Execute merge with --no-commit --no-ff
        merge_result = subprocess.run(
            ["git", "merge", "--no-commit", "--no-ff", slug],
            capture_output=True,
            text=True,
            check=False,
        )
        merge_result_returncode = merge_result.returncode
        merge_result_stderr = merge_result.stderr

        # If merge failed, capture new untracked files and clean them up
        # before exiting (so they don't cause issues on retry)
        if merge_result_returncode != 0:
            untracked_after = capture_untracked_files()
            materialized = untracked_after - untracked_before
            for filepath in materialized:
                path_obj = Path(filepath)
                if path_obj.exists():
                    path_obj.unlink()

    if merge_result_returncode == 0:
        # Clean merge - proceed to commit
        pass
    elif merge_result_returncode == 1:
        # Merge with conflicts
        # Check for unresolved conflicts
        conflict_result = subprocess.run(
            ["git", "diff", "--name-only", "--diff-filter=U"],
            capture_output=True,
            text=True,
            check=True,
        )
        conflict_files = (
            conflict_result.stdout.strip().split("\n")
            if conflict_result.stdout.strip()
            else []
        )

        if not conflict_files:
            # Merge actually succeeded (false positive for conflicts)
            pass
        # Attempt to resolve conflicts automatically
        elif resolve_conflicts(conflict_files, slug):
            # All conflicts resolved
            pass
        else:
            # Some conflicts cannot be auto-resolved
            # Report conflicts but leave merge in progress for manual resolution
            click.echo("Merge conflicts detected:", err=True)
            for f in conflict_files:
                click.echo(f"  {f}", err=True)
            raise SystemExit(1)
    else:
        click.echo(
            f"Error: merge failed with exit code {merge_result_returncode}", err=True
        )
        if merge_result_stderr:
            click.echo(merge_result_stderr, err=True)
        raise SystemExit(2)

    # Construct merge commit message
    commit_message = f"🔀 {message}" if message else f"🔀 Merge wt/{slug}"

    # Create merge commit
    commit_result = subprocess.run(
        ["git", "commit", "-m", commit_message],
        capture_output=True,
        text=True,
        check=False,
    )

    if commit_result.returncode != 0:
        click.echo("Error: failed to create merge commit", err=True)
        click.echo(commit_result.stderr, err=True)
        raise SystemExit(1)

    # Get merge commit hash
    hash_result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    )
    merge_commit = hash_result.stdout.strip()

    # Run precommit validation (mandatory correctness gate)
    precommit_result = subprocess.run(
        ["just", "precommit"],
        capture_output=True,
        text=True,
        check=False,
    )

    if precommit_result.returncode != 0:
        click.echo("Precommit validation failed:", err=True)
        click.echo(precommit_result.stdout, err=True)
        click.echo(precommit_result.stderr, err=True)
        raise SystemExit(1)

    # Output merge commit hash
    click.echo(merge_commit)
