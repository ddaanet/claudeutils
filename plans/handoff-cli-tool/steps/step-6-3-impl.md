# Cycle 6.3

**Plan**: `plans/handoff-cli-tool/runbook.md`
**Execution Model**: sonnet
**Phase**: 6

---

## Phase Context

Staging, submodule coordination, amend semantics, structured output.

---

---

**GREEN Phase:**

**Implementation:** Add amend support to `commit_pipeline()`

**Behavior:**
- If `amend` in `input.options`: add `--amend` to `git commit` args
- Pass `amend=True` to `validate_files()` — enables HEAD file acceptance
- Submodule amend: `_git("-C", path, "commit", "--amend", "-m", message)` then re-stage pointer
- Message always provided (never `--no-edit`)

**Changes:**
- File: `src/claudeutils/session/commit/pipeline.py`
  Action: Add amend flag handling throughout pipeline

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_session_commit_pipeline.py -v`
**Verify no regression:** `just precommit`

---
