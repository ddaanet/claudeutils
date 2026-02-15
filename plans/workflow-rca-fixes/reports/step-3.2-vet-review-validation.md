# Vet Review: vet-requirement.md updates (Step 3.2)

**Scope**: vet-requirement.md 4-status taxonomy integration and validation
**Date**: 2026-02-15T00:00:00Z
**Mode**: review + fix

## Summary

Reviewed vet-requirement.md updates for 4-status taxonomy integration (FIXED, DEFERRED, OUT-OF-SCOPE, UNFIXABLE), UNFIXABLE validation protocol, and execution context enforcement. Document implements taxonomy correctly with concrete validation steps and structured field requirements. Found 3 major issues related to terminology precision, reference path accuracy, and delegation template completeness.

**Overall Assessment**: Ready (after fixes)

## Issues Found

### Critical Issues

None.

### Major Issues

1. **Resume protocol references "vet-fix-agent" without clarifying delegation mechanism**
   - Location: vet-requirement.md:106
   - Problem: Step 4 says "resume vet-fix-agent for reclassification" but doesn't specify mechanism (new Task call vs continuation). Without mechanism clarity, orchestrators may re-delegate fresh instead of providing guidance for re-classification.
   - Suggestion: Add note: "Resume by delegating to vet-fix-agent again with reclassification guidance in prompt (no continuation mechanism available)"
   - **Status**: FIXED

2. **Delegation template missing "Do NOT flag items outside provided scope" constraint**
   - Location: vet-requirement.md:65-86
   - Problem: Line 59 mentions this constraint as mitigation, but delegation template (lines 65-86) does not include it. Without the constraint in the template, delegating agents may omit it.
   - Suggestion: Add to delegation template after Requirements section: "**Constraints:** Do NOT flag items outside provided scope (scope OUT list)."
   - **Status**: FIXED

### Minor Issues

1. **Four-status taxonomy not explicitly listed in introduction**
   - Location: vet-requirement.md:1-40
   - Note: The four statuses (FIXED, DEFERRED, OUT-OF-SCOPE, UNFIXABLE) are introduced at line 94 in the detection protocol section, but not mentioned in the overview. Adding a forward reference in the "Vet process" section would improve navigability.
   - **Status**: FIXED

## Fixes Applied

- vet-requirement.md:106 — Added clarification that resume means new delegation with reclassification guidance (no continuation available)
- vet-requirement.md:85 (after Requirements) — Added Constraints section to delegation template with "Do NOT flag items outside provided scope"
- vet-requirement.md:27 (after step 5) — Added forward reference to four-status taxonomy for reader orientation

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| FR-9 | Satisfied | Lines 110-114: validation steps check subcategory code, investigation summary, scope OUT overlap, with resume protocol for failed validation |
| FR-10 | Partial | Lines 47-51: structured field requirements with "Fail loudly" directive. Full implementation requires orchestrate skill update (Step 3.3, out of scope). Fragment provides enforcement guidance as specified. |

**Gaps:** FR-10 orchestrate template enforcement is documented here but not yet implemented in orchestrate skill (Step 3.3).

---

## Positive Observations

- Clear distinction between DEFERRED (known future work) and OUT-OF-SCOPE (irrelevant) with rationale
- Concrete validation steps with mechanical grep protocol (consistent with weak orchestrator pattern)
- Structured field enforcement catches empty prose early (lines 47-51)
- Investigation gate checklist format matches taxonomy exactly (4 gates: scope OUT, design deferral, codebase patterns, conclusion)
- Resume protocol provides exit path for misclassified UNFIXABLE (prevents blocking on agent error)

## Recommendations

- When implementing FR-10 in orchestrate skill (Step 3.3), ensure enforcement uses the exact field structure from delegation template (lines 70-83)
- Consider adding example of UNFIXABLE validation failure → resume guidance in detection protocol section (would clarify resume flow)
