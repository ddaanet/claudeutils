---
name: tdd-integration
model: sonnet
---

# TDD Workflow Integration Runbook

**Context**: Integrate pytest-md TDD-specific skills into agent-core workflow system while preserving TDD methodology using weak orchestrator and plan-specific agent patterns.

**Source**: `plans/tdd-integration/design.md`
**Design**: Complete - all architectural decisions made

**Status**: Ready
**Created**: 2026-01-19
**Reviewed**: 2026-01-19 (Sonnet, NEEDS_REVISION → READY after revision)
**Revised**: 2026-01-19 (Addressed all critical and major review issues)

---

## Weak Orchestrator Metadata

**Total Steps**: 8

**Execution Model**:
- Steps 1-5, 8: Sonnet (file creation, semantic modifications, documentation)
- Step 6: Requires separate planning session (complex parsing logic)
- Step 7: Requires separate planning session (complex skill creation)

**Step Dependencies**:
- Steps 1-3: Parallel (independent file creation)
- Steps 4-5: Parallel (independent skill updates, after Steps 1-3 for reference consistency)
- Step 6: After Steps 1-5 (needs tdd-task.md baseline)
- Step 7: After Step 6 (needs prepare-runbook.py updates)
- Step 8: Can proceed independently (final integration, not blocked by Steps 6-7)

**Error Escalation**:
- Sonnet → User: Parse errors, file not found, unexpected file structure
- Blocked tasks → User: Complexity exceeds sonnet capability, needs architectural decision

**Report Locations**: `plans/tdd-integration/reports/step-N-report.md`

**Success Criteria**:
- All 8 steps completed (or steps 6-7 marked for separate planning)
- All new files created with correct structure
- All modified files maintain existing format
- No syntax errors in modified skills
- prepare-runbook.py validates successfully (if step 6 completed)

**Prerequisites**:
- Working directory: `/Users/david/code/claudeutils` (✓ verified)
- agent-core submodule accessible at `agent-core/` (✓ verified via ls)
- `agents/workflow.md` exists (✓ verified via ls)
- Skills modifiable in `agent-core/skills/` (✓ verified via ls)
- Reports directory: `plans/tdd-integration/reports/` (✓ created)
- pytest-md available at `~/code/pytest-md/` (⚠ NOT VERIFIED - will check in Step 8)
- Git available for submodule operations (⚠ assumed available)
- Python3 available for script validation (⚠ assumed available - required if Step 6 executed)

---

## Common Context

### Key Constraints

**File Locations:**
- Workflow docs: `agent-core/agents/`
- Baseline agents: `agent-core/agents/`
- Skills: `agent-core/skills/<skill-name>/skill.md`
- Scripts: `agent-core/bin/`

**Naming Conventions:**
- Workflow files: `<workflow-name>-workflow.md`
- Baseline agents: `<agent-type>-task.md`
- Plan-specific agents: `<runbook-name>-task.md` (generated)

**TDD Cycle Format:**
```markdown
## Cycle X.Y: [name]

**Dependencies**: [prerequisite cycles or None]

### RED Phase
**Test**: [test name and location]
**Assertions**: [specific assertions]
**Expected Failure**: [exact failure message]

### GREEN Phase
**Implementation**: [what to implement]
**Files**: [files to modify]
**Minimal**: [minimal implementation guidance]

### Stop Conditions
- If RED passes unexpectedly: [action]
- If GREEN fails after 2 attempts: [action]
```

**Command Reference:**
- `just test` - Run test suite (TDD iteration)
- `just lint` - Lint + reformat (post-GREEN cleanup)
- `just precommit` - Check + test without reformat (refactor validation)

**Design Decisions:**
- TDD task agent is baseline template, not standalone shared agent
- Refactoring uses tiered approach (script → simple runbook → full runbook)
- WIP commit + amend pattern for clean history
- Separate workflow docs (oneshot vs tdd)

### Project Paths

**agent-core (submodule):**
- Workflow docs: `agent-core/agents/`
- Skills: `agent-core/skills/`
- Scripts: `agent-core/bin/`

**claudeutils (parent):**
- Current workflow doc: `agents/workflow.md`
- Plans: `plans/`

**pytest-md (external):**
- Location: `~/code/pytest-md/`
- Old skills: `.claude/skills/`
- Old agents: `.claude/agents/`

### Validation Standards

**File creation success:**
- File exists at specified path
- File size > 0 bytes
- File contains required sections from design

**File modification success:**
- Original file structure preserved
- New sections added in correct location
- No syntax errors introduced
- grep confirms expected additions

**Script modification success:**
- Python script validates (`python3 -m py_compile`)
- No import errors
- Help text updated if applicable

---

## Step 1: Create oneshot workflow documentation

**Objective**: Move existing workflow.md to agent-core and rename to oneshot-workflow.md

**Script Evaluation**: Prose description (uses specialized tools for file operations)

**Execution Model**: Sonnet

**Tool Usage**:
- Use Read tool to read source file
- Use Write tool to create destination file
- Use Bash only for directory verification
- Never use bash file operations (cp, cat, etc.)

**Implementation**:

1. Verify destination directory exists:
   ```bash
   test -d agent-core/agents || (echo "ERROR: agent-core/agents not found" && exit 1)
   ```

2. Read source file:
   - Use Read tool on `agents/workflow.md`
   - Store content for write operation

3. Write to destination:
   - Use Write tool to create `agent-core/agents/oneshot-workflow.md`
   - Write exact content from source file

4. Report success:
   - Note: Original `agents/workflow.md` preserved for reference until all updates complete

**Expected Outcome**:
- File `agent-core/agents/oneshot-workflow.md` exists
- File size matches original `agents/workflow.md`
- Original file still exists (will be deleted in later step after reference updates)

**Unexpected Result Handling**:
- If source file missing: STOP - verify current working directory
- If destination directory missing: STOP - verify agent-core submodule initialized
- If copy fails: STOP - check file permissions

**Error Conditions**:
- File not found → STOP and report to user
- Permission denied → STOP and report to user
- Disk space issue → STOP and report to user

**Validation**:
- Read `agent-core/agents/oneshot-workflow.md` successfully (confirms file exists)
- File size > 10000 bytes (workflow.md is substantial)
- Grep for "workflow" pattern in `agent-core/agents/oneshot-workflow.md` (confirms content copied)

**Success Criteria**:
- File created successfully
- File size matches source
- File readable and contains workflow content

**Report Path**: `plans/tdd-integration/reports/step-1-report.md`

---

## Step 2: Create TDD workflow documentation

**Objective**: Write new `agent-core/agents/tdd-workflow.md` documenting TDD workflow

**Script Evaluation**: Prose description (requires semantic content creation)

**Execution Model**: Sonnet

**Tool Usage**:
- Use Write tool to create new file
- Use Read tool to reference design document
- Use Grep tool for content validation
- Never use bash file operations or heredocs

**Implementation**:

Create new file `agent-core/agents/tdd-workflow.md` with the following structure and content based on design document:

**Required Sections:**

1. **Overview**
   - TDD workflow purpose and when to use
   - Integration with oneshot workflow
   - Methodology detection signals

2. **Workflow Stages**
   - `/design` (TDD mode) → design document with spike test section
   - `/plan-tdd` → TDD runbook with cycles
   - `/orchestrate` → cycle execution via tdd-task agent
   - `/vet` → review uncommitted changes
   - Apply fixes if needed
   - `/review-analysis` → TDD process review

3. **TDD Cycle Structure**
   - RED phase protocol
   - GREEN phase protocol
   - REFACTOR phase protocol (mandatory per cycle)
   - Stop conditions and escalation

4. **Refactoring Tiers**
   - Tier 1: Script-based (mechanical transformations)
   - Tier 2: Simple runbook (2-5 steps, minor judgment)
   - Tier 3: Full runbook (5+ steps, design decisions)

5. **Commit Strategy**
   - WIP commit as rollback point
   - Post-refactoring amend
   - Safety checks before amend
   - Only precommit-validated states in history

6. **Command Reference**
   - `just test` - Run test suite
   - `just lint` - Lint + reformat
   - `just precommit` - Check + test (no reformat)

7. **Integration Points**
   - How TDD workflow differs from oneshot
   - When to use each workflow
   - Transition between workflows

**Content Source**: Extract from `plans/tdd-integration/design.md` sections:
- Unified Workflow Entry Point
- TDD Runbook Structure
- TDD Task Agent (protocol sections)
- Post-TDD Execution Flow
- Command Reference

**Expected Outcome**:
- File `agent-core/agents/tdd-workflow.md` created
- Contains all 7 required sections
- Follows markdown format consistent with oneshot-workflow.md
- File size 5000-8000 bytes (substantial documentation)

**Unexpected Result Handling**:
- If agent-core/agents directory missing: STOP - verify submodule
- If file size < 3000 bytes: Review content completeness before proceeding

**Error Conditions**:
- Directory not found → STOP and report to user
- Write permission denied → STOP and report to user

**Validation**:
- Read `agent-core/agents/tdd-workflow.md` successfully (confirms file exists)
- Use Grep to verify all required sections present (Overview, Workflow Stages, etc.)
- File size typically 5000-8000 bytes (may vary with detail level)
- Content accurately reflects design document

**Success Criteria**:
- File created with all 7 required sections
- Content accurately reflects design document
- File size indicates substantial documentation (5000-8000 bytes)
- Markdown syntax valid

**Report Path**: `plans/tdd-integration/reports/step-2-report.md`

---

## Step 3: Create TDD task agent baseline

**Objective**: Write `agent-core/agents/tdd-task.md` baseline template for TDD cycle execution

**Script Evaluation**: Prose description (complex protocol documentation)

**Execution Model**: Sonnet

**Tool Usage**:
- Use Write tool to create new file
- Use Read tool to reference design document
- Use Grep tool for content validation
- Never use bash file operations or heredocs

**Implementation**:

Create new file `agent-core/agents/tdd-task.md` with baseline TDD protocol that will be combined with runbook-specific context by prepare-runbook.py.

**Required Sections:**

1. **Agent Role and Purpose**
   - Baseline template for TDD cycle execution
   - Combined with runbook context to create plan-specific agents
   - Fresh context per cycle (no accumulation)

2. **RED Phase Protocol**
   - Write test exactly as specified in cycle definition
   - Run `just test`
   - Verify failure matches expected message
   - If passes unexpectedly → check for `[REGRESSION]` marker
   - If not regression: STOP and escalate

3. **GREEN Phase Protocol**
   - Write minimal implementation to make test pass
   - Run `just test` → verify test passes
   - Run full suite → handle any regressions individually (never batch)
   - If stuck after 2 attempts → STOP, mark BLOCKED, escalate

4. **REFACTOR Phase Protocol (Mandatory)**

   Step-by-step refactoring process:

   a. **Format & Lint**
   ```bash
   just lint  # includes reformatting
   ```
   Fix lint errors. Ignore complexity warnings and line limits (addressed next).

   b. **Intermediate Commit**
   ```bash
   git commit -m "WIP: Cycle X.Y [name]"  # rollback point
   ```

   c. **Quality Check**
   ```bash
   just precommit  # validates green BEFORE refactoring
   ```
   Surfaces complexity warnings and line limit issues.

   d. **Refactoring Assessment (if warnings)**

   | Warning Type | Handler |
   |--------------|---------|
   | Common (split module, simplify function) | Sonnet designs, executes |
   | Architectural (new abstraction, multi-module impact) | Opus designs, decides escalation |
   | New abstraction introduced | Opus, always escalate to human |

   e. **Execute Refactoring**
   - Use scripts proactively (Tier 1)
   - Verify with `just precommit` after
   - If fails: STOP, keep state for diagnostic

   f. **Post-Refactoring Updates**
   Update all references to refactored code:
   - Plans: All designs and runbooks (`grep -r "old_ref" plans/`)
   - Agent documentation: Files in `agents/`
   - CLAUDE.md: Only if behavioral rules affected
   - Regenerate step files if runbook.md changed

   g. **Amend Commit**
   Safety check:
   ```bash
   current_msg=$(git log -1 --format=%s)
   if [[ "$current_msg" != WIP:* ]]; then
     echo "ERROR: Expected WIP commit, found: $current_msg"
     exit 1
   fi
   ```

   Amend and reword:
   ```bash
   git commit --amend -m "Cycle X.Y: [name]"
   ```

5. **Structured Log Entry Template**
   ```markdown
   ### Cycle X.Y: [name] [timestamp]
   - Status: RED_VERIFIED | GREEN_VERIFIED | STOP_CONDITION | REGRESSION
   - Test command: `[exact command]`
   - RED result: [FAIL as expected | PASS unexpected | N/A]
   - GREEN result: [PASS | FAIL - reason]
   - Regression check: [N/N passed | failures]
   - Refactoring: [none | description]
   - Files modified: [list]
   - Stop condition: [none | description]
   - Decision made: [none | description]
   ```

6. **Stop Conditions and Escalation**
   - RED passes unexpectedly (not regression) → STOP, escalate
   - GREEN fails after 2 attempts → STOP, mark BLOCKED, escalate
   - Refactoring fails precommit → STOP, keep state, escalate
   - Architectural refactoring needed → Escalate to opus
   - New abstraction proposed → Escalate to human via opus

7. **Tool Usage Constraints**
   - Use Read, Write, Edit for file operations
   - Use Bash for test commands, git commands, precommit
   - Use Grep for reference finding (grep -r pattern)
   - Never use heredocs in Bash (sandbox restriction)
   - Report all errors explicitly (never suppress)

**Content Source**: Extract from design document sections:
- TDD Task Agent (all subsections)
- TDD Execution Escalation
- Command Reference

**Expected Outcome**:
- File `agent-core/agents/tdd-task.md` created
- Contains all 7 required sections
- Protocol is explicit and actionable for weak orchestrator
- File size 6000-10000 bytes (comprehensive baseline)

**Unexpected Result Handling**:
- If file size < 5000 bytes: Review completeness of protocol steps
- If refactoring section unclear: Add more specific decision criteria

**Error Conditions**:
- Directory not found → STOP and report
- Write permission denied → STOP and report

**Validation**:
- Read `agent-core/agents/tdd-task.md` successfully (confirms file exists)
- Use Grep to verify all 7 required sections present
- Use Grep to verify command examples present ("just test", "just lint", "just precommit")
- File size typically 6000-12000 bytes (comprehensive baseline)
- Content matches design document protocol

**Success Criteria**:
- File created with all 7 required sections
- RED/GREEN/REFACTOR protocol complete and explicit
- Stop conditions clearly defined
- Escalation rules documented
- File size indicates comprehensive baseline (6000-10000 bytes)

**Report Path**: `plans/tdd-integration/reports/step-3-report.md`

---

## Step 4: Update /design skill for TDD mode

**Objective**: Modify `/design` skill to support both general and TDD modes

**Script Evaluation**: Prose description (semantic modifications to skill)

**Execution Model**: Sonnet

**Tool Usage**:
- Use Read tool to read existing skill file
- Use Edit tool to modify skill file
- Use Grep tool for validation
- Never use bash sed/awk or heredocs

**Implementation**:

Modify `agent-core/skills/design/skill.md` to add TDD mode support while preserving existing general mode functionality.

**Modifications Required:**

1. **Add Mode Selection Section** (near top of skill)
   ```markdown
   ## Design Mode Selection

   The design skill supports two modes based on methodology detection:

   **TDD Mode** - Triggered when:
   - Project has test-first culture
   - User mentions "test", "TDD", "red/green"
   - Feature requires behavioral verification
   - Project is pytest-md or similar

   **General Mode** - Triggered when:
   - Infrastructure/migration work
   - Refactoring without behavior change
   - Prototype/exploration work
   - Default if TDD signals absent
   ```

2. **Document Shared Sections** (both modes)
   - Problem statement
   - Requirements (functional, non-functional, out of scope)
   - Key design decisions with rationale
   - High-level phases

3. **Document TDD Mode Additions**
   ```markdown
   ### TDD Mode Specific Sections

   **Spike Test Section**:
   - Verify current behavior
   - Document framework defaults
   - Identify what might already work

   **Confirmation Markers**:
   - Use `(REQUIRES CONFIRMATION)` for decisions needing user input

   **Flag Reference Table** (if adding CLI options):
   - Document new flags and their behavior

   **"What Might Already Work" Analysis**:
   - Identify existing functionality to leverage
   ```

4. **Document General Mode Additions**
   ```markdown
   ### General Mode Specific Sections

   - Integration points
   - Edge cases
   - Risks and mitigations
   - Detailed implementation notes
   ```

5. **Update Output Section**
   ```markdown
   ## Output

   **TDD Mode**: Design document consumed by `/plan-tdd`
   **General Mode**: Design document consumed by `/plan-adhoc`
   ```

**Integration Points:**
- Preserve existing skill structure
- Add new sections without breaking existing usage
- Maintain backward compatibility with general mode
- Reference tdd-workflow.md and oneshot-workflow.md for details

**Expected Outcome**:
- skill.md modified with TDD mode support
- Mode selection documented
- TDD-specific sections added
- General mode sections preserved
- File size increase of ~500-1000 bytes

**Unexpected Result Handling**:
- If skill.md structure differs from expected: Review and adapt modifications
- If existing mode selection already present: Merge rather than duplicate

**Error Conditions**:
- File not found → STOP and report
- Parse error in existing content → STOP and report
- Write permission denied → STOP and report

**Validation**:
- Use Grep to verify "TDD Mode" present in `agent-core/skills/design/skill.md`
- Use Grep to verify mode selection section added
- Use Read to confirm original content preserved
- File size increased by ~800-1500 bytes

**Success Criteria**:
- skill.md contains mode selection logic
- TDD mode additions documented
- General mode preserved
- No syntax errors introduced
- File size increase 500-1000 bytes

**Report Path**: `plans/tdd-integration/reports/step-4-report.md`

---

## Step 5: Update /oneshot skill for methodology detection

**Objective**: Add TDD methodology detection to `/oneshot` skill entry point

**Script Evaluation**: Prose description (semantic modifications)

**Execution Model**: Sonnet

**Tool Usage**:
- Use Read tool to read existing skill file
- Use Edit tool to modify skill file
- Use Grep tool for validation
- Never use bash sed/awk or heredocs

**Implementation**:

Modify `agent-core/skills/oneshot/skill.md` to add methodology detection logic that routes to TDD or general workflow.

**Modifications Required:**

1. **Add Methodology Detection Section** (after "When to Use" section)
   ```markdown
   ## Methodology Detection

   The oneshot skill detects appropriate workflow based on these signals:

   **TDD Methodology Signals:**
   - Project has test-first culture
   - User mentions "test", "TDD", "red/green"
   - Feature requires behavioral verification
   - Project is pytest-md or similar

   **General Methodology Signals:**
   - Infrastructure/migration work
   - Refactoring without behavior change
   - Prototype/exploration
   - Default if TDD signals absent

   **Workflow Routing:**
   - TDD path: `/design` (TDD mode) → `/plan-tdd` → `/orchestrate` → `/vet` → `/review-analysis`
   - General path: `/design` → `/plan-adhoc` → `/orchestrate` → `/vet`
   ```

2. **Update Workflow Description**
   Add after methodology detection:
   ```markdown
   ## Workflow Selection

   Based on methodology detection, oneshot routes to:

   **TDD Workflow** (feature development):
   - Design with spike test section
   - Plan as TDD cycles (RED/GREEN/REFACTOR)
   - Execute via tdd-task agent
   - Review process compliance

   **General Workflow** (oneshot work):
   - Design with implementation details
   - Plan as sequential steps
   - Execute via quiet-task agent
   - Review code quality
   ```

3. **Add Workflow Documentation References**
   ```markdown
   ## Workflow Documentation

   - TDD workflow: See `agent-core/agents/tdd-workflow.md`
   - General workflow: See `agent-core/agents/oneshot-workflow.md`
   ```

**Expected Outcome**:
- skill.md modified with methodology detection
- Workflow routing documented
- References to workflow docs added
- File size increase of ~300-500 bytes

**Unexpected Result Handling**:
- If skill structure differs from expected: Adapt section placement
- If methodology detection already exists: Merge updates

**Error Conditions**:
- File not found → STOP and report
- Write permission denied → STOP and report

**Validation**:
- Use Grep to verify "Methodology Detection" in `agent-core/skills/oneshot/skill.md`
- Use Grep to verify TDD signals documented
- Use Grep to verify workflow routing present
- File size increased by ~300-500 bytes

**Success Criteria**:
- skill.md contains methodology detection
- Workflow routing documented
- References to workflow docs added
- No syntax errors
- File size increase 300-500 bytes

**Report Path**: `plans/tdd-integration/reports/step-5-report.md`

---

## Step 6: Update prepare-runbook.py for TDD cycles

**Objective**: Create planning request for prepare-runbook.py TDD cycle support

**Script Evaluation**: Large/Complex - Task requires separate planning session

**Execution Model**: Sonnet (creates planning request document)

**Tool Usage**:
- Use Write tool to create planning request file
- Use Read tool to reference design document
- Never use bash file operations or heredocs

**Rationale for Separate Planning**:
- Script modifications exceed 100 lines
- Complex parsing logic for cycle detection
- Multiple code paths (TDD vs general runbook)
- Requires careful handling of baseline selection (tdd-task.md vs quiet-task.md)
- Error handling for malformed cycle definitions
- Testing strategy needed

**Planning Requirements**:
1. Analyze current prepare-runbook.py structure
2. Design cycle detection logic (regex patterns for "## Cycle X.Y:")
3. Design TDD metadata detection (frontmatter: `type: tdd`)
4. Design baseline selection logic (tdd-task.md vs quiet-task.md)
5. Design cycle file generation (different from step files)
6. Design validation for cycle format
7. Update help text and error messages
8. Add unit tests or validation scripts

**Dependencies**:
- Step 3 must be complete (tdd-task.md baseline must exist)
- Understanding of current prepare-runbook.py implementation
- Design document cycle format specification

**Implementation**:

Create planning request document at `plans/tdd-integration/reports/step-6-planning-request.md` containing:

1. **Task Objective**: Add TDD cycle format support to prepare-runbook.py

2. **Complexity Rationale**:
   - Script modifications exceed 100 lines
   - Complex parsing logic for cycle detection
   - Multiple code paths (TDD vs general runbook)
   - Baseline selection logic (tdd-task.md vs quiet-task.md)

3. **Planning Requirements** (from design doc):
   - Analyze current prepare-runbook.py structure
   - Design cycle detection logic (regex for "## Cycle X.Y:")
   - Design TDD metadata detection (frontmatter: `type: tdd`)
   - Design baseline selection logic
   - Design cycle file generation
   - Design validation for cycle format
   - Update help text and error messages

4. **Dependencies**:
   - Step 3 must be complete (tdd-task.md baseline exists)
   - Current prepare-runbook.py implementation understood

5. **Reference Material**:
   - `plans/tdd-integration/design.md` (TDD runbook structure section)
   - `agent-core/bin/prepare-runbook.py` (current implementation)
   - `agent-core/agents/tdd-task.md` (baseline template created in Step 3)

6. **Next Action**: Requires separate planning session with sonnet or opus

**Expected Outcome**:
- Planning request file created at `plans/tdd-integration/reports/step-6-planning-request.md`
- Contains all 6 sections above
- Step marked as ready for separate planning session

**Error Handling**:
- Write permission denied → STOP and report
- Design document not found → STOP and report

**Validation**:
- Read `plans/tdd-integration/reports/step-6-planning-request.md` successfully
- Use Grep to verify all 6 required sections present
- File size > 2000 bytes (comprehensive request)

**Success Criteria**:
- Planning request file created with all required sections
- Contains all planning requirements from design doc
- Ready for delegation to separate planning session

**Report Path**: `plans/tdd-integration/reports/step-6-report.md`

---

## Step 7: Create /plan-tdd skill

**Objective**: Create planning request for /plan-tdd skill implementation

**Script Evaluation**: Large/Complex - Task requires separate planning session

**Execution Model**: Sonnet (creates planning request document)

**Tool Usage**:
- Use Write tool to create planning request file
- Use Read tool to reference design document
- Never use bash file operations or heredocs

**Rationale for Separate Planning**:
- New skill creation with substantial logic
- Must adapt pytest-md reference implementation
- Complex TDD cycle planning logic
- Requires 4-point planning process for TDD runbooks
- Integration with prepare-runbook.py (depends on step 6)
- Error handling and validation
- Testing strategy needed

**Planning Requirements**:
1. Review pytest-md `/plan-design` skill as reference
2. Design 4-point planning process for TDD runbooks
3. Design cycle breakdown logic (feature → cycles)
4. Design RED/GREEN/REFACTOR phase templates
5. Design stop condition generation
6. Design dependency tracking between cycles
7. Design metadata generation for TDD runbooks
8. Create skill directory structure and frontmatter
9. Update skill documentation

**Dependencies**:
- Step 6 must be complete (prepare-runbook.py supports TDD cycles)
- pytest-md reference implementation available
- Design document TDD runbook structure specification

**Reference Material**:
- `~/code/pytest-md/.claude/skills/plan-design/` (if exists)
- `plans/tdd-integration/design.md` (TDD runbook structure section)
- `agent-core/agents/tdd-workflow.md` (created in step 2)

**Implementation**:

Create planning request document at `plans/tdd-integration/reports/step-7-planning-request.md` containing:

1. **Task Objective**: Create new `/plan-tdd` skill for TDD runbook generation

2. **Complexity Rationale**:
   - New skill creation with substantial logic
   - Must adapt pytest-md reference implementation
   - Complex TDD cycle planning logic
   - Integration with prepare-runbook.py (depends on Step 6)

3. **Planning Requirements** (from design doc):
   - Review pytest-md `/plan-design` skill as reference
   - Design 4-point planning process for TDD runbooks
   - Design cycle breakdown logic (feature → cycles)
   - Design RED/GREEN/REFACTOR phase templates
   - Design stop condition generation
   - Design dependency tracking between cycles
   - Design metadata generation for TDD runbooks
   - Create skill directory structure and frontmatter

4. **Dependencies**:
   - Step 6 must be complete (prepare-runbook.py supports TDD cycles)
   - pytest-md reference implementation available
   - Design document TDD runbook structure specification

5. **Reference Material**:
   - `~/code/pytest-md/.claude/skills/plan-design/` (if exists)
   - `plans/tdd-integration/design.md` (TDD runbook structure section)
   - `agent-core/agents/tdd-workflow.md` (created in Step 2)

6. **Next Action**: Requires separate planning session with sonnet

**Expected Outcome**:
- Planning request file created at `plans/tdd-integration/reports/step-7-planning-request.md`
- Contains all 6 sections above
- Step marked as ready for separate planning session (after Step 6 complete)

**Error Handling**:
- Write permission denied → STOP and report
- Design document not found → STOP and report

**Validation**:
- Read `plans/tdd-integration/reports/step-7-planning-request.md` successfully
- Use Grep to verify all 6 required sections present
- File size > 2000 bytes (comprehensive request)

**Success Criteria**:
- Planning request file created with all required sections
- Contains reference to pytest-md implementation
- Ready for delegation to separate planning session (after Step 6)

**Report Path**: `plans/tdd-integration/reports/step-7-report.md`

---

## Step 8: pytest-md integration

**Objective**: Integrate agent-core into pytest-md via submodule and remove old files

**Script Evaluation**: Medium script (~75 lines, mostly sequential operations)

**Execution Model**: Sonnet

**Working Directory**: Execute from claudeutils root (script handles directory changes via cd)

**Tool Usage**:
- Use Bash for all git operations, directory changes, file operations
- This step uses bash file operations (not Read/Write tools) because it's git/submodule work
- Never suppress errors with `|| true` or `2>/dev/null` except where explicitly intended

**Implementation**:

```bash
#!/usr/bin/env bash
# Integrate agent-core into pytest-md

set -e  # Exit on error

# Verify pytest-md directory exists
PYTEST_MD_DIR="$HOME/code/pytest-md"
if [[ ! -d "$PYTEST_MD_DIR" ]]; then
  echo "ERROR: pytest-md directory not found at $PYTEST_MD_DIR"
  exit 1
fi

cd "$PYTEST_MD_DIR"

# Add agent-core as submodule (if not already added)
if [[ ! -d agent-core ]]; then
  echo "Adding agent-core submodule..."
  git submodule add ../agent-core agent-core
else
  echo "✓ agent-core submodule already exists"
fi

# Initialize submodule (if needed)
git submodule update --init --recursive

# Verify agent-core sync recipe exists
if [[ ! -f agent-core/Makefile ]] && [[ ! -f agent-core/justfile ]]; then
  echo "WARNING: No sync recipe found in agent-core (expected Makefile or justfile)"
fi

# Run sync recipe if exists (install skills/agents)
if [[ -f agent-core/justfile ]]; then
  echo "Running agent-core sync recipe..."
  just -f agent-core/justfile sync
elif [[ -f agent-core/Makefile ]]; then
  echo "Running agent-core sync recipe..."
  make -C agent-core sync
else
  echo "SKIP: No sync recipe found - manual installation may be required"
fi

# Backup old skills (before removal)
if [[ -d .claude/skills ]] && [[ -n "$(ls -A .claude/skills 2>/dev/null)" ]]; then
  echo "Backing up old skills..."
  mkdir -p .backup/skills
  cp -r .claude/skills/* .backup/skills/
  echo "✓ Old skills backed up to .backup/skills/"

  # Remove old skills
  echo "Removing old project-specific skills..."
  rm -rf .claude/skills/*
  echo "✓ Old skills removed"
else
  echo "ℹ No skills to backup (directory empty or missing)"
fi

# Backup old agents (before removal)
if [[ -d .claude/agents ]] && [[ -n "$(ls -A .claude/agents 2>/dev/null)" ]]; then
  echo "Backing up old agents..."
  mkdir -p .backup/agents
  cp -r .claude/agents/* .backup/agents/
  echo "✓ Old agents backed up to .backup/agents/"

  # Remove old agents
  echo "Removing old project-specific agents..."
  rm -rf .claude/agents/*
  echo "✓ Old agents removed"
else
  echo "ℹ No agents to backup (directory empty or missing)"
fi

# Verify integration
echo ""
echo "Integration summary:"
echo "  Submodule: $(git submodule status agent-core | awk '{print $2, $1}')"
echo "  Old skills backed up: .backup/skills/"
echo "  Old agents backed up: .backup/agents/"
echo ""
echo "✓ pytest-md integration complete"
echo ""
echo "Next steps:"
echo "  1. Review .backup/ directory for any project-specific customizations"
echo "  2. Verify agent-core skills/agents are accessible"
echo "  3. Test TDD workflow with pytest-md project"
```

**Expected Outcome**:
- agent-core submodule added to pytest-md
- Submodule initialized and updated
- Sync recipe executed (skills/agents installed)
- Old skills backed up and removed
- Old agents backed up and removed
- Integration verified

**Unexpected Result Handling**:
- If pytest-md directory missing: STOP - verify path is correct
- If submodule add fails: Check if already exists, continue
- If sync recipe missing: Skip sync step, document manual installation needed
- If backup fails: Continue but warn user

**Error Conditions**:
- pytest-md not found → STOP and report
- Git operation fails → STOP and report
- Permission denied → STOP and report

**Validation**:
- Submodule exists: `git submodule status agent-core` in pytest-md
- Submodule initialized: `test -f agent-core/README.md` in pytest-md
- Old files backed up: `test -d .backup/skills` in pytest-md
- Old files removed: `test -z "$(ls -A .claude/skills)"` in pytest-md

**Success Criteria**:
- agent-core submodule added and initialized
- Old skills and agents backed up
- Old skills and agents removed
- Integration verified via git submodule status

**Report Path**: `plans/tdd-integration/reports/step-8-report.md`

---

## Orchestrator Instructions

**CRITICAL: Each step MUST be executed by a separate agent invocation.** Do not execute multiple steps in a single agent call.

Use tdd-integration-task agent for all step executions.

**Execution Order:**

**Phase 1 - Parallel execution (Steps 1-3):**
- Launch 3 agents in parallel (single message with 3 Task tool calls):
  - Agent 1: Execute Step 1 (create oneshot-workflow.md)
  - Agent 2: Execute Step 2 (create tdd-workflow.md)
  - Agent 3: Execute Step 3 (create tdd-task.md)
- Wait for all 3 agents to complete before proceeding

**Phase 2 - Parallel execution (Steps 4-5):**
- Launch 2 agents in parallel (single message with 2 Task tool calls):
  - Agent 4: Execute Step 4 (update /design skill)
  - Agent 5: Execute Step 5 (update /oneshot skill)
- Wait for both agents to complete before proceeding

**Phase 3 - Sequential execution (Steps 6-8):**
- Agent 6: Execute Step 6 (create planning request for prepare-runbook.py)
- Agent 7: Execute Step 7 (create planning request for /plan-tdd) - after Step 6 completes
- Agent 8: Execute Step 8 (pytest-md integration) - can run independently

**Agent Invocation Pattern:**
```
For parallel steps: Single message with multiple Task tool calls
For sequential steps: One Task tool call per message, wait for completion
```

**Error Handling:**

- File not found errors → Verify prerequisites, escalate to user
- Permission denied → Escalate to user immediately
- Unexpected file structure → Stop and escalate to sonnet for review
- Parse errors in modified files → Stop and escalate to sonnet for fix

**Escalation Rules:**

- Haiku → Sonnet: Complex modifications, unexpected structures
- Sonnet → User: Missing prerequisites, blocked tasks, architectural decisions

**Success Criteria:**

- Steps 1-5 completed successfully (files created/modified)
- Steps 6-7 completed successfully (planning requests created)
- Step 8 completed successfully (pytest-md integrated)
- All validation criteria met for all steps
- No syntax errors in any modified files
- Planning requests ready for separate planning sessions

---

## Design Decisions

### Decision 1: Separate Planning for Steps 6-7

**Problem**: Should prepare-runbook.py and /plan-tdd creation be in this runbook or separate?

**Choice**: Separate planning sessions for steps 6-7

**Rationale**: Both tasks exceed complexity threshold for inline runbook steps (>100 lines, complex logic, multiple design decisions). Separating allows this runbook to complete steps 1-5 and 8 while delegating complex implementation planning to dedicated sessions.

### Decision 2: Copy vs Move workflow.md

**Problem**: Should workflow.md be moved or copied initially?

**Choice**: Copy initially, preserve original

**Rationale**: Safer during transition - allows verification of new location before removing original. Original will be deleted after all reference updates confirmed in later steps.

### Decision 3: Parallel Execution Where Possible

**Problem**: Which steps can run in parallel?

**Choice**: Steps 1-2 parallel, steps 4-5 parallel

**Rationale**: These steps are independent file creation/modification tasks with no dependencies. Parallelizing reduces overall execution time.

---

## Dependencies

**Before This Runbook:**
- agent-core workflow infrastructure complete
- pytest-md TDD skills available as reference
- prepare-runbook.py exists and works for general runbooks

**After This Runbook:**
- Steps 1-5 complete: Core documentation and workflow files created
- Steps 6-7 complete: Planning requests ready for separate planning sessions
- Step 8 complete: pytest-md integrated with agent-core submodule
- Next work: Execute planning sessions for steps 6-7, then implement

**Blocked Work:**
- prepare-runbook.py TDD support (requires Step 6 planning session execution)
- /plan-tdd skill creation (requires Step 7 planning session execution)
- Full TDD workflow testing (requires both implementations complete)
- pytest-md TDD feature development (requires full TDD workflow)

---

## Revision History

**Initial Draft (2026-01-19)** - Created from design document

**Revision 1 (2026-01-19)** - Addressed critical and major review issues:
- Fixed step dependencies (Steps 1-3 now parallel)
- Rewrote Step 1 to use Read/Write tools instead of bash cp
- Added explicit tool usage instructions to all file operation steps
- Clarified Steps 6-7 execution model (create planning requests, not blocked)
- Completed prerequisite verification with unverified items marked
- Rewrote all validation sections to use specialized tools
- Fixed Step 8 error suppression in backup logic
- Added working directory specification for Step 8
- Updated orchestrator instructions to reflect corrected dependencies

**Review report**: `plans/tdd-integration/reports/runbook-review.md`

---

## Notes

**Steps 6-7 Planning Requests:**
Both steps create planning request documents rather than attempting inline implementation. This follows the script-first principle: complex logic (>100 lines) requires dedicated planning sessions. The planning requests will be executed as separate tasks after this runbook completes.

**Testing Strategy:**
After Steps 6-7 planning sessions are executed and implementations complete, create sample TDD runbook for pytest-md feature and execute via updated /orchestrate to verify full integration.

**Reference Updates:**
After Step 1 (workflow.md copy), may need to update references from `agents/workflow.md` to `agent-core/agents/oneshot-workflow.md` in CLAUDE.md and other documentation. This is NOT included in current runbook steps but should be tracked separately. Original file preserved during transition.

**Submodule Sync:**
Step 8 assumes agent-core has a sync recipe (Makefile or justfile). If not present, manual installation of skills/agents may be required. Document this in Step 8 report.

**Tool Usage Standards:**
All file operation steps now explicitly specify tool usage (Read, Write, Edit, Grep) per project standards. Step 8 is exception as it performs git/submodule operations which require bash.
