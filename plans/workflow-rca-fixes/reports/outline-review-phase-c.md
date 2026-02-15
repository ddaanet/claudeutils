# Outline Review: workflow-rca-fixes

**Artifact**: plans/workflow-rca-fixes/outline.md
**Date**: 2026-02-14T00:00:00Z
**Mode**: review + fix-all

## Summary

Outline is comprehensive, well-structured, and directly executable. All 18 FRs traced to specific phases with clear file targets. Reflexive bootstrapping order is sound. Three-layer validation (reviewer → diagnostic opus → restart) provides strong quality gates. Phase types correctly classified (all general). Ready for design document generation.

**Overall Assessment**: Ready

## Requirements Traceability

| Requirement | Outline Section | Coverage | Notes |
|-------------|-----------------|----------|-------|
| FR-1 | Phase 2 | Complete | runbook-review.md restructure: type-agnostic axes + behavioral vacuity |
| FR-2 | Phase 2 | Complete | review-plan Section 11 expansion with general detection patterns |
| FR-3 | Phase 2 | Complete | runbook Phase 0.95 LLM failure mode gate |
| FR-4 | Phase 5 | Complete | runbook/references/ general-step materials |
| FR-5 | Phase 4 | Complete | outline-review-agent growth validation gate |
| FR-6 | Phase 6 | Complete | runbook Phase 1.4 deletion |
| FR-7 | Phase 3 | Complete | vet-fix-agent four-status taxonomy |
| FR-8 | Phase 3 | Complete | vet-fix-agent investigation-before-escalation protocol |
| FR-9 | Phase 3 | Complete | vet-requirement UNFIXABLE validation |
| FR-10 | Phase 3 | Complete | vet-requirement + orchestrate template enforcement |
| FR-11 | Phase 4 | Complete | outline-review-agent semantic propagation checklist |
| FR-12 | Phase 1 | Complete | project-conventions + error-handling skills + agent frontmatter |
| FR-13 | Phase 1 | Complete | memory-index skill + vet-fix-agent frontmatter |
| FR-14 | Phase 5 | Complete | design Phase C.1 density checkpoint |
| FR-15 | Phase 5 | Complete | design Phase C.1 repetition helper prescription |
| FR-16 | Phase 5 | Complete | workflows-terminology deliverable review step |
| FR-17 | Phase 6 | Complete | orchestration-execution feedback requirement |
| FR-18 | Phase 3 | Complete | vet-fix-agent review-fix integration rule |
| C-1 | Approach, Phase types | Complete | All prose edits, no code changes |
| C-2 | Phase 1 | Complete | Native `skills:` frontmatter mechanism |
| C-3 | Phase 1 | Complete | skill-reviewer validation for fragment-wrapping skills |
| C-4 | Phase 6 FR-17 | Complete | FR-17 documents requirement, defers to wt/error-handling |

**Traceability Assessment**: All requirements covered with explicit mappings to phases and target files.

## Review Findings

### Critical Issues

None.

### Major Issues

None.

### Minor Issues

None.

## Fixes Applied

No fixes required. Outline was already comprehensive and well-aligned to requirements.

## Positive Observations

**Reflexive bootstrapping order is sound:**
- Phase 1 (agent composition) improves all downstream agents before they're used
- Phase 2 (runbook review) improves plan-reviewer before it reviews runbooks
- Phase 3 (vet overhaul) improves vet-fix-agent before it vets outputs
- Phase 4 (outline review) improves outline-review-agent before it reviews outlines
- Dependency graph is acyclic and correct

**Three-layer validation provides strong quality:**
- Domain-specific reviewer (skill-reviewer, agent-creator, vet-fix-agent)
- Optional interactive opus diagnostic with RCA methodology
- Restart protocol ensures changes take effect before next phase

**Execution context is explicit:**
- Review-after-edit rule specifies which reviewer for each artifact type
- Restart rule specifies when session restart required (agent/fragment edits)
- Diagnostic review rule specifies when/how to enable opus RCA (Phases 1-4 only)

**Research grounding is strong:**
- MAR's "degeneration of thought" → two-model separation (sonnet review + opus diagnostic)
- Flow-of-Action SOP-constrained RCA → methodology documents as review SOPs
- ACE framework knowledge injection → skills frontmatter for conventions

**Scope boundaries are clear:**
- All 18 FRs in scope, mapped to phases
- Out-of-scope items explicit (code changes, error-handling framework implementation, formal verification)
- Dependencies explicit (wt/error-handling for FR-17 implementation)

**Traceability table is complete:**
- All 18 FRs map to phases with target files
- No requirements gaps
- No orphaned phases

**Key decisions are well-justified:**
- Convention bundling (deslop + token-economy + tmp-directory) with token counts
- Memory index transport via Bash (sub-agents lack Skill tool)
- Behavioral vacuity heuristic (cycles > LOC/20)
- Review-fix integration prevents duplicate sections

**Phase types correct:**
- All phases are general (prose edits)
- No TDD phases (no code changes per C-1)

## Recommendations

**For design document generation (Phase C):**

1. **Prerequisite loading:** Before starting Phase C, ensure `plugin-dev:skill-development` and `plugin-dev:agent-development` are loaded. Reference patterns: `agent-core/skills/orchestrate/SKILL.md` continuation passing section, existing non-invocable skills (review-plan, plugin-dev-validation, handoff-haiku).

2. **File inventory:** Build complete inventory of all files requiring edits. Validate against git tree to catch any path errors early.

3. **Edit specifications:** For each phase, provide exact edit locations (section headings, line anchors) and explicit before/after content where feasible. Reduces ambiguity during runbook execution.

4. **Diagnostic review methodology:** Since no formal `design-review-methodology.md` exists, design.md should explicitly reference pipeline-contracts (T1-T6 defect classification) + plugin-dev patterns as review SOPs for opus diagnostic sessions.

5. **Token budget tracking:** FR-12 includes token counts (~400 for project-conventions, ~100 for error-handling). Design.md should validate total per-agent injection stays within reasonable bounds (<15% of context).

6. **Skill prolog design:** Memory-index skill (FR-13) needs transport instruction prolog. Design should specify exact wording: "Sub-agents invoke: `agent-core/bin/when-resolve.py when '<trigger>'`" for Bash recall.

7. **Integration test cases:** Consider documenting expected behavior changes after each phase — enables verification that changes took effect (e.g., after Phase 1, vet-fix-agent should produce deslopped prose).

8. **Checkpoint commit strategy:** Six phases → potential for six checkpoint commits. Design should specify commit boundaries and whether to squash after completion.

---

**Ready for user presentation**: Yes
