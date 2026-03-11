# Cycle 7.4

**Plan**: `plans/handoff-cli-tool/runbook.md`
**Execution Model**: sonnet
**Phase**: 7

---

## Phase Context

End-to-end tests with real git repos via `tmp_path`. Verifies complete pipelines through CLI entry points.

---

---

## Cycle 7.4: Cross-subcommand — handoff then status

**RED Phase:**

**Test:** `test_handoff_then_status`
**File:** `tests/test_session_integration.py`

**Assertions:**
- Create `tmp_path` git repo with `agents/session.md`
- CliRunner invokes `_session handoff` with stdin (updates session.md)
- Then CliRunner invokes `_session status` (reads updated session.md)
- Status output reflects the new status line from handoff input
- Status output reflects the updated completed section
- Verifies parser consistency: handoff writes → status reads the same format

**Expected failure:** Parser asymmetry between write and read paths

**Why it fails:** Integration verifies round-trip consistency

**Verify RED:** `pytest tests/test_session_integration.py::test_handoff_then_status -v`

---
