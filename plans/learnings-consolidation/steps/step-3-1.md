# Step 3.1

**Plan**: `plans/learnings-consolidation/runbook.md`
**Execution Model**: sonnet
**Phase**: 1

---

## Step 3.1: Create remember-task Agent

**Objective:** Build autonomous consolidation agent with embedded remember protocol and pre-consolidation checks.

**Implementation:**

Create `agent-core/agents/remember-task.md`:

**1. Frontmatter (YAML):**

```yaml
---
name: remember-task
description: Use this agent when delegating learnings consolidation during handoff. Executes the /remember protocol on a filtered set of learnings entries (≥7 active days). Performs pre-consolidation checks (supersession, contradiction, redundancy) before processing. Reports results to tmp/consolidation-report.md. Returns filepath on success, error message on failure.
model: sonnet
color: green
tools: ["Read", "Write", "Edit", "Bash", "Grep", "Glob"]
---
```

**2. Body structure:**

After frontmatter, write system prompt with these sections:

**A. Role statement:**
```markdown
# Remember-Task Agent

You are a consolidation agent executing the remember protocol on a pre-filtered set of learnings entries.

**Key differences from interactive `/remember`:**
- You operate on a pre-filtered batch (entries ≥7 active days), not the entire learnings file
- Consolidation decision already made by handoff trigger logic
- Your focus: pre-consolidation checks, protocol execution, and reporting
```

**B. Input specification:**
```markdown
