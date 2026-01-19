# Step 2.1

**Plan**: `plans/unification/phase2-execution-plan.md`
**Common Context**: See plan file for context

---

## Step 2.1: Compare Compose Scripts

**Objective**: Verify emojipack compose.sh matches claudeutils agents/compose.sh

**Script Evaluation**: Direct execution (single diff command, ≤25 lines)

**Implementation**:
```bash
# Create analysis directory if needed
mkdir -p scratch/consolidation/analysis

# Verify source files exist
if [ ! -f /Users/david/code/emojipack/agents/compose.sh ]; then
    echo "ERROR: emojipack compose.sh not found" >&2
    exit 1
fi
if [ ! -f agents/compose.sh ]; then
    echo "ERROR: claudeutils compose.sh not found" >&2
    exit 1
fi

# Compare compose scripts
diff -u /Users/david/code/emojipack/agents/compose.sh \
        agents/compose.sh \
        > scratch/consolidation/analysis/compose-sh-diff.patch || true

# Check result and report
PATCH_SIZE=$(wc -c < scratch/consolidation/analysis/compose-sh-diff.patch)
if [ "$PATCH_SIZE" -eq 0 ]; then
    echo "SUCCESS: Scripts identical (patch empty)"
else
    echo "UNEXPECTED: Scripts differ ($PATCH_SIZE bytes) - expected identical per phase2.md"
    echo "ACTION: Document differences in execution report and escalate to sonnet"
fi
```

**Expected Outcome**: Empty patch (scripts should be identical per phase2.md comment)

**Unexpected Result Handling**:
- If patch non-empty: Document differences, do NOT proceed to Step 2.2, escalate to sonnet for path verification

**Error Conditions**:
- Source file not found → Report error, escalate to sonnet
- Permission denied → Report error, escalate to sonnet
- Output directory not writable → Report error, escalate to sonnet

**Validation**:
- Patch file exists at expected path
- Patch file size documented in execution report
- If non-empty, differences summarized in execution report

**Success Criteria**:
- Patch file created at `scratch/consolidation/analysis/compose-sh-diff.patch`
- File size documented (0 bytes = identical as expected)
- Execution report contains verification results

**Report Path**: `plans/unification/reports/phase2-step1-execution.md`

---
