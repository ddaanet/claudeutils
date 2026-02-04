---
name: design-workflow-enhancement
model: sonnet
---

# Design Workflow Enhancement Runbook

**Context**: Implement outline-first workflow for design skill with documentation checkpoint and quiet-explore agent

**Source**: Design Rev 2 at `plans/design-workflow-enhancement/design.md`

**Status**: Draft
**Created**: 2026-02-01

---

## Weak Orchestrator Metadata

**Total Steps**: 6

**Execution Model**:
- Step 1: Sonnet (agent creation from spec)
- Step 2: Sonnet (plugin-dev:agent-creator review + fix)
- Step 3: Sonnet (skill edits with interpretation)
- Step 4: Haiku (symlink management and validation)
- Step 5: Sonnet (design skill + design-vet-agent requirements extension)
- Step 6: Sonnet (plan skills + vet agents requirements validation)

**Step Dependencies**:
- Steps 1-2: Sequential (review depends on creation)
- Step 3: Can run parallel with 1-2 (no agent file dependency)
- Step 4: Depends on 1-3 (symlinks after all files exist)
- Steps 5-6: Can run parallel with each other and with 1-3 (no file dependencies); run Step 4 validation after all steps for comprehensive results

**Error Escalation**:
- Sonnet → User: Missing files, structural misalignments, ambiguous guidance, unfixable agent spec issues
- Haiku → Sonnet: Symlink creation failures

**Report Locations**: `plans/design-workflow-enhancement/reports/step-{N}-*.md`

**Success Criteria**:
- All 7 files created/modified:
  - `agent-core/agents/quiet-explore.md` (created)
  - `agent-core/skills/design/SKILL.md` (modified)
  - `agent-core/skills/plan-adhoc/SKILL.md` (modified)
  - `agent-core/skills/plan-tdd/SKILL.md` (modified)
  - `agent-core/agents/design-vet-agent.md` (modified)
  - `agent-core/agents/vet-agent.md` (modified)
  - `agent-core/agents/vet-fix-agent.md` (modified)
- quiet-explore agent passes plugin-dev:agent-creator review
- Symlinks created in `.claude/agents/quiet-explore.md`
- design-vet-agent includes requirements alignment checks (section 4.5)
- vet-agent and vet-fix-agent include conditional requirements validation
- plan-adhoc and plan-tdd include requirements passthrough
- `just dev` passes (formatting, validation)

**Prerequisites**:
- Design document exists (✓ verified: `plans/design-workflow-enhancement/design.md`)
- Target skill files exist (✓ verified via Glob):
  - `agent-core/skills/design/SKILL.md`
  - `agent-core/skills/plan-adhoc/SKILL.md`
  - `agent-core/skills/plan-tdd/SKILL.md`
- Agent files exist:
  - `agent-core/agents/quiet-task.md` (baseline for quiet-explore)
  - `agent-core/agents/design-vet-agent.md` (modified in Step 5)
  - `agent-core/agents/vet-agent.md` (modified in Step 6)
  - `agent-core/agents/vet-fix-agent.md` (modified in Step 6)
- Symlink recipe exists: `just sync-to-parent` in agent-core/

---

## Common Context

**Design location**: `plans/design-workflow-enhancement/design.md`

**Key constraints from design**:
- Outline-first workflow: Phase A (research + outline) → Phase B (discussion) → Phase C (generate design)
- Documentation checkpoint replaces Steps 1 + 1.5 (understand + memory discovery)
- quiet-explore writes to files (quiet task pattern), returns filepath only
- Context7 calls happen directly from main session (MCP tools unavailable in sub-agents)
- Documentation perimeter section in design output guides planner reading

**Agent spec location**: Design section "quiet-explore Agent" (lines 128-167)

**Project conventions**:
- Agent files: `agent-core/agents/*.md` with YAML frontmatter
- Skill files: `agent-core/skills/*/SKILL.md` with YAML frontmatter
- Symlinks: Created via `just sync-to-parent` (requires `dangerouslyDisableSandbox: true`)
- Multi-line YAML descriptions use `|` syntax (prevents parse errors)

**Stop conditions (all steps)**:
- File not found at expected path
- Structural mismatch (e.g., expected section missing)
- YAML parse errors after edits
- Validation failures after changes

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

## Step 2: Review quiet-explore Agent

**Objective**: Review and fix agent file using plugin-dev:agent-creator

**Execution Model**: Sonnet (agent-creator review)

**Subagent Type**: `plugin-dev:agent-creator`

**Implementation**:

Delegate review to plugin-dev:agent-creator:
```
Review the existing agent file at agent-core/agents/quiet-explore.md for:
- YAML syntax correctness (frontmatter fields, multi-line description format)
- Description quality and clarity
- System prompt structure and completeness (all 7 directives from design)
- Tool list appropriateness
- Consistency with quiet-task baseline pattern

Write review report to plans/design-workflow-enhancement/reports/step-2-agent-review.md.
Apply critical/major fixes directly to the agent file.
Return filepath only on success.
```

**Rationale**: Agent files should be reviewed by agent-creator (agent specialist), not vet-agent (code quality specialist). Design Decision 8 specifies this pattern.

**Expected Outcome**: Agent file reviewed and improved, report written

**Unexpected Result Handling**:
- If review identifies contradictory requirements in spec: Report to user with specific conflicts
- If git diff shows no changes after review but report lists issues: Verify report explains why no changes needed

**Error Conditions**:
- Agent file missing → Error: "Agent file not found, Step 1 may have failed"
- Review report not created → Escalate with error message from agent-creator

**Validation**:
- Review report exists at expected path
- Agent file still valid YAML after fixes
- All critical/major issues from report addressed
- Compare before/after using git diff (verify improvements made or report explains no-change rationale)

**Success Criteria**:
- Review complete with report written
- All critical/major issues fixed
- Agent file passes YAML parse
- Improvements documented in git diff or review report

**Report Path**: `plans/design-workflow-enhancement/reports/step-2-agent-review.md` (created by agent-creator)

---

## Step 3: Update Skills

**Objective**: Update design skill (restructure) and plan skills (add documentation perimeter reading)

**Execution Model**: Sonnet (interprets design guidance into skill edits)

**Implementation**:

**3.1 - Update design skill** (`agent-core/skills/design/SKILL.md`):

**First:** Read full skill file to identify current section structure (numbered steps vs phases, exact headings).

From design "Step mapping" table (section "Architecture > Design Skill: Three-Phase Workflow"), restructure skill from current Steps 0-7 into Phases A-C:

**Changes needed**:
- Replace "### 1. Understand Request" + "### 1.5. Memory Discovery" → Phase A.1 (documentation checkpoint using hierarchy from design "Documentation Checkpoint" section)
- Replace "### 2. Explore Codebase" → Phase A.2 (delegate to quiet-explore, specify report path)
- Replace "### 3. Research (if needed)" → Phase A.3-4 (Context7 + web research, call directly from main session)
- Split "### 4. Create Design Document" into:
  - Phase A.5 (outline) — new section for outline creation + presentation
  - Phase C.1 (full design) — move current Step 4 content here, add documentation perimeter requirement (design "Documentation Perimeter in Design Output" section)
- Rename "### 5. Vet Design" → Phase C.3 (design-vet-agent review - opus model for architectural analysis)
- Rename "### 6. Apply Fixes" → Phase C.4 (keep unchanged)
- Rename "### 7. Handoff and Commit" → Phase C.5 (keep unchanged)

**Phase B (new)**: Insert between Phase A and Phase C — iterative discussion section from design "Phase B: Iterative Discussion" section

**Preservation mapping**:
- "### 0. Complexity Triage" → Keep as-is before Phase A
- Plugin-topic skill-loading directive (currently in Step 4 "Create Design Document") → Move to Phase A.5 (outline section)
- Tail-call to `/handoff --commit` (currently Step 7) → Becomes Phase C.5 (no change)

**3.2 - Update plan-adhoc skill** (`agent-core/skills/plan-adhoc/SKILL.md`):

Add "Read documentation perimeter" as first numbered item (item 0) within Point 0.5 section, before the existing "Discover relevant prior knowledge" item.

**Insertion point**: After "### Point 0.5: Discover Codebase Structure (REQUIRED)" heading, before "**Before writing any runbook content:**"

**New content**:
```markdown
**0. Read documentation perimeter (if present):**

If design document includes "Documentation Perimeter" section:
- Read all files listed under "Required reading"
- Note Context7 references (may need additional queries)
- Factor knowledge into step design

This provides designer's recommended context. Still perform discovery steps 1-2 below for path verification and memory-index scan.
```

**After insertion**: Renumber existing items (currently 1-2) to (1-2) — no change needed, just verify they remain after new item 0.

**3.3 - Update plan-tdd skill** (`agent-core/skills/plan-tdd/SKILL.md`):

Add documentation perimeter reading to Phase 1 as Step 0, before existing actions.

**Insertion point**: After "### Phase 1: Intake (Tier 3 Only)" heading and "**Objective:** Load design and project conventions.", before "**Actions:**" section.

**New content** (insert as first numbered item in Actions list, before "1. **Determine design path:**"):
```markdown
0. **Read documentation perimeter (if present):**
   - If design includes "Documentation Perimeter" section, read all listed files under "Required reading"
   - Note Context7 references for potential additional queries
   - This provides designer's recommended context before discovery

```

**After insertion**: Existing actions 1-4 remain numbered as-is (they're already correctly numbered).

**Expected Outcome**: design skill restructured into 3-phase workflow, plan-adhoc and plan-tdd updated with documentation perimeter reading

**Unexpected Result Handling**:
- If skill structure doesn't match expected sections: Read full skill file to identify actual structure, then apply changes
- If unclear how to integrate guidance: Report ambiguity to user

**Error Conditions**:
- Skill file missing → Error with specific path
- Section not found where expected → Read file, report actual structure

**Validation**:
- All 3 skill files modified
- design skill has Phases A-C structure
- plan-adhoc has documentation perimeter reading in Point 0.5
- plan-tdd has documentation perimeter reading in Phase 1
- YAML frontmatter still valid after edits

**Success Criteria**:
- 3 skill files updated
- Structural changes preserve existing logic flow
- No YAML parse errors

**Report Path**: `plans/design-workflow-enhancement/reports/step-3-skill-updates.md`

---

## Step 4: Create Symlinks and Validate

**Objective**: Create symlinks for agent, run validation

**Execution Model**: Haiku (simple operations)

**Implementation**:

```bash
# Navigate to agent-core and create symlinks
cd /Users/david/code/claudeutils/agent-core && just sync-to-parent

# Verify symlink created
ls -la /Users/david/code/claudeutils/.claude/agents/quiet-explore.md

# Run validation
cd /Users/david/code/claudeutils && just dev
```

**Expected Outcome**: Symlink exists, validation passes

**Unexpected Result Handling**:
- If symlink creation fails: Check permissions, escalate to sonnet
- If validation fails: Report specific failures (formatting, linting)

**Error Conditions**:
- `just sync-to-parent` fails → Escalate with error output
- Symlink not created → Verify agent file exists, escalate if so
- `just dev` fails → Report failures for fixing

**Validation**:
- Symlink exists and points to `agent-core/agents/quiet-explore.md`
- `just dev` exits with code 0

**Success Criteria**:
- Symlink verified
- All checks pass

**Report Path**: `plans/design-workflow-enhancement/reports/step-4-symlinks-validation.md`

---

## Step 5: Extend Design Skill and Design-Vet-Agent for Requirements

**Objective**: Add requirements checkpoint (A.0) to design skill and requirements alignment checks to design-vet-agent

**Execution Model**: Sonnet (interprets design guidance into skill/agent edits)

**Implementation**:

**5.1 - Update design skill** (`agent-core/skills/design/SKILL.md`):
- Add Phase A.0 (Requirements Checkpoint) before A.1
- Update Phase C.1 to include requirements section guidance with traceability format

**5.2 - Update design-vet-agent** (`agent-core/agents/design-vet-agent.md`):
- Add requirements alignment checks to "Analyze Design" section
- Add section 4.5 "Validate Requirements Alignment"
- Update review report template with "Requirements Alignment" section

**Expected Outcome**: Design skill has A.0 requirements checkpoint, design-vet-agent validates requirements alignment

**Validation**:
- Both files modified
- Phase A.0 appears before A.1
- design-vet-agent has section 4.5
- YAML frontmatter valid

**Report Path**: `plans/design-workflow-enhancement/reports/step-5-requirements-design.md`

---

## Step 6: Extend Plan Skills and Vet Agents for Requirements Validation

**Objective**: Add requirements passthrough to plan skills and conditional requirements validation to vet agents

**Execution Model**: Sonnet (interprets design guidance into skill/agent edits)

**Implementation**:

**6.1 - Update plan-adhoc skill** (`agent-core/skills/plan-adhoc/SKILL.md`):
- Extend Point 0.5 item 0 to read requirements from design
- Add requirements to Common Context template
- Update vet checkpoint prompt to include requirements validation

**6.2 - Update plan-tdd skill** (`agent-core/skills/plan-tdd/SKILL.md`):
- Same changes as plan-adhoc (Phase 1 intake, Common Context, checkpoints)

**6.3 - Update vet-agent** (`agent-core/agents/vet-agent.md`):
- Add conditional requirements validation section (triggers when context provided)
- Add "Requirements Validation" section to review report template

**6.4 - Update vet-fix-agent** (`agent-core/agents/vet-fix-agent.md`):
- Same changes as vet-agent

**Expected Outcome**: Plan skills passthrough requirements, vet agents conditionally validate against requirements

**Validation**:
- All 4 files modified
- Requirements reading in both plan skills
- Conditional requirements validation in both vet agents
- Backward compatible (no requirements context = no validation)
- YAML frontmatter valid

**Report Path**: `plans/design-workflow-enhancement/reports/step-6-requirements-validation.md`

---

## Orchestrator Instructions

**Parallelization**:
- Steps 1-2: Must run sequentially (review depends on agent creation)
- Step 3: Can run in parallel with Steps 1-2 (no dependency on agent file)
- Steps 5-6: Can run in parallel with each other and with Steps 1-3 (no file dependencies)
- Step 4: Must run after all other steps complete (symlinks + comprehensive validation)

**Stop conditions**:
- Any step reports error → stop, escalate to user
- Step 2 review identifies UNFIXABLE critical issues → stop, escalate

---

## Design Decisions

**Agent creation pattern**: Task agent creates from spec, plugin-dev:agent-creator reviews and applies fixes. This follows design Decision 8 — agent-creator is the specialist for agent files (YAML syntax, description quality, prompt structure).

**No sequential dependency for Step 3**: Skills reference agents by name string. Agent file doesn't need to exist at skill-edit time, only at runtime after symlinks (design Runbook Guidance).

**Symlink step stays simple**: `just sync-to-parent` is a 2-line operation (cd + just). Combined with validation for efficiency (design Runbook Guidance line 247).

**Model selection**: Sonnet for Steps 1-3 (interprets spec/design guidance, applies review fixes), haiku for Step 4 (scripted operations). Rationale: learnings.md "model selection for interpreting design guidance" — sonnet interprets intent, haiku executes explicit commands.

---

## Dependencies

**Before This Runbook**:
- Design complete at `plans/design-workflow-enhancement/design.md` (including Requirements Alignment Validation extension)
- Agent-core and skill structure unchanged

**After This Runbook**:
- Design skill uses outline-first workflow with requirements checkpoint (A.0)
- quiet-explore agent available for use
- Plan skills consume documentation perimeter and requirements
- Vet agents conditionally validate against requirements
- design-vet-agent validates requirements alignment in designs
- Ready for manual testing (run `/design` on test task with requirements.md)

---

## Notes

**Testing strategy** (from design):
- Manual: Run `/design` on test task with requirements.md, verify outline-first flow
- Verify quiet-explore writes report and returns filepath
- Verify Context7 direct calls + Write to report works
- Verify planner reads documentation perimeter section
- Verify design-vet-agent produces requirements alignment section in review
- Verify vet-agent validates against requirements when context provided

**Out of scope** (deferred to future work):
- Session-log based capture of research artifacts
- Automated perimeter validation hooks
- Requirements coverage metrics
