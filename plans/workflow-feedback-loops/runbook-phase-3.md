## Phase 3: Skill Changes

### Step 3.1: Update /design skill

**Objective:** Add outline file output and FP-1 checkpoint

**Execution Model:** Sonnet

**Implementation:**

Edit `agent-core/skills/design/SKILL.md`:

1. Modify Phase A.5 (BEHAVIORAL CHANGE):
   - Current: Outline presented inline in conversation
   - New: Write outline to `plans/<job>/outline.md`
   - Add instruction to create plans/<job>/ directory if needed

2. Add FP-1 checkpoint after A.5:
   - Delegate to `outline-review-agent`
   - Agent applies all fixes to outline
   - Agent writes review to `plans/<job>/reports/outline-review.md`

3. Modify Phase B:
   - After FP-1 review: `open plans/<job>/outline.md` (presents to user in editor)
   - User reads outline in editor, provides feedback in chat
   - Designer applies deltas to outline file
   - Re-review via outline-review-agent if significant changes

**Reference:** Design Section "Skill Changes - /design Skill" lines 405-419

**Expected Outcome:** Outline written to file, reviewed before user sees it

**Success Criteria:**
- Phase A.5 writes to file, not inline
- FP-1 checkpoint delegated to outline-review-agent
- Phase B uses `open` command to present outline

---

### Step 3.2: Update /plan-adhoc skill

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

### Step 3.3: Update /plan-tdd skill

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

### Step 3.4: Update /orchestrate skill

**Objective:** Enhance phase boundary checkpoints with requirements context

**Execution Model:** Sonnet

**Implementation:**

Edit `agent-core/skills/orchestrate/SKILL.md`:

1. Add requirements context to vet-fix-agent prompts:
   - Include requirements summary in checkpoint prompt
   - Format: List of FR-* items relevant to completed phase

2. Add explicit instruction for changed files:
   - Run: `git diff --name-only <last-checkpoint-commit>..HEAD`
   - Pass changed file list to vet-fix-agent (not git diff text)
   - Agent reviews each file using Read tool

3. Add runbook exclusion instruction:
   - Explicitly state: "Do NOT read runbook.md"
   - Scope: Implementation changes only

4. Add phase boundary detection guidance:
   - Parse step file frontmatter for `Phase: N`
   - When phase number changes → phase boundary checkpoint

**Reference:** Design Section "FP-5: Phase Boundary Review (ENHANCED)" and "/orchestrate Skill" lines 485-489

**Expected Outcome:** Checkpoints include requirements context, use file list not diff text

**Success Criteria:**
- Requirements context in vet-fix-agent prompt
- Changed files list pattern documented
- Runbook exclusion explicit
- Phase boundary detection documented
