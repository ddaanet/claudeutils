# Runbook Review: Phase 3 — Parent merge preservation + untracked handling

**Artifact**: `plans/worktree-merge-resilience/runbook-phase-3.md`
**Date**: 2026-02-18T00:00:00Z
**Mode**: review + fix-all
**Phase types**: TDD (2 cycles)

## Summary

Phase 3 covers two behavioral changes to `_phase3_merge_parent`: removing the abort block (Cycle 3.1, FR-2/NFR-2) and adding untracked-file `git add` + retry logic (Cycle 3.2, FR-3/D-4). The RED phase assertions are behaviorally specific and correctly plausible against the current implementation. GREEN phases describe behavior without prescriptive code.

One major issue found: the new success-path test (Test B, Cycle 3.2) reaches Phase 4 which calls `just precommit`, but the RED description omitted the `mock_precommit` fixture requirement. One minor issue: the Test A setup guidance incorrectly implied the test needs a content change when the existing content is already different.

**Overall Assessment**: Ready (all issues fixed)

## Findings

### Major Issues

1. **Test B missing `mock_precommit` fixture requirement**
   - Location: Cycle 3.2, RED Phase — `test_merge_untracked_file_same_content_auto_resolved`
   - Problem: Same-content untracked file auto-resolves, so `_phase3_merge_parent` returns normally and `_phase4_merge_commit_and_precommit` runs. Phase 4 calls `subprocess.run(["just", "precommit"], ...)`. Without `mock_precommit`, the test will fail with precommit subprocess failure (no justfile in the test repo). The common context says "Use `mock_precommit` for success-path tests" but the RED phase description omitted it, creating a silent trap for the executor.
   - Fix: Added "This is a success-path test: same-content auto-merge → Phase 4 runs → `just precommit` is called. Use `mock_precommit` fixture." before the Test B assertions.
   - **Status**: FIXED

### Minor Issues

1. **Test A setup guidance implies unnecessary change**
   - Location: Cycle 3.2, RED Phase — `test_merge_aborts_cleanly_when_untracked_file_blocks`
   - Problem: "Change the test setup so the untracked file on main has DIFFERENT content from the branch version" — the existing test already writes "# Untracked\n" on main vs "# Branch\n" on branch. The directive implies active modification where none is needed, risking the executor changing content unnecessarily or adding duplicate setup.
   - Fix: Replaced with "The existing test setup already has different content on main ('# Untracked\n') vs branch ('# Branch\n'). No setup change needed. Update assertions only."
   - **Status**: FIXED

## Fixes Applied

- Cycle 3.2 RED Phase (Test B) — added `mock_precommit` fixture requirement and explanation before assertions
- Cycle 3.2 RED Phase (Test A) — replaced "change the test setup" with "existing setup already has different content, update assertions only"

## RED Plausibility Verification

**Cycle 3.1 (`test_merge_conflict_surfaces_git_error`):**
Current code (lines 170-175): calls `_git("merge", "--abort")`, outputs "Merge aborted: conflicts in ...", raises `SystemExit(1)`.
- `exit_code == 3`: fails (currently 1) ✓
- MERGE_HEAD present: fails (`--abort` removes it) ✓
- `"aborted"` NOT in output: fails ("Merge aborted" is present) ✓
All assertions correctly fail RED.

**Cycle 3.2 Test A (`test_merge_aborts_cleanly_when_untracked_file_blocks`):**
Current code (lines 154-157): no-MERGE_HEAD → `click.echo(f"Merge failed: {stderr}", err=True)` + `raise SystemExit(1)`.
- `exit_code == 3`: fails (currently 1) ✓
- MERGE_HEAD exists: fails (git refused before starting, no MERGE_HEAD) ✓
- Conflict markers in file: fails (no merge attempted, file unchanged) ✓
All assertions correctly fail RED.

**Cycle 3.2 Test B (`test_merge_untracked_file_same_content_auto_resolved`):**
No existing test → test fails on collection (name not found) ✓

## LLM Failure Mode Analysis

- **Vacuity**: Both cycles test real behavioral changes (abort removal, untracked recovery). Not vacuous.
- **Dependency ordering**: Cycle 3.1 removes abort block; Cycle 3.2 adds detection in the separate no-MERGE_HEAD branch. These are independent code paths. Sequential order correct (abort removal first, then untracked detection after).
- **Density**: 2 cycles covering distinct failure modes (source conflict vs. merge refusal). No collapse warranted.
- **Checkpoint spacing**: Checkpoint after Cycle 3.1 (NFR-2 grep). 2 cycles total — spacing adequate.
- **File growth**: `merge.py` currently ~263 lines. Phase 3 adds ~15-20 lines (untracked detection + retry). No file growth concern.

## Unfixable Issues (Escalation Required)

None — all issues fixed.

---

**Ready for next step**: Yes
