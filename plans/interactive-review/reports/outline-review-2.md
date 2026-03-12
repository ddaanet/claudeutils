# Outline Review: interactive-review (Rev 2)

**Artifact**: plans/interactive-review/outline.md
**Date**: 2026-03-12
**Mode**: review + fix-all (PDR)

## Summary

Post-user-review outline with strong grounding and clear decision rationale. All decisions are selected (not "explore options") with traceable justification to Fagan, Phabricator, and cognitive load research. Three major issues found: FR-4 vocabulary deviation undocumented, iteration guard implementation mechanism unspecified, and batch-apply vs immediate side-effect distinction unclear. All fixed. Prior review (outline-review.md) fixes remain intact.

**Overall Assessment**: Ready

## Requirements Traceability

| Requirement | Outline Section | Coverage | Notes |
|-------------|-----------------|----------|-------|
| FR-1 | D-5, D-9 | Complete | Item-by-item with degenerate single-iteration fallback |
| FR-2 | D-7 | Complete | 6 artifact types with detection patterns + natural-language override |
| FR-3 | D-4 | Complete | Domain-relevant recall per item, null recall silent |
| FR-4 | D-1, D-4 | Complete | 4 explicit verdicts (a/r/k/s); deviations from FR-4 now documented (discuss implicit, absorb folded into kill, skip added) |
| FR-5 | D-2 | N/A | Lifted by user; batch-apply replaces immediate edits |
| FR-6 | D-6 | Complete | Learn/pending/brief as immediate side effects; absorb transfers deferred to batch-apply (now explicit) |
| FR-7 | D-8 | Complete | Summary: N approved/revised/killed/skipped + cross-item outputs |
| C-1 | Approach, D-9 | Complete | Extension within /proof, not separate skill |
| C-2 | D-6 | Complete | Implicit discussion reuses reword-accumulate-sync scoped to one item |

**Traceability Assessment**: All active requirements covered. FR-5 correctly treated as lifted. FR-4 deviations now explicitly documented with justification.

## Scope-to-Component Traceability

Single-component design (SKILL.md + references/item-review.md). All scope items trace to affected files.

| Scope IN Item | Component | Notes |
|---------------|-----------|-------|
| Item-by-item iteration mode | SKILL.md | D-5, D-9 |
| Verdict vocabulary (4 explicit + kill sub-actions) | SKILL.md | D-1 |
| Orientation phase | SKILL.md | D-3 |
| Batch-apply with accumulation | SKILL.md + references/item-review.md | D-2 |
| Per-item recall context | SKILL.md | D-4 |
| Granularity detection | references/item-review.md | D-7 |
| Implicit discussion | SKILL.md | D-6, reuses existing mechanics |
| Iteration guards | SKILL.md | D-6, behavioral instruction (same pattern as anti-patterns section) |
| Normal loop actions (learn, pending, brief) | SKILL.md | D-6 |
| Cross-item outputs | SKILL.md | D-6, FR-6 |
| Review summary | SKILL.md | D-8 |
| Single loop path | SKILL.md | D-9 |
| Linear iteration with revisit | SKILL.md | D-5 |
| Multi-file single artifact | inherited | Existing /proof glob handling; no new implementation |

**Scope Assessment**: All items assigned. No orphans. Multi-file support correctly identified as inherited.

## Cross-Component Interface Compatibility

Single component — no cross-component interfaces to verify. Internal interface (verdict accumulation list → batch-apply) is well-specified in D-2 with explicit format.

## Review Findings

### Critical Issues

None.

### Major Issues

1. **FR-4 vocabulary deviation undocumented**
   - Location: D-1
   - Problem: FR-4 specifies 5 verdicts (approve, revise, kill, discuss, absorb). Outline reduces to 4 explicit (a/r/k/s) — discuss becomes implicit, absorb becomes kill sub-action, skip added. These are user-validated design decisions but the deviation from FR-4's original vocabulary was not noted. A reader comparing requirements to design sees a mismatch with no explanation.
   - Fix: Added explicit "FR-4 deviation" note at top of D-1 documenting all three changes with justification reference.
   - **Status**: FIXED

2. **Iteration guard implementation mechanism unspecified**
   - Location: Scope IN, D-6
   - Problem: "No direct edits during iteration" and "refuses execution-oriented requests" — but no specification of how. Is this a behavioral instruction in SKILL.md prose, a structural gate, or a hook? For a SKILL.md extension, the enforcement mechanism matters.
   - Fix: Scope IN item annotated: behavioral instruction in SKILL.md, same enforcement pattern as existing /proof anti-patterns section.
   - **Status**: FIXED

3. **Batch-apply vs immediate side-effect distinction unclear**
   - Location: D-6 cross-item outputs
   - Problem: D-2 says verdicts accumulate for batch-apply. D-6 says cross-item outputs (learn, pending, brief) are captured via loop actions. But FR-6 acceptance says "Discussion that surfaces a task -> p: semantics applied inline." A reader could think batch-apply means ALL outputs are deferred, or conversely that FR-6's "immediately" contradicts D-2. The two categories (immediate side effects vs deferred verdict application) were not distinguished.
   - Fix: Added explicit distinction in D-6: loop actions are immediate side effects; absorb transfers are deferred to batch-apply alongside other verdict edits.
   - **Status**: FIXED

### Minor Issues

1. **D-6 terminal actions list inconsistent with D-8**
   - Location: D-6
   - Problem: D-6 listed terminal actions as "apply, discard, handoff." D-8 defines apply and discard. "Handoff" appeared only in D-6 with no D-8 specification. Meanwhile D-8 listed "revisit" as terminal, but revisit re-enters the loop.
   - Fix: D-6 terminal list reduced to "apply, discard" (matching D-8). D-8 "revisit" reclassified as loop action with explicit note that it returns to iteration.
   - **Status**: FIXED

2. **Skip verdict design addition not flagged**
   - Location: D-4 verdict prompt
   - Problem: `skip` is a design addition beyond FR-4's vocabulary. Prior review recommended confirming with user. The outline presented it without marking the deviation.
   - Fix: Added bracketed annotation to verdict prompt noting skip is a design addition beyond FR-4.
   - **Status**: FIXED

3. **Multi-file single artifact scope item lacks implementation note**
   - Location: Scope IN
   - Problem: Listed as in-scope but no corresponding design decision. Existing /proof already handles glob patterns (SKILL.md line 37). Without annotation, reads as new work.
   - Fix: Annotated scope item: inherited from existing /proof, no new implementation; D-7 granularity detection applies per-file within composite.
   - **Status**: FIXED

## Fixes Applied

- D-1 — added FR-4 deviation note documenting all vocabulary changes from original requirement
- D-4 verdict prompt — annotated skip as design addition beyond FR-4
- D-6 terminal actions — removed "handoff", reduced to "apply, discard" matching D-8
- D-6 cross-item outputs — added explicit distinction between immediate side effects (loop actions) and deferred verdict application (batch-apply)
- D-8 "revisit" — reclassified from terminal action to loop action with explicit note
- Scope IN "Iteration guards" — annotated implementation mechanism (behavioral instruction)
- Scope IN "Multi-file single artifact" — annotated as inherited behavior, not new implementation

## Positive Observations

- Every key decision cites specific frameworks with rationale for adaptation (Fagan, Phabricator, cognitive load research)
- User review session decisions (D-1 through D-9) are faithfully encoded with clear attribution
- FR-5 lift handled cleanly — D-2 explains the rationale and structural prevention of known agent failure pattern
- Dogfooding feedback (blockquote rendering, table-heavy TOC, missing orientation) all incorporated
- Kill sub-action design elegantly preserves absorb capability within the 3-5 convergence range
- Open questions are genuine (skip outcome semantics, grounding report divergence) rather than placeholder

## Recommendations

- Supplementary grounding (D-1) should be scoped before design phase — artifact-type-dependent verdict vocabularies need research across backlog refinement, architecture review, and process review domains
- Per-item size threshold for hierarchical granularity (D-7) needs empirical grounding — cognitive load per review segment literature
- Skip outcome semantics (open question) should be resolved during user discussion before design

---

**Ready for user presentation**: Yes
