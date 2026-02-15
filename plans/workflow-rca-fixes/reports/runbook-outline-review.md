# Runbook Outline Review: workflow-rca-fixes

**Artifact**: plans/workflow-rca-fixes/runbook-outline.md
**Design**: plans/workflow-rca-fixes/design.md
**Date**: 2026-02-15T14:30:00Z
**Mode**: review + fix-all

## Summary

Outline is well-structured with complete requirements coverage, correct reflexive bootstrapping order, and balanced phase distribution. All 20 FRs mapped to specific steps with clear traceability. Six issues identified and fixed: one critical (file growth exceeds threshold), one major (restart requirement incomplete), four minor (clarity and consistency).

**Overall Assessment**: Ready

## Requirements Coverage

| Requirement | Phase | Steps | Coverage | Notes |
|-------------|-------|-------|----------|-------|
| FR-1 | 2 | 2.1 | Complete | Type-agnostic restructure + general bullets + file growth axis |
| FR-2 | 2 | 2.2 | Complete | Section 11 general detection patterns |
| FR-3 | 2 | 2.3 | Complete | Phase 0.95 fast-path gate |
| FR-4 | 5 | 5.1 | Complete | General-step reference material (3 files) |
| FR-5 | 4 | 4.1 | Complete | Growth validation in outline-review-agent |
| FR-6 | 6 | 6.1 | Complete | Delete Phase 1.4 from runbook skill |
| FR-7 | 3 | 3.1 | Complete | Four-status taxonomy (split to vet-taxonomy.md) |
| FR-8 | 3 | 3.1 | Complete | Investigation-before-escalation protocol |
| FR-9 | 3 | 3.2 | Complete | UNFIXABLE validation in vet-requirement.md |
| FR-10 | 3 | 3.3 | Complete | Orchestrate template enforcement |
| FR-11 | 4 | 4.1 | Complete | Semantic propagation checklist |
| FR-12 | 1 | 1.1-1.3 | Complete | Convention injection via skills (3 skills + 5 agents) |
| FR-13 | 1 | 1.2-1.3 | Complete | Memory index skill + vet-fix-agent update |
| FR-14 | 5 | 5.2 | Complete | Design skill density checkpoint |
| FR-15 | 5 | 5.2 | Complete | Repetition helper prescription |
| FR-16 | 5 | 5.3 | Complete | Deliverable review in workflows-terminology |
| FR-17 | 6 | 6.2 | Complete | Execution feedback requirement documented |
| FR-18 | 3 | 3.1 | Complete | Review-fix integration rule (Grep→Edit protocol) |
| FR-19 | 5 | 5.2 | Complete | Design skill agent-name validation + late-addition check |
| FR-20 | 5 | 5.4 | Complete | Design-vet-agent cross-reference + mechanism-check |

**Coverage Assessment**: All 20 requirements covered with explicit step mappings and clear implementation notes.

## Phase Structure Analysis

### Phase Balance

| Phase | Steps | Complexity | Percentage | Assessment |
|-------|-------|------------|------------|------------|
| 1 | 3 | Medium | 18.75% | Balanced |
| 2 | 3 | High | 18.75% | Balanced |
| 3 | 3 | High | 18.75% | Balanced |
| 4 | 1 | Medium | 6.25% | Small but necessary (single agent, 2 FRs) |
| 5 | 4 | Medium | 25% | Balanced |
| 6 | 2 | Low | 12.5% | Balanced |

**Balance Assessment**: Well-balanced. Phase 4 is smaller but cannot merge with Phase 3 (different agent target, maintains reflexive bootstrapping order).

### Complexity Distribution

- **Low complexity phases**: 1 (Phase 6)
- **Medium complexity phases**: 3 (Phases 1, 4, 5)
- **High complexity phases**: 2 (Phases 2, 3)

**Distribution Assessment**: Appropriate. High-complexity phases target core review/vet infrastructure (Phases 2-3). Medium phases handle composition and content. Low phase handles cleanup.

## Review Findings

### Critical Issues

1. **File growth exceeds threshold**
   - Location: Phase 3, Step 3.1
   - Problem: vet-fix-agent.md currently 436 lines, adding ~150 lines → ~586 lines (46% over 400-line threshold)
   - Fix: Split Step 3.1 to create separate `agent-core/agents/vet-taxonomy.md` file for taxonomy content, vet-fix-agent.md references it. Updated step description with split approach and file creation order.
   - **Status**: FIXED

### Major Issues

1. **Phase 5 restart requirement incomplete**
   - Location: Phase 5 metadata, Expansion Guidance restart triggers
   - Problem: Phase 5 restart note said "design-vet-agent.md changes only" but Phase 5 also modifies workflows-terminology.md, which is loaded via CLAUDE.md @-reference and requires restart
   - Fix: Updated Phase 5 restart note to "design-vet-agent.md agent definition + workflows-terminology.md fragment". Updated Expansion Guidance restart triggers for Phase 5.
   - **Status**: FIXED

### Minor Issues

1. **Bootstrap note clarity**
   - Location: Step 1.1, Step 1.2
   - Problem: Step 1.2 mentioned "project-conventions skill exists (early bootstrap)" but Step 1.1 didn't note it was the second skill creation. Expansion agent might be confused about ordering.
   - Fix: Added bootstrap note to Step 1.1 explaining project-conventions already created in session.md Phase C, clarifying that error-handling is the second skill. Added transport prolog explanation to Step 1.2.
   - **Status**: FIXED

2. **Step dependency not explicit**
   - Location: Step 3.2
   - Problem: Step 3.2 review notes "uses updated taxonomy from 3.1" but doesn't make dependency explicit or note that 3.1 must commit before 3.2 review can use new taxonomy
   - Fix: Added "Depends on: Step 3.1 (vet-fix-agent taxonomy committed)" to Step 3.2. Clarified review note.
   - **Status**: FIXED

3. **Growth projection context missing**
   - Location: Expansion Guidance file growth projection
   - Problem: Mentioned vet-fix-agent.md +~150 lines but didn't provide current file size for validation context
   - Fix: Updated projection with actual current size (436 lines), calculated total (586 lines), noted 46% over threshold, added split requirement and approach.
   - **Status**: FIXED

4. **Phase 4 density justification missing**
   - Location: Expansion Guidance consolidation candidates
   - Problem: Phase 4 is single-step (1 step handling 2 FRs), which appears light compared to other phases. No explanation for why it's not split or merged.
   - Fix: Added step density note explaining Phase 4 handles two related criteria for same agent, splitting would create unnecessary commits/reviews for same file.
   - **Status**: FIXED

## Fixes Applied

- Phase 5 metadata — Updated restart requirement to include workflows-terminology.md fragment
- Step 1.1 — Added project-conventions bootstrap note and pattern reference
- Step 1.2 — Added transport prolog explanation for Bash-based recall
- Step 3.1 — Split to create separate vet-taxonomy.md file, updated both file descriptions
- Step 3.2 — Added explicit dependency on Step 3.1, clarified review note
- Expansion Guidance restart triggers — Updated Phase 5 to include fragment change
- Expansion Guidance file growth projection — Added actual file sizes, calculated projections, noted critical threshold violation for vet-fix-agent.md, specified split approach
- Expansion Guidance consolidation candidates — Added Phase 4 density justification

## Design Alignment

**Architecture**: Outline follows reflexive bootstrapping order correctly — improve tools before using them downstream. Phase dependencies match design: composition (1) → review logic (2) → vet logic (3) → outline review (4) → content edits (5) → cleanup (6).

**Module structure**: All target files from design correctly identified. Skill creation, agent updates, decision/fragment edits all match design specifications.

**Key decisions**:
- Decision 1 (reflexive order) — correctly implemented in phase sequence
- Decision 2 (convention injection) — Phase 1 creates skills, subsequent phases use them
- Decision 3 (four-status taxonomy) — Phase 3 Step 3.1 implements with taxonomy split
- Decision 4 (review-fix integration) — Phase 3 Step 3.1 adds Grep→Edit protocol
- Decision 5 (diagnostic review interactive) — Phases 1-4 flagged for diagnostic review, Phases 5-6 skipped
- Decision 6 (all general phases) — all phases correctly marked type: general
- Decision 7 (execution model) — sonnet for edits, opus for diagnostic (Phases 1-4)

## Positive Observations

**Complete requirements traceability**: Mapping table includes all 20 FRs with specific step references and implementation notes.

**Reflexive bootstrapping correctly ordered**: Phase sequence follows tool-usage dependency graph. Each improvement applied before that tool is used downstream.

**Review routing well-specified**: Skills → skill-reviewer, agents → agent-creator, decisions/fragments → vet-fix-agent. Clear and consistent.

**Restart triggers clearly documented**: Each phase metadata includes restart requirement with justification. Expansion Guidance consolidates all triggers with explanations.

**Cross-phase dependencies explicit**: Expansion Guidance documents how Phase 1 skills are used in Phases 2-6, how Phase 2 review-plan is used by Phase 3+ plan-reviewer, etc.

**Prerequisite loading documented**: Expansion Guidance notes plugin-dev skills needed before planning and references to existing patterns.

**Diagnostic review methodology specified**: Phases 1-4 flagged for interactive opus RCA, Phases 5-6 skipped with rationale.

**Growth projection included**: Expansion Guidance originally had file growth estimates (now updated with actual measurements after fix).

**Step density reasonable**: No phase has disproportionately large step count. Phase 2-3 have 3 steps each (High complexity), others balanced.

## Recommendations

**During expansion:**

1. **Taxonomy split execution** — When expanding Step 3.1, create vet-taxonomy.md first with all taxonomy content (definitions, criteria, subcategory codes, examples, report template), then update vet-fix-agent.md to reference it. Keeps vet-fix-agent.md within 400-line limit.

2. **Bootstrap context for Phase 1** — Load project-conventions skill content before expanding Steps 1.1-1.2 to understand the pattern for wrapping fragments as skills (prolog + fragment content).

3. **Review sequencing in Phase 3** — Step 3.2 depends on Step 3.1 commit. Ensure 3.1 changes are committed before invoking vet-fix-agent review in 3.2 (taxonomy must be in agent context).

4. **Diagnostic review priming** — After Phases 1-4, output diagnostic primer with:
   - What was edited and why (FR references)
   - Reviewer report path and summary
   - Methodology to apply (plugin-dev patterns for agents/skills, pipeline-contracts for vet/review artifacts)
   - Suggested prompts for interactive opus RCA

5. **Restart after each phase** — Phases 1-5 all require restart (Phase 6 does not). Follow checkpoint guidance to run `just sync-to-parent` and restart session before next phase.

6. **Checkpoint execution** — Each phase checkpoint includes specific validation steps. Phase 1: sync symlinks + restart. Phase 2-5: restart only. Phase 6: final validation of all 20 FRs.

---

**Ready for full expansion**: Yes

All requirements covered, phase structure balanced, reflexive bootstrapping correctly ordered, file growth issue resolved with taxonomy split, restart requirements complete, all fixes applied.
