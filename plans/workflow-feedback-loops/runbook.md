---
name: workflow-feedback-loops
model: sonnet
---

## Common Context

**Design Reference:** plans/workflow-feedback-loops/design.md

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

## Key Decisions Reference

- **Fix-all policy:** outline agents fix ALL (incl. minor); vet-agent/tdd-plan-reviewer remain review-only
- **Phase-by-phase expansion:** Outline provides holistic structure, runbook expands phase-by-phase
- **Input validation matrix:** Each agent validates requirements + design + artifact
- **FP-5 artifact delivery:** Changed file list, not git diff text or runbook
- **Behavioral change A.5:** Outline written to file, not inline presentation

## Weak Orchestrator Metadata

| Attribute | Value |
|-----------|-------|
| Total Steps | 12 |
| Execution Model | Sequential |
| Dependencies | See design for cross-plan dependencies |
| Error Escalation | Any phase failure → stop and report |

### Phase 1: New Agents

**Prerequisite:** Load `plugin-dev:agent-development` skill before starting (provides agent structure, frontmatter guidance, progressive disclosure patterns).

## Step 1.1: Create outline-review-agent

**Objective:** Create agent that reviews design outlines before user discussion

**Execution Model:** Sonnet

**Implementation:**

Create `agent-core/agents/outline-review-agent.md` with:

**Frontmatter:**
- name: outline-review-agent
- description: Use when reviewing design outlines after Phase A.5, before user discussion. Validates soundness, completeness, feasibility.
- model: sonnet
- color: cyan
- tools: [Read, Write, Edit, Bash, Grep, Glob]

**System prompt requirements:**
1. Input validation: Verify requirements exist (file or inline), verify artifact is outline.md (not design.md, not runbook)
2. Review criteria from design FP-1:
   - Soundness: Approach is technically feasible
   - Completeness: All requirements have corresponding approach elements
   - Scope: Boundaries are clear and reasonable
   - Feasibility: No obvious blockers or circular dependencies
   - Clarity: Key decisions are explicit, not implicit
3. Requirements-to-outline traceability: Every FR-* must map to outline section
4. Fix-all policy: Apply ALL fixes (critical, major, AND minor) using Edit tool
5. Output: Write review to specified path, return filepath

**Reference:** Design Section "FP-1: Outline Review (NEW)" lines 112-147

**Expected Outcome:** Agent file exists, follows agent-development skill patterns

**Success Criteria:**
- File exists at agent-core/agents/outline-review-agent.md
- Valid YAML frontmatter with all required fields
- System prompt includes input validation, review criteria, fix-all policy
- Examples in description show triggering conditions

---

## Step 1.2: Create runbook-outline-review-agent

**Objective:** Create agent that reviews runbook outlines before full expansion

**Execution Model:** Sonnet

**Implementation:**

Create `agent-core/agents/runbook-outline-review-agent.md` with:

**Frontmatter:**
- name: runbook-outline-review-agent
- description: Use when reviewing runbook outlines after Point 0.75 (plan-adhoc) or Phase 1.5 (plan-tdd), before full runbook generation.
- model: sonnet
- color: cyan
- tools: [Read, Write, Edit, Bash, Grep, Glob]

**System prompt requirements:**
1. Input validation: Verify requirements, design, and outline all exist
2. Review criteria from design FP-3:
   - Requirements coverage: Every FR-* maps to at least one step/cycle
   - Design alignment: Steps reference design decisions appropriately
   - Phase structure: Phases are balanced and logically grouped
   - Complexity distribution: No phase is disproportionately large
   - Dependency sanity: No obvious circular or missing dependencies
3. Fix-all policy: Apply ALL fixes using Edit tool
4. Output: Write review to specified path, return filepath

**Reference:** Design Section "FP-3: Runbook Outline Review (NEW)" lines 169-231

**Expected Outcome:** Agent file exists, follows agent-development skill patterns

**Success Criteria:**
- File exists at agent-core/agents/runbook-outline-review-agent.md
- Valid YAML frontmatter with all required fields
- System prompt includes input validation, review criteria, fix-all policy
- Runbook outline format from design is referenced


### Phase 2: Enhanced Agents

## Step 2.1: Enhance design-vet-agent

**Objective:** Extend design-vet-agent with fix-all policy and explicit requirements validation

**Execution Model:** Sonnet

**Implementation:**

Edit `agent-core/agents/design-vet-agent.md`:

1. Add explicit requirements input validation to Step 0:
   - Before review, verify requirements exist (plans/<job>/requirements.md OR requirements section in design)
   - If requirements missing, return structured error with recommendation

2. Extend fix policy from critical/major to fix-all:
   - Change instructions to apply ALL fixes (critical, major, AND minor)
   - Rationale: Document fixes are low-risk; earlier cleanup saves iteration

3. Enhance requirements traceability verification:
   - Existing Step 4.5 validates traceability table exists
   - Enhance to verify completeness: every FR-* has corresponding design element

**Reference:** Design Section "FP-2: Design Review (ENHANCED)" lines 149-166

**Expected Outcome:** Agent applies all fixes, validates requirements exist

**Success Criteria:**
- Step 0 includes requirements existence check
- Fix policy explicitly says "apply ALL fixes including minor"
- Traceability verification is more thorough

---

## Step 2.2: Enhance vet-agent

**Objective:** Add outline validation without changing fix policy

**Execution Model:** Sonnet

**Implementation:**

Edit `agent-core/agents/vet-agent.md`:

1. Add outline validation to Step 0:
   - When reviewing runbook, check if `plans/<job>/reports/runbook-outline-review.md` exists
   - If outline review missing, warn (not error) that outline was not reviewed

2. Add requirements inheritance check:
   - Verify runbook covers outline's requirements mapping
   - If outline exists, compare coverage

3. Preserve review-only behavior:
   - Do NOT change fix policy
   - Caller (planner) applies fixes with full context

**Reference:** Design Section "ENHANCED: vet-agent / tdd-plan-reviewer" lines 384-390

**Expected Outcome:** Agent warns about missing outline review

**Success Criteria:**
- Outline review check added
- Fix policy unchanged (remains review-only)
- Requirements inheritance mentioned

---

## Step 2.3: Enhance tdd-plan-reviewer

**Objective:** Add outline validation without changing fix policy

**Execution Model:** Sonnet

**Implementation:**

Edit `agent-core/agents/tdd-plan-reviewer.md`:

1. Add outline validation:
   - When reviewing TDD runbook, check if `plans/<job>/reports/runbook-outline-review.md` exists
   - If outline review missing, warn that outline was not reviewed

2. Add requirements inheritance:
   - Verify runbook covers outline's requirements mapping

3. Preserve review-only behavior:
   - Do NOT change fix policy
   - Caller (planner) applies fixes with full context

**Reference:** Design Section "ENHANCED: vet-agent / tdd-plan-reviewer" lines 384-390

**Expected Outcome:** Agent warns about missing outline review

**Success Criteria:**
- Outline review check added
- Fix policy unchanged
- Requirements inheritance mentioned

---

## Step 2.4: Enhance vet-fix-agent

**Objective:** Add runbook rejection and requirements context requirement

**Execution Model:** Sonnet

**Implementation:**

Edit `agent-core/agents/vet-fix-agent.md`:

1. Add explicit runbook rejection to Step 0:
   - If task prompt contains path to `runbook.md` → reject with error
   - Error message: "This agent reviews implementation changes, not planning artifacts. Use vet-agent for runbook review."

2. Add requirements context requirement:
   - Document that prompt MUST include requirements summary
   - Example format from design Section FP-5

3. Document scope explicitly:
   - Agent reviews implementation changes (code, tests)
   - Agent does NOT read runbook.md
   - Input is changed file list, not git diff text

**Reference:** Design Section "FP-5: Phase Boundary Review (ENHANCED)" lines 285-334

**Expected Outcome:** Agent rejects runbook paths, requires requirements context

**Success Criteria:**
- Step 0 includes runbook rejection logic
- Documentation requires requirements in prompt
- Scope is explicit (implementation only)


### Phase 3: Skill Changes

## Step 3.1: Update /design skill

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

## Step 3.4: Update /orchestrate skill

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


### Phase 4: Infrastructure

## Step 4.1: Update prepare-runbook.py

**Objective:** Add Phase metadata to step file frontmatter

**Execution Model:** Sonnet

**Implementation:**

Edit `agent-core/bin/prepare-runbook.py`:

1. Extract phase number from step headers:
   - Parse `## Phase N` headers in runbook
   - Track current phase as steps are processed
   - For flat runbooks (no phase headers), use phase 1

2. Add Phase field to step file frontmatter:
   - Each step file gets `phase: N` in YAML frontmatter
   - Enables orchestrator phase boundary detection

3. Validation:
   - Warn if phase numbers have gaps
   - Error if phase numbers decrease (non-monotonic)

**Reference:** Design Section "Implementation Notes" line 540

**Expected Outcome:** Step files include phase metadata for orchestrator

**Success Criteria:**
- Step files have `phase: N` in frontmatter
- Phase extraction handles both flat and grouped runbooks
- Validation catches phase ordering issues

---

## Step 4.2: Update workflows.md

**Objective:** Document runbook outline format for discoverability

**Execution Model:** Sonnet

**Implementation:**

Edit `agents/decisions/workflows.md`:

1. Add new section "Runbook Artifacts":
   - Document runbook outline format from design
   - Include template structure
   - Explain requirements mapping table
   - Explain phase structure format

2. Reference the format:
   - Cross-reference from plan-adhoc Point 0.75
   - Cross-reference from plan-tdd Phase 1.5

**Content to add (from design lines 196-228):**

```markdown
## Runbook Outline Format

**Location:** `plans/<job>/runbook-outline.md`

**Structure:**
- Header with design reference and type (tdd | general)
- Requirements mapping table
- Phase structure with objectives and step titles
- Key decisions reference

**Template:**
[Include format from design FP-3 section]
```

**Reference:** Design Section "Implementation Notes" line 539

**Expected Outcome:** Runbook outline format is documented and discoverable

**Success Criteria:**
- New "Runbook Artifacts" section exists
- Complete format template included
- Cross-references from /plan-adhoc Point 0.75 and /plan-tdd Phase 1.5 exist


## Orchestrator Instructions

Execute all phases sequentially:

1. Read each phase header to understand objective and complexity
2. Execute all steps in phase order
3. After each phase: check reports directory for review results
4. If review identifies blockers: fix and re-run phase
5. Continue to next phase

**Stop on:** Any failure in step execution, blocker in review, or missing artifact.
