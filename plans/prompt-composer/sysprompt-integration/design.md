# System Prompt Pattern Integration: Design

**Goal**: Extract and integrate relevant patterns from Claude Code's system prompt into
our module system, enabling agents with overridden system prompts to retain beneficial
behaviors.

- **Implementation**: See `tasks-opus.md` and `tasks-delegable.md`.
- **Draft Content**: See `drafts.md` for preliminary module content.

---

## Problem

When using Claude Code with a custom/overridden system prompt (via `--system-prompt` or
orchestration), agents lose access to Claude Code's built-in behavioral patterns:

- Tool usage best practices (batching, specialized tools over bash)
- Communication patterns (emoji, conciseness, professional objectivity)
- Safety patterns (OWASP, over-engineering avoidance)
- Progress tracking (TodoWrite usage patterns)

## Solution

Extract patterns from Claude Code's system prompt into our modular system, categorized
by:

1. **Tool-conditional modules** (`.tool.md`) - included when specific tools are enabled
2. **Core modules** (`.semantic.md`) - patterns that apply to all/most roles
3. **Role-specific modules** - patterns that apply to specific role types

---

## Source Material

- Claude Code system prompt v2.0.75 (from `claude-code-system-prompts` repository)
- Task agent prompt (agent-prompt-task-tool.md) for scope comparison
- Reference extraction in `agents/modules/src/sysprompt-reference/` (13 files)

### System Tool Descriptions

**Architecture:** Tool descriptions are NOT part of the system prompt. They're included
in the tool description message whenever that tool is enabled. Source files:

```
claude-code-system-prompts/system-prompts/tool-description-*.md
```

**Implications:**

- System prompt size is more manageable than initially estimated
- Tool descriptions add context overhead per-enabled-tool
- A command-based MCP could provide shell execution without Bash tool's full description
  overhead (see ROADMAP.md)
- System tools don't offer another shell escape hatch - likely intentional for
  sandboxing

**Key considerations:**

- **Not all tools in plain Claude Code**: Computer, ReadFile are IDE/extension-only.
- **Dynamic injection**: `tool-description-task-async-return-note.md` is NOT in initial
  prompt (injected later).
- **Large tool descriptions**: See "Tool Description Size Analysis" below.

**Budgeting implications:**

Role budgets must account for both scenarios:

1. **Fine-tuned sessions** (wrapper/agent files): Relevant tools only, minimal tool
   description overhead.
2. **Default interactive sessions**: All system tools enabled, full tool description
   load.

#### Tool Description Size Analysis

| Tool            | Lines | Key Content                                  |
| --------------- | ----- | -------------------------------------------- |
| todowrite       | 189   | When to use, when NOT, 8 examples, states    |
| bash-git-commit | 95    | Safety protocol (8 rules), commit/PR flows   |
| enterplanmode   | 92    | When to use, when NOT, examples              |
| task            | 78    | Agent types, usage notes, examples           |
| bash            | 65    | Specialized tools preference, command chains |
| Smaller tools   | 6-22  | glob, edit, write, askuser, etc.             |
| **Total**       | ~966  |                                              |

**bash-git-commit detail** (25+ instructions):

- Git Safety Protocol (8 rules): never update config, never destructive commands, amend
  conditions (3 sub-conditions), never skip hooks
- Commit Workflow (4 numbered steps with sub-bullets)
- PR Workflow (3 numbered steps with HEREDOC examples)
- Important Notes (5 additional constraints)

Justifies separating bash.tool.md (file I/O preferences) from bash-git.tool.md
(commit/PR).

### Related Plans

- `plans/prompt-composer/design.md` - Overall module system architecture
- `plans/prompt-composer/plan-outline.md` - Module system implementation phases

---

## Reference Files Created

Created `agents/modules/src/sysprompt-reference/` with 13 reference files:

| File                                    | Content                                | Integration Target      |
| --------------------------------------- | -------------------------------------- | ----------------------- |
| `identity.sysprompt.md`                 | CLI context, output format             | Core                    |
| `security.sysprompt.md`                 | URL restrictions, OWASP                | Code roles              |
| `professional-objectivity.sysprompt.md` | Technical accuracy                     | Conversational roles    |
| `planning-no-timelines.sysprompt.md`    | No time estimates                      | Planning roles          |
| `todowrite.sysprompt.md`                | Task tracking with examples            | todowrite.tool.md       |
| `askuser.sysprompt.md`                  | Question framing                       | askuser.tool.md         |
| `user-hooks.sysprompt.md`               | Hook handling                          | Skip (interactive-only) |
| `doing-tasks.sysprompt.md`              | Over-engineering, read-before-modify   | Code roles              |
| `system-reminders.sysprompt.md`         | System reminder handling               | Core                    |
| `tool-policy.sysprompt.md`              | Parallel/sequential, specialized tools | Tool modules            |
| `tone-style.sysprompt.md`               | Emoji, conciseness                     | Core                    |
| `help-feedback.sysprompt.md`            | Help commands                          | Interactive-only (skip) |
| `documentation-lookup.sysprompt.md`     | Self-documentation                     | Interactive-only (skip) |

See `CATALOG.md` in that directory for scope analysis and integration notes.

---

## Key Decisions

1. **Separate directory** (`tools/`) - cleaner than embedding in existing modules
2. **`.tool.md` suffix** - distinguishes from always-included `.semantic.md`
3. **`requires_tools` frontmatter** - declarative, composer handles matching
4. **No variable interpolation** - tool names are stable, keep it simple
5. **Single variant per tool module** - start simple, add tier variants if needed
6. **No markdown title before frontmatter** - frontmatter must be first (YAML spec)
7. **Bash consolidation** - all "prefer specialized tools" rules in bash.tool.md

---

## Design Questions Resolved

### Q1: read-edit.tool.md - bash-related instructions

**A**: read-edit.tool.md MUST NOT require Bash. It contains file I/O instructions that
apply whenever Read/Edit/Write are available. The "prefer over Bash" rules should
either:

- Move to bash.tool.md (consolidate all bash-related guidance there), OR
- Use conditional sections within read-edit.tool.md

**Decision**: Consolidate "prefer Read/Edit/Write over Bash" into bash.tool.md since:

- No reasonable use case for Bash without Read/Edit/Write
- Simpler to have all bash-related guidance in one place
- read-edit.tool.md focuses on file operation mechanics (batching, sequencing)

### Q2: read-edit.tool.md - "refresh after write"

**A**: **REVISED interpretation**. Original intent was to save a tool call for the
following edit-execute batch at minimal context cost (old reads discarded). The rule:

- Edits in same batch should NOT have downstream dependencies at all
- Refresh is for the next batch (edit→test cycle), not within-batch
- Move to Preferred tier and clarify: "refresh before next batch that depends on writes"

### Q3: bash.tool.md - use case for "bash without read/write"?

**A**: No reasonable use case identified. All roles with Bash also have Read/Edit/Write.
**Decision**: Consolidate ALL bash-related instructions (including "prefer specialized
tools") into bash.tool.md. This module implicitly requires Read/Edit/Write be available
(enforced by role configs, not requires_tools).

### Q4: todowrite.tool.md - weak-only assumption wrong?

**A**: **CORRECTED**. Tool modules are NOT weak-only. All agents (strong/standard/weak)
use tools. Claude Code uses one system prompt for all model classes, so examples may
have been added for weak model adherence but apply to all.

**Implication**: Tool modules should have tier variants like semantic modules. Examples
may be T2/T3 content that strong models don't need. But for simplicity, start with
single variant per tool module (equivalent to "weak" in detail level).

### Q5: tool-batching.semantic.md - parallel/chained/sequential

**A**: Clarification accepted. Three modes:

1. **Parallel**: No dependencies (Read A, Read B)
2. **Chained**: B runs after A, but B's params don't need A's result (Edit→Test)
3. **Sequential**: B's params depend on A's result (Read→Edit at discovered line)

### Q6: Tool interspersion and context benefit

**A**: **OPEN TRADEOFF**. The system prompt places tool instructions WITHIN workflow
prose (e.g., "When doing tasks... use the TodoWrite tool..."). This interspersion may
provide context benefit - rules are encountered where semantically relevant.

Our composition extracts rules into separate sections (tiered modules). This loses the
natural context association. Adding explicit context to extracted rules (e.g., "When
planning multi-step tasks, use TodoWrite") increases prompt size and cognitive burden.

- **Interspersed**: Context preserved, but harder to tier/budget.
- **Extracted**: Easier to tier/budget, but may lose context benefit.

No clear winner. Start with extracted approach (simpler tooling), monitor for adherence
issues that suggest context loss.

---

## Research: Task Agent vs Main Prompt

Task agent prompt (agent-prompt-task-tool.md) is a **minimal replacement** for the main
system prompt. Rules NOT in Task agent are effectively "interactive-only" in default
Claude Code.

| Pattern                  | Main     | Task | Scope                                |
| ------------------------ | -------- | ---- | ------------------------------------ |
| Hooks                    | ✓        | ✗    | Interactive-only                     |
| System-reminder handling | ✓        | ✗    | *Reminders injected but no handling* |
| Professional objectivity | ✓        | ✗    | Conversational roles                 |
| Over-engineering         | ✓        | ✗    | Interactive-only                     |
| OWASP security           | ✓        | ✗    | Interactive-only                     |
| Read before modify       | ✓        | ✗    | Interactive-only                     |
| Emoji                    | ✓        | ✓    | Both (core)                          |
| File creation            | ✓        | ✓    | Both (core)                          |
| Documentation files      | implicit | ✓    | Task agent MORE specific             |
| Absolute paths           | ✗        | ✓    | Task agent Bash only (cwd resets)    |

**Key finding**: System-reminder at end of Task agent file IS an actual injected
reminder, proving reminders ARE injected into subagent contexts. Handling instructions
not present may be oversight or expectation that agent naturally processes them.

---

## Research Completed

### User Hooks

**Decision:** Skip for module system (interactive-only).

| Context                    | Hooks Available | Evidence                               |
| -------------------------- | --------------- | -------------------------------------- |
| Interactive CLI            | Yes             | Main system prompt line 111            |
| Task agent (subagent)      | No              | agent-prompt-task-tool.md has no hooks |
| Orchestrated (custom sysp) | Depends         | Only if explicitly included            |

Hook events: PreToolUse, PostToolUse, UserPromptSubmit, Notification, Stop,
SubagentStop, SessionStart/End. SubagentStop fires in main agent context only.

### Instruction Count

**Finding:** The ~50 estimate counted "sections" not constraints. Actual constraint
count is 200-300+ depending on definition. See "Pending Research: Rule Definition"
below.

Per IFScale research, Claude-sonnet exhibits "linear decay" starting around 100-150
instructions. This validates our tiering approach (T1/T2/T3) to reduce constraint
density.

---

## Pending Research

### 1. Token Counter Tool (Prerequisite)

**Status:** ROADMAP.md - HIGH priority, implement before agent composition.

Required to validate prompt size assumptions and measure impact of:

- System prompt vs tool descriptions
- Tier variants (T1-only vs T1+T2+T3)
- MCP overhead vs system tool overhead

### 2. Rule Definition for Budgeting

**Problem:** We budget "rules" but haven't defined what counts as one.

| Definition Candidate | Example                          | Implication        |
| -------------------- | -------------------------------- | ------------------ |
| Section heading      | "# Git Safety Protocol"          | ~50 total (wrong)  |
| Bullet point         | "- NEVER update git config"      | ~200+ total        |
| Atomic constraint    | Each NEVER/ALWAYS/MUST statement | ~300+ total        |
| IFScale-style        | "Include keyword X in output"    | N/A (too specific) |
| Conditional judgment | "If X, then Y" (RuleBench)       | ~100-150 total     |

**Tasks:**

1. Review IFScale benchmark methodology - what counts as "instruction"?
2. Review RuleBench - what makes a well-formed vs poorly-formed rule?
3. Propose rule counting guidelines for our module system
4. Re-count existing modules using new definition

### 3. Rule Formulation Guidelines

**Problem:** Different model classes have different adherence patterns.

**IFScale findings:**

| Model Class | Decay Pattern   | Performance at 500 instructions |
| ----------- | --------------- | ------------------------------- |
| Reasoning   | Threshold decay | 62-69% (o3, gemini-2.5-pro)     |
| Claude-4    | Linear decay    | 43-45% (sonnet, opus)           |
| Smaller     | Exponential     | 7-15%                           |

**RuleBench findings:**

- Natural language rules outperform formal logic
- Irrelevant/distractor rules hurt performance significantly
- Counterfactual rules (conflicting with training) cause degradation

**Tasks:**

1. Develop empirically-grounded rule formulation guidelines (based on RuleBench,
   IFScale)
2. Test opus-class agents: baseline vs with-guidelines
3. Test sonnet-class agents: baseline vs with-guidelines
4. Compare results across model classes
5. Determine if weak/strong tiers should map to formulation style, not just rule count

---

## Architecture

### Tool Module Directory Structure

```
agents/modules/src/tools/
  read-edit.tool.md      # requires: [Read, Edit, Write]
  bash.tool.md           # requires: [Bash]
  task-agent.tool.md     # requires: [Task]
  webfetch.tool.md       # requires: [WebFetch]
  todowrite.tool.md      # requires: [TodoWrite]
  askuser.tool.md        # requires: [AskUserQuestion]
```

### Role Config Schema Extension

```yaml
# agents/roles/code.yaml
role: code
target_class: weak
rule_budget: 35

modules:
  - communication
  - checkpoint-obedience
  - tdd-cycle

enabled_tools: # NEW
  - Read
  - Edit
  - Write
  - Bash
  - Task
```

Composer automatically includes tool modules where `requires_tools ⊆ enabled_tools`.

### Role Tool Enablement

| Role     | Read/Edit | Bash | Task | WebFetch | TodoWrite | AskUser |
| -------- | --------- | ---- | ---- | -------- | --------- | ------- |
| planning | ✓         | ✓    | ✓    | ✓        | ✓         | ✓       |
| code     | ✓         | ✓    | ✓    | -        | -         | -       |
| lint     | ✓         | ✓    | -    | -        | ✓         | -       |
| execute  | ✓         | ✓    | ✓    | -        | -         | -       |
| refactor | ✓         | ✓    | ✓    | -        | ✓         | ✓       |
| review   | ✓         | ✓    | ✓    | -        | ✓         | -       |
| remember | ✓         | ✓    | -    | -        | ✓         | ✓       |

### Budget Impact

| Tool Module | Weak Rules | Included When           |
| ----------- | ---------- | ----------------------- |
| read-edit   | 5-6        | Read+Edit+Write enabled |
| bash        | 6-8        | Bash enabled            |
| task-agent  | 4-6        | Task enabled            |
| webfetch    | 2-4        | WebFetch enabled        |
| todowrite   | 8-12       | TodoWrite enabled       |
| askuser     | 3-4        | AskUserQuestion enabled |

- **Maximum additional**: ~35 rules (if all tools enabled)
- **Typical code role**: ~16 rules (Read/Edit/Bash/Task, no TodoWrite/AskUser)
- **Minimal lint role**: ~20 rules (Read/Edit/Bash/TodoWrite)

---

## Scope Analysis

### Patterns to Add to Existing Modules

| Pattern                    | Target Module             | Tier | Scope          |
| -------------------------- | ------------------------- | ---- | -------------- |
| Professional objectivity   | communication.semantic.md | T1   | Conversational |
| Emoji: avoid               | communication.semantic.md | T1   | **Core**       |
| Short and concise          | communication.semantic.md | T2   | **Core**       |
| Planning without timelines | plan-creation.semantic.md | T2   | Planning roles |
| Over-engineering avoidance | code-quality.semantic.md  | T1   | Code roles     |
| OWASP security             | code-quality.semantic.md  | T1   | Code roles     |
| System-reminder handling   | (new context module)      | T2   | **Core**       |

### AskUser Scope Clarification

Q: "Relevant for execute but not code?"

**A**: Both are plan execution roles, but differ in decision scope:

- **code**: Follows detailed plan with specific targets. Writes new logic. Unexpected =
  STOP (per communication).
- **execute**: Executes fully-specified refactoring plans from refactor agent. Must NOT
  write new logic, only modifies existing code without changing behavior. Task must be
  fully specified - no decisions needed.
- **refactor**: Broader scope, designs the refactoring approach, may need clarification.

AskUser NOT for code or execute roles - if unexpected, stop and handoff.

---

## Deferred (Phase 3 of main plan)

- Config schema `enabled_tools` field
- Composer tool module selection logic

---

## Research Reference

### Sources

**LLM Instruction/Rule Following:**

- [IFScale: How Many Instructions Can LLMs Follow at Once?](https://arxiv.org/html/2507.11538v1)
  - NeurIPS 2025 submission
  - Benchmark: keyword inclusion constraints, scales 10-500 instructions
  - Key finding: Claude-sonnet linear decay, reasoning models threshold decay

- [RuleBench: Beyond Instruction Following](https://arxiv.org/html/2407.08440v1)
  - Distinguishes "instruction" (direct behavioral guideline) from "rule" (abstract
    policy requiring conditional judgment)
  - Key finding: natural language > formal logic, irrelevant rules hurt performance

- [InFoBench](https://arxiv.org/html/2401.03601v1) - Decomposed Requirements Following
  Ratio

- [RuLES Benchmark](https://github.com/normster/llm_rules) - Simple rule following
  evaluation

**Claude Code:**

- [Hooks Reference](https://code.claude.com/docs/en/hooks)
- [How to Configure Hooks](https://claude.com/blog/how-to-configure-hooks)
- System prompts: `../claude-code-system-prompts/` (v2.0.75)

### Key Definitions

**Instruction (IFScale):** A constraint requiring specific output (e.g., "include
keyword X"). Exact match required.

**Rule (RuleBench):** Abstract policy requiring conditional judgment. Formalized as σ⊢φ
where triggering appropriate response depends on context.

**Linear decay:** Steady, predictable decline in adherence as instruction count
increases. Observed in Claude-sonnet-4, gpt-4.1.

**Threshold decay:** Near-perfect performance until critical density (~150
instructions), then decline. Observed in reasoning models (o3, gemini-2.5-pro).

---

## Handoff Notes

### For Token Counter Planning

- See ROADMAP.md "Token Count Tool" section
- Primary use case: measure module/prompt sizes in tokens
- Required measurements:
  - System prompt (main) token count
  - Per-tool-description token counts
  - Composed role prompts at different tier levels
  - MCP tool definition overhead (for comparison)

### For Rule Definition Research

- Start with IFScale and RuleBench papers (links above)
- Goal: define what counts as a "rule" for budgeting purposes
- Output: counting guidelines + re-count of existing modules
- Consider: is "rule" the right abstraction, or should we budget tokens/instructions?

### For Rule Formulation Research

- Build on RuleBench findings (natural language > formal, no irrelevant rules)
- Design experiment: same rules, different formulations
- Test opus and sonnet separately, compare with/without guidelines
- Output: formulation guidelines for module authors

---

## Research: Custom Agent Prompt Composition

- **Date:** 2025-12-31
- **Agent:** a80df58 (claude-code-guide)
- **Question:** Do custom agents in `.claude/agents/` automatically receive core rules
  from Claude Code's system prompt?

### Finding: NO Automatic Rule Injection

Custom agents spawned via the Task tool **DO NOT** automatically receive core behavioral
rules like:

- Emoji avoidance
- Professional objectivity
- Tool batching patterns
- Communication guidelines

**Evidence:**

From
[Claude Code Subagents documentation](https://code.claude.com/docs/en/sub-agents.md):

> Your subagent's system prompt goes here. This can be multiple paragraphs and should
> clearly define the subagent's role, capabilities, and approach to solving problems.

The documentation explicitly states that whatever you write in the agent file is
**exactly** what the subagent gets.

From
[Agent SDK documentation](https://platform.claude.com/docs/en/agent-sdk/modifying-system-prompts.md):

> The Agent SDK uses an **empty system prompt** by default for maximum flexibility.

And:

> Claude Code's system prompt includes: Tool usage instructions and available tools,
> Code style and formatting guidelines, Response tone and verbosity settings, Security
> and safety instructions
>
> **These are NOT passed to subagents.**

### Architectural Difference

**Main session:**

- Modular, conditional system prompt
- Environment-dependent rules
- 40+ strings conditionally loaded

**Custom agents:**

- Only the `prompt` field from agent definition
- Separate context window
- No inherited rules or memory
- Tools restricted to agent's `tools` field

### Built-in vs Custom Agents

**Built-in agents** (general-purpose, Explore, Plan):

- Curated system prompts by Anthropic
- Include tool-specific instructions
- Designed for specific use cases

**Custom agents:**

- Get only what you define
- Must explicitly include all desired behavioral rules
- Don't inherit main session conventions

### Implication for Subagent Generation

**CRITICAL:** Custom agents in `.claude/agents/` must include ALL rules explicitly:

```markdown
---
name: code-reviewer
tools: Read, Grep, Glob
---

# Code Review Agent

Follow these core rules:

- Avoid emojis unless explicitly requested
- Maintain professional objectivity
- Be concise for CLI output
- Use specialized tools (Read not cat, Edit not sed) [... rest of prompt with all needed
  rules ...]
```

**Consequence:** Subagent prompts will be LARGER than role prompts, as they cannot rely
on Claude Code's system prompt to provide foundation rules.

### Sources

- [Claude Code Subagents Documentation](https://code.claude.com/docs/en/sub-agents.md)
- [Agent SDK Subagents](https://platform.claude.com/docs/en/agent-sdk/subagents.md)
- [Modifying System Prompts - Agent SDK](https://platform.claude.com/docs/en/agent-sdk/modifying-system-prompts.md)
- [Claude Code System Prompts Repository](https://github.com/Piebald-AI/claude-code-system-prompts)
