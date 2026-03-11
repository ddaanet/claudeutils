# Cycle 4.7

**Plan**: `plans/handoff-cli-tool/runbook.md`
**Execution Model**: sonnet
**Phase**: 4

---

## Phase Context

Stdin parsing, session.md writes, committed detection, state caching, diagnostics.

---

---

## Cycle 4.7: CLI wiring — `claudeutils _session handoff`

**RED Phase:**

**Test:** `test_session_handoff_cli_fresh`, `test_session_handoff_cli_resume`, `test_session_handoff_cli_no_stdin_no_state`
**File:** `tests/test_session_handoff.py`

**Assertions:**
- CliRunner with stdin input → exit 0, session.md status line updated, completed section written, diagnostics output
- CliRunner without stdin but with existing state file → exit 0, resumes from `step_reached`
- CliRunner without stdin and no state file → exit 2, output contains error message about missing input

**Expected failure:** Command not registered

**Why it fails:** No handoff subcommand

**Verify RED:** `pytest tests/test_session_handoff.py::test_session_handoff_cli_fresh -v`

---
