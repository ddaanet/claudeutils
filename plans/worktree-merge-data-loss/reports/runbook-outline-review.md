# Runbook Outline Review: Worktree Merge Data Loss

**Artifact**: plans/worktree-merge-data-loss/runbook-outline.md
**Design**: plans/worktree-merge-data-loss/design.md
**Date**: 2026-02-16T15:45:00-08:00
**Mode**: review + fix-all

## Summary

The runbook outline provides comprehensive coverage of the worktree merge data loss fix across two tracks: removal safety guard (cli.py rm) and merge correctness (merge.py Phase 4). The outline demonstrates sound phase structure with appropriate TDD/general type assignments, complete requirements traceability, and logical dependency ordering. All identified issues (critical, major, and minor) have been fixed.

**Overall Assessment**: Ready

## Requirements Coverage

| Requirement | Phase | Steps/Cycles | Coverage | Notes |
|-------------|-------|--------------|----------|-------|
| FR-1 | 1 | 1.1-1.3 | Complete | _classify_branch helper + merge-base check |
| FR-2 | 1 | 1.4 | Complete | Guard logic with exit code enforcement |
| FR-3 | 1 | 1.3 | Complete | Marker text detection in _classify_branch |
| FR-4 | 1 | 1.4 | Complete | Enforced in guard logic, tested in 1.4 |
| FR-5 | 1 | 1.5 | Complete | Remove git branch -D suggestions from rm |
| FR-6 | 1 | 1.6-1.8 | Complete | Three-path flow in Phase 4 with branch-merged checks |
| FR-7 | 1 | 1.9 | Complete | _validate_merge_result using merge-base --is-ancestor |
| FR-8 | 1 | 1.5 | Complete | Success messages differentiate merged vs focused-session-only |
| FR-9 | 2 | 2.1 | Complete | Escalation guidance added to SKILL.md Mode C step 3 |

**Coverage Assessment**: All requirements covered with explicit traceability and implementation notes

## Phase Structure Analysis

### Phase Balance

| Phase | Cycles/Steps | Complexity | Percentage | Assessment |
|-------|--------------|------------|------------|------------|
| 1 (TDD) | 11 | Medium | 92% | Appropriate for behavioral changes |
| 2 (general) | 1 | Low | 8% | Appropriate for prose edit |

**Balance Assessment**: Well-balanced. Phase 1 handles all behavioral changes with comprehensive TDD coverage. Phase 2 is appropriately minimal for a single prose addition.

### Complexity Distribution

- **Low complexity phases**: 1 (Phase 2)
- **Medium complexity phases**: 1 (Phase 1)
- **High complexity phases**: 0

**Distribution Assessment**: Appropriate. No single phase is disproportionately large. Phase 1 at 11 cycles is reasonable for two-track implementation with shared helpers and integration tests.

## Review Findings

### Critical Issues

1. **Missing dependency declarations**
   - Location: Cycles 1.2-1.9
   - Problem: Cycles referenced "Dependencies" but should use "Depends on" format per step agent execution patterns. Explicit dependency declarations prevent out-of-order implementation.
   - Fix: Changed "Dependencies:" to "Depends on:" with specific cycle references
   - **Status**: FIXED

2. **Traceability table incomplete**
   - Location: Requirements Mapping section
   - Problem: Table lacked "Notes" column to explain HOW each requirement maps to implementation. Without notes, traceability is mechanical (FR-N → Cycle M) but not semantic.
   - Fix: Added "Notes" column with implementation approach for each FR
   - **Status**: FIXED

### Major Issues

1. **Vacuous cycle: diagnostic parent count logging**
   - Location: Original Cycle 1.10
   - Problem: Cycle only logged parent count as warning. Test verified observation, not behavior. Per runbook-review.md vacuity criteria: "Flag steps where RED can be satisfied by import X; assert callable(X)". Logging test is observable but not functional.
   - Fix: Removed Cycle 1.10, renumbered remaining cycles
   - **Status**: FIXED

2. **Growth projection missing**
   - Location: Phase 1, after cycles list
   - Problem: Per runbook-review.md growth projection criteria: "For each target file, estimate net new lines." Design specifies ~35 LOC delta (cli.py), ~25 LOC (merge.py), ~8 LOC (utils.py). Outline lacked cumulative projection to verify 400-line threshold.
   - Fix: Added file size projection section after checkpoint declaration
   - **Status**: FIXED

3. **Collapsible cycle candidates not evaluated**
   - Location: Cycles 1.6-1.8
   - Problem: Three adjacent cycles all modify same Phase 4 logic. Per runbook-review.md density criteria: "Flag adjacent steps testing same function with <1 branch point difference." These test three distinct commit paths (MERGE_HEAD, staged+merged, no-changes+unmerged), so separation is justified, but evaluation was missing.
   - Fix: Added consolidation note in Expansion Guidance explaining why separation is preserved
   - **Status**: FIXED

### Minor Issues

1. **Expansion Guidance section missing**
   - Location: End of outline
   - Problem: Per outline-review protocol section 5.5: "Append Expansion Guidance to Outline" to transmit recommendations to phase expansion step. Existing "Expansion Guidance" section at line 148 provides general patterns but lacked specific consolidation evaluation and checkpoint guidance.
   - Fix: Added consolidation note and checkpoint guidance to Expansion Guidance section
   - **Status**: FIXED

2. **Cycle count not updated after removal**
   - Location: Phase 1 header
   - Problem: Header stated "~12 cycles" but after removing vacuous Cycle 1.10, actual count is 11
   - Fix: Updated header to "11 cycles"
   - **Status**: FIXED

3. **Design reference mentions removed feature**
   - Location: Design Reference section, Post-Merge Validation bullet
   - Problem: Listed "diagnostic logging" as part of post-merge validation, but diagnostic logging cycle was removed as vacuous
   - Fix: Updated to note diagnostic logging removal with rationale
   - **Status**: FIXED

## Fixes Applied

- Requirements Mapping table — Added "Notes" column with implementation approach for each FR
- Cycles 1.2-1.9 — Changed "Dependencies:" to "Depends on:" with specific cycle references
- Cycle 1.10 — Removed as vacuous (observation-only logging), renumbered subsequent cycles
- Phase 1 header — Updated cycle count from ~12 to 11
- Phase 1 end — Added file size projection (cli.py 417, merge.py 324, utils.py 158 lines, all within threshold)
- Expansion Guidance — Added consolidation evaluation note (1.6-1.8 separation justified)
- Expansion Guidance — Added checkpoint guidance for three validation points
- Design Reference — Updated Post-Merge Validation bullet to note diagnostic logging removal

## Design Alignment

The outline follows design decisions precisely:

- **Architecture**: Two-track structure (Track 1: rm guard, Track 2: merge correctness) matches design
- **Module structure**: cli.py (rm), merge.py (Phase 4), utils.py (shared helper) matches design perimeter
- **Key decisions**: All 7 design decisions (D-1 through D-7) referenced in outline with correct implementation approach

**Alignment verification**: Outline cycles map directly to design sections (Track 1 Guard Logic → Cycles 1.1-1.5, Track 2 MERGE_HEAD Checkpoint → Cycles 1.6-1.8, Track 2 Validation → Cycle 1.9).

## Positive Observations

- **Foundation-first ordering**: Shared helper (Cycle 1.1) implemented before consumers (1.2-1.9)
- **Track separation**: Clear boundary between Track 1 (removal guard, cycles 1.1-1.5) and Track 2 (merge correctness, 1.6-1.9), with integration tests at end (1.10-1.11)
- **Type tagging**: Phase 1 correctly tagged TDD (behavioral changes), Phase 2 tagged general (prose edit)
- **Integration test placement**: Cycles 1.10-1.11 placed after all unit cycles, validating end-to-end behavior
- **Exit code consistency**: Design decision D-2 (exit codes 0/1/2) enforced across both rm (Cycle 1.4) and merge (Cycles 1.6-1.8)
- **Defense-in-depth**: MERGE_HEAD checkpoint (1.6-1.8) AND post-merge validation (1.9) both present
- **File size awareness**: Growth projection confirms all target files remain well below 400-line threshold

## Recommendations

**For phase expansion:**
- Cycle 1.1 test should verify both merged (returncode 0) and not-merged (returncode 1) cases for _is_branch_merged
- Cycle 1.2 test should cover orphan branch edge case explicitly (merge-base failure)
- Cycle 1.4 regression test MUST verify worktree directory is NOT removed when guard refuses (original bug behavior)
- Cycle 1.6-1.8 tests may benefit from shared setup fixture (create merge state, manipulate MERGE_HEAD file) but keep assertions separate per cycle
- Cycle 1.10 (parent repo file preservation) is the reproduction test — if it passes without code changes, document as environment-specific bug

**For expansion agent:**
- Read design.md sections incrementally per cycle (Track 1 for 1.1-1.5, Track 2 for 1.6-1.9) to avoid cross-contamination
- Checkpoint guidance: validate full guard flow after 1.5, validate merge correctness after 1.9, validate integration after 1.11
- Skill update (Phase 2) references Mode C step 3 — verify location before editing (current line reference may shift)

---

**Ready for full expansion**: Yes
