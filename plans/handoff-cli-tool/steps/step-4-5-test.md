# Cycle 4.5

**Plan**: `plans/handoff-cli-tool/runbook.md`
**Execution Model**: sonnet
**Phase**: 4

---

## Phase Context

Stdin parsing, session.md writes, committed detection, state caching, diagnostics.

---

---

## Cycle 4.5: Precommit integration

**RED Phase:**

**Test:** `test_handoff_precommit_pass`, `test_handoff_precommit_fail`
**File:** `tests/test_session_handoff.py`

**Assertions:**
- `run_precommit()` calls `just precommit` subprocess, returns `PrecommitResult` with `success: bool`, `output: str`
- On failure: `success == False`, `output` contains the precommit failure text
- On success: `success == True`, `output` contains passing summary

**Expected failure:** `ImportError` — `run_precommit` doesn't exist

**Why it fails:** No precommit integration

**Verify RED:** `pytest tests/test_session_handoff.py::test_handoff_precommit_pass -v`

---
