# Cycle 4: Delete old functions, update imports

**Timestamp:** 2026-02-28

## Status
GREEN_VERIFIED

## Summary
Successfully deleted obsolete functions (`move_task_to_worktree`, `remove_worktree_task`, `_task_is_in_pending_section`, `_find_git_root`) and replaced them with new functions (`add_slug_marker`, `remove_slug_marker`). All tests updated to reflect new behavior. Full test suite passes.

## RED Phase
- **Expected Failure:** Tests importing deleted functions fail with ImportError
- **Actual Result:** Test collection failed with ImportError as expected
  - `test_worktree_session.py`: Cannot import `move_task_to_worktree`
  - `test_worktree_session_remove.py`: Cannot import `remove_worktree_task`
  - `test_worktree_new_creation.py`: Cannot import `move_task_to_worktree`
- **Verified:** RED phase confirmed

## GREEN Phase

### Changes Made

**Source Files:**
1. `/src/claudeutils/worktree/session.py`
   - Deleted `move_task_to_worktree()` function (66 lines)
   - Deleted `_find_git_root()` helper function (9 lines)
   - Deleted `_task_is_in_pending_section()` helper function (13 lines)
   - Deleted `remove_worktree_task()` function (46 lines)

2. `/src/claudeutils/worktree/cli.py`
   - Updated imports: replaced `move_task_to_worktree`, `remove_worktree_task` with `add_slug_marker`, `remove_slug_marker`
   - Updated `new()` function: replaced `move_task_to_worktree()` call with `add_slug_marker()`
   - Replaced `_update_session_and_amend()` with simplified `_update_session()`:
     - Removed merge commit amending logic
     - Now only calls `remove_slug_marker()` to update session.md
   - Updated `rm()` function: replaced `_update_session_and_amend(slug)` with `_update_session(slug)`
   - Removed amend note from output

**Test Files:**
1. `/tests/test_worktree_session.py`
   - Removed import of `move_task_to_worktree`
   - Deleted 4 test functions: `test_move_task_to_worktree_single_line`, `test_move_task_to_worktree_slug_marker`, `test_move_task_to_worktree_creates_section`, `test_move_task_to_worktree_multiline`

2. `/tests/test_worktree_session_remove.py`
   - **DELETED ENTIRELY** (all 3 tests tested `remove_worktree_task()`)

3. `/tests/test_worktree_session_automation.py`
   - Renamed `test_new_task_mode_moves_task_to_worktree` → `test_new_task_mode_adds_slug_marker`
   - Updated assertions to verify slug marker is added (not task moved)
   - Updated session.md setup to have task already in Worktree Tasks section
   - Renamed `test_rm_calls_remove_worktree_task_before_branch_delete` → `test_rm_removes_slug_marker`
   - Updated to verify marker removal instead of task removal
   - Renamed `test_rm_e2e_removes_completed_task_from_worktree_tasks` → `test_rm_e2e_slug_marker_removal`
   - Updated to verify marker removal and task preservation

4. `/tests/test_worktree_rm.py`
   - Renamed `test_rm_amends_merge_commit_when_session_modified` → `test_rm_removes_slug_marker_from_session`
   - Updated test to verify marker removal (not amending)
   - **DELETED** `test_rm_output_indicates_amend` (tested old amending behavior)

5. `/tests/test_worktree_new_creation.py`
   - Removed import of `move_task_to_worktree`
   - Updated `test_new_task_name_with_branch_override` to mock `add_slug_marker` instead of `move_task_to_worktree`
   - Updated `test_new_positional_task_name_derives_slug_with_session` to mock `add_slug_marker`
   - Updated `test_new_task_commits_session_md`: task now in Worktree Tasks section

6. `/tests/test_worktree_commands.py`
   - Updated `test_task_mode_integration`: task now in Worktree Tasks section

7. `/tests/test_worktree_new_config.py`
   - Updated `test_new_positional_task_name`: task now in Worktree Tasks section

### Test Results
- **Initial RED phase:** 3 collection errors (ImportError from deleted functions)
- **After fixes:** 1366/1367 passed, 1 xfail (known bug)
- **All assertions pass:** Tests verify new behavior (marker addition/removal)

## Refactoring

### Code Quality Checks
- **Lint:** PASS (all formatting correct)
- **Precommit:** PASS (no violations)
- **Test Sentinel:** Cache used (tests unchanged except for behavioral updates)

### Changes from Quality Checks
- Fixed docstring formatting in `test_rm_removes_slug_marker_from_session` (added blank line between summary and description)
- All imports organized correctly

## Files Modified
1. `src/claudeutils/worktree/session.py` (deletions: 134 lines)
2. `src/claudeutils/worktree/cli.py` (modified imports, simplified _update_session)
3. `tests/test_worktree_session.py` (removed 4 test functions)
4. `tests/test_worktree_session_remove.py` (deleted file)
5. `tests/test_worktree_session_automation.py` (updated 3 tests)
6. `tests/test_worktree_rm.py` (updated 1 test, deleted 1 test)
7. `tests/test_worktree_new_creation.py` (updated 4 tests, removed import)
8. `tests/test_worktree_commands.py` (updated 1 test)
9. `tests/test_worktree_new_config.py` (updated 1 test)

## Stop Condition
None. Cycle completed successfully.

## Architectural Decisions
- **Simplified rm() workflow:** Removed merge commit amending logic. Session.md updates are now handled separately from git operations.
- **Task location assumption:** Tasks being operated on must already exist in Worktree Tasks section (enforced by add_slug_marker ValueError).
- **Slug marker lifecycle:** Markers are added when worktree is created (`new` command) and removed when worktree is removed (`rm` command).

## Notes
- All deleted functions were single-use wrappers around the new functions
- Old behavior (move from Pending to Worktree) is replaced by new workflow where tasks are manually moved before calling `new`
- Tests now verify marker-based tracking instead of section-based movement
