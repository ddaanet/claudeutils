# Step 3.3

**Plan**: `plans/workflow-feedback-loops/runbook.md`
**Execution Model**: sonnet
**Phase**: 3

---

## Step 3.3: Update /plan-tdd skill

**Objective:** Add runbook outline step and phase-by-phase cycle expansion

**Execution Model:** Sonnet

**Implementation:**

Edit `agent-core/skills/plan-tdd/SKILL.md`:

1. Add Phase 1.5 (after Phase 1, before Phase 2):
   **Phase 1.5: Generate Runbook Outline**
   - Same structure as /plan-adhoc Point 0.75
   - Use TDD-specific format: cycles instead of steps, RED/GREEN markers
   - Delegate to `runbook-outline-review-agent` (fix-all)

2. Modify Phases 2-4 for phase-by-phase expansion:
   For each phase in outline:
   - Generate phase cycles: `plans/<job>/runbook-phase-N.md`
   - Delegate to `tdd-plan-reviewer` for review (review-only)
   - Planner applies fixes (prescriptive code, RED/GREEN violations)
   - Phase cycles finalized

3. Modify Phase 5 for assembly:
   - Concatenate all phase files into `plans/<job>/runbook.md`
   - Add Weak Orchestrator Metadata, Common Context
   - Final cross-phase consistency check
   - Delegate to `tdd-plan-reviewer` for holistic review
   - Apply any final fixes
   - Run prepare-runbook.py

4. Add fallback:
   - If outline has ≤3 phases and ≤10 total cycles → generate all at once

**Reference:** Design Section "Skill Changes - /plan-tdd Skill" lines 455-480

**Expected Outcome:** TDD outline before cycles, phase-by-phase with TDD-specific review

**Success Criteria:**
- Phase 1.5 creates TDD runbook outline
- Phase-by-phase cycle expansion with tdd-plan-reviewer
- Assembly with final review
- Fallback documented

---
