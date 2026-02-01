# Step 1

**Plan**: `/Users/david/code/claudeutils/plans/design-workflow-enhancement/runbook.md`
**Common Context**: See plan file for context

---

## Step 1: Create quiet-explore Agent

**Objective**: Create `agent-core/agents/quiet-explore.md` from design specification

**Execution Model**: Sonnet (interprets spec into agent file)

**Implementation**:

Read design section "quiet-explore Agent" (lines 128-167) and create agent file at `agent-core/agents/quiet-explore.md`.

**Agent specification from design**:
- Name: quiet-explore
- Description: Multi-line using `|` syntax, summarize "exploration results persist to files for reuse across phases"
- Model: haiku
- Color: cyan
- Tools: ["Read", "Glob", "Grep", "Bash", "Write"]

**System prompt directives** (from design):
- File search specialist (based on built-in Explore prompt)
- Read-only for codebase (Write only for report output)
- Parallel tool calls for speed
- Absolute paths in findings
- Report format: Structured findings with file paths, key patterns, code snippets
- Output: Write report to caller-specified path, return filepath only
- Bash: Read-only operations (ls, git status, git log, git diff)

**Report location convention** (include in prompt):
- Design phase: `plans/{name}/reports/explore-{topic}.md`
- Ad-hoc: `tmp/explore-{topic}.md`

**Expected Outcome**: Agent file created with valid YAML frontmatter and system prompt incorporating all directives

**Unexpected Result Handling**:
- If baseline pattern (quiet-task.md) unclear: Read `agent-core/agents/quiet-task.md` for reference structure
- If multi-line description fails YAML parse: Verify `|` syntax used correctly

**Error Conditions**:
- Missing design file → Escalate to user
- Cannot determine appropriate system prompt structure → Escalate to user

**Validation**:
- File exists at `agent-core/agents/quiet-explore.md`
- YAML frontmatter parses (name, description, model, color, tools present)
- System prompt includes report output directive
- System prompt includes read-only Bash constraint

**Success Criteria**:
- Agent file created
- YAML uses multi-line syntax for description
- System prompt addresses all 7 directives from design

**Report Path**: `plans/design-workflow-enhancement/reports/step-1-agent-creation.md`

---
