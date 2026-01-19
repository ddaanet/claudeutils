# Phase 1 Execution Plan - Script Implementation and Baseline Rename

**Context**: Implement prepare-runbook.py script and rename task-execute to quiet-task per oneshot workflow design.

**Source**: `plans/oneshot-workflow/design.md` (Phase 1)
**Design**: `plans/oneshot-workflow/design.md`

**Status**: Revision 1 (ready for split)
**Created**: 2026-01-19
**Reviewed**: 2026-01-19 (sonnet, NEEDS_REVISION)
**Revised**: 2026-01-19 (addressed 3 critical + 3 major issues)

---

## Weak Orchestrator Metadata

**Total Steps**: 4

**Execution Model**:
- Step 1.1: Haiku (simple directory creation)
- Step 1.2: Haiku (file move/rename with reference updates)
- Step 1.3: Sonnet (Python script implementation with complex logic)
- Step 1.4: Haiku (test execution and verification)

**Step Dependencies**: Sequential (1.1 → 1.2 → 1.3 → 1.4)

**Error Escalation**:
- Haiku → Sonnet: Unexpected file states, permission errors, script execution failures
- Sonnet → User: Design decisions needed, script architecture changes required

**Report Locations**:
- Execution logs: `plans/oneshot-workflow/reports/phase1-step{N}-execution.md`

**Success Criteria**:
- Step 1.1: Directories created at expected paths
- Step 1.2: File renamed and moved, all references updated, no broken links
- Step 1.3: Script created with all required functionality, passes validation checks
- Step 1.4: Script successfully processes test runbook, creates expected outputs
- All execution reports written to expected paths
- No blocking errors

**Prerequisites**:
- agent-core repo exists at /Users/david/code/agent-core (✓ verified)
- claudeutils repo at /Users/david/code/claudeutils (✓ verified)
- task-execute.md exists at .claude/agents/task-execute.md (✓ verified)
- Test runbook exists at plans/unification/phase2-execution-plan.md (✓ verified)
- Python 3 available with stdlib modules (re, pathlib, argparse)

---

## Common Context

### Script Specification

**Script name**: `prepare-runbook.py`
**Location**: `agent-core/bin/prepare-runbook.py`
**Language**: Python 3, stdlib only (re, pathlib, argparse)

**Purpose**: Transform runbook markdown → execution artifacts (plan-specific agent, step files, orchestrator plan)

**Inputs**:
- Runbook markdown file with:
  - Optional YAML frontmatter (name, model)
  - Optional "Common Context" section
  - Required "Step N:" or "Step N.M:" sections
  - Optional "Orchestrator Instructions" section

**Outputs**:
1. **Plan-specific agent**: `.claude/agents/<runbook-name>-task.md`
   - Baseline quiet-task.md content + appended common context
2. **Step files**: `plans/<runbook-name>/steps/step-N.md` or `step-N-M.md`
   - Individual step instructions
3. **Orchestrator plan**: `plans/<runbook-name>/orchestrator-plan.md`
   - Orchestrator instructions (or default if not provided)

**Validation Requirements**:
- MUST fail on:
  - Missing baseline agent (agent-core/agents/quiet-task.md)
  - No step sections found
  - Duplicate step numbers
  - Non-writable output directories
- SHOULD warn (not fail):
  - Existing artifacts (overwriting is normal)
  - Missing optional sections

**Interface**:
```bash
prepare-runbook.py <runbook-file.md>
# Derives output paths from runbook location and name
```

**Example**:
```bash
prepare-runbook.py plans/foo/runbook.md
# Creates:
#   .claude/agents/foo-task.md
#   plans/foo/steps/step-*.md
#   plans/foo/orchestrator-plan.md
```

**Composition Strategy**: Simple append with separator
```markdown
[Full quiet-task.md content]

---
# Runbook-Specific Context

[Common context section from runbook]
```

**Frontmatter Parsing** (stdlib only):
```python
def parse_frontmatter(content):
    if not content.startswith('---'):
        return {}, content
    end = content.index('---', 3)
    meta = {}
    for line in content[3:end].strip().split('\n'):
        key, _, value = line.partition(':')
        meta[key.strip()] = value.strip()
    return meta, content[end+3:].lstrip()
```

### Baseline Agent Rename

**Current**: `.claude/agents/task-execute.md` (local to claudeutils)
**Target**: `agent-core/agents/quiet-task.md` (reusable baseline)

**Rationale**:
- "task-execute" conflicts with Task tool in Claude Code
- "quiet-task" emphasizes quiet execution pattern
- Move to agent-core makes it reusable across projects

**References to update**:
- Documentation in CLAUDE.md
- References in context.md
- References in design documents
- Any existing runbooks or scripts

### File Structure Changes

**New directories**:
- `agent-core/agents/` - Baseline agents (quiet-task.md)
- `agent-core/bin/` - Reusable scripts (prepare-runbook.py)

**Existing references**:
- `build-plan-agent.sh` at plans/unification/ (hardcoded path to baseline)
- Any documentation referencing task-execute

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

## Step 1.2: Move and Rename Baseline Agent

**Objective**: Move task-execute.md to agent-core/agents/quiet-task.md and update references

**Script Evaluation**: Small script (file copy + reference updates, ≤25 lines for move, prose for reference updates)

**Execution Model**: Haiku

**Implementation**:

**Part A: Copy file to new location**
```bash
#!/usr/bin/env bash
# Copy task-execute.md to agent-core/agents/quiet-task.md

SOURCE="/Users/david/code/claudeutils/.claude/agents/task-execute.md"
TARGET="/Users/david/code/agent-core/agents/quiet-task.md"

# Verify source exists
if [ ! -f "$SOURCE" ]; then
    echo "ERROR: Source file not found: $SOURCE" >&2
    exit 1
fi

# Copy to target
cp "$SOURCE" "$TARGET"

# Verify copy
if [ -f "$TARGET" ]; then
    echo "SUCCESS: Copied to $TARGET"
    echo "File size: $(wc -c < "$TARGET") bytes"
else
    echo "ERROR: Copy failed" >&2
    exit 1
fi
```

**Part B: Update frontmatter in new file**

Using Edit tool:
1. Read `/Users/david/code/agent-core/agents/quiet-task.md`
2. Edit frontmatter:
   - Change `name: task-execute` → `name: quiet-task`
   - Update `description:` to reference quiet execution pattern

**Part C: Update references**

Search for references to update (using Grep tool):

**Verification: Search entire repository**
```bash
# Search entire claudeutils repo for task-execute references
cd /Users/david/code/claudeutils
rg "task-execute" --type md --files-with-matches
```

If files found beyond the 4 known locations below, document in report and escalate to sonnet.

**Known locations to update**:
- `/Users/david/code/claudeutils/CLAUDE.md`
- `/Users/david/code/claudeutils/agents/context.md`
- `/Users/david/code/claudeutils/plans/unification/build-plan-agent.sh`
- `/Users/david/code/claudeutils/plans/oneshot-workflow/design.md`

Update each reference:
- Documentation: Change "task-execute" → "quiet-task"
- Paths: Update to `/Users/david/code/agent-core/agents/quiet-task.md`

**Part D: Keep original for compatibility**

Leave `.claude/agents/task-execute.md` in place for now (removal in Phase 4 cleanup).

**Expected Outcome**: File copied, frontmatter updated, references updated

**Unexpected Result Handling**:
- If source file missing: Report error and escalate
- If references found in unexpected locations: Document in report, proceed with known updates

**Error Conditions**:
- Source file not found → Report error, escalate to sonnet
- Permission denied → Report error, escalate to sonnet
- Grep finds references in unexpected files → Document in report, escalate to sonnet

**Validation**:
- New file exists at target location
- Frontmatter updated correctly
- All known references updated
- Original file still exists

**Success Criteria**:
- `agent-core/agents/quiet-task.md` exists with updated frontmatter
- References in known files updated
- No broken references to old path in critical files

**Report Path**: `plans/oneshot-workflow/reports/phase1-step2-execution.md`

---

## Step 1.3: Implement prepare-runbook.py Script

**Objective**: Create prepare-runbook.py script with full functionality per specification

**Script Evaluation**: Large/complex (>100 lines, multiple functions, validation logic) - PROSE DESCRIPTION

**Execution Model**: Sonnet

**Implementation**:

Create `/Users/david/code/agent-core/bin/prepare-runbook.py` with the following structure:

### Main Components

**1. Argument Parsing**
- Accept single argument: runbook file path
- Validate file exists and is readable
- Derive output paths from runbook location and name

**2. Frontmatter Parsing**
- Use stdlib approach (no pyyaml dependency)
- Extract name and model from YAML frontmatter
- Default: name from filename, model = sonnet

**3. Section Extraction**
- Parse runbook content into sections:
  - Common Context (optional)
  - Steps (required, format: "## Step N:" or "## Step N.M:")
  - Orchestrator Instructions (optional)
- Validate step numbering (no duplicates)
- Preserve section content verbatim

**Section boundary detection**:
- Common Context: `## Common Context` (H2) to next H2 heading or Steps
- Steps: Each `## Step N:` or `## Step N.M:` (H2 heading with "Step" prefix)
- Orchestrator: `## Orchestrator Instructions` (H2) to end of file

**Content extraction**:
- Include the heading line in extracted content
- Preserve all content until next H2 heading
- Preserve blank lines and formatting within sections
- Strip leading/trailing blank lines from section content

**4. Plan-Specific Agent Generation**
- Read baseline from `agent-core/agents/quiet-task.md`
- Extract baseline content (skip frontmatter)
- Create new frontmatter with plan-specific values
- Append separator
- Append common context (if exists)
- Write to `.claude/agents/<runbook-name>-task.md`

**Frontmatter strategy**: Replace baseline frontmatter entirely
- name: `<runbook-name>-task`
- description: "Execute <runbook-name> steps from the plan with plan-specific context."
- model: From runbook frontmatter or "haiku" default
- color: "cyan"
- tools: ["Read", "Write", "Edit", "Bash", "Grep", "Glob"]

**Reference implementation**: See `/Users/david/code/claudeutils/plans/unification/build-plan-agent.sh` (lines 73-100) for existing agent composition approach. The prepare-runbook.py script extends this pattern with step extraction and validation.

**5. Step File Generation**
- Extract each step section
- Create individual files: `plans/<runbook-name>/steps/step-N.md` or `step-N-M.md`
- Include reference to plan and common context
- Format:
  ```markdown
  # Step N: [Title]

  **Plan**: [path to runbook]
  **Common Context**: [path to common context file or inline]

  [Step content from runbook]
  ```

**6. Orchestrator Plan Generation**
- Use Orchestrator Instructions section if present
- Otherwise generate default:
  ```markdown
  # Orchestrator Plan: [runbook-name]

  Execute steps sequentially using [runbook-name]-task agent.
  Stop on error and escalate to sonnet.
  ```
- Write to `plans/<runbook-name>/orchestrator-plan.md`

**7. Validation**
- Baseline agent exists (MUST fail if missing)
- At least one step section exists (MUST fail if missing)
- No duplicate step numbers (MUST fail if duplicates)
- Output directories writable (MUST fail if not writable)
- Warn if artifacts exist (overwriting is normal)
- Warn if optional sections missing

**8. Output**
- Print list of created/updated files
- Print summary (N steps, agent name, model)
- On error: Clear error message with context

**9. Make Executable**
- Add shebang line at top of file: `#!/usr/bin/env python3`
- Set executable permission: `chmod +x prepare-runbook.py`

### Path Derivation Logic

From input `plans/foo/runbook.md`:
- Runbook name: `foo` (from parent directory)
- Agent: `.claude/agents/foo-task.md`
- Steps: `plans/foo/steps/step-*.md`
- Orchestrator: `plans/foo/orchestrator-plan.md`

### Error Handling

- File not found → Exit with clear message
- Parse error → Exit with line number and context
- Write error → Exit with path and permission info
- Validation error → Exit with specific validation failure

**Expected Outcome**: Script created with all functionality, executable, well-structured

**Unexpected Result Handling**:
- If implementation reveals design issues: Document in report, escalate to user
- If stdlib frontmatter parsing insufficient: Document limitation, proceed with simple parsing

**Error Conditions**:
- Script syntax errors → Report error with details
- Missing imports → Report error, verify stdlib-only requirement
- Logic errors discovered during implementation → Document and escalate

**Validation**:
- Script is executable (`chmod +x`)
- No syntax errors (`python3 -m py_compile`)
- Uses only stdlib imports
- Follows specification sections

**Success Criteria**:
- Script exists at `agent-core/bin/prepare-runbook.py`
- Script is executable (has executable permission and shebang)
- No syntax errors
- All required functions implemented (9 components)
- Validation logic present
- Help message available

**Report Path**: `plans/oneshot-workflow/reports/phase1-step3-execution.md`

---

## Step 1.4: Test Script with Phase 2 Runbook

**Objective**: Verify script works correctly with existing Phase 2 execution plan

**Script Evaluation**: Prose description (test execution with multiple verification steps)

**Execution Model**: Haiku

**Implementation**:

**Part A: Prepare test environment**
1. Ensure clean state (remove any previous test outputs)
2. Verify test runbook exists: `plans/unification/phase2-execution-plan.md`

**Part B: Execute script**
```bash
cd /Users/david/code/claudeutils
python3 /Users/david/code/agent-core/bin/prepare-runbook.py \
    plans/unification/phase2-execution-plan.md
```

**Part C: Verify outputs**

Check created files (Note: runbook name is derived from parent directory `unification`, not filename):
1. Plan-specific agent: `.claude/agents/unification-task.md`
   - Verify file exists
   - Verify contains baseline content
   - Verify contains appended common context (if any)
   - Verify frontmatter updated

2. Step files: `plans/unification/steps/step-2-1.md`, `step-2-2.md`, `step-2-3.md`
   - Verify all 3 step files created (Step 2.1, 2.2, 2.3)
   - Verify each contains correct step content
   - Verify each has plan reference

3. Orchestrator plan: `plans/unification/orchestrator-plan.md`
   - Verify file exists
   - Verify contains orchestrator instructions or default

**Part D: Validate content**
1. Read plan-specific agent, verify structure:
   - Contains baseline quiet-task content
   - Contains separator: "---\n# Runbook-Specific Context"
   - Contains Common Context section from runbook (if present)
   - Frontmatter updated with correct name ("unification-task")
2. Read step-2-1.md, verify format:
   - Has "# Step 2.1:" heading
   - Contains step content from runbook
   - Has reference to plan or common context
3. Read orchestrator-plan.md, verify contains instructions
4. Check for any error messages or warnings from script

**Part E: Re-run test (idempotency check)**
- Run script again with same input
- Verify no errors on overwrite
- Verify outputs updated (not duplicated)

**Expected Outcome**: Script executes successfully, creates all expected outputs

**Unexpected Result Handling**:
- If script fails: Document error, check if it's a script bug or runbook format issue
- If outputs incorrect: Document discrepancies, escalate to sonnet for script fix
- If runbook format incompatible: Document format issue, escalate to user for design decision

**Error Conditions**:
- Script execution error → Capture error output, escalate to sonnet
- Missing outputs → Document which files missing, escalate to sonnet
- Malformed outputs → Document formatting issues, escalate to sonnet
- Idempotency failure → Document overwrite errors, escalate to sonnet

**Validation**:
- Script exits with code 0
- All expected files created
- File contents match expected format
- No errors in script output
- Re-run succeeds

**Success Criteria**:
- Script executes without errors
- All 3 expected output files created
- Plan-specific agent contains baseline + context
- Step files contain correct content
- Orchestrator plan created
- Re-run succeeds (idempotent)
- No warnings or errors in output

**Report Path**: `plans/oneshot-workflow/reports/phase1-step4-execution.md`

---

## Design Decisions

**1. Script location: agent-core/bin/**
- Rationale: Reusable across projects, aligns with existing tooling patterns
- Alternative considered: claudeutils-specific, but reduces reusability

**2. Python 3 stdlib only**
- Rationale: Minimize dependencies, simple deployment
- Alternative: pyyaml for robust YAML parsing (deferred to future if needed)

**3. Simple append strategy for agent composition**
- Rationale: Maintainable, clear separation, no template complexity
- Alternative: Template variables (rejected as over-engineered)

**4. Keep original task-execute.md during Phase 1**
- Rationale: Compatibility during transition, cleanup in Phase 4
- Alternative: Remove immediately (rejected to avoid breaking existing workflows)

**5. Idempotent script behavior (overwrite)**
- Rationale: Normal workflow to re-run after runbook updates
- Warning on overwrite (not error) to inform user

**6. Step file naming from parent directory**
- Rationale: Clear association, avoids filename parsing complexity
- Uses parent directory of runbook as runbook name

---

## Dependencies

**Before This Plan**:
- agent-core repository exists
- claudeutils repository exists
- Oneshot workflow design complete

**After This Plan**:
- Phase 2: Skill creation (uses quiet-task baseline and prepare-runbook.py)
- Phase 3: Documentation updates (references new paths)
- Phase 4: Cleanup (removes old task-execute.md, updates remaining references)

---

## Revision History

**Revision 1 (2026-01-19)** - Initial draft, addressed review feedback:
- Critical #1: Fixed Step 1.4 expected paths (unification-task.md, not phase2-execution-plan-task.md)
- Critical #2: Added executable permission directive to Step 1.3 Component 9
- Critical #3: Added repository-wide reference search to Step 1.2 Part C
- Major #4: Clarified frontmatter replacement strategy in Step 1.3 Component 4
- Major #5: Added detailed content validation to Step 1.4 Part D
- Major #6: Specified section parsing logic in Step 1.3 Component 3

**Review report**: `plans/oneshot-workflow/reports/phase1-plan-review.md`

---

## Notes

### Testing Strategy
Test with existing Phase 2 runbook ensures compatibility with current format and validates all script functionality in realistic scenario.

### Migration Path
Old `build-plan-agent.sh` remains functional during Phase 1. Phase 4 will update or remove it after prepare-runbook.py is proven.

### Future Enhancements
If YAML parsing needs grow complex, add pyyaml dependency with SessionStart hook for installation (plugin-compatible pattern).
