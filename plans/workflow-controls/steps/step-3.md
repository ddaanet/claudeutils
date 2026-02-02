# Step 3

**Plan**: `plans/workflow-controls/runbook.md`
**Common Context**: See plan file for context

---

## Step 3: Update commit Skill - STATUS Display

**Objective**: Replace bare "Next: task" with full STATUS format.

**Script Evaluation**: Direct execution (surgical edit)

**Execution Model**: Sonnet

**Implementation**:

Edit `agent-core/skills/commit/SKILL.md`.

Find this section (starts at line ~185):
```markdown
