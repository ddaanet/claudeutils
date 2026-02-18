# Runbook Review: Phase 4 — Conflict context output

**Artifact**: `plans/worktree-merge-resilience/runbook-phase-4.md`
**Date**: 2026-02-18T00:00:00Z
**Mode**: review + fix-all
**Phase types**: TDD (1 cycle)

## Summary

Phase 4 is a single-cycle TDD phase that adds `_format_conflict_report` to `merge.py` and calls it from both conflict exit sites. The cycle is well-structured: GREEN avoids prescriptive code, RED assertions are mostly concrete, and the cross-phase dependency on Phase 3 is correctly stated. Two minor issues fixed: (1) divergence assertion was too loose — matched any digit + "commit" substring including diff stat lines, (2) "Why it fails" described the pre-Phase-3 state rather than the Phase 3 post-implementation state that Phase 4 actually builds on.

**Overall Assessment**: Ready

## Critical Issues

None.

## Major Issues

None.

## Minor Issues

### Issue 1: Divergence assertion too loose

**Location**: Cycle 4.1, RED Phase, Assertions, bullet 4 (line 35)
**Problem**: Assertion required "a line with commit count pattern — e.g., `'commits on branch'` or digit followed by `' commit'`". This is ambiguous — a diff stat line like `src/feature.py | 3 +++` contains a digit and could be misread as satisfying the pattern. The GREEN description specifies the exact format: `"Branch: N commits ahead, Main: M commits ahead since merge-base"`. The RED assertion must be tight enough that only the correct format satisfies it, not adjacent output fields.
**Fix**: Replaced with format-anchored assertion: line starting with `"Branch: "` followed by a digit. Includes a concrete example matching the GREEN format spec.
**Status**: FIXED

### Issue 2: "Why it fails" describes pre-Phase-3 state

**Location**: Cycle 4.1, RED Phase, "Why it fails" (line 40)
**Problem**: "call sites use simple `click.echo` of file names only" describes the state of `merge.py` before Phase 3 is implemented. Phase 4 depends on Phase 3 (stated in the Depends-on line). By the time an executor reaches Phase 4, the call sites will have been changed by Phase 3 — they will emit file names and exit 3, not exit 1 with a simple echo. The description also omits the collection error that occurs first (test doesn't exist yet).
**Fix**: Updated to describe the Phase 3 post-implementation state. Clarified two-stage failure: test doesn't exist (collection error first), then once written, fails on missing diff stats / divergence / hint fields.
**Status**: FIXED

## File Reference Validation

- `src/claudeutils/worktree/merge.py` — exists, confirmed
- `tests/test_worktree_merge_conflicts.py` — exists, confirmed
- `test_conflict_output_contains_all_fields` — does NOT exist in test file (correct: this is the RED phase test to be written)
- `_format_git_error` at merge.py line 15 — confirmed; GREEN location hint "after `_format_git_error`" is valid
- `mock_precommit` fixture — exists in `tests/fixtures_worktree.py`, confirmed
- `_phase3_merge_parent` if-conflicts block — exists at merge.py lines 170-175, confirmed
- `parent_conflicts` branch in `merge()` — Phase 1 creates this routing stub (cross-phase dependency, correctly stated)

## RED Plausibility Check

**Cycle 4.1:** `test_conflict_output_contains_all_fields` does not exist in `tests/test_worktree_merge_conflicts.py` — pytest will raise a collection error (no such test). RED will fail. Once the test is written (per GREEN), Phase 3 will have changed the conflict exit path to exit 3 with file names only. The diff stat, divergence, and hint assertions will all fail against Phase 3's output. RED is plausible.

**Cross-phase dependency check:** Phase 4 requires Phase 3 Cycle 3.1 to have implemented (a) the `parent_conflicts` routing stub in `merge()` and (b) the conflict-preserving exit with code 3 in `_phase3_merge_parent`. The Depends-on line states this explicitly. The test setup's "Assert exit_code == 3" (step 4) will fail until Phase 3 is complete — correct sequencing.

## LLM Failure Mode Checks

**Vacuity:** Single cycle, single behavioral outcome (all FR-4 fields in output). No scaffolding-only items. Not vacuous.

**Dependency ordering:** One cycle — no intra-phase ordering to validate. Cross-phase dependency stated explicitly in Depends-on.

**Density:** Single cycle implementing a new formatting function — appropriate granularity. FR-4 has 4 distinct output fields; collapsing further would produce an unverifiable RED.

**Checkpoint spacing:** Phase 3 is the prior checkpoint. Phase 4 is 1 cycle. No checkpoint gap issue.

**File growth:** `merge.py` is currently 263 lines. Adding `_format_conflict_report` with git subprocess calls across 4 fields will add approximately 25-35 lines — projected ~290-300 lines, well below the 350-line flag threshold.

**Model assignment:** No explicit model tag. Phase edits `merge.py` (not a skill/fragment/agent file) with a git-querying function. Moderate complexity, consistent with sonnet. No advisory flag needed.

## Fixes Applied

- Cycle 4.1, RED Phase, Assertions bullet 4 — tightened divergence assertion to require `"Branch: "` prefix matching the GREEN format spec, eliminating ambiguity with diff stat lines
- Cycle 4.1, RED Phase, "Why it fails" — updated to describe Phase 3 post-implementation state (exits 3 with file names, no rich fields), added two-stage failure description (collection error first, field assertion failure second)

## Unfixable Issues (Escalation Required)

None — all issues fixed.

---

**Ready for next step**: Yes
