# Cycle 4.6

**Plan**: `plans/handoff-cli-tool/runbook.md`
**Execution Model**: sonnet
**Phase**: 4

---

## Phase Context

Stdin parsing, session.md writes, committed detection, state caching, diagnostics.

---

---

**GREEN Phase:**

**Implementation:** Add `format_diagnostics()` to `session/handoff/context.py`

**Behavior:**
- `format_diagnostics(precommit: PrecommitResult, git_output: str | None, learnings_age_days: int | None) -> str`
- Always include precommit result block
- If precommit passed: include git status/diff output
- If any learnings ≥ 7 days: append age summary line
- All output as structured markdown

**Changes:**
- File: `src/claudeutils/session/handoff/context.py`
  Action: Create with `format_diagnostics()`

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_session_handoff.py -v`
**Verify no regression:** `just precommit`

---
