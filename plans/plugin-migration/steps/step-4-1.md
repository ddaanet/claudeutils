# Step 4.1

**Plan**: `plans/plugin-migration/runbook.md`
**Execution Model**: haiku
**Phase**: 3

---

## Step 4.1: Create portable.just with extracted recipes

**Objective:** Extract portable recipes (claude, claude0, wt-*, precommit-base) from root justfile to `edify-plugin/just/portable.just` with minimal bash prolog.

**Implementation:**

1. **Create directory:**
```bash
mkdir -p edify-plugin/just
```

2. **Extract portable recipes to edify-plugin/just/portable.just:**

Create file with minimal bash prolog and portable recipes:

```just
# Minimal bash prolog (subset of root justfile prolog)
# Portable recipes need only: fail, visible, color variables

# Color variables
RED := '\033[0;31m'
GREEN := '\033[0;32m'
YELLOW := '\033[1;33m'
NC := '\033[0m' # No Color

# Helper function: fail with error message
fail := 'printf "${RED}Error: %s${NC}\n" "$1" >&2 && exit 1'

# Helper function: print visible message
visible := 'printf "${GREEN}%s${NC}\n" "$1"'

# Claude with plugin directory
claude:
    claude --plugin-dir ./edify-plugin

# Claude with empty system prompt
claude0:
    claude --plugin-dir ./edify-plugin --system-prompt ""

# Create git worktree for parallel work
wt-new name base="HEAD":
    #!/usr/bin/env bash
    set -euo pipefail
    main_dir=$(pwd)
    worktree_dir="../$(basename "$main_dir")-{{name}}"

    # Create worktree
    git worktree add -b wt/{{name}} "$worktree_dir" {{base}} || {{ fail }} "Failed to create worktree"

    # Initialize submodule with --reference to avoid remote fetch
    cd "$worktree_dir"
    git submodule update --init --reference "$main_dir/edify-plugin" || {{ fail }} "Failed to initialize submodule"

    {{ visible }} "Worktree created: $worktree_dir"
    {{ visible }} "Branch: wt/{{name}}"

# List active worktrees
wt-ls:
    git worktree list

# Remove worktree and branch
wt-rm name:
    #!/usr/bin/env bash
    set -euo pipefail
    main_dir=$(pwd)
    worktree_dir="../$(basename "$main_dir")-{{name}}"

    # Deinit submodule
    cd "$worktree_dir"
    git submodule deinit -f --all || true
    cd "$main_dir"

    # Remove worktree (force required for submodules)
    git worktree remove --force "$worktree_dir" || {{ fail }} "Failed to remove worktree"

    # Delete branch
    git branch -D wt/{{name}} || {{ fail }} "Failed to delete branch"

    {{ visible }} "Removed worktree and branch wt/{{name}}"

# Merge worktree branch back
wt-merge name:
    #!/usr/bin/env bash
    set -euo pipefail

    # Merge branch
    git merge --no-ff wt/{{name}} || {{ fail }} "Merge failed"

    # Auto-resolve session.md conflicts (take theirs)
    if git diff --name-only --diff-filter=U | grep -q agents/session.md; then
        git checkout --theirs agents/session.md
        git add agents/session.md
        {{ visible }} "Auto-resolved agents/session.md (took theirs)"
    fi

    # Update submodule reference
    git submodule update --init --recursive

    {{ visible }} "Merged wt/{{name}}"

# Run edify-plugin validators (base precommit)
precommit-base:
    #!/usr/bin/env bash
    set -euo pipefail

    # Run edify-plugin validators
    edify-plugin/bin/validate-tasks.py || {{ fail }} "Task validation failed"
    edify-plugin/bin/validate-learnings.py || {{ fail }} "Learnings validation failed"
    edify-plugin/bin/validate-memory-index.py || {{ fail }} "Memory index validation failed"

    {{ visible }} "Base validators passed"
```

**Recipe extraction notes:**
- **Portable recipes only:** claude, claude0, wt-*, precommit-base (recipes that work without project-specific dependencies)
- **Minimal prolog:** Only fail, visible, color variables (D-5 constraint)
- **Submodule path:** wt-new uses `--reference "$main_dir/edify-plugin"` (updated from agent-core)
- **Validators:** precommit-base calls validators via `edify-plugin/bin/` relative paths

**Design References:**
- D-5: Justfile import for portable recipes
- Component 5: Portable recipes table (claude, claude0, wt-*, precommit-base)
- Outline expansion guidance: wt-new recipe contains edify-plugin submodule reference

**Validation:**
- File exists at `edify-plugin/just/portable.just`
- Recipes use minimal prolog only (fail, visible, colors)
- claude/claude0 use `--plugin-dir ./edify-plugin`
- wt-new uses `--reference "$main_dir/edify-plugin"`
- precommit-base calls validators at `edify-plugin/bin/`
- precommit-base works: `just --justfile edify-plugin/just/portable.just precommit-base`

**Expected Outcome:** portable.just created with extracted recipes and minimal prolog.

**Unexpected Result Handling:**
- If recipe syntax error: verify Just syntax (use `just --justfile edify-plugin/just/portable.just --list`)
- If prolog functions missing: ensure fail, visible, color variables defined
- If submodule reference wrong: must use edify-plugin not agent-core

**Success Criteria:**
- portable.just exists and parses correctly with all 7 recipes (claude, claude0, wt-new, wt-ls, wt-rm, wt-merge, precommit-base)
- Minimal prolog (no project-specific functions — only fail, visible, colors)
- All edify-plugin paths updated
- precommit-base validator calls work

---
