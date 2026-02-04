# Skill Chaining Patterns Exploration

## Summary

This codebase implements skill chaining through **tail-call continuation**, a pattern where skills invoke other skills as their final action. Skill content is injected into conversations via the Claude Code Skill tool, and system prompts are constructed through baseline templates combined with runbook-specific context via `prepare-runbook.py`. The architecture supports both cooperative (first-party) skills and weak orchestrator patterns for delegation.

## Key Findings

### 1. Tail-Call Continuation Pattern

**Location:** `/Users/david/code/claudeutils/agent-core/skills/handoff/SKILL.md` (lines 213-223)

Skills chain via tail-calls, invoking the next skill as their final action:

```markdown
## Tail-Call: --commit Flag

**If `--commit` flag was provided:** As the **final action** of this skill, invoke `/commit` using the Skill tool.

This is a tail-call — handoff is complete, and `/commit` takes over. The commit skill will:
- Commit all staged/unstaged changes
- Display the next pending task from session.md

**Why tail-calls work:** Skills terminate when another skill is invoked. A tail-call (invoking a skill as the very last action) is safe because the current skill was done anyway. This enables skill composition without the mid-execution termination problem.
```

**Key insight:** Skills terminate when another skill is invoked, making tail-calls safe as a composition mechanism.

### 2. Real-World Chaining Examples

#### Design → Planning → Execution → Commit Chain

**Location:** `/Users/david/code/claudeutils/agent-core/skills/plan-adhoc/SKILL.md` (lines 688-694)

```markdown
**Workflow stages:**
1. `/design` - Opus creates design document
2. `/plan-adhoc` - Sonnet creates execution runbook (THIS SKILL) → auto-runs prepare-runbook.py → tail-calls `/handoff --commit`
3. `/handoff` updates session.md → tail-calls `/commit`
4. `/commit` commits everything → displays next pending task (restart instructions)
5. User restarts session, switches to haiku, pastes `/orchestrate {name}` from clipboard
6. `/orchestrate` - Haiku executes runbook steps
```

**Complete flow:**
- `/design` completes, returns
- Next skill invocation needed: `/plan-adhoc`
- `/plan-adhoc` runs `prepare-runbook.py`, then invokes `/handoff --commit`
- `/handoff` processes session.md, then invokes `/commit` (via Skill tool)
- `/commit` stages files, creates commit, displays STATUS showing next pending task

#### Tier 1 and Tier 2 Direct Implementation Pattern

**Location:** `/Users/david/code/claudeutils/agent-core/skills/plan-adhoc/SKILL.md` (lines 59-76)

```markdown
### Tier 1: Direct Implementation
1. Implement changes directly using Read/Write/Edit tools
2. Delegate to vet agent for review
3. Apply critical/major priority fixes from vet review
4. Tail-call `/handoff --commit`

### Tier 2: Lightweight Delegation
1. Delegate work via `Task(subagent_type="quiet-task", model="haiku", prompt="...")`
2. After delegation complete: delegate to vet agent for review
3. Apply critical/major priority fixes from vet review
4. Tail-call `/handoff --commit`
```

Both tiers terminate with the same tail-call to `/handoff --commit`, establishing a universal termination pattern.

### 3. Skill Invocation Mechanism

**Skill Tool Usage**

Skills invoke other skills using the Skill tool. In handoff skill (lines 215-216 of SKILL.md):

```markdown
**If `--commit` flag was provided:** As the **final action** of this skill, invoke `/commit` using the Skill tool.
```

And in design skill (lines 219-224):

```markdown
**CRITICAL: As the final action, invoke `/handoff --commit`.**

This tail-call chains:
1. `/handoff` updates session.md with completed design work
2. Tail-calls `/commit` which commits the design document
3. `/commit` displays STATUS showing next pending task
```

**Tool permission configuration:** `.claude/settings.json` (line 14)

```json
"permissions": {
    "allow": [
      "Bash(git:*)",
      "Bash(wc:*)",
      ...
      "Skill"
    ]
}
```

The Skill tool is explicitly allowed in permissions, enabling skill-to-skill invocation.

### 4. System Prompt Construction for Agents

**Baseline Template Pattern**

Sub-agents use baseline templates combined with runbook-specific context. Two models:

**quiet-task baseline:** `/Users/david/code/claudeutils/agent-core/agents/quiet-task.md`

- General execution agent (haiku model)
- Handles Read, Write, Edit, Bash, Grep, Glob tools
- Emphasizes quiet execution (reports to files, terse returns)
- Covers file operations, tool selection, git constraints, verification

**tdd-task baseline:** `/Users/david/code/claudeutils/agent-core/agents/tdd-task.md`

- TDD cycle execution agent (haiku model)
- Implements RED/GREEN/REFACTOR phase protocols
- Handles stop conditions and escalation
- Includes detailed phase sequencing and verification

#### prepare-runbook.py Context Injection

**Location:** `/Users/david/code/claudeutils/agent-core/bin/prepare-runbook.py` (lines 1-30)

The `prepare-runbook.py` script transforms runbooks into execution artifacts:

```
Transforms a runbook markdown file into:
1. Plan-specific agent (.claude/agents/<runbook-name>-task.md)
2. Step/Cycle files (plans/<runbook-name>/steps/)
3. Orchestrator plan (plans/<runbook-name>/orchestrator-plan.md)

Supports:
- General runbooks (## Step N:)
- TDD runbooks (## Cycle X.Y:, requires type: tdd in frontmatter)
```

**System prompt construction pattern:**
1. Read baseline template (quiet-task.md or tdd-task.md)
2. Extract Common Context section from runbook
3. Prepend Common Context to baseline
4. Create plan-specific agent at `.claude/agents/<runbook-name>-task.md`
5. Each step file receives its own Execution Model metadata header

### 5. Orchestrator Pattern for Weak Execution

**Location:** `/Users/david/code/claudeutils/agent-core/skills/orchestrate/SKILL.md`

The orchestrate skill implements weak orchestrator pattern:

```markdown
## Execution Process

### 3. Execute Steps Sequentially

**For each step in order:**

**3.1 Invoke plan-specific agent with step file:**

Use Task tool with:
- subagent_type: "<runbook-name>-task"
- prompt: "Execute step from: plans/<runbook-name>/steps/step-N.md"
- description: "Execute step N of runbook"
- model: [from step file header "Execution Model" field]

**CRITICAL — Model selection:** The orchestrator itself may run on haiku, but step agents use the model specified in each step file's **header metadata**.
```

**Key pattern:** Orchestrator delegatesvia Task tool to plan-specific agents created by prepare-runbook.py. Each step specifies its own model via metadata header.

### 6. Sub-Agent Context Injection

**Task Tool Delegation Pattern**

**Location:** `/Users/david/code/claudeutils/agent-core/skills/plan-adhoc/SKILL.md` (line 73)

```markdown
Delegate work via `Task(subagent_type="quiet-task", model="haiku", prompt="...")` with relevant context from design included in prompt (file paths, design decisions, conventions).
```

**Process:**
1. Caller selects subagent_type (e.g., "quiet-task", "vet-agent", "design-vet-agent")
2. Claude Code runtime loads agent definition from `.claude/agents/<subagent_type>.md`
3. Agent definition (YAML frontmatter) + prompt are combined into system prompt for sub-agent
4. Sub-agent executes in isolated session, returns result

**Sub-agent isolation:** No continuation directives leak into sub-agent system prompts (this is a design requirement in continuation-passing, FR-6).

### 7. Hook-Based Context Injection

**UserPromptSubmit Hook for Shortcuts**

**Location:** `/Users/david/code/claudeutils/agent-core/hooks/userpromptsubmit-shortcuts.py`

Hooks intercept user prompts and inject context:

```python
# Tier 1: Command shortcuts (exact match)
COMMANDS = {
    's': '[SHORTCUT: #status] List pending tasks with metadata from session.md...',
    'x': '[SHORTCUT: #execute] Smart execute: if an in-progress task exists...',
    'xc': '[SHORTCUT: #execute --commit] Execute task to completion, then handoff → commit...',
    # ... more commands
}

# Tier 2: Directive shortcuts (colon prefix)
DIRECTIVES = {
    'd': '[DIRECTIVE: DISCUSS] Discussion mode. Analyze and discuss only...',
    'p': '[DIRECTIVE: PENDING] Record pending task. Append to session.md...',
}
```

**Output pattern (lines 74-82):**

```python
output = {
    'hookSpecificOutput': {
        'hookEventName': 'UserPromptSubmit',
        'additionalContext': expansion
    },
    'systemMessage': expansion
}
print(json.dumps(output))
```

**Mechanism:**
1. Hook fires on every user prompt (UserPromptSubmit event)
2. Checks for exact command match (Tier 1) or colon directive (Tier 2)
3. Outputs dual context: `additionalContext` (injected, not shown) + `systemMessage` (visible)
4. No matcher support (UserPromptSubmit doesn't support matcher field) — all filtering script-internal

### 8. Skill Content Loading Mechanism

**Location:** `.claude/settings.json` (line 14)

Skill tool is explicitly permitted:

```json
"permissions": {
    "allow": [
      ...
      "Skill"
    ]
}
```

**How skills are loaded:**
1. User invokes skill via `/skillname` (slash prefix)
2. Claude Code plugin discovers skill file from `.claude/skills/` or symlinked locations
3. Skill frontmatter (YAML) provides metadata: name, description, allowed-tools, user-invocable flag
4. Skill content (markdown body) is injected into conversation as context
5. Skill tool is available in the skill's allowed-tools list

**Symlink pattern:** Skills symlinked from `agent-core/skills/` to `.claude/skills/`:

```bash
# Created by: just sync-to-parent (in agent-core directory)
# Pattern: ln -sf ../../agent-core/skills/skillname .claude/skills/skillname
```

### 9. Continuation Passing Design (Planned)

**Location:** `/Users/david/code/claudeutils/plans/continuation-passing/requirements.md`

Current design outlines three cooperation levels for skill chaining:

```markdown
## Cooperation Levels

| Level | Mechanism | Skills |
|-------|-----------|--------|
| Cooperative | Skill reads continuation, invokes next | First-party |
| Wrapped | Payload explains continuation to unaware skill | Second/third-party |
| Explicit | User manually invokes next skill | Fallback |
```

**Proposed parsing model:**

```
/skill context, /next and /final
       ↓
Skill: "skill"
Context: "context"
Continuation: "/next and /final"

After `/skill` completes:
/next and /final
     ↓
Skill: "next"
Context: (none)
Continuation: "/final"
```

**Key FR (FR-5):** Prose-to-explicit translation — pure prose in user input translates to explicit `/skill` references when calling next skill.

### 10. Skill Chaining at Different Tiers

#### Full Runbook (Tier 3) Chaining

**Location:** `/Users/david/code/claudeutils/agent-core/skills/plan-tdd/SKILL.md` (lines 45-56)

TDD workflow chaining:

```markdown
**Workflow Integration**

/design (TDD mode) → /plan-tdd → [tdd-plan-reviewer] → [apply fixes] → prepare-runbook.py → /orchestrate

**CRITICAL:** After runbook generation and review:
1. If violations found: Apply fixes to runbook
2. prepare-runbook.py runs **automatically** (Phase 5 step 5) — no manual invocation needed
3. Skill auto-commits, hands off, and copies `/orchestrate {name}` to clipboard
```

#### Error Escalation Chaining

**Location:** `/Users/david/code/claudeutils/agent-core/skills/orchestrate/SKILL.md` (lines 152-193)

Orchestrator escalates via Task tool delegation:

```markdown
**Escalation levels (from orchestrator metadata):**

**Level 1: Haiku → Sonnet (Refactor Agent)**
- Triggers: Quality check warnings from TDD cycles
- Action: Delegate to refactor agent (sonnet) for evaluation and execution
- If refactor agent fixes: Resume execution
- If refactor agent escalates: Route to opus or user as appropriate

**Level 2: Sonnet → User**
- Triggers: Design decisions needed, architectural changes required
- Action: Stop execution, provide detailed context to user
```

### 11. Session Handoff Mechanism

**Handoff Token Expansion**

**Location:** `/Users/david/code/claudeutils/agent-core/skills/handoff/SKILL.md` (lines 37-39)

```markdown
**Pending task tokens:** When adding new pending tasks, use `#PNDNG` as a placeholder token. The commit skill replaces these with unique identifiers before committing. This enables `task-context.sh` to find the session.md where a task was introduced.

**Format:** `- [ ] **Task name** #PNDNG — description | model`
```

**Precommit validation** in justfile runs `agent-core/bin/validate-tasks.py` which:
1. Expands `#PNDNG` tokens to unique identifiers
2. Validates task uniqueness across session.md, learning keys, and git history
3. Prevents duplicate task names

## Patterns

### Universal Tail-Call Termination

All skill tiers and types terminate with `/handoff --commit`:

| Skill Path | Tier | Termination |
|------------|------|-------------|
| `/design` | Complex | `invoke /handoff --commit` |
| `/plan-adhoc` Tier 1 | Direct Implementation | `tail-call /handoff --commit` |
| `/plan-adhoc` Tier 2 | Lightweight Delegation | `tail-call /handoff --commit` |
| `/plan-adhoc` Tier 3 | Full Runbook | Auto → `tail-call /handoff --commit` |
| `/plan-tdd` | Any | Auto → `tail-call /handoff --commit` |

**Benefits:**
- Consistent workflow exit: handoff → commit → STATUS
- Session.md always updated before commit
- Next pending task displayed automatically
- STATUS serves as entry point for next session

### Context Injection Layers

Three layered approaches to context injection:

| Layer | Mechanism | Use Case |
|-------|-----------|----------|
| Ambient (CLAUDE.md) | Pre-loaded in every session | Core workflows, fundamental rules |
| Hook-based (UserPromptSubmit) | Intercept user input, inject context | Workflow shortcuts (s, x, xc, h, hc, ci) |
| Explicit (Skill frontmatter) | Skill content injected when invoked | Detailed guidance, skill-specific protocols |

### Sub-Agent Model Selection

Weak orchestrator uses step-specific models via metadata:

```markdown
# Example step-1.md header
---
Execution Model: sonnet
Title: Complex algorithmic refactoring
---

## Step 1: Refactor widget factory
[body...]
```

**Pattern:** Each step declares its required model in frontmatter. Orchestrator reads the model and passes it to Task tool. Sub-agent system prompt includes baseline template + inherited context.

### Cooperative Skill Discovery

Skills that participate in tail-calls are "cooperative" — they understand the pattern:

**Current cooperative skills:**
- `/design` → hands off to `/plan-adhoc` or `/plan-tdd`
- `/plan-adhoc` → hands off to `/handoff --commit`
- `/plan-tdd` → auto-runs prepare-runbook.py → hands off to `/handoff --commit`
- `/handoff` (with --commit flag) → tail-calls `/commit`
- `/commit` → displays STATUS (no further tail-call)

Non-cooperative skills (external, third-party) would require "Wrapped" protocol from continuation-passing design (FR-8).

## Gaps

1. **Explicit continuation parsing not yet implemented** — Current system relies on manual skill invocation. Proposed continuation-passing design (prose syntax like `/design, /plan-adhoc and /orchestrate`) not yet active.

2. **Sub-agent isolation for continuation** — If continuation-passing is implemented, ensure FR-6 is satisfied: continuation directives must not leak into sub-agent system prompts when skills spawn agents via Task tool.

3. **Mid-chain error recovery** — Current architecture stops on error and requires user intervention. No mechanism for automatic error recovery or alternative branching mid-chain.

4. **Bidirectional context flow** — Context flows from caller to called skill (via prompt in Task tool or skill invocation). No mechanism for called skill to return structured data back to caller beyond text output.

5. **Third-party skill wrapping** — "Wrapped" cooperation level (FR-8) for non-cooperative skills not yet implemented.

6. **Continuation across session boundaries** — Tail-calls work within single session. Multi-session continuation requires session handoff + clipboard copy (manual). No persistent continuation state across restarts.

## Code Examples

### Example 1: Full Tail-Call Chain in Design Skill

**File:** `/Users/david/code/claudeutils/agent-core/skills/design/SKILL.md` (lines 217-227)

```markdown
#### C.5. Handoff and Commit

**CRITICAL: As the final action, invoke `/handoff --commit`.**

This tail-call chains:
1. `/handoff` updates session.md with completed design work
2. Tail-calls `/commit` which commits the design document
3. `/commit` displays STATUS showing next pending task

The next pending task will typically be the planning phase (`/plan-adhoc` or `/plan-tdd`).

**Why:** Universal tail behavior ensures consistent workflow termination. User always sees what's next.
```

### Example 2: Task Delegation with Context Injection

**File:** `/Users/david/code/claudeutils/agent-core/skills/orchestrate/SKILL.md` (lines 66-79)

```markdown
**3.1 Invoke plan-specific agent with step file:**

Use Task tool with:
- subagent_type: "<runbook-name>-task"
- prompt: "Execute step from: plans/<runbook-name>/steps/step-N.md

CRITICAL: For session handoffs, use /handoff-haiku, NOT /handoff."
- description: "Execute step N of runbook"
- model: [from step file header "Execution Model" field]
```

### Example 3: Hook-Based Context Injection

**File:** `/Users/david/code/claudeutils/agent-core/hooks/userpromptsubmit-shortcuts.py` (lines 18-46)

```python
COMMANDS = {
    's': (
        '[SHORTCUT: #status] List pending tasks with metadata from session.md. '
        'Display in STATUS format. Wait for instruction.'
    ),
    'x': (
        '[SHORTCUT: #execute] Smart execute: if an in-progress task exists, '
        'resume it. Otherwise start the first pending task from session.md. '
        'Complete the task, then stop. Do NOT commit or handoff.'
    ),
    'xc': (
        '[SHORTCUT: #execute --commit] Execute task to completion, '
        'then handoff → commit → status display.'
    ),
    # ... more commands
}
```

### Example 4: Runbook Tier Structure in Plan-Adhoc

**File:** `/Users/david/code/claudeutils/agent-core/skills/plan-adhoc/SKILL.md` (lines 49-112)

```markdown
### Tier 1: Direct Implementation

**Criteria:**
- Design complete (no open decisions)
- All edits straightforward (<100 lines each)
- Total scope: <6 files
- Single session, single model
- No parallelization benefit

**Sequence:**
1. Implement changes directly using Read/Write/Edit tools
2. Delegate to vet agent for review
3. Apply critical/major priority fixes from vet review
4. Tail-call `/handoff --commit`
```

## Technical Insights

### Why Tail-Calls Work

Skills terminate when another skill is invoked. This makes tail-calls safe for skill composition:
- Current skill completes its work (done anyway)
- As final action, invokes next skill
- System terminates current skill, loads next skill
- No mid-execution interruption problem
- Seamless continuation for user

### Model Switching Mechanism

The weak orchestrator pattern enables safe model switching:
1. **Design phase (Opus):** Complex architectural decisions
2. **Planning phase (Sonnet):** Detailed runbook creation
3. **Execution phase (Haiku):** Mechanical step execution
4. **Checkpoints (Sonnet):** Quality review of accumulated changes
5. **Final review (Sonnet/Opus):** Vet changes before commit

Each phase explicitly declares its model via:
- Skill frontmatter metadata (`model: sonnet`)
- Step file headers (`Execution Model: haiku`)
- Task tool invocation (`model="opus"`)

### Context Preservation Across Handoffs

Session.md acts as context persistence layer:
1. Each skill updates session.md before handing off
2. Next agent/session reads session.md from CLAUDE.md
3. Context preserved across model switches and restarts
4. No context loss on tail-calls
5. Learnings accumulated in separate learnings.md

## Recommendations for Continuation-Passing Design

1. **Implement explicit continuation parsing** based on requirements.md FR-1 through FR-5
2. **Add continuation-aware mode to skill protocol** — skills optionally read remaining continuation and invoke next
3. **Implement sub-agent isolation** (FR-6) — strip continuation section when building sub-agent system prompt
4. **Add error recovery branching** — allow skills to specify alternative continuations on failure
5. **Create continuation registry** — maintain list of cooperative skills for auto-detection
6. **Test multi-session continuations** — verify continuation survives session restart + clipboard copy
