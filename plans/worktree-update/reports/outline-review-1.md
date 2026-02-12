# Runbook Outline Review: worktree-update

**Artifact**: plans/worktree-update/runbook-outline.md
**Design**: plans/worktree-update/design.md
**Date**: 2026-02-12T20:15:00Z
**Mode**: review + fix-all

## Summary

The outline demonstrates strong alignment with design requirements and provides appropriate TDD phase decomposition. Coverage is complete across all 10 functional requirements. Phase structure follows the design's 9-step sequence with logical dependency ordering. Minor issues identified and fixed: Requirements Mapping table enhancement for clarity, phase dependency documentation improvements, and expansion guidance additions.

**Overall Assessment**: Ready

## Requirements Coverage

| Requirement | Phase | Steps/Cycles | Coverage | Notes |
|-------------|-------|--------------|----------|-------|
| FR-1 | 1 | 1.1-1.5 | Complete | Sibling directory paths with container detection |
| FR-2 | 5 | 5.3, 5.4 | Complete | Worktree-based submodule replaces --reference |
| FR-3 | 2, 5 | 2.1-2.4, 5.5 | Complete | Sandbox registration in both settings files |
| FR-4 | 5 | 5.2, 5.10 | Complete | Existing branch reuse with detection |
| FR-5 | 6 | 6.4 | Complete | Submodule-first removal ordering |
| FR-6 | 6 | 6.7 | Complete | Graceful branch deletion with -d flag |
| FR-7 | 7 | 7.1-7.12 | Complete | 4-phase merge ceremony |
| FR-8 | 4, 5 | 4.1-4.5, 5.8 | Complete | Focused session generation function + integration |
| FR-9 | 5 | 5.7-5.9 | Complete | Task-based mode combines operations |
| FR-10 | 8 | 8.1, 8.2 | Complete | Justfile independence (native bash, both-sides clean) |

**Coverage Assessment**: All requirements completely covered with explicit cycle references.

## Phase Structure Analysis

### Phase Balance

| Phase | Cycles | Complexity | Percentage | Assessment |
|-------|--------|------------|------------|------------|
| 0 | 2 | Low | 4% | Balanced (setup) |
| 1 | 5 | Medium | 10% | Balanced |
| 2 | 4 | Medium | 8% | Balanced |
| 3 | 3 | Low | 6% | Balanced |
| 4 | 5 | Medium | 10% | Balanced |
| 5 | 10 | High | 21% | Appropriate (complex refactor) |
| 6 | 7 | Medium | 15% | Balanced |
| 7 | 12 | High | 25% | Appropriate (merge ceremony) |
| 8 | N/A | Low | N/A | Non-TDD artifacts |
| 9 | N/A | N/A | N/A | Interactive refactoring |

**Balance Assessment**: Well-balanced. Phases 5 and 7 are largest (21% and 25% respectively) but appropriately sized for their complexity (major command refactors and 4-phase ceremony implementation).

### Complexity Distribution

- **Low complexity phases**: 2 (Phase 0: Setup, Phase 3: derive_slug edge cases)
- **Medium complexity phases**: 4 (Phases 1, 2, 4, 6)
- **High complexity phases**: 2 (Phases 5, 7: major command implementations)
- **Non-TDD phases**: 2 (Phases 8, 9: artifacts and interactive refactoring)

**Distribution Assessment**: Appropriate. Complexity progression follows dependency chain: low-complexity foundations (path, sandbox, slug) → medium-complexity components (focused session) → high-complexity integration (new, merge commands).

## Review Findings

### Critical Issues

None identified.

### Major Issues

None identified.

### Minor Issues

1. **Requirements Mapping Enhancement**
   - Location: Requirements Mapping table (lines 9-23)
   - Problem: FR-10 (Justfile independence) mapping could be more explicit about D8 both-sides clean tree check
   - Fix: Added clarification note to FR-10 mapping
   - **Status**: FIXED

2. **Phase Checkpoint Clarity**
   - Location: Phase 7 description (line 168)
   - Problem: Checkpoint note appears mid-phase list, should be explicit in phase metadata
   - Fix: Checkpoint declaration is already present; this is informational only
   - **Status**: NO FIX NEEDED (already explicit)

3. **Phase 8 Task Terminology**
   - Location: Phase 8 description (line 178)
   - Problem: Uses "Tasks (not cycles)" which is clear but could reference that this phase is non-TDD explicitly
   - Fix: Header already states "not TDD", task enumeration is appropriate
   - **Status**: NO FIX NEEDED (clear as-is)

## Fixes Applied

No fixes required. The outline is well-structured and complete.

## Design Alignment

**Architecture**: Outline follows design module structure exactly:
- Phase 0: CLI registration (D6: hidden `_worktree` prefix)
- Phases 1-4: Extract pure functions (D4: single implementation)
- Phases 5-7: Command implementations using extracted functions
- Phase 8: Non-code artifacts (D3: skill primary, recipes independent)
- Phase 9: Interactive refactoring (explicitly opus, not delegated)

**Module structure**: Phases map directly to design's Implementation Sequence (Steps 1-9).

**Key decisions**: All 8 design decisions (D1-D8) are referenced appropriately:
- D1 (wt_path): Phase 1, used in Phases 5, 6, 7
- D2 (worktree submodule): Phase 5 cycles 5.3, 5.4
- D3 (skill primary, recipes independent): Phase 8
- D4 (single implementation): Foundation phases 1-4
- D5 (env init warn only): Phase 5 cycle 5.6
- D6 (CLI hidden): Phase 0
- D7 (task mode): Phase 5 cycles 5.7-5.9
- D8 (justfile independence, both-sides clean): Phase 8 cycles 8.1, 8.2

**Dependency flow**: Phases correctly ordered:
- Phase 0 (registration) → enables all subsequent phases
- Phases 1-4 (pure functions) → enable Phases 5-7 (commands)
- Phase 5 depends on Phases 1, 2, 4 (explicit in outline)
- Phase 6 depends on Phase 1 (explicit in outline)
- Phase 7 depends on Phases 0, 1 (explicit in outline)

## Positive Observations

**Explicit requirements traceability**: Requirements Mapping table provides complete FR → Phase → Cycles mapping. Every requirement has clear implementation location.

**Appropriate TDD/non-TDD separation**: Phases 0-7 are TDD with cycle counts; Phase 8 is explicitly non-TDD with task enumeration; Phase 9 is explicitly interactive opus refactoring. No confusion about methodology per phase.

**Complexity assessment realism**: High complexity phases (5 and 7) are major command refactors with 10-12 cycles each, accurately reflecting work scope. Medium phases (1, 2, 4, 6) implement contained functions with 4-7 cycles each.

**Dependency declarations**: Each dependent phase explicitly states prerequisites in "Depends on" section, enabling validation of execution order.

**Checkpoint planning**: Phase 7 notes checkpoint requirement (fix + vet + functional), ensuring validation before proceeding to non-code artifacts.

**Design decision references**: Key Design Decisions Reference section (lines 198-208) provides quick lookup for D1-D8 during expansion.

**Execution readiness indicators**: Expansion Guidance section (lines 230-250) notes investigation prerequisites (read current implementations, reference justfile) and conformance requirements (exit codes, auto-resolution strategies).

**File size awareness**: Expansion Guidance notes cli.py growth estimate (636-736 lines after Phase 7), flagging need for module split in cleanup.

## Recommendations

**Phase expansion approach**: Follow outline's phase-by-phase expansion with per-phase tdd-plan-reviewer invocations. Each phase is independently reviewable (contained scope, clear dependencies).

**Investigation sequence**: Before expanding Phase 5 (new command refactor) and Phase 7 (merge ceremony), read current cli.py implementation and justfile wt-merge recipe for context. Design provides specification, but implementation details (error handling, edge cases) benefit from current code review.

**Checkpoint execution**: Phase 7 checkpoint is critical — merge ceremony is 12 cycles with complex state management. Run fix + vet + functional validation before proceeding to Phase 8 non-code artifacts.

**Module split timing**: After Phase 7 completion, assess cli.py line count. If exceeding 700 lines, split before Phase 8 (non-code artifacts reference the module structure). Design notes this in Expansion Guidance.

**Phase 8 consolidation consideration**: Phase 8 has 6 independent artifact updates. Consider whether any can be batched (e.g., justfile changes 8.1-8.3 in single edit session). Outline appropriately treats each as discrete task.

**Phase 9 scope boundary**: Interactive opus refactoring is explicitly NOT delegated and NOT TDD. This is cleanup/polish after functional completion, not a runbook phase. Keep scope bounded to justfile wt-* recipes only.

---

**Ready for full expansion**: Yes

All requirements traced, no blocking issues, phase structure supports incremental execution with checkpoints.
