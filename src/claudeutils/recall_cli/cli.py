"""Click group and subcommands for _recall artifact operations."""

import os
from pathlib import Path
from typing import NoReturn

import click

from .artifact import parse_entry_keys_section


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
