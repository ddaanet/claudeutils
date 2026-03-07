# Cycle 7.1

**Plan**: `plans/handoff-cli-tool/runbook.md`
**Execution Model**: sonnet
**Phase**: 7

---

## Phase Context

End-to-end tests with real git repos via `tmp_path`. Verifies complete pipelines through CLI entry points.

---

---

**GREEN Phase:**

**Implementation:** Fix any wiring gaps discovered by integration test

**Behavior:**
- The test exercises: CLI command → parse_session() → render functions → formatted output
- Fixes are targeted at wiring issues (import paths, function signatures, data threading)
- No new production code expected — all components built in Phases 2-3

**Changes:**
- Fix any import or wiring issues discovered
- May require adjusting function signatures for data threading

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_session_integration.py::test_status_integration -v`
**Verify no regression:** `just precommit`

---
