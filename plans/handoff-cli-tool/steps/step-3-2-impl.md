# Cycle 3.2

**Plan**: `plans/handoff-cli-tool/runbook.md`
**Execution Model**: sonnet
**Phase**: 3

---

## Phase Context

Pure data transformation: session.md + filesystem state → STATUS output. No mutations, no stdin.

---

---

**GREEN Phase:**

**Implementation:** Add `render_pending()`, `render_worktree()`, `render_unscheduled()` to `session/status/render.py`

**Behavior:**
- `render_pending(tasks, plan_states)`: Filter to pending tasks (checkbox `" "`), format with optional plan status. Non-default model shown in parens. Plan status from `plan_states` dict mapping plan name → status string
- `render_worktree(tasks)`: Format worktree tasks with `→` markers
- `render_unscheduled(all_plans, task_plan_dirs)`: Filter plans not in `task_plan_dirs` set, exclude `delivered`, sort alphabetically, format with `—` separator

**Approach:** Each function produces a section string or empty string. Caller concatenates non-empty sections.

**Changes:**
- File: `src/claudeutils/session/status/render.py`
  Action: Add three rendering functions

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_session_status.py -v`
**Verify no regression:** `just precommit`

---
