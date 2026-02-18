# Outline Review: runbook-evolution

**Artifact**: plans/runbook-evolution/outline.md
**Date**: 2026-02-18
**Mode**: review + fix-all

## Summary

The outline is well-structured with clear placement decisions, explicit scope boundaries, and verified insertion points. All in-scope requirements (FR-1, FR-2, FR-3) map to concrete outline sections. Four issues found and fixed: missing anti-pattern coverage for FR-2a, imprecise insertion point description, missing note about existing anti-pattern entry contradicting FR-3c, and missing explicit traceability matrix.

**Overall Assessment**: Ready

## Requirements Traceability

| Requirement | Outline Section | Coverage | Notes |
|-------------|-----------------|----------|-------|
| FR-1 (Prose Atomicity) | Phase 0.75 addition, Anti-patterns | Complete | Directive + anti-pattern entry |
| FR-2a (Migration Consistency) | Phase 0.75 addition, Anti-patterns | Complete | Was missing anti-pattern; added |
| FR-2b (Bootstrapping Ordering) | Phase 0.75 addition | Complete | References existing workflow-advanced.md decision |
| FR-3a (Integration-First) | Testing Strategy, TDD Cycle Planning, Anti-patterns | Complete | New section + cycle guidance + strengthened entry |
| FR-3b (Unit as Supplement) | Testing Strategy, TDD Cycle Planning | Complete | Explicit criteria from requirements |
| FR-3c (Real Subprocesses) | Testing Strategy, Anti-patterns | Complete | Generalizes existing testing.md decision |
| FR-3d (Local Substitutes) | Testing Strategy | Complete | SQLite/local services pattern |
| FR-4 (Deferred Enforcement) | Scope OUT | Deferred | Per requirements: observe FR-3 results first |
| FR-5 (Test Migration) | Scope OUT | Deferred | Per requirements: separate design, depends on FR-3 |

**Traceability Assessment**: All requirements covered. FR-4 and FR-5 correctly deferred per requirements.

## Review Findings

### Critical Issues

None.

### Major Issues

1. **Missing FR-2a anti-pattern coverage**
   - Location: Anti-patterns.md additions section
   - Problem: FR-2a (migration consistency / expand-contract) had no anti-pattern entry. FR-1 and FR-3 had entries; FR-2a was silently omitted. Self-modification without expand/contract is a distinct failure mode worth capturing.
   - Fix: Added "Self-modification without expand/contract" anti-pattern entry referencing FR-2a
   - **Status**: FIXED

2. **Existing anti-pattern contradicts FR-3c**
   - Location: Key Decisions section
   - Problem: "Missing integration cycles" entry in anti-patterns.md (line 18) recommends "with mocked I/O" as the correction. This contradicts FR-3c (real subprocesses for subprocess domains). The outline said "strengthens" the entry without noting the contradiction that needs resolving.
   - Fix: Added Key Decision noting the existing entry's "mocked I/O" recommendation contradicts FR-3c and the edit must update it
   - **Status**: FIXED

### Minor Issues

1. **Imprecise insertion point description**
   - Location: TDD Cycle Planning Guidance addition
   - Problem: Description said "after GREEN specification" but the meaningful landmark is "before 'Classify and add investigation prerequisites'" (line 536). The content logically belongs between GREEN spec and prerequisites — saying "after GREEN" is correct but less precise.
   - Fix: Updated description to "after line 535, before 'Classify and add investigation prerequisites'"
   - **Status**: FIXED

2. **Missing explicit traceability matrix**
   - Location: End of outline (before Open Questions)
   - Problem: FR references were scattered through section descriptions but no consolidated mapping existed. Outline review protocol requires explicit requirement-to-section traceability.
   - Fix: Added Requirements Traceability table with all 9 FRs mapped
   - **Status**: FIXED

3. **Missing FR tags on cycle planning items**
   - Location: TDD Cycle Planning Guidance addition
   - Problem: The two bullet points didn't reference which FRs they addressed. Integration-first maps to FR-3a; wire-then-isolate maps to FR-3b.
   - Fix: Added FR references in parentheses
   - **Status**: FIXED

## Fixes Applied

- Anti-patterns.md additions — added FR-2a "Self-modification without expand/contract" entry
- Anti-patterns.md additions — noted existing entry's "mocked I/O" contradicts FR-3c, needs update
- Key Decisions — added decision about existing anti-pattern entry needing FR-3c alignment
- TDD Cycle Planning section — clarified insertion point description
- TDD Cycle Planning section — added FR-3a/FR-3b tags to bullet items
- Added Requirements Traceability table before Open Questions

## Positive Observations

- Insertion points verified against actual SKILL.md line numbers (253, 535, 791 all confirmed correct)
- Single holistic edit per file is consistent with FR-1 (prose atomicity applied to the implementation itself)
- Scope boundaries mirror requirements exactly (same IN/OUT)
- Key decision about FR-1 exception mechanism (only FR-2a, no generic escape hatch) prevents erosion
- "No open questions" is credible given the well-specified requirements and exploration report

## Recommendations

- During design discussion: confirm whether the existing "Missing integration cycles" anti-pattern entry should be rewritten or appended to (rewrite is cleaner given the mocked I/O contradiction)
- The xfail checkpoint pattern (lines 767-770) is adjacent to FR-3a but the outline correctly leaves it unchanged — worth confirming this is intentional during discussion

---

**Ready for user presentation**: Yes
