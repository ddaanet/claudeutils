# Step 1.1

**Plan**: `plans/workflow-feedback-loops/runbook.md`
**Execution Model**: sonnet
**Phase**: 1

---

## Step 1.1: Create outline-review-agent

**Objective:** Create agent that reviews design outlines before user discussion

**Execution Model:** Sonnet

**Implementation:**

Create `agent-core/agents/outline-review-agent.md` with:

**Frontmatter:**
- name: outline-review-agent
- description: Use when reviewing design outlines after Phase A.5, before user discussion. Validates soundness, completeness, feasibility.
- model: sonnet
- color: cyan
- tools: [Read, Write, Edit, Bash, Grep, Glob]

**System prompt requirements:**
1. Input validation: Verify requirements exist (file or inline), verify artifact is outline.md (not design.md, not runbook)
2. Review criteria from design FP-1:
   - Soundness: Approach is technically feasible
   - Completeness: All requirements have corresponding approach elements
   - Scope: Boundaries are clear and reasonable
   - Feasibility: No obvious blockers or circular dependencies
   - Clarity: Key decisions are explicit, not implicit
3. Requirements-to-outline traceability: Every FR-* must map to outline section
4. Fix-all policy: Apply ALL fixes (critical, major, AND minor) using Edit tool
5. Output: Write review to specified path, return filepath

**Reference:** Design Section "FP-1: Outline Review (NEW)" lines 112-147

**Expected Outcome:** Agent file exists, follows agent-development skill patterns

**Success Criteria:**
- File exists at agent-core/agents/outline-review-agent.md
- Valid YAML frontmatter with all required fields
- System prompt includes input validation, review criteria, fix-all policy
- Examples in description show triggering conditions

---
