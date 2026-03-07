# Cycle 4.5

**Plan**: `plans/handoff-cli-tool/runbook.md`
**Execution Model**: sonnet
**Phase**: 4

---

## Phase Context

Stdin parsing, session.md writes, committed detection, state caching, diagnostics.

---

---

**GREEN Phase:**

**Implementation:** Add `run_precommit()` to `session/handoff/pipeline.py`

**Behavior:**
- `PrecommitResult` dataclass: `success: bool`, `output: str`
- `run_precommit() -> PrecommitResult` — `subprocess.run(["just", "precommit"], capture_output=True, text=True, check=False)`. Return success based on returncode.

**Changes:**
- File: `src/claudeutils/session/handoff/pipeline.py`
  Action: Add `PrecommitResult`, `run_precommit()`

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_session_handoff.py -v`
**Verify no regression:** `just precommit`

---
