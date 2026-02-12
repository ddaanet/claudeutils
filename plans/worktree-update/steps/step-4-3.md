# Cycle 4.3

**Plan**: `plans/worktree-update/runbook.md`
**Execution Model**: haiku
**Phase**: 4

---

## Cycle 4.3: Reference files filtering — relevant entries only

**Objective:** Include only reference file entries relevant to the extracted task.

**RED Phase:**

**Test:** `test_focus_session_references_filtering`
**Assertions:**
- Given session.md with Reference Files section containing:
  - Entry relevant to task (mentions task name or plan directory)
  - Entry NOT relevant to task
- `focus_session("task-name", session_path)` returns string containing only relevant reference entries
- Unrelated reference entries NOT included
- Reference Files section header present only if relevant entries exist
- If no relevant references: section omitted entirely

**Expected failure:** AssertionError: all references included (no filtering) or references section missing entirely

**Why it fails:** Function doesn't filter references yet

**Verify RED:** `pytest tests/test_worktree_cli.py::test_focus_session_references_filtering -v`

---

**GREEN Phase:**

**Implementation:** Add reference files filtering logic to `focus_session()` function

**Behavior:**
- Parse Reference Files section from session.md
- For each reference entry, check if it mentions:
  - Task name
  - Plan directory associated with task
- Include only matching entries in focused session
- Omit Reference Files section entirely if no relevant entries

**Approach:** Same pattern as blocker filtering — parse section, filter by relevance, conditional inclusion

**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Add reference file parsing to `focus_session()` function
  Location hint: After blocker filtering, before building output string
- File: `src/claudeutils/worktree/cli.py`
  Action: Implement relevance check for references (same logic as blockers)
  Location hint: Filter reference lines by content matching
- File: `src/claudeutils/worktree/cli.py`
  Action: Conditionally include Reference Files section in output
  Location hint: String formatting with conditional section

**Verify GREEN:** `pytest tests/test_worktree_cli.py::test_focus_session_references_filtering -v`
- Must pass

**Verify no regression:** `pytest tests/test_worktree_cli.py -v`
- All Cycle 4.1 and 4.2 tests still pass

---
