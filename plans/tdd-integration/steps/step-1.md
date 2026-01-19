# Step 1

**Plan**: `plans/tdd-integration/runbook.md`
**Common Context**: See plan file for context

---

## Step 1: Create oneshot workflow documentation

**Objective**: Move existing workflow.md to agent-core and rename to oneshot-workflow.md

**Script Evaluation**: Prose description (uses specialized tools for file operations)

**Execution Model**: Sonnet

**Tool Usage**:
- Use Read tool to read source file
- Use Write tool to create destination file
- Use Bash only for directory verification
- Never use bash file operations (cp, cat, etc.)

**Implementation**:

1. Verify destination directory exists:
   ```bash
   test -d agent-core/agents || (echo "ERROR: agent-core/agents not found" && exit 1)
   ```

2. Read source file:
   - Use Read tool on `agents/workflow.md`
   - Store content for write operation

3. Write to destination:
   - Use Write tool to create `agent-core/agents/oneshot-workflow.md`
   - Write exact content from source file

4. Report success:
   - Note: Original `agents/workflow.md` preserved for reference until all updates complete

**Expected Outcome**:
- File `agent-core/agents/oneshot-workflow.md` exists
- File size matches original `agents/workflow.md`
- Original file still exists (will be deleted in later step after reference updates)

**Unexpected Result Handling**:
- If source file missing: STOP - verify current working directory
- If destination directory missing: STOP - verify agent-core submodule initialized
- If copy fails: STOP - check file permissions

**Error Conditions**:
- File not found → STOP and report to user
- Permission denied → STOP and report to user
- Disk space issue → STOP and report to user

**Validation**:
- Read `agent-core/agents/oneshot-workflow.md` successfully (confirms file exists)
- File size > 10000 bytes (workflow.md is substantial)
- Grep for "workflow" pattern in `agent-core/agents/oneshot-workflow.md` (confirms content copied)

**Success Criteria**:
- File created successfully
- File size matches source
- File readable and contains workflow content

**Report Path**: `plans/tdd-integration/reports/step-1-report.md`

---
