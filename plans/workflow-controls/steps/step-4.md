# Step 4

**Plan**: `plans/workflow-controls/runbook.md`
**Common Context**: See plan file for context

---

## Step 4: Update handoff Skill - STATUS Tail

**Objective**: Add STATUS display as default tail, skip when `--commit` specified.

**Script Evaluation**: Direct execution (surgical edit)

**Execution Model**: Sonnet

**Implementation**:

Edit `agent-core/skills/handoff/SKILL.md`.

**Part 1:** Add new step 7 after the "6. Trim Completed Tasks" section.

Insert this new section:

```markdown
### 7. Display STATUS (unless --commit)

**If `--commit` flag was NOT specified:**

Display STATUS listing as final output. Read session.md Pending Tasks section and format:

```
Next: <first pending task name>
  `<command to start it>`
  Model: <recommended model> | Restart: <yes/no>

Pending:
- <task 2 name> (<model if non-default>)
- <task 3 name>
```

**Graceful degradation:**
- Missing session.md or no Pending Tasks → "No pending tasks."
- Old format (no metadata) → use defaults (sonnet, no restart)

**If `--commit` flag WAS specified:**

Skip STATUS display. The `/commit` skill will show it after committing.

**Rationale:** STATUS replaces the old session size advice. Model recommendations are now shown in STATUS display's "Model:" field.
```

**Part 2:** Remove old session size advice section.

Find and delete this section (starts around line ~121):
```markdown
[If still >150 lines after trimming:]
session.md is [X] lines (threshold: 150) after trimming completed tasks.
Review pending tasks and learnings for further reduction.

[If workflow complete:]
All workflow tasks complete. Start fresh session for new work.

[If next task needs different model:]
Next task ([task name]) requires [model name]. Switch model when starting new session."
```

**If next pending task needs different model:**
- Design stage → Suggest Opus
- Execution stage → Suggest Haiku
- Planning/Review/Completion → Suggest Sonnet

Example: "Next task: Design stage. Switch to Opus model for architectural work."
```

This advice is superseded by STATUS display's model recommendations.

**Expected Outcome**: Handoff shows STATUS unless chaining to commit.

**Unexpected Result Handling**:
- If step numbering different → adjust insertion point

**Error Conditions**:
- Edit fails → report current structure

**Validation**:
- New step 7 exists
- Conditional logic for --commit flag present
- Old session size advice removed

**Success Criteria**:
- STATUS tail added
- Flag logic correct
- Old advice section removed

**Report Path**: `plans/workflow-controls/reports/step-4.md`

---
