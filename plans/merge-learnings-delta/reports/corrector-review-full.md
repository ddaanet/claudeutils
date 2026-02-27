# Review: merge-learnings-delta full deliverable

**Scope**: All changed files on `merge-learnings-delta` vs `main`
**Date**: 2026-02-27
**Mode**: review + fix

## Summary

The deliverable implements FR-1 test coverage (9 tests across 3 classes for consolidation scenarios) and FR-2 reporting (`click.echo` summary line in `remerge_learnings_md()`). The production change is minimal and correct. Tooling refactoring (justfile, fixtures) is clean. All tests pass via `just precommit`. No critical issues.

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

None.

### Major Issues

None.

### Minor Issues

1. **`_git` local function shadows same name imported into `remerge.py` production module**
   - Location: `tests/test_learnings_consolidation.py:21`
   - Note: The test file defines `def _git(repo: Path, *args: str) -> None:` which is a module-level helper with a different signature from `claudeutils.worktree.git_ops._git`. These are in different modules so there is no actual shadowing at runtime. However, it duplicates the pattern from `fixtures_worktree._run_git` — a named helper that already does the same thing. The existing `_run_git` in fixtures_worktree raises on failure (same behavior) but returns the `CompletedProcess`. The test's `_git` is equivalent and idiomatic for the file. This is acceptable given it's a private test helper in a standalone file; no change needed. Noting for completeness only.
   - **Status**: OUT-OF-SCOPE — local helper in test file with different signature; no collision at runtime. Pattern is consistent with `tests/test_worktree_remerge_session.py` which also defines a local `_git`.

2. **`from _pytest.monkeypatch import MonkeyPatch` private import**
   - Location: `tests/test_learnings_consolidation.py:8`
   - Note: This imports from `_pytest`, a private implementation module. The public API is `pytest.MonkeyPatch` (available since pytest 6.2). Several existing test files already use the same `_pytest.monkeypatch.MonkeyPatch` import pattern. This is consistent with codebase convention.
   - **Status**: OUT-OF-SCOPE — pattern matches existing test files (`test_worktree_merge_errors.py`, `test_worktree_remerge_session.py`, `test_worktree_merge_session_resolution.py`). Not a regression introduced by this branch.

3. **`dropped` count logic counts theirs-only entries that ours didn't have either**
   - Location: `src/claudeutils/worktree/remerge.py:69-73`
   - Note: The dropped counter is:
     ```python
     dropped = sum(
         1
         for h in theirs_segs
         if h != "" and h in base_segs and h not in merged_segments
     )
     ```
     This correctly counts entries that were: in theirs, in base (not new on theirs), and not in final merge. This is the set that ours removed (consolidation). The guard `h in base_segs` correctly excludes entries that were genuinely new on theirs (those would be appended, not dropped). Logic is correct.
   - **Status**: OUT-OF-SCOPE — logic is correct; noting for documentation only.

4. **`_populate_branch` in `fixtures_worktree.py` is module-level but named with underscore convention**
   - Location: `tests/fixtures_worktree.py:99`
   - Note: `_populate_branch` is a private helper function extracted from `make_repo_with_branch`. It is not a pytest fixture (no `@pytest.fixture`), cannot shadow fixtures, and doesn't conflict with any existing fixture names. The refactor correctly eliminates the `PLR0913` suppression. Clean.
   - **Status**: OUT-OF-SCOPE — correct refactor, no issues.

## Fixes Applied

No fixes were needed. All issues identified are OUT-OF-SCOPE informational notes.

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| FR-1: 5 consolidation scenario tests | Satisfied | `TestConsolidationScenarios` (5 tests): consolidation+new, consolidation-only, modified-consolidated-away, modified-surviving, no-consolidation |
| FR-1: both merge directions | Satisfied | `TestConsolidationIntegration` (2 tests): `test_branch_to_main_consolidation`, `test_main_to_branch_consolidation` |
| FR-1: real git repos with tmp_path | Satisfied | Integration class uses `init_repo` fixture + `tmp_path` + real subprocess git |
| FR-2: `learnings.md: kept N + appended M new (dropped K consolidated)` | Satisfied | `remerge.py:75-78`; format matches exactly |
| FR-2: `click.echo` consistent with existing merge reporting | Satisfied | stdout (not stderr) via `click.echo` |
| FR-2: silent on noop | Satisfied | `if appended > 0 or dropped > 0:` guard; `test_silent_on_noop` verifies |
| NFR-1: no merge failure | Satisfied | Reporting code runs after `write_text` + `git add`; no new exception paths |
| NFR-2: no new dependencies | Satisfied | Only uses `click` (already a dependency) and existing `parse_segments` |

**Gaps**: None.

---

## Positive Observations

- `BranchSpec` dataclass cleanly replaces the 5-parameter keyword argument explosion. All callers updated consistently across `test_worktree_merge_correctness.py`, `test_worktree_rm_guard.py`.
- The `_populate_branch` extraction correctly inverts the `if/elif/else` chain without reordering semantics — the default case (`else: write file.txt`) is preserved.
- Reporting counts in `remerge.py` are computed post-write using the already-materialized segment dicts — no additional parsing or git calls. Zero overhead on the merge path.
- `dropped` correctly uses `h in base_segs` as a discriminator: entries new on theirs (not in base) that weren't appended would be a diff3 bug, not a consolidation — this guard prevents false positives in that edge case.
- Hook tests correctly relaxed assertions from exact bracket-prefixed strings (`[DISCUSS]`, `[PENDING]`) to case-insensitive substring (`"discuss" in ... .lower()`), improving tolerance to wording changes without losing behavioral coverage.
- `TestMergeReporting.test_reports_counts_when_segments_change` uses `capsys` correctly — `click.echo` without `err=True` writes to stdout, which `capsys.readouterr().out` captures.
- `test_validate_runbook.py` fixture-based refactor (`run_validate`, `run_validate_with_args`) eliminates repeated `monkeypatch`/`tmp_path` threading through 12 test functions. The `_RunValidateFn` type alias makes the fixture type self-documenting.
- Justfile `red-lint` recipe correctly omits `run-pytest` — only `run-lint-checks` — enabling the TDD RED gate without running the full test suite.
- Sentinel hash extension (`agent-core/hooks/ agent-core/bin/`) correctly invalidates test cache when hook scripts change, closing the gap where hook behavior changes weren't caught.
