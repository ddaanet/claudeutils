#!/usr/bin/env just --justfile

help:
    @uv run just --list --unsorted

# Run all checks (format, check, test, line-limits)
[no-exit-message]
dev: format check test line-limits

# Run tests quietly
[no-exit-message]
test *ARGS:
    uv run pytest -q {{ ARGS }}

# Format, check with complexity disabled, test
[no-exit-message]
lint: format
    uv run ruff check -q --ignore=C901
    docformatter -c src tests
    uv run mypy
    uv run pytest -q

# Check code style
[no-exit-message]
check:
    uv run ruff check -q
    docformatter -c src tests
    uv run mypy

# Check file line limits
[no-exit-message]
line-limits:
    ./scripts/check_line_limits.sh

# Role: code - verify tests pass
[group('roles')]
[no-exit-message]
role-code *ARGS:
    uv run pytest {{ ARGS }}

# Role: lint - format and verify all checks pass (no complexity)
[group('roles')]
[no-exit-message]
role-lint: lint

# Role: refactor - full development cycle
[group('roles')]
[no-exit-message]
role-refactor: dev

# Format code
format:
    #!/usr/bin/env bash -euo pipefail
    tmpfile=$(mktemp tmp-fmt-XXXXXX)
    trap "rm $tmpfile" EXIT
    patch-and-print() {
        patch "$@" | sed -Ene "/^patching file '/s/^[^']+'([^']+)'/  - \\1/p"
    }
    uv run ruff check -q --fix-only --diff | patch-and-print >> "$tmpfile" || true
    uv run ruff format -q --diff | patch-and-print >> "$tmpfile" || true
    # docformatter --diff applies the change *and* outputs the diff, so we need to
    # reverse the patch (-R) and dry run (-C), and it prefixes the path with before and
    # after (-p1 ignores the first component of the path). Hence `patch -RCp1`.
    docformatter --diff src tests | patch-and-print -RCp1 >> "$tmpfile" || true

    git ls-files | grep '\.md$' | grep -v '/TEST_DATA\.md$' \
    | uv run scripts/fix_markdown_structure.py >> "$tmpfile"
    dprint -c .dprint.json check --list-different >> "$tmpfile" || true
    dprint -c .dprint.json fmt -L warn >> "$tmpfile"
    modified=$(sort --unique < "$tmpfile")
    bold=$'\033[1m'; nobold=$'\033[22m'
    red=$'\033[31m'; resetfg=$'\033[39m'
    if [ -n "$modified" ] ; then
        echo "$bold${red}Reformatted files:$nobold$resetfg"
        echo "$modified"
    fi
