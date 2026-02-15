# Vet Review: review-plan SKILL.md Section 11 (LLM Failure Modes)

**Scope**: Section 11.1-11.3 with type-specific detection patterns
**Date**: 2026-02-15T12:00:00Z
**Mode**: review + fix

## Summary

Reviewed Section 11 (LLM Failure Modes) after adding **TDD:** and **General:** labels with type-specific detection patterns. All three sub-sections (11.1 Vacuity, 11.2 Dependency Ordering, 11.3 Density) include explicit detection criteria for both phase types. Section is well-structured with clear type-specific guidance.

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

None.

### Major Issues

None.

### Minor Issues

1. **11.1 Integration wiring criterion lacks type label**
   - Location: agent-core/skills/review-plan/SKILL.md:265
   - Note: "Integration wiring items where called function already tested" appears after General detection but has no **TDD:** or **General:** label. Context suggests TDD-specific (testing already-tested functions), but unlabeled.
   - **Status**: FIXED

2. **11.2 Foundation-first principle unlabeled**
   - Location: agent-core/skills/review-plan/SKILL.md:269
   - Note: "Foundation-first within phases: existence → structure → behavior → refinement" applies to both types but has no indication it's universal
   - **Status**: FIXED

## Fixes Applied

- agent-core/skills/review-plan/SKILL.md:265 — Added **TDD:** label to integration wiring criterion (TDD-specific: testing integration of already-tested function)
- agent-core/skills/review-plan/SKILL.md:269 — Added "(all types)" annotation to foundation-first principle (universal ordering guideline)

## Positive Observations

- Clear **TDD:** and **General:** labels distinguish detection patterns between phase types
- Each sub-section includes concrete examples for both types
- General detection patterns correctly capture behavioral vacuity (step N+1 achievable by extending N)
- Dependency ordering includes both output-reference and file-state patterns for general phases
- Density detection covers file-level composability and trivial config changes
- Fix guidance provided for each failure mode

## Recommendations

None — section achieves requirements with explicit type-specific detection criteria.
