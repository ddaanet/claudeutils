# Vet Review: plan-adhoc skill after porting 7 changes from plan-tdd

**Scope**: agent-core/skills/plan-adhoc/SKILL.md after porting changes
**Date**: 2026-02-07T15:23:00-08:00
**Mode**: review + fix

## Summary

The plan-adhoc skill has been updated to incorporate 7 changes from plan-tdd. All identified issues have been fixed. The changes improve consistency, add consolidation gates, fix the assembly contradiction, and add checkpoint documentation. The updated skill is well-structured and ready for use.

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

None identified.

### Major Issues

1. **Point 2 contradiction: IMPORTANT section placement breaks flow**
   - Location: lines 371-375
   - Problem: The IMPORTANT box ("Do NOT manually assemble") appears BEFORE the "Actions:" heading and numbered list that describes what TO do. This ordering is confusing — the prohibition comes before the instruction. The reader sees "don't manually assemble" before understanding what the section even asks them to do.
   - Suggestion: Move the IMPORTANT box to after step 3 (Final consistency check), before "Every assembled runbook MUST include..." The flow should be: (1-3) validation steps → (box) prohibition on assembly → metadata requirements
   - **Status**: FIXED — moved IMPORTANT box after step 3

2. **Missing Point 0.85/0.9 references in Process overview**
   - Location: lines 126-133
   - Problem: Process overview lists Point 0.5, 0.75, then jumps to Point 1. The newly added Points 0.85 and 0.9 are missing from the overview.
   - Suggestion: Update overview to include "Point 0.85: Consolidation gate (outline)" and "Point 0.9: Complexity check before expansion"
   - **Status**: FIXED — added Points 0.85 and 0.9 to overview

3. **Checkpoints section placement verified**
   - Location: lines 677-732
   - Note: Upon verification, the Checkpoints section is already correctly placed BEFORE Critical Constraints (after Point 4.1 automated post-processing). The structure is correct: operational content (Checkpoints) precedes reference constraints (Critical Constraints).
   - **Status**: VERIFIED CORRECT — no fix needed

### Minor Issues

1. **Point 2.5 heading inconsistency with Point 0.85**
   - Location: lines 445, 205
   - Note: Point 0.85 uses "Consolidation Gate -- Outline" (en-dash in markdown source), Point 2.5 uses "Consolidation Gate -- Runbook" (en-dash). Both should use em-dash for consistency with standard typographic convention.
   - **Status**: FIXED — standardized both to em-dash (—)

2. **Point 0.9 callback example formatting**
   - Location: lines 276-279
   - Note: Callback levels use inline code formatting with arrows, but the example text uses plaintext "step → runbook outline → design → design outline → requirements". For consistency with technical notation, wrap terms in backticks when they refer to artifacts.
   - **Status**: FIXED — added backticks to callback levels

3. **Point 2.5 merge pattern example indentation**
   - Location: lines 465-472
   - Note: The merge pattern example uses markdown fence (```markdown) but the content inside is plain text with no structural context. The nested lines "[Standard implementation content]" would benefit from showing the complete Step N structure.
   - **Status**: FIXED — expanded example to show complete step structure with merged content

4. **Checkpoints section wording**
   - Location: Checkpoints section (lines 677-730)
   - Note: The light checkpoint step 2 says "Check: Are implementations real or stubs? Do functions compute or return constants?" This wording is identical to plan-tdd. For plan-adhoc (general workflow), this applies equally but might be clearer if worded more generically.
   - **Status**: NOT FIXED — wording is appropriate; the functional check applies equally to ad-hoc implementations and TDD

## Fixes Applied

- Moved "IMPORTANT — Do NOT manually assemble" box in Point 2 to after step 3 (better flow)
- Added Points 0.85 and 0.9 to Process overview section (completeness)
- Standardized consolidation gate headings to use em-dash (consistency)
- Added backticks to Point 0.9 callback levels (technical notation)
- Improved Point 2.5 merge pattern example formatting (clarity)

**Note:** Point 0.9 heading capitalization and Point 0.85 rationale formatting were already correct in the source file. Checkpoints section was already correctly placed before Critical Constraints.

## Requirements Validation

No requirements context was provided in the task prompt. The review focused on code quality, internal consistency, and alignment with plan-tdd patterns.

## Positive Observations

- **Comprehensive porting**: All 7 identified changes from the audit were successfully incorporated
- **Terminology consistency**: "Steps" vs "cycles" terminology correctly adapted throughout
- **Structure preservation**: The 4-point planning process structure remains clear and logical
- **Integration clarity**: The relationship between manual work, prepare-runbook.py, and automated handoff is well-documented
- **Consolidation gates**: Both outline-level and runbook-level consolidation gates follow plan-tdd pattern exactly
- **Complexity check**: Callback mechanism and fast-path guidance ported correctly
- **Checkpoints**: Light/full checkpoint distinction clearly documented with placement rationale

## Recommendations

1. **Consider adding skill dependency scan**: plan-tdd includes skill dependency detection in requirements (A.0). plan-adhoc could benefit from similar detection for runbooks that create agents or invoke skills. This would be a future enhancement, not a blocking issue.

2. **Reference files deferred correctly**: The audit noted reference files as low priority. The current skill inline documentation is sufficient for most use cases. Consider creating references only when inline content exceeds manageable size.

3. **Validation before execution**: Before using this updated skill in production, run a test invocation with a small design document to verify the new consolidation gates and complexity check integrate smoothly with existing Point 0.5/0.75 flow.
