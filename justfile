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
        patch "$@" | sed -Ene "/^patching file '/s/^[^']+'([^']+)'/\\1/p"
    }
    uv run ruff check -q --fix-only --diff | patch-and-print >> "$tmpfile" || true
    uv run ruff format -q --diff | patch-and-print >> "$tmpfile" || true
    # docformatter --diff applies the change *and* outputs the diff, so we need to
    # reverse the patch (-R) and dry run (-C), and it prefixes the path with before and
    # after (-p1 ignores the first component of the path). Hence `patch -RCp1`.
    docformatter --diff src tests | patch-and-print -RCp1 >> "$tmpfile" || true

    git ls-files | grep '\.md$' | grep -v '/TEST_DATA\.md$' \
    | uv run claudeutils markdown >> "$tmpfile"
    dprint -c .dprint.json check --list-different \
    | sed "s|^$(pwd)/||g" >> "$tmpfile" || true
    dprint -c .dprint.json fmt -L warn
    modified=$(sort --unique < "$tmpfile")
    if [ -n "$modified" ] ; then
        bold=$'\033[1m'; nobold=$'\033[22m'
        red=$'\033[31m'; resetfg=$'\033[39m'
        echo "${bold}${red}**Reformatted files:**"
        echo "$modified" | sed "s|^|${bold}${red}  - ${nobold}${resetfg}|"
    fi

# Create release: tag, build tarball, upload to PyPI and GitHub
release bump='patch': _fail_if_claudecode dev
    #!/usr/bin/env bash -euo pipefail
    {{ _bash-defs }}
    git diff --quiet HEAD || fail "Error: uncommitted changes"
    release=$(uv version --bump {{ bump }} --dry-run)
    while read -re -p "Release $release? [y/n] " answer; do
        case "$answer" in
            y|Y) break;;
            n|N) exit 1;;
            *) continue;;
        esac
    done
    visible uv version --bump {{ bump }}
    version=$(uv version)
    git add pyproject.toml uv.lock
    visible git commit -m "🔖 Release $version"
    visible git push
    tag="v$(uv version --short)"
    git rev-parse "$tag" >/dev/null 2>&1 && fail "Error: tag $tag already exists"
    visible git tag -a "$tag" -m "Release $version"
    visible git push origin "$tag"
    visible uv build
    visible uv publish
    visible gh release create "$tag" --title "$version" \
        --generate-notes
    echo "${GREEN}Release $tag complete${NORMAL}"

# Bash definitions
[private]
_bash-defs := '''
COMMAND="''' + style('command') + '''"
ERROR="''' + style('error') + '''"
GREEN=$'\033[32m'
NORMAL="''' + NORMAL + '''"
safe () { "$@" || status=false; }
end-safe () { ${status:-true}; }
show () { echo "$COMMAND$*$NORMAL"; }
visible () { show "$@"; "$@"; }
fail () { echo "${ERROR}$*${NORMAL}"; exit 1; }
'''

# Fail if CLAUDECODE is set
[no-exit-message]
[private]
_fail_if_claudecode:
    #!/usr/bin/env bash -euo pipefail
    if [ "${CLAUDECODE:-}" != "" ]; then
        echo -e '{{ style("error") }}⛔️ Denied: Protected recipe{{ NORMAL }}'
        exit 1
    fi

