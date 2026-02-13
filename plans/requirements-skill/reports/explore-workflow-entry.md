# Workflow Entry Points Exploration

## Summary

Requirements enter the system primarily through conversational user input followed by `/design` skill invocation. The `/design` skill gates complexity assessment (simple/moderate/complex) and either executes directly, routes to planning, or initiates full design work. Current system has no dedicated `/requirements` skill; requirements are captured during design Phase A.0 via `requirements.md` file discovery or documented inline during exploration. User workflow is indirect: user describes job → agent decides route → appropriate workflow executes.

---

## Key Findings

### 1. Workflow Entry Point Routing

**Absolute file path:** `/Users/david/code/claudeutils-wt/requirements-skill/agent-core/fragments/workflows-terminology.md`

**Entry point rules (lines 3-6):**
- Questions/research/discussion → Handle directly (no workflow)
- Implementation tasks → Use `/design` skill (complexity-aware routing)
- Workflow in progress → Continue from current state (check session.md)

**Design skill gates complexity triage (Phase 0):**
- Simple (no design needed) → Execute directly, update session.md
- Moderate (planning needed, not design) → Skip design, route to `/runbook`
- Complex (design needed) → Proceed with Phases A-C

**Design skill file:** `/Users/david/code/claudeutils-wt/requirements-skill/agent-core/skills/design/SKILL.md`

**Key routing logic (lines 19-34):**
```
Simple: Single file, obvious implementation, no architectural decisions
Moderate: Clear requirements, no architectural uncertainty, well-defined scope
Complex: Architectural decisions, multiple valid approaches, uncertain requirements
```

### 2. Requirements Checkpoint (Phase A.0)

**Critical design entry point for structured requirements:**

**Location:** `/Users/david/code/claudeutils-wt/requirements-skill/agent-core/skills/design/SKILL.md` lines 43-67

**Phase A.0 execution rules:**

1. **If `requirements.md` exists** in job directory (`plans/<job-name>/requirements.md`):
   - Read and summarize functional/non-functional requirements
   - Note scope boundaries (in/out of scope)
   - Carry requirements context into outline and design
   - Scan for skill dependencies (agents, skills, hooks, plugins) → load immediately

2. **If no `requirements.md` exists:**
   - Document requirements discovered during research
   - Can be inline in design.md or separate requirements.md (designer judgment)

**Skill dependency scanning (lines 55-59):**
- "sub-agent", "delegate to agent" → Load `plugin-dev:agent-development`
- "skill", "invoke skill" → Load `plugin-dev:skill-development`
- "hook", "PreToolUse" → Load `plugin-dev:hook-development`
- "plugin", "MCP server" → Load `plugin-dev:plugin-structure`, `plugin-dev:mcp-integration`

**Anti-pattern called out (lines 61-65):** Deferring skill loading to Phase A.1 when requirements explicitly mention feature dependencies. Correct pattern: Scan during A.0, load immediately.

### 3. Requirements Artifact Patterns

**Existing requirements.md files:**
- `/Users/david/code/claudeutils-wt/requirements-skill/plans/handoff-validation/requirements.md`
- `/Users/david/code/claudeutils-wt/requirements-skill/plans/orchestrate-evolution/requirements.md`
- `/Users/david/code/claudeutils-wt/requirements-skill/plans/requirements-skill/requirements.md`
- `/Users/david/code/claudeutils-wt/requirements-skill/plans/tweakcc/requirements.md`

**Alternative: problem.md files:**
- `/Users/david/code/claudeutils-wt/requirements-skill/plans/continuation-prepend/problem.md`
- `/Users/david/code/claudeutils-wt/requirements-skill/plans/parallel-orchestration/problem.md`

**Format variance observed:**

From `/Users/david/code/claudeutils-wt/requirements-skill/plans/requirements-skill/requirements.md`:
```markdown
## Functional Requirements
FR-1: [Requirement]

## Non-Functional Requirements
NFR-1: [Requirement]

## Open Questions (Research Needed)
Q-1: [Question]
```

From `/Users/david/code/claudeutils-wt/requirements-skill/plans/orchestrate-evolution/requirements.md`:
```markdown
## Requirements
[Brief statement]

## Open Questions
[List of questions]
```

From `/Users/david/code/claudeutils-wt/requirements-skill/plans/continuation-prepend/problem.md`:
```markdown
## Problem
[Problem statement]

## Mechanism
[How it should work]
```

### 4. Task Metadata Format

**Session.md task entry pattern:**

From `/Users/david/code/claudeutils-wt/requirements-skill/agents/session.md`:
```markdown
- [ ] **Task Name** — `command` | model | restart?
  - Plan: <plan-directory> | Status: <status>
  - Command: `/design plans/<plan-name>/`
```

**Metadata fields:**
- Task Name: Prose identifier (unique across session)
- Command: Backtick-wrapped entry command
- Model: `haiku`, `sonnet`, or `opus` (default: sonnet)
- Restart: Optional flag (omit if not needed)
- Plan directory: For tracking association
- Status: From `agents/jobs.md` tracking

### 5. No Current `/requirements` Skill

**Planned but not implemented:**

From `/Users/david/code/claudeutils-wt/requirements-skill/plans/requirements-skill/requirements.md`:
```
## Recommendation
Defer implementation until design/plan skill requirements sections are working.
Evaluate whether separate /requirements skill provides value beyond in-skill
requirements capture.
```

**Open design question (from requirements.md):**
```
Q-1: Scope overlap
Design skill Phase A does exploration + outline. Plan skills do context
collection. How does /requirements differ?

Q-2: Context collection depth
- Minimal: Just user requirements, no codebase exploration
- Medium: Requirements + relevant file discovery
- Full: Requirements + exploration + doc search (duplicates design)

Q-3: Artifact format
- Inline in conversation?
- Separate requirements.md file?
- YAML frontmatter in design.md?

Q-4: When to use
- Before any implementation work?
- Only for complex/unclear requirements?
- As alternative to design for moderate tasks?
```

### 6. Shelve Skill for Context Management

**Location:** `/Users/david/code/claudeutils-wt/requirements-skill/agent-core/skills/shelve/SKILL.md`

**Purpose (lines 1-9):** Archive session context and reset for new work when switching to unrelated work.

**Workflow (lines 40-68):**
1. Read current `agents/session.md`
2. Create `agents/shelf/` directory
3. Archive to `agents/shelf/<name>-session.md` with metadata header
4. Prepend to `agents/todo.md` with reference
5. Reset session.md to template (line 74): `cp .claude/skills/shelve/templates/session.md agents/session.md`

**Key pattern:** Preserves abandoned session context without blocking new work. Enables session recovery via `git log -S` or restoration from shelf.

### 7. Documentation Checkpoint (Phase A.1)

**Structured documentation loading pattern:**

From `/Users/david/code/claudeutils-wt/requirements-skill/agent-core/skills/design/SKILL.md` lines 69-90

**Hierarchy (levels are fallback when previous didn't answer):**

| Level | Source | Method | When |
|-------|--------|--------|------|
| 1. Local knowledge | `memory-index.md`, `agents/decisions/*.md` | Read directly or quiet-explore | Always (core) |
| 2. Key skills | plugin-dev:* skills | Skill invocation | When design touches plugins |
| 3. Context7 | External library docs via MCP | Direct MCP calls | When external lib needed |
| 4. Local explore | Codebase exploration | Delegate to quiet-explore agent | Always for complex |
| 5. Web research | External patterns, specifications | WebSearch/WebFetch | When local insufficient |

**Flexibility note (lines 85-90):** Level 1 always loaded. Levels 2-5 conditional on task domain. Designer identifies domain and loads relevant docs — no fixed "always read X" list beyond level 1 core.

### 8. Continuation Passing Integration

**Location:** `/Users/david/code/claudeutils-wt/requirements-skill/agent-core/skills/orchestrate/SKILL.md` lines 5-7

**Orchestrate default exit chain:**
```yaml
continuation:
  cooperative: true
  default-exit: ["/handoff --commit", "/commit"]
```

**Protocol pattern:** Skills cooperatively chain work via continuation. `/orchestrate` preserves `/handoff --commit` + `/commit` tail behavior regardless of phase boundaries.

---

## Patterns Across System

### Entry Point Decision Tree

1. **User submits work description** (natural language in conversation)
2. **Agent queries:** Is this a question, research request, or implementation task?
   - Question/research → Answer directly
   - Implementation → Proceed to next level
3. **Agent invokes `/design`** with `plans/<job-name>/` directory
4. **Design Phase 0 gates complexity:**
   - Simple → Execute directly, update session.md with result
   - Moderate → Skip design, route to `/runbook` directly
   - Complex → Proceed with Phases A-C (research, outline, review, design)
5. **Design Phase A.0 gates requirements:**
   - Check `plans/<job-name>/requirements.md` if exists
   - If found: Summarize + scan for skill dependencies
   - If not: Document from exploration + create if needed
6. **Design creates artifacts** in `plans/<job-name>/`:
   - `outline.md` (Phase A.5)
   - `design.md` (Phase C.1)
   - `reports/explore-*.md` (Phase A.2-4, from quiet-explore agent)
   - `reports/design-review.md` (Phase C.3)
7. **Tail-call chain** via `/handoff --commit` → `/commit`
   - Updates session.md
   - Commits design artifacts
   - Displays next pending task (typically `/runbook`)

### Context Transmission Patterns

**Session.md metadata format:**
- Task name as lookup key for git history recovery
- Command entry point (e.g., `/design plans/<name>/`)
- Model tier hint (haiku/sonnet/opus)
- Plan directory association for artifact discovery

**Design-to-Planner Context:**
- `plans/<job>/design.md` contains binding constraints (classification tables, scope)
- `plans/<job>/requirements.md` (if exists) specifies functional/non-functional/out-of-scope
- `plans/<job>/outline.md` (if generated) validates approach before design
- "Documentation Perimeter" section in design specifies what planner must read

**Planner-to-Orchestrator Context:**
- `plans/<job>/runbook.md` main execution spec (created by `/runbook`)
- `plans/<job>/steps/step-*.md` individual execution units (from `prepare-runbook.py`)
- `.claude/agents/<job>-task.md` plan-specific agent definition (from `prepare-runbook.py`)
- `plans/<job>/orchestrator-plan.md` execution sequencing and error rules (from `prepare-runbook.py`)

### No Direct User Input Capture

**Current system characteristic:** No dedicated phase captures user-provided requirements in structured form. Options exist:
1. **Requirements.md approach:** Designer creates after Phase A exploration
2. **Inline approach:** Designer documents findings during Phase A, inline in design.md
3. **Problem.md approach:** Used for some plans (continuation-prepend, parallel-orchestration)

**Gap in current system:** No explicit "gather requirements from user" step. Requirements discovered during design Phase A exploration, not collected beforehand. Reverse of typical software engineering (where requirements precede design).

---

## Gaps and Unresolved Questions

### 1. Pre-Design Requirements Gathering

**Current state:** No skill captures "what does user want?" before `/design`.
**Gap:** If user doesn't know how to describe their job, no structured elicitation happens.
**Unresolved:** Should `/requirements` skill exist as pre-design step? Design skill Phase A.0 suggests requirements might already exist as file.

### 2. Requirements vs Problem Artifact Naming

**Observed variance:** Some plans use `problem.md`, others use `requirements.md`.
**No convention:** No documented rule for when to create which file.
**Unresolved:** Should system standardize on single artifact name?

### 3. Skill Dependency Detection Timing

**Current rule:** Scan requirements during A.0 for agent/skill/hook mentions → load immediately.
**Unresolved:** What if user mentions feature that requires skill but doesn't explicitly say "skill"?
**Example:** "I need to create a sub-agent for this" vs "I need to create an agent" — are these detected equally?

### 4. When to Use `/shelve` Before `/design`

**Design skill line 35:** "If session has significant pending work (>5 tasks), suggest `/shelve`."
**Unresolved:** Exact condition? What defines "significant"? How does agent measure?

### 5. Requirements Artifact Format Standardization

**Observed formats:**
- YAML with Functional/Non-Functional sections
- Simple markdown with brief statements
- problem.md with Problem/Mechanism sections
**Unresolved:** Should Phase A.0 enforce format? Or accept any structured format?

### 6. Documentation Perimeter Scope

**Pattern established:** Design specifies "what planner must read" in Documentation Perimeter section.
**Unresolved:** Does this mean planner is blocked until those docs exist? Or is it a "nice to have"?
**Execution consequence:** If planner can't find a documented file, does orchestrate fail?

---

## Artifacts and Integration Points

### Absolute Paths (Execution Context)

**Skills (entry points):**
- Design: `/Users/david/code/claudeutils-wt/requirements-skill/agent-core/skills/design/SKILL.md`
- Runbook: `/Users/david/code/claudeutils-wt/requirements-skill/agent-core/skills/runbook/SKILL.md`
- Orchestrate: `/Users/david/code/claudeutils-wt/requirements-skill/agent-core/skills/orchestrate/SKILL.md`
- Shelve: `/Users/david/code/claudeutils-wt/requirements-skill/agent-core/skills/shelve/SKILL.md`

**Documentation:**
- Workflow terminology: `/Users/david/code/claudeutils-wt/requirements-skill/agent-core/fragments/workflows-terminology.md`
- Session tracking: `/Users/david/code/claudeutils-wt/requirements-skill/agents/session.md`
- Job tracking: `/Users/david/code/claudeutils-wt/requirements-skill/agents/jobs.md`

**Example plan structures:**
- Requirements file: `/Users/david/code/claudeutils-wt/requirements-skill/plans/requirements-skill/requirements.md`
- Problem file: `/Users/david/code/claudeutils-wt/requirements-skill/plans/continuation-prepend/problem.md`
- Output directory: `/Users/david/code/claudeutils-wt/requirements-skill/plans/requirements-skill/reports/` (for exploration outputs)

---

## Workflow Entry Summary

**User provides:** Natural language job description in conversation

**System responds with:**
1. `/design plans/<job-name>/` invocation (creates directory if needed)
2. Design skill runs complexity triage (Phase 0)
3. Based on complexity:
   - Simple → Execute directly
   - Moderate → Route to `/runbook`
   - Complex → Proceed with design phases

**Design Phase A.0 specifically checks:**
- Does `plans/<job-name>/requirements.md` exist?
- If yes: Carry forward as requirements context
- If no: Document requirements discovered during exploration

**Output flow:**
- Design produces `plans/<job-name>/design.md`
- Tail-calls `/handoff --commit` → `/commit`
- Updates session.md with next step (typically `/runbook plans/<job-name>/design.md`)

**Current system characteristic:** Requirements are discovered reactively during design exploration, not collected proactively before design. No dedicated `/requirements` skill exists. Plan is to evaluate this gap after design/plan skill requirements sections mature.
