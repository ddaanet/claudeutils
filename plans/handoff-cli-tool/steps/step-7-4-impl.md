# Cycle 7.4

**Plan**: `plans/handoff-cli-tool/runbook.md`
**Execution Model**: sonnet
**Phase**: 7

---

## Phase Context

End-to-end tests with real git repos via `tmp_path`. Verifies complete pipelines through CLI entry points.

---

---

**GREEN Phase:**

**Implementation:** Fix any format asymmetries between handoff writes and status reads

**Behavior:**
- Handoff writes status line and completed section in format that status parser expects
- Any format divergence between write and read is a bug

**Changes:**
- Fix any discovered format mismatches

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_session_integration.py -v`
**Verify no regression:** `just precommit`

---

**Phase 7 Checkpoint (full):** `just precommit` — all tests pass, full suite green. Final checkpoint covers all 7 phases.
