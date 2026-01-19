# Oneshot Workflow Design Document

**Date:** 2026-01-19
**Status:** Design complete, ready for planning
**Scope:** Ad-hoc task execution workflow with supporting tooling

---

## Overview

Formalize the workflow for executing one-off, ad-hoc tasks using weak orchestrator pattern. Includes terminology standardization, skill definitions, and automation script.

**Not in scope:** Feature development workflow (TDD emphasis, separate design).

---

## Terminology

| Term | Definition |
|------|------------|
| **Job** | What the user wants to accomplish |
| **Design** | Opus output from design session; may contain phases |
| **Phase** | Design-level segmentation for complex work |
| **Runbook** | Implementation steps for a phase or standalone job |
| **Step** | Individual unit within runbook |
| **Runbook prep** | 4-point process: Evaluate, Metadata, Review, Split |

### Renames (from existing)

| Old | New | Rationale |
|-----|-----|-----------|
| `task-execute` | `quiet-task` | Avoid conflict with Task tool |
| `task-plan` | `/plan-adhoc` | Skill-based, distinguishes from future `/plan-tdd` |

---

## Workflow Stages

### Stage 1: Initial Discussion (Sonnet)

Define job scope with user.

**Decision tree:**
- **Simple job** → Execute directly using CLAUDE.md orchestration patterns
- **Moderate complexity** → Produce implementation runbook immediately (Stage 3)
- **Complex/uncertain requirements** → Handoff to Opus design session (Stage 2)

**Complexity heuristics:**
- Moderate: Clear requirements, straightforward implementation choices
- Complex: Architectural decisions required OR user uncertainty about requirements

### Stage 2: Design Session (Opus) - Optional

Pick up from Stage 1 handoff.

**Activities:**
- Examine artifacts, explore local code, search web as needed
- Get user validation on design outline
- Create dense design document

**Design document requirements:**
- Motivation and scope
- Key architectural choices with rationale
- Design decisions with constraints considered
- Implementation phases (if complex)
- NO detailed implementation steps (sonnet does this in Stage 3)

**Goal:** Capture fuzzy human requirements and complex technical constraints. Once specified, sonnet can execute.

**Output:** Compact design doc targeting sonnet audience (minimize opus output tokens).

### Stage 3: Planning Session (Sonnet)

**Inputs:** User requirements (from Stage 1) OR design document (from Stage 2)

**Activities:**
1. Create implementation steps using 4-point runbook prep process
2. Get user validation on runbook outline
3. If design has multiple phases: plan each phase iteratively after previous execution
4. Delegate review to sonnet sub-agent with context + design doc + runbook
5. Apply review fixes
6. If simple enough for single step: offer immediate execution
7. Run `prepare-runbook.py` to create plan-specific agent + step files
8. Prime `session.md` for weak orchestrator handoff

**4-Point Runbook Prep Process:**
1. **Evaluate** - Script (≤25 lines) vs prose (25-100) vs separate planning (>100)
2. **Metadata** - Weak orchestrator coordination info
3. **Review** - Sonnet sub-agent validates completeness/executability
4. **Split** - Create per-step files for context isolation

### Stage 4: Execution (Weak Orchestrator)

Execute runbook steps using plan-specific agent.

**Orchestrator responsibilities:**
- Invoke plan-specific agent for each step
- Track progress
- Handle error escalation per runbook rules
- Report to specified locations

### Stage 5: Review (Sonnet)

New session with fresh context.

**Delegate review to sub-agent. Fix classification:**
- **Few/simple fixes** → Execute directly
- **Moderate fixes** → Delegate execution
- **Complex fixes** → Create fixes runbook (follow Stage 3 rules)

### Stage 6: Completion

- Update project documentation for changes
- Record architectural choices and design decisions
- Move relevant decisions OUTSIDE `plans/` to permanent project docs
- Delete plan-specific agent (no use beyond its runbook)

---

## Skills

### `/design`

**Purpose:** Opus design session
**Applicability:** Both oneshot and feature dev workflows
**Trigger:** Complex jobs, uncertain requirements

**Activities:**
- Artifact examination
- Code exploration
- Web search if needed
- Design outline validation
- Dense design document creation

### `/plan-adhoc`

**Purpose:** Sonnet planning session with runbook prep
**Contrast:** `/plan-tdd` (future, feature dev emphasis)

**Activities:**
- 4-point runbook prep process
- Review delegation
- Script invocation for artifact creation
- Session handoff priming

**Integration:** Invokes `prepare-runbook.py` in Point 4

### `/orchestrate`

**Purpose:** Execute runbook with weak agent
**Scope:** Prepared runbooks only (post `/plan-adhoc`)

**Content:**
- Common process handling
- Error escalation rules
- Progress tracking
- Report location management

### `/vet`

**Purpose:** Review in-progress changes
**Scope:** Uncommitted changes, recent commits, partial branch (any combination)
**Distinction:** Does NOT conflict with built-in `/review` (PR-focused)

**Activities:**
- Scope determination (ask user what to review)
- Change analysis
- Improvement suggestions
- Issue identification

---

## Script: `prepare-runbook.py`

### Location

`agent-core/bin/prepare-runbook.py`

**Rationale:** Reusable across projects, aligns with existing tooling location.

### Inputs

**Primary:** Runbook document with required sections

**Runbook format:**
```yaml
---
name: <runbook-name>
model: sonnet  # default model for steps
---
```

```markdown
## Common Context
[Shared knowledge for plan-specific agent]
- Architecture decisions
- File paths and conventions
- Constraints and requirements

## Step N: [Title]
[Individual step instructions]

## Orchestrator Instructions
[Sequencing, error handling, reporting]
```

### Outputs

1. **Plan-specific agent:** `.claude/agents/<runbook-name>-task.md`
   - Baseline from `quiet-task.md` + appended common context

2. **Step files:** `plans/<runbook-name>/steps/step-N.md`
   - Individual step instructions extracted

3. **Orchestrator plan:** `plans/<runbook-name>/orchestrator-plan.md`
   - Instructions for weak agent execution

### Composition Strategy

**Simple append with separator:**
```markdown
[Full quiet-task.md content]

---
# Runbook-Specific Context

[Common context section from runbook]
```

**Rationale:** Simple, maintainable, clear separation. Template variables add complexity for minimal benefit.

### Validation

**Must fail on:**
- Missing baseline agent (`agent-core/agents/quiet-task.md`)
- Missing required sections (Steps minimum)
- Duplicate step numbers
- Non-writable output directories

**Should warn (not fail):**
- Existing artifacts (overwriting is normal workflow)
- Missing optional sections (Common Context, Orchestrator)

### Defaults

- Common context: Empty = pure quiet-task baseline
- Orchestrator: Sequential execution, stop on error
- Model: Inherited from frontmatter or sonnet default

### Interface

```bash
prepare-runbook.py <runbook-file.md>
# Derives output paths from runbook location and name

prepare-runbook.py plans/foo/runbook.md
# Creates:
#   .claude/agents/foo-task.md
#   plans/foo/steps/step-*.md
#   plans/foo/orchestrator-plan.md
```

**Output:** List of created files, or error with clear message.

### Implementation

**Language:** Python 3, stdlib only (`re`, `pathlib`, `argparse`)

**No pip dependencies.** If YAML parsing needs grow, add `pyyaml` with SessionStart hook setup (plugin-compatible).

**Frontmatter parsing (stdlib):**
```python
def parse_frontmatter(content):
    if not content.startswith('---'):
        return {}, content
    end = content.index('---', 3)
    meta = {}
    for line in content[3:end].strip().split('\n'):
        key, _, value = line.partition(':')
        meta[key.strip()] = value.strip()
    return meta, content[end+3:].lstrip()
```

### Replaces

`agent-core/bin/create-plan-agent.sh` - either replace or have new script call it internally. Preference: replace (cleaner, single responsibility).

---

## Session Handoff (Stage 3 → Stage 4)

**Skill-driven, not scripted.**

`session.md` must contain:
- Reference to `context.md`
- Reference to design document (if exists)
- Reference to orchestrator plan
- Standard handoff sections (status, blockers, next actions)

---

## Change Management

**Plan changes mid-execution:**
- Re-run `prepare-runbook.py` (idempotent, overwrites)
- Git tracks changes to runbook and artifacts
- No artifact versioning (branches serve this purpose)

**Execution reveals errors:**
- Update runbook document
- Re-run script
- Resume execution from failed step

---

## Documentation Flow

**During execution:**
- Decisions recorded in `plans/<name>/decisions.md`

**After completion (Stage 6):**
- Integrate relevant decisions to project documentation
- Location: `agents/design-decisions.md` or project-specific
- Remove plan-specific agent
- Archive or delete plan directory per project convention

---

## Success Criteria

**Script:**
1. Transforms valid runbook → complete execution artifacts
2. Validates structure, fails clearly on errors
3. Idempotent (re-runnable)
4. Integrates with existing workflow

**Workflow:**
1. Clear stage boundaries
2. Appropriate model selection per stage
3. No orphaned steps (agent creation has clear home)
4. Repeatable, documented process

---

## Implementation Phases

### Phase 1: Script Implementation
- `prepare-runbook.py` with full validation
- Move/rename `task-execute.md` → `quiet-task.md` in agent-core
- Test with existing Phase 3 runbook

### Phase 2: Skill Creation
- `/design` skill
- `/plan-adhoc` skill (rename + extend `task-plan`)
- `/orchestrate` skill
- `/vet` skill

### Phase 3: Documentation
- Workflow documentation (skill-based, interconnected)
- Update CLAUDE.md terminology
- Update context.md with finalized patterns

### Phase 4: Cleanup
- Remove/archive `create-plan-agent.sh`
- Update existing runbooks to new format
- Terminology pass on existing docs

---

## References

**Existing artifacts:**
- `agents/auto-agent-discussion.md` - Original discussion document
- `.claude/skills/task-plan/skill.md` - Current 4-point process (becomes `/plan-adhoc`)
- `agent-core/agents/quiet-task.md` - Baseline task agent (formerly `task-execute.md`)
- `agent-core/bin/create-plan-agent.sh` - Existing script (to replace)

**Patterns:**
- Weak orchestrator pattern (`agents/context.md`)
- Quiet execution pattern (`CLAUDE.md`)
- Commit agent delegation (`CLAUDE.md`)
