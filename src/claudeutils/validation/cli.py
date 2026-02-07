"""CLI commands for validation."""

import sys
from pathlib import Path

import click

from claudeutils.validation.common import find_project_root
from claudeutils.validation.decision_files import validate as validate_decision_files
from claudeutils.validation.jobs import validate as validate_jobs
from claudeutils.validation.learnings import validate as validate_learnings
from claudeutils.validation.memory_index import validate as validate_memory_index
from claudeutils.validation.tasks import validate as validate_tasks


@click.group(invoke_without_command=True)
@click.pass_context
def validate(ctx: click.Context) -> None:
    """Validate project structure and conventions.

    Run all validators by default, or specify individual validators.
    """
    if ctx.invoked_subcommand is None:
        # Run all validators
        root = find_project_root(Path.cwd())
        all_errors: dict[str, list[str]] = {}

        # Validate learnings
        try:
            errors = validate_learnings(Path("agents/learnings.md"), root)
            if errors:
                all_errors["learnings"] = errors
        except Exception as e:
            all_errors["learnings"] = [f"Error: {e}"]

        # Validate memory-index
        try:
            errors = validate_memory_index(Path("agents/memory-index.md"), root)
            if errors:
                all_errors["memory-index"] = errors
        except Exception as e:
            all_errors["memory-index"] = [f"Error: {e}"]

        # Validate tasks
        try:
            errors = validate_tasks("agents/session.md", "agents/learnings.md", root)
            if errors:
                all_errors["tasks"] = errors
        except Exception as e:
            all_errors["tasks"] = [f"Error: {e}"]

        # Validate decision files
        try:
            errors = validate_decision_files(root)
            if errors:
                all_errors["decisions"] = errors
        except Exception as e:
            all_errors["decisions"] = [f"Error: {e}"]

        # Validate jobs
        try:
            errors = validate_jobs(root)
            if errors:
                all_errors["jobs"] = errors
        except Exception as e:
            all_errors["jobs"] = [f"Error: {e}"]

        # Print errors with headers
        if all_errors:
            for validator_name, errors in all_errors.items():
                click.echo(f"Error ({validator_name}):", err=True)
                for error in errors:
                    click.echo(f"  {error}", err=True)
            sys.exit(1)


@validate.command()
def learnings() -> None:
    """Validate learnings.md."""
    root = find_project_root(Path.cwd())
    errors = validate_learnings(Path("agents/learnings.md"), root)
    if errors:
        for error in errors:
            click.echo(error, err=True)
        sys.exit(1)


@validate.command()
def memory_index() -> None:
    """Validate memory-index.md."""
    root = find_project_root(Path.cwd())
    errors = validate_memory_index(Path("agents/memory-index.md"), root)
    if errors:
        for error in errors:
            click.echo(error, err=True)
        sys.exit(1)


@validate.command()
def tasks() -> None:
    """Validate task keys in session.md."""
    root = find_project_root(Path.cwd())
    errors = validate_tasks("agents/session.md", "agents/learnings.md", root)
    if errors:
        for error in errors:
            click.echo(error, err=True)
        sys.exit(1)


@validate.command()
def decisions() -> None:
    """Validate decision files."""
    root = find_project_root(Path.cwd())
    errors = validate_decision_files(root)
    if errors:
        for error in errors:
            click.echo(error, err=True)
        sys.exit(1)


@validate.command()
def jobs() -> None:
    """Validate jobs.md."""
    root = find_project_root(Path.cwd())
    errors = validate_jobs(root)
    if errors:
        for error in errors:
            click.echo(error, err=True)
        sys.exit(1)
