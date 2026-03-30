# Cycle 1.3: Submodule CleanFileError Paths [2026-03-24]

## Execution Summary

**Status:** RED_VERIFIED (REGRESSION)

This cycle verifies that submodule file paths in CleanFileError include the full path with submodule prefix (e.g., `agent-core/fragments/foo.md`), not just the relative path (e.g., `fragments/foo.md`).

The test passes, confirming the expected behavior is already in place (regression case per `[REGRESSION]` marker in cycle spec).

## RED Phase

**Test:** `test_submodule_clean_error_shows_full_path` (test_session_commit_pipeline.py)

**Test Command:** `just test tests/test_session_commit_pipeline.py::test_submodule_clean_error_shows_full_path -v`

**RED Result:** PASS (expected for regression)

- Test creates a git repo with a submodule (`agent-core`)
- Creates a clean file in the submodule (`agent-core/fragments/foo.md`)
- Calls `commit_pipeline` with the submodule file in the file list
- Verifies `CleanFileError` is raised with the full path including `agent-core` prefix

**Why Regression:** Cycle spec includes `[REGRESSION]` marker, indicating the fix was already applied in a prior session. Test passes on first run, confirming the behavior is correct.

## GREEN Phase

**Status:** SKIPPED

No GREEN phase needed for regression tests. The test passing confirms correct behavior.

## REFACTOR Phase

**Linting:** Fixed import order in test_session_commit_pipeline.py

**Changes:**
- Moved `from unittest.mock import patch` to top-level imports (test_session_commit.py)
- Reordered imports to follow alphabetical convention (test_session_commit_pipeline.py)
- Removed duplicate test setup code by relocating test from test_session_commit.py to test_session_commit_pipeline.py (avoids file size limit issues)

**Precommit Status:** Passed (after import fixes)

**Final Commit:** `Cycle 1.3: Submodule CleanFileError paths (m-1)` (f07d7240)

## Files Modified

- `tests/test_session_commit_pipeline.py` — Added regression test for submodule CleanFileError path handling

## Stop Condition

None. Cycle completed successfully.

## Decision Made

**Test Location:** Placed in `test_session_commit_pipeline.py` rather than `test_session_commit.py` because:
1. Tests the commit pipeline's submodule handling behavior
2. Avoids exceeding 400-line file limit in test_session_commit.py
3. Aligns with module organization (commit_pipeline module tests in commit_pipeline test file)

## Notes

The cycle finding (m-1) from the RC10 deliverable review describes a bug where submodule file paths in CleanFileError would lack the repo context. The test verifies that paths include the full `agent-core/fragments/foo.md` format. Since the test passes, the fix is already in place (likely applied in a prior session). This confirms the expected behavior without requiring new implementation.
