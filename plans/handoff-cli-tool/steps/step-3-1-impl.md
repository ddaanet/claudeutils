# Cycle 3.1

**Plan**: `plans/handoff-cli-tool/runbook.md`
**Execution Model**: sonnet
**Phase**: 3

---

## Phase Context

Pure data transformation: session.md + filesystem state → STATUS output. No mutations, no stdin.

---

---

**GREEN Phase:**

**Implementation:** Create `src/claudeutils/session/status/render.py` with `render_next()`

**Behavior:**
- Iterate tasks, find first with `checkbox == " "` and `worktree_marker is None`
- Format as `Next:` block with command, model, restart
- Model defaults to "sonnet" if None. Restart shows "yes" if True, "no" if False

**Changes:**
- File: `src/claudeutils/session/status/render.py`
  Action: Create with `render_next(tasks: list[ParsedTask]) -> str`

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_session_status.py -v`
**Verify no regression:** `just precommit`

---
