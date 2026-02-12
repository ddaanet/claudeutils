"""Worktree CLI module."""

import json
import os
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Any

import click


def wt_path(slug: str, create_container: bool = False) -> Path:  # noqa: FBT001,FBT002
    """Return absolute worktree path, optionally creating -wt container."""
    if not slug or not slug.strip():
        msg = "slug must not be empty or whitespace"
        raise ValueError(msg)

    current_path = Path.cwd()
    parent_name = current_path.parent.name

    container_path = (
        current_path.parent
        if parent_name.endswith("-wt")
        else current_path.parent / f"{current_path.name}-wt"
    )

    if create_container and not parent_name.endswith("-wt"):
        container_path.mkdir(parents=True, exist_ok=True)

    return container_path / slug


def derive_slug(task_name: str, max_length: int = 30) -> str:
    """Transform task name to slug: lowercase, hyphens, truncated to max_length."""
    if not task_name or not task_name.strip():
        msg = "task_name must not be empty"
        raise ValueError(msg)

    slug = re.sub(r"[^a-z0-9]+", "-", task_name.lower()).strip("-")[:max_length]
    return slug.rstrip("-")


def _is_relevant_entry(entry: str, task_name: str, plan_dir: str | None) -> bool:
    """Check if entry mentions task name or plan directory."""
    entry_lower = entry.lower()
    task_lower = task_name.lower()

    if task_lower in entry_lower:
        return True
    return bool(plan_dir and plan_dir.lower() in entry_lower)


def _filter_section(
    content: str, section_name: str, task_name: str, plan_dir: str | None
) -> str:
    """Extract and filter a section, returning section text or empty string."""
    pattern = rf"## {re.escape(section_name)}\n\n(.*?)(?=\n## |\Z)"
    match = re.search(pattern, content, re.DOTALL)
    if not match:
        return ""

    relevant_lines = []
    for line in match.group(1).split("\n"):
        if line.startswith("- "):
            if _is_relevant_entry(line[2:].strip(), task_name, plan_dir):
                relevant_lines.append(line)
        elif line.strip():
            relevant_lines.append(line)

    return (
        f"## {section_name}\n\n" + "\n".join(relevant_lines) + "\n"
        if relevant_lines
        else ""
    )


def focus_session(task_name: str, session_md_path: str | Path) -> str:
    """Extract task from session.md and generate focused session."""
    content = Path(session_md_path).read_text()
    pattern = rf"- \[ \] \*\*{re.escape(task_name)}\*\* (.+?)(?=\n-|\n## |\Z)"
    match = re.search(pattern, content, re.DOTALL)
    if not match:
        msg = f"Task '{task_name}' not found in session.md"
        raise ValueError(msg)

    metadata = match.group(1).rstrip()
    plan_dir = None
    if "plan:" in metadata:
        plan_match = re.search(r"plan:\s*(\S+)", metadata)
        if plan_match:
            plan_dir = plan_match.group(1)

    result = (
        f"# Session: Worktree — {task_name}\n\n"
        f"**Status:** Focused worktree for parallel execution.\n\n"
        f"## Pending Tasks\n\n- [ ] **{task_name}** {metadata}\n"
    )

    for section in ["Blockers / Gotchas", "Reference Files"]:
        filtered = _filter_section(content, section, task_name, plan_dir)
        if filtered:
            result += f"\n{filtered}"

    return result


def add_sandbox_dir(container: str, settings_path: str | Path) -> None:
    """Add container to permissions.additionalDirectories."""
    settings_path = Path(settings_path)
    if settings_path.exists():
        with settings_path.open() as f:
            settings: dict[str, Any] = json.load(f)
    else:
        settings_path.parent.mkdir(parents=True, exist_ok=True)
        settings = {"permissions": {"additionalDirectories": []}}

    dirs = settings.setdefault("permissions", {}).setdefault(
        "additionalDirectories", []
    )
    if container not in dirs:
        dirs.append(container)

    with settings_path.open("w") as f:
        json.dump(settings, f, indent=2, ensure_ascii=False)


@click.group(name="_worktree")
def worktree() -> None:
    """Manage git worktrees."""


@worktree.command()
def ls() -> None:
    """List active worktrees (excluding main)."""
    main_path = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()

    porcelain_output = subprocess.run(
        ["git", "worktree", "list", "--porcelain"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()

    lines = porcelain_output.split("\n") if porcelain_output else []
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
                entries.append((Path(path).name, branch, path))
        else:
            i += 1

    for slug, branch, path in entries:
        click.echo(f"{slug}\t{branch}\t{path}")


def _build_tree_with_session(content: str, base_tree: str, env: dict[str, str]) -> str:
    """Build git tree with session.md added."""
    blob = subprocess.run(
        ["git", "hash-object", "-w", "--stdin"],
        input=content,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    subprocess.run(
        ["git", "read-tree", base_tree], env=env, check=True, capture_output=True
    )
    subprocess.run(
        [
            "git",
            "update-index",
            "--add",
            "--cacheinfo",
            f"100644,{blob},agents/session.md",
        ],
        env=env,
        check=True,
        capture_output=True,
    )
    return subprocess.run(
        ["git", "write-tree"], env=env, capture_output=True, text=True, check=True
    ).stdout.strip()


def _create_session_commit(slug: str, base: str, session: str) -> str:
    """Pre-commit session.md, return commit hash."""
    try:
        content = Path(session).read_text()
    except (FileNotFoundError, PermissionError) as e:
        click.echo(f"Error reading session file {session}: {e}", err=True)
        raise SystemExit(1) from e

    with tempfile.NamedTemporaryFile(delete=False, suffix=".index") as tmp_index:
        tmp_index_path = tmp_index.name

    try:
        env = {**os.environ, "GIT_INDEX_FILE": tmp_index_path}
        base_tree = subprocess.run(
            ["git", "rev-parse", f"{base}^{{tree}}"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()

        tree = _build_tree_with_session(content, base_tree, env)
        return subprocess.run(
            [
                "git",
                "commit-tree",
                tree,
                "-p",
                base,
                "-m",
                f"Focused session for {slug}",
            ],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
    finally:
        Path(tmp_index_path).unlink()


@worktree.command(name="clean-tree")
def clean_tree() -> None:
    """Validate clean state, exempt session context files."""
    parent_status = subprocess.run(
        ["git", "status", "--porcelain"], capture_output=True, text=True, check=True
    ).stdout

    submodule_result = subprocess.run(
        ["git", "-C", "agent-core", "status", "--porcelain"],
        capture_output=True,
        text=True,
        check=False,
    )
    submodule_status = (
        submodule_result.stdout if submodule_result.returncode == 0 else ""
    )

    exempt_files = {"session.md", "jobs.md", "learnings.md"}
    filtered_lines = []
    for line in (parent_status + submodule_status).rstrip().split("\n"):
        if not line:
            continue
        tokens = line.split()
        if (
            len(tokens) >= 2
            and tokens[-1].startswith("agents/")
            and Path(tokens[-1]).name in exempt_files
        ):
            continue
        filtered_lines.append(line)

    if filtered_lines:
        click.echo("\n".join(filtered_lines))
        raise SystemExit(1)


@worktree.command()
@click.argument("slug")
@click.option("--base", default="HEAD", help="Base commit for worktree branch")
@click.option("--session", default="", help="Session file path")
def new(slug: str, base: str, session: str) -> None:
    """Create worktree at wt/{slug}/ with branch {slug}."""
    worktree_path = Path(f"wt/{slug}")

    if worktree_path.exists():
        click.echo(f"Error: existing directory {worktree_path}", err=True)
        raise SystemExit(1)

    if (
        subprocess.run(
            ["git", "rev-parse", "--verify", slug],
            check=False,
            capture_output=True,
        ).returncode
        == 0
    ):
        click.echo(f"Error: existing branch {slug}", err=True)
        raise SystemExit(1)

    try:
        if session:
            branch_commit = _create_session_commit(slug, base, session)
            subprocess.run(
                ["git", "branch", slug, branch_commit], check=True, capture_output=True
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

        project_root = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()

        agent_core_local = Path(project_root) / "agent-core"
        if agent_core_local.exists() and (agent_core_local / ".git").exists():
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


@worktree.command(name="add-commit")
@click.argument("files", nargs=-1, required=True)
def add_commit(files: tuple[str, ...]) -> None:
    """Stage files and commit with message from stdin."""
    subprocess.run(["git", "add", *list(files)], check=True)

    has_staged = (
        subprocess.run(["git", "diff", "--quiet", "--cached"], check=False).returncode
        == 1
    )

    if has_staged:
        message = click.get_text_stream("stdin").read()
        result = subprocess.run(
            ["git", "commit", "-m", message],
            capture_output=True,
            text=True,
            check=True,
        )
        click.echo(result.stdout.strip())


@worktree.command()
@click.argument("slug")
def rm(slug: str) -> None:
    """Remove worktree at wt/{slug}/ and its branch (forced)."""
    worktree_path = Path(f"wt/{slug}")

    if worktree_path.exists():
        result = subprocess.run(
            ["git", "-C", str(worktree_path), "status", "--porcelain"],
            check=False,
            capture_output=True,
            text=True,
        )
        if result.stdout.strip():
            click.echo(f"Warning: {slug} has uncommitted changes")

        subprocess.run(
            ["git", "worktree", "remove", "--force", str(worktree_path)],
            check=True,
            capture_output=True,
        )
    else:
        subprocess.run(["git", "worktree", "prune"], check=True, capture_output=True)

    result = subprocess.run(
        ["git", "branch", "-D", slug], check=False, capture_output=True, text=True
    )
    if result.returncode != 0 and "not found" not in result.stderr.lower():
        click.echo(result.stderr)

    click.echo(f"Removed worktree {slug}")
