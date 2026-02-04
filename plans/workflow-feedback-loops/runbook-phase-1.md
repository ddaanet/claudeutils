## Phase 1: New Agents

**Prerequisite:** Load `plugin-dev:agent-development` skill before starting (provides agent structure, frontmatter guidance, progressive disclosure patterns).

### Step 1.1: Create outline-review-agent

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

### Step 1.2: Create runbook-outline-review-agent

**Objective:** Create agent that reviews runbook outlines before full expansion

**Execution Model:** Sonnet

**Implementation:**

Create `agent-core/agents/runbook-outline-review-agent.md` with:

**Frontmatter:**
- name: runbook-outline-review-agent
- description: Use when reviewing runbook outlines after Point 0.75 (plan-adhoc) or Phase 1.5 (plan-tdd), before full runbook generation.
- model: sonnet
- color: cyan
- tools: [Read, Write, Edit, Bash, Grep, Glob]

**System prompt requirements:**
1. Input validation: Verify requirements, design, and outline all exist
2. Review criteria from design FP-3:
   - Requirements coverage: Every FR-* maps to at least one step/cycle
   - Design alignment: Steps reference design decisions appropriately
   - Phase structure: Phases are balanced and logically grouped
   - Complexity distribution: No phase is disproportionately large
   - Dependency sanity: No obvious circular or missing dependencies
3. Fix-all policy: Apply ALL fixes using Edit tool
4. Output: Write review to specified path, return filepath

**Reference:** Design Section "FP-3: Runbook Outline Review (NEW)" lines 169-231

**Expected Outcome:** Agent file exists, follows agent-development skill patterns

**Success Criteria:**
- File exists at agent-core/agents/runbook-outline-review-agent.md
- Valid YAML frontmatter with all required fields
- System prompt includes input validation, review criteria, fix-all policy
- Runbook outline format from design is referenced
