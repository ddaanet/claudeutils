# Cycle 4.2

**Plan**: `plans/worktree-update/runbook.md`
**Execution Model**: haiku
**Phase**: 4

---

## Cycle 4.2: Section filtering — Blockers and Reference Files

**Objective:** Include only blockers/gotchas and reference file entries relevant to the extracted task.

**Prerequisite:** Read `agents/session.md` Blockers/Gotchas and Reference Files sections — understand entry format and how entries reference tasks or plan directories.

**RED Phase:**

**Test:** `test_focus_session_section_filtering`
**Assertions:**
- Given session.md with Blockers/Gotchas section containing:
  - Entry mentioning task name directly
  - Entry mentioning task's plan directory (e.g., `plans/feature-x/`)
  - Entry NOT related to task
- And Reference Files section containing:
  - Entry relevant to task (mentions task name or plan directory)
  - Entry NOT relevant to task
- `focus_session("task-name", session_path)` returns string containing only relevant blocker and reference entries
- Unrelated entries NOT included in output
- Blockers section header present only if relevant entries exist
- Reference Files section header present only if relevant entries exist
- If no relevant blockers: Blockers section omitted entirely
- If no relevant references: Reference Files section omitted entirely

**Expected failure:** AssertionError: all entries included (no filtering) or sections always included even when empty

**Why it fails:** Function doesn't filter blockers or references yet, includes everything or nothing

**Verify RED:** `pytest tests/test_worktree_cli.py::test_focus_session_section_filtering -v`

---

**GREEN Phase:**

**Implementation:** Add section filtering logic to `focus_session()` function

**Behavior:**
- Parse Blockers/Gotchas section from session.md
- Parse Reference Files section from session.md
- For each entry in both sections, check if it mentions:
  - Task name (exact match or substring)
  - Plan directory associated with task (if task has plan metadata)
- Include only matching entries in focused session
- Omit each section entirely if no relevant entries

**Approach:** Section parsing, relevance checking per entry, conditional section inclusion. Same filtering logic applies to both Blockers and References sections.

**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Add section parsing to `focus_session()` function for both Blockers and References
  Location hint: After task extraction, before building output string
- File: `src/claudeutils/worktree/cli.py`
  Action: Implement relevance check — search for task name or plan directory in entry text
  Location hint: Shared filter function applied to both sections
- File: `src/claudeutils/worktree/cli.py`
  Action: Conditionally include each section in output (only if filtered list non-empty)
  Location hint: String formatting with conditional sections

**Verify GREEN:** `pytest tests/test_worktree_cli.py::test_focus_session_section_filtering -v`
- Must pass

**Verify no regression:** `pytest tests/test_worktree_cli.py::test_focus_session_task_extraction -v`
- Cycle 4.1 test still passes

---
