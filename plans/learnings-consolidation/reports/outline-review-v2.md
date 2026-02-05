# Outline Review: learnings-consolidation

**Artifact**: plans/learnings-consolidation/outline.md
**Date**: 2026-02-05T19:45:00Z
**Mode**: review + fix-all

## Summary

Outline is sound and complete. Approach correctly interprets automation as "invocation of existing logic" rather than reimplementation. Two-test model (trigger vs freshness) is well-motivated. Git-active days measurement addresses calendar time pitfalls. Sub-agent pattern properly uses embedded skill content, not Skill tool. All fixes applied were clarifications and completeness improvements.

**Overall Assessment**: Ready

## Requirements Traceability

All functional requirements from requirements.md are explicitly addressed:

| Requirement | Outline Section | Coverage | Notes |
|-------------|-----------------|----------|-------|
| FR-1: Automated consolidation trigger | Key Decisions #1, Threshold Behavior | Complete | Handoff integration point specified |
| FR-2: Git-active days measurement | Key Decisions #2, Parameters Summary | Complete | Algorithm and time unit explicit |
| FR-3: Tiered thresholds (soft + hard) | Threshold Behavior | Complete | Size (150 lines) + staleness (14 days) |
| FR-4: Freshness threshold (7 active days) | Two-Test Model, Threshold Behavior | Complete | Per-entry filtering independent of trigger |
| FR-5: Minimum batch size (3 entries) | Key Decisions #5, Parameters Summary | Complete | Overhead threshold defined |
| FR-6: Age calculation (git blame) | Key Decisions #2, Implementation Components | Complete | Per-header git blame → active days |
| FR-7: Sub-agent with preloaded skill | Key Decisions #4, Implementation Components | Complete | remember-task.md agent pattern |
| FR-8: Quiet execution pattern | Key Decisions #4 | Complete | File output, filepath return |
| FR-9: Partial failure handling | Partial Failure Handling | Complete | Escalation, not autonomous resolution |

**Traceability Assessment**: All requirements covered with explicit implementation mapping.

## Review Findings

### Critical Issues

None found.

### Major Issues

None found.

### Minor Issues

1. **Missing staleness parameter value**
   - Location: "Staleness-triggered consolidation" section
   - Problem: "N+ active days" not specified; requirements discussion suggests 14 days but outline doesn't commit
   - Fix: Added note specifying N=14 active days (must exceed freshness threshold)
   - **Status**: FIXED

2. **Batch sizing not in scope boundaries**
   - Location: "Scope Boundaries" section
   - Problem: Batch size determination (counting entries meeting threshold) is in scope but not listed
   - Fix: Added "Batch size determination (count entries meeting freshness threshold)" to in-scope list
   - **Status**: FIXED

3. **Parameters table missing default values**
   - Location: "Parameters Summary" section
   - Problem: Table shows measurement but not configured values
   - Fix: Added "Default" column with concrete thresholds (150 lines, 14 days staleness, 7 days freshness, 3 batch)
   - **Status**: FIXED

4. **Implementation components lack detail**
   - Location: "Implementation Components" section
   - Problem: Component list too sparse; doesn't convey I/O contracts or algorithms
   - Fix: Expanded each component with input/output/algorithm details
   - **Status**: FIXED

5. **Missing requirements traceability section**
   - Location: End of document
   - Problem: No explicit FR-* mapping to outline sections
   - Fix: Added "Requirements Traceability" section with complete mapping
   - **Status**: FIXED

6. **Edge case: partial success not covered**
   - Location: "Risk Assessment" section
   - Problem: Doesn't address case where entries removed from learnings.md but consolidation fails mid-stream
   - Fix: Added edge case with mitigation (report contains removed entries list)
   - **Status**: FIXED

## Fixes Applied

- Line 58: Added staleness parameter default (N=14 active days) with rationale
- Line 83: Added "Batch size determination" to in-scope list
- Line 97: Added "Default" column to Parameters Summary table with concrete values
- Line 91: Expanded Implementation Components with I/O contracts and algorithms (4 components × 3-4 details each)
- Line 111: Added Requirements Traceability section with FR-* mappings
- Line 109: Added edge case for partial consolidation failure with mitigation

## Positive Observations

- **Two-test separation is well-motivated** — Trigger (should we?) vs freshness (what to?) addresses different concerns with different thresholds
- **Active days measurement solves real problems** — Immunizes against vacation/weekend/context-reset aging artifacts
- **Reuse over reimplementation** — Correctly frames automation as invocation, not duplication of `/remember` logic
- **Sub-agent pattern correct** — Recognizes Skill tool limitation in Task agents, uses embedded content
- **Partial failure handling is realistic** — Escalates blockers (target file at limit) instead of autonomous scope expansion
- **Risk assessment acknowledges git edge cases** — git blame with merges/renames is non-trivial; mitigation is skip-not-assume
- **Scope boundaries are explicit** — Clear what's in vs out, particularly memory refactoring deferral

## Recommendations

1. **Test git blame edge cases during implementation** — Merge commits, file renames, squashed commits may produce unexpected ages. Verify behavior with test repo scenarios.

2. **Consider staleness parameter tunability** — 14 active days is reasonable default but users with different work patterns may want adjustment. Make configurable if implementing settings.

3. **Document staleness vs freshness relationship** — Staleness must exceed freshness to avoid immediate re-trigger. This constraint is implicit; consider making explicit in implementation.

4. **Plan for escalation handling** — Outline specifies escalation but doesn't define user-facing workflow. Consider how user sees/responds to "target file at limit" escalation.

5. **Validate minimum batch size assumption** — 3 entries = overhead threshold assumes agent spawn cost > manual consolidation of 1-2 entries. May want to measure actual overhead in practice.

---

**Ready for user presentation**: Yes
