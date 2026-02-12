# Cycle 5.6

**Plan**: `plans/worktree-update/runbook.md`
**Execution Model**: haiku
**Phase**: 5

---

## Cycle 5.6: Add `--task` option with `--session-md` default

**Objective:** Add `--task` flag to enable task-based worktree creation mode.

**RED Phase:**

**Test:** `test_new_task_option`
**Assertions:**
- `claudeutils _worktree new --task "Implement feature"` works (no positional slug required)
- `--session-md` option available with default value `agents/session.md`
- `--task` and positional slug are mutually exclusive (error if both provided)
- `--session` option ignored when `--task` provided (warning printed)
- Help text shows `--task` and `--session-md` options

**Expected failure:** click.UsageError: missing required argument slug, or no error when both slug and --task provided

**Why it fails:** `--task` option doesn't exist, slug still required

**Verify RED:** `pytest tests/test_worktree_new.py::test_new_task_option -v`

---

**GREEN Phase:**

**Implementation:** Add Click options and mutual exclusivity validation

**Behavior:**
- Make slug argument optional: `@click.argument('slug', required=False)`
- Add `--task` option: `@click.option('--task', help="Task name from session.md")`
- Add `--session-md` option: `@click.option('--session-md', default='agents/session.md', help="Path to session.md")`
- At function start: validate exactly one of (slug, --task) provided (raise UsageError if both or neither)
- If `--task` and `--session` both provided: print warning, ignore `--session`

**Approach:** Click decorators for options, validation logic at function start

**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Modify slug argument to be optional in `new` command
  Location hint: Change `@click.argument('slug')` to `@click.argument('slug', required=False)`
- File: `src/claudeutils/worktree/cli.py`
  Action: Add `--task` option decorator
  Location hint: Before `def new(...)` function signature
- File: `src/claudeutils/worktree/cli.py`
  Action: Add `--session-md` option decorator
  Location hint: After `--task` option
- File: `src/claudeutils/worktree/cli.py`
  Action: Add mutual exclusivity validation at function start
  Location hint: First lines of function, raise click.UsageError if invalid combination

**Verify GREEN:** `pytest tests/test_worktree_new.py::test_new_task_option -v`
- Must pass

**Verify no regression:** `pytest tests/test_worktree_new.py -v`
- All previous explicit mode tests still pass

---
