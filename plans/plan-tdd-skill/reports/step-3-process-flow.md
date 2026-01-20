# Step 3: Skill Process Flow Design

**Date**: 2026-01-20
**Purpose**: Define end-to-end execution flow for /plan-tdd skill

---

## Process Overview

The /plan-tdd skill transforms a design document into a TDD runbook through five sequential phases: Intake, Analysis, Cycle Planning, Runbook Generation, and Validation.

---

## Phase 1: Intake

### Inputs
- Design document path (from user invocation or default location)
- Optional: CLAUDE.md for project conventions

### Actions

**1.1 Determine Design Document Path**

User invocation patterns:
- `/plan-tdd` → Use default: `plans/[last-modified]/design.md`
- `/plan-tdd <path>` → Use specified path
- `/plan-tdd <feature-name>` → Use `plans/<feature-name>/design.md`

Logic:
```
If user provides path:
    design_path = user_path
Else if user provides feature name:
    design_path = plans/{feature-name}/design.md
Else:
    # Find most recently modified design.md in plans/
    design_path = find_latest_design_doc()
```

**1.2 Read Design Document**

Actions:
- Use Read tool to load design document
- Store content for analysis

Error handling:
- File not found → STOP, report path, suggest alternatives
- Permission denied → STOP, report error
- Empty file → STOP, report empty document

**1.3 Read Project Conventions (Optional)**

Actions:
- Check if `CLAUDE.md` exists in project root
- If exists: Read tool to load
- Extract relevant conventions (tool usage, testing patterns)

Error handling:
- CLAUDE.md not found → Proceed with defaults (not an error)
- CLAUDE.md unreadable → WARNING, proceed with defaults

**1.4 Initial Validation**

Actions:
- Verify design document is valid markdown
- Check for basic structure (headers, content)
- Identify TDD mode indicator (`type: tdd` or "TDD" in title/goal)

Error handling:
- Not valid markdown → STOP, report parsing errors
- No TDD indicators → Ask user: "Is this a TDD runbook? If yes, I'll proceed with TDD format."
- User says no → STOP, suggest /plan-adhoc instead

### Outputs
- `design_content`: Parsed design document
- `design_path`: Absolute path to design doc
- `feature_name`: Extracted from design or path
- `conventions`: Project-specific rules (if available)

### User Interaction Points
- Confirm TDD mode if ambiguous
- Confirm design document path if multiple candidates found

---

## Phase 2: Analysis

### Inputs
- `design_content` from Phase 1
- `conventions` from Phase 1

### Actions

**2.1 Extract Feature Information**

Actions:
- Parse goal/objective statement
- Extract feature name
- Identify high-level requirements

Patterns to search:
- `**Goal:**` or `## Goal`
- `# [Feature Name]` (H1 title)
- Objective/purpose statements in first paragraphs

Error handling:
- No goal found → STOP, ask user to provide goal
- Feature name unclear → Infer from filename or ask user

**2.2 Extract Design Decisions**

Actions:
- Find "Design Decisions" section
- Extract each decision with rationale
- Store for Common Context generation

Patterns to search:
- `## Design Decisions`
- `### Decision N:`
- Bullet lists of decisions

Error handling:
- No design decisions section → WARNING, proceed with empty context
- Unstructured decisions → Extract best-effort, warn about format

**2.3 Check for Unresolved Items**

Actions:
- Grep for confirmation markers in design content
- Extract context around each marker
- Build list of unresolved items

Patterns to search:
- `(REQUIRES CONFIRMATION)`
- `(TBD)`
- `(TODO: decide)`
- `[DECIDE:]`
- `???`

Error handling:
- Unresolved items found → STOP, report list with context, ask user to resolve

Example stop message:
```
Found 3 unresolved items in design:

1. Line 45: Authentication method (REQUIRES CONFIRMATION)
   Context: "Use OAuth2 or API keys (REQUIRES CONFIRMATION)"

2. Line 78: Error handling strategy (TBD)
   Context: "Retry logic to be determined (TBD)"

3. Line 102: Database choice
   Context: "SQLite or PostgreSQL [DECIDE:]"

Please resolve these decisions in the design document before proceeding.
```

**2.4 Identify Implementation Structure**

Actions:
- Look for explicit phases/sections
- Identify behavioral increments
- Determine decomposition strategy

Patterns to search:
- `## Phase N:` headers
- `### [Feature/Component]` subsections
- Bullet lists of features/behaviors
- Test scenarios or acceptance criteria

Error handling:
- No clear structure → Attempt to infer from content
- Cannot infer → STOP, ask user to clarify structure

**2.5 Determine Cycle Count Estimate**

Actions:
- Count identified increments
- Apply granularity heuristic (1-3 assertions/cycle)
- Estimate total cycle count

Logic:
```
increments = count_behavioral_increments()
cycles_estimate = increments * 1.2  # Account for setup cycles
```

Purpose: Inform user of runbook size, set expectations

### Outputs
- `goal`: Feature objective
- `feature_name`: Clean feature name for paths
- `design_decisions`: List of decisions with rationale
- `phases`: List of phase definitions
- `increments`: List of behavioral increments per phase
- `cycle_estimate`: Estimated cycle count

### User Interaction Points
- STOP if unresolved confirmations found
- Confirm cycle estimate if very large (>20 cycles)

---

## Phase 3: Cycle Planning

### Inputs
- `phases` and `increments` from Phase 2
- `design_decisions` from Phase 2
- Cycle breakdown algorithm from Step 2

### Actions

**3.1 Apply Cycle Breakdown Algorithm**

Actions:
- For each phase, number as X (1, 2, 3, ...)
- For each increment within phase, number as Y (1, 2, 3, ...)
- Generate Cycle X.Y definitions

Logic: See Step 2 algorithm (Phase 2: Feature Decomposition)

**3.2 Generate RED Specifications**

For each cycle:
- Define test to write
- Specify expected failure message
- Explain why it will fail
- Provide verification command

Logic: See Step 2 algorithm (Phase 3.1: RED Specification Generation)

**3.3 Generate GREEN Specifications**

For each cycle:
- Define minimal implementation
- Specify file changes
- Provide verification commands
- Include regression check

Logic: See Step 2 algorithm (Phase 3.2: GREEN Specification Generation)

**3.4 Assign Dependencies**

For each cycle:
- Default: Sequential within phase
- Check design for explicit cross-phase dependencies
- Mark regressions where applicable

Logic: See Step 2 algorithm (Phase 3.3: Dependency Assignment)

**3.5 Generate Stop Conditions**

For each cycle:
- Include standard stop conditions template
- Add cycle-specific conditions if needed
- Define escalation protocol

Logic: See Step 2 algorithm (Phase 3.4: Stop Conditions Generation)

**3.6 Build Dependency Graph**

Actions:
- Create adjacency list from dependencies
- Validate no circular dependencies
- Determine execution order

Error handling:
- Circular dependency detected → STOP, report cycle chain
- Invalid dependency reference → STOP, report missing cycle

### Outputs
- `cycles`: List of cycle definitions with RED/GREEN/Stop Conditions
- `dependency_graph`: Validated dependency structure
- `execution_order`: Sequential or parallel execution plan

### User Interaction Points
- None (automated processing)

---

## Phase 4: Runbook Generation

### Inputs
- All outputs from Phases 1-3
- Templates for frontmatter, metadata, context, cycles

### Actions

**4.1 Generate Frontmatter**

Template:
```yaml
---
name: {feature_name}
type: tdd
model: haiku
---
```

Actions:
- Fill feature_name from Phase 2
- Set type to "tdd"
- Set model to "haiku" (TDD execution default)

**4.2 Generate Title and Context Section**

Template:
```markdown
# {Feature Name} TDD Runbook

**Context**: {goal}

**Design**: {design_path}

**Status**: Draft
**Created**: {date}
```

Actions:
- Fill feature name (title case)
- Fill goal from Phase 2
- Fill design path from Phase 1
- Fill current date

**4.3 Generate Weak Orchestrator Metadata**

Template:
```markdown
## Weak Orchestrator Metadata

**Total Steps**: {cycle_count}

**Execution Model**:
- All cycles: Haiku (TDD execution)

**Step Dependencies**: {sequential|parallel|mixed}

**Error Escalation**:
- Haiku → User: Stop conditions triggered, regression failure

**Report Locations**: `plans/{feature_name}/reports/`

**Success Criteria**: All cycles complete with GREEN verification

**Prerequisites**:
{prerequisites_from_design}
```

Actions:
- Count cycles
- Determine dependency type from dependency_graph
- Extract prerequisites from design doc
- Fill feature_name

**4.4 Generate Common Context**

Template:
```markdown
## Common Context

**Key Design Decisions:**

{numbered_list_of_decisions_from_phase_2}

**Project Paths**:
{file_paths_from_design}

**Conventions**:
{tool_usage_rules}
{testing_patterns}
{error_handling}
```

Actions:
- Format design decisions as numbered list
- Extract file paths from design doc
- Include tool usage rules (Read/Write/Grep, no Bash file ops)
- Include project conventions from CLAUDE.md if available

**4.5 Generate Cycle Sections**

For each cycle in execution order:

Template:
```markdown
## Cycle {X.Y}: {cycle_name} {dependency_marker}

**Objective**: {clear_goal}

**Script Evaluation**: Direct execution (TDD task)

**Execution Model**: Haiku

**RED Phase:**

{test_to_write}

**Expected failure:**
```
{expected_error_message}
```

**Why it fails:** {explanation}

**Verify RED:** {verification_command}

---

**GREEN Phase:**

{minimal_implementation}

**Verify GREEN:** {verification_command}

**Verify no regression:** {regression_check_command}

---

**Stop Conditions:**

{standard_stop_conditions}

{custom_stop_conditions_if_applicable}

---
```

Actions:
- Fill from cycle definitions in Phase 3
- Add dependency markers ([DEPENDS: X.Y], [REGRESSION])
- Format code blocks and commands properly

**4.6 Generate Design Decisions Section**

Template:
```markdown
## Design Decisions

{decisions_from_design_with_rationale}
```

Actions:
- Copy design decisions from Phase 2
- Format consistently

**4.7 Generate Dependencies Section**

Template:
```markdown
## Dependencies

**Before This Runbook**:
{prerequisites}

**After This Runbook**:
{deliverables}
```

Actions:
- Extract prerequisites from design
- Infer deliverables from cycles

**4.8 Write Runbook File**

Actions:
- Combine all sections
- Write to `plans/{feature_name}/runbook.md`
- Use Write tool (new file)

Error handling:
- Path already exists → Ask user: "Overwrite existing runbook?"
- Permission denied → STOP, report error
- Write fails → STOP, report error

### Outputs
- `runbook_path`: Absolute path to generated runbook
- `runbook_content`: Full runbook content

### User Interaction Points
- Confirm overwrite if runbook already exists

---

## Phase 5: Validation

### Inputs
- `runbook_path` from Phase 4
- `runbook_content` from Phase 4

### Actions

**5.1 Verify Runbook Format**

Checks:
- Valid YAML frontmatter
- All required sections present
- Cycle headers match `## Cycle X.Y:` pattern
- No duplicate cycle IDs

Actions:
- Parse frontmatter as YAML
- Check for Weak Orchestrator Metadata section
- Check for Common Context section
- Regex match all cycle headers
- Verify no duplicates

Error handling:
- Invalid YAML → STOP, report error, offer to fix
- Missing section → STOP, report missing section
- Invalid cycle headers → STOP, report format issue
- Duplicate IDs → STOP, report duplicates

**5.2 Check prepare-runbook.py Compatibility**

Actions:
- Verify prepare-runbook.py exists
- Simulate parsing (regex match cycle headers)
- Confirm `type: tdd` in frontmatter

Error handling:
- prepare-runbook.py not found → WARNING, report path
- Parsing would fail → STOP, report compatibility issue

**5.3 Validate Dependencies**

Actions:
- Run topological sort on dependency graph
- Check all references are valid
- Verify no circular dependencies

Error handling:
- Should have been caught in Phase 3, but double-check
- Any issues → STOP, report

**5.4 Generate Success Report**

Content:
- Runbook path
- Cycle count
- Dependency structure (sequential/parallel)
- Next action guidance

Template:
```
TDD runbook created successfully!

**Location**: {runbook_path}
**Cycles**: {count}
**Dependencies**: {structure}

**Next steps**:
1. Review runbook at {runbook_path}
2. Run prepare-runbook.py to generate execution artifacts:
   python3 agent-core/bin/prepare-runbook.py {runbook_path}
3. Execute with /orchestrate or individual cycle files

**Execution artifacts** (after prepare-runbook.py):
- Agent baseline: .claude/agents/{feature_name}-task.md
- Cycle files: plans/{feature_name}/steps/cycle-{X}-{Y}.md
- Orchestrator plan: plans/{feature_name}/orchestrator-plan.md
```

**5.5 Report to User**

Actions:
- Display success report
- Provide runbook path
- Suggest next actions

### Outputs
- Success report displayed to user
- Runbook ready for prepare-runbook.py processing

### User Interaction Points
- Display final report
- Wait for user to proceed with prepare-runbook.py

---

## Integration with prepare-runbook.py

### Runbook → Preparation Flow

```
1. /plan-tdd generates: plans/{name}/runbook.md
   - Frontmatter: type: tdd
   - Cycles: ## Cycle X.Y: format

2. User runs: python3 agent-core/bin/prepare-runbook.py plans/{name}/runbook.md
   - Parses frontmatter (type: tdd → use tdd-task.md baseline)
   - Extracts Common Context
   - Splits cycles into individual files

3. prepare-runbook.py generates:
   - .claude/agents/{name}-task.md (baseline + common context)
   - plans/{name}/steps/cycle-X-Y.md (individual cycles)
   - plans/{name}/orchestrator-plan.md (execution index)

4. User executes cycles:
   - /orchestrate plans/{name}/orchestrator-plan.md
   - OR: Direct cycle invocation with plan-specific agent
```

### Compatibility Requirements

**Runbook must have:**
- `type: tdd` in frontmatter
- `## Weak Orchestrator Metadata` section
- `## Common Context` section
- Cycle headers: `## Cycle X.Y: {name}`

**prepare-runbook.py expectations:**
- Can parse YAML frontmatter
- Can extract sections by H2 headers
- Can parse cycle IDs with regex: `## Cycle (\d+)\.(\d+):`
- Has access to `agent-core/agents/tdd-task.md` baseline

**Validation ensures:**
- All requirements met
- No breaking format issues
- Clean extraction guaranteed

---

## Error Handling Per Phase

### Phase 1: Intake
- File not found → STOP, report path
- Invalid markdown → STOP, report parsing error
- Not TDD mode → Confirm with user

### Phase 2: Analysis
- No goal → STOP, ask user
- Unresolved confirmations → STOP, report list
- No structure → STOP, ask for clarification

### Phase 3: Cycle Planning
- Circular dependency → STOP, report chain
- Invalid reference → STOP, report missing cycle
- Empty cycle → WARNING, skip or fold into next

### Phase 4: Runbook Generation
- Path exists → Ask user to overwrite
- Write fails → STOP, report error

### Phase 5: Validation
- Format error → STOP, offer to fix
- Compatibility issue → STOP, report details

**General principle:** Fail fast, clear messages, actionable guidance

---

## User Interaction Summary

### Required Interactions
1. **Ambiguous TDD mode** → Confirm TDD vs general runbook
2. **Unresolved confirmations** → Resolve before proceeding
3. **Runbook exists** → Confirm overwrite

### Optional Interactions
1. **Large cycle count** (>20) → Confirm expected size
2. **Multiple design candidates** → Confirm which to use

### No Interaction Needed
- Standard TDD design doc → Fully automated
- All decisions resolved → Straight through to runbook

---

## Performance Characteristics

### Time Complexity
- Phase 1 (Intake): O(1) - single file read
- Phase 2 (Analysis): O(n) - linear scan of design content
- Phase 3 (Cycle Planning): O(n²) - dependency graph validation
- Phase 4 (Runbook Generation): O(n) - linear cycle generation
- Phase 5 (Validation): O(n) - linear validation checks

**Total**: O(n²) dominated by dependency validation

**Typical execution**: <2 seconds for 20 cycles

### Space Complexity
- Design content: O(k) where k = design file size
- Cycles: O(n) where n = cycle count
- Dependency graph: O(n²) worst case (fully connected)

**Typical memory**: <10 MB for large runbooks (50 cycles)

---

## Process Flow Summary

```
┌─────────────────────────────────────────────────────────────┐
│ Phase 1: INTAKE                                             │
│ - Read design doc                                           │
│ - Read CLAUDE.md (optional)                                 │
│ - Validate basic structure                                  │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│ Phase 2: ANALYSIS                                           │
│ - Extract goal & feature name                               │
│ - Extract design decisions                                  │
│ - Check for unresolved items → STOP if found               │
│ - Identify phases & increments                              │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│ Phase 3: CYCLE PLANNING                                     │
│ - Apply breakdown algorithm                                 │
│ - Generate RED specifications                               │
│ - Generate GREEN specifications                             │
│ - Assign dependencies                                       │
│ - Build & validate dependency graph → STOP if circular     │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│ Phase 4: RUNBOOK GENERATION                                 │
│ - Generate frontmatter                                      │
│ - Generate metadata section                                 │
│ - Generate common context                                   │
│ - Generate cycle sections                                   │
│ - Write to plans/{name}/runbook.md                          │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│ Phase 5: VALIDATION                                         │
│ - Verify runbook format                                     │
│ - Check prepare-runbook.py compatibility                    │
│ - Validate dependencies                                     │
│ - Generate success report                                   │
│ - Report next steps to user                                 │
└─────────────────────────────────────────────────────────────┘
```

---

**Process flow design complete. Size: 17829 bytes**
