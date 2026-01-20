# Step 2: Cycle Breakdown Algorithm Design

**Date**: 2026-01-20
**Purpose**: Define algorithm for decomposing design documents into atomic TDD cycles

---

## Algorithm Overview

The cycle breakdown algorithm transforms a design document into a structured TDD runbook with numbered cycles. It operates in four phases: Input Validation, Feature Decomposition, Cycle Definition, and Validation.

---

## Phase 1: Input Validation

### 1.1 Design Document Structure Check

**Inputs:**
- Design document path (from user or default `plans/[name]/design.md`)

**Checks:**
- File exists and is readable
- Contains valid markdown
- Has identifiable sections (## headers)

**Actions:**
- Read design document
- Parse markdown structure
- Identify section headers

**Error Conditions:**
- File not found → STOP, report path
- Not valid markdown → STOP, report parsing error
- Empty file → STOP, report empty document

### 1.2 TDD-Specific Sections Check

**Required elements for TDD mode:**
- Goal statement or feature description
- Design decisions or implementation approach
- Behavioral increments or phases

**Optional but valuable:**
- Pre-implementation spike section
- Expected test count
- RED-GREEN-REFACTOR protocol (can use defaults)

**Actions:**
- Scan for goal/objective statement
- Identify design decisions section
- Locate implementation phases or behavioral increments
- Check for TDD protocol section (use defaults if missing)

**Error Conditions:**
- No goal statement → STOP, ask user for clarification
- No design decisions → WARNING, proceed with empty Common Context
- No implementation phases → Attempt to infer from content, or STOP if unclear

### 1.3 Unresolved Confirmations Check

**Pattern to search:**
- `(REQUIRES CONFIRMATION)`
- `(TBD)`
- `(TODO: decide)`
- `[DECIDE:]`

**Actions:**
- Grep for confirmation markers
- Extract context around each marker
- List all unresolved items

**Error Conditions:**
- Any unresolved confirmations found → STOP, report list to user
- User must resolve before continuing

**Rationale:** TDD cycles require fully-resolved design decisions. Unresolved items block effective RED/GREEN definition.

---

## Phase 2: Feature Decomposition

### 2.1 Phase Identification

**Strategy:**
- Look for top-level sections in design doc (## Phase N, ## Feature Area, etc.)
- If no explicit phases, treat entire feature as single phase
- Each phase becomes "X" in X.Y numbering

**Heuristics:**
- Section with word "Phase" → explicit phase
- Section describing distinct feature area → implicit phase
- Subsections under same parent → increments within phase

**Actions:**
- Parse H2 headers for phase markers
- Assign phase numbers (1, 2, 3, ...)
- Extract phase descriptions

**Example mapping:**
```
## Phase 1: Setup Errors → Phase 1
## Phase 2: Pass Reporting → Phase 2
## Authentication → Phase 1 (implicit)
## Authorization → Phase 2 (implicit)
```

### 2.2 Behavioral Increment Identification

**Strategy:**
- Within each phase, identify discrete behavioral changes
- Each increment becomes "Y" in X.Y numbering
- Look for action verbs: "Add", "Implement", "Create", "Test"

**Heuristics:**
- H3 headers under phase → likely increments
- Bullet points describing features → possible increments
- Test scenarios → direct mapping to cycles
- Design decisions with implementation → increment per decision

**Actions:**
- Parse H3 headers or bullets within each phase
- Extract increment descriptions
- Assign increment numbers (1, 2, 3, ...)

**Example mapping:**
```
## Phase 1: Setup Errors
### Add setup error test fixture → Cycle 1.1
### Separate errors from failures → Cycle 1.2
### Test default mode shows both → Cycle 1.3
```

### 2.3 Granularity Adjustment

**Criteria for splitting increments:**
- Increment has >3 distinct assertions
- Increment combines multiple behaviors
- Increment has complex setup + verification
- Increment has multiple error paths

**Criteria for combining increments:**
- Increment has single assertion
- Increment is trivial setup (fixture creation)
- Increment is purely documentation

**Actions:**
- Evaluate each increment for complexity
- Split complex increments into sub-cycles
- Combine trivial increments where logical
- Maintain 1-3 assertion guideline

**Example:**
```
Original: "Implement authentication with Google and GitHub"
Split:
- Cycle 2.1: Implement Google OAuth
- Cycle 2.2: Implement GitHub OAuth
- Cycle 2.3: Test provider selection logic
```

---

## Phase 3: Cycle Definition

### 3.1 RED Specification Generation

**For each cycle, generate:**

**Test Description:**
- What to test
- Expected behavior
- Test file location

**Expected Failure:**
- Specific error message
- Why it will fail
- How to verify RED

**Template:**
```markdown
**RED Phase:**

**Test:** [What to test and where]

**Expected failure:**
```
[Exact error message or pattern]
```

**Why it fails:** [Explanation of missing implementation]

**Verify RED:** [Command to run, what to observe]
```

**Extraction logic:**
- Parse increment description for behavior
- Infer test location from project structure
- Generate assertion based on expected behavior
- Predict failure message based on assertion type

**Example:**
```markdown
**RED Phase:**

**Test:** Add test in `tests/test_errors.py` asserting "## Errors" section exists

**Expected failure:**
```
AssertionError: Expected '## Errors' section for setup/teardown errors
```

**Why it fails:** Current implementation puts all failures in "## Failures" section

**Verify RED:** Run `pytest tests/test_errors.py::test_errors_separate -v`
- Must fail with assertion error
- If passes, STOP - feature already implemented
```

### 3.2 GREEN Specification Generation

**For each cycle, generate:**

**Implementation Description:**
- What to implement (minimal)
- Where to make changes
- Specific code actions

**Verification:**
- How to verify GREEN
- Regression check command

**Template:**
```markdown
**GREEN Phase:**

**Implementation:** [Minimal code to make test pass]

**Changes:**
- File: [path]
  Action: [specific change]

**Verify GREEN:** [Command to run, expected result]

**Verify no regression:** [Command to check existing tests]
```

**Extraction logic:**
- Infer implementation from design decisions
- Identify file locations from project structure
- Specify minimal change to pass test
- Default regression command to full test suite

**Example:**
```markdown
**GREEN Phase:**

**Implementation:** Add separate errors bucket and section generator

**Changes:**
- File: `src/plugin.py`
  Action: Add `self.errors = []` list
  Action: Modify categorization to split setup errors
  Action: Add `_generate_errors()` method
  Action: Update report builder to include errors section

**Verify GREEN:** Run `pytest tests/test_errors.py::test_errors_separate -v`
- Must pass

**Verify no regression:** Run `pytest tests/`
- All existing tests must pass
```

### 3.3 Dependency Assignment

**Rules:**
- Default: Sequential within phase (1.1 → 1.2 → 1.3)
- Cross-phase: Only if explicitly required by design
- Parallel: Only if increments are independent

**Dependency markers:**
- `[DEPENDS: X.Y]` - Explicit dependency
- `[REGRESSION]` - No dependency, tests existing behavior
- No marker - Sequential dependency on previous cycle in phase

**Assignment logic:**
1. Within phase: Assume each cycle depends on previous (1.1 → 1.2 → 1.3)
2. Check design doc for explicit dependencies
3. Mark regressions if design indicates existing behavior
4. Allow parallel execution only if design explicitly indicates independence

**Example:**
```
Cycle 1.1: Add test fixture [No dependency - first in phase]
Cycle 1.2: Test errors section [DEPENDS: 1.1] (implicit - sequential)
Cycle 1.3: Test default mode [DEPENDS: 1.2] (implicit - sequential)
Cycle 2.1: Test pass reporting [DEPENDS: 1.3] (cross-phase - uses error separation)
Cycle 2.2: Test verbose mode [REGRESSION] (tests existing behavior)
```

### 3.4 Stop Conditions Generation

**Standard template for all cycles:**

```markdown
**Stop Conditions:**

**STOP IMMEDIATELY if:**
- Test passes on first run (expected RED failure)
- Test failure message doesn't match expected
- Test passes after partial GREEN implementation
- Any existing test breaks (regression failure)
- Test requires changes to cycle scope

**Actions when stopped:**
1. Document what happened in execution report
2. If test passes unexpectedly:
   - Check if feature already implemented
   - If yes: Mark cycle as `[REGRESSION]`, proceed
   - If no: Fix test to ensure RED, retry
3. If regression detected:
   - STOP execution
   - Report which tests broke
   - Escalate to user
4. If scope unclear:
   - STOP execution
   - Report ambiguity
   - Request clarification
```

**Custom conditions (cycle-specific):**
- Add for complex cycles with multiple steps
- Add for cycles with external dependencies
- Add for cycles with performance requirements

**Example custom condition:**
```markdown
**Additional stop conditions for Cycle 3.2 (Database Integration):**
- Database connection fails → Check credentials, report error
- Schema migration fails → Check migration script, report error
- Performance >100ms → Optimize query, document results
```

---

## Phase 4: Validation

### 4.1 Cycle ID Validation

**Checks:**
- All cycle IDs match `X.Y` pattern (e.g., `1.1`, `2.3`, `10.5`)
- No duplicate cycle IDs
- No gaps in numbering (1.1, 1.2, 1.3 - no skipping)
- Valid numbering starts at 1 (not 0)

**Actions:**
- Extract all cycle IDs
- Parse with regex: `^(\d+)\.(\d+)$`
- Sort and check sequence
- Report any violations

**Error conditions:**
- Invalid format → STOP, report invalid IDs
- Duplicates → STOP, report duplicates
- Gaps → WARNING (acceptable), document
- Starting at 0 → STOP, renumber from 1

### 4.2 Dependency Validation

**Checks:**
- All `[DEPENDS: X.Y]` references point to valid cycle IDs
- No circular dependencies (A → B → A)
- Dependencies don't reference future cycles (topological order)
- No self-dependencies (1.1 depends on 1.1)

**Actions:**
- Build dependency graph
- Topological sort to detect cycles
- Verify all references exist
- Check execution order feasibility

**Error conditions:**
- Invalid reference → STOP, report missing cycle
- Circular dependency → STOP, report cycle chain
- Forward dependency → STOP, report ordering issue
- Self-dependency → STOP, report cycle ID

**Algorithm for cycle detection:**
1. Build adjacency list from dependencies
2. Perform depth-first search with visited/visiting states
3. If visiting node encountered again → cycle detected
4. Report cycle chain for debugging

### 4.3 Content Validation

**Checks:**
- Each cycle has RED Phase section
- Each cycle has GREEN Phase section
- Each cycle has Stop Conditions section
- Objective is clear and measurable

**Actions:**
- Parse each cycle structure
- Check for required sections
- Validate section content (not empty)
- Check objective clarity

**Error conditions:**
- Missing RED → STOP, report cycle ID
- Missing GREEN → STOP, report cycle ID
- Missing Stop Conditions → WARNING, use default
- Unclear objective → WARNING, document for review

### 4.4 prepare-runbook.py Compatibility Check

**Checks:**
- Frontmatter has `type: tdd`
- Weak Orchestrator Metadata section present
- Common Context section present
- Cycle headers are H2 level (`## Cycle X.Y:`)
- Cycle IDs parseable by regex `## Cycle (\d+)\.(\d+):`

**Actions:**
- Simulate prepare-runbook.py parsing
- Verify section extraction would succeed
- Check header levels
- Validate frontmatter YAML

**Error conditions:**
- Wrong header level → STOP, report structure issue
- Missing sections → STOP, report missing metadata
- Invalid frontmatter → STOP, report YAML error

---

## Edge Cases Handling

### 1. Single-Cycle Feature

**Scenario:** Design has only one behavioral increment

**Handling:**
- Valid - create Cycle 1.1 only
- Include all sections
- No dependencies
- Proceed normally

**Validation:** Ensure cycle is well-defined despite being sole cycle

### 2. No Dependencies Between Cycles

**Scenario:** All cycles are independent (rare for TDD)

**Handling:**
- Mark cycles as parallel-safe
- Document in Weak Orchestrator Metadata
- Enable parallel execution if orchestrator supports

**Validation:** Verify truly independent (no shared state)

### 3. All Cycles Are Regressions

**Scenario:** Feature already implemented, only tests needed

**Handling:**
- Valid - mark all cycles as `[REGRESSION]`
- Adjust stop conditions (no RED expected)
- Document in Common Context

**Validation:** Ensure tests are comprehensive

### 4. Cycle Depends on Future Cycle

**Scenario:** Dependency graph has forward reference (2.1 depends on 3.1)

**Handling:**
- Invalid - STOP execution
- Report ordering issue
- Suggest renumbering or removing dependency

**Validation:** Topological sort catches this

### 5. Empty Cycle (No Assertions)

**Scenario:** Increment is pure setup, no testable behavior

**Handling:**
- Option 1: Skip cycle (setup folded into next cycle)
- Option 2: Create setup-only cycle (no RED/GREEN, just GREEN)
- Prefer Option 1 to maintain TDD discipline

**Validation:** Warn if cycle has no assertions

### 6. Complex Cycle (>5 Assertions)

**Scenario:** Increment tests multiple behaviors

**Handling:**
- Suggest splitting into sub-cycles
- Document complexity in cycle
- Proceed if user confirms

**Validation:** Warn if cycle exceeds complexity threshold

### 7. Missing Design Decisions

**Scenario:** Design doc has no "Design Decisions" section

**Handling:**
- Attempt to extract decisions from content
- Create minimal Common Context
- Warn user about missing context

**Validation:** Check if extraction was successful

---

## Output Specifications

### Runbook Structure

```markdown
---
name: [feature-name]
type: tdd
model: haiku
---

# [Feature Name] TDD Runbook

**Context**: [Brief description]

**Design**: [Reference to design doc]

**Status**: Draft
**Created**: YYYY-MM-DD

---

## Weak Orchestrator Metadata

**Total Steps**: [N cycles]

**Execution Model**:
- All cycles: Haiku (TDD execution)

**Step Dependencies**: [Sequential / Parallel / Mixed]

**Error Escalation**:
- Haiku → User: Stop conditions triggered, regression failure

**Report Locations**: `plans/[name]/reports/`

**Success Criteria**: All cycles complete with GREEN verification

**Prerequisites**:
- [List from design doc]

---

## Common Context

[Design decisions, file paths, conventions from design doc]

---

## Cycle 1.1: [Name]

[Full cycle content]

---

## Cycle 1.2: [Name] [DEPENDS: 1.1]

[Full cycle content]

---

[... more cycles ...]

---

## Design Decisions

[From design doc]

---

## Dependencies

**Before This Runbook**:
- [Prerequisites]

**After This Runbook**:
- [Deliverables]
```

---

## Algorithm Summary

**Input:** Design document path
**Output:** TDD runbook at `plans/[name]/runbook.md`

**Steps:**
1. **Validate** design doc structure and resolve confirmations
2. **Decompose** into phases and increments
3. **Define** RED/GREEN/Stop Conditions for each cycle
4. **Validate** cycle IDs, dependencies, and content
5. **Generate** runbook with frontmatter, metadata, context, and cycles

**Error handling:** Fail fast with clear messages, escalate to user

**Complexity:** O(n²) for dependency validation (topological sort), O(n) for other phases

**Success:** Valid TDD runbook compatible with prepare-runbook.py

---

**Algorithm design complete. Size: 15478 bytes**
