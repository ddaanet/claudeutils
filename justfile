# Use direct commands, venv activation is handled by direnv, see .envrc
# Do not let errors pass silently, only use `2>/dev/null` when necessary (probing)
# Use the "safe" function to capture exit status from commands and continue on error.
# The "end-safe" function return the last non-zero exit status captured by safe, or 0.
# The "show" command prints a message to stdout in just command style.
# The "visible" command prints the command in just command style and executes it.

help:
    just --list --unsorted

# Run all checks (format, check, test, line-limits)
[no-exit-message]
dev: format precommit

# Run pre-commit checks (check, test, line-limits)
[no-exit-message]
precommit:
    #!/usr/bin/env bash -euo pipefail
    {{ _bash-defs }}
    sync
    report "bare ignores" check_bare_ignores
    report "ruff" ruff check -q
    report "docformatter" docformatter -c src tests
    report "mypy" mypy
    report "line limits" ./scripts/check_line_limits.sh
    pytest
    end-safe

# Run tests
[no-exit-message]
test *ARGS:
    #!/usr/bin/env bash -euo pipefail
    {{ _bash-defs }}
    sync
    pytest {{ ARGS }}

# Format, check with complexity disabled, test
[no-exit-message]
lint: format
    #!/usr/bin/env bash -euo pipefail
    {{ _bash-defs }}
    sync
    report "bare ignores" check_bare_ignores
    report "ruff" ruff check -q --ignore=C901
    report "docformatter" docformatter -c src tests
    report "mypy" mypy
    pytest
    end-safe

# Check code style
[no-exit-message]
check:
    #!/usr/bin/env bash -euo pipefail
    {{ _bash-defs }}
    sync
    report "ruff" ruff check -q
    report "docformatter" docformatter -c src tests
    report "mypy" mypy
    end-safe

# Check file line limits
[no-exit-message]
line-limits:
    ./scripts/check_line_limits.sh

# Role: code - verify tests pass
[group('roles')]
[no-exit-message]
role-code *ARGS: (test ARGS)

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
    {{ _bash-defs }}
    sync
    tmpfile=$(mktemp tmp-fmt-XXXXXX)
    trap "rm $tmpfile" EXIT
    patch-and-print() {
        patch "$@" | sed -Ene "/^patching file '/s/^[^']+'([^']+)'/\\1/p"
    }
    ruff check -q --fix-only --diff | patch-and-print >> "$tmpfile" || true
    ruff format -q --diff | patch-and-print >> "$tmpfile" || true
    # docformatter --diff applies the change *and* outputs the diff, so we need to
    # reverse the patch (-R) and dry run (-C), and it prefixes the path with before and
    # after (-p1 ignores the first component of the path). Hence `patch -RCp1`.
    docformatter --diff src tests | patch-and-print -RCp1 >> "$tmpfile" || true

    # TODO: Format markdown files, when markdown fixup work is done

    modified=$(sort --unique < "$tmpfile")
    if [ -n "$modified" ] ; then
        bold=$'\033[1m'; nobold=$'\033[22m'
        red=$'\033[31m'; resetfg=$'\033[39m'
        echo "${bold}${red}**Reformatted files, Read again before Edit:**"
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
test -t 1 && colorful=true || colorful=false
if $colorful; then
    style_command () { echo -n "''' + style('command') + '''"; }
    style_error () { echo -n "''' + style('error') + '''"; }
    style_normal () { echo -n "''' + NORMAL + '''"; }
    style_bold () { echo -en "\033[1m"; }
    style_red () { echo -en "\033[31m"; }
    style_green () { echo -en "\033[32m"; }
    style_yellow () { echo -en "\033[33m"; }
    style_header () { echo -en "\033[1;36m"; }
else
    style_command () { :; }
    style_error () { :; }
    style_normal () { :; }
    style_bold () { :; }
    style_red () { :; }
    style_green () { :; }
    style_yellow () { :; }
    style_header () { :; }
fi
end_line () { style_normal; echo; }
safe () { "$@" || status=false; }
end-safe () { ${status:-true}; }
show () { style_command; echo -n "$*"; end_line; }
visible () { show "$@"; "$@"; }
fail () { { style_error; echo -n "$*"; end_line; } >&2; exit 1; }

# Do not uv sync when in Claude Code sandbox
sync() { test -w /tmp &&  uv sync -q "$@"; }

newline_needed=false
need_newline() { newline_needed=true; }
newline_if_needed() { $newline_needed && echo || true; }

header() { style_header; echo -n "$*"; end_line; }
report () {
    # Usage: report "header" command args
    header=$1; shift
    if [[ ! -v tmpfile ]]; then
        tmpfile=$(mktemp tmp/lint-XXXXXX)
        trap "rm $tmpfile" EXIT
    fi
    safe "$@" > "$tmpfile"
    if [ -s "$tmpfile" ]; then
        newline_if_needed
        header "# $header"; echo; cat "$tmpfile"
        need_newline
    fi
}
check_bare_ignores() {
    color_opt=$($colorful && echo "--color=always" || true)
    ! rg $color_opt --type python "#\s+type:\s+ignore(\$|[^\[])|#\snoqa(\$|[^:])"
}
ruff () {
    if $colorful
    then FORCE_COLOR=1 command ruff "$@"
    else command ruff "$@"
    fi
}
mypy () {
    if $colorful
    then FORCE_COLOR=1 command mypy "$@"
    else command mypy "$@"
    fi
}
pytest() {
    newline_if_needed
    color_opt=$($colorful && echo "--color=yes" || true)
    command pytest $color_opt "$@" |& while read -r line; do
        in_block=false
        if [[ $line =~ ([^*]*)(\*\*[^*]+\*\*)(.*)$ ]]; then
            line=$(
                echo -n "${BASH_REMATCH[1]}"
                style_bold
                echo -n "${BASH_REMATCH[2]}"
                style_normal
                echo "${BASH_REMATCH[3]}")
        fi
        shopt -s nocasematch
        if [[ $line =~ ^(.*\ )?(passed)([,\ ].*)?$ ]]; then
            line=$(
                echo -n "${BASH_REMATCH[1]}"
                style_green
                echo -n "${BASH_REMATCH[2]}"
                style_normal
                echo "${BASH_REMATCH[3]}"
            )
        fi
        if [[ $line =~ ^(.*\ )?(failed)([,\ ].*)?$ ]]; then
            line=$(
                echo -n "${BASH_REMATCH[1]}"
                style_red
                echo -n "${BASH_REMATCH[2]}"
                style_normal
                echo "${BASH_REMATCH[3]}"
            )
        fi
        shopt -u nocasematch
        if [[ $line =~ ^\`{3}python* ]]; then
            style_yellow;
            echo "$line"
            in_block=true
        elif [[ $line =~ ^\`{3} && $in_block ]]; then
            echo -n "$line"
            end_line
            in_block=false
        elif [[ $line =~ \#+\ +[^\ ] ]]
        then header "$line"
        else echo "$line"
        fi
    done
    need_newline
}
'''

# Fail if CLAUDECODE is set
[no-exit-message]
[private]
_fail_if_claudecode:
    #!/usr/bin/env bash -euo pipefail
    {{ _bash-defs }}
    [ "${CLAUDECODE:-}" = "" ] || fail "⛔️ Denied: Protected recipe"
