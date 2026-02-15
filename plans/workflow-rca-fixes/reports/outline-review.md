# Outline Review: Workflow RCA Fixes

**Artifact**: plans/workflow-rca-fixes/outline.md
**Date**: 2026-02-14T18:42:00Z
**Mode**: review + fix-all

## Summary

The outline provides a clear 6-phase approach to implementing 18 functional requirements from RCA analysis. All phases are well-defined with specific target files and concrete editing tasks. The design correctly identifies all changes as prose edits (C-1 constraint) and uses native `skills:` mechanism for agent composition (C-2 constraint). Traceability matrix maps all 18 FRs to phases. All issues identified have been fixed.

**Overall Assessment**: Ready

## Requirements Traceability

| Requirement | Outline Section | Coverage | Notes |
|-------------|-----------------|----------|-------|
| FR-1 | Phase 1 | Complete | Behavioral vacuity, type-agnostic restructuring, file growth axis |
| FR-2 | Phase 1 | Complete | General detection patterns in Section 11 |
| FR-3 | Phase 1 | Complete | LLM failure mode gate for Phase 0.95 fast-path |
| FR-4 | Phase 5 | Complete | General-step reference material (patterns, anti-patterns, examples) |
| FR-5 | Phase 3 | Complete | Outline growth validation gate |
| FR-6 | Phase 6 | Complete | Delete Phase 1.4 from runbook skill |
| FR-7 | Phase 2 | Complete | Four-status taxonomy (FIXED/DEFERRED/OUT-OF-SCOPE/UNFIXABLE) |
| FR-8 | Phase 2 | Complete | Investigation-before-escalation protocol |
| FR-9 | Phase 2 | Complete | UNFIXABLE validation in detection protocol |
| FR-10 | Phase 2 | Complete | Execution context requirement + template enforcement |
| FR-11 | Phase 3 | Complete | Semantic propagation checklist |
| FR-12 | Phase 4 | Complete | Fragment-wrapping skills for conventions |
| FR-13 | Phase 4 | Complete | Memory index injection via skills |
| FR-14 | Phase 5 | Complete | Design skill Phase C density checkpoint |
| FR-15 | Phase 5 | Complete | Repetition helper prescription (>5 operations) |
| FR-16 | Phase 5 | Complete | Deliverable review as post-orchestration workflow step |
| FR-17 | Phase 6 | Complete | Execution-to-planning feedback requirement documented |
| FR-18 | Phase 2 | Complete | Review-fix integration rule (merge not append) |

**Traceability Assessment**: All requirements covered. Every FR has explicit phase assignment and target file identification.

## Review Findings

### Critical Issues

None identified after fixes applied.

### Major Issues

**1. FR-5 missing from Phase 3 header**
- Location: Phase 3 header (originally listed only FR-11)
- Problem: Outline growth validation gate (FR-5) was assigned to Phase 3 in traceability matrix but not reflected in phase header
- Fix: Updated Phase 3 header to "(FR-5, FR-11)" and expanded bullet to include both requirements explicitly
- **Status**: FIXED

**2. FR-10 target file incorrect**
- Location: Phase 2 (originally listed pipeline-contracts.md for FR-10)
- Problem: Execution context requirement lives in vet-requirement.md fragment, not pipeline-contracts.md decision file
- Fix: Updated Phase 2 to edit vet-requirement.md for FR-9 and FR-10, moved orchestrate template enforcement to separate bullet
- **Status**: FIXED

**3. Missing expansion details for Phase 1-3, 5-6**
- Location: All phase bullets (originally just high-level summaries)
- Problem: Phase bullets lacked specificity on what edits to make (no mention of thresholds, detection patterns, specific additions)
- Fix: Expanded all phase bullets with concrete implementation details — thresholds (400-line limit, >10 cycles), detection patterns (scaffolding vacuity, artifact dependency), structural changes (type-agnostic axes, four-status taxonomy), specific file targets (references/general-patterns.md)
- **Status**: FIXED

### Minor Issues

**1. Traceability matrix missing from outline**
- Location: Scope Boundaries section
- Problem: No explicit FR-to-phase mapping table in outline (requirements.md has 18 FRs but outline didn't enumerate coverage)
- Fix: Added Requirements Traceability section with complete table mapping all 18 FRs to phases and target files
- **Status**: FIXED

**2. Phase type clarification needed**
- Location: Key Decisions #5
- Problem: Stated "all phases are general" without explaining why Phase 4 skill creation isn't code
- Fix: Added clarification that Phase 4 creates SKILL.md files as content authoring, not code implementation
- **Status**: FIXED

**3. Rationale missing for FR-18 decision**
- Location: Key Decisions #4
- Problem: Review-fix integration rule stated without evidence from RCA
- Fix: Added pattern example from outline-review-agent Round 1 (duplicate "Expansion Guidance" sections)
- **Status**: FIXED

**4. Behavioral vacuity connection to FR-1 implicit**
- Location: Key Decisions #3
- Problem: Behavioral vacuity detection described but not connected to FR-1's "scaffolding AND behavioral vacuity" requirement
- Fix: Added explicit connection to FR-1 requirement
- **Status**: FIXED

**5. FR-16 target file missing**
- Location: Phase 5 (originally "Edit deliverable-review integration into post-orchestration workflow")
- Problem: No specific file identified for deliverable review integration
- Fix: Changed to edit workflows-terminology.md Implementation workflow route section
- **Status**: FIXED

**6. FR-17 target file ambiguous**
- Location: Phase 6 (originally "workflow-core.md or orchestration-execution.md")
- Problem: Two alternative files listed without decision
- Fix: Selected orchestration-execution.md as target (execution-to-planning feedback is execution concern, not workflow structure)
- **Status**: FIXED

## Fixes Applied

- Phase 1 bullets — Added implementation details (behavioral vacuity detection, type-agnostic restructuring with concept → TDD → general → action format, file growth projection with 400-line threshold, LLM failure mode gate with inline fix-before-promotion)
- Phase 2 bullets — Reorganized to edit vet-requirement.md for FR-9/FR-10, expanded vet-fix-agent.md edits with four-status taxonomy details, investigation checklist steps, review-fix integration rule pattern
- Phase 3 header — Added FR-5 to "(FR-5, FR-11)"
- Phase 3 bullets — Split into two separate edits (FR-5 growth validation gate with thresholds, FR-11 semantic propagation checklist with grep-based classification)
- Phase 4 bullets — Expanded skill creation with token estimates (~300, ~250, ~200 tokens), explicit agent frontmatter assignments per FR-12, memory index transport instruction for FR-13
- Phase 5 bullets — Expanded to six separate edits targeting runbook/references/ files (general-patterns.md, anti-patterns.md, examples.md), design/SKILL.md Phase C.1 additions (density checkpoint, repetition helper prescription), workflows-terminology.md Implementation workflow route
- Phase 6 bullets — Specified Phase 1.4 deletion, selected orchestration-execution.md as FR-17 target with local vs global replanning distinction
- Key Decisions #3 — Added FR-1 connection to behavioral vacuity detection
- Key Decisions #4 — Added RCA evidence (outline-review-agent Round 1 pattern)
- Key Decisions #5 — Added Phase 4 skill creation clarification
- Requirements Traceability section — Added complete FR-to-phase-to-file mapping table

## Positive Observations

**Strong architectural coherence:**
- 6-phase structure follows natural dependency order (review mechanisms → vet overhaul → outline review → agent composition → skills → documentation)
- No circular dependencies between phases
- Clear file ownership (each file edited in single phase)

**Constraint compliance:**
- All changes correctly identified as prose edits (C-1)
- Native `skills:` mechanism used throughout (C-2)
- Fragment-wrapping skills designed for skill-reviewer validation (C-3)
- FR-17 correctly deferred to error-handling framework (C-4)

**Research grounding:**
- Open questions Q-1/Q-2 resolved empirically with evidence (skills inject full SKILL.md, ~300-1400 tokens per skill)
- Token cost estimates provided for fragment-wrapping skills (300-400 tokens each)
- ODC taxonomy correctly applied to vet status classification (orthogonal type × trigger)

**Traceability discipline:**
- All 18 FRs mapped to specific phases
- Each FR identifies target files and concrete changes
- No requirements gaps or missing coverage

**Clear scope boundaries:**
- In-scope / out-of-scope explicitly stated
- Dependencies on error-handling framework and skill-reviewer documented
- Constraints C-1 through C-4 referenced throughout

## Recommendations

**For runbook expansion:**
1. Validate fragment-wrapping skill structure against existing plan-reviewer pattern (skills: [review-plan] frontmatter reference) before Phase 4 execution
2. Consider splitting Phase 4 into two sub-phases if skill-reviewer validation cycle reveals need for iteration (create skills → validate → edit agents)
3. For FR-4 general-step reference material, include cross-references to existing TDD reference material for contrast (what differs between TDD and general granularity)
4. For FR-5 outline growth validation, consider adding checkpoint: grep for growth projection when outline contains >10 cycles on same file
5. For FR-13 memory index injection, test Bash recall transport pattern (`when-resolve.py`) before full agent rollout to verify no path resolution issues

**For execution:**
- Phase 1-3 can execute sequentially without checkpoints (low-risk prose edits to independent files)
- Phase 4 requires checkpoint after skill creation before agent frontmatter edits (validate skills load correctly)
- Phase 5-6 can execute in parallel if both target different files (Phase 5: runbook/references/, design/SKILL.md, workflows-terminology.md; Phase 6: runbook/SKILL.md Phase 1.4 deletion, orchestration-execution.md)

**For verification:**
- After Phase 4: Restart session and verify injected skills appear in agent context (test with vet-fix-agent invoking deslop guidance)
- After Phase 6: Grep for "Phase 1.4" in runbook/SKILL.md to confirm deletion completed (no orphaned references)

---

**Ready for user presentation**: Yes

All requirements traced, all issues fixed, approach is sound and feasible. Outline provides sufficient detail for runbook expansion.
