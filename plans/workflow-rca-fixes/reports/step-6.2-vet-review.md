# Step 6.2 Self-Review: Execution-to-Planning Feedback

**Artifact:** `agents/decisions/orchestration-execution.md`
**FR:** FR-17

## Changes Applied

Added `.Execution Escalation` section with four subsections:

- **When Item-Level Escalation Blocks Execution** — UNFIXABLE items, orchestrator stops, surfaces to user. Cross-references existing `vet-requirement.md` protocol.
- **When Local Recovery Suffices** — Refactor agent within same design, no user input needed, design assumptions hold.
- **When Global Replanning Is Needed** — Four concrete trigger categories: design assumptions invalidated, scope creep accumulation, runbook structure broken, test plan inadequate.
- **Implementation Deferral** — FR-17 documents requirement only; concrete mechanisms deferred to `wt/error-handling`.

Added two memory index entries for discoverability.

## Verification Checklist

- [x] Three escalation tiers documented with clear distinctions
- [x] Global replanning triggers are concrete (four categories with symptoms)
- [x] Implementation deferral to `wt/error-handling` is explicit
- [x] Grounding references when-recall incident (from requirements)
- [x] Section follows existing document conventions (`.` prefix H2, `###` H3 entries, Decision Date fields)
- [x] Distinction between tiers stated explicitly in each subsection
- [x] Memory index updated with trigger keys

## Potential Concerns

- DEFERRED: The "Implementation Deferral" subsection uses H3 but is not a `/when` pattern entry — it's a deferral note. This is consistent with how the document uses H3 for subsections within grouped H2 sections (e.g., `.Scripting Principles` has H3 entries that are decisions, not all `/when` patterns).
- No issues found requiring escalation.

## Status

All acceptance criteria met. No UNFIXABLE items.
