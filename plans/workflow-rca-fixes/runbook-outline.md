# Runbook Outline: Workflow RCA Fixes

**Job**: workflow-rca-fixes
**Design**: plans/workflow-rca-fixes/design.md
**Requirements**: plans/workflow-rca-fixes/requirements.md (20 FRs, 4 constraints)
**Date**: 2026-02-15

---

## Requirements Mapping Table

| Requirement | Phase | Steps | Notes |
|-------------|-------|-------|-------|
| FR-1: Restructure runbook-review.md as type-agnostic | 2 | 2.1 | Add general detection bullets to 4 axes + file growth as 5th axis |
| FR-2: Expand review-plan Section 11 with general detection | 2 | 2.2 | Add `**General:**` bullets to Sections 11.1-11.3 |
| FR-3: Add LLM failure mode gate to Phase 0.95 | 2 | 2.3 | Fast-path gate before promotion |
| FR-4: Add general-step reference material | 5 | 5.1 | Create general-patterns.md, update anti-patterns.md + examples.md |
| FR-5: Outline growth validation gate | 4 | 4.1 | Add projection validation to runbook-outline-review-agent |
| FR-6: Delete Phase 1.4 (file size awareness) | 6 | 6.1 | Remove section from runbook SKILL.md |
| FR-7: Vet status taxonomy (4-status) | 3 | 3.1 | Replace binary with FIXED/DEFERRED/OUT-OF-SCOPE/UNFIXABLE |
| FR-8: Investigation-before-escalation protocol | 3 | 3.1 | Add 4-gate checklist to vet-fix-agent (same step as FR-7) |
| FR-9: UNFIXABLE validation in detection protocol | 3 | 3.2 | Add validation steps to vet-requirement.md |
| FR-10: Orchestrate template enforcement | 3 | 3.2-3.3 | Strengthen vet-requirement.md execution context + orchestrate skill delegation template |
| FR-11: Semantic propagation checklist | 4 | 4.1 | Add grep-based classification (same step as FR-5) |
| FR-12: Agent convention injection via skills | 1 | 1.1-1.3 | Create 2 skills (project-conventions exists) + update 5 agent frontmatters |
| FR-13: Memory index injection for sub-agents | 1 | 1.2-1.3 | Create memory-index skill + update vet-fix-agent |
| FR-14: Design skill Phase C density checkpoint | 5 | 5.2 | Add density check to design SKILL.md Phase C |
| FR-15: Design-time repetition helper prescription | 5 | 5.2 | Add helper extraction guidance (same step as FR-14) |
| FR-16: Deliverable review as workflow step | 5 | 5.3 | Document in workflows-terminology.md |
| FR-17: Execution-to-planning feedback requirement | 6 | 6.2 | Document in orchestration-execution.md |
| FR-18: Review-fix integration rule | 3 | 3.1 | Add Grep→Edit protocol to vet-fix-agent (same step as FR-7) |
| FR-19: Design skill agent-name validation + late-addition check | 5 | 5.2 | Add validation steps (same step as FR-14) |
| FR-20: Design-vet-agent cross-reference + mechanism-check | 5 | 5.4 | Add review criteria to design-vet-agent |

**Coverage**: All 20 FRs mapped to specific steps

---

## Key Design Decisions Reference

**Decision 1 (Reflexive bootstrapping order):**
improve each tool before using it downstream → order: composition (Phase 1) → runbook review (Phase 2) → vet (Phase 3) → outline review (Phase 4) → content edits (Phase 5) → cleanup (Phase 6)

**Decision 2 (Convention injection via skills):**
`skills:` frontmatter injects full SKILL.md (~300-400 tokens per skill, 2-3 per agent manageable)

**Decision 3 (Four-status vet taxonomy):**
FIXED/DEFERRED/OUT-OF-SCOPE/UNFIXABLE with investigation gates → prevents over-escalation

**Decision 4 (Review-fix integration):**
merge into existing sections by heading match, not append

**Decision 5 (Diagnostic review as interactive opus session):**
NOT delegated, enabled for Phases 1-4 (self-referential), skipped for Phases 5-6 (content)

**Decision 6 (All general phase types):**
No TDD phases — all prose edits, no behavioral code changes

**Decision 7 (Execution model):**
Sonnet for edits, opus for diagnostic review (Phases 1-4 only)

---

## Phase Structure

### Phase 1: Agent Composition (type: general)

**Complexity:** Medium
**Steps:** 3
**Model:** Sonnet
**Restart required:** Yes (agent frontmatter changes)
**Diagnostic review:** Yes (improving review tools)

**FRs addressed:** FR-12, FR-13

**Steps:**

- **Step 1.1:** Create error-handling skill
  - Note: project-conventions skill already created in early bootstrap (session.md Phase C)
  - Create `agent-core/skills/error-handling/SKILL.md` wrapping `agent-core/fragments/error-handling.md`
  - Follow pattern from project-conventions: skill prolog + fragment content
  - Commit changes
  - Review: delegate to skill-reviewer (plugin-dev)

- **Step 1.2:** Create memory-index skill
  - Create `agent-core/skills/memory-index/SKILL.md` wrapping `agents/memory-index.md` with Bash transport prolog
  - Transport prolog explains sub-agents use Bash, not Skill tool: `agent-core/bin/when-resolve.py when "<trigger>"`
  - Commit changes
  - Review: delegate to skill-reviewer

- **Step 1.3:** Update agent frontmatters (batch)
  - Update 5 agents in single edit session:
    - vet-fix-agent.md: Add `skills: [project-conventions, error-handling, memory-index]`
    - design-vet-agent.md: Verify `skills: [project-conventions]` (early bootstrap)
    - outline-review-agent.md: Add `skills: [project-conventions]`
    - plan-reviewer.md: Add `skills: [project-conventions]` (already has review-plan)
    - refactor.md: Add `skills: [project-conventions, error-handling]`
  - Commit all frontmatter changes together
  - Review: delegate to agent-creator (plugin-dev) for batch validation

**Checkpoint:** Run `just sync-to-parent` to sync skill symlinks. Restart session for next phase.

---

### Phase 2: Runbook Review Overhaul (type: general)

**Complexity:** High
**Steps:** 3
**Model:** Sonnet
**Restart required:** Yes (runbook-review.md loaded via CLAUDE.md)
**Diagnostic review:** Yes (improving review logic)

**FRs addressed:** FR-1, FR-2, FR-3

**Steps:**

- **Step 2.1:** Restructure runbook-review.md as type-agnostic
  - Read `agents/decisions/runbook-review.md`
  - Restructure 4 axes with type-neutral definitions, then TDD/General bullets
  - Add file growth as 5th axis
  - Update process section: use "item (cycle or step)" terminology
  - Add behavioral vacuity detection for general phases
  - Commit changes
  - Review: delegate to vet-fix-agent

- **Step 2.2:** Expand review-plan Section 11 with general detection
  - Read `agent-core/skills/review-plan/SKILL.md`
  - Add `**General:**` bullets to Sections 11.1-11.3 (vacuity, ordering, density)
  - Commit changes
  - Review: delegate to skill-reviewer

- **Step 2.3:** Add LLM failure mode gate to runbook Phase 0.95
  - Read `agent-core/skills/runbook/SKILL.md`
  - Add validation step in Phase 0.95 before fast-path promotion
  - Check: vacuity, ordering, density, checkpoints inline
  - Commit changes
  - Review: delegate to skill-reviewer

**Checkpoint:** All review logic updated. Restart session for next phase.

---

### Phase 3: Vet Agent Overhaul (type: general)

**Complexity:** High
**Steps:** 3
**Model:** Sonnet
**Restart required:** Yes (agent definition + fragment changes)
**Diagnostic review:** Yes (improving vet tools)

**FRs addressed:** FR-7, FR-8, FR-9, FR-10, FR-18

**Steps:**

- **Step 3.1:** Add four-status taxonomy and investigation protocol to vet-fix-agent
  - Note: vet-fix-agent.md currently 436 lines, projected +150 would exceed 400-line threshold
  - Split approach: create taxonomy reference file, update vet-fix-agent to reference it
  - Create `agent-core/agents/vet-taxonomy.md`:
    - FIXED/DEFERRED/OUT-OF-SCOPE/UNFIXABLE status definitions with criteria
    - Subcategory codes (U-REQ, U-ARCH, U-DESIGN) with examples
    - Deferred Items report section template
  - Update `agent-core/agents/vet-fix-agent.md`:
    - Add reference to vet-taxonomy.md in frontmatter or instructions
    - Add 4-gate investigation-before-escalation checklist before UNFIXABLE:
      1. Check scope OUT list → OUT-OF-SCOPE
      2. Check design for documented deferral → DEFERRED
      3. Glob/Grep for existing patterns → FIXED via pattern-matching
      4. Only then classify UNFIXABLE with evidence
    - Add review-fix integration rule (FR-18): before applying fix, Grep target file for heading; if heading exists → Edit within that section; if no match → append new section
  - Commit both files
  - Review: delegate to agent-creator (plugin-dev) for both files

- **Step 3.2:** Update vet-requirement.md (UNFIXABLE validation + execution context enforcement)
  - Depends on: Step 3.1 (vet-fix-agent taxonomy committed)
  - Read `agent-core/fragments/vet-requirement.md`
  - Update "Three issue statuses" section to four statuses: add OUT-OF-SCOPE between DEFERRED and UNFIXABLE, matching taxonomy from Step 3.1
  - Add validation steps after grep-for-UNFIXABLE:
    - Check each has subcategory code
    - Check each has investigation summary
    - Check not in scope OUT list
    - Resume agent for reclassification if validation fails
  - Strengthen execution context section (FR-10): add enforcement language that IN/OUT scope fields must be structured lists, not empty prose; add fail-loudly guidance when fields are missing or unstructured
  - Commit changes
  - Review: delegate to vet-fix-agent (uses updated taxonomy from 3.1, must be committed first)

- **Step 3.3:** Add orchestrate template enforcement
  - Read `agent-core/skills/orchestrate/SKILL.md`
  - Add checkpoint delegation template with enforcement guidance
  - Require structured IN/OUT scope fields, fail loudly if empty
  - Commit changes
  - Review: delegate to skill-reviewer

**Checkpoint:** All vet logic updated. Restart session for next phase.

---

### Phase 4: Runbook Outline Review Agent (type: general)

**Complexity:** Medium
**Steps:** 1
**Model:** Sonnet
**Restart required:** Yes (agent definition changes)
**Diagnostic review:** Yes (improving outline review)

**FRs addressed:** FR-5, FR-11

**Steps:**

- **Step 4.1:** Add outline growth validation and semantic propagation checklist
  - Read `agent-core/agents/runbook-outline-review-agent.md`
  - Add growth validation criterion:
    - Validate projected file sizes vs 400-line threshold
    - Split phases must precede first phase exceeding 350 cumulative
    - Flag outlines with >10 cycles same file without projection
  - Add semantic propagation checklist under execution readiness:
    - When design introduces new terminology/types: verify artifact inventory
    - Grep-based classification: producer (rewrite) or consumer (update)
    - All files referencing old semantics must be in outline
  - Add deliverable-level traceability check:
    - Cross-reference outline coverage against design deliverables table, not just FR numbers
    - Each design deliverable row must map to an outline step (FRs with multiple deliverables need multiple step mappings)
    - Grounding: interactive opus review caught FR-10 with 2 deliverables mapped to 1 step; FR-presence check marked "Complete"
  - Commit changes
  - Review: delegate to agent-creator (plugin-dev)

**Checkpoint:** Outline review logic updated. Restart session for next phase.

---

### Phase 5: Design + Runbook Skill Fixes (type: general)

**Complexity:** Medium
**Steps:** 4
**Model:** Sonnet
**Restart required:** Yes (design-vet-agent.md agent definition + workflows-terminology.md fragment)
**Diagnostic review:** No (content edits informed by diagnostic findings)

**FRs addressed:** FR-4, FR-14, FR-15, FR-16, FR-19, FR-20

**Steps:**

- **Step 5.1:** Create general-step reference material
  - Create `agent-core/skills/runbook/references/general-patterns.md`:
    - Granularity criteria, prerequisite validation patterns, composable vs atomic
  - Update `agent-core/skills/runbook/references/anti-patterns.md`:
    - Add general-step anti-patterns section
  - Update `agent-core/skills/runbook/references/examples.md`:
    - Add complete general-step example
  - Commit changes
  - Review: delegate to skill-reviewer

- **Step 5.2:** Add density checkpoint, repetition helper, and validation steps to design skill
  - Read `agent-core/skills/design/SKILL.md`
  - Add density validation step to Phase C (flag too-granular and too-coarse)
  - Add helper extraction recommendation (>5 repeated operations threshold)
  - Add agent-name validation step to Phase C (Glob agent directories)
  - Add late-addition completeness check (re-validate requirements added after outline review)
  - Commit changes
  - Review: delegate to skill-reviewer

- **Step 5.3:** Add deliverable review to workflow terminology
  - Read `agent-core/fragments/workflows-terminology.md`
  - Add deliverable review as post-orchestration workflow step (requires opus)
  - Commit changes
  - Review: delegate to vet-fix-agent

- **Step 5.4:** Add review criteria to design-vet-agent
  - Read `agent-core/agents/design-vet-agent.md`
  - Add cross-reference criterion (Glob agent directories, verify names)
  - Add mechanism-check criterion (flag behavior without concrete mechanism)
  - Commit changes
  - Review: delegate to agent-creator (plugin-dev)

**Checkpoint:** All content edits complete. Restart session for next phase (design-vet-agent change only).

---

### Phase 6: Cleanup + Feedback Requirement (type: general)

**Complexity:** Low
**Steps:** 2
**Model:** Sonnet
**Restart required:** No
**Diagnostic review:** No

**FRs addressed:** FR-6, FR-17

**Steps:**

- **Step 6.1:** Delete Phase 1.4 from runbook skill
  - Read `agent-core/skills/runbook/SKILL.md`
  - Delete Phase 1.4 section (file size awareness)
  - Redundant with outline-level enforcement (FR-5 from Phase 4)
  - Commit changes
  - Review: delegate to skill-reviewer

- **Step 6.2:** Document execution-to-planning feedback requirement
  - Read `agents/decisions/orchestration-execution.md`
  - Add section: local recovery vs global replanning escalation, handoff to `wt/error-handling`
  - Distinguish from local (refactor agent) and item-level (UNFIXABLE)
  - Commit changes
  - Review: delegate to vet-fix-agent

**Checkpoint:** Final cleanup complete. All 20 FRs implemented.

---

## Complexity Per Phase

| Phase | Steps | Complexity | Estimated Lines Changed | Restart? | Diagnostic? |
|-------|-------|------------|------------------------|----------|-------------|
| 1 | 3 | Medium | ~150 (2 skills + 5 frontmatters) | Yes | Yes |
| 2 | 3 | High | ~200 (restructure + expand + gate) | Yes | Yes |
| 3 | 3 | High | ~300 (taxonomy + protocol + integration) | Yes | Yes |
| 4 | 1 | Medium | ~100 (growth + propagation) | Yes | Yes |
| 5 | 4 | Medium | ~250 (references + design + vet criteria) | Yes | No |
| 6 | 2 | Low | ~50 (delete + document) | No | No |

**Total:** 16 steps across 6 phases

---

## Expansion Guidance

**Phase ordering notes:**
- Reflexive bootstrapping: improve tools before using them
- Phase 1 → Phase 2 → Phase 3 → Phase 4: all require restart
- Phase 5 → Phase 6: only Phase 5 restart needed (design-vet-agent change)

**Restart triggers:**
- Phase 1: Agent frontmatter changes (skills injection)
- Phase 2: runbook-review.md loaded via CLAUDE.md @-reference
- Phase 3: Agent definitions (vet-fix-agent) + fragment (vet-requirement.md)
- Phase 4: Agent definitions (runbook-outline-review-agent)
- Phase 5: Agent definition (design-vet-agent) + fragment (workflows-terminology.md loaded via CLAUDE.md)
- Phase 6: No restart needed

**Review routing:**
- Skills → skill-reviewer (plugin-dev)
- Agents → agent-creator (plugin-dev)
- Decisions/fragments → vet-fix-agent

**Diagnostic review methodology:**
- Phases 1-4: Interactive opus session after each phase
- Session stops primed with methodology + prompts
- User switches to opus for RCA
- Phases 5-6: Skip (content edits, not self-referential improvements)

**Consolidation candidates:**
- Phase 6 is trivial (2 steps, Low complexity) but cannot merge with Phase 5 (different restart requirement)
- Phase 4 is single-step (1 step, Medium complexity) but cannot merge with Phase 3 (different agent target, maintains reflexive ordering)
- All other phases have substantial complexity or cross-phase dependencies

**Step density note:**
- Phase 2 has 3 steps (High complexity), Phase 4 has 1 step (Medium complexity handling 2 FRs)
- Phase 4 step handles two related criteria (growth validation + semantic propagation) for same agent
- Splitting Phase 4 into 2 steps would create unnecessary commits/reviews for same file

**File growth projection:**
- **CRITICAL:** vet-fix-agent.md growth exceeds threshold
  - Current: 436 lines
  - Adding: ~150 lines (taxonomy + protocol + integration rule)
  - Projected: ~586 lines (46% over 400-line threshold)
  - **Split required:** Extract taxonomy to `agent-core/agents/vet-taxonomy.md` referenced by vet-fix-agent
  - Step 3.1 must create taxonomy file separately, then update vet-fix-agent to reference it
- Other files within threshold:
  - runbook-review.md: current ~200 lines, adding ~50 → ~250 lines
  - All other edits <100 lines per file
- All edits are additions/restructuring, not new file creation

**Cross-phase dependencies:**
- Phase 1 creates skills → Phase 2-6 agents use updated skills
- Phase 2 updates review-plan → Phase 3+ plan-reviewer uses updated logic
- Phase 3 updates vet-fix-agent → Phase 4-6 vets use updated taxonomy
- Phase 4 updates outline-review → used in future planning workflows
- Phase 5 updates design skill + vet → used in future design workflows

**Prerequisite loading:**
- plugin-dev:skill-development loaded (Step 1.1-1.2 skill creation)
- plugin-dev:agent-development loaded (all agent frontmatter modifications)
- Continuation passing section of orchestrate/SKILL.md read (understanding agent composition)
- Existing non-invocable skills examined (review-plan, plugin-dev-validation, handoff-haiku)
