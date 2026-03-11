# Cycle 4.7

**Plan**: `plans/handoff-cli-tool/runbook.md`
**Execution Model**: sonnet
**Phase**: 4

---

## Phase Context

Stdin parsing, session.md writes, committed detection, state caching, diagnostics.

---

---

**GREEN Phase:**

**Implementation:** Create `src/claudeutils/session/handoff/cli.py` with Click command, wire full pipeline

**Behavior:**
- `@click.command(name="handoff")` function
- Read stdin (if available) → `parse_handoff_input()`
- If no stdin: check for state file → `load_state()` → resume
- If no stdin and no state: `_fail("**Error:** No input on stdin and no state file", code=2)`
- Fresh pipeline: parse → save_state → overwrite_status → write_completed → run_precommit → diagnostics → clear_state
- Resume: load state → skip to `step_reached` → continue pipeline
- On precommit failure: output result + diagnostics, leave state file, exit 1

**Changes:**
- File: `src/claudeutils/session/handoff/cli.py`
  Action: Create with `handoff` Click command orchestrating full pipeline
- File: `src/claudeutils/session/cli.py`
  Action: Register: `from claudeutils.session.handoff.cli import handoff; session_group.add_command(handoff)`

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_session_handoff.py -v`
**Verify no regression:** `just precommit`

---

**Phase 4 Checkpoint:** `just precommit` — handoff subcommand fully functional.
