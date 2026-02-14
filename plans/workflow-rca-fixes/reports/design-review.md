# Design Review: Workflow RCA Fixes

**Design Document**: `plans/workflow-rca-fixes/design.md`
**Review Date**: 2026-02-14
**Reviewer**: design-vet-agent (opus)

## Summary

Comprehensive design for 18 prose-edit FRs across 6 phases, with reflexive bootstrapping ordering, three-layer validation, and research-grounded design decisions. The document is thorough, well-structured, and clearly maps every requirement to a phase and target file.

**Overall Assessment**: Ready

## Issues Found and Fixed

### Critical Issues

None found.

### Major Issues

None found.

### Minor Issues

1. **Requirements Dependencies section references wrong FR**
   - Problem: `requirements.md` line 158 says "FR-15 documents requirement" in the `wt/error-handling` dependency, but FR-15 is repetition helper prescription. Should be FR-17 (execution-to-planning feedback).
   - Fix Applied: Not fixed -- issue is in requirements.md, not in the design document under review. The design document correctly associates FR-17 with `wt/error-handling` in Phase 6 and constraint C-4.

2. **Phase 5 restart reasoning could be more precise**
   - Problem: Design says "workflows-terminology.md loaded via @-ref requires restart only for structural changes" to justify no restart. Adding deliverable review as a workflow step is a structural addition to the workflow route, which loads at session start.
   - Fix Applied: Not fixed -- this is a judgment call. The addition is a documentation-only change (adding a step description), not a route change that affects execution routing logic. The planner can assess restart need at planning time.

3. **FR-4 target file naming**
   - Problem: FR-4 in requirements references "each of patterns.md, anti-patterns.md, examples.md" needing general-step sections. Design Phase 5 creates a new `general-patterns.md` rather than editing existing `patterns.md`. This is a design decision (separate file for general patterns) but diverges from requirements acceptance criteria wording.
   - Fix Applied: Not fixed -- design decision is reasonable (separate file avoids polluting TDD-focused patterns.md). Planner should verify acceptance criteria satisfaction.

## Requirements Alignment

**Requirements Source:** `plans/workflow-rca-fixes/requirements.md`

| Requirement | Addressed | Design Reference |
|-------------|-----------|------------------|
| FR-1 | Yes | Phase 2 deliverables table |
| FR-2 | Yes | Phase 2 deliverables table |
| FR-3 | Yes | Phase 2 deliverables table |
| FR-4 | Yes | Phase 5 deliverables table (note: general-patterns.md vs patterns.md) |
| FR-5 | Yes | Phase 4 deliverables table |
| FR-6 | Yes | Phase 6 deliverables table |
| FR-7 | Yes | Phase 3 deliverables table + Vet Status Taxonomy section |
| FR-8 | Yes | Phase 3 deliverables table |
| FR-9 | Yes | Phase 3 deliverables table |
| FR-10 | Yes | Phase 3 deliverables table (two files) |
| FR-11 | Yes | Phase 4 deliverables table |
| FR-12 | Yes | Phase 1 deliverables table + Convention Injection section |
| FR-13 | Yes | Phase 1 deliverables table + Convention Injection section |
| FR-14 | Yes | Phase 5 deliverables table |
| FR-15 | Yes | Phase 5 deliverables table |
| FR-16 | Yes | Phase 5 deliverables table |
| FR-17 | Yes | Phase 6 deliverables table + C-4 constraint |
| FR-18 | Yes | Phase 3 deliverables table + Review-Fix Integration section |
| C-1 | Yes | Problem statement, Key Decision #6 |
| C-2 | Yes | Key Decision #2 |
| C-3 | Yes | Phase 1 review section |
| C-4 | Yes | Phase 6 + out of scope |

**Gaps:** None. All 18 FRs and 4 constraints are addressed.

## Positive Observations

- Reflexive bootstrapping ordering is well-reasoned and the dependency chain is explicit. Each phase's improvements are available to subsequent phases.
- Deliverables tables per phase with FR traceability make planning straightforward -- the planner knows exactly what files to edit and why.
- Research grounding is specific (MAR degeneration of thought, ODC orthogonal classification, ACE knowledge injection) rather than hand-waved.
- Three-layer validation with clear enablement criteria (Phases 1-4 yes, 5-6 no) prevents over-process on low-risk edits.
- Diagnostic review methodology section is practical: priming protocol, artifact-type methodology mapping, feedback paths, and explicit methodology gap acknowledgment.
- Documentation perimeter is comprehensive with both required reading and skill-loading directives.

## Recommendations

- Planner should verify FR-4 acceptance criteria satisfaction given the general-patterns.md vs patterns.md divergence.
- Fix the FR-15/FR-17 reference error in requirements.md during planning or execution.

## Next Steps

- Proceed to `/runbook plans/workflow-rca-fixes/design.md` for runbook generation.
