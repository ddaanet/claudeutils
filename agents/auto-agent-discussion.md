# Discussion Handoff: Plan-to-Execution Script Design

**Date:** 2026-01-19
**Topic:** Automating plan-specific agent creation via mechanical transformation script
**Discussion Type:** Design exploration for execution preparation tooling

---

## Problem Statement

User executed Phase 3 plan using weak orchestrator. Weak agent attempted to create plan-specific agent during execution, revealing workflow gap: **no formalized step for plan-specific agent creation**.

**Current pattern (per context.md:47-50):**
- Plan-specific agent should be created during planning by planning agent (sonnet-level)
- NOT during execution (too complex for haiku weak orchestrator)
- But: No enforcement, no clear integration point in workflow

**User observation:**
- Step splitting exists as separate phase (after design, before execution)
- Agent creation is orphaned - no clear home in workflow
- Natural coupling: steps reference agent, agent contains plan context

---

## Key Context Files

### Core Instructions
- `CLAUDE.md` - Project instructions including:
  - Delegation principle (lines 44-77)
  - Script-first evaluation (lines 79-118)
  - Model selection (lines 120-130)
  - Quiet execution pattern (lines 132-154)
  - Commit agent delegation (lines 156-200)

### Session State
- `agents/session.md` - Current session status:
  - Phase 3 plan complete and READY (line 3)
  - Plan location: plans/unification/phase3-execution-plan.md (line 30)
  - Recent work includes step splitting (line 8)

- `agents/context.md` - Stable architecture context:
  - Plan-specific agent pattern (lines 33-57)
  - Weak orchestrator pattern (lines 59-70)
  - Quiet execution pattern (lines 72-82)
  - Design decisions and rationale (lines 84-166)

### Implementation Artifacts
- `agent-core/agents/task-execute.md` - Baseline task agent template
- `agent-core/bin/create-plan-agent.sh` - Existing script for agent creation (unused)
- `plans/unification/phase3-execution-plan.md` - Example plan structure
- `skills/skill-task-plan.md` - 4-point planning process skill

---

## Proposed Solution: Mechanical Transformation Script

**Single script bridges planning → execution:**

### Input Format
Structured plan document with three required sections:

```
## Common Context
[Shared knowledge appended to plan-specific agent]
- Architecture decisions
- File paths and conventions
- Constraints and requirements
- Background needed by all steps

## Step N: [Title]
[Individual step instructions - becomes step-N.md]

## Orchestrator Instructions
[Sequencing, error handling, reporting - becomes orchestrator-plan.md]
```

### Output Artifacts
1. **Plan-specific agent** - `.claude/agents/<plan-name>-task.md`
   - Baseline from task-execute.md
   - + Appended common context section

2. **Step files** - `plans/<plan-name>/steps/step-N.md`
   - Individual step instructions extracted

3. **Orchestrator plan** - `plans/<plan-name>/orchestrator-plan.md`
   - Instructions for weak agent execution

### Workflow Integration
Replace current orphaned agent creation with:

```
Phase 1: Design (sonnet)
└─ Write plan document with required sections

Phase 2: Prepare Execution (run script)
├─ Create plan-specific agent
├─ Extract step files
├─ Generate orchestrator plan
└─ Validate prerequisites

Phase 3: Execute (weak orchestrator)
└─ Invoke plan-specific agent per step
```

---

## Design Questions for Discussion

### 1. Common Context Scope
**What belongs in common context section?**
- Architecture/design decisions affecting all steps?
- File paths, conventions, constraints?
- Background knowledge execution agents need?
- Domain knowledge vs procedural guidance?

**Example from Phase 3:**
```
Output: scratch/consolidation/design/compose-api.md
Inputs: scratch/consolidation/analysis/*.md
Principle: Extract patterns, synthesize unified API
Model: All steps use sonnet (architectural design)
```

### 2. Orchestrator Section Content
**What guidance does weak orchestrator need?**
- Step sequencing (linear/parallel/conditional)?
- Success criteria per step?
- Error escalation rules (abort vs retry vs escalate)?
- Reporting requirements?
- Model overrides per step?

**Minimal example:**
```
Execute steps 1-5 sequentially
On error: Stop and report
Success: All steps complete, output file exists
```

### 3. Script Interface Design

**Location:**
- `agent-core/bin/prepare-execution.sh` (reusable)?
- `claudeutils/scripts/prepare-execution.sh` (project-specific)?

**Invocation:**
```bash
prepare-execution.sh <plan-file>
# Or with explicit paths
prepare-execution.sh --plan plans/unification/phase3-execution-plan.md \
                     --agent-dir .claude/agents \
                     --steps-dir plans/unification/steps
```

**Output:**
- List of created files (validation)
- Error if required sections missing
- Summary for review

### 4. Plan Format Requirements

**Option A: Strict validation**
- Fail if required sections missing (Common Context, Steps, Orchestrator)
- Enforce header format exactly
- No execution without valid structure

**Option B: Flexible with defaults**
- Common context optional (empty = pure task-execute baseline)
- Orchestrator optional (default = sequential, stop on error)
- Only steps required

**Option C: Frontmatter + sections**
```yaml
---
plan: phase3
agent: phase3-task
model: sonnet
output: scratch/consolidation/design/compose-api.md
---
```

**Trade-offs:**
- Strict: Forces discipline, prevents errors
- Flexible: Easier adoption, sensible defaults
- Frontmatter: Machine-readable metadata, validation-friendly

### 5. Integration with task-plan Skill

**Current 4-point process:**
1. Script evaluation (≤25 lines = bash, else delegate)
2. Agent identification (roles/models needed)
3. Sequential dependencies (step ordering)
4. Step files creation

**Proposal: Point 4 becomes "Execution Preparation"**

Should script invocation be:
- **Manual** - User/orchestrator runs script when ready
- **Automatic** - Planning agent runs script as final planning step
- **Skill-driven** - New `/prepare` skill wraps script
- **Integrated** - task-plan skill invokes script automatically

### 6. Baseline Agent Composition

**How does common context combine with task-execute.md?**

**Option A: Simple append**
```
[Full task-execute.md content]

---
# Plan-Specific Context

[Common context section]
```

**Option B: Section merge**
- Identify sections in task-execute.md
- Insert common context into specific sections (e.g., after "## Context")

**Option C: Template variables**
- task-execute.md has `{{COMMON_CONTEXT}}` placeholder
- Script replaces with common context content

### 7. Change Management

**What if plan changes mid-execution?**
- Re-run script (overwrites artifacts)?
- Incremental update (patch specific files)?
- Version artifacts (phase3-v2-task.md)?
- Fail if artifacts exist?

**What if execution reveals plan errors?**
- Update plan document and re-run script?
- Manual fix of generated artifacts?
- Rollback to planning phase?

### 8. Validation and Prerequisites

**Should script validate:**
- `agent-core/agents/task-execute.md` exists?
- Output directories exist/are writable?
- No conflicting artifacts exist?
- Plan section headers are unique?
- Step numbers are sequential?

**Failure modes:**
- Missing baseline agent → fail with error
- Existing artifacts → prompt to overwrite?
- Invalid plan structure → detailed error message
- Missing required sections → fail with requirements

---

## Success Criteria

**Script should:**
1. Transform valid plan → complete execution artifacts
2. Validate plan structure and fail clearly on errors
3. Be idempotent (re-runnable without side effects)
4. Integrate cleanly with existing workflow
5. Reduce manual toil in execution preparation

**After implementation:**
1. No more orphaned agent creation step
2. Clear boundary: plan document → execution artifacts
3. Repeatable, reviewable, version-controlled
4. Weak orchestrator can validate prerequisites automatically

---

## Discussion Goals

1. **Refine common context scope** - What belongs in agent vs steps vs orchestrator?
2. **Choose plan format** - Strict validation vs flexible defaults vs frontmatter?
3. **Define script interface** - Where it lives, how it's invoked, integration points
4. **Resolve composition strategy** - How common context merges with baseline
5. **Establish change management** - How to handle plan updates mid-execution
6. **Finalize validation rules** - What script should check/enforce

**Expected output from discussion:**
- Specification for script implementation
- Updated task-plan skill Point 4 guidance
- Plan template example
- Integration pattern with weak orchestrator

---

## References

**Existing patterns to learn from:**
- `/shelve` skill - Progressive disclosure, template separation
- `/commit` skill - Proper Claude Code skill structure
- `create-plan-agent.sh` - Current agent creation script (single-purpose)
- Weak orchestrator pattern - Error escalation, quiet execution

**Related work:**
- Phase 3 ready for execution (validates pattern works)
- Formalized 4-point planning validated through Phase 2/3
- Agent-core sync pattern established (just sync-to-parent)

**User context:**
- "User's planning ≠ Claude Code planning mode"
- User planning can write files, delegate to file-writing agents
- Not bound by EnterPlanMode/ExitPlanMode restrictions
- Prefers mechanical transformation over manual steps
