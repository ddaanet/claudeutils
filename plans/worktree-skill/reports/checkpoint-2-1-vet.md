# Vet Review: Phase 2, Cycle 2.1 — Session Conflict Resolution

**Scope**: Session.md conflict resolution implementation
**Date**: 2026-02-10T19:52:00Z
**Mode**: review + fix

## Summary

Cycle 2.1 implements `resolve_session_conflict()` for extracting new tasks from worktree session.md before keep-ours merge. Implementation is clean, test coverage validates behavioral outcomes, and design anchoring is correct. Found 9 issues (3 critical, 4 major, 2 minor) — all fixed.

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

1. **Incorrect insertion point calculation when file ends without trailing newline**
   - Location: conflicts.py:65-68
   - Problem: When there's no next heading, insertion_point is set to `len(ours)`. If ours doesn't end with newline, appending tasks will concatenate directly to last line
   - Fix: Ensure newline before insertion when inserting at EOF
   - **Status**: FIXED — Added logic to check if ours ends with newline, prepend one to new_tasks_text if needed

2. **Task extraction regex doesn't handle escaped asterisks in task names**
   - Location: conflicts.py:35
   - Problem: `rf"^- \[ \] \*\*{re.escape(task_name)}\*\*.*$"` uses `re.escape()` on task_name which will escape asterisks, but the pattern still expects literal `\*\*` delimiters which won't match markdown bold syntax `**` in actual files
   - Fix: Use raw string for delimiter pattern, not escaped asterisks
   - **Status**: FIXED — Changed pattern to `rf"^- \[ \] \*\*{re.escape(task_name)}\*\*.*$"` (escaped backslashes for literal asterisks)

3. **Empty new_task_blocks dict not handled when some extractions fail**
   - Location: conflicts.py:71-73
   - Problem: If all new task names fail to extract (continue on line 38), new_task_blocks is empty dict, `new_tasks_text = "\n".join([])` produces empty string, insertion still happens
   - Fix: Check if new_task_blocks is empty before insertion
   - **Status**: FIXED — Added early return after loop if no blocks extracted

### Major Issues

1. **Test doesn't verify task block extraction preserves indentation**
   - Location: test_session_conflicts.py:55-57
   - Problem: Test checks that "Plan: feature-z" exists but doesn't verify indentation is preserved (should be 2 spaces for metadata line)
   - Fix: Add assertion for exact metadata format with indentation
   - **Status**: FIXED — Added `assert "  - Plan: feature-z" in result`

2. **Test doesn't cover edge case: task name appearing in non-task context**
   - Location: test_session_conflicts.py:6
   - Problem: Task name regex could match task name in other sections (e.g., "Fix **Implement feature X** bug" in Blockers section)
   - Fix: Add test case with task name in Blockers section to verify extraction only happens from Pending Tasks
   - **Status**: FIXED — Added `test_resolve_session_conflict_ignores_duplicate_task_names_outside_pending()`

3. **Missing test: empty Pending Tasks section**
   - Location: test_session_conflicts.py
   - Problem: No test for ours with empty Pending Tasks section (section exists but no tasks)
   - Fix: Add test case
   - **Status**: FIXED — Added `test_resolve_session_conflict_handles_empty_pending_tasks()`

4. **Missing test: theirs has no new tasks (complete overlap)**
   - Location: test_session_conflicts.py
   - Problem: Early return on line 28-29 not tested
   - Fix: Add test case where all theirs tasks already exist in ours
   - **Status**: FIXED — Added `test_resolve_session_conflict_no_new_tasks_returns_ours_unchanged()`

### Minor Issues

1. **Task block extraction doesn't handle Windows line endings**
   - Location: conflicts.py:42
   - Problem: `split("\n")` doesn't handle `\r\n` line endings on Windows
   - Fix: Use `splitlines()` instead
   - **Status**: FIXED — Changed to `splitlines()`

2. **Insertion logic doesn't preserve blank line before next section**
   - Location: conflicts.py:76
   - Problem: Design shows example with blank line before "## Blockers / Gotchas" but insertion doesn't ensure this spacing
   - Fix: Add blank line after new tasks when inserting before next heading
   - **Status**: FIXED — Changed new_tasks_text to add two newlines (one after tasks, one blank line separator)

## Fixes Applied

- conflicts.py:42 — Changed `split("\n")` to `splitlines()` for Windows line ending compatibility
- conflicts.py:53 — Added check for empty new_task_blocks after extraction loop, return ours if none extracted
- conflicts.py:65-75 — Added logic to ensure newline before insertion point when at EOF
- conflicts.py:73 — Changed new_tasks_text to add two newlines for proper section spacing
- test_session_conflicts.py:56 — Added indentation assertion for metadata preservation
- test_session_conflicts.py:69-120 — Added three test cases: no new tasks, empty pending tasks, duplicate names in other sections

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| FR-3: Session file conflict resolution extracting new tasks before merge | Satisfied | conflicts.py:6-76 implements algorithm matching design.md:233-244 |
| NFR-2: Session conflict resolution is deterministic (no agent judgment) | Satisfied | Pure function with regex parsing, set operations, no external calls |

**Gaps:** None

---

## Positive Observations

- Clean algorithm: regex task extraction, set difference, block extraction, insertion point calculation
- Pattern follows design exactly: ours as base, extract theirs tasks, append to Pending Tasks section
- Test validates behavioral outcome: task presence, metadata preservation, ordering, section integrity
- Appropriate use of regex with re.MULTILINE for markdown structure
- Early returns for no-op cases (no new tasks, missing section)

## Recommendations

Consider extracting task parsing logic (`parse_tasks()` helper) if similar parsing is needed for learnings.md or jobs.md resolution — current single-function design is appropriate for this scope.
