# Runbook Outline Review: worktree-merge-resilience

**Artifact**: plans/worktree-merge-resilience/runbook-outline.md
**Design**: plans/worktree-merge-resilience/outline.md (outline serves as design)
**Requirements**: plans/worktree-merge-resilience/requirements.md
**Date**: 2026-02-18
**Mode**: review + fix-all

## Summary

The runbook outline is well-structured with clear phase boundaries, explicit design decision references, and appropriate TDD/general typing. Seven issues found: one major (missing `clean` state cycle), two major (missing checkpoints, growth projection), and four minor (traceability table format, dependency inconsistencies, cli.py omission from D-8 scope, hardcoded call site count). All fixed.

**Overall Assessment**: Ready

## Requirements Coverage

| Requirement | Phase | Cycles/Steps | Coverage | Notes |
|-------------|-------|--------------|----------|-------|
| FR-1 | 2 | 2.1, 2.2 | Complete | D-6 check=False, MERGE_HEAD preserved |
| FR-2 | 3 | 3.1 | Complete | D-3 abort removal, exit 3 |
| FR-3 | 3 | 3.2, 3.3 | Complete | D-4 git-add-retry, both same/different content |
| FR-4 | 4 | 4.1, 4.2 | Complete | Output contract: file list, diff stats, divergence, hint |
| FR-5 | 1 | 1.1-1.5 | Complete | 5-state machine, all states have dedicated cycles (added 1.5) |
| NFR-1 | 5 | 5.1 | Complete | Exit code audit, error vs conflict classification |
| NFR-2 | 3, 5 | 3.1, 5.1 | Complete | Cross-cutting: Phase 3 removes abort, Step 5.1 audits all paths |
| C-1 | 5 | 5.3 | Complete | SKILL.md Mode C exit code 3 handling |
| C-2 | 5 | 5.2 | Complete | D-8 stdout unification |

**Coverage Assessment**: All requirements covered. FR-5 gap (missing `clean` state cycle) identified and fixed.

## Phase Structure Analysis

### Phase Balance

| Phase | Cycles/Steps | Complexity | Percentage | Assessment |
|-------|--------------|------------|------------|------------|
| 1 | 5 cycles | High | 33% | Balanced (was 27% with 4 cycles) |
| 2 | 2 cycles | Medium | 13% | Balanced |
| 3 | 3 cycles | High | 20% | Balanced |
| 4 | 2 cycles | Medium | 13% | Balanced |
| 5 | 3 steps | Low | 20% | Balanced |

**Balance Assessment**: Well-balanced. Phase 1 is largest (5 cycles) but justified by 5-state machine requiring distinct git setups.

### Complexity Distribution

- Low complexity phases: 1 (Phase 5)
- Medium complexity phases: 2 (Phases 2, 4)
- High complexity phases: 2 (Phases 1, 3)

**Distribution Assessment**: Appropriate. High complexity phases have checkpoint markers.

## Review Findings

### Critical Issues

None.

### Major Issues

1. **Missing `clean` state cycle in Phase 1**
   - Location: Phase 1, Cycles 1.1-1.4
   - Problem: Design D-5 defines 5 states (`merged`, `parent_resolved`, `parent_conflicts`, `submodule_conflicts`, `clean`) but outline had only 4 cycles. The `clean` state (no merge in progress, run full pipeline) had no dedicated test proving the state machine router reaches the full pipeline path.
   - Fix: Added Cycle 1.5 for `clean` state with integration test verifying all phases execute in sequence.
   - **Status**: FIXED

2. **No checkpoint guidance in high-complexity phases**
   - Location: Phases 1 and 3
   - Problem: Phase 1 (5 cycles, High) and Phase 3 (3 cycles, High) had no checkpoint markers. Phases with complex data manipulation need validation points.
   - Fix: Added checkpoint after Cycle 1.3 (verify in-progress state routing) and after Cycle 3.1 (verify NFR-2 invariant via grep).
   - **Status**: FIXED

3. **No growth projection for merge.py**
   - Location: Expansion Guidance
   - Problem: merge.py (262 lines) is modified by all 5 phases. Projected cumulative ~387 lines exceeds 350-line threshold. No split recommendation existed.
   - Fix: Added growth projection section to Expansion Guidance with split recommendation: extract `_format_conflict_report` and state detection into `merge_state.py` if threshold exceeded after Phase 3.
   - **Status**: FIXED

### Minor Issues

1. **Requirements mapping table missing Cycles/Steps column**
   - Location: Requirements Mapping section
   - Problem: Table had `| Requirement | Phase | Key Decision |` instead of including cycle-level traceability.
   - Fix: Restructured table to `| Requirement | Phase | Cycles/Steps | Key Decision | Notes |` with explicit cycle references for each requirement.
   - **Status**: FIXED

2. **Phase 2 dependency declaration inconsistency**
   - Location: Phase 2, two separate "Depends on" references
   - Problem: Phase scope paragraph said "Depends on: Phase 1" and bottom field said "Depends on: Cycle 1.4" — redundant and confusing.
   - Fix: Consolidated to single `Depends on:` field with cycle-level reference and rationale.
   - **Status**: FIXED

3. **cli.py omitted from D-8 migration scope**
   - Location: Step 5.2, Phase 5 affected files
   - Problem: `cli.py` merge handler (lines 258-263) uses `click.echo(..., err=True)` for merge error output. D-8 requires all merge output to stdout, but Step 5.2 only listed merge.py.
   - Fix: Added `cli.py` (merge handler only) to Step 5.2 affected files and Phase 5 affected files list.
   - **Status**: FIXED

4. **Hardcoded call site count in Step 5.2**
   - Location: Step 5.2 execution model
   - Problem: Stated "~8 call sites" without verification. Exploration report doesn't enumerate `err=True` occurrences in merge.py specifically.
   - Fix: Changed to "grep `err=True` to enumerate call sites" — execution agent discovers actual count.
   - **Status**: FIXED

5. **Cycle 3.1 dependency incomplete**
   - Location: Cycle 3.1 inline dependency
   - Problem: Listed "Depends on: Cycle 1.3" but Phase 3 scope header listed "Depends on: Cycles 1.3, 2.1". Missing dependency on Phase 2 pass-through stability.
   - Fix: Updated Cycle 3.1 dependency to "Depends on: Cycles 1.3, 2.1" with rationale.
   - **Status**: FIXED

6. **NFR-2 mapped only to Phase 3**
   - Location: Requirements Mapping table
   - Problem: NFR-2 is cross-cutting (D-7) — Phase 3 removes the primary violation but Step 5.1 audits all remaining paths. Mapping showed only Phase 3.
   - Fix: Updated mapping to show "3, 5" with note "Cross-cutting: Phase 3 removes abort, Step 5.1 audits all paths."
   - **Status**: FIXED

## Fixes Applied

- Requirements Mapping table — restructured with Cycles/Steps and Notes columns; added cycle-level references for all requirements; NFR-2 mapped to Phases 3 and 5
- Phase 1 — added Cycle 1.5 (`clean` state); added checkpoint after Cycle 1.3
- Phase 2 — consolidated duplicate dependency declarations into single field
- Phase 3 — added checkpoint after Cycle 3.1; updated Cycle 3.1 dependency to include 2.1
- Phase 5 — added cli.py to Step 5.2 and affected files; removed hardcoded call site count
- Expansion Guidance — restructured into labeled sections; added growth projection with split recommendation; added consolidation candidates; added checkpoint guidance; added semantic propagation analysis; added justfile scope boundary note

## Design Alignment

- **Architecture**: Aligned. State machine entry (D-5) reflected in Phase 1 with all 5 states covered.
- **Module structure**: Aligned. Single-file approach (merge.py) with growth projection and extraction boundary identified.
- **Key decisions**: All 8 decisions (D-1 through D-8) referenced in appropriate phases and Expansion Guidance.
- **Scope boundaries**: Aligned with design. Justfile out-of-scope noted in Expansion Guidance (not in original outline).

## Positive Observations

- Phase typing is well-chosen: TDD for behavioral logic (Phases 1-4), General for exit code threading + docs (Phase 5)
- Existing test updates explicitly identified (Cycles 3.1, 3.2) with RED-phase change rationale
- Dependency chain is clean: 1 → 2 → 3 → 4 → 5, with cycle-level dependencies declared
- Expansion Guidance included from initial outline (testing diamond, prose atomicity, self-modification ordering)
- Phase 5 execution model assignments are thoughtful: Sonnet for audit judgment, Haiku for mechanical substitution, Opus for LLM-consumed prose

## Recommendations

- During Phase 1 expansion, consider whether Cycles 1.1 and 1.2 can share a common repo setup fixture (both route to Phase 4, differ only in detection condition)
- Step 5.3 must address the justfile/Python CLI invocation discrepancy: SKILL.md Mode C currently invokes `just wt-merge`, but this runbook only modifies the Python CLI. Either update Mode C to invoke `claudeutils _worktree merge` or note justfile parity as deferred work.
- Phase 3 Cycle 3.2 stderr message to parse: verify the exact error message git produces for untracked file collisions across git versions (message text may vary)

---

**Ready for full expansion**: Yes
