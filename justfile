#!/usr/bin/env just --justfile

help:
    @uv run just --list --unsorted

# Run all checks (format, check, test)
dev: format check test

# Run tests quietly
test *ARGS:
    uv run pytest --quiet --no-header --tb=short {{ ARGS }}

# Check code style
check:
    uv run ruff check -q --output-format=concise
    uv run mypy

# Format code
format:
    uv run ruff check --quiet --fix --unsafe-fixes --fix-only
    uv run ruff format --quiet
