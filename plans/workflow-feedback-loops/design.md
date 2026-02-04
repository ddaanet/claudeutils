# Workflow Feedback Loops Design

**Goal:** Counter compounding errors by introducing feedback loops after each expansion step and implementation phase. Earlier feedback = less recovery effort.

**Status:** Draft
**Created:** 2026-02-04
**Mode:** General (affects infrastructure across multiple skills)

---

## Requirements

**Source:** User prompt (inline)

**Functional:**
- FR-1: Feedback loops after each expansion step — addressed by 5 feedback checkpoints
- FR-2: Feedback loops after each implementation phase — addressed by phase-boundary checkpoints
- FR-3: Review agents validate soundness — addressed by agent review protocols
- FR-4: Review agents validate alignment with requirements — addressed by requirements input validation
- FR-5: Review agents validate alignment with design — addressed by design input validation
- FR-6: Review agents apply ALL fixes immediately — addressed by fix-all policy
- FR-7: Add runbook outline step before full runbook — addressed by FP-3 checkpoint
- FR-8: Review agents validate correct inputs only — addressed by strict input validation

**Non-functional:**
- NFR-1: Reuse existing skills for detailed guidance — leverage existing protocols
- NFR-2: Create new role-specific agents where needed — minimize agent proliferation

**Out of scope:**
- Requirements gathering workflow changes
- Session.md validation
- Handoff skill changes
- /remember or /commit skill changes

---

## Architecture

### Feedback Checkpoint Model

Five feedback points (FP) inserted at expansion boundaries:

```
Design Workflow:
  A. Research
  ↓
  A.5 Outline generation → write to file
  ↓
  [FP-1: outline-review] ← NEW
  ↓
  B. User discussion (outline presented via `open` command)
  ↓
  C.1 Design expansion
  ↓
  [FP-2: design-vet-agent] ← EXISTS (enhanced)
  ↓
  C.5 Commit

Planning Workflow:
  0. Tier assessment
  ↓
  1-3. Runbook outline generation ← NEW STEP
  ↓
  [FP-3: runbook-outline-review] ← NEW
  ↓
  4. Full runbook generation (from requirements+design+outline)
  ↓
  [FP-4: runbook-review] ← EXISTS (vet-agent or tdd-plan-reviewer)
  ↓
  5. prepare-runbook.py + commit

Execution Workflow:
  Phase N work
  ↓
  [FP-5: phase-vet] ← EXISTS (vet-fix-agent, enhanced trigger)
  ↓
  Phase N+1 work
```

### Agent Input Validation Model

Every review agent validates THREE inputs:

| Input | Source | Validation |
|-------|--------|------------|
| Requirements | `plans/<job>/requirements.md` OR inline in design | Must exist and be parseable |
| Design | `plans/<job>/design.md` | Must exist, must be complete (no TBD/TODO) |
| Artifact | Varies by checkpoint | Must match expected document type |

**Rejection behavior:** If any input missing or wrong type → structured error with routing recommendation.

### Fix Policy

**Fix-all agents (apply ALL fixes including minor):**
- `outline-review-agent` (NEW) — fixes outline before user sees it
- `runbook-outline-review-agent` (NEW) — fixes outline before expansion
- `design-vet-agent` (ENHANCED) — fixes design before commit (enhances existing critical/major to include minor)
- `vet-fix-agent` (EXISTS) — fixes implementation during orchestration (critical/major only, per existing contract)

**Review-only agents (caller applies fixes):**
- `vet-agent` — used in Tier 1/2 where caller has context to apply fixes
- `tdd-plan-reviewer` — used in TDD planning where planner has context

**Rationale:** Preserve vet-agent/vet-fix-agent distinction for caller-context-aware fix application (Tier 1/2 pattern from `vet-requirement.md`). New outline agents always fix because outline→expansion is always automated. vet-fix-agent keeps existing critical/major policy because implementation fixes carry higher risk.

Only UNFIXABLE issues remain in reports (architectural changes, ambiguous requirements).

---

## Checkpoint Specifications

### FP-1: Outline Review (NEW)

**Location:** `/design` skill, after Phase A.5, before Phase B

**Prerequisite change to /design skill:** Phase A.5 must write outline to `plans/<job>/outline.md` instead of presenting inline in conversation. This is a behavioral change from current workflow.

**Trigger:** Outline file created at `plans/<job>/outline.md`

**Agent:** `outline-review-agent` (NEW, sonnet model)

**Inputs validated:**
- Requirements: `plans/<job>/requirements.md` OR requirements section in user prompt
- Research context: Exploration reports from Phase A.1-A.4 (if any)
- Artifact: `plans/<job>/outline.md`

**Requirements-to-outline traceability:**
- Outline MUST reference requirements explicitly
- Each requirement maps to approach elements in outline
- Agent verifies: every FR-* in requirements has corresponding outline section
- Missing coverage → agent adds placeholder sections with TODO markers

**Review criteria:**
- Soundness: Approach is technically feasible
- Completeness: All requirements have corresponding approach elements
- Scope: Boundaries are clear and reasonable
- Feasibility: No obvious blockers or circular dependencies
- Clarity: Key decisions are explicit, not implicit

**Output:**
- Writes review to `plans/<job>/reports/outline-review.md`
- Applies all fixes to `plans/<job>/outline.md`
- Returns filepath

**Post-review:** Present outline to user via `open plans/<job>/outline.md`

---

### FP-2: Design Review (ENHANCED)

**Location:** `/design` skill, Phase C.3

**Agent:** `design-vet-agent` (EXISTS, opus model)

**Enhancements:**
1. Add explicit requirements input validation (verify requirements exist before review)
2. Extend fix policy to include minor fixes (currently applies critical/major)
3. Verify requirements traceability table is complete (Section 4.5 already exists, enhance to validate completeness)

**Inputs validated:**
- Requirements: Must exist (file or inline)
- Design: The artifact being reviewed
- (No separate artifact — design IS the artifact)

**Review criteria:** Existing + enhanced requirements traceability verification

---

### FP-3: Runbook Outline Review (NEW)

**Location:** `/plan-adhoc` and `/plan-tdd`, after outline generation, before full runbook

**Trigger:** Runbook outline file created

**Agent:** `runbook-outline-review-agent` (NEW, sonnet model)

**Inputs validated:**
- Requirements: From design's Requirements section
- Design: `plans/<job>/design.md`
- Artifact: `plans/<job>/runbook-outline.md`

**Review criteria:**
- Requirements coverage: Every FR-* maps to at least one step/cycle
- Design alignment: Steps reference design decisions appropriately
- Phase structure: Phases are balanced and logically grouped
- Complexity distribution: No phase is disproportionately large
- Dependency sanity: No obvious circular or missing dependencies

**Output:**
- Writes review to `plans/<job>/reports/runbook-outline-review.md`
- Applies all fixes to `plans/<job>/runbook-outline.md`
- Returns filepath

**Runbook outline format:**

```markdown
# Runbook Outline: <name>

**Design:** plans/<job>/design.md
**Type:** tdd | general

## Requirements Mapping

| Requirement | Phase | Steps/Cycles | Notes |
|-------------|-------|--------------|-------|
| FR-1 | 1 | 1.1, 1.2 | Core functionality |
| FR-2 | 2 | 2.1-2.3 | Error handling |

## Phase Structure

### Phase 1: <name>
**Objective:** <what this phase accomplishes>
**Complexity:** Low/Medium/High
**Steps:**
- 1.1: <title>
- 1.2: <title>

### Phase 2: <name>
**Objective:** <what this phase accomplishes>
**Complexity:** Low/Medium/High
**Steps:**
- 2.1: <title>
- 2.2: <title>

## Key Decisions Reference
- Decision 1: <from design> → affects Phase 1
- Decision 2: <from design> → affects Phase 2
```

**Format documentation:** Add runbook outline format to `agents/decisions/workflows.md` under "Runbook Artifacts" section for discoverability.

---

### FP-4: Runbook Phase Review (ENHANCED + ITERATIVE)

**Location:** After each phase expansion in `/plan-adhoc` and `/plan-tdd`

**Key change:** Runbook is generated phase-by-phase, not all at once.

**Phase-by-phase expansion model:**

```
Outline (holistic) → approved
  ↓
Phase 1 expansion → FP-4 review → planner applies fixes
  ↓
Phase 2 expansion → FP-4 review → planner applies fixes
  ↓
... (repeat for each phase)
  ↓
Full runbook assembled → final validation
```

**Agents (review-only, caller applies fixes):**
- `vet-agent` for general runbooks
- `tdd-plan-reviewer` for TDD runbooks

**Per-phase review inputs:**
- Requirements: Subset relevant to this phase (from outline mapping)
- Design: `plans/<job>/design.md`
- Outline: `plans/<job>/runbook-outline.md` (for phase structure reference)
- Artifact: `plans/<job>/runbook-phase-N.md` (single phase content)

**Per-phase review criteria:**
- Phase content matches outline structure
- Requirements for this phase are covered
- Dependencies on previous phases are explicit
- No scope creep beyond outline's phase definition

**Final assembly:**
- After all phases reviewed, concatenate into `runbook.md`
- Final validation: cross-phase consistency, total requirements coverage
- No new content in final validation (just assembly)

**Benefits of phase-by-phase:**
- Earlier feedback per phase (catch issues in Phase 1 before writing Phase 5)
- Smaller review scope (easier to verify)
- Cross-phase issues caught during expansion (dependency mismatches)
- Quality preserved because outline provides holistic structure

**Fallback:** For small runbooks (≤3 phases, ≤10 steps/cycles), planner may generate all at once and review holistically. Tier assessment determines approach.

---

### FP-5: Phase Boundary Review (ENHANCED)

**Location:** `/orchestrate` skill, at explicit `## Phase N` boundaries

**Agent:** `vet-fix-agent` (EXISTS)

**Phase boundary detection:** Orchestrator identifies boundaries by:
1. Parse orchestrator-plan.md for step metadata
2. Each step file includes `Phase: N` in YAML frontmatter (added by prepare-runbook.py)
3. When step's phase number differs from previous step → phase boundary

**Enhancements:**
1. Stricter input validation: MUST NOT receive runbook (implementation context only)
2. MUST receive requirements + design reference
3. Fix policy unchanged (critical/major — implementation risk higher than document fixes)

**Inputs validated:**
- Requirements: Summary from design (passed via prompt, not file path)
- Design: `plans/<job>/design.md` path (for reference, agent may read)
- Artifact: Changed files list (NOT git diff text, NOT runbook)

**Artifact delivery mechanism:**
1. Orchestrator runs: `git diff --name-only <last-checkpoint-commit>..HEAD`
2. Passes changed file list to vet-fix-agent prompt
3. Agent reviews each changed file using Read tool
4. Agent applies fixes using Edit tool

**Example prompt to vet-fix-agent:**
```
Review implementation changes for Phase 2.

Requirements context:
- FR-1: User authentication with JWT
- FR-2: Secure password storage

Design reference: plans/auth-feature/design.md

Changed files (review these):
- src/auth/handlers.py
- src/auth/tokens.py
- tests/test_auth.py

Write review to: plans/auth-feature/reports/phase-2-vet.md
```

**Critical constraint:** Phase review agent reviews IMPLEMENTATION, not runbook. It should not read `runbook.md` — only the code/test changes from the phase.

**Validation rule:** If task prompt contains path to `runbook.md` → reject with error.

---

## Agent Specifications

### NEW: outline-review-agent

```yaml
name: outline-review-agent
description: Reviews design outlines for soundness, completeness, and feasibility before user discussion.
model: sonnet
tools: [Read, Write, Edit, Bash, Grep, Glob]
```

**Model selection rationale:** Sonnet (not opus) because outlines are structural artifacts, not architectural decisions. The architect (opus) makes decisions during design; outline review validates structure and completeness, which sonnet handles well.

**Protocol:**
1. Validate inputs (requirements exist, research context available)
2. Read outline
3. Check against review criteria
4. Apply ALL fixes using Edit
5. Write report
6. Return filepath

### NEW: runbook-outline-review-agent

```yaml
name: runbook-outline-review-agent
description: Reviews runbook outlines for requirements coverage and design alignment before full runbook generation.
model: sonnet
tools: [Read, Write, Edit, Bash, Grep, Glob]
```

**Model selection rationale:** Sonnet (not opus) because outline review validates structure against design, not architectural decisions. Design decisions are already made; this validates coverage and balance.

**Protocol:**
1. Validate inputs (requirements, design, outline all exist)
2. Read all three documents
3. Build requirements coverage matrix
4. Check phase structure and complexity
5. Apply ALL fixes using Edit
6. Write report
7. Return filepath

### ENHANCED: design-vet-agent

**Changes:**
- Add requirements input validation: Verify requirements exist (file or inline) before review
- Extend fix policy: Apply ALL fixes including minor (currently critical/major)
- Enhance Step 4.5: Verify requirements traceability table completeness

### ENHANCED: vet-agent / tdd-plan-reviewer

**Changes (review-only agents, NO fix policy change):**
- Add outline validation: Verify outline was reviewed before runbook (check for `outline-review.md` report)
- Add requirements inheritance: Check runbook covers outline's requirements mapping
- Remain review-only: Caller (planner) applies fixes with full context

### ENHANCED: vet-fix-agent

**Changes:**
- Add explicit rejection: If given runbook path → error
- Add requirements context: Must receive requirements summary in prompt
- Document: Agent reviews implementation changes, not planning artifacts
- Fix policy unchanged: Critical/major only (implementation fixes carry higher risk)

---

## Skill Changes

### /design Skill

**Phase A.5 changes (BEHAVIORAL CHANGE):**
1. Write outline to file: `plans/<job>/outline.md` (instead of inline presentation)
2. Delegate to `outline-review-agent`
3. After review: `open plans/<job>/outline.md` (presents to user)

**Phase B changes:**
1. User reads outline in editor
2. Feedback provided in chat
3. Designer applies deltas to outline file
4. Re-review if significant changes

**Phase C.3 changes:**
1. Enhanced design-vet-agent with requirements validation
2. Fix-all policy (extend to minor)

### /plan-adhoc Skill

**New step between Point 0.5 and Point 1:**

**Point 0.75: Generate Runbook Outline**
1. Create `plans/<job>/runbook-outline.md` with:
   - Requirements mapping table
   - Phase structure (with step titles)
   - Key decisions reference
   - Complexity per phase
2. Delegate to `runbook-outline-review-agent` (fix-all)
3. Outline approved → proceed to phase expansion

**Point 1-2: Phase-by-Phase Expansion** (replaces monolithic generation)

For each phase in outline:
1. Generate phase content: `plans/<job>/runbook-phase-N.md`
2. Delegate to `vet-agent` for review (review-only)
3. Planner applies fixes from review
4. Phase content finalized

**Point 3: Assembly and Final Review**
1. Concatenate all phase files into `plans/<job>/runbook.md`
2. Add Weak Orchestrator Metadata (computed from phases)
3. Final cross-phase consistency check (no new content generation)
4. Delegate to `vet-agent` for holistic review (review-only)
5. Planner applies any final fixes

**Fallback for small runbooks:**
- If outline has ≤3 phases and ≤10 total steps → generate all at once
- Single review pass instead of per-phase
- Tier assessment determines which approach

### /plan-tdd Skill

**New step between Phase 1 and Phase 2:**

**Phase 1.5: Generate Runbook Outline**
1. Same structure as /plan-adhoc Point 0.75
2. Use TDD-specific format: cycles instead of steps, RED/GREEN markers
3. Delegate to `runbook-outline-review-agent` (fix-all)

**Phase 2-4: Phase-by-Phase Cycle Expansion**

For each phase in outline:
1. Generate phase cycles: `plans/<job>/runbook-phase-N.md`
2. Delegate to `tdd-plan-reviewer` for review (review-only)
3. Planner applies fixes (prescriptive code, RED/GREEN violations)
4. Phase cycles finalized

**Phase 5: Assembly and Final Review**
1. Concatenate all phase files into `plans/<job>/runbook.md`
2. Add Weak Orchestrator Metadata, Common Context
3. Final cross-phase consistency check
4. Delegate to `tdd-plan-reviewer` for holistic review (review-only)
5. Planner applies any final fixes
6. Run prepare-runbook.py

**Fallback for small TDD runbooks:**
- If outline has ≤3 phases and ≤10 total cycles → generate all at once
- Single review pass instead of per-phase

### /orchestrate Skill

**Phase boundary checkpoint changes:**
1. Add requirements context to vet-fix-agent prompt
2. Add explicit instruction: Do NOT read runbook.md
3. Scope: git diff of phase only

---

## Input Validation Matrix

| Agent | Requirements | Design | Outline | Runbook | Code Changes |
|-------|--------------|--------|---------|---------|--------------|
| outline-review-agent | ✓ required | ✗ N/A | ✓ artifact | ✗ reject | ✗ N/A |
| design-vet-agent | ✓ required | ✓ artifact | ✗ N/A | ✗ reject | ✗ N/A |
| runbook-outline-review-agent | ✓ required | ✓ required | ✓ artifact | ✗ reject | ✗ N/A |
| vet-agent (runbook review) | ✓ required | ✓ required | ✓ required | ✓ artifact | ✗ N/A |
| tdd-plan-reviewer | ✓ required | ✓ required | ✓ required | ✓ artifact | ✗ N/A |
| vet-fix-agent (phase review) | ✓ required | ✓ reference | ✗ N/A | ✗ reject | ✓ artifact |

**Rejection patterns:**

```
Error: Invalid input for [agent-name]
Details: Received [document-type] but this agent reviews [expected-type]
Context: [evidence from document]
Recommendation: Use [correct-agent] for [document-type] review
```

---

## Documentation Perimeter

**Required reading (planner must load before starting):**
- `agents/decisions/workflows.md` — existing workflow patterns
- `agent-core/fragments/vet-requirement.md` — vet agent usage (Tier 1/2/3 patterns)
- `plans/workflow-feedback-loops/reports/explore-current-feedback.md` — current state analysis

**Context7 references:** None needed (internal tooling)

**Additional research allowed:** None — all patterns are internal

---

## Implementation Notes

**Affected files:**
- `agent-core/skills/design/SKILL.md` — outline step, review integration, behavioral change A.5
- `agent-core/skills/plan-adhoc/SKILL.md` — outline step, phase-by-phase expansion
- `agent-core/skills/plan-tdd/SKILL.md` — outline step, phase-by-phase expansion
- `agent-core/skills/orchestrate/SKILL.md` — phase checkpoint enhancement
- `agent-core/agents/outline-review-agent.md` — NEW
- `agent-core/agents/runbook-outline-review-agent.md` — NEW
- `agent-core/agents/design-vet-agent.md` — enhanced (fix-all, requirements validation)
- `agent-core/agents/vet-agent.md` — enhanced (outline validation, NO fix policy change)
- `agent-core/agents/tdd-plan-reviewer.md` — enhanced (outline validation, NO fix policy change)
- `agent-core/agents/vet-fix-agent.md` — enhanced (runbook rejection, requirements context)
- `agents/decisions/workflows.md` — document runbook outline format
- `agent-core/bin/prepare-runbook.py` — add Phase metadata to step files

**New artifacts per job:**
- `plans/<job>/outline.md` — design outline (before user discussion)
- `plans/<job>/runbook-outline.md` — runbook structure (before expansion)
- `plans/<job>/runbook-phase-N.md` — per-phase content (during expansion)
- `plans/<job>/reports/outline-review.md` — outline review report
- `plans/<job>/reports/runbook-outline-review.md` — runbook outline review report
- `plans/<job>/reports/phase-N-review.md` — per-phase review reports

**Testing strategy:**
- Manual validation: Run through design → plan → execute cycle
- Check: Each checkpoint produces report
- Check: Fixes applied at each stage
- Check: Invalid inputs rejected with correct error

**Risk areas:**
- Token overhead from additional review passes (mitigated: early catches save rework)
- Outline step adds latency (mitigated: catches issues before expensive full generation)
- Behavioral change in /design Phase A.5 (inline → file) requires user adjustment

---

## Next Steps

1. Route to `/plan-adhoc` for runbook generation
2. Load `plugin-dev:agent-development` before planning (creates 2 new agents)
