# Deliverable Review: continuation-prepend

**Date:** 2026-02-28
**Methodology:** agents/decisions/deliverable-review.md

## Inventory

| Type | File | + | - |
|------|------|---|---|
| Test | tests/test_continuation_integration.py | +93 | -0 |
| Agentic prose | agent-core/fragments/continuation-passing.md | +6 | -2 |
| Agentic prose | agent-core/skills/handoff/SKILL.md | +1 | -1 |
| Agentic prose | agent-core/skills/inline/SKILL.md | +3 | -2 |
| Agentic prose | agent-core/skills/orchestrate/references/continuation.md | +15 | -3 |

5 files, 110 net lines. All files match plan.md scope exactly — no missing or unspecified deliverables.

## Critical Findings

None.

## Major Findings

1. **Protocol step ordering diverges from design spec**
   - Design (problem.md:27-39): "If empty → stop" at step 2 (before prepend step 3)
   - Implementation (continuation-passing.md:41-46): "If no continuation" at step 4 (after prepend step 2)
   - Axis: conformance
   - Impact: Design prohibits prepending to empty continuations (step 2 stops first). Implementation allows it — a skill with no continuation could prepend entries, creating a chain from nothing. Test `test_prepend_empty_continuation_creates_chain` validates the implementation behavior but contradicts design step ordering. The same divergence propagates to inline/SKILL.md (steps 2-4) and handoff/SKILL.md (paragraph ordering).
   - Resolution: Either update problem.md to match implementation (move empty-check after prepend) or update implementation to match design (move empty-check before prepend and remove the empty-prepend test). The implementation's ordering is arguably more useful — it enables subroutine injection on standalone invocations — but the design should reflect the chosen semantics.

## Minor Findings

**Protocol clarity:**

2. Steps 3/4 in continuation-passing.md lost explicit conditionality compared to old protocol. Old: "If continuation present: peel..." / "If no continuation: default-exit" (clear if/else). New: step 3 "Peel first entry..." (appears unconditional) / step 4 "If no continuation: default-exit." An agent following literally could attempt step 3 when no continuation exists. Same pattern in inline/SKILL.md steps 3-4. Low practical risk (agents handle conditional semantics well) but less precise than the original.

**Pre-existing (not introduced by this PR):**

3. Handoff "If empty: stop" vs `default-exit: ["/commit"]` — pre-existing inconsistency noted by corrector review. The `--commit` flag handles commit invocation outside CPS.
4. `/worktree` has `cooperative: true` but no §Continuation section — pre-existing, not in Cooperative Skills table.
5. `/design` and `/runbook` listed as cooperative in table but lack `cooperative: true` frontmatter — pre-existing, explicitly out of scope.

## Gap Analysis

| Design Requirement (problem.md) | Status | Evidence |
|----------------------------------|--------|----------|
| Protocol extended with optional prepend step | Covered | continuation-passing.md:41-44 |
| Append-only invariant for existing entries | Covered | All 4 prose files state invariant |
| Skills that don't prepend skip step | Covered | continuation-passing.md:44 |
| Backward compatible (no infrastructure changes) | Covered | No hook/transport/frontmatter changes |
| Fragment updated | Covered | continuation-passing.md steps 2-4 |
| inline/SKILL.md §Continuation updated | Covered | inline/SKILL.md:168-171 |
| handoff/SKILL.md §Continuation updated | Covered | handoff/SKILL.md:153 |
| orchestrate continuation reference updated | Covered | orchestrate/references/continuation.md:11-14, 40-49 |
| Integration test: prepend + consume + resume | Covered | TestContinuationPrepend (6 tests) |
| Step ordering: empty check before prepend | **Diverged** | Implementation swaps steps 2-3 vs design |

## Summary

- Critical: 0
- Major: 1 (step ordering conformance)
- Minor: 2 new + 3 pre-existing

The implementation is functionally correct and the test suite comprehensive (6 tests covering core path, multi-prepend, transport format, backward compat, and edge case). The single major finding is a conformance gap between the design spec's step ordering and the implementation's — they disagree on whether prepending to empty continuations is permitted. This requires a design-or-implementation alignment decision but does not affect correctness for the standard use case (prepending to a non-empty continuation).
