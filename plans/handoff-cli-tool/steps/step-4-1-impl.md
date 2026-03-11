# Cycle 4.1

**Plan**: `plans/handoff-cli-tool/runbook.md`
**Execution Model**: sonnet
**Phase**: 4

---

## Phase Context

Stdin parsing, session.md writes, committed detection, state caching, diagnostics.

---

---

**GREEN Phase:**

**Implementation:** Create `src/claudeutils/session/handoff/parse.py`

**Behavior:**
- `HandoffInput` dataclass: `status_line: str`, `completed_lines: list[str]`
- `parse_handoff_input(text: str) -> HandoffInput` — locate `**Status:**` line, extract text after marker. Locate `## Completed This Session` heading, extract all lines until next `## ` or EOF
- `HandoffInputError` exception for missing required markers

**Changes:**
- File: `src/claudeutils/session/handoff/parse.py`
  Action: Create with `HandoffInput`, `HandoffInputError`, `parse_handoff_input()`

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_session_handoff.py -v`
**Verify no regression:** `just precommit`

---
