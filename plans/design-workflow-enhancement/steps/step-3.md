# Step 3

**Plan**: `plans/design-workflow-enhancement/runbook.md`
**Common Context**: See plan file for context

---

## Step 3: Restructure design/SKILL.md into Three-Phase Workflow

**Objective**: Transform design skill from linear steps (0-7) to three-phase workflow (Research+Outline → Iterative Discussion → Generate Design).

**Execution Model**: Sonnet

**Implementation**:

Read `agent-core/skills/design/SKILL.md` and restructure according to design.md specification (lines 30-69).

**Key Changes**:

1. **Replace Step 1 + Step 1.5 with Phase A.1 (Documentation Checkpoint)**:
   - Expand from current memory discovery into 5-level hierarchy
   - **Level 1 text to insert:** "**Level 1 (Local knowledge)**: Scan memory-index.md for entries relevant to task domain. For any matches, read referenced files to load full context. Always read agents/design-decisions.md. Read other agents/decisions/*.md and agent-core/fragments/*.md ONLY when memory-index entries reference them as relevant to the task domain."
   - Level 2 (conditional): plugin-dev skills when touching hooks/agents/skills/MCP
   - Level 3 (conditional): Context7 via direct MCP tool calls (write results to report)
   - Level 4 (always for complex): quiet-explore agent
   - Level 5 (conditional): WebSearch/WebFetch when local sources insufficient
   - Emphasize domain-awareness: no fixed "always read X" beyond level 1

2. **Replace Step 2 with Phase A.2 (Explore Codebase)**:
   - Change delegation from `subagent_type="Explore"` to `subagent_type="quiet-explore"`
   - Specify report path pattern: `plans/{name}/reports/explore-{topic}.md`
   - Clarify: only Read specific files AFTER exploration identifies them

3. **Add Phase A.3-4 (Context7 + Web Research)**:
   - Context7: Designer calls MCP tools directly, writes results to `plans/{name}/reports/context7-{topic}.md`
   - Web: WebSearch/WebFetch direct from main session when needed

4. **Split Step 4 into Phase A.5 (Outline) + Phase C.1 (Full Design)**:
   - Phase A.5: Produce freeform plan outline, present to user
   - Add escape hatch: Insert text in Phase A.5: "**Escape hatch:** If user input already specifies approach, decisions, and scope (e.g., detailed problem.md), compress A+B by presenting outline and asking for validation in a single message."
   - Phase C.1: Write full design.md incorporating validated outline + all research

5. **Add Phase B (Iterative Discussion)**:
   - User provides feedback on outline
   - Designer responds with incremental deltas only (not full outline regeneration)
   - Loop until user validates approach
   - Termination: fundamental approach change → restart Phase A

6. **Add Documentation Perimeter to Phase C.1**:
   - Insert new section in design.md template AFTER "Implementation notes" section
   - Section heading: "## Documentation Perimeter"
   - Required reading (files planner must load)
   - Context7 references (library + query hint)
   - Note that additional research is allowed
   - Example placement: After Implementation Notes, before Next Steps

7. **Update Phase C.3-4 (Vet Process)**:
   - Change from `(subagent_type="general-purpose", model="opus")` to `(subagent_type="vet-agent", model="sonnet")`
   - Designer reads report and applies critical/major fixes (has context per vet-requirement pattern)

8. **Keep Step 0 (Complexity Triage) unchanged** - runs before phases

9. **Update Phase C.5**: Tail-call `/handoff --commit` (already exists)

**Expected Outcome**: Design skill restructured with outline-first workflow, documentation checkpoint, and research artifact persistence.

**Unexpected Result Handling**:
- If current step structure differs significantly: Review actual structure, map old → new carefully
- If plugin-related skill-loading directives already exist: Preserve and integrate with documentation checkpoint

**Error Conditions**:
- File not found → Escalate to sonnet (prerequisite validation failed)
- YAML frontmatter parse errors → Fix syntax
- Ambiguous section boundaries → Escalate to sonnet for clarification

**Validation**:
- All 8 phases/steps from old structure accounted for in new structure
- Documentation checkpoint includes all 5 levels
- Phase B includes termination condition
- Phase C.1 includes documentation perimeter section template

**Success Criteria**:
- File modified with three-phase structure
- Documentation checkpoint replaces Step 1 + Step 1.5
- Outline-first flow with escape hatch documented
- quiet-explore referenced instead of built-in Explore
- Documentation perimeter section included in design.md template

**Report Path**: `plans/design-workflow-enhancement/reports/step-3-restructure-design-skill.md`

---
