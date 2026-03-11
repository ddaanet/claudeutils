## 2026-03-11: Origin — system invariants + pipeline traceability

**Problem:** Workflow leaks (merge drops, skipped gates, committed regressions) are violations of unstated system properties. Existing approach is piecemeal: detect leak → write learning → add rule/hook. No shared framework for asking "which properties are defended?"

**Two levels identified in discussion:**

1. **System invariants** — define what properties the system guarantees. Currently implicit across fragments, learnings, and decision files. Examples: merge preserves all session entries, append-only files never lose lines, every pending task references a plan directory, full test suite runs before commit. This level produces a specification document.

2. **Pipeline traceability** — ensure requirements survive each workflow stage (requirements → design → runbook → steps → implementation → review). Key finding: until recently, nothing checked FR coverage between requirements authoring and deliverable review. Requirements could silently drop at any intermediate stage. This level produces a mechanism (traceability checks at stage boundaries).

**Interaction:** Independent problems. Perfect pipeline traceability doesn't give you a system spec. A complete invariant spec doesn't prevent FR loss between stages.

**Sequencing:** Start with requirements definition / grounding for the invariant vocabulary (#1), then build pipeline traceability (#2).

**Absorbs/reframes:**
- quality-grounding (partially) — invariant specification subsumes "are claims grounded"
- review-gate — one enforcement instance within the traceability framework

**Key insight from discussion:** The value isn't primarily in auditing after the fact — it's in the traceability matrix: property → enforcement mechanism → verification method. The audit becomes "which properties lack enforcement?" rather than "what leaked this time?"

**Enforcement categories (from defense-in-depth):**
- Structural properties (checkable against artifacts — deliverable review handles these today)
- Process properties (behavioral invariants of execution — require runtime enforcement, not post-hoc review)
