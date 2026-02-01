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

**Total Steps**: 4

**Execution Model**:
- Step 1: Sonnet (agent creation from spec)
- Step 2: Sonnet (vet-agent review, planner applies fixes)
- Step 3: Sonnet (skill edits with interpretation)
- Step 4: Haiku (symlink management and validation)

**Step Dependencies**:
- Steps 1-2: Sequential (review depends on creation)
- Step 3: Independent (no agent file dependency)
- Step 4: Depends on 1-3 (symlinks after all files exist)

**Error Escalation**:
- Sonnet → User: Missing files, structural misalignments, ambiguous guidance, unfixable agent spec issues
- Haiku → Sonnet: Symlink creation failures

**Report Locations**: `plans/design-workflow-enhancement/reports/step-{N}-*.md`

**Success Criteria**:
- All 4 files created/modified (1 agent, 3 skills)
- quiet-explore agent passes plugin-dev:agent-creator review
- Symlinks created in `.claude/agents/quiet-explore.md`
- `just dev` passes (formatting, validation)

**Prerequisites**:
- Design document exists (✓ verified: `plans/design-workflow-enhancement/design.md`)
- Target skill files exist (✓ verified via Glob):
  - `agent-core/skills/design/SKILL.md`
  - `agent-core/skills/plan-adhoc/SKILL.md`
  - `agent-core/skills/plan-tdd/SKILL.md`
- Agent baseline exists: `agent-core/agents/quiet-task.md`
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

**Objective**: Review and fix agent file using vet-agent

**Execution Model**: Sonnet (vet-agent review)

**Implementation**:

Delegate review to vet-agent:
```
Review agent-core/agents/quiet-explore.md for:
- YAML syntax correctness (frontmatter fields, multi-line description format)
- Description quality and clarity
- System prompt structure and completeness (all 7 directives from design)
- Tool list appropriateness
- Consistency with quiet-task baseline pattern

Write review report to plans/design-workflow-enhancement/reports/step-2-agent-review.md.
Return filepath only on success.
```

After receiving review, read report and apply all critical/major priority fixes to agent file.

**Expected Outcome**: Agent file reviewed and improved, report written

**Unexpected Result Handling**:
- If review identifies contradictory requirements in spec: Report to user with specific conflicts
- If git diff shows no changes after review but report lists issues: Verify report explains why no changes needed

**Error Conditions**:
- Agent file missing → Error: "Agent file not found, Step 1 may have failed"
- Review report not created → Escalate with error message from vet-agent

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

**Report Path**: `plans/design-workflow-enhancement/reports/step-2-agent-review.md` (created by vet-agent)

---

## Step 3: Update Skills

**Objective**: Update design skill (restructure) and plan skills (add documentation perimeter reading)

**Execution Model**: Sonnet (interprets design guidance into skill edits)

**Implementation**:

**3.1 - Update design skill** (`agent-core/skills/design/SKILL.md`):

**First:** Read full skill file to identify current section structure (numbered steps vs phases, exact headings).

From design "Step mapping" table (lines 68-79), restructure skill from current Steps 0-7 into Phases A-C:

**Changes needed**:
- Replace "### 1. Understand Request" + "### 1.5. Memory Discovery" (lines ~40-54) → Phase A.1 (documentation checkpoint using hierarchy from design lines 85-103)
- Replace "### 2. Explore Codebase" (lines ~56-60) → Phase A.2 (delegate to quiet-explore, specify report path)
- Replace "### 3. Research (if needed)" (lines ~62-64) → Phase A.3-4 (Context7 + web research, call directly from main session)
- Split "### 4. Create Design Document" (lines ~66-94) into:
  - Phase A.5 (outline) — new section for outline creation + presentation
  - Phase C.1 (full design) — move current Step 4 content here, add documentation perimeter requirement (design lines 104-126)
- Rename "### 5. Vet Design" (lines ~96-110) → Phase C.3 (general-purpose opus review - keep unchanged)
- Rename "### 6. Apply Fixes" (lines ~112-116) → Phase C.4 (keep unchanged)
- Rename "### 7. Handoff and Commit" (lines ~118-129) → Phase C.5 (keep unchanged)

**Phase B (new)**: Insert between Phase A and Phase C — iterative discussion section from design lines 53-59

**Preservation mapping**:
- "### 0. Complexity Triage" (lines ~20-36) → Keep as-is before Phase A
- Plugin-topic skill-loading directive (currently in Step 4 lines ~86-94) → Move to Phase A.5 (outline section)
- Tail-call to `/handoff --commit` (currently Step 7 lines ~120-127) → Becomes Phase C.5 (no change)

**3.2 - Update plan-adhoc skill** (`agent-core/skills/plan-adhoc/SKILL.md`):

Add "Read documentation perimeter" as first numbered item (item 0) within Point 0.5 section, before the existing "Discover relevant prior knowledge" item.

**Insertion point**: After "### Point 0.5: Discover Codebase Structure (REQUIRED)" heading (line ~95), before "**Before writing any runbook content:**"

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

**Insertion point**: After "### Phase 1: Intake (Tier 3 Only)" heading and "**Objective:** Load design and project conventions." (lines ~104-106), before "**Actions:**" section.

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

## Orchestrator Instructions

**Parallelization**:
- Steps 1-2: Must run sequentially (review depends on agent creation)
- Step 3: Can run in parallel with Steps 1-2 (no dependency on agent file)
- Step 4: Must run after all previous steps complete (needs all files + fixes applied)

**Stop conditions**:
- Any step reports error → stop, escalate to user
- Step 2 review identifies UNFIXABLE critical issues → stop, escalate

---

## Design Decisions

**Agent creation pattern**: Task agent creates from spec, vet-agent reviews, planner applies fixes. This follows standard review pattern for implementation artifacts (vet-requirement.md, learnings.md: model selection for design interpretation).

**No sequential dependency for Step 3**: Skills reference agents by name string. Agent file doesn't need to exist at skill-edit time, only at runtime after symlinks (design Runbook Guidance).

**Symlink step stays simple**: `just sync-to-parent` is a 2-line operation (cd + just). Combined with validation for efficiency (design Runbook Guidance line 247).

**Model selection**: Sonnet for Steps 1-3 (interprets spec/design guidance, applies review fixes), haiku for Step 4 (scripted operations). Rationale: learnings.md "model selection for interpreting design guidance" — sonnet interprets intent, haiku executes explicit commands.

---

## Dependencies

**Before This Runbook**:
- Design complete at `plans/design-workflow-enhancement/design.md`
- Agent-core and skill structure unchanged

**After This Runbook**:
- Design skill uses outline-first workflow
- quiet-explore agent available for use
- Plan skills consume documentation perimeter
- Ready for manual testing (run `/design` on test task)

---

## Notes

**Testing strategy** (from design):
- Manual: Run `/design` on test task, verify outline-first flow
- Verify quiet-explore writes report and returns filepath
- Verify Context7 direct calls + Write to report works
- Verify planner reads documentation perimeter section

**Out of scope** (deferred to future work):
- Session-log based capture of research artifacts
- Automated perimeter validation hooks
