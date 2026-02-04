# Runbook Outline: workflow-feedback-loops

**Design:** plans/workflow-feedback-loops/design.md
**Type:** general

## Requirements Mapping

| Requirement | Phase | Steps | Notes |
|-------------|-------|-------|-------|
| FR-1: Feedback after expansion | 1-4 | All agent/skill changes | Core feature |
| FR-2: Feedback after implementation phase | 3 | 3.4 | orchestrate enhancement |
| FR-3: Review agents validate soundness | 1, 2 | 1.1-1.2, 2.1-2.2 | Agent protocols |
| FR-4: Review agents validate requirements alignment | 1, 2 | 1.1-1.2, 2.1-2.2 | Input validation |
| FR-5: Review agents validate design alignment | 1, 2 | 1.1-1.2, 2.1-2.2 | Input validation |
| FR-6: Fix-all policy for outline agents | 1 | 1.1, 1.2 | Fix-all in new agents |
| FR-7: Runbook outline step before full runbook | 3 | 3.1-3.2 | plan-adhoc/plan-tdd |
| FR-8: Validate correct inputs only | 1, 2 | All | Input validation matrix |

## Phase Structure

### Phase 1: New Agents
**Objective:** Create outline-review-agent and runbook-outline-review-agent
**Complexity:** Medium
**Steps:**
- 1.1: Create outline-review-agent at agent-core/agents/outline-review-agent.md (sonnet, fix-all)
- 1.2: Create runbook-outline-review-agent at agent-core/agents/runbook-outline-review-agent.md (sonnet, fix-all)

### Phase 2: Enhanced Agents
**Objective:** Update existing agents with new validation and fix policies
**Complexity:** Medium
**Steps:**
- 2.1: Enhance agent-core/agents/design-vet-agent.md (extend to fix-all policy, add requirements validation)
- 2.2: Enhance agent-core/agents/vet-agent.md (add outline validation, remains review-only)
- 2.3: Enhance agent-core/agents/tdd-plan-reviewer.md (add outline validation, remains review-only)
- 2.4: Enhance agent-core/agents/vet-fix-agent.md (add runbook rejection, add requirements context)

### Phase 3: Skill Changes
**Objective:** Update planning skills with outline steps and phase-by-phase expansion
**Complexity:** High
**Steps:**
- 3.1: Update agent-core/skills/design/SKILL.md (A.5 write to file, FP-1 checkpoint)
- 3.2: Update agent-core/skills/plan-adhoc/SKILL.md (Point 0.75 outline, phase-by-phase)
- 3.3: Update agent-core/skills/plan-tdd/SKILL.md (Phase 1.5 outline, phase-by-phase)
- 3.4: Update agent-core/skills/orchestrate/SKILL.md (phase boundary checkpoint, requirements context)

### Phase 4: Infrastructure
**Objective:** Update supporting files and documentation
**Complexity:** Medium
**Steps:**
- 4.1: Update agent-core/bin/prepare-runbook.py (add Phase metadata to step file frontmatter)
- 4.2: Update agents/decisions/workflows.md (document runbook outline format)

## Key Decisions Reference

- **Fix-all policy:** outline agents fix ALL (incl. minor); vet-agent/tdd-plan-reviewer remain review-only
- **Phase-by-phase expansion:** Outline provides holistic structure, runbook expands phase-by-phase
- **Input validation matrix:** Each agent validates requirements + design + artifact
- **FP-5 artifact delivery:** Changed file list, not git diff text or runbook
- **Behavioral change A.5:** Outline written to file, not inline presentation
