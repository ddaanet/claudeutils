# Design Review: Domain-Specific Validation

**Design Document**: plans/domain-validation/design.md
**Review Date**: 2026-02-08
**Reviewer**: design-vet-agent (opus)

## Summary

The design proposes a skill-directed vet approach where domain validation knowledge is encoded in structured skill files that vet-fix-agent reads during review. The architecture is well-reasoned, leveraging planning-time domain detection to work within the weak orchestrator constraint. The approach is additive (no changes to existing agents) and extensible via a simple 3-step template. All requirements are addressed with clear traceability.

**Overall Assessment**: Ready

## Issues Found and Fixed

### Critical Issues

None found.

### Major Issues

1. **D-2 planner awareness update was vague**
   - Problem: The instruction "Plan skills should document that when writing vet checkpoint steps, the planner should check if domain validation skills exist" lacked specificity about what changes to make in the plan skills and where to add them.
   - Impact: Implementer would have insufficient guidance for the plan skill modifications, leading to inconsistent or incomplete changes.
   - Fix Applied: Replaced vague guidance with specific instruction: add a "Domain Validation" subsection to vet checkpoint guidance in both `/plan-adhoc` and `/plan-tdd`, with exact wording for what the subsection should instruct the planner to do.

2. **D-3 rules file path patterns overlapped with existing rules files**
   - Problem: The proposed `.claude/rules/plugin-dev-validation.md` included paths `.claude/skills/**/*`, `.claude/agents/**/*`, `agent-core/skills/**/*`, `agent-core/agents/**/*` which already trigger existing rules files (`skill-development.md`, `agent-development.md`). This overlap was not acknowledged, creating ambiguity about whether both rules files would fire and whether the validation rules file was intended to supersede the creation rules.
   - Impact: Implementer could create conflicting path patterns or misunderstand the interaction between existing creation-guidance rules files and the new validation-guidance rules file.
   - Fix Applied: Narrowed D-3 paths to `.claude/plugins/**/*` only and added a "Path scope note" explaining the rationale: existing rules files cover broader paths for creation guidance; this rules file targets plugin-specific validation. Added explanation that both rules firing simultaneously is correct (complementary purposes).

3. **Affected files section was imprecise**
   - Problem: Listed directory paths (`agent-core/skills/plan-adhoc/`) instead of specific file paths, and used "or" between `workflow-core.md` and `workflow-advanced.md` without deciding.
   - Impact: Implementer would need to determine which files to modify.
   - Fix Applied: Changed to specific file paths (`agent-core/skills/plan-adhoc/SKILL.md`, `agent-core/skills/plan-tdd/SKILL.md`) and resolved the decision to `agents/decisions/workflow-advanced.md` (domain validation is an advanced workflow pattern, not a core workflow change).

### Minor Issues

1. **Missing requirements traceability table**
   - Problem: The design listed FR-1 through FR-8 and NFR-1 through NFR-4 with inline references but lacked a formal traceability table mapping each requirement to specific design sections.
   - Fix Applied: Added a "Requirements Traceability" section before Implementation Notes with a complete table mapping all 12 requirements to their corresponding design decisions and architecture sections.

2. **D-1 user-invocable note was hedging**
   - Problem: Phrasing "It may have frontmatter `user-invocable: false` if that field exists, otherwise the filename/location makes its role clear" expressed uncertainty about whether the frontmatter field exists rather than making a design decision.
   - Fix Applied: Changed to definitive instruction: "Include `user-invocable: false` in frontmatter to prevent interactive discovery."

3. **Testing strategy lacked success criteria**
   - Problem: Testing strategy described activities ("Create a plugin skill, run vet") but not measurable outcomes for determining pass/fail.
   - Fix Applied: Added explicit success criteria to each test case (e.g., "domain-specific issues identified and fixed that generic vet would miss", "catches at least 2 additional issues", "vet checkpoint steps include domain validation skill reference").

4. **Next Steps skill-loading directive was unclear**
   - Problem: "Load `plugin-dev:skill-development` before planning" read as a generic note rather than a specific directive for planning workflow.
   - Fix Applied: Prefixed with "Skill loading directive:" label and added rationale: "the validation skill file is itself a skill artifact and must follow skill development conventions."

## Requirements Alignment

**Requirements Source:** inline (design.md Requirements section)

| Requirement | Addressed | Design Reference |
|-------------|-----------|------------------|
| FR-1: Domain-specific validation | Yes | D-1 (skill file format), D-4 (criteria) |
| FR-2: Optional project-specific validation | Yes | D-6 (opt-in/out) |
| FR-3: Plugin-dev as first use case | Yes | D-4 (criteria extraction) |
| FR-4: Agent discovery | Yes | D-2 (planning-time detection), D-3 (rules file) |
| FR-5: Validation rules placement | Yes | D-1 (skill files) |
| FR-6: Project opt-in mechanism | Yes | D-6 (path matching + rules) |
| FR-7: Integration with vet workflows | Yes | D-5, Architecture |
| FR-8: Extensibility model | Yes | D-7 (3-step template) |
| NFR-1: Weak orchestrator compatible | Yes | Architecture (planning-time detection) |
| NFR-2: No agent proliferation | Yes | Architecture (one vet-fix-agent) |
| NFR-3: No fidelity loss | Yes | Architecture (direct file read) |
| NFR-4: Autofix | Yes | Architecture (reviewer fixes directly) |

**Gaps:** None. All requirements are addressed.

## Positive Observations

- **Excellent constraint documentation.** The "Why This Architecture" section articulates five concrete constraints (sub-agent isolation, weak orchestrator, Dunning-Kruger, cost, autofix trust) that justify the design. Each is grounded in observed system behavior, not theoretical concerns.
- **Clean separation of concerns.** The design correctly identifies three temporal phases (planning, orchestration, execution) and assigns domain detection to the phase with sufficient intelligence (planning), not the phase that's convenient (execution).
- **Minimalist extensibility model.** D-7's 3-step template (skill file + rules file + planner awareness) requires no code changes, no new agents, and no framework. This is the simplest viable approach that satisfies all extensibility requirements.
- **Strong exploration foundation.** The two exploration reports provide thorough analysis of the existing review agent ecosystem and validation patterns, giving the design solid grounding in actual codebase architecture.
- **Additive design.** No changes to vet-fix-agent, vet-requirement fragment, or existing plugin-dev review agents. The design layers domain validation on top of existing infrastructure without disrupting it.
- **D-5 correctly handles the existing plugin-dev review agent overlap.** The design acknowledges that plugin-dev already has review agents and clearly delineates their role (interactive use) from the new domain validation pattern (standard vet workflow).

## Recommendations

- Consider adding a "Commands" subsection to D-1's skill file structure, since `plugin-dev:command-development` is listed in D-4 as a source but the D-1 template only shows Skills/Agents/Hooks sections.
- The D-3 rules file now targets only `.claude/plugins/**/*`. If plugin development work frequently creates artifacts outside that directory (e.g., plugin skills in `agent-core/skills/`), the planner may need to detect plugin-dev domain from design document context (D-2 path 2) rather than rules file activation. This is likely fine for the first use case but worth monitoring.

## Next Steps

- Design is ready for planning via `/plan-adhoc`
- No blocking issues remain
