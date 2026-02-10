# Justfile Rules:
# - Errors should not pass silently without good reason
# - Only use `2>/dev/null` for probing (checking exit status when command has no quiet option)
# - Only use `|| true` to continue after expected failures (required with `set -e`)
# Enable bash tracing (set -x) for all recipes. Usage: just trace=true <recipe>

trace := "false"

# List available recipes
help:
    @just --list --unsorted

# Format and run all checks
[no-exit-message]
dev: format cache precommit

# Rebuild cached just help output (if justfiles changed)
cache:
    gmake --no-print-directory -C agent-core all

# Run all checks
[no-exit-message]
precommit:
    #!{{ bash_prolog }}
    sync
    claudeutils validate
    gmake --no-print-directory -C agent-core check
    run-checks
    pytest_output=$(safe pytest -q 2>&1)
    echo "$pytest_output"
    if echo "$pytest_output" | grep -q "skipped"; then fail "Tests skipped — all tests must run"; fi
    run-line-limits
    report-end-safe "Precommit"

# Run test suite
[no-exit-message]
test *ARGS:
    #!{{ bash_prolog }}
    sync
    pytest {{ ARGS }}
    report-end-safe "Tests"

# Check file line limits
[no-exit-message]
line-limits:
    #!{{ bash_prolog }}
    sync
    run-line-limits
    report-end-safe "Line limits"

# Create a git worktree for parallel work
[no-exit-message]
wt-new name base="HEAD" session="":
    #!{{ bash_prolog }}
    repo_name=$(basename "$PWD")
    wt_dir="../${repo_name}-{{name}}"
    branch="wt/{{name}}"
    if [ -d "$wt_dir" ]; then
        fail "Worktree already exists: $wt_dir"
    fi
    main_dir="$PWD"
    if [ -n "{{session}}" ]; then
        # Pre-commit focused session.md to branch before worktree creation
        blob=$(git hash-object -w "{{session}}")
        tmp_index=$(mktemp -p tmp/)
        trap "rm -f '$tmp_index'" EXIT ERR
        GIT_INDEX_FILE="$tmp_index" git read-tree "{{base}}"
        GIT_INDEX_FILE="$tmp_index" git update-index --cacheinfo "100644,$blob,agents/session.md"
        new_tree=$(GIT_INDEX_FILE="$tmp_index" git write-tree)
        rm -f "$tmp_index"
        trap - EXIT ERR
        new_commit=$(git commit-tree "$new_tree" -p "$(git rev-parse "{{base}}")" -m "wt: focused session.md")
        git branch "$branch" "$new_commit"
        visible git worktree add "$wt_dir" "$branch"
    else
        visible git worktree add "$wt_dir" -b "$branch" "{{base}}"
    fi
    (cd "$wt_dir" && visible git submodule update --init --reference "$main_dir/agent-core")
    # Put agent-core on a branch (not detached HEAD)
    (cd "$wt_dir/agent-core" && visible git checkout -b "wt/{{name}}")
    # Create .venv so direnv can load it
    (cd "$wt_dir" && visible uv sync)
    # Allow direnv in worktree
    (cd "$wt_dir" && direnv allow 2>/dev/null) || true
    echo ""
    echo "${GREEN}✓${NORMAL} Worktree ready: $wt_dir"
    echo "  Launch: ${COMMAND}cd $wt_dir && claude${NORMAL}"

# Create worktree with focused session for a specific task
[no-exit-message]
wt-task name task_name base="HEAD":
    #!{{ bash_prolog }}
    focused_session="tmp/focused-session-{{name}}.md"
    mkdir -p tmp
    agent-core/bin/focus-session.py "{{task_name}}" > "$focused_session"
    just wt-new "{{name}}" "{{base}}" "$focused_session"
    rm -f "$focused_session"

# List active git worktrees
wt-ls:
    @git worktree list

# Remove a git worktree and its branch
[no-exit-message]
wt-rm name:
    #!{{ bash_prolog }}
    repo_name=$(basename "$PWD")
    wt_dir="../${repo_name}-{{name}}"
    branch="wt/{{name}}"
    if [ ! -d "$wt_dir" ]; then
        fail "Worktree not found: $wt_dir"
    fi
    # Check for uncommitted changes (warn before force-removing)
    if ! (cd "$wt_dir" && git diff --quiet HEAD); then
        echo "${RED}Warning: $wt_dir has uncommitted changes${NORMAL}"
    fi
    # --force required: git can't remove worktrees containing submodules
    visible git worktree remove --force "$wt_dir"
    if git rev-parse --verify "$branch" >/dev/null 2>&1; then
        visible git branch -d "$branch" || \
            echo "${RED}Branch $branch has unmerged changes. Use: git branch -D $branch${NORMAL}"
    fi
    echo "${GREEN}✓${NORMAL} Worktree removed: $wt_dir"

# Merge a worktree branch back and resolve submodule + session.md
[no-exit-message]
wt-merge name:
    #!{{ bash_prolog }}
    repo_name=$(basename "$PWD")
    wt_dir="$(cd .. && pwd)/${repo_name}-{{name}}"
    branch="wt/{{name}}"
    if ! git rev-parse --verify "$branch" >/dev/null 2>&1; then
        fail "Branch not found: $branch"
    fi
    # Step 1: Fetch agent-core commits from worktree into main's submodule
    if [ -d "$wt_dir/agent-core" ] && (cd "$wt_dir/agent-core" && git rev-parse --verify "$branch" >/dev/null 2>&1); then
        (cd agent-core && visible git fetch "$wt_dir/agent-core" "$branch:$branch")
        (cd agent-core && visible git merge --no-edit "$branch")
        (cd agent-core && visible git branch -d "$branch")
        visible git add agent-core
        git diff --quiet --cached || visible git commit -m "Merge agent-core from $branch"
    fi
    # Step 2: Merge parent branch, auto-resolve agent-core + session.md
    if ! git merge --no-edit "$branch"; then
        # agent-core already merged in Step 1 — keep ours
        if git diff --name-only --diff-filter=U | grep -q "^agent-core$"; then
            visible git checkout --ours agent-core
            visible git add agent-core
        fi
        if git diff --name-only --diff-filter=U | grep -q "^agents/session.md$"; then
            visible git checkout --ours agents/session.md
            visible git add agents/session.md
        fi
        # Fail if other conflicts remain
        remaining=$(git diff --name-only --diff-filter=U)
        if [ -n "$remaining" ]; then
            echo "${RED}Unresolved conflicts:${NORMAL}"
            echo "$remaining"
            fail "Resolve conflicts, then: git commit --no-edit"
        fi
        visible git commit --no-edit
    fi
    echo ""
    echo "${GREEN}✓${NORMAL} Merged $branch"
    echo "  Cleanup: ${COMMAND}just wt-rm {{name}}${NORMAL}"

# Format, check with complexity disabled, test
[no-exit-message]
lint: format
    #!{{ bash_prolog }}
    sync
    ruff_ignores=C901,PLR0904,PLR0911,PLR0912,PLR0913,PLR0914,PLR0915,PLR0916,PLR0917,PLR1701,PLR1702
    report "ruff check" ruff check -q --ignore=$ruff_ignores
    report "docformatter -c" docformatter -c src tests
    report "mypy" mypy
    pytest_output=$(safe pytest -q 2>&1)
    echo "$pytest_output"
    if echo "$pytest_output" | grep -q "skipped"; then fail "Tests skipped — all tests must run"; fi
    report-end-safe "Lint"

# Check code style
[no-exit-message]
check:
    #!{{ bash_prolog }}
    sync
    run-checks
    report-end-safe "Checks"

# Format code
format:
    #!{{ bash_prolog }}
    sync
    set-tmpfile
    patch-and-print() {
        patch "$@" | sed -Ene "/^patching file '/s/^[^']+'([^']+)'/\\1/p"
    }
    ruff check -q --fix-only --diff | patch-and-print >> "$tmpfile" || true
    ruff format -q --diff | patch-and-print >> "$tmpfile" || true
    # docformatter --diff applies the change *and* outputs the diff, so we need to
    # reverse the patch (-R) and dry run (-C), and it prefixes the path with before and
    # after (-p1 ignores the first component of the path). Hence `patch -RCp1`.
    docformatter --diff src tests | patch-and-print -RCp1 >> "$tmpfile" || true

    # Format markdown files with remark-cli
    # TODO: fix markdown reformatting bugs and re-enable
    # npx remark . -o --quiet && git diff --name-only | grep '\.md$' >> "$tmpfile" || true

    modified=$(sort --unique < "$tmpfile")
    if [ -n "$modified" ] ; then
        bold=$'\033[1m'; nobold=$'\033[22m'
        red=$'\033[31m'; resetfg=$'\033[39m'
        echo "${bold}${red}**Reformatted files:**"
        echo "$modified" | sed "s|^|${bold}${red}  - ${nobold}${resetfg}|"
    fi

# Create release: tag, build tarball, upload to PyPI and GitHub
# Use --dry-run to perform local changes and verify external permissions without publishing

# Use --rollback to revert local changes from a crashed dry-run
[no-exit-message]
release *ARGS: _fail_if_claudecode dev
    #!{{ bash_prolog }}
    DRY_RUN=false
    ROLLBACK=false
    BUMP=patch
    # Parse flags and positional args
    for arg in {{ ARGS }}; do
        case "$arg" in
            --dry-run) DRY_RUN=true ;;
            --rollback) ROLLBACK=true ;;
            --*) fail "Error: unknown option: $arg" ;;
            *) [[ -n "${positional:-}" ]] && fail "Error: too many arguments"
               positional=$arg ;;
        esac
    done
    [[ -n "${positional:-}" ]] && BUMP=$positional

    # Cleanup function: revert commit and remove build artifacts
    cleanup_release() {
        local initial_head=$1
        local initial_branch=$2
        local version=$3
        visible git reset --hard "$initial_head"
        if [[ -n "$initial_branch" ]]; then
            visible git checkout "$initial_branch"
        else
            visible git checkout "$initial_head"
        fi

        # Remove only this version's build artifacts
        if [[ -n "$version" ]] && [[ -d dist ]]; then
            find dist -name "*${version}*" -delete
            [[ -d dist ]] && [[ -z "$(ls -A dist)" ]] && visible rmdir dist
        fi
    }

    # Rollback mode
    if [[ "$ROLLBACK" == "true" ]]; then
        # Check if there's a release commit at HEAD
        if git log -1 --format=%s | grep -q "🔖 Release"; then
            # Verify no permanent changes (commit not pushed to remote)
            # Skip check if HEAD is detached or has no upstream
            if git symbolic-ref -q HEAD >/dev/null && git rev-parse --abbrev-ref @{u} >/dev/null 2>&1; then
                # We're on a branch with upstream - check if release commit is unpushed
                if ! git log @{u}.. --oneline | grep -q "🔖 Release"; then
                    fail "Error: release commit already pushed to remote"
                fi
            fi

            version=$(git log -1 --format=%s | grep -oP '(?<=Release ).*')
            current_branch=$(git symbolic-ref -q --short HEAD || echo "")
            cleanup_release "HEAD~1" "$current_branch" "$version"
            echo "${GREEN}✓${NORMAL} Rollback complete"
        else
            fail "No release commit found"
        fi
        exit 0
    fi

    # Check preconditions
    git diff --quiet HEAD || fail "Error: uncommitted changes"
    current_branch=$(git symbolic-ref -q --short HEAD || echo "")
    [[ -z "$current_branch" ]] && fail "Error: not on a branch (HEAD is detached)"
    main_branch=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@' || echo "main")
    [[ "$current_branch" != "$main_branch" ]] && fail "Error: must be on $main_branch branch (currently on $current_branch)"
    release=$(uv version --bump "$BUMP" --dry-run)
    tag="v$(echo "$release" | awk '{print $NF}')"
    git rev-parse "$tag" >/dev/null 2>&1 && fail "Error: tag $tag already exists"

    # Interactive confirmation (skip in dry-run)
    if [[ "$DRY_RUN" == "false" ]]; then
        while read -re -p "Release $release? [y/n] " answer; do
            case "$answer" in
                y|Y) break;;
                n|N) exit 1;;
                *) continue;;
            esac
        done
    fi

    if [[ "$DRY_RUN" == "true" ]]; then
        INITIAL_HEAD=$(git rev-parse HEAD)
        INITIAL_BRANCH=$(git symbolic-ref -q --short HEAD || echo "")
        trap 'cleanup_release "$INITIAL_HEAD" "$INITIAL_BRANCH" "${version:-}"; exit 1' ERR EXIT
    fi

    # Perform local changes: version bump, commit, build
    visible uv version --bump "$BUMP"
    version=$(uv version)
    git add pyproject.toml uv.lock
    visible git commit -m "🔖 Release $version"
    tag="v$(uv version --short)"
    visible uv build

    if [[ "$DRY_RUN" == "true" ]]; then
        # Verify external permissions
        git push --dry-run || fail "Error: cannot push to git remote"
        [[ -z "${UV_PUBLISH_TOKEN:-}" ]] && fail "Error: UV_PUBLISH_TOKEN not set. Get token from https://pypi.org/manage/account/token/"
        uv publish --dry-run dist/* || fail "Error: cannot publish to PyPI"
        gh auth status >/dev/null 2>&1 || fail "Error: not authenticated with GitHub"

        echo ""
        echo "${GREEN}✓${NORMAL} Dry-run complete: $version"
        echo "  ${GREEN}✓${NORMAL} Git push permitted"
        echo "  ${GREEN}✓${NORMAL} PyPI publish permitted"
        echo "  ${GREEN}✓${NORMAL} GitHub release permitted"

        # Normal cleanup
        trap - ERR EXIT
        cleanup_release "$INITIAL_HEAD" "$INITIAL_BRANCH" "$version"
        echo ""
        echo "Run: ${COMMAND}just release $BUMP${NORMAL}"
        exit 0
    fi

    # Perform external actions
    visible git push
    visible git tag -a "$tag" -m "Release $version"
    visible git push origin "$tag"
    visible uv publish
    visible gh release create "$tag" --title "$version" --generate-notes
    echo "${GREEN}✓${NORMAL} Release $tag complete"

# Bash prolog
[private]
bash_prolog := \
    ( if trace == "true" { "/usr/bin/env bash -xeuo pipefail" } \
    else { "/usr/bin/env bash -euo pipefail" } ) + "\n" + '''
COMMAND="''' + style('command') + '''"
ERROR="''' + style('error') + '''"
RED=$'\033[31m'
GREEN=$'\033[32m'
NORMAL="''' + NORMAL + '''"
safe () { "$@" || status=false; }
end-safe () { ${status:-true}; }
show () { echo "$COMMAND$*$NORMAL"; }
visible () { show "$@"; "$@"; }
fail () { echo "${ERROR}$*${NORMAL}"; exit 1; }

# Do not uv sync when in Claude Code sandbox
sync() { if [ -w /tmp ]; then uv sync -q; fi; }
set-tmpfile() {
    if [[ ! -v tmpfile ]]; then
        tmpfile=$(mktemp tmp/justfile-XXXXXX)
        trap "rm $tmpfile" EXIT
    fi
}

HEADER_STYLE=$'\033[1;36m'  # Bold cyan
report () {
    # Usage: report "header" command args
    header=$1; shift
    set-tmpfile
    safe "$@" > "$tmpfile"
    if [ -s "$tmpfile" ]; then
        echo "${HEADER_STYLE}# $header${NORMAL}"
        cat "$tmpfile"
    fi
}

run-checks() {
    report "ruff check" ruff check -q
    report "docformatter -c" docformatter -c src tests
    report "mypy" mypy
}

run-line-limits() {
    ./scripts/check_line_limits.sh
}

report-end-safe() {
    if end-safe
    then echo "${GREEN}✓$NORMAL $1 OK"
    else echo "${RED}✗$NORMAL $1 failed"
    fi
    end-safe
}
'''

# Fail if CLAUDECODE is set
[no-exit-message]
[private]
_fail_if_claudecode:
    #!{{ bash_prolog }}
    if [ "${CLAUDECODE:-}" != "" ]
    then fail "⛔️ Denied: Protected recipe"
    fi
