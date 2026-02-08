# Vet Review: Phase 3 Runbook (Tier 3 Fixes)

**Scope**: Phase 3 runbook file (runbook-phase-3.md)
**Date**: 2026-02-08T15:45:00Z

## Summary

Phase 3 runbook covers 2 steps for Tier 3 fixes (Gap 1 conformance requirements + N2 vet alignment). Overall structure is clear and executable. Dependency on Phase 2 (Gap 4) is correctly stated. Minor improvements needed for skill file location precision and content integration guidance.

**Overall Assessment**: Needs Minor Changes

## Issues Found

### Critical Issues

None.

### Major Issues

1. **Integration location for plan-tdd too vague**
   - Location: Step 9, lines 82-86
   - Problem: "Locate cycle planning sections (likely Phase 2-3 or within planner guidance)" is too imprecise for haiku executor
   - Fix: Specify section name pattern to search for (e.g., "Search for '## Phase 2' or '### Cycle Design' in planner section") OR specify to add after specific existing content

2. **Integration location for plan-adhoc too vague**
   - Location: Step 9, lines 87-90
   - Problem: "Locate step planning sections (likely Point 1 or within planner guidance)" is too imprecise
   - Fix: Specify section name to search for (e.g., "Search for 'Point 1:' or '### Step Design' in planner guidance") OR specify insertion point relative to existing structure

### Minor Issues

1. **Example table formatting not specified**
   - Location: Step 9, lines 45-47 and lines 69-73
   - Note: Markdown table formatting in content blocks may render as prose if not properly formatted
   - Suggestion: Explicitly note "Format as markdown table" or provide exact markdown syntax

2. **Cross-reference validation not in success criteria**
   - Location: Step 9, lines 104-109
   - Note: Success criteria mention "references Gap 4" but validation section (lines 98-102) mentions "testing.md" as alternative
   - Suggestion: Clarify that either "Gap 4" or "testing.md" is acceptable, or specify which is required

3. **Phase 2 dependency statement location**
   - Location: Line 7
   - Note: Dependency clearly stated in header but not repeated in Step 9 context (line 18 mentions it was defined, not that it's complete)
   - Suggestion: Add explicit "Prerequisite: Phase 2 committed" in Step 9 context section

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| FR-1 (conformance cycles mandatory) | Satisfied | Step 9 implements plan-tdd/plan-adhoc updates |
| FR-5 (vet alignment standard) | Satisfied | Step 10 implements vet-fix-agent update |
| DD-1 (conformance as executable contracts) | Satisfied | Step 9 lines 64-77 references DD-1 explicitly |
| DD-5 (vet alignment always-on) | Satisfied | Step 10 lines 116-118 references DD-5 explicitly |

**Gaps**: None. All Phase 3 requirements covered.

---

## Positive Observations

- Dependency on Gap 4 (Phase 2) clearly stated multiple times (lines 7, 18-20)
- Both steps include objective, implementation, success criteria structure
- File paths are correct (plan-tdd, plan-adhoc, vet-fix-agent all exist in agent-core/)
- Design decision references accurate (DD-1 lines 64-77, DD-5 lines 121-135)
- Content blocks (~15 lines for each planning skill, ~5 lines for vet-fix-agent) match design estimates
- Report paths follow convention (plans/.../reports/step-N-execution.md)
- Validation steps include reading updated files to verify changes
- Rationale clearly explains why changes matter (translation loss prevention, conformance vs structure)

## Recommendations

1. **Before execution**: Haiku executor should Read plan-tdd/SKILL.md and plan-adhoc/SKILL.md to identify exact section names for integration locations, then update the implementation guidance with specific section anchors

2. **Content integration**: When editing skills, use Edit tool to insert content at natural boundaries (after existing section, before next heading) rather than searching for "likely" locations

3. **Checkpoint verification**: At Phase 3 checkpoint, verify that Gap 4 changes are present in testing.md before considering Phase 3 complete (defense-in-depth validation)

## Next Steps

1. Fix integration location guidance for plan-tdd (Step 9 implementation section)
2. Fix integration location guidance for plan-adhoc (Step 9 implementation section)
3. Optionally clarify cross-reference requirements (Gap 4 vs testing.md)
4. Execute Phase 3 after Phase 2 is committed
