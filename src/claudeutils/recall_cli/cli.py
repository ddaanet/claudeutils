"""Click group and subcommands for _recall artifact operations."""

import os
from pathlib import Path
from typing import NoReturn

import click

from claudeutils.when.resolver import resolve

from .artifact import parse_entry_keys_section, parse_trigger


def _fail(msg: str, code: int = 1) -> NoReturn:
    """Display message and exit with code.

    LLM-native: stdout, no framing.
    """
    click.echo(msg)
    raise SystemExit(code)


@click.group(name="_recall")
def recall_cmd() -> None:
    """Manage artifact operations (hidden)."""


@recall_cmd.command()
@click.argument("job")
def check(job: str) -> None:
    """Check if artifact has valid Entry Keys section.

    Exits 0 if artifact exists with >=1 entry, exits 1 otherwise.
    """
    project_root = Path(os.getenv("CLAUDE_PROJECT_DIR", "."))
    artifact_path = project_root / "plans" / job / "recall-artifact.md"

    if not artifact_path.exists():
        _fail(f"recall-artifact.md missing for {job}", code=1)

    try:
        content = artifact_path.read_text()
    except (OSError, ValueError) as e:
        _fail(f"Failed to read artifact: {e}", code=1)

    entries = parse_entry_keys_section(content)

    if entries is None:
        _fail(f"recall-artifact.md has no Entry Keys section for {job}", code=1)

    if not entries:
        _fail(f"recall-artifact.md has no entries for {job}", code=1)

    # Valid artifact: exit 0


def _strip_operator(arg: str) -> str:
    """Strip optional operator prefix (when/how), return bare trigger."""
    parts = arg.split(" ", 1)
    if len(parts) >= 2 and parts[0].lower() in {"when", "how"}:
        return parts[1]
    return arg


@recall_cmd.command()
@click.argument("args", nargs=-1, required=True)
def resolve_cmd(args: tuple[str, ...]) -> None:
    """Resolve artifact triggers to decision content.

    MODE DETECTION:
    - If first arg is a file path (artifact mode): read file, parse Entry Keys,
      resolve each trigger via when.resolver.resolve()
    - Otherwise (argument mode): resolve each arg as a trigger

    OUTPUT: Resolved content separated by ---, exit 0 on success.
    """
    project_root = Path(os.getenv("CLAUDE_PROJECT_DIR", "."))
    index_path = str(project_root / ".claude" / "memory-index.json")
    decisions_dir = str(project_root / "agents" / "decisions")

    # Mode detection: artifact mode if first arg is a file
    if args and Path(args[0]).is_file():
        # Artifact mode
        artifact_path = args[0]
        try:
            content = Path(artifact_path).read_text()
        except (OSError, ValueError) as e:
            _fail(f"Failed to read artifact: {e}", code=1)

        entries = parse_entry_keys_section(content)
        if entries is None or not entries:
            _fail("Artifact has no Entry Keys entries", code=1)

        triggers = [parse_trigger(entry) for entry in entries]
    else:
        # Argument mode: each arg is a trigger
        triggers = list(args)

    # Resolve triggers
    results: list[str] = []
    seen: set[str] = set()

    for trigger in triggers:
        # Strip operator to get bare query
        query = _strip_operator(trigger)
        if not query.strip():
            continue

        try:
            result = resolve(query, index_path, decisions_dir)
            if result not in seen:
                seen.add(result)
                results.append(result)
        except (OSError, ValueError, RuntimeError) as e:
            _fail(f"Error resolving '{trigger}': {e}", code=1)

    if not results:
        _fail("No entries resolved", code=1)

    # Output results separated by ---
    output = "\n---\n".join(results)
    click.echo(output)
