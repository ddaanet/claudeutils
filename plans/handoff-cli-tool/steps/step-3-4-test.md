# Cycle 3.4

**Plan**: `plans/handoff-cli-tool/runbook.md`
**Execution Model**: sonnet
**Phase**: 3

---

## Phase Context

Pure data transformation: session.md + filesystem state → STATUS output. No mutations, no stdin.

---

---

## Cycle 3.4: CLI wiring — `claudeutils _session status`

**RED Phase:**

**Test:** `test_session_status_cli`, `test_session_status_missing_session`
**File:** `tests/test_session_status.py`

**Assertions:**
- CliRunner invoking `_session status` with a real session.md file in cwd produces output containing:
  - `Next:` section with first pending task
  - `Pending:` section
  - Output exits with code 0
- CliRunner invoking `_session status` without session.md file → exit code 2, output contains `**Error:**`

**Expected failure:** Command `_session status` not registered — Click returns non-zero with "No such command"

**Why it fails:** No status subcommand registered in session CLI group

**Verify RED:** `pytest tests/test_session_status.py::test_session_status_cli -v`

---
