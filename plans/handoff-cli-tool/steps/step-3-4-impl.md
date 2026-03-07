# Cycle 3.4

**Plan**: `plans/handoff-cli-tool/runbook.md`
**Execution Model**: sonnet
**Phase**: 3

---

## Phase Context

Pure data transformation: session.md + filesystem state → STATUS output. No mutations, no stdin.

---

---

**GREEN Phase:**

**Implementation:** Create `src/claudeutils/session/status/cli.py` with Click command, register in session group

**Behavior:**
- `@click.command(name="status")` function
- Read `agents/session.md` (cwd-relative) → `parse_session()`
- Call `claudeutils _worktree ls` via subprocess for plan states
- Parse `_worktree ls` output for plan status: lines matching `  Plan: {name} [{status}] → ...` — extract name and status into a dict `{name: status}` passed to `render_pending()`
- Call render functions (Next, Pending, Worktree, Unscheduled, Parallel)
- Concatenate non-empty sections with blank line separators
- Output to stdout, exit 0
- Missing session.md → `_fail("**Error:** Session file not found: agents/session.md", code=2)`

**Changes:**
- File: `src/claudeutils/session/status/cli.py`
  Action: Create with `status` Click command
- File: `src/claudeutils/session/cli.py`
  Action: Import and register: `from claudeutils.session.status.cli import status; session_group.add_command(status)`

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_session_status.py -v`
**Verify no regression:** `just precommit`

---

**Phase 3 Checkpoint:** `just precommit` — status subcommand fully functional.
