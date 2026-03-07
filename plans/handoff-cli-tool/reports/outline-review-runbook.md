# Runbook Outline Review: Session CLI Tool

**Artifact**: plans/handoff-cli-tool/runbook-outline.md
**Design**: plans/handoff-cli-tool/outline.md
**Date**: 2026-03-07
**Mode**: review + fix-all

## Summary

Well-structured outline with 7 phases covering all design requirements. Phase decomposition improves on the design's Phase Notes by separating the session.md parser into its own TDD phase. Requirements mapping table was missing step-level traceability and several design subsections — fixed. Minor consolidation opportunities in Phases 2 and 3.

**Overall Assessment**: Ready

## Requirements Coverage

| Requirement | Phase | Steps/Cycles | Coverage | Notes |
|---|---|---|---|---|
| S-1: Package structure | 1 | 1.3 | Complete | -- |
| S-2: `_git()` extraction + submodule discovery | 1 | 1.1 | Complete | -- |
| S-3: Output/error conventions | 1, all | 1.2 | Complete | Cross-cutting via `_fail()` + `_git_ok()` |
| S-4: Session.md parser | 2 | 2.1-2.5 | Complete | -- |
| S-5: Git status/diff utility | 1 | 1.4 | Complete | -- |
| H-1: Domain boundaries | 4 | -- | Complete | Design constraint, not deliverable |
| H-2: Committed detection | 4 | 4.3 | Complete | -- |
| H-3: Diagnostics | 4 | 4.6 | Complete | -- |
| H-4: State caching | 4 | 4.4 | Complete | -- |
| C-1: Scripted vet check | 5 | 5.6 | Complete | -- |
| C-2: Submodule coordination | 6 | 6.2 | Complete | -- |
| C-3: Input validation | 5 | 5.5 | Complete | -- |
| C-4: Validation levels | 6 | 6.4 | Complete | -- |
| C-5: Amend semantics | 6 | 6.3 | Complete | -- |
| ST-0: Worktree-destined tasks | 3 | 3.1 | Complete | -- |
| ST-1: Parallel group detection | 3 | 3.5 | Complete | -- |
| ST-2: Preconditions + degradation | 2, 3 | 2.5, 3.6 | Complete | -- |

**Coverage Assessment**: All requirements covered.

## Phase Structure Analysis

### Phase Balance

| Phase | Steps/Cycles | Type | Percentage | Assessment |
|---|---|---|---|---|
| 1 | 4 | general | 11% | Balanced |
| 2 | 5 | tdd | 13% | Balanced |
| 3 | 6 | tdd | 16% | Balanced |
| 4 | 7 | tdd | 18% | Balanced (7 cycles — checkpoint guidance added) |
| 5 | 6 | tdd | 16% | Balanced |
| 6 | 6 | tdd | 16% | Balanced |
| 7 | 4 | tdd | 11% | Balanced |

**Balance Assessment**: Well-balanced. No phase exceeds 20%. Largest phase (4) has 7 cycles with checkpoint guidance.

### Complexity Distribution

- Phase 1 (general): Medium — extraction refactoring with import updates across 5 files
- Phases 2, 3: Medium — parser and rendering, builds on existing code
- Phase 4: High — state machine with committed detection, precommit integration, state caching
- Phases 5, 6: High — commit pipeline with submodule coordination, amend semantics
- Phase 7: Medium — integration tests using established infrastructure

**Distribution Assessment**: Appropriate. High complexity concentrated in Phases 4-6 (the core pipelines), well-decomposed into cycles.

## Review Findings

### Critical Issues

None.

### Major Issues

1. **Requirements mapping table lacked step-level traceability**
   - Location: Requirements Mapping section
   - Problem: Table only mapped requirements to phases, not to specific steps/cycles. Missing `Steps/Cycles` and `Notes` columns. Design subsections H-1 through H-4, C-1 through C-5, ST-0 through ST-2 not individually mapped.
   - Fix: Expanded table with Steps/Cycles column, Notes column, and all 18 individual requirements mapped to specific steps/cycles.
   - **Status**: FIXED

### Minor Issues

1. **Cycle 2.4 potentially vacuous**
   - Location: Phase 2, Cycle 2.4
   - Problem: Worktree tasks parsing uses identical task format as in-tree tasks (Cycle 2.3), differing only by section name. Could be satisfied by parametrizing the prior cycle's test.
   - Fix: Added annotation noting parametrization candidate; expansion guidance recommends combining if no worktree-specific logic exists.
   - **Status**: FIXED

2. **Missing cross-phase dependency declarations**
   - Location: Phases 3, 4, 6
   - Problem: Phase 3 (status) and Phase 4 (handoff) depend on Phase 2 (parser) but dependency not declared. Phase 6 depends on Phase 5 but not declared.
   - Fix: Added `Depends on:` declarations to Cycles 3.6, 4.7, and 6.6.
   - **Status**: FIXED

3. **Phase 4 has 7 cycles without mid-phase checkpoint recommendation**
   - Location: Phase 4
   - Problem: 7 cycles exceeds the 6-cycle threshold where mid-phase checkpoints improve recovery. State caching (4.4) is a natural boundary.
   - Fix: Added checkpoint guidance in Expansion Guidance section recommending checkpoint after Cycle 4.4.
   - **Status**: FIXED

4. **Expansion Guidance lacked structured sections**
   - Location: Expansion Guidance
   - Problem: Original guidance was a flat bullet list missing consolidation candidates, checkpoint guidance, cycle expansion specifics, and code references.
   - Fix: Restructured into sections: Phase type, Consolidation candidates, Existing code reuse, Checkpoint guidance, Cycle expansion, Subprocess in tests, Shared test fixtures, References to include.
   - **Status**: FIXED

## Fixes Applied

- Requirements Mapping table: expanded from 2-column (Requirement, Phase) to 4-column (Requirement, Phase, Steps/Cycles, Notes) with 18 individually mapped requirements
- Cycle 2.4: added parametrization annotation
- Cycles 3.6, 4.7, 6.6: added `Depends on:` declarations
- Expansion Guidance: restructured into 8 sections with actionable specifics, consolidation candidates, checkpoint recommendation, and source code references

## Design Alignment

- **Architecture**: Aligned. Package structure (S-1) matches design. `_session` and `_git` command groups correctly placed.
- **Module structure**: Aligned. Outline's Phase 2 (parser as separate TDD phase) improves on design's grouping with Phase 1 — parser is substantial enough for its own phase.
- **Key decisions**: All referenced. Stdout-only output (S-3), exit code semantics, `_fail()` pattern, existing parser reuse, CliRunner testing, submodule discovery via `git submodule status`.
- **Existing code integration**: Correctly identifies `worktree/session.py` (TaskBlock, extract_task_blocks, find_section_bounds), `validation/task_parsing.py` (ParsedTask, parse_task_line, TASK_PATTERN), and `worktree/git_ops.py` (_git, _is_submodule_dirty) as reuse targets.

## Positive Observations

- Clean separation of parser (Phase 2) from consumers (Phases 3, 4) — enables parallel expansion and isolated testing
- Commit pipeline decomposed into parser+validation (Phase 5) and execution+output (Phase 6) — separates parsing concerns from git operations
- Integration phase (7) includes cross-subcommand test (7.4: handoff then status reads) — validates parser consistency across write and read paths
- Key Decisions section captures non-obvious choices (extending existing ParsedTask, `_fail()` with Never return type)

## Recommendations

- During Phase 1 expansion, grep for all `_git` and `_is_submodule_dirty` imports before extraction — the outline lists 5 files but verify none were missed
- Phase 4 Cycle 4.3 (committed detection) has 3 modes per design H-2 — each mode should be an explicit test case during expansion
- Phase 6 Cycle 6.2 (submodule coordination) has a 4-cell decision matrix per design C-2 — each cell should be a test case

---

**Ready for full expansion**: Yes
