# Cycle 7.3

**Plan**: `plans/handoff-cli-tool/runbook.md`
**Execution Model**: sonnet
**Phase**: 7

---

## Phase Context

End-to-end tests with real git repos via `tmp_path`. Verifies complete pipelines through CLI entry points.

---

---

**GREEN Phase:**

**Implementation:** Fix wiring issues in commit pipeline

**Behavior:**
- Parent-only: stdin → parse → validate → precommit → stage → commit → output
- Submodule: partition → submodule commit → pointer stage → parent commit
- Amend: same pipeline with `--amend` flag propagation

**Changes:**
- Fix any discovered wiring issues

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_session_integration.py -v`
**Verify no regression:** `just precommit`

---
