# TDD Runbook Review: Worktree Skill Phase 3

**Artifact**: `plans/worktree-skill/runbook-phase-3.md`
**Date**: 2026-02-10T22:45:00Z
**Mode**: review + fix-all

## Summary

Phase 3 implements merge orchestration and source conflicts with 13 cycles covering clean tree gates, 3-phase submodule resolution, parent merge with session/source conflicts, precommit validation, idempotency, and fallback strategies. This is the highest-complexity phase in the worktree skill implementation.

- Total cycles: 13
- Issues found: 0 critical, 2 major, 3 minor
- Issues fixed: 5
- Unfixable (escalation required): 0

**Overall Assessment**: Ready

## Critical Issues

None found.

## Major Issues

### Issue 1: Vague prose in Cycle 3.11 RED
**Location**: Cycle 3.11, line 161
**Problem**: Expected return value used example file list `["src/claudeutils/worktree/cli.py", "tests/test_worktree_cli.py"]` which are specific files that depend on test fixture rather than general behavioral specification
**Fix**: Changed to "Function returns list of resolved files (exact file paths depend on test fixture — verify list contains all conflicted files excluding session context patterns)"
**Status**: FIXED

### Issue 2: Heading format inconsistency (cycles 3.11-3.13)
**Location**: Cycles 3.11, 3.12, 3.13
**Problem**: Used `**RED:**` and `**GREEN:**` without standard suffixes "— Behavioral Verification" / "— Behavioral Description" used consistently in cycles 3.1-3.10
**Fix**: Added standard suffixes to all three cycles for consistency
**Status**: FIXED

## Minor Issues

None beyond the heading inconsistencies addressed in Major Issue 2.

## Fixes Applied

- Cycle 3.11 RED: Made expected return value more general (test-fixture-agnostic)
- Cycle 3.11 RED: Added "— Behavioral Verification" suffix
- Cycle 3.11 GREEN: Added "— Behavioral Description" suffix
- Cycle 3.12 RED: Added "— Behavioral Verification" suffix
- Cycle 3.12 GREEN: Added "— Behavioral Description" suffix
- Cycle 3.13 RED: Added "— Behavioral Verification" suffix
- Cycle 3.13 GREEN: Added "— Behavioral Description" suffix

## Unfixable Issues (Escalation Required)

None — all issues fixed.

## Alignment with Outline

Phase 3 accurately implements the outline's Cycle 3.1-3.13 specifications:
- FR-2 (submodule resolution) fully covered in cycles 3.2-3.5
- FR-3 (session conflicts) covered in cycle 3.7
- FR-4 (source conflicts) covered in cycles 3.11-3.13
- NFR-1 (idempotent merge) covered in cycle 3.9
- NFR-2 (deterministic session resolution) covered in cycle 3.7
- NFR-3 (direct git plumbing) evident throughout (no /commit skill)
- NFR-4 (mandatory precommit) covered in cycles 3.8, 3.12, 3.13

## Recommendations

1. **Test fixture dependencies**: Cycles 3.1-3.13 reference files from Phase 2 (`src/claudeutils/worktree/conflicts.py`, `src/claudeutils/worktree/merge.py`). Executor must verify Phase 2 completion before starting Phase 3.

2. **Integration test emphasis**: All cycles use real git repos with actual merge states (not mocks). This is correct per outline's "E2E test strategy" and design decision D-8 (idempotency requires real state detection).

3. **Precommit as oracle**: Cycles 3.12-3.13 implement the heuristic resolution pattern with precommit as mechanical validator. This correctly implements D-4 (precommit oracle) — no agent judgment, mechanical validation only.

4. **Checkpoint requirement**: This phase has "full checkpoint" designation in outline. After Phase 3 completion, delegate to vet-fix-agent for comprehensive review before proceeding to Phase 4.

5. **Cycle granularity is appropriate**: 13 cycles for this complexity is well-scoped. Each cycle tests a distinct behavioral path (no-divergence, fast-forward, diverged commits, clean merge, session conflicts, source conflicts, precommit pass, precommit fail with fallback). No consolidation opportunities detected.

---

**Ready for next step**: Yes

