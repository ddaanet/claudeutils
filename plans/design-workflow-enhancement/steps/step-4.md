# Step 4

**Plan**: `plans/design-workflow-enhancement/runbook.md`
**Execution Model**: haiku
**Report Path**: `plans/design-workflow-enhancement/reports/step-4-symlinks-validation.md`

---

## Step 4: Create Symlinks and Validate

**Objective**: Create symlinks for agent, run validation

**Execution Model**: Haiku (simple operations)

**Implementation**:

```bash
# Navigate to agent-core and create symlinks
cd /Users/david/code/claudeutils/agent-core && just sync-to-parent

# Verify symlink created
ls -la /Users/david/code/claudeutils/.claude/agents/quiet-explore.md

# Run validation
cd /Users/david/code/claudeutils && just dev
```

**Expected Outcome**: Symlink exists, validation passes

**Unexpected Result Handling**:
- If symlink creation fails: Check permissions, escalate to sonnet
- If validation fails: Report specific failures (formatting, linting)

**Error Conditions**:
- `just sync-to-parent` fails → Escalate with error output
- Symlink not created → Verify agent file exists, escalate if so
- `just dev` fails → Report failures for fixing

**Validation**:
- Symlink exists and points to `agent-core/agents/quiet-explore.md`
- `just dev` exits with code 0

**Success Criteria**:
- Symlink verified
- All checks pass

**Report Path**: `plans/design-workflow-enhancement/reports/step-4-symlinks-validation.md`

---
