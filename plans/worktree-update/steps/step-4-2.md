# Cycle 4.2

**Plan**: `plans/worktree-update/runbook.md`
**Execution Model**: haiku
**Phase**: 4

---

## Cycle 4.2: Blockers filtering — relevant entries only

**Objective:** Include only blockers/gotchas relevant to the extracted task.

**Prerequisite:** Read `agents/session.md` Blockers/Gotchas section — understand entry format and how entries reference tasks or plan directories.

**RED Phase:**

**Test:** `test_focus_session_blockers_filtering`
**Assertions:**
- Given session.md with Blockers/Gotchas section containing:
  - Entry mentioning task name directly
  - Entry mentioning task's plan directory (e.g., `plans/feature-x/`)
  - Entry NOT related to task
- `focus_session("task-name", session_path)` returns string containing only relevant blocker entries
- Unrelated blocker entries NOT included in output
- Blockers section header present only if relevant entries exist
- If no relevant blockers: section omitted entirely

**Expected failure:** AssertionError: all blockers included (no filtering) or blockers section always included even when empty

**Why it fails:** Function doesn't filter blockers yet, includes everything or nothing

**Verify RED:** `pytest tests/test_worktree_cli.py::test_focus_session_blockers_filtering -v`

---

**GREEN Phase:**

**Implementation:** Add blocker filtering logic to `focus_session()` function

**Behavior:**
- Parse Blockers/Gotchas section from session.md
- For each blocker entry, check if it mentions:
  - Task name (exact match or substring)
  - Plan directory associated with task (if task has plan metadata)
- Include only matching entries in focused session
- Omit Blockers section entirely if no relevant entries

**Approach:** Section parsing, relevance checking per entry, conditional section inclusion

**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Add blocker parsing to `focus_session()` function
  Location hint: After task extraction, before building output string
- File: `src/claudeutils/worktree/cli.py`
  Action: Implement relevance check — search for task name or plan directory in blocker text
  Location hint: Filter blocker lines by content matching
- File: `src/claudeutils/worktree/cli.py`
  Action: Conditionally include Blockers section in output (only if filtered list non-empty)
  Location hint: String formatting with conditional section

**Verify GREEN:** `pytest tests/test_worktree_cli.py::test_focus_session_blockers_filtering -v`
- Must pass

**Verify no regression:** `pytest tests/test_worktree_cli.py::test_focus_session_task_extraction -v`
- Cycle 4.1 test still passes

---
