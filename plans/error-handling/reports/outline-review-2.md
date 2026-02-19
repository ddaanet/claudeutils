# Outline Review: Error Handling Framework (Round 2)

**Artifact**: plans/error-handling/outline.md
**Date**: 2026-02-18
**Mode**: review + fix-all
**Prior review**: plans/error-handling/reports/outline-review.md (2026-02-13)

## Summary

The outline has been substantially strengthened since the first review. All three open questions are resolved with empirical data. Grounding against five established frameworks (Avižienis FEF, Saga, MASFT, Temporal, LLM agentic failures) adds vocabulary precision and structural completeness. The six key decisions (D-1 through D-6) are well-reasoned with clear rationale. Issues found were structural (duplicate sections, incomplete Architecture coverage of Layer 0, retry scope ambiguity in taxonomy) rather than fundamental.

**Overall Assessment**: Ready

## Requirements Traceability

Requirements extracted from exploration report gap analysis and grounding report corrections (no standalone requirements.md exists).

| Requirement | Outline Section | Coverage | Notes |
|-------------|-----------------|----------|-------|
| FR-1: Task failure states | D-2, Architecture 2, Phase 3 | Complete | blocked/failed/canceled with Temporal grounding |
| FR-2: CPS chain error recovery | D-1, Architecture 3, Phase 4 | Complete | Abort-and-record, pivot transactions, idempotency |
| FR-3: Escalation acceptance criteria | D-3, Architecture 1, Phase 2 | Complete | Three measurable criteria, all required |
| FR-4: Rollback strategy | D-5, Architecture 1, Phase 2 | Complete | Git-atomic-snapshot, revert to step start |
| FR-5: Error taxonomy extension | Architecture (Error Taxonomy), Phase 1 | Complete | 5 categories, fault/failure vocab, retryable/non-retryable |
| FR-6: Timeout handling | Resolved Questions Q1, Architecture 1 | Complete | Dual-signal: max_turns ~150 (now), duration ~600s (deferred) |
| FR-7: Hook error protocol | D-6, Phase 5 | Complete | Stderr visibility, degraded mode, formalized |
| FR-8: Cross-system documentation | Phase 5, Integration Points | Complete | Consolidation as final phase |
| FR-9: Agent-level classification | Architecture (Error Taxonomy), Phase 1 | Complete | Tier-aware: sonnet/opus self-classify, haiku raw |
| FR-10: Fault prevention layer | Approach L0, Architecture (Layer 0), Phase 0 | Complete | prerequisite-validation.md reference |
| NFR-1: Fault/failure vocabulary | Error Taxonomy section | Complete | Avižienis FEF chain mapping |
| NFR-2: Retryable/non-retryable | Error Taxonomy section, D-1 | Complete | Subsystem-specific response clarified |
| NFR-3: Inter-agent misalignment | Error Taxonomy (Category 5) | Complete | MASFT FC2, detection via existing review pipeline |
| NFR-4: Git-atomic-snapshot assumption | D-5 | Complete | Explicit assumption with breakage conditions |
| NFR-5: Pivot transactions | D-1, Architecture 3 | Complete | Post-orchestrate identified as pivot |
| NFR-6: Idempotency requirement | Architecture 3 | Complete | Recovery operations must be idempotent |

**Traceability Assessment**: All requirements covered

## Review Findings

### Critical Issues

None found.

### Major Issues

1. **Retry scope ambiguity in Error Taxonomy**
   - Location: Error Taxonomy, "Retryable vs non-retryable" subsection
   - Problem: Original text stated "Retryable -> retry with backoff before escalating" as a universal rule, but D-1 explicitly says CPS uses 0 retries (abort-and-record). The taxonomy presented retry-with-backoff as applying to all subsystems, contradicting the CPS-specific decision.
   - Fix: Replaced with subsystem-specific response: orchestration (Layer 2) retries via Sonnet diagnostic; CPS (Layer 4) records classification but aborts regardless. Non-retryable escalates immediately in all subsystems.
   - **Status**: FIXED

2. **Error flow diagram didn't distinguish subsystem paths**
   - Location: Architecture, Error Flow
   - Problem: Single linear flow implied all errors follow same path (classify -> retry if retryable -> escalate). This contradicted D-1 (CPS: 0 retries) and didn't show Layer 0 prevention.
   - Fix: Restructured diagram with Layer 0 entry point and separate orchestration/CPS paths showing different retry behavior.
   - **Status**: FIXED

3. **Layer 0 missing from Architecture section**
   - Location: Architecture section
   - Problem: Layer 0 (fault prevention) was in Approach and Implementation Plan but had no Architecture subsection, unlike Layers 1-4. This created an asymmetry where the most cost-effective layer lacked architectural description.
   - Fix: Added "Fault Prevention (Layer 0)" subsection to Architecture with four concrete prevention points (plan-reviewer, orchestrator clean-tree, commit Gate A, CPS hook validation).
   - **Status**: FIXED

### Minor Issues

1. **Duplicate "Resolved Questions" headers**
   - Location: Lines 45 and 50
   - Problem: Two separate sections ("Resolved Questions" and "Resolved Questions (continued)") broke document structure. Likely artifact of incremental editing.
   - Fix: Merged into single "Resolved Questions" section.
   - **Status**: FIXED

2. **In-scope list incomplete**
   - Location: Scope Boundaries, "In scope"
   - Problem: Missing Layer 0 (fault prevention), timeout handling, and hook error protocol (D-6). These are addressed in the outline body but not listed in the scope summary.
   - Fix: Added fault prevention documentation, timeout, and hook error protocol to in-scope list.
   - **Status**: FIXED

3. **Implementation Plan Phase 2 vague on dirty tree recovery**
   - Location: Phase 2, third bullet
   - Problem: Said "Document recovery paths for dirty tree violations" without referencing D-5 which already defines the rollback strategy.
   - Fix: Changed to reference D-5 explicitly and state the concrete recovery: revert to last clean commit, re-execute step.
   - **Status**: FIXED

4. **Success Metrics missing timeout validation**
   - Location: Success Metrics, Validation subsection
   - Problem: Timeout calibration was a major resolved question with empirical thresholds but Success Metrics didn't include verifying timeout behavior.
   - Fix: Added validation criterion for `max_turns` ~150 against calibration data.
   - **Status**: FIXED

5. **Phase 5 missing hook error protocol**
   - Location: Implementation Plan, Phase 5
   - Problem: D-6 (hook error protocol) had no corresponding implementation plan item. Hook formalization was implied by "consolidation" but not explicit.
   - Fix: Added hook error protocol formalization with three failure modes (crash, timeout, invalid output) and their responses.
   - **Status**: FIXED

6. **Layer 0 missing from Integration Points**
   - Location: Architecture, Integration Points
   - Problem: Listed Layers 1-5 but not Layer 0 (prevention), despite Layer 0 being foundational to all subsystems.
   - Fix: Added Layer 0 entry: "validates preconditions before all subsystems execute."
   - **Status**: FIXED

## Fixes Applied

- Error Taxonomy: retryable/non-retryable response now subsystem-specific (orchestration retries, CPS aborts)
- Error Flow diagram: restructured with Layer 0 entry and separate orchestration/CPS paths
- Architecture: added "Fault Prevention (Layer 0)" subsection with four prevention points
- Resolved Questions: merged duplicate sections into one
- Scope Boundaries: in-scope list expanded with Layer 0, timeout, hook protocol
- Phase 2: references D-5 explicitly, concrete dirty tree recovery
- Phase 5: added hook error protocol formalization (D-6)
- Success Metrics: added timeout validation criterion
- Integration Points: added Layer 0

## Positive Observations

- All three open questions from the first review are now resolved with empirical data or explicit decisions
- Grounding against five frameworks adds rigor without over-engineering (deliberate exclusions documented)
- D-5 git-atomic-snapshot assumption is explicit about when the model breaks
- Tier-aware classification (sonnet/opus self-classify, haiku reports raw) is a pragmatic design that preserves context locality
- Timeout calibration (938 observations, sleep detection heuristic, two independent failure modes) is thorough empirical work
- The "0 retries, extend when needed" stance (D-1) aligns with the project's build-for-current-requirements principle

## Recommendations

- During Phase C (full design), specify the exact session.md recording format for CPS chain failures — what fields appear in Blockers, what context is preserved for `r` resume
- Consider whether Category 5 (inter-agent misalignment) needs its own retryable/non-retryable classification or is always non-retryable
- The `max_turns` ~150 threshold should be documented as a tunable parameter, not a fixed constant, since the calibration data will grow

---

**Ready for user presentation**: Yes
