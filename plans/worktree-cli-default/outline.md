# Worktree CLI Default to --task: Outline

## Goal

Make positional arg accept task name (with session integration), add `--branch` for bare slug.

**Before:**
- `new <slug>` — bare slug, no session integration
- `new --task "Task Name"` — derives slug, session integration
- `new <slug> --task "Name"` — error (mutually exclusive)

**After:**
- `new "Task Name"` — derives slug, session integration
- `new --branch <slug>` — bare slug, no session integration
- `new "Task Name" --branch <slug>` — custom slug override + session integration (solves 29-char problem)
- `new` (no args) — error

## Affected Files

- `src/claudeutils/worktree/cli.py` — argument rewiring
- `tests/test_worktree_new_creation.py` — 4 tests: `["new", "slug"]` → `["new", "--branch", "slug"]`
- `tests/test_worktree_new_config.py` — `test_new_task_option` rewrite; `test_new_session_handling_branch_reuse` update
- `agent-core/skills/worktree/SKILL.md` — update invocation examples (`--task "name"` → `"name"`)

## TDD Cycles

### Phase 1: `--branch` flag + positional = task name (type: tdd)

**Cycle 1.1 — `new --branch <slug>` creates worktree (no session integration)**
- RED: `invoke(worktree, ["new", "--branch", "my-feature"])` exits 0, worktree at `my-feature` exists
- Verifies: `--branch` option accepted, bare slug behavior preserved

**Cycle 1.2 — `new "Task Name"` derives slug, does session integration**
- RED: `invoke(worktree, ["new", "My task"])` exits 0, worktree at `my-task`, session.md updated
- Verifies: positional = task name, derive_slug called, move_task_to_worktree called

**Cycle 1.3 — `new "Task Name" --branch <slug>` uses custom slug with session integration**
- RED: task name "Runbook quality gates Phase B" + `--branch runbook-quality-gates` → exits 0, worktree at `runbook-quality-gates`, session.md updated with that slug
- Verifies: `--branch` overrides derived slug when used with task name

**Cycle 1.4 — `new` with no args → error**
- RED: `invoke(worktree, ["new"])` exits non-zero with usage error
- Verifies: task name required

**Cycle 1.5 — `new --task "Name"` removed (backward compat error)**
- RED: `invoke(worktree, ["new", "--task", "Name"])` exits non-zero
- Verifies: `--task` option no longer exists

### Phase 2: Update existing tests (type: general)

**Step 2.1 — Update `test_worktree_new_creation.py`**
- 4 tests: `["new", "test-feature"]` → `["new", "--branch", "test-feature"]`
- Behavior unchanged — bare slug tests stay as bare slug via `--branch`

**Step 2.2 — Update `test_worktree_new_config.py`**
- `test_new_task_option`: rewrite — test positional task name instead of `--task`, remove mutual-exclusion sub-test for slug+`--task`
- `test_new_sandbox_registration`: `["new", "test-feature"]` → `["new", "--branch", "test-feature"]`
- `test_new_container_idempotent`, `test_new_environment_init*`: same slug-to-branch rename

**Step 2.3 — Update SKILL.md invocation examples**
- `_worktree new --task "<task name>"` → `_worktree new "<task name>"`
- `_worktree new <slug>` → `_worktree new --branch <slug>`

### Phase 1 addendum: Absorbed scope

**Cycle 1.6 — `new "Task Name"` commits session.md (not left untracked)**
- RED: After `invoke(worktree, ["new", "My task"])`, `git status` in parent shows session.md tracked (not in untracked files list)
- Verifies: `new` with session integration doesn't leave session.md untracked on main

**Note:** Worktree skill adhoc mode (creating worktree without task tracking) is covered by `new --branch <slug>` (Cycle 1.1) — no additional work needed.

## Scope

- IN: cli.py argument parsing, test updates, SKILL.md prose, session.md tracking fix
- OUT: `rm`, `merge`, `ls` subcommands; `derive_slug` logic; `move_task_to_worktree` logic; `focus_session` logic
