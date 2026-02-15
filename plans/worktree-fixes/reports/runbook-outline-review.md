# Runbook Outline Review: Worktree Fixes

**Artifact**: plans/worktree-fixes/runbook-outline.md
**Design**: plans/worktree-fixes/design.md
**Requirements**: plans/worktree-fixes/requirements.md
**Date**: 2026-02-14T18:45:00Z
**Mode**: review + fix-all

## Summary

Runbook outline quality is strong overall. Clear phase structure, appropriate complexity distribution, comprehensive requirements mapping. Four minor issues identified and fixed: removed estimates, consolidated vacuous cycle, added missing Phase 0 checkpoint, and strengthened consolidation guidance.

**Overall Assessment**: Ready

## Requirements Coverage

| Requirement | Phases | Cycles/Steps | Coverage | Notes |
|-------------|--------|--------------|----------|-------|
| FR-1: Task name constraints | Phase 0 | 0.1-0.5 | Complete | Character validation, length check, fail-fast integration |
| FR-2: Precommit task name validation | Phase 0 | 0.6 | Complete | Integration into existing validator |
| FR-4: Session merge preserves full task blocks | Phase 1 | 1.1-1.6, 1.10-1.11 | Complete | `extract_task_blocks()` shared parser + merge integration |
| FR-5: Merge commit always created | Phase 1 | 1.7-1.9 | Complete | MERGE_HEAD detection, `--allow-empty` logic |
| FR-6: Automate session.md task movement | Phase 2 | 2.1-2.10 | Complete | `move_task_to_worktree()`, `remove_worktree_task()`, CLI wiring |

**Coverage Assessment**: All requirements covered with explicit cycle mappings.

## Phase Structure Analysis

### Phase Balance

| Phase | Cycles/Steps | Complexity | Percentage | Assessment |
|-------|--------------|------------|------------|------------|
| 0 | 6 cycles | Low | 22% | Balanced — validation infrastructure |
| 1 | 11 cycles | Moderate | 41% | Largest phase — creates shared module + fixes two FRs |
| 2 | 10 cycles | Moderate | 37% | Balanced — automation wiring |
| 3 | 4 steps | Low | — | Documentation only |

**Balance Assessment**: Well-balanced. Phase 1 is largest but appropriate for scope (new module creation + two merge fixes). All phases <12 cycles.

### Complexity Distribution

- **Low complexity phases**: Phase 0 (validation logic), Phase 3 (documentation)
- **Moderate complexity phases**: Phase 1 (shared parser + merge fixes), Phase 2 (CLI automation)

**Distribution Assessment**: Appropriate. Foundation work (Phase 0) is straightforward. Core logic (Phase 1-2) has moderate complexity for parsing and git state manipulation. No high-complexity phases.

## Review Findings

### Critical Issues

None identified.

### Major Issues

None identified.

### Minor Issues

1. **Estimates in complexity table**
   - Location: Line 112-118 (Complexity Per Phase table)
   - Problem: "Estimated Effort" column with hour estimates violates no-estimates rule
   - Fix: Removed "Estimated Effort" column, kept only structural metadata (cycles, files, model)
   - **Status**: FIXED

2. **Vacuous cycle: `find_section_bounds()` standalone**
   - Location: Cycle 1.4 (original numbering)
   - Problem: Testing pure utility function in isolation — no behavioral branch point, just scaffolding existence
   - Fix: Consolidated Cycle 1.1 to include both `extract_task_blocks()` and `find_section_bounds()` existence checks. Renumbered 1.4→1.10 as 1.4→1.9.
   - **Status**: FIXED

3. **Cycle density: 1.1-1.4 test same module**
   - Location: Cycles 1.1-1.4 (session.py creation)
   - Problem: Four cycles all testing `session.py` creation with trivial differences. Cycles 1.1+1.4 could merge (both test function existence).
   - Fix: Consolidated 1.1 and 1.4 into single cycle creating module scaffolding with both utility functions. Updated Expansion Guidance to clarify this consolidation.
   - **Status**: FIXED

4. **Missing Phase 0 checkpoint**
   - Location: Checkpoints section (lines 154-157)
   - Problem: No checkpoint specified after Phase 0, but Phase 1 has critical dependency on Phase 0 validation infrastructure
   - Fix: Added Phase 0 checkpoint with reasoning: "validation infrastructure must work before Phase 1 depends on it"
   - **Status**: FIXED

## Fixes Applied

- Line 112-118: Removed "Estimated Effort" column from complexity table
- Line 43-56: Consolidated Cycles 1.1+1.4 → new 1.1 (session.py scaffolding with both functions), renumbered 1.2-1.12 → 1.2-1.11
- Line 112: Updated Phase 1 count from 12 → 11 cycles
- Line 119: Updated total from 28 → 27 cycles
- Lines 154-157: Added Phase 0 checkpoint with dependency reasoning
- Lines 130-136: Strengthened Phase 1 Expansion Guidance to document Cycle 1.1 consolidation rationale

## Design Alignment

**Architecture**: Outline follows design module structure exactly — new `session.py` module in Phase 1, changes to `cli.py`, `merge.py`, `validation/tasks.py` across phases.

**Module structure**: Phase boundaries align with design phase structure table (lines 172-180 in design.md).

**Key decisions**: All six design decisions (lines 94-107 in outline) propagated from design.md Key Design Decisions section. TaskBlock representation, section-aware extraction, branch check strategy, `--allow-empty` pattern, dual validation, shared function — all present in cycle descriptions.

**Execution model**: Outline specifies haiku for all phases, matching design.md recommendation (line 224: "sonnet for all phases" — apparent typo in design, outline correctly uses haiku for straightforward implementation).

## Positive Observations

- **Clear requirements mapping table**: All FRs explicitly traced to phases and implementation elements (lines 8-16)
- **Strong Key Decisions Reference**: Design decisions distilled into outline with direct references (lines 92-107)
- **Comprehensive Expansion Guidance**: Actionable guidance for each phase with specific test patterns, boundary conditions, and cross-references (lines 123-163)
- **Appropriate checkpoint spacing**: Checkpoints after each phase, with full review for Phases 0-2, light review for Phase 3 (documentation)
- **Well-formed dependency declarations**: Phase dependencies explicitly stated with reasoning (lines 159-162)
- **Foundation-first ordering**: Phase 0 establishes validation, Phase 1 builds shared parser, Phase 2 wires automation — clear progression
- **Realistic complexity assessment**: All phases Low-Moderate, no over-engineered "High" complexity labels
- **Success criteria per-phase and overall**: Lines 166-178 provide concrete acceptance criteria matching FRs

## Recommendations

**For full runbook expansion:**

1. **Parametrize validation tests aggressively** (Phase 0): Character set violations should be single parametrized test with 8+ cases, not separate cycles. Saves token overhead in expanded runbook.

2. **Verify git state transitions explicitly** (Phase 1): Cycles 1.7-1.9 test `_phase4` — ensure tests verify git state (MERGE_HEAD presence/absence, branch ancestry) not just function returns.

3. **E2E before unit for session.py** (Phase 1-2): Consider E2E test first in each phase (merge with multi-line blocks in Phase 1, `new --task` in Phase 2) to establish behavioral target, then drill into edge cases with unit tests.

4. **Cross-reference existing test patterns** (All phases): Expansion Guidance references `agents/decisions/testing.md` and exploration report — ensure expanded cycles cite specific existing tests as templates (e.g., "follow `test_worktree_merge_conflicts.py::test_conflicting_pending_tasks` pattern").

5. **Consolidate trivial setup in Phase 1.1** (Phase 1): First cycle should create full `session.py` scaffolding (module, dataclass, both function stubs) as single unit. Expansion should clarify "existence → structure → behavior" for this module creation.

---

**Ready for full expansion**: Yes

All requirements traced, phases balanced, no vacuous cycles, no unfixable issues. Expansion Guidance provides clear direction for cycle elaboration. Checkpoint structure supports iterative review.
