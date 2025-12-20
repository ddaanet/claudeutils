#!/usr/bin/env just --justfile

help:
    @uv run just --list --unsorted

# Run all checks (format, check, test)
dev: format check test line-limits

# Run tests quietly
test *ARGS:
    uv run pytest {{ ARGS }}

# Format, check with complexity disabled, test
lint: format
    uv run ruff check -q --ignore=C901
    docformatter -c src tests
    uv run mypy
    uv run pytest

# Check code style
check:
    uv run ruff check -q
    docformatter -c src tests
    uv run mypy

# Check file line limits
line-limits:
    ./scripts/check_line_limits.sh

# Role: code - verify tests pass
[group('roles')]
role-code *ARGS:
    uv run pytest {{ ARGS }}

# Role: lint - format and verify all checks pass (no complexity)
[group('roles')]
role-lint: format
    uv run ruff check -q --ignore=C901
    docformatter -c src tests
    uv run mypy
    uv run pytest

# Role: refactor - full development cycle
[group('roles')]
role-refactor: dev

# Format code
format:
    #!/usr/bin/env bash -euo pipefail
    tmpfile=$(mktemp tmp-fmt-XXXXXX)
    trap "rm $tmpfile" EXIT
    uv run ruff check -q --fix-only --diff | patch >> "$tmpfile" || true
    uv run ruff format -q --diff | patch >> "$tmpfile" || true
    # docformatter --diff applies the change *and* outputs the diff, so we need to
    # reverse the patch (-R) and dry run (-C), and it prefixes the path with before and
    # after (-p1 ignores the first component of the path). Hence `patch -RCp1`.
    docformatter --diff src tests | patch -RCp1 >> "$tmpfile" || true
    modified=$(
        sed -Ene "/^patching file '/s/^[^']+'([^']+)'/  - \\1/p" < "$tmpfile" \
        | sort --unique)
    bold=$'\033[1m'; nobold=$'\033[22m'
    red=$'\033[31m'; resetfg=$'\033[39m'
    if [ -n "$modified" ] ; then
        echo "$bold${red}Reformatted files:$nobold$resetfg"
        echo "$modified"
    fi
