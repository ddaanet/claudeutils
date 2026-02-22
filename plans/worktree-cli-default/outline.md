# Worktree CLI Default to --task: Outline

## Goal

Make positional arg accept task name (with session integration), add `--branch` for bare slug. Remove sandbox registration from `new`.

**Before:**
- `new <slug>` — bare slug, no session integration
- `new --task "Task Name"` — derives slug, session integration
- `new <slug> --task "Name"` — error (mutually exclusive)
- `new` writes `additionalDirectories` to `.claude/settings.local.json`

**After:**
- `new "Task Name"` — derives slug, session integration
- `new --branch <slug>` — bare slug, no session integration
- `new "Task Name" --branch <slug>` — custom slug override + session integration (solves 29-char problem)
- `new` (no args) — error
- No sandbox registration — inter-tree operations via git or user-validated sandbox override

## Affected Files

- `src/claudeutils/worktree/cli.py` — argument rewiring, remove `add_sandbox_dir` calls from `_create_parent_worktree`
- `tests/test_worktree_new_creation.py` — 4 tests: `["new", "slug"]` → `["new", "--branch", "slug"]`
- `tests/test_worktree_new_config.py` — `test_new_task_option` rewrite; `test_new_sandbox_registration` removal; slug-to-branch renames
- `agent-core/skills/worktree/SKILL.md` — update invocation examples (`--task "name"` → `"name"`)

## TDD Cycles

### Phase 1: `--branch` flag + positional = task name (type: tdd)

**Cycle 1.1 — `new --branch <slug>` creates worktree (no session integration, no sandbox registration)**
- RED: `invoke(worktree, ["new", "--branch", "my-feature"])` exits 0, worktree at `my-feature` exists, session.md NOT modified, no `.claude/settings.local.json` written
- Verifies: `--branch` option accepted, bare slug behavior preserved, sandbox registration removed

**Cycle 1.2 — `new "Task Name"` derives slug, does session integration**
- RED: `invoke(worktree, ["new", "My task"])` exits 0, worktree at `my-task`, `move_task_to_worktree` called with task name and derived slug
- Verifies: positional = task name, derive_slug called, session.md gets inline worktree marker

**Cycle 1.3 — `new "Task Name" --branch <slug>` uses custom slug with session integration**
- RED: task name "Runbook quality gates Phase B" + `--branch runbook-quality-gates` → exits 0, worktree at `runbook-quality-gates`, `move_task_to_worktree` called with that slug
- Verifies: `--branch` overrides derived slug when used with task name

**Cycle 1.4 — `new` with no args → error**
- RED: `invoke(worktree, ["new"])` exits non-zero with usage error
- Verifies: at least one of positional task name or `--branch` required

**Cycle 1.5 — `new "Task Name"` commits session.md (not left untracked)**
- RED: After `invoke(worktree, ["new", "My task"])`, `git status` in parent shows session.md tracked (not in untracked files list)
- Verifies: `new` with session integration doesn't leave session.md untracked on main

**Note:** Worktree skill adhoc mode (creating worktree without task tracking) is covered by `new --branch <slug>` (Cycle 1.1) — no additional work needed.

**Note:** `--task` option removal is not a separate cycle — it's a side effect of the argument rewiring in Cycle 1.1. Click rejects unknown options by default.

### Phase 2: Update existing tests + cleanup (type: general)

Phase 1 breaks existing tests that use the old `["new", "slug"]` invocation. Phase 2 fixes them.

**Step 2.1 — Update `test_worktree_new_creation.py`**
- 4 tests: `["new", "test-feature"]` → `["new", "--branch", "test-feature"]`
- Behavior unchanged — bare slug tests stay as bare slug via `--branch`

**Step 2.2 — Update `test_worktree_new_config.py`**
- `test_new_task_option`: rewrite — test positional task name instead of `--task`, remove mutual-exclusion sub-test for slug+`--task`
- `test_new_sandbox_registration`: remove — sandbox registration no longer occurs
- `test_new_container_idempotent`, `test_new_environment_init*`: slug-to-branch rename

**Step 2.3 — Update SKILL.md invocation examples**
- `_worktree new --task "<task name>"` → `_worktree new "<task name>"`
- `_worktree new <slug>` → `_worktree new --branch <slug>`

## Scope

- IN: cli.py argument parsing, sandbox removal (`add_sandbox_dir` calls), test updates, SKILL.md prose, session.md tracking fix
- OUT: `rm`, `merge`, `ls` subcommands; `derive_slug` logic; `move_task_to_worktree` logic; `focus_session` logic; `add_sandbox_dir` function definition (may become dead code — separate cleanup)
- SEPARATE TASK: `rm --confirm` gate fix (listed as absorbed in session.md but orthogonal to CLI argument changes)
