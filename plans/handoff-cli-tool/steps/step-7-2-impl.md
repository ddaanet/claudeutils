# Cycle 7.2

**Plan**: `plans/handoff-cli-tool/runbook.md`
**Execution Model**: sonnet
**Phase**: 7

---

## Phase Context

End-to-end tests with real git repos via `tmp_path`. Verifies complete pipelines through CLI entry points.

---

---

**GREEN Phase:**

**Implementation:** Fix wiring issues discovered by integration test

**Behavior:**
- Fresh mode exercises: stdin → parse → state cache → status overwrite → completed write → precommit → diagnostics → cleanup
- Resume mode exercises: state load → skip to step → precommit → diagnostics → cleanup
- Fixes targeted at data threading and error propagation

**Changes:**
- Fix any discovered wiring issues

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_session_integration.py -v`
**Verify no regression:** `just precommit`

---
