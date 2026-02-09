# Outline Review: Domain-Specific Validation

**Artifact**: plans/domain-validation/outline.md
**Date**: 2026-02-07T19:45:00Z
**Mode**: review + fix-all

## Summary

The outline presents a sound approach to domain-specific validation that leverages existing architecture (rules files, skills, agents) without introducing new abstraction layers. The design correctly identifies that routing enrichment and pattern documentation are the missing pieces, not a validation framework. After fixes, all requirements are traced to implementation sections with clear, feasible approaches.

**Overall Assessment**: Ready

## Requirements Traceability

| Requirement | Outline Section | Coverage | Notes |
|-------------|-----------------|----------|-------|
| FR-1: Domain-specific validation | Approach, Key Decisions | Complete | Routing via rules files with skill references |
| FR-2: Optional project validation | Implementation Details (opt-in) | Complete | Implicit via path matching, explicit via rules override |
| FR-3: Plugin-dev first use case | Scope | Complete | Listed as in-scope implementation deliverable |
| FR-4: Agent discovery | Implementation Details (routing) | Complete | Rules inject guidance, caller routes to specialist |
| FR-5: Validation rules placement | Implementation Details (placement) | Complete | Skills, agents, rules files (not fragments) |
| FR-6: Project opt-in | Implementation Details (opt-in) | Complete | Path matching provides natural scoping |
| FR-7: Vet integration | Implementation Details (integration) | Complete | Transparent routing, no vet-requirement changes |
| FR-8: Extensibility model | Implementation Details (extensibility) | Complete | 3-step template (rules + skill + agent) |

**Traceability Assessment**: All requirements covered with explicit implementation approaches.

## Review Findings

### Critical Issues

None.

### Major Issues

1. **Open Questions lacked resolution**
   - Location: "Open Questions" section (original line 42-47)
   - Problem: Three design questions posed but not answered; outline incomplete without resolution
   - Fix: Added "Implementation Details" section resolving all questions with specific approaches; updated Open Questions to "None — all resolved"
   - **Status**: FIXED

2. **Missing requirements traceability**
   - Location: End of document (no traceability section present)
   - Problem: Requirements from session.md not explicitly mapped to outline sections
   - Fix: Added "Traceability" section with 8-row table mapping all FR-* requirements to outline sections
   - **Status**: FIXED

### Minor Issues

1. **Vague "vet routing enrichment" scope**
   - Location: "In scope" section
   - Problem: "Vet routing enrichment (domain-aware vet delegation)" doesn't specify mechanism
   - Fix: Added Implementation Details section explaining routing mechanism (rules inject guidance, caller routes)
   - **Status**: FIXED

2. **Extensibility model underspecified**
   - Location: "Key Decisions" mentions skills as portable units, but no template
   - Problem: FR-8 asks for extensibility model, but outline didn't provide concrete steps
   - Fix: Added extensibility template with 3-step pattern (rules file + skill + agent) in Implementation Details
   - **Status**: FIXED

3. **Project opt-in mechanism not detailed**
   - Location: "Key Decisions" mentions rules files, but not how projects opt in/out
   - Problem: FR-6 requires opt-in mechanism, outline only implied path matching
   - Fix: Added explicit opt-in section explaining implicit (path matching) vs explicit (rules override) approaches
   - **Status**: FIXED

## Fixes Applied

- Added "Implementation Details" section with 5 subsections addressing FR-4, FR-5, FR-6, FR-7, FR-8
- Added "Traceability" section with complete requirements mapping table
- Updated "Open Questions" to reflect resolution of all design questions
- Clarified routing mechanism (rules inject guidance, not static routing table)
- Specified validation knowledge placement (skills, agents, rules files — not fragments)
- Documented opt-in mechanism (path matching + rules override)
- Provided extensibility template (3-step pattern matching existing agents)

## Positive Observations

- **No new abstraction layer** — Strong decision to codify existing pattern rather than over-engineer
- **Exploration-informed** — Design references actual findings from explore-review-agents.md and explore-validation-patterns.md
- **Pattern consistency** — Extensibility template matches existing design-vet-agent and tdd-plan-reviewer patterns
- **Scope discipline** — Clear boundaries on what's in/out of scope; no scope creep
- **Feasibility** — All proposed approaches leverage existing infrastructure (rules files, skills, agents already work)

## Recommendations

- **During design discussion:** Validate that implicit opt-in (path matching) is sufficient, or if projects need explicit feature flags in settings.json
- **During planning:** Consider whether plugin-dev validation agents should live in agent-core or in plugin-dev submodule (location affects discoverability)
- **For extensibility:** Consider creating example domain validation implementation (not plugin-dev) as reference for future domains
- **Integration point:** Verify that rules file guidance is sufficient for routing, or if vet-requirement fragment needs explicit "check for domain routing hints" step

---

**Ready for user presentation**: Yes — all requirements traced, all questions resolved, feasible approach.
