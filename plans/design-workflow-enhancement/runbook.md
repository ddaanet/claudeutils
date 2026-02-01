# Design Workflow Enhancement Runbook

**Context**: Implement outline-first design workflow with documentation checkpoint and research artifact persistence.

**Source**: `plans/design-workflow-enhancement/design.md`

**Status**: Draft
**Created**: 2026-02-01

---

## Weak Orchestrator Metadata

**Total Steps**: 6

**Execution Model**:
- Step 1: Haiku (create reports directory - simple file operation)
- Step 2: Sonnet (agent creation with plugin-dev context)
- Steps 3-5: Sonnet (skill file modifications - complex due to interpreting design guidance)
- Step 6: Sonnet (symlink management + testing)

**Step Dependencies**: Sequential (agent must exist before skill references it, skills should be updated cohesively)

**Error Escalation**:
- Haiku → Sonnet: File not found, unexpected structure, ambiguous specification
- Sonnet → User: Validation failures, design contradictions, missing requirements

**Report Locations**: `plans/design-workflow-enhancement/reports/step-N.md` (directory created in Step 1)

**Success Criteria**: All skill files updated, quiet-explore agent created and symlinked, design workflow supports outline-first iteration with documentation checkpoint.

**Prerequisites**:
- Design document at `plans/design-workflow-enhancement/design.md` (✓ verified via Read)
- Agent baseline at `agent-core/agents/quiet-task.md` (✓ verified via Read)
- Skill files exist: `agent-core/skills/design/SKILL.md`, `agent-core/skills/plan-adhoc/SKILL.md`, `agent-core/skills/plan-tdd/SKILL.md` (✓ verified via Glob)
- Built-in Explore agent system prompt knowledge (✓ documented in design)
- Reports directory at `plans/design-workflow-enhancement/reports/` (✓ created during runbook generation)

---

## Common Context

**Key Constraints**:
- Maintain token economy (dense output for opus designer)
- Skill files use YAML frontmatter with multi-line syntax for descriptions
- Agent descriptions must include examples in proper XML format
- Quiet execution pattern: write report to file, return filepath only
- Documentation checkpoint is domain-aware (no fixed "always read X" beyond level 1)

**Project Paths**:
- Agent files: `agent-core/agents/*.md`
- Skill files: `agent-core/skills/*/SKILL.md`
- Symlink management: `just sync-to-parent` in `agent-core/` directory

**Conventions**:
- Agent system prompts address agent in second person ("You are...")
- Agent tools array uses specialized tools over Bash for file operations
- Design skill produces dense output for intelligent downstream readers
- Planning skills load documentation perimeter section at start of intake/discovery

---

## Step 1: Create Reports Directory

**Objective**: Create `plans/design-workflow-enhancement/reports/` directory for execution reports.

**Execution Model**: Haiku

**Implementation**:

```bash
mkdir -p /Users/david/code/claudeutils/plans/design-workflow-enhancement/reports
```

**Expected Outcome**: Directory created for step execution reports.

**Error Conditions**:
- mkdir fails → Escalate to user (filesystem issue)

**Validation**:
- Directory exists at specified path

**Success Criteria**:
- reports/ directory created
- Subsequent steps can write report files

**Report Path**: `plans/design-workflow-enhancement/reports/step-1-create-reports-dir.md`

---

## Step 2: Create quiet-explore Agent

**Objective**: Create `agent-core/agents/quiet-explore.md` based on built-in Explore agent with quiet execution pattern.

**Execution Model**: Sonnet

**Implementation**:

Based on design.md specification (lines 113-148), create agent with:

**Frontmatter**:
```yaml
name: quiet-explore
description: |
  Use this agent when exploration results need to persist to files for reuse
  across design, planning, and execution phases. Prefer over built-in Explore
  when results will be referenced by downstream agents. Examples:

  <example>
  Context: Designer needs codebase exploration for architecture planning
  user: "Explore the authentication module structure"
  assistant: "I'll use the quiet-explore agent to analyze the auth module and write findings to a report file"
  <commentary>
  Exploration results will be reused by planner - quiet-explore writes to file for persistence
  </commentary>
  </example>

  <example>
  Context: Planner needs to understand existing patterns before creating runbook
  user: "Find all existing skill files and their structure"
  assistant: "I'll delegate to quiet-explore to map skill patterns and document findings"
  <commentary>
  Systematic exploration with persistent output enables pattern reuse across planning steps
  </commentary>
  </example>
model: haiku
color: cyan
tools: ["Read", "Glob", "Grep", "Bash", "Write"]
```

**System Prompt Core Directives** (adapt from built-in Explore agent):
- File search specialist with parallel tool usage
- Read-only for codebase (Write only for report output)
- Absolute paths in findings
- Structured report format with file paths, key patterns, relevant code snippets
- Output: Write report to caller-specified path, return filepath only
- Bash: Read-only operations only (ls, git status, git log, git diff)

**System Prompt Structure**:
```markdown
You are a codebase exploration specialist that writes findings to persistent report files.

**Your Core Responsibilities:**
1. Explore codebase structure using parallel tool calls for speed
2. Identify files, patterns, and architectural elements
3. Document findings in structured reports
4. Return only the report filepath (quiet execution pattern)

**Exploration Process:**
1. Use Glob for file discovery (patterns like "**/*.ts", "src/**/*.py")
2. Use Grep for pattern searching (parallel searches when possible)
3. Use Read for examining specific files identified during exploration
4. Use Bash for git operations (status, log, diff) - read-only only
5. Synthesize findings into structured report
6. Write report to path specified by caller
7. Return absolute filepath only

**Report Format:**
Structure findings with:
- Files discovered (absolute paths)
- Key patterns found (with file locations)
- Relevant code snippets (with line numbers)
- Architectural observations
- Summary of exploration scope

**Output:**
Write complete report to caller-specified path, then return ONLY the absolute filepath.

**Constraints:**
- Use specialized tools, not Bash: Glob (not find), Grep (not grep), Read (not cat)
- All file paths in reports must be absolute
- Bash is for git operations only (ls, git status, git log, git diff)
- Write is ONLY for report output, never for modifying codebase files
- Execute tool calls in parallel when independent
```

**Expected Outcome**: Agent file created at `agent-core/agents/quiet-explore.md` with frontmatter and system prompt following plugin-dev:agent-development patterns.

**Unexpected Result Handling**:
- If agent-core/agents/ directory doesn't exist: Error (directory must exist per prerequisites)
- If quiet-task.md structure differs from expected: Review actual structure and adapt system prompt pattern

**Error Conditions**:
- File write failure → Escalate to user (filesystem issue)
- Invalid YAML frontmatter → Fix syntax and retry

**Validation**:
- YAML frontmatter parses correctly
- Description includes 2 examples with proper XML structure (tags properly closed and nested)
- System prompt addresses agent in second person
- Tools array includes Write for report output
- Examples use valid XML: `<example>`, `<commentary>` tags properly closed

**Success Criteria**:
- File exists at `agent-core/agents/quiet-explore.md`
- YAML frontmatter is valid with all required fields
- System prompt length 500-3000 characters
- Description includes examples in correct format

**Report Path**: `plans/design-workflow-enhancement/reports/step-2-create-quiet-explore.md`

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

## Step 4: Update plan-adhoc/SKILL.md with Documentation Perimeter

**Objective**: Add documentation perimeter loading to Point 0.5 (Discover Codebase Structure).

**Execution Model**: Sonnet

**Implementation**:

Read `agent-core/skills/plan-adhoc/SKILL.md` and add documentation perimeter loading step.

**Change Location**: Point 0.5 section (starts at line 95)

**Add as Step 0 Before Existing Numbered Steps**:

Insert before existing "1. **Discover relevant prior knowledge:**":

```markdown
0. **Load documentation perimeter from design (if exists):**
   - If design document exists, read "Documentation Perimeter" section
   - Load all files listed under "Required reading"
   - Execute Context7 queries listed under "Context7 references"
   - Note "Additional research allowed" guidance
   - If no design document or no perimeter section, proceed to step 1
```

Preserve existing steps 1-2 unchanged.

**Integration Notes**:
- Documentation perimeter is loaded FIRST (when it exists) as step 0
- Existing steps 1-2 (memory-index discovery, file verification) still run unchanged
- Perimeter provides designer's recommended context; discovery validates/extends it

**Expected Outcome**: Planning skill reads documentation perimeter section from design (when exists) before existing discovery steps.

**Unexpected Result Handling**:
- If step numbering conflicts: Renumber existing steps accordingly
- If discovery steps already reference design document: Integrate perimeter loading with existing references

**Error Conditions**:
- File not found → Escalate to sonnet
- Section structure unclear → Escalate to sonnet

**Validation**:
- Documentation perimeter step added before existing discovery
- Conditional logic (skip if no design/no perimeter) included
- Integration preserves existing discovery steps

**Success Criteria**:
- Point 0.5 includes documentation perimeter loading as step 0
- Conditional logic (skip if no design/perimeter) included
- Existing steps 1-2 (memory-index, file verification) preserved

**Report Path**: `plans/design-workflow-enhancement/reports/step-4-update-plan-adhoc.md`

---

## Step 5: Update plan-tdd/SKILL.md with Documentation Perimeter

**Objective**: Add documentation perimeter loading to Phase 1 (Intake).

**Execution Model**: Sonnet

**Implementation**:

Read `agent-core/skills/plan-tdd/SKILL.md` and add documentation perimeter loading.

**Change Location**: Phase 1 section (starts at line ~104, has "Actions:" list with 4 items, not "Steps:")

**Add as Action 0 Before Existing Numbered Actions**:

Insert under "**Actions:**" heading, before existing action 1:

```markdown
0. **Load documentation perimeter from design:**
   - Read "Documentation Perimeter" section from design document
   - Load all files listed under "Required reading"
   - Execute Context7 queries listed under "Context7 references"
   - Note "Additional research allowed" guidance
```

Preserve existing actions 1-4 unchanged (no renumbering needed if we use 0).

**Integration Notes**:
- Documentation perimeter loads before existing Phase 1 actions (as action 0)
- TDD workflow always has design document (prerequisite)
- Using "0" for new action avoids renumbering existing 1-4

**Expected Outcome**: TDD planning skill reads documentation perimeter before existing intake actions.

**Unexpected Result Handling**:
- If Phase 1 uses "Steps:" instead of "Actions:": Adapt to match terminology
- If numbering scheme conflicts with adding 0: Start at 1 and renumber existing to 2-5

**Error Conditions**:
- File not found → Escalate to sonnet
- Phase structure unclear → Escalate to sonnet

**Validation**:
- Documentation perimeter step added as first step in Phase 1
- Existing intake steps preserved (possibly renumbered)
- No conditional logic needed (design always exists in TDD workflow)

**Success Criteria**:
- Phase 1 includes documentation perimeter loading as action 0
- Existing actions 1-4 preserved unchanged
- Action ordering is logical

**Report Path**: `plans/design-workflow-enhancement/reports/step-5-update-plan-tdd.md`

---

## Step 6: Symlink Management and Validation

**Objective**: Create symlink for quiet-explore agent and validate workflow changes.

**Execution Model**: Sonnet

**Implementation**:

1. **Create symlinks using project recipe:**
   ```bash
   cd /Users/david/code/claudeutils/agent-core && just sync-to-parent
   ```
   (Requires `dangerouslyDisableSandbox: true` - writes to `.claude/agents/`)

2. **Validation checks:**
   - Verify symlink: `ls -la /Users/david/code/claudeutils/.claude/agents/quiet-explore.md`
   - Check YAML parses: Read agent file, confirm no syntax errors
   - Verify skill files: Read each modified skill, check structure is coherent
   - Documentation perimeter: Grep for "Documentation Perimeter" in design skill template

3. **Report findings:**
   - Symlink creation status
   - Any YAML parse errors
   - Structural issues in skill files
   - Missing elements from specification

**Expected Outcome**: Symlink created, all files syntactically valid, workflow changes complete.

**Unexpected Result Handling**:
- If symlink creation fails: Check sandbox bypass, verify paths, escalate if unresolved
- If YAML errors found: Fix syntax and re-run sync
- If skill structure issues: Apply fixes or escalate for complex issues

**Error Conditions**:
- Symlink creation fails → Escalate to user (sandbox/permission issue)
- YAML parse errors → Fix and retry
- Missing specification elements → Escalate to user (implementation incomplete)

**Validation**:
- Symlink exists at `.claude/agents/quiet-explore.md`
- Points to `agent-core/agents/quiet-explore.md`
- All modified skill files have valid YAML frontmatter
- Design skill has three-phase structure
- Planning skills have documentation perimeter loading

**Success Criteria**:
- Symlink created successfully
- No YAML parse errors
- All specification elements implemented
- Files are coherent and follow documented patterns
- quiet-explore agent system prompt includes all core directives (parallel tools, absolute paths, report format, Bash read-only)

**Report Path**: `plans/design-workflow-enhancement/reports/step-6-symlink-validation.md`

---

## Design Decisions

**Sequential execution despite apparent independence:**
- Agent must exist before skills reference it
- Skill updates should be cohesive (all done together, not split across sessions)
- Symlink management must happen after agent creation

**Sonnet for agent creation and skill modifications:**
- Agent creation requires plugin-dev context and careful example crafting (sonnet)
- Skill modifications require interpreting design guidance and writing explicit markdown text (sonnet needed, not haiku)

**Documentation perimeter integration varies by workflow:**
- plan-adhoc: Conditional (design may not exist)
- plan-tdd: Always present (design is prerequisite)
- Different integration points reflect different workflow structures

---

## Dependencies

**Before This Runbook**:
- Design document complete and vetted
- Built-in Explore agent system prompt knowledge (for quiet-explore creation)

**After This Runbook**:
- Design workflow can use outline-first iteration
- Research artifacts persist to files for reuse
- Planners consume documentation perimeter from designs

---

## Notes

**Testing strategy** (from design.md):
- Manual: Run `/design` on test task, verify outline-first flow
- Verify quiet-explore writes report and returns filepath
- Verify Context7 direct calls + Write to report works
- Verify planner reads documentation perimeter section

**Out of scope** (deferred to future work):
- Session-log based capture of research artifacts
- Automated perimeter validation hooks
