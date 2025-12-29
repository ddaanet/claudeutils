# System Prompt Pattern Integration: Opus Tasks

Tasks requiring Opus-level reasoning. See `design.md` for context, `drafts.md` for
preliminary module content to refine.

---

## Research Tasks (Completed)

### 1. Tool Description Analysis ✓

**Completed.** See design.md "Tool Description Size Analysis".

- Total ~966 lines across all tool descriptions
- Largest: todowrite (189), bash-git-commit (95), enterplanmode (92)
- Architecture note: tool descriptions are in tool message, NOT system prompt

### 2. Instruction Count Reality Check ✓

**Completed.** The ~50 estimate was wrong - counted sections not constraints.

- Actual: 200-300+ constraints depending on definition
- IFScale research: Claude-sonnet linear decay starts at 100-150 instructions
- This validates tiering approach (T1/T2/T3)

### 3. User Hooks Research ✓

**Completed.** See design.md "Research Completed: User Hooks".

- Decision: Skip for module system (interactive-only)
- Task agents have no hook awareness
- SubagentStop fires in main agent context only

---

## New Research Tasks (Pending)

### A. Token Counter Tool

**Priority:** HIGH - prerequisite for other research.

See ROADMAP.md. Implement before continuing module work.

### B. Rule Definition for Budgeting

See design.md "Pending Research: Rule Definition for Budgeting".

**Tasks:**

1. Review IFScale benchmark methodology
2. Review RuleBench rule definition
3. Propose counting guidelines for our modules
4. Re-count existing modules

### C. Rule Formulation Guidelines

See design.md "Pending Research: Rule Formulation Guidelines".

**Tasks:**

1. Develop empirically-grounded formulation guidelines
2. Test opus-class: baseline vs with-guidelines
3. Test sonnet-class: baseline vs with-guidelines
4. Compare and document

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

- [x] All 13 sysprompt-reference files mapped to modules (see design.md table)
- [ ] Tool description instructions captured in tool modules
- [x] Interactive-only patterns explicitly marked as skipped (hooks, help-feedback,
      documentation-lookup)
