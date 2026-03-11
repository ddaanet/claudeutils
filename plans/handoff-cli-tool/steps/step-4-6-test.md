# Cycle 4.6

**Plan**: `plans/handoff-cli-tool/runbook.md`
**Execution Model**: sonnet
**Phase**: 4

---

## Phase Context

Stdin parsing, session.md writes, committed detection, state caching, diagnostics.

---

---

## Cycle 4.6: Diagnostic output (H-3)

**RED Phase:**

**Test:** `test_diagnostics_precommit_pass`, `test_diagnostics_precommit_fail`, `test_diagnostics_learnings_age`
**File:** `tests/test_session_handoff.py`

**Assertions:**
- `format_diagnostics(precommit_result, git_status, learnings_age)` when precommit passed:
  - Contains precommit output
  - Contains git status/diff markdown
  - No learnings age warning if all entries < 7 days
- When precommit failed:
  - Contains precommit failure output
  - Does NOT contain git status/diff (conditional — only on pass)
  - Contains learnings age summary if any ≥ 7 days
- When learnings have entries ≥ 7 active days:
  - Output contains `**Learnings:** N entries ≥7 days — consider /codify`

**Expected failure:** `ImportError`

**Why it fails:** No diagnostics formatting function

**Verify RED:** `pytest tests/test_session_handoff.py::test_diagnostics_precommit_pass -v`

---
