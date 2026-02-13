# Design Review: Requirements Skill

**Design Document**: `plans/requirements-skill/design.md`
**Review Date**: 2026-02-13
**Reviewer**: design-vet-agent (opus)

## Summary

The design specifies a dual-mode `/requirements` skill that captures user intent through either extraction (mid-conversation) or elicitation (cold-start), producing a standard `requirements.md` artifact. The architecture is well-grounded in empirical research, appropriately scoped, and integrates cleanly with the existing `/design` workflow without requiring changes to downstream skills.

**Overall Assessment**: Ready

## Issues Found and Fixed

### Critical Issues

None found.

### Major Issues

1. **Empirical grounding reference path inconsistency**
   - Problem: Line 169 referenced `references/empirical-grounding.md` (relative to skill directory), but the research report exists at `plans/requirements-skill/reports/research-empirical.md`. The Documentation Perimeter section (line 225) correctly referenced the reports path, creating an internal inconsistency.
   - Impact: Planner would be confused about which file to read and where the source material lives.
   - Fix Applied: Updated line 169 to reference the actual research report path and clarify that the distilled version will be created at the skill-internal path.

2. **Requirements.md FR-2 terminology drift**
   - Problem: The source `requirements.md` lists follow-up options as `/plan-adhoc, /plan-tdd`, which no longer exist — they are unified as `/runbook`. The design correctly uses `/runbook` but did not acknowledge this divergence from the requirements source.
   - Impact: A planner consulting the requirements source would see a discrepancy without explanation, potentially questioning whether the design addresses FR-2 correctly.
   - Fix Applied: Added parenthetical note to FR-2 line explaining the terminology unification.

3. **Missing skill-loading directive in Next Steps**
   - Problem: This design creates a skill (SKILL.md), which qualifies as `plugin-dev:skill-development` territory per the design skill's own protocol. Next Steps did not include the skill-loading directive.
   - Impact: Planner would start without `plugin-dev:skill-development` context, potentially producing a SKILL.md that doesn't follow skill conventions (frontmatter format, allowed-tools, etc.).
   - Fix Applied: Added `Load plugin-dev:skill-development before planning` as step 1 in Next Steps.

### Minor Issues

1. **SKILL.md Content Outline missing model and invocability**
   - Problem: The content outline listed "Frontmatter" without specifying `user-invocable: true`, and omitted "Target Model" as a section despite opus being a key design decision.
   - Fix Applied: Added `user-invocable: true` to frontmatter item, added "Target Model" as item 2 with opus rationale.

2. **Missing Requirements Traceability table**
   - Problem: Design had inline FR/NFR mapping in the Requirements section but no formal traceability table for quick verification.
   - Fix Applied: Added a Requirements Traceability table after the Out of Scope section, mapping all 5 requirements to their design references.

## Requirements Alignment

**Requirements Source:** `plans/requirements-skill/requirements.md`

| Requirement | Addressed | Design Reference |
|-------------|-----------|------------------|
| FR-1: Conversational collection | Yes | Elicit mode (Architecture > Dual-Mode Operation) |
| FR-2: Flexible follow-up | Yes | Workflow Positioning section (/handoff, /design, /runbook) |
| FR-3: Requirements artifact | Yes | Standard Artifact Format section |
| NFR-1: Lightweight | Yes | Lightweight Codebase Discovery (capped at ~5 tool calls) |
| NFR-2: Standalone value | Yes | Workflow Positioning (standalone path, no follow-up required) |

**Gaps:** None. All requirements addressed. Open questions from requirements.md (Q-1 through Q-4) are resolved by the design decisions.

## Positive Observations

- **Empirical grounding is strong.** Design decisions map directly to research findings (HAIC pattern, semi-structured interviews, hallucination mitigation). This is unusually well-supported for a procedural skill.
- **Scope discipline.** Clear boundaries on discovery (capped tool calls, no delegation), gap-fill (max 3 questions), and out-of-scope items. The design resists feature creep effectively.
- **Clean integration.** Design A.0 already consumes `requirements.md` — no changes needed to downstream skills. This is the ideal integration pattern (additive, not invasive).
- **Mode detection heuristic is pragmatic.** Inferring from conversation state rather than requiring explicit flags aligns with natural usage patterns.
- **Gap detection design is well-calibrated.** Distinguishing critical (ask) vs non-critical (note) sections prevents over-interrogation while catching genuine gaps.
- **Skill dependency scanning is forward-looking.** Flagging plugin-dev dependencies in the artifact creates a bridge between requirements and design that currently requires manual detection.

## Recommendations

- Consider whether the `allowed-tools` frontmatter should explicitly list Glob, Grep, Read (for discovery) and Write (for artifact creation). The design implicitly requires these but the SKILL.md content outline doesn't call it out.
- The question budget (max 3) is specified in Gap Detection but not in Elicit mode. The elicit mode is inherently more question-heavy — clarify whether the 3-question cap applies to gap-fill only or to the entire elicit interaction.

## Next Steps

- Design is ready for planning via `/runbook`.
- Planner should load `plugin-dev:skill-development` before starting (per Next Steps item 1).
- Implementation is Tier 1 (direct, <6 files) — runbook tier assessment may route to lightweight execution.
