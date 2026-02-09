# Runbook Outline Review: Validator Consolidation

**Artifact**: plans/validator-consolidation/runbook-outline.md
**Requirements**: plans/validator-consolidation/requirements.md
**Date**: 2026-02-07T13:30:00-08:00
**Mode**: review + fix-all

## Summary

The outline provides a clear, well-structured migration plan for consolidating validators from agent-core/bin/ scripts into the claudeutils package. All functional requirements are mapped to specific steps, phase structure is balanced, and the approach is logical (foundation → validators → integration). Minor issues with mapping clarity, success criteria, and checkpoint placement were identified and fixed.

**Overall Assessment**: Ready

## Requirements Coverage

| Requirement | Phase | Steps/Cycles | Coverage | Notes |
|-------------|-------|--------------|----------|-------|
| FR-1 | 3 | 3.7 | Complete | Click subcommand group |
| FR-2 | 1 | 1.2 | Complete | Title format, word count, duplicates |
| FR-3 | 2 | 2.6 | Complete | Entry existence, ambiguity, duplicates |
| FR-4 | 2 | 2.5 | Complete | Uniqueness within session, git history |
| FR-5 | 2 | 2.6 | Complete | Orphan detection explicitly noted in Step 6 |
| FR-6 | 3 | 3.8 | Complete | Single just precommit call |
| NFR-1 | All | 1.1-3.7 | Complete | Full test suite per validator |
| NFR-2 | All | 1.1-2.6 | Complete | Line numbers, file paths, descriptions |
| NFR-3 | All | All | Complete | <1s for typical project |
| C-1 | 2 | 2.5 | Complete | Merge commit handling explicit |
| C-2 | 1 | 1.1 | Complete | CLAUDE.md as root marker in common.py |
| D-1 | 1-2 | 1.1-2.6 | Complete | src/claudeutils/validation/ |
| D-2 | 1 | 1.1 | Complete | common.py utilities |
| D-3 | All | 1.1-3.7 | Complete | Post-hoc tests for ported logic |
| D-4 | 3 | 3.7 | Complete | claudeutils validate [targets] |

**Coverage Assessment**: All requirements covered with explicit step mappings and requirement-to-step traceability.

## Phase Structure Analysis

### Phase Balance

| Phase | Steps | Complexity | Percentage | Assessment |
|-------|-------|------------|------------|------------|
| 1 | 4 | Medium | 29% (~700 lines) | Balanced |
| 2 | 2 | High | 52% (~1250 lines) | Largest phase, justified by validator complexity |
| 3 | 2 | Low | 19% (~350 lines) | Balanced |

**Balance Assessment**: Phase 2 is larger (52% of total work) but this is justified by the complexity of the two validators being ported (tasks.py 275 lines, memory_index.py 480 lines). The phase grouping is logical and cannot be easily subdivided without creating artificial boundaries mid-validator.

### Complexity Distribution

- **Low complexity phases**: 1 (Phase 3)
- **Medium complexity phases**: 1 (Phase 1)
- **High complexity phases**: 1 (Phase 2)

**Distribution Assessment**: Appropriate — starts with foundation and simple validators (medium), progresses to complex validators with git operations and autofix logic (high), finishes with integration (low).

## Review Findings

### Critical Issues

None identified.

### Major Issues

None identified.

### Minor Issues

1. **Requirements mapping ambiguity**
   - Location: Requirements Mapping table
   - Problem: Table used "Step X" format for phase-grouped outline (should be "Phase.Step")
   - Fix: Updated table to use consistent "X.Y" notation (1.1, 1.2, etc.) matching phase structure
   - **Status**: FIXED

2. **Missing requirement references in step descriptions**
   - Location: Steps 1, 2, 5, 6, 7, 8
   - Problem: Step descriptions didn't explicitly reference which requirements they address
   - Fix: Added FR/NFR/C/D annotations to step descriptions (e.g., "Step 1 (C-2, D-2)", "Step 2 (FR-2)")
   - **Status**: FIXED

3. **FR-5 (Orphan detection) not explicit in Step 6**
   - Location: Phase 2, Step 6
   - Problem: Step 6 mapped to FR-5 but didn't explicitly mention orphan detection in description
   - Fix: Added bold "orphan detection" with FR-5 reference and explanation to Step 6 description
   - **Status**: FIXED

4. **Click framework not specified in Key Decisions**
   - Location: Key Decisions, D-4 resolution
   - Problem: Mentioned "Click subcommand group" but didn't reference existing pattern
   - Fix: Added reference to existing CLI pattern (`claudeutils feedback`, `claudeutils token`)
   - **Status**: FIXED

5. **Vague model selection conditional**
   - Location: Phase 2 header
   - Problem: "haiku (sonnet for Step 6 if autofix logic needs judgment)" is ambiguous
   - Fix: Changed to "haiku" with note explaining autofix is being ported (not designed), so haiku sufficient
   - **Status**: FIXED

6. **Missing success criteria**
   - Location: All steps
   - Problem: Steps lacked explicit success criteria for verification
   - Fix: Added success criteria bullet to each step (1-8)
   - **Status**: FIXED

7. **Missing phase checkpoints**
   - Location: Phase boundaries
   - Problem: No explicit validation steps between phases to verify foundation before proceeding
   - Fix: Added checkpoint descriptions at end of Phase 1, Phase 2, and Phase 3
   - **Status**: FIXED

8. **Notes column missing from mapping table**
   - Location: Requirements Mapping table
   - Problem: Table could benefit from brief notes explaining coverage
   - Fix: Added Notes column with context for each requirement mapping
   - **Status**: FIXED

## Fixes Applied

- Requirements Mapping table: Added Notes column, updated step notation to phase.step format (3.7, 1.2, etc.)
- Step 1: Added (C-2, D-2) annotations, success criteria
- Step 2: Added (FR-2) annotation, success criteria with specific checks
- Step 3: Added success criteria
- Step 4: Added success criteria
- Phase 1: Added checkpoint with specific pytest command
- Step 5: Added (FR-4, C-1) annotations, bolded merge commit handling, success criteria
- Step 6: Added (FR-3, FR-5) annotations, bolded and explained orphan detection, success criteria
- Phase 2: Resolved model selection ambiguity, added checkpoint
- Step 7: Added (FR-1, D-4) annotations, success criteria
- Step 8: Added (FR-6) annotation, success criteria, checkpoint
- Key Decisions: Enhanced D-4 with existing CLI pattern reference
- Expansion Guidance: Added comprehensive guidance section for runbook expansion

## Design Alignment

**Architecture**: Outline follows design decision D-1 (validators in claudeutils package) with clear module structure (`src/claudeutils/validation/` with per-validator modules + common.py).

**Module structure**: Matches design decision D-2 (shared patterns in common.py) and properly sequences foundation (Step 1) before validators (Steps 2-6).

**Key decisions**: All design decisions (D-1 through D-4) explicitly referenced and incorporated:
- D-1: Package location specified in all validator steps
- D-2: common.py utilities in Step 1
- D-3: Test suite per step throughout
- D-4: CLI entry point resolved to Option A in Step 7

**Constraints**: Both constraints addressed:
- C-1 (merge commit handling) explicit in Step 5 with git operation details
- C-2 (CLAUDE.md root marker) explicit in Step 1 common.py

## Positive Observations

**Logical progression**: Foundation → simple validators → complex validators → integration is clear and minimizes rework.

**Parallelization opportunities**: Outline correctly identifies Steps 2-4 and Steps 5-6 as parallelizable after Step 1, enabling efficient execution.

**Source preservation**: Each porting step references source script location and line count, making verification straightforward.

**Checkpoint placement**: Added checkpoints at each phase boundary provide natural verification points before proceeding to next phase.

**Test-first approach**: Every step includes test file creation, ensuring validation logic is testable from the start.

**Realistic estimates**: Scope estimates (~700, ~1250, ~350 lines) align with source script sizes (80+113+145, 275+480, CLI overhead).

## Recommendations

**Step 6 module split**: If memory_index.py approaches 400-line limit during porting, consider extracting autofix logic to `memory_index_autofix.py` helper module. The outline correctly notes this as a consideration.

**Test execution at checkpoints**: Phase checkpoints specify pytest commands — ensure these are actually run during execution, not just documented.

**Common utilities scope**: Step 1 may benefit from extracting header parsing utilities if multiple validators share that pattern. Evaluate during Phase 1 execution.

**CLI --fix flag**: Expansion guidance mentions `--fix` flag for autofix-capable validators. Consider whether this should be in initial implementation (Step 7) or deferred to followup work.

**Git mocking patterns**: Step 5 notes "subprocess calls need careful mocking" — consider creating reusable mock fixtures in tests/conftest.py to avoid duplication across validator tests.

---

**Ready for full expansion**: Yes

All requirements traced to specific steps, phase structure is balanced and logical, complexity distribution is appropriate, and no unfixable issues identified. The outline provides sufficient detail for phase-by-phase expansion with clear success criteria and checkpoints.
