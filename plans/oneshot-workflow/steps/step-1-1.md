# Phase 1 Execution - Step 1

**Plan**: `plans/oneshot-workflow/phase1-execution-plan.md`
**Common Context**: See plan file for script specification, baseline rename info, and file structure

---

## Step 1.1: Create Directory Structure

**Objective**: Create agent-core/agents/ and agent-core/bin/ directories

**Script Evaluation**: Direct execution (simple directory creation, ≤25 lines)

**Execution Model**: Haiku

**Implementation**:
```bash
#!/usr/bin/env bash
# Create directory structure in agent-core

AGENT_CORE="/Users/david/code/agent-core"

# Verify agent-core exists
if [ ! -d "$AGENT_CORE" ]; then
    echo "ERROR: agent-core directory not found at $AGENT_CORE" >&2
    exit 1
fi

# Create directories
mkdir -p "$AGENT_CORE/agents"
mkdir -p "$AGENT_CORE/bin"

# Verify creation
if [ -d "$AGENT_CORE/agents" ] && [ -d "$AGENT_CORE/bin" ]; then
    echo "SUCCESS: Created directories:"
    echo "  - $AGENT_CORE/agents"
    echo "  - $AGENT_CORE/bin"
    ls -ld "$AGENT_CORE/agents" "$AGENT_CORE/bin"
else
    echo "ERROR: Failed to create one or more directories" >&2
    exit 1
fi
```

**Expected Outcome**: Directories created successfully

**Unexpected Result Handling**:
- If directories already exist: Proceed (idempotent operation)
- If creation fails: Report error and escalate to sonnet

**Error Conditions**:
- agent-core not found → Report error, escalate to sonnet
- Permission denied → Report error, escalate to sonnet

**Validation**:
- Both directories exist
- Directories are writable

**Success Criteria**:
- `agent-core/agents/` exists and is writable
- `agent-core/bin/` exists and is writable

**Report Path**: `plans/oneshot-workflow/reports/phase1-step1-execution.md`

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
