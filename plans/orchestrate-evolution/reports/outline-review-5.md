# Runbook Outline Review: orchestrate-evolution

**Artifact**: plans/orchestrate-evolution/runbook-outline.md
**Design**: plans/orchestrate-evolution/design.md
**Date**: 2026-02-24
**Mode**: review + fix-all

## Summary

The outline is well-structured with complete requirements coverage, clear phase progression, and appropriate complexity distribution. Three dependency declaration gaps were found and fixed. A test file growth risk was identified based on prior project learnings and addressed with split guidance. The outline is ready for full runbook expansion after fixes.

**Overall Assessment**: Ready

## Requirements Coverage

| Requirement | Phase | Steps/Cycles | Coverage | Notes |
|-------------|-------|--------------|----------|-------|
| FR-2 | 3 | Step 3.1 | Complete | SKILL.md remediation protocol |
| FR-3 | 3 | Step 3.1 | Complete | RCA task after remediation |
| FR-4 | 1 | Cycles 1.1-1.3 | Complete | Agent caching eliminates inline content |
| FR-5 | 1 | Cycle 1.1 | Complete | Clean tree footer in agent definition |
| FR-6 | 1 | Cycle 1.1 | Complete | Scope enforcement footer + structural absence |
| FR-7 | 2 | Cycle 2.4 + Phase 3 | Complete | verify-step.sh + SKILL.md invocation |
| FR-8 | 4, 5 | Phase 4 + Phase 5 | Complete | Agents + scripts + SKILL.md loop |
| FR-8a | 4 | Cycle 4.4 | Complete | verify-red.sh |
| FR-8b | 2, 5 | Cycle 2.4, Step 5.1 | Complete | Fixed: clarified composed GREEN gate (was mapped only to verify-step.sh) |
| FR-8c | 4 | Cycle 4.1 | Complete | test-corrector + impl-corrector |
| FR-8d | 5 | Step 5.1 | Complete | TDD loop resume strategy |
| NFR-1 | 1, 2 | Agent caching + plan format | Complete | File references only |
| NFR-2 | All | All phases | Complete | Q-4 clean break |
| NFR-3 | 3 | Step 3.1 | Complete | Sonnet default |

**Coverage Assessment**: All requirements covered. FR-8b mapping refined for precision.

## Deliverable-Level Traceability

| Deliverable | Action | FR | Outline Item | Status |
|-------------|--------|-----|--------------|--------|
| `SKILL.md` | Rewrite | FR-2, FR-3, NFR-3 | Step 3.1 | Mapped |
| `prepare-runbook.py` | Modify | FR-4, FR-5, FR-6 | Phases 1, 2, 4 | Mapped |
| `refactor.md` | Modify | — | Step 3.2 | Mapped |
| `delegation.md` | Modify | NFR-1 | Step 3.3 | Mapped |
| `verify-step.sh` | Create | FR-7 | Cycle 2.4 | Mapped |
| `orchestrator-plan.md` | Generated | NFR-1 | Cycles 2.1-2.3 | Mapped |
| `SKILL.md` | Extend | FR-8, FR-8d | Step 5.1 | Mapped |
| `verify-red.sh` | Create | FR-8a | Cycle 4.4 | Mapped |
| `<plan>-tester.md` | Generated | FR-8 | Cycle 4.1 | Mapped |
| `<plan>-implementer.md` | Generated | FR-8 | Cycle 4.1 | Mapped |
| `<plan>-test-corrector.md` | Generated | FR-8c | Cycle 4.1 | Mapped |
| `<plan>-impl-corrector.md` | Generated | FR-8c | Cycle 4.1 | Mapped |

**Deliverable Assessment**: All design deliverables (Phase 1 + Phase 2 tables) mapped to outline items.

## Phase Structure Analysis

### Phase Balance

| Phase | Items | Complexity | Percentage | Assessment |
|-------|-------|------------|------------|------------|
| 1 | 4 cycles | Medium | 25% | Balanced |
| 2 | 4 cycles | Medium | 25% | Balanced |
| 3 | 3 steps | High/Low/Low | 19% | Balanced (dominated by Step 3.1) |
| 4 | 4 cycles | Medium | 25% | Balanced |
| 5 | 1 step | Medium | 6% | Small but justified (opus model, different concerns) |

**Balance Assessment**: Well-balanced. Phase 5 is small but justified by model boundary (opus vs sonnet) and logical separation (skill extension vs infrastructure).

### Complexity Distribution

- Low complexity phases: 0
- Medium complexity phases: 4 (Phases 1, 2, 4, 5)
- High complexity phases: 1 (Phase 3, driven by Step 3.1 SKILL.md rewrite)

**Distribution Assessment**: Appropriate. High complexity concentrated in Phase 3 (SKILL.md rewrite) which is correctly flagged for full checkpoint at boundary.

## Review Findings

### Critical Issues

None.

### Major Issues

1. **Phase 4 missing dependency on Phase 2**
   - Location: Phase 4 "Depends on" declaration
   - Problem: Cycle 4.3 adds TDD role markers to the orchestrator plan format established in Phase 2. Without Phase 2, the plan format doesn't exist for Phase 4 to extend.
   - Fix: Added Phase 2 to dependency declaration: "Phase 2 (orchestrator plan format extended with TDD role markers)"
   - **Status**: FIXED

2. **Phase 5 missing dependency on Phase 3**
   - Location: Phase 5 "Depends on" declaration
   - Problem: Step 5.1 extends SKILL.md which was rewritten in Phase 3 Step 3.1. Only Phase 4 was declared as dependency.
   - Fix: Added Phase 3 to dependency declaration: "Phase 3 (SKILL.md rewrite provides base to extend)"
   - **Status**: FIXED

3. **Test file growth risk for test_prepare_runbook_agents.py**
   - Location: Phase 1 Files, Phase 4 Files (both extend same test file)
   - Problem: `test_prepare_runbook_agents.py` is 353 lines. Phase 1 (4 cycles) and Phase 4 Cycle 4.1 both target it. Projected growth: 353 + ~80 (Phase 1) + ~80 (Phase 4) = ~513 lines, well past 400-line threshold. Project learnings document this exact failure pattern with 3 escalations in a prior runbook.
   - Fix: Added growth projection warning to Expansion Guidance section with split recommendation (Phase 4 tests to new `test_prepare_runbook_tdd_agents.py`)
   - **Status**: FIXED

### Minor Issues

1. **FR-8b mapping imprecision**
   - Location: Requirements Mapping table, FR-8b row
   - Problem: FR-8b (GREEN gate) was mapped only to "Cycle 2.4 (verify-step.sh composes with `just test`)" — but verify-step.sh alone is the clean-tree check, not the full GREEN gate. The composed GREEN gate (test pass + clean tree) is defined in Step 5.1's TDD loop.
   - Fix: Updated mapping to "Cycle 2.4 (verify-step.sh: clean tree), Step 5.1 (composed GREEN = `just test` + verify-step.sh)" with Phase reference expanded to "2, 5"
   - **Status**: FIXED

2. **Phase 5 Step 5.1 missing post-phase state note**
   - Location: Step 5.1 title
   - Problem: Step 5.1 extends SKILL.md without noting it was rewritten to ~200 lines in Phase 3. Expanding agents need this context.
   - Fix: Added "(extends ~200-line rewrite from Phase 3)" to Step 5.1 title
   - **Status**: FIXED

## Fixes Applied

- Requirements Mapping table, FR-8b row: refined GREEN gate mapping to reference both verify-step.sh (Cycle 2.4) and composed gate (Step 5.1)
- Phase 4 "Depends on": added Phase 2 dependency for orchestrator plan format
- Phase 5 "Depends on": added Phase 3 dependency for SKILL.md base
- Step 5.1 title: added post-phase state note "(extends ~200-line rewrite from Phase 3)"
- Expansion Guidance: added test file growth risk warning with split recommendation for `test_prepare_runbook_agents.py`
- Appended "Expansion Guidance (Review)" section with consolidation analysis, cycle expansion notes, checkpoint guidance, and recall artifact references

## Design Alignment

- **Architecture**: Outline follows design's 2-phase structure (Phase 1 = foundation, Phase 2 = TDD). The outline's 5 phases decompose design's 2 phases into TDD-appropriate granularity (agent caching, plan format, prose, TDD agents, TDD skill).
- **Module structure**: Files match design deliverable tables exactly. No extraneous files, no missing files.
- **Key decisions**: All 6 design decisions (D-1 through D-6) referenced in Key Decisions Reference section and traced to specific outline items.
- **Agent caching model (D-2)**: Phases 1 and 4 implement the two tiers (general agents, TDD agents) exactly as designed.
- **Remediation (D-3)**: Step 3.1 covers the full protocol (resume → recovery → RCA → escalate).
- **Inline phases (D-6)**: Cycle 2.2 adds INLINE markers; Step 3.1 adds orchestrator inline handling.

## Positive Observations

- Clean phase decomposition: design's 2 logical phases split into 5 execution phases that respect model boundaries (sonnet TDD phases vs opus prose phases)
- Recall artifact guidance pre-loaded in Expansion Guidance section (E2E testing, agent baselines, naming conventions)
- Checkpoint plan distinguishes light vs full checkpoints appropriately — full checkpoints at high-impact boundaries (Phase 3 SKILL.md rewrite, Phase 5 completion)
- Every cycle has explicit verification criteria
- Dependency chain is now complete: Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 5 (with Phase 4 also depending on Phases 1+2, Phase 5 on Phases 3+4)

## Recommendations

- During expansion, the planner should confirm `test_prepare_runbook_agents.py` split point before Phase 4 begins (either split during Phase 1 planning or route Phase 4 tests to new file)
- Step 3.1 is the highest-risk item (SKILL.md rewrite from 517 → ~200 lines). Expansion should specify clear sections to preserve vs remove, not leave this to the opus agent's judgment
- Phase 4 Cycle 4.1 generates 4 agent types — expansion should specify shared helper extraction if agent generation code duplicates significantly across types

---

**Ready for full expansion**: Yes
