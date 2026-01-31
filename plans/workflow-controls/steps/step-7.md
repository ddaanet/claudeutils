# Step 7

**Plan**: `plans/workflow-controls/runbook.md`
**Common Context**: See plan file for context

---

## Step 7: Add UserPromptSubmit Hook to Settings

**Objective**: Register hook in `.claude/settings.json`.

**Script Evaluation**: Direct execution (JSON edit)

**Execution Model**: Sonnet

**Implementation**:

Read `.claude/settings.json` current structure, then add UserPromptSubmit hook:

```json
{
  "hooks": {
    "PreToolUse": [...existing...],
    "PostToolUse": [...existing...],
    "UserPromptSubmit": [
      {
        "type": "command",
        "command": "python3 $CLAUDE_PROJECT_DIR/agent-core/hooks/userpromptsubmit-shortcuts.py",
        "timeout": 5
      }
    ]
  }
}
```

**Note:** UserPromptSubmit hooks do not support the `matcher` field (per design.md line 44, 98). The hook always fires on every prompt and does internal filtering via regex.

**Expected Outcome**: Hook registered in settings.

**Unexpected Result Handling**:
- If hooks structure different → adapt to format
- If UserPromptSubmit already exists → append to array

**Error Conditions**:
- JSON parse failure → verify syntax
- File write failure → escalate

**Validation**:
- Valid JSON after edit
- UserPromptSubmit key exists
- Command path uses $CLAUDE_PROJECT_DIR
- Timeout set to 5 seconds

**Success Criteria**:
- Hook registered
- JSON valid
- Path portable

**Report Path**: `plans/workflow-controls/reports/step-7.md`

---
