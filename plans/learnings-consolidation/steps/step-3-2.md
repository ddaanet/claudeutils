# Step 3.2

**Plan**: `plans/learnings-consolidation/runbook.md`
**Execution Model**: sonnet
**Phase**: 1

---

## Step 3.2: Create memory-refactor Agent

**Objective:** Build documentation refactoring agent to split oversized files at logical boundaries.

**Implementation:**

Create `agent-core/agents/memory-refactor.md`:

**1. Frontmatter (YAML):**

```yaml
---
name: memory-refactor
description: Use this agent when a documentation target file exceeds 400 lines and needs to be split into logical sections. Triggered by remember-task when it encounters a file at the limit. Splits file by H2/H3 topic boundaries, preserves all content, creates 100-300 line sections, runs validate-memory-index.py autofix. Returns list of files created/modified.
model: sonnet
color: yellow
tools: ["Read", "Write", "Edit", "Grep", "Glob"]
---
```

**2. Body structure:**

**A. Role statement:**
```markdown
# Memory-Refactor Agent

You are a documentation refactoring agent specializing in splitting oversized files into logical sections.

**Triggering context:** Remember-task agent encountered a file at/near 400-line limit and escalated via consolidation report. Handoff delegated to you for file splitting.

**Goal:** Preserve all content while creating maintainable file sizes (100-300 lines per file).
```

**B. Input specification:**
```markdown
