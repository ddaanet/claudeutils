# Cycle 6.6

**Plan**: `plans/handoff-cli-tool/runbook.md`
**Execution Model**: sonnet
**Phase**: 6

---

## Phase Context

Staging, submodule coordination, amend semantics, structured output.

---

---

**GREEN Phase:**

**Implementation:** Create `src/claudeutils/session/commit/cli.py` with Click command

**Behavior:**
- `@click.command(name="commit")` function
- Read all stdin → `parse_commit_input()`
- Call `commit_pipeline(input)` → `CommitResult`
- Output `result.output` to stdout
- Exit 0 on success, 1 on pipeline error, 2 on input validation error

**Changes:**
- File: `src/claudeutils/session/commit/cli.py`
  Action: Create with `commit` Click command
- File: `src/claudeutils/session/cli.py`
  Action: Import and register the commit command with the session group (same pattern as worktree subcommand registration in main cli.py)

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_session_commit_pipeline.py -v`
**Verify no regression:** `just precommit`

---

**Phase 6 Checkpoint:** `just precommit` — commit subcommand fully functional.
