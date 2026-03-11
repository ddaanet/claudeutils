# Cycle 7.2

**Plan**: `plans/handoff-cli-tool/runbook.md`
**Execution Model**: sonnet
**Phase**: 7

---

## Phase Context

End-to-end tests with real git repos via `tmp_path`. Verifies complete pipelines through CLI entry points.

---

---

## Cycle 7.2: Handoff integration

**RED Phase:**

**Test:** `test_handoff_fresh_integration`, `test_handoff_resume_integration`
**File:** `tests/test_session_integration.py`

**Prerequisite:** Read `src/claudeutils/session/handoff/cli.py` — understand full pipeline

**Assertions — fresh mode:**
- Create `tmp_path` git repo with `agents/session.md` (committed initial state)
- CliRunner invokes `_session handoff` with stdin:
  ```
  **Status:** Phase 1 complete.

  ## Completed This Session

  **Infrastructure work:**
  - Extracted git helpers
  ```
- After invocation:
  - `agents/session.md` status line updated to "Phase 1 complete."
  - Completed section contains "Infrastructure work:" and "Extracted git helpers"
  - Output contains diagnostics (precommit result)
  - No state file remains (cleaned up on success)
  - Exit code 0

**Assertions — resume mode:**
- Create state file at `tmp/.handoff-state.json` with `step_reached: "precommit"`
- CliRunner invokes `_session handoff` without stdin
- Pipeline resumes from precommit step (skips write steps)
- Exit code 0

**Expected failure:** End-to-end pipeline wiring gaps

**Why it fails:** Fresh/resume modes exercise different pipeline paths

**Verify RED:** `pytest tests/test_session_integration.py::test_handoff_fresh_integration -v`

---
