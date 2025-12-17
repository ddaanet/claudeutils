#!/usr/bin/env just --justfile

help:
    @uv run just --list --unsorted

# Run all checks (format, check, test)
dev: format check test

# Run tests quietly
test *ARGS:
    uv run pytest {{ ARGS }}

# Check code style
check:
    uv run ruff check -q
    docformatter -c src tests
    uv run mypy

# Format code
format:
    uv run ruff check -q --fix-only
    uv run ruff format -q
    docformatter src tests || true
