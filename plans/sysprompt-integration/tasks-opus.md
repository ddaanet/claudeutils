# System Prompt Pattern Integration: Opus Tasks

Tasks requiring Opus-level reasoning. See `design.md` for context, `drafts.md` for
preliminary module content to refine.

---

## Research Tasks

### 1. Tool Description Analysis

Extract instructions from
`claude-code-system-prompts/system-prompts/tool-description-*.md`:

- Count instructions per tool description
- Identify which tools are Claude Code CLI vs IDE-only (Computer, ReadFile)
- Note dynamic injections (task-async-return-note)
- Special attention to `bash-git-commit-and-pr-creation-instructions.md` (large)

**Output**: Instruction inventory with counts and categorization.

### 2. Instruction Count Reality Check

Verify total instructions across:

- System prompt (main)
- Tool descriptions (for default interactive session with all tools)

**Expected**: ≈50 instructions total. Validates extraction completeness.

### 3. User Hooks Research

Determine hook availability per execution context:

- Interactive CLI
- Task agent (sub-agent)
- Orchestrated agents (custom system prompt)

**Output**: Decision on whether to include hooks in module system or mark
interactive-only.

---

## Processing Tasks

### 4. Finalize Tool Module Content

Review draft tool modules against source material. For each module:

- Verify all relevant instructions captured from system prompt
- Verify all relevant instructions captured from tool descriptions
- Confirm tier assignments (T1/T2/T3) appropriate
- Validate rule counts match budget

Tool modules to finalize:

| Module             | Draft Rules | Source Files to Check                        |
| ------------------ | ----------- | -------------------------------------------- |
| read-edit.tool.md  | 5-6         | tool-policy, doing-tasks                     |
| bash.tool.md       | 6-8         | tool-policy, bash-git-commit-and-pr-creation |
| task-agent.tool.md | 4-6         | tool-policy                                  |
| webfetch.tool.md   | 2-4         | (tool description only)                      |
| todowrite.tool.md  | 8-12        | todowrite.sysprompt                          |
| askuser.tool.md    | 3-4         | askuser.sysprompt                            |

### 5. Finalize Semantic Module Updates

Review existing modules for patterns to add:

| Target Module             | Patterns to Add                                        |
| ------------------------- | ------------------------------------------------------ |
| communication.semantic.md | emoji avoid (T1), short/concise (T2), objectivity (T1) |
| plan-creation.semantic.md | no-timelines (T2)                                      |
| code-quality.semantic.md  | over-engineering (T1), OWASP (T1)                      |
| tool-batching.semantic.md | parallel/chained/sequential clarification              |
| (new) context.semantic.md | system-reminder handling (T2)                          |

For each: draft exact rule text with tier assignment.

---

## Validation Tasks

### 6. Budget Validation

After finalizing content, verify budgets work for both scenarios:

1. **Fine-tuned sessions**: Role modules + relevant tool modules only
2. **Default interactive**: Role modules + all tool modules

Check no role exceeds target budget (typically 35 rules for weak).

### 7. Cross-Reference Check

Ensure no instruction from source material was missed:

- [ ] All 13 sysprompt-reference files mapped to modules
- [ ] Tool description instructions captured in tool modules
- [ ] Interactive-only patterns explicitly marked as skipped
