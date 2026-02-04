# Step 3.2

**Plan**: `plans/workflow-feedback-loops/runbook.md`
**Execution Model**: sonnet

---

## Step 3.2: Update /plan-adhoc skill

**Objective:** Add runbook outline step and phase-by-phase expansion

**Execution Model:** Sonnet

**Implementation:**

Edit `agent-core/skills/plan-adhoc/SKILL.md`:

1. Add Point 0.75 (after Point 0.5, before Point 1):
   **Point 0.75: Generate Runbook Outline**
   - Create `plans/<job>/runbook-outline.md` with format from design
   - Include: Requirements mapping table, Phase structure, Key decisions reference, Complexity per phase
   - Delegate to `runbook-outline-review-agent` (fix-all)
   - Proceed to phase expansion after approval

2. Modify Points 1-2 for phase-by-phase expansion:
   For each phase in outline:
   - Generate phase content: `plans/<job>/runbook-phase-N.md`
   - Delegate to `vet-agent` for review (review-only)
   - Planner applies fixes from review
   - Phase content finalized

3. Modify Point 3 for assembly:
   - Concatenate all phase files into `plans/<job>/runbook.md`
   - Add Weak Orchestrator Metadata (computed from phases)
   - Final cross-phase consistency check
   - Delegate to `vet-agent` for holistic review
   - Apply any final fixes

4. Add fallback for small runbooks:
   - If outline has ≤3 phases and ≤10 total steps → generate all at once
   - Single review pass instead of per-phase

**Reference:** Design Section "Skill Changes - /plan-adhoc Skill" lines 422-452

**Expected Outcome:** Outline step before full generation, phase-by-phase with reviews

**Success Criteria:**
- Point 0.75 creates runbook outline
- Phase-by-phase expansion with reviews
- Assembly step combines phases
- Fallback documented for small runbooks

---
