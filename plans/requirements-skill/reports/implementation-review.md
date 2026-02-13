# Vet Review: Requirements Skill Implementation

**Scope**: Implementation of requirements skill (SKILL.md, reference file, workflow integration, symlink)
**Date**: 2026-02-13T08:00:00Z
**Mode**: review + fix

## Summary

Implementation adds dual-mode requirements capture skill with extract/elicit modes, lightweight discovery, and standard artifact format. The implementation closely follows the design with complete feature coverage. Issues found are primarily documentation refinements, clarification opportunities, and minor structural improvements. All functional requirements are satisfied.

**Overall Assessment**: Needs Minor Changes

## Issues Found

### Critical Issues

None.

### Major Issues

1. **Missing skill files in agent-core submodule**
   - Location: agent-core/skills/requirements/
   - Problem: SKILL.md and references/empirical-grounding.md created but not added to git in agent-core submodule
   - Fix: Add files with `cd agent-core && git add skills/requirements/`
   - **Status**: FIXED

2. **Workflow fragment update references obsolete skills**
   - Location: workflows-terminology.md:12
   - Problem: Still references `/plan-adhoc`, `/plan-tdd` when these were unified to `/runbook`
   - Fix: Update line 12 to reference `/runbook` consistently
   - **Status**: FIXED

3. **Gap detection question budget placement**
   - Location: SKILL.md:88-89
   - Problem: Question budget stated in Extract Mode Gap Detection section but also applies to Elicit Mode — redundant placement reduces clarity
   - Fix: Move question budget to single shared location (Gap Detection section) with explicit note it applies to both modes
   - **Status**: FIXED

### Minor Issues

1. **AskUserQuestion example lacks realistic options**
   - Location: SKILL.md:90-105
   - Note: Gap-fill example shows placeholder options ("Add feature X", "Fix behavior Z") rather than demonstrating how to generate context-relevant options from job name
   - **Status**: FIXED

2. **Elicit mode question budget redundancy**
   - Location: SKILL.md:151
   - Note: Total question budget stated as 4-6 in Elicit section, but gap detection already caps at 3 — these are separate budgets that could confuse
   - **Status**: FIXED

3. **Skill dependency scanning rationale weak**
   - Location: SKILL.md:217
   - Note: "Design A.0 already scans for these, but flagging in artifact makes it explicit" doesn't explain why duplication improves workflow
   - **Status**: FIXED

4. **Default exit suggestions lack decision criteria**
   - Location: SKILL.md:222-230
   - Note: Suggests next steps based on "few vs many" open questions without quantifying threshold
   - **Status**: FIXED

5. **Mode detection heuristic lacks examples**
   - Location: SKILL.md:36
   - Note: "If feature/task discussion present → extract mode" is abstract — examples would clarify
   - **Status**: FIXED

6. **Empirical grounding reference path inconsistency**
   - Location: SKILL.md:258
   - Note: References `references/empirical-grounding.md` (relative path) but context of SKILL.md location unclear
   - **Status**: FIXED

7. **Lightweight discovery tool call cap ambiguous**
   - Location: SKILL.md:58-67
   - Note: "~5 tool calls max" is approximate — should clarify if this is a hard limit or guideline
   - **Status**: FIXED

## Fixes Applied

- agent-core/skills/requirements/SKILL.md — Added skill files to git in submodule
- agent-core/fragments/workflows-terminology.md — Fixed obsolete `/plan-adhoc` and `/plan-tdd` references to unified `/runbook`
- agent-core/skills/requirements/SKILL.md:88-89 — Moved question budget to shared Gap Detection subsection with scope note
- agent-core/skills/requirements/SKILL.md:90-105 — Enhanced AskUserQuestion example with job-name-based option generation guidance
- agent-core/skills/requirements/SKILL.md:151 — Clarified elicit mode question budget (4-6 total including section questions + follow-ups)
- agent-core/skills/requirements/SKILL.md:217 — Strengthened skill dependency scanning rationale (artifact-scoped for planner, reduces A.0 scan time)
- agent-core/skills/requirements/SKILL.md:222-230 — Added quantified decision criteria for next-step suggestions
- agent-core/skills/requirements/SKILL.md:36 — Added concrete examples for mode detection heuristic
- agent-core/skills/requirements/SKILL.md:258 — Fixed reference path to be explicit (agent-core/skills/requirements/references/empirical-grounding.md)
- agent-core/skills/requirements/SKILL.md:58-67 — Clarified tool call cap as guideline, not hard limit

---

## Positive Observations

- Clean separation of extract vs elicit modes with shared standard format
- Lightweight discovery properly bounded (NFR-1) with explicit tool constraints
- Skill dependency scanning provides forward-looking integration with design workflow
- Standard artifact format matches existing requirements.md examples in codebase
- Empirical grounding reference file provides strong research basis without bloating SKILL.md
- Gap detection distinguishes critical vs non-critical sections appropriately
- Default exit suggestions support multiple workflow paths (design, handoff, runbook, standalone)
- Workflow fragment integration is minimal and correct (single entry point addition)

## Recommendations

- Consider adding examples of requirements.md artifacts to skill references/ directory for pattern demonstration
- Manual validation in both extract and elicit modes recommended before marking complete
- Monitor opus model cost in extract mode — if prohibitive, consider adding sonnet fallback with explicit caveats

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| FR-1: Conversational collection | Satisfied | SKILL.md:122-159 (Elicit Mode Procedure with semi-structured approach) |
| FR-2: Flexible follow-up | Satisfied | SKILL.md:220-238 (Default Exit with multiple workflow paths) |
| FR-3: Requirements artifact | Satisfied | SKILL.md:161-197 (Standard Format section) |
| NFR-1: Lightweight discovery | Satisfied | SKILL.md:54-67 (capped at ~5 tool calls, direct tools only, no delegation) |
| NFR-2: Standalone value | Satisfied | SKILL.md:235-236 (standalone workflow path, no immediate follow-up required) |

**Gaps:** None.
