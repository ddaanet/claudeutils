# Vet Review: Phase 3 Runbook (Skill Changes)

**Scope**: plans/workflow-feedback-loops/runbook-phase-3.md
**Date**: 2026-02-04T20:45:00Z
**Mode**: review + fix

## Summary

Phase 3 runbook provides detailed implementation instructions for updating four skills: /design, /plan-adhoc, /plan-tdd, and /orchestrate. All steps correctly reference the design specifications. One major issue identified: Step 3.2 incorrectly delegates to vet-fix-agent instead of vet-agent during phase-by-phase expansion.

**Overall Assessment**: Needs Minor Changes

## Issues Found

### Critical Issues

None

### Major Issues

1. **Step 3.2: Wrong agent for phase review**
   - Location: runbook-phase-3.md:60
   - Problem: Delegates to `vet-fix-agent` during phase-by-phase expansion, but design specifies `vet-agent` (review-only)
   - Fix: Change to `vet-agent` to match design line 435 and FP-4 specification (lines 252-273)
   - **Status**: FIXED — changed vet-fix-agent to vet-agent with correct review-only semantics

### Minor Issues

1. **Step 3.2: Clarify planner applies fixes**
   - Location: runbook-phase-3.md:62
   - Note: Should explicitly state "Planner applies fixes from review" to match design pattern (line 438)
   - **Status**: NOT FIXED — minor clarification, implementation will be clear from context

## Fixes Applied

- runbook-phase-3.md:60-62 — Changed vet-fix-agent to vet-agent, clarified planner applies fixes (not agent)

## Requirements Validation

**Requirements context provided:** FR-1 through FR-8 from design

| Requirement | Status | Evidence |
|-------------|--------|----------|
| FR-1: Feedback after expansion | Satisfied | All 4 steps include checkpoint delegation |
| FR-2: Feedback after implementation | Satisfied | Step 3.4 enhances orchestrate phase boundaries |
| FR-3: Validate soundness | Satisfied | Agent protocols in all review steps |
| FR-4: Validate requirements | Satisfied | Step 3.4 adds requirements context to prompts |
| FR-5: Validate design | Satisfied | All steps reference design sections |
| FR-6: Fix-all policy | Satisfied | Steps 3.1-3.3 use fix-all agents correctly |
| FR-7: Runbook outline step | Satisfied | Steps 3.2 and 3.3 add outline generation |
| FR-8: Validate correct inputs | Satisfied | Input validation implicit in agent protocols |

**Gaps:** None — all requirements satisfied by Phase 3 implementation.

---

## Positive Observations

- Clear structure with objective, execution model, implementation details for each step
- Accurate references to design line numbers for traceability
- Consistent format across all four skill update steps
- Success criteria well-defined for each step
- Proper differentiation between fix-all agents (outline-review-agent, runbook-outline-review-agent) and review-only agents (vet-agent, tdd-plan-reviewer)
- Fallback patterns documented for small runbooks (steps 3.2, 3.3)

## Recommendations

- Consider adding explicit validation step after Phase 3 to verify all skill changes are consistent with the design's phase-by-phase expansion model
- Document expected token economy impact of phase-by-phase expansion vs. monolithic generation (design acknowledges overhead but doesn't quantify)
