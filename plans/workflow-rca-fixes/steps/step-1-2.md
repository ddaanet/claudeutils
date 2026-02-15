# Step 1.2

**Plan**: `plans/workflow-rca-fixes/runbook.md`
**Execution Model**: sonnet
**Phase**: 1

---

## Step 1.2: Create memory-index skill

**Objective**: Wrap memory-index.md with Bash transport prolog for sub-agent recall.

**Prerequisites**:
- Read `agents/memory-index.md` (content to wrap)
- Read error-handling skill from Step 1.1 (pattern reference)
- plugin-dev:skill-development loaded

**Implementation**:

Create `agent-core/skills/memory-index/SKILL.md`:

1. YAML frontmatter:
   - name: memory-index
   - description: "This skill should be used when sub-agents need memory recall capabilities. Provides index of when/how entries with Bash transport for agents without Skill tool access."
   - user-invocable: false

2. Skill prolog with Bash transport explanation:
   - Sub-agents lack Skill tool
   - Must invoke via Bash: `agent-core/bin/when-resolve.py when "<trigger>"`
   - Index syntax unchanged from main agent `/when` invocations

3. Include full content of `agents/memory-index.md`

**Expected Outcome**: Skill file created at `agent-core/skills/memory-index/SKILL.md` with transport prolog and memory index content.

**Error Conditions**:
- If transport prolog unclear → add concrete Bash invocation examples
- If index content malformed → verify memory-index.md structure

**Validation**:
1. Commit changes
2. Delegate to skill-reviewer: "Review memory-index skill for transport prolog clarity and index completeness"
3. Read review report
4. If UNFIXABLE: STOP, escalate
5. If all fixed: proceed

**Report location**: plans/workflow-rca-fixes/reports/step-1.2-skill-review.md

---
