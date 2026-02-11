# Design Review: Orchestrate Evolution

**Design Document**: `plans/orchestrate-evolution/design.md`
**Review Date**: 2026-02-10
**Reviewer**: design-vet-agent (opus)

## Summary

The design specifies an evolution of the orchestrate skill from a weak haiku orchestrator to a sonnet-based execution orchestrator with agent caching, post-step remediation, and refactor agent improvements. It cleanly defers parallel execution and planning orchestration to separate plans. The design is well-structured, with clear decisions, rationale, and scope boundaries.

**Overall Assessment**: Needs Minor Changes

## Issues Found and Fixed

### Critical Issues

None found.

### Major Issues

1. **Documentation Perimeter references nonexistent file**
   - Problem: `agents/decisions/architecture.md` listed in "Required reading" does not exist. 12 decision files exist in `agents/decisions/` but none named `architecture.md`.
   - Impact: Planner would fail to load required reading at plan start, causing confusion or delay.
   - Fix Applied: Changed reference to `agents/decisions/implementation-notes.md` which contains module patterns and implementation decisions (the closest match to the described "module patterns" purpose).

2. **Files Changed table missing orchestrator plan output artifact**
   - Problem: The design introduces a new "Orchestrator Plan Format" (structured metadata file) but the Files Changed table didn't list this as a generated output of prepare-runbook.py.
   - Impact: Planner might miss implementing orchestrator plan generation, treating it as an internal concern rather than a deliverable.
   - Fix Applied: Added `plans/<plan>/orchestrator-plan.md` as a generated artifact in the Files Changed table.

### Minor Issues

1. **Requirements source relationship unclear**
   - Problem: The design has inline requirements that supersede the skeletal `plans/orchestrate-evolution/requirements.md` (which still mentions "Blocked on continuation-passing"), but the design didn't state this supersession explicitly.
   - Fix Applied: Added note that inline requirements supersede the skeletal requirements.md file.

2. **Testing strategy assumes old-format runbook works**
   - Problem: Integration test plan says "run against existing prepared runbook (e.g., plugin-migration)" but Q-4 specifies clean break with no backwards compatibility. plugin-migration's existing artifacts were generated with old format and must be regenerated first.
   - Fix Applied: Added "(requires regeneration per Q-4 clean break)" to testing strategy.

3. **Verification script directory note**
   - Problem: The `scripts/` directory under orchestrate skill doesn't exist yet. The Files Changed table mentions "new `scripts/` directory" in parentheses but this was easy to overlook.
   - Fix Applied: Clarified "new `scripts/` directory under orchestrate skill" for precision.

## Requirements Alignment

**Requirements Source:** Inline (design lines 9-41), superseding `plans/orchestrate-evolution/requirements.md`

| Requirement | Addressed | Design Reference |
|-------------|-----------|------------------|
| FR-2 | Yes | Post-Step Remediation Protocol (D-3), steps 1-4 |
| FR-3 | Yes | Post-Step Remediation Protocol (D-3), step 3 (RCA task generation) |
| FR-4 | Yes | Agent Caching Model (D-2), plan-specific agent templates |
| FR-5 | Yes | Agent Caching Model (D-2), "Clean tree requirement" footer |
| FR-6 | Yes | Agent Caching Model (D-2), "Scope enforcement" + structural boundary |
| FR-7 | Yes | Verification Script section, git status + precommit check |
| NFR-1 | Yes | Orchestrator Plan Format + Key Orchestration Principles (bloat prevention) |
| NFR-2 | Yes | Q-4: clean break, regenerate old plans |
| NFR-3 | Yes | D-1: sonnet default, mechanical checks preserved |
| FR-1 (deferred) | N/A | Explicitly out of scope, deferred to plans/parallel-orchestration/ |

**Gaps:** None. All requirements traced to design elements. Deferred FR-1 acknowledged with future plan reference.

## Positive Observations

- **Agent caching model (D-2) is well-designed.** Clear separation between cached (agent definition) and non-cached (step reference) context. The two-agent-type constraint (task + vet) keeps complexity bounded while serving distinct roles.
- **Recovery agent context narrowing.** The design explicitly narrows the outline's D-3 step 5 (recovery agent receives "design + outline from task agent") to mechanical recovery only (step file + git diff + error output). This avoids over-engineering recovery with context it doesn't need.
- **Verification script is appropriately simple.** A skill-local bash script for git clean + precommit is the right level of abstraction — scriptable, testable, no agent judgment required.
- **Context tiers table** provides clear mental model for which agent gets what context, making the caching model immediately understandable.
- **Explicit D-3 note** documenting where design diverges from outline prevents confusion during planning.
- **Scope boundaries are precise.** In-scope and out-of-scope lists align with each other and with resolved questions.

## Recommendations

1. **Outline stale reference:** The outline's Approach section mentions "Parallel dispatch" alongside post-step remediation and agent caching. Q-1 and Scope correctly defer parallel execution. If the planner reads both outline and design, this could cause momentary confusion. Consider adding a note to the outline's Approach section (low priority, outline is validated but this is a factual staleness).

2. **Orchestrator plan filename convention:** The design shows the format structure but doesn't specify the filename. Is it `orchestrator-plan.md`? `<plan>-orchestrator.md`? The planner will need to decide this. Specifying a convention would reduce a decision point during planning.

3. **Message count heuristic for context measurement:** D-3 uses ">15 messages" as proxy for >100k tokens. This is acknowledged as a heuristic. During implementation, consider whether the Task tool's return metadata provides any token count information that could replace the heuristic.

## Next Steps

1. Route to `/plan-adhoc` as specified in design's Next Steps section
2. Planner should load `plugin-dev:agent-development` and `plugin-dev:skill-development` before planning
3. Planner should regenerate plugin-migration artifacts before using as integration test target
