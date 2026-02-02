# Step 5

**Plan**: `plans/workflow-controls/runbook.md`
**Common Context**: See plan file for context

---

## Step 5: Update handoff-haiku Skill - Task Metadata Format

**Objective**: Document task metadata convention for mechanical merge.

**Script Evaluation**: Direct execution (surgical edit)

**Execution Model**: Sonnet

**Implementation**:

Edit `agent-core/skills/handoff-haiku/SKILL.md` in Pending Tasks section (around line 40-60):

Add after existing Pending Tasks instructions:

```markdown
**Task metadata format:**

Use this convention when writing tasks:

```
- [ ] **Task Name** — `command` | model | restart?
```

Examples:
```
- [ ] **Implement ambient awareness** — `/plan-adhoc plans/ambient-awareness/design.md` | sonnet
- [ ] **Design runbook identifiers** — `/design plans/runbook-identifiers/problem.md` | opus | restart
```

**Field rules:**
- Command: Backtick-wrapped command to start the task
- Model: `haiku`, `sonnet`, or `opus` (default: sonnet if omitted)
- Restart: Optional flag - only include if restart needed (omit = no restart)

**Mechanical merge:**
Preserve metadata format verbatim when carrying forward unresolved items. No judgment needed - copy unchanged.
```

**Expected Outcome**: Skill documents metadata convention.

**Unexpected Result Handling**:
- If Pending Tasks section reorganized → adapt to structure

**Error Conditions**:
- Section not found → report structure for guidance

**Validation**:
- Metadata format documented
- Examples provided
- Mechanical merge instruction present

**Success Criteria**:
- Convention documented
- Examples clear
- Merge behavior specified

**Report Path**: `plans/workflow-controls/reports/step-5.md`

---
