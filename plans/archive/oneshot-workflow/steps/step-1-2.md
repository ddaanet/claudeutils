# Phase 1 Execution - Step 2

**Plan**: `plans/oneshot-workflow/phase1-execution-plan.md`
**Common Context**: See plan file for script specification, baseline rename info, and file structure

---

## Step 1.2: Move and Rename Baseline Agent

**Objective**: Move task-execute.md to agent-core/agents/quiet-task.md and update references

**Script Evaluation**: Small script (file copy + reference updates, ≤25 lines for move, prose for reference updates)

**Execution Model**: Haiku

**Implementation**:

**Part A: Copy file to new location**
```bash
#!/usr/bin/env bash
# Copy task-execute.md to agent-core/agents/quiet-task.md

SOURCE="/Users/david/code/claudeutils/.claude/agents/task-execute.md"
TARGET="/Users/david/code/agent-core/agents/quiet-task.md"

# Verify source exists
if [ ! -f "$SOURCE" ]; then
    echo "ERROR: Source file not found: $SOURCE" >&2
    exit 1
fi

# Copy to target
cp "$SOURCE" "$TARGET"

# Verify copy
if [ -f "$TARGET" ]; then
    echo "SUCCESS: Copied to $TARGET"
    echo "File size: $(wc -c < "$TARGET") bytes"
else
    echo "ERROR: Copy failed" >&2
    exit 1
fi
```

**Part B: Update frontmatter in new file**

Using Edit tool:
1. Read `/Users/david/code/agent-core/agents/quiet-task.md`
2. Edit frontmatter:
   - Change `name: task-execute` → `name: quiet-task`
   - Update `description:` to reference quiet execution pattern

**Part C: Update references**

Search for references to update (using Grep tool):

**Verification: Search entire repository**
```bash
# Search entire claudeutils repo for task-execute references
cd /Users/david/code/claudeutils
rg "task-execute" --type md --files-with-matches
```

If files found beyond the 4 known locations below, document in report and escalate to sonnet.

**Known locations to update**:
- `/Users/david/code/claudeutils/CLAUDE.md`
- `/Users/david/code/claudeutils/agents/context.md`
- `/Users/david/code/claudeutils/plans/unification/build-plan-agent.sh`
- `/Users/david/code/claudeutils/plans/oneshot-workflow/design.md`

Update each reference:
- Documentation: Change "task-execute" → "quiet-task"
- Paths: Update to `/Users/david/code/agent-core/agents/quiet-task.md`

**Part D: Keep original for compatibility**

Leave `.claude/agents/task-execute.md` in place for now (removal in Phase 4 cleanup).

**Expected Outcome**: File copied, frontmatter updated, references updated

**Unexpected Result Handling**:
- If source file missing: Report error and escalate
- If references found in unexpected locations: Document in report, proceed with known updates

**Error Conditions**:
- Source file not found → Report error, escalate to sonnet
- Permission denied → Report error, escalate to sonnet
- Grep finds references in unexpected files → Document in report, escalate to sonnet

**Validation**:
- New file exists at target location
- Frontmatter updated correctly
- All known references updated
- Original file still exists

**Success Criteria**:
- `agent-core/agents/quiet-task.md` exists with updated frontmatter
- References in known files updated
- No broken references to old path in critical files

**Report Path**: `plans/oneshot-workflow/reports/phase1-step2-execution.md`

---

---

## Execution Instructions

1. Read `phase1-execution-plan.md` for:
   - Prerequisites and validation requirements
   - Error escalation triggers
   - Success criteria

2. Execute this step following the implementation section above

3. Perform all validation checks as specified

4. Write execution log to report path specified above with:
   - What was done
   - Results and artifacts created
   - Any errors or unexpected outcomes
   - Verification of success criteria

5. Return format:
   - Success: "done: <brief summary>"
   - Failure: "error: <description with diagnostic info>"

6. **Stop immediately** on any unexpected results per communication rules
