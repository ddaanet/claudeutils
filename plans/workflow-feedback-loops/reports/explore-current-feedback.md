# Workflow Feedback Loop Architecture — Current State

**Date:** 2026-02-04
**Scope:** Design, planning, execution, and validation phases
**Status:** Comprehensive analysis of existing checkpoints and validation layers

---

## Summary

The codebase implements a multi-layer feedback system with review checkpoints at critical workflow transitions. Feedback is performed by specialized agents (design-vet-agent, vet-agent, tdd-plan-reviewer) that validate specific document types and apply fixes where appropriate. The architecture distinguishes between design-time, planning-time, and execution-time reviews. Significant gaps exist: no pre-design outline validation, no early planning feedback, and limited intermediate phase review during execution.

---

## 1. Current Review Checkpoints

### 1.1 Design Phase (`/design` skill)

**Checkpoint Location:** Phase C.3 — After design document generation

**Document Type:** `design.md`

**Review Agent:** `design-vet-agent` (opus model)

**What Gets Reviewed:**
- Completeness (problem, requirements, architecture, decisions, affected files, testing strategy, next steps)
- Clarity (unambiguous decisions, rationale, assumptions, technical accuracy)
- Feasibility (realistic complexity, no circular dependencies, error handling, migration path)
- Consistency (architectural patterns, project conventions, module structure, naming)
- Documentation Perimeter validation (required reading files exist)
- Plugin topic detection (skill-loading directives present for hooks/agents/skills)
- Requirements alignment (all functional/non-functional requirements addressed)

**Review Output:**
- Report written to: `plans/<job-name>/reports/design-review.md`
- Assessment: Ready / Needs Minor Changes / Needs Significant Changes
- Critical/Major/Minor issue categorization
- Positive observations

**Validation Rules (from design-vet-agent.md):**
- Validates design document only (rejects runbooks with Step/Cycle headers)
- Checks design against existing patterns using Glob/Grep
- Verifies memory-index references exist
- Maps requirements to design decisions

**Post-Review Process:**
- Designer reads review report (lines 238-249 of /design SKILL.md)
- CRITICAL and MAJOR issues must be fixed
- Re-review if changes significant
- Proceed to Phase C.5 (handoff + commit)

**Execution:** Manual in main session. Cannot run in sub-agents.

---

### 1.2 TDD Planning Phase (`/plan-tdd` skill)

**Checkpoint Location:** Phase 5.2 — After runbook generation, before prepare-runbook.py

**Document Type:** `runbook.md` with `type: tdd`

**Review Agent:** `tdd-plan-reviewer` (sonnet model)

**What Gets Reviewed:**
- GREEN phase anti-patterns (prescriptive code vs behavior description)
- RED/GREEN sequencing violations (will RED fail before GREEN?)
- Implementation hints vs prescriptions
- Test specification quality (specific assertions, expected failure messages)
- Weak RED phase assertions (structure-only vs behavior tests)
- Metadata accuracy (Total Steps matches actual cycle count)
- Empty-first cycle ordering (should test simplest happy path first)
- File reference validation (CRITICAL: runbook paths must exist in codebase)

**Review Process:**
- Phase 1: Scan for code blocks in GREEN phases using Grep (`^\*\*GREEN Phase:\*\*` with -A context)
- Phase 2: Validate all file paths (Common Context, RED/GREEN, verify commands) using Glob
- Phase 3: Analyze each cycle for sequencing violations
- Phase 4: Generate report

**Review Output:**
- Report written to: `plans/<feature-name>/reports/runbook-review.md`
- Summary: violations count, overall assessment (PASS / NEEDS REVISION)
- Critical/Major issues with locations and recommendations

**Validation Rules (from tdd-plan-reviewer.md):**
- Validates TDD runbook only (YAML `type: tdd`, contains `## Cycle` headers)
- Rejects design documents (→ use design-vet-agent)
- Rejects general runbooks (→ use vet-agent)
- Uses review-tdd-plan skill (separate file) for detailed criteria

**Post-Review Process:**
- Planner reads review report (lines 438-448 of /plan-tdd SKILL.md)
- If PASS: Proceed to Phase 5.4 (prepare-runbook.py)
- If violations found:
  - Apply all HIGH and MEDIUM priority fixes
  - Update runbook
  - Re-run tdd-plan-reviewer if changes significant
  - Iterate until PASS

**Execution:** Automatic delegation from /plan-tdd Phase 5.2. Runs in sub-agent.

---

### 1.3 General Planning Phase (`/plan-adhoc` skill)

**Checkpoint Location:** Point 3 — After runbook generation, before prepare-runbook.py

**Document Type:** General runbook (no `type: tdd` required)

**Review Agent:** `vet-agent` (sonnet model)

**What Gets Reviewed:**
- Completeness (all required steps present, well-defined)
- Correctness (steps are accurate, logic sound)
- Executability (steps are unambiguous, have clear success criteria)
- File path validation (CRITICAL: all referenced paths exist, use Glob to verify)
- Requirements satisfaction (if requirements context included)
- Weak orchestrator metadata (total steps, execution model, error escalation, success criteria)

**Review Scope:**
- Runbook structure and metadata
- File references
- Step organization
- Prerequisite completeness

**Review Output:**
- Report written to: `plans/<name>/reports/runbook-review.md`
- Assessment: Ready / Needs Minor Changes / Needs Significant Changes
- Critical/Major/Minor issue categorization
- Requirements validation table (if applicable)

**Validation Rules (from vet-agent.md):**
- Validates code and runbooks (rejects design documents → use design-vet-agent)
- Document type check in Step 0
- Structured issue categorization with location, problem, fix/suggestion

**Post-Review Process:**
- Planner reads review report (lines 293-310 of /plan-adhoc SKILL.md)
- Apply all CRITICAL and MAJOR fixes (required)
- Iterate if changes significant
- Proceed to Point 4 (prepare-runbook.py) when "Ready"

**Execution:** Manual delegation from /plan-adhoc Point 3.

---

### 1.4 Execution Phase (`/orchestrate` skill)

**Checkpoint Location:** Step 3.4 — At phase boundaries (light checkpoints) and final phase (full checkpoints)

**Light Checkpoint:**
- **When:** Every phase boundary
- **What Checks:**
  1. Fix: Run `just dev`, fix failures, commit when passing
  2. Functional: Check for stubs/hardcoded values against design

**Full Checkpoint:**
- **When:** Final phase boundary or explicit `checkpoint: full` markers
- **What Checks:**
  1. Fix: Run `just dev`, fix failures, commit when passing
  2. Vet: Delegate to vet-fix-agent for quality review (writes report, applies critical/major fixes)
  3. Functional: Check for stubs/hardcoded values against design

**Vet-fix-agent Review Detail:**
- Scope: Accumulated changes since last checkpoint
- Issues categorized as critical/major/minor
- Each issue marked as FIXED or UNFIXABLE
- If UNFIXABLE critical/major issues exist → escalate to user
- If all fixed → proceed

**Other Execution Safeguards:**
- Post-step tree check: After each step, verify no uncommitted changes (git status --porcelain)
  - If ANY uncommitted changes: STOP execution, escalate to user
  - Rationale: Every step must leave clean tree; step agent is responsible for committing

**Execution:** Automatic at phase boundaries during orchestration.

---

## 2. Review Agents Architecture

### 2.1 design-vet-agent

**File:** `/Users/david/code/claudeutils/agent-core/agents/design-vet-agent.md`

**Model:** opus (architectural analysis)

**Input Validation (Step 0):**
- Check filename is `design.md` or path contains "design"
- Verify NOT a runbook (no Step/Cycle headers, no `type: tdd`)
- Return structured error if wrong type

**Review Criteria:**
1. Completeness (all required sections)
2. Clarity (unambiguous decisions, clear rationale)
3. Feasibility (realistic, no circular deps, error handling)
4. Consistency (architectural patterns, project conventions)
5. Documentation Perimeter (required reading files exist)
6. Plugin topics (skill-loading directives present)
7. Requirements alignment (requirements traced to design elements)

**Output Format:**
- Critical Issues (must fix before planning)
- Major Issues (strongly recommended)
- Minor Issues (optional)
- Requirements Alignment table (if requirements present)
- Positive Observations
- Recommendations
- Next Steps

**Assessment Criteria:**
- Ready: No critical, 0-1 major issues
- Needs Minor Changes: No critical, 1-3 major issues
- Needs Significant Changes: Critical issues present OR 4+ major issues OR architectural rework needed

---

### 2.2 vet-agent

**File:** `/Users/david/code/claudeutils/agent-core/agents/vet-agent.md`

**Model:** sonnet (code/runbook review)

**Input Validation (Step 0):**
- Check if file is `design.md` or contains "design" in path
- If design document → return error (use design-vet-agent)
- Accepts code and runbooks

**Review Scope Options:**
1. Uncommitted changes (git diff)
2. Recent commits (last N commits)
3. Current branch (all commits since branch point)
4. Specific files (named files only)
5. Everything (uncommitted + recent)

**Review Criteria:**
1. Code Quality (logic, edge cases, error handling, readability)
2. Project Standards (patterns, conventions, style, dependencies, CLAUDE.md compliance)
3. Security (no hardcoded secrets, input validation, vulnerabilities)
4. Testing (appropriate coverage, clear tests)
5. Documentation (comments, updated docs, commit messages)
6. Completeness (TODOs addressed, no debug code, related changes included)
7. Requirements Validation (if context provided — functional/non-functional requirements met)

**Runbook-Specific Checks:**
- Extract all file paths referenced in steps/cycles
- Use Glob to verify each path exists
- Use Grep to verify referenced test functions exist
- Flag missing files as CRITICAL (runbooks fail immediately with wrong paths)

**Output Format:**
- Critical Issues (must fix before commit/merge)
- Major Issues (strongly recommended)
- Minor Issues (optional)
- Requirements Validation table (if applicable)
- Positive Observations
- Recommendations
- Next Steps

**Assessment Criteria:**
- Ready: No critical, 0-1 major issues
- Needs Minor Changes: No critical, 1-3 major issues
- Needs Significant Changes: Critical present OR 4+ major issues OR design problems

---

### 2.3 vet-fix-agent

**File:** `/Users/david/code/claudeutils/agent-core/agents/vet-fix-agent.md`

**Model:** sonnet (code/runbook review + fixes)

**Purpose:** Review AND apply fixes. Used during orchestration where no other agent has fix context.

**Difference from vet-agent:**
- Same review scope and criteria as vet-agent
- PLUS: Applies fixes for critical/major issues using Edit tool
- Each issue marked as FIXED or UNFIXABLE
- If fix cannot be applied safely → mark UNFIXABLE (architectural changes, ambiguous approaches)
- Final assessment reflects post-fix state

**Fix Constraints:**
- Fix ONLY critical and major issues
- Each fix must be minimal and targeted (no scope creep)
- Never fix minor issues (report only)
- Never refactor surrounding code while fixing
- If a fix would require architectural changes → mark UNFIXABLE

**Output Format:**
- Same as vet-agent PLUS
- Fixes Applied section (what was changed and why)
- Each issue marked as FIXED or UNFIXABLE with status reason

---

### 2.4 tdd-plan-reviewer

**File:** `/Users/david/code/claudeutils/agent-core/agents/tdd-plan-reviewer.md`

**Model:** sonnet (TDD runbook review)

**Input Validation:**
- Check YAML frontmatter for `type: tdd`
- Check for `## Cycle` headers
- If design document → error (use design-vet-agent)
- If general runbook (no `type: tdd`) → error (use vet-agent)
- If code/implementation → error (use vet-agent)

**Review Process (from review-tdd-plan skill):**
1. Scan for code blocks in GREEN phases (Grep pattern)
2. Validate all file references (Glob for paths, Grep for functions)
3. Analyze cycles for RED/GREEN sequencing
4. Generate report with violations

**Review Output:**
- Total cycles count
- Violations found (critical, warnings)
- Critical Issues (implementation code in GREEN, RED/GREEN violations)
- Warnings (large implementations, empty-first cycles)
- Recommendations
- Overall assessment: PASS / NEEDS REVISION

---

## 3. Input Validation Pattern

All review agents implement Step 0 validation:

```
Step 0: Validate Document Type
├─ design-vet-agent: design.md only (rejects runbooks)
├─ vet-agent: code/runbooks (rejects design)
├─ vet-fix-agent: code/runbooks (rejects design)
└─ tdd-plan-reviewer: TDD runbooks only (rejects design/general runbooks)
```

**Error Format (Consistent):**
```
Error: Wrong agent type
Details: [What agent reviews vs. what was given]
Context: [Evidence from document]
Recommendation: [Which agent to use]
```

---

## 4. Gaps in Current Feedback Architecture

### Gap 1: No Design Outline Validation (Phase A → Phase B)

**Where:** Design skill Phase A.5 (after outline generation, before user discussion)

**Missing:** Feedback checkpoint on freeform outline before Phase B (iterative discussion)

**Current Flow:**
```
Phase A: Research + Outline
  ↓ (outline presented to user)
Phase B: Iterative Discussion
  ↓ (user provides feedback)
Phase C: Generate Design
```

**Impact:**
- Outlines may be incomplete or ambiguous
- User spends multiple discussion rounds on foundational issues
- Early validation could catch scope/feasibility issues before design investment

**Evidence:**
- Phase A.5 output: "Freeform summary presented to user in conversation (not a file)"
- No agent involvement
- No validation criteria defined

---

### Gap 2: No Pre-Design Requirements Validation (Before Phase A)

**Where:** Design skill Phase A.0 (requirements checkpoint)

**Missing:** Validation that requirements.md (if present) is valid, complete, and aligned with design task

**Current Flow:**
```
Phase A.0: Requirements Checkpoint
  ├─ If requirements.md exists: read and summarize
  └─ (No validation of requirements quality/completeness)
```

**Impact:**
- Incomplete or poorly-written requirements go undetected
- Design built on ambiguous requirements
- Late discovery of scope issues after design completion

**Evidence:**
- Phase A.0: "Document requirements discovered during research"
- No agent validation of requirements document
- Traceability mapping (lines 171-183 of /design) happens DURING design, not before

---

### Gap 3: No Early Planning Feedback (Point 0.5 of `/plan-adhoc`)

**Where:** `/plan-adhoc` Point 0.5 (codebase discovery), Point 1 (script evaluation)

**Missing:** Feedback on runbook outline/structure BEFORE full runbook generation (Point 3 review)

**Current Flow:**
```
Point 0: Tier Assessment → (no validation)
Point 0.5: Discover Codebase → (no validation)
Point 1: Evaluate Script vs Direct → (no validation)
Point 2: Create Metadata → (no validation)
Point 3: Vet Review → [FIRST VALIDATION CHECKPOINT]
```

**Impact:**
- Runbooks with missing file paths are written before discovery happens
- Wrong tier assessment not caught until vet review
- Large structural issues discovered late

**Evidence:**
- Points 0-2 have no review mechanism
- Point 3 is first and only checkpoint before prepare-runbook.py
- File path validation happens in vet-agent, not during discovery

---

### Gap 4: Limited Intermediate Phase Validation (During `/orchestrate`)

**Where:** `/orchestrate` skill execution between phase boundaries

**Missing:** Feedback on phase output BEFORE proceeding to next phase (only at phase END)

**Current Flow:**
```
Phase N work
  ↓
Phase N complete (checkpoint runs)
  ├─ Light: Fix + Functional check
  └─ Full: Fix + Vet + Functional check
```

**What's Missing:**
- Incremental validation within phases (e.g., after 3-5 cycles)
- Intermediate artifact checks (e.g., test coverage growing)
- Early detection of stubs/incomplete implementations

**Evidence:**
- Orchestrate skill only documents phase-boundary checkpoints (lines 133-141)
- No intra-phase checkpoints mentioned
- statusline-wiring learning (learnings.md): "3 major gaps at vet checkpoint that integration tests would have caught earlier"

---

### Gap 5: No Handoff Document Validation

**Where:** `/handoff` skill or session.md updates

**Missing:** Validation that session.md handoff is well-formed and complete

**Current Impact:**
- Malformed pending tasks
- Missing metadata (model, restart flag)
- Unclear task descriptions
- Next session starts without clear direction

**Evidence:**
- vet-requirement.md lists "Session handoffs (already reviewed during /handoff)" as NOT requiring vet
- No specification of what "already reviewed" means
- No validation rules defined for session.md format

---

### Gap 6: No Cross-Document Traceability Validation

**Where:** Throughout workflow

**Missing:** Validation that design requirements are actually implemented in runbook steps

**Current Flow:**
```
Design → specifies requirements
Runbook → organizes steps
(No automated check: do all design requirements map to runbook steps?)
```

**Impact:**
- Requirements drift after design
- Implementation scope creep not caught
- Requirements gap discovered at execution time

**Evidence:**
- Design-vet-agent verifies requirements exist (lines 100-115)
- Vet-agent verifies implementation satisfies requirements (lines 122-126)
- But no step that validates: "Does runbook cover all design requirements?"

---

### Gap 7: No Repository/Consistency Check Before Planning

**Where:** `/plan-adhoc` Point 0 (tier assessment) before Point 0.5

**Missing:** Early validation that design document actually exists and is ready

**Current Flow:**
```
Point 0: Tier Assessment
  ↓ (assumes design exists)
Point 0.5: Discover Codebase
  └─ (might fail if design path wrong)
```

**Impact:**
- Planner discovers design missing or wrong path after tier assessment
- Design not ready (still has TODOs, confirmations pending)
- Wastes planner tokens on analysis before problem discovered

**Evidence:**
- Point 0 says "if design specifies" but doesn't verify design exists
- TDD plan Phase 1.2 does verify design: "STOP if: not found, empty, permission denied"
- Ad-hoc plan has no equivalent check

---

## 5. Validation Rules Summary

### Per-Document-Type Validation

| Document Type | Agent | Validates | Output Location |
|---|---|---|---|
| design.md | design-vet-agent | Completeness, clarity, feasibility, consistency | plans/*/reports/design-review.md |
| TDD runbook | tdd-plan-reviewer | Code in phases, RED/GREEN, file paths | plans/*/reports/runbook-review.md |
| General runbook | vet-agent | Structure, file paths, requirements | plans/*/reports/runbook-review.md |
| Execution changes | vet-fix-agent | Code quality, standards, requirements | plans/*/reports/checkpoint-*-vet.md |
| requirements.md | (none) | Not validated | — |
| session.md | (none) | Not validated | — |

---

## 6. File Path Validation Pattern

**Locations where file path validation occurs:**

1. **Design-vet-agent** (Step 4, lines 82-84):
   - Verifies "Documentation Perimeter" files exist
   - Checks design references using Glob

2. **TDD-plan-reviewer** (Phase 2, lines 149-166):
   - Validates all file paths in Common Context, RED, GREEN, verify commands
   - Critical: missing paths = runbook failure at execution

3. **Vet-agent** (Section 3, lines 110-115):
   - Extracts file paths from steps/cycles
   - Verifies with Glob
   - Verifies test function names exist with Grep

4. **During /plan-adhoc Point 0.5**:
   - Discovers relevant files using Glob
   - Records actual file paths for runbook steps
   - Explicitly states: "NEVER assume file paths from conventions alone"

---

## 7. Behavioral Test Validation (TDD-specific)

**RED phase assertion quality check (tdd-plan-reviewer.md lines 100-225):**

**Weak (structural only):**
- `assert result.exit_code == 0`
- `assert "KEY" in env_vars`
- `assert hasattr(obj, "method")`

**Strong (behavioral):**
- `assert "Mode: plan" in result.output`
- `assert env_vars["KEY"] != ""`
- `assert obj.method(input) == expected`

**Validation Rule:**
- If RED test can pass with stub returning constant/empty value → weak
- Must add content assertions or mock interactions

---

## 8. Key Patterns and Rules

### Checkpoint Triggering

**Design Phase:**
- Automatic at Phase C.3 (after design.md created)
- Cannot be skipped

**TDD Planning:**
- Automatic at Phase 5.2 (after runbook.md created)
- Cannot be skipped

**General Planning:**
- Manual delegation at Point 3 (planner responsibility)
- Can be skipped (though discouraged)

**Execution:**
- Automatic at phase boundaries
- Light checkpoint: every phase
- Full checkpoint: final phase + marked phases

### Issue Severity Classification

**Consistent across all agents:**
- Critical: Must fix before proceeding
- Major: Should fix (strongly recommended)
- Minor: Optional (document as future improvements)

**Escalation Rule:**
- If CRITICAL or high-priority MAJOR issues unfixable → escalate to user
- Agent applies fixes where possible, flags unfixable items

### Document Type Routing

**All agents implement Step 0 validation:**
- Rejects wrong document types with structured error
- Recommends correct agent/tool
- Prevents agent misuse

---

## 9. Missing Feedback Opportunities

**High Priority (affect multiple workflows):**

1. **Pre-design validation** (Gap 1 + 2)
   - Outline quality check before Phase B discussion
   - Requirements document validation (if exists)
   - Would save design iteration cycles

2. **Design-to-runbook traceability** (Gap 6)
   - Validate runbook steps cover design requirements
   - Would catch scope drift before execution
   - Could happen at planning review (Point 3)

3. **Pre-handoff validation** (Gap 5)
   - Session.md well-formedness check
   - Pending task metadata validation
   - Would improve continuity between sessions

**Medium Priority (specific workflow gaps):**

4. **Early planning structure validation** (Gap 3)
   - Runbook outline review before full generation
   - Would catch tier/structure issues early

5. **Intermediate execution checkpoints** (Gap 4)
   - Intra-phase validation (not just phase boundaries)
   - Would catch issues earlier

6. **Pre-planning prerequisite validation** (Gap 7)
   - Verify design exists and is ready before planning starts
   - Would prevent wasted planner tokens

---

## 10. Checkpoint Architecture Diagram

```
Workflow Stage          Checkpoint           Agent        Output
─────────────────────────────────────────────────────────────────
DESIGN PHASE
Phase A-B Research      (none)               —            —
Phase A.5 Outline       (none)               —            —
Phase B Discussion      (none, manual)       —            —
Phase C.1 Design doc    (created)            —            design.md
Phase C.3 Design vet →  design-vet-agent     opus         design-review.md
Phase C.4 Apply fixes   (manual, design)     —            design.md updated
Phase C.5 Handoff       (none)               —            session.md updated

TDD PLANNING PHASE
Phase 0 Tier assess     (none)               —            —
Phase 1-4 Gen runbook   (none)               —            runbook.md
Phase 5.2 TDD review →  tdd-plan-reviewer    sonnet       runbook-review.md
Phase 5.3 Apply fixes   (manual, planner)    —            runbook.md updated
Phase 5.4 Prepare       (auto)               —            step-*.md created
Phase 5.5 Handoff       (none)               —            session.md updated

AD-HOC PLANNING PHASE
Point 0 Tier assess     (none)               —            —
Point 0.5 Discover      (none)               —            —
Point 1 Evaluate        (none)               —            —
Point 2 Metadata        (none)               —            —
Point 3 Review     →    vet-agent            sonnet       runbook-review.md
Point 4.1 Prepare       (auto)               —            step-*.md created
Point 4.3 Handoff       (none)               —            session.md updated

EXECUTION PHASE
Step N execution        (none per-step)      [plan-task]  reports/step-N.md
Phase boundary:
  - Light checkpoint → Fix + Functional
  - Full checkpoint → Fix + Vet + Functional → vet-fix-agent → checkpoint-*-vet.md
Final checkpoint        (vet-fix-agent)      sonnet       checkpoint-final-vet.md
```

---

## 11. Validation Completeness Assessment

### Fully Covered

✓ Design document architectural correctness
✓ TDD runbook RED/GREEN discipline
✓ Runbook file path existence
✓ Code quality and standards (implementation phase)
✓ Requirements satisfaction (code against requirements)

### Partially Covered

⚠ Runbook structure (only after full generation, not outline)
⚠ Tier assessment (implicit, not validated)
⚠ Design-to-implementation traceability (only at code review, not earlier)

### Not Covered

✗ Design outline quality (before Phase B discussion)
✗ Requirements document quality (if exists)
✗ Session handoff well-formedness
✗ Intra-phase execution progress
✗ Design prerequisite existence (before planning)
✗ Cross-document consistency (design ↔ runbook ↔ implementation)

---

## 12. Agent Tool Usage for Validation

**Read tool:** Design docs, runbooks, requirements, code
**Glob tool:** File path verification (critical for runbook validation)
**Grep tool:** Pattern matching (code blocks, test functions, function signatures)
**Write tool:** Report generation
**Edit tool:** Fix application (vet-fix-agent only)
**Bash tool:** Git operations for change scope (vet agents)
**Skill tool:** TDD reviewer loads review-tdd-plan skill for detailed criteria

---

## 13. Report Locations Pattern

**Design phase:**
`plans/<job>/reports/design-review.md`

**TDD planning:**
`plans/<feature>/reports/runbook-review.md`

**General planning:**
`plans/<name>/reports/runbook-review.md`

**Execution checkpoints:**
`plans/<name>/reports/checkpoint-{N}-vet.md` (for phase N)
`plans/<name>/reports/checkpoint-final-vet.md` (final phase)

**Ad-hoc reviews:**
`tmp/vet-review-{TIMESTAMP}.md`

---

## Recommendations for Future Enhancement

Based on the gaps identified:

1. **Add outline validation checkpoint** in `/design` Phase A → Phase B
2. **Add requirements validation** (separate agent or design-vet-agent extension)
3. **Add design-to-runbook traceability check** in planning review agents
4. **Add pre-planning design existence check** in `/plan-adhoc` and `/plan-tdd`
5. **Add session.md validation** before handoff commits
6. **Add intra-phase validation** in `/orchestrate` (every 3-5 cycles in TDD, every 2 steps in general)
7. **Add cross-workflow consistency checks** (design requirements vs. implemented features)

