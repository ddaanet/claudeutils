# Cycle 6.6

**Plan**: `plans/handoff-cli-tool/runbook.md`
**Execution Model**: sonnet
**Phase**: 6

---

## Phase Context

Staging, submodule coordination, amend semantics, structured output.

---

---

## Cycle 6.6: CLI wiring — `claudeutils _session commit`

**RED Phase:**

**Test:** `test_session_commit_cli_success`, `test_session_commit_cli_validation_error`
**File:** `tests/test_session_commit_pipeline.py`

**Assertions:**
- CliRunner with valid commit markdown on stdin (real git repo via `tmp_path`, file staged) → exit 0, stdout contains `[branch hash] message` format line
- CliRunner with files that have no changes → exit 2, stdout contains `**Error:**` and `STOP:`
- CliRunner with empty stdin → exit 2, stdout contains `**Error:**` and references missing required section

**Expected failure:** Command not registered

**Why it fails:** No commit subcommand

**Verify RED:** `pytest tests/test_session_commit_pipeline.py::test_session_commit_cli_success -v`

---
