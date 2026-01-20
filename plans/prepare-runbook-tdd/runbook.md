---
name: prepare-runbook-tdd
model: sonnet
---

# Add TDD Cycle Format Support to prepare-runbook.py

**Context**: Extend `prepare-runbook.py` to support TDD runbook format with cycle detection, parsing, and artifact generation.

**Source**: Planning request from `plans/tdd-integration/reports/step-6-planning-request.md`
**Design**: `plans/tdd-integration/design.md` § TDD Runbook Structure (lines 105-153) and § prepare-runbook.py Updates (lines 326-352)

**Status**: Draft
**Created**: 2026-01-20

---

## Weak Orchestrator Metadata

**Total Steps**: 9

**Execution Model**:
- Steps 1-9: Sonnet (code analysis, design, and implementation)

**Step Dependencies**:
- Sequential (each step builds on previous)
- Step 9 depends on Steps 3-8 (all implementation complete)

**Error Escalation**:
- Sonnet → User: Unexpected file structure, validation failures, integration test failures

**Report Locations**: `plans/prepare-runbook-tdd/reports/step-N-report.md`

**Success Criteria**:
- `prepare-runbook.py` successfully processes TDD runbook format
- Generates cycle files (not step files) for TDD runbooks
- Uses `tdd-task.md` baseline for TDD runbooks
- Maintains backward compatibility with general runbooks
- Integration test passes on `plans/tdd-integration/runbook.md`

**Prerequisites**:
- `agent-core/bin/prepare-runbook.py` exists (✓ current implementation)
- `agent-core/agents/tdd-task.md` exists (✓ created in Step 3 of tdd-integration)
- `plans/tdd-integration/runbook.md` exists (✓ test runbook available)

---

## Common Context

**Objective**: Add TDD cycle format support to `prepare-runbook.py` while maintaining backward compatibility with general runbook processing.

**Key Constraints**:
- Maintain existing CLI interface (no breaking changes)
- Preserve general runbook processing (## Step N: format)
- Use same output structure (.claude/agents/, plans/*/steps/, orchestrator-plan.md)
- Follow existing code patterns and style

**Project Paths**:
- Script: `agent-core/bin/prepare-runbook.py` (~290 lines current)
- TDD baseline: `agent-core/agents/tdd-task.md`
- General baseline: `agent-core/agents/quiet-task.md`
- Test runbook: `plans/tdd-integration/runbook.md`

**TDD Runbook Format**:
- Frontmatter: `type: tdd` (vs `type: general` or absent)
- Cycle headers: `## Cycle X.Y: [name]` (vs `## Step N:`)
- Cycle files: `cycle-X-Y.md` (vs `step-N.md`)
- Baseline: `tdd-task.md` (vs `quiet-task.md`)

**Conventions**:
- Use existing function patterns (`extract_sections`, `generate_step_file`)
- Error messages start with "ERROR: " or "WARNING: "
- Validate structure before generation
- Report counts and paths in output

**Tool Usage Reminder**:
- Use **Read** instead of `cat`
- Use **Edit** for file modifications
- Use **Write** for new files
- Use **Bash** only for running scripts
- Use **Grep** for code searches

---

## Step 1: Analyze Current Implementation

**Objective**: Understand current `prepare-runbook.py` structure, functions, and control flow.

**Script Evaluation**: Prose description (analysis task)

**Execution Model**: Sonnet

**Implementation**:

1. Read `agent-core/bin/prepare-runbook.py`
2. Identify key functions and their responsibilities:
   - `parse_frontmatter()` - Extract YAML metadata
   - `extract_sections()` - Parse step sections from runbook
   - `read_baseline_agent()` - Load baseline template
   - `generate_step_file()` - Create individual step files
   - `generate_agent_frontmatter()` - Create plan-specific agent
   - `validate_and_create()` - Main orchestration
   - `derive_paths()` - Calculate output paths
3. Document current step pattern: `r'^## Step\s+([\d.]+):\s*(.*)'`
4. Document current file generation logic
5. Identify integration points for TDD support
6. Create analysis document with:
   - Function inventory
   - Current control flow
   - Extension points for TDD support
   - Shared logic that can be reused

**Expected Outcome**: Clear understanding of code structure and where TDD logic integrates.

**Unexpected Result Handling**:
- If structure differs significantly from planning request assumptions → STOP and report discrepancies

**Error Conditions**:
- File not found → Escalate to user
- Unable to understand code structure → Escalate to user

**Validation**:
- Analysis document covers all functions mentioned in planning request
- Integration points identified for each TDD requirement

**Success Criteria**:
- Analysis document created at report path
- Document includes function inventory with line numbers
- Document includes integration points for 6 TDD requirements

**Report Path**: `plans/prepare-runbook-tdd/reports/step-1-analysis.md`

---

## Step 2: Design Cycle Detection and Parsing Logic

**Objective**: Design regex patterns, control flow, and data structures for TDD cycle detection and parsing.

**Script Evaluation**: Prose description (design task)

**Execution Model**: Sonnet

**Implementation**:

1. Design cycle detection regex:
   - Pattern for `## Cycle X.Y: [name]` format
   - Capture groups for major (X), minor (Y), and name
   - Differentiation from step pattern
2. Design conditional extraction logic:
   - Input: runbook frontmatter with `type` field
   - Control flow: if `type: tdd` → extract cycles, else → extract steps
   - Shared parsing logic where possible
3. Design cycle numbering validation:
   - Sequential major numbers (1, 2, 3...)
   - Sequential minor numbers within major (1.1, 1.2, 1.3...)
   - Gap detection algorithm
   - Duplicate detection algorithm
4. Design cycle content extraction:
   - Full cycle section (including subsections)
   - RED/GREEN/REFACTOR phase preservation
   - Stop conditions inclusion
5. Design data structure for cycles:
   - Mirror existing step data structure
   - Fields: cycle_number, major, minor, name, content
6. Document design decisions:
   - Why specific regex patterns chosen
   - How validation will work
   - Error messages for validation failures

**Expected Outcome**: Complete design specification for cycle detection and parsing.

**Unexpected Result Handling**:
- If requirements conflict with existing code patterns → document alternatives and escalate

**Error Conditions**:
- Design conflicts with existing architecture → Escalate to user

**Validation**:
- Design covers all requirements from planning request § 3.2
- Regex pattern tested with example cycle headers
- Validation algorithm handles edge cases

**Success Criteria**:
- Design document created at report path
- Document includes tested regex pattern
- Document includes validation algorithm pseudocode
- Document includes example data structures

**Report Path**: `plans/prepare-runbook-tdd/reports/step-2-design.md`

---

## Step 3: Implement Cycle Detection and Extraction

**Objective**: Modify `extract_sections()` or create `extract_cycles()` to parse TDD runbook cycle structure.

**Script Evaluation**: Prose description (50-80 line modification)

**Execution Model**: Sonnet

**Implementation**:

1. Create new function `extract_cycles(content)` based on `extract_sections()` pattern:
   - Use cycle regex from Step 2 design
   - Parse cycle headers and extract full content
   - Return list of cycle dictionaries with fields: major, minor, number, title, content
2. Modify `extract_sections()` or create wrapper to route based on runbook type:
   - If TDD runbook → call `extract_cycles()`
   - If general runbook → call existing step extraction logic
3. Implement cycle numbering validation:
   - Check sequential major numbers
   - Check sequential minor numbers within major
   - Detect gaps and duplicates
   - Return validation errors
4. Add error handling:
   - No cycles found in TDD runbook
   - Malformed cycle headers
   - Non-sequential numbering
5. Test regex pattern with sample cycle headers:
   - `## Cycle 1.1: User can authenticate`
   - `## Cycle 2.3: System validates token`

**Expected Outcome**: Function that extracts cycles from TDD runbooks with validation.

**Unexpected Result Handling**:
- If cycle structure in test runbook doesn't match pattern → report discrepancy and STOP

**Error Conditions**:
- Regex fails to match valid cycle headers → Revise pattern
- Validation logic incorrect → Fix algorithm

**Validation**:
- Function returns list of cycle dictionaries
- Validation catches gaps and duplicates
- Error messages clear and actionable

**Success Criteria**:
- `extract_cycles()` function implemented
- Validation logic implemented
- At least 3 error conditions handled
- Function tested with sample data (documented in report)

**Report Path**: `plans/prepare-runbook-tdd/reports/step-3-report.md`

---

## Step 4: Implement TDD Metadata Detection

**Objective**: Extend frontmatter parsing to detect `type: tdd` field and set runbook type flag.

**Script Evaluation**: Prose description (20-30 line modification)

**Execution Model**: Sonnet

**Implementation**:

1. Review existing `parse_frontmatter()` function
2. Add `type` field extraction from frontmatter:
   - Default value: `general` (if absent)
   - Valid values: `tdd`, `general`
   - Store in frontmatter dictionary
3. Add validation for type field:
   - Warn if unknown type value
   - Default to `general` for unknown values
4. Pass runbook type to downstream functions:
   - Modify function signatures if needed
   - Propagate type through call chain
5. Add error message for TDD runbook without type field:
   - "WARNING: TDD runbook detected (cycle headers) but missing 'type: tdd' in frontmatter"

**Expected Outcome**: Frontmatter parsing detects and validates runbook type.

**Unexpected Result Handling**:
- If frontmatter structure differs from expected → report and STOP

**Error Conditions**:
- Invalid YAML syntax → Report clear error
- Unknown type value → Warn and default to general

**Validation**:
- Type field extracted correctly
- Default behavior preserves backward compatibility
- Warning issued for missing type in TDD runbook

**Success Criteria**:
- `parse_frontmatter()` returns type field
- Type validation implemented
- Backward compatibility maintained (no type field → general)
- Changes tested with sample frontmatter (documented in report)

**Report Path**: `plans/prepare-runbook-tdd/reports/step-4-report.md`

---

## Step 5: Implement Conditional Baseline Selection

**Objective**: Modify `read_baseline_agent()` to load `tdd-task.md` for TDD runbooks and `quiet-task.md` for general runbooks.

**Script Evaluation**: Prose description (15-20 line modification)

**Execution Model**: Sonnet

**Implementation**:

1. Review existing `read_baseline_agent()` function
2. Add `runbook_type` parameter to function signature
3. Implement conditional baseline selection:
   - If `runbook_type == "tdd"` → load `agent-core/agents/tdd-task.md`
   - If `runbook_type == "general"` → load `agent-core/agents/quiet-task.md`
   - If unknown type → default to `quiet-task.md` and warn
4. Update all calls to `read_baseline_agent()` to pass runbook type
5. Add error handling for missing baseline files:
   - "ERROR: Baseline agent not found: [path]"
   - Exit with clear error message

**Expected Outcome**: Baseline selection conditional on runbook type.

**Unexpected Result Handling**:
- If baseline file missing → Clear error and STOP

**Error Conditions**:
- Baseline file not found → Report path and exit
- Invalid runbook type → Warn and use default

**Validation**:
- Correct baseline loaded for TDD runbooks
- Correct baseline loaded for general runbooks
- Error message clear when baseline missing

**Success Criteria**:
- `read_baseline_agent()` accepts runbook_type parameter
- Conditional logic implemented
- Error handling for missing baselines
- All callers updated to pass type
- Changes tested (documented in report)

**Report Path**: `plans/prepare-runbook-tdd/reports/step-5-report.md`

---

## Step 6: Implement Cycle File Generation

**Objective**: Create `generate_cycle_file()` function to generate cycle files with pattern `cycle-X-Y.md`.

**Script Evaluation**: Prose description (30-40 line modification)

**Execution Model**: Sonnet

**Implementation**:

1. Create `generate_cycle_file()` function modeled on `generate_step_file()`:
   - Parameters: cycle_data, runbook_name, steps_dir
   - File naming: `cycle-{major}-{minor}.md` (e.g., `cycle-1-1.md`)
   - Location: Same `plans/<runbook-name>/steps/` directory
2. Implement cycle file template:
   ```markdown
   # Cycle {major}.{minor}

   **Plan**: `plans/{runbook_name}/runbook.md`
   **Common Context**: See plan file for context

   ---

   ## Cycle {major}.{minor}: {name}

   {cycle_content}
   ```
3. Extract cycle content from parsed cycle data:
   - Include full cycle section
   - Preserve all subsections (RED/GREEN/REFACTOR/Stop Conditions)
   - Maintain markdown formatting
4. Modify main generation logic to route based on runbook type:
   - If TDD → use `generate_cycle_file()`
   - If general → use `generate_step_file()`
5. Update output messages:
   - "✓ Created cycle: plans/{runbook}/steps/cycle-{X}-{Y}.md"

**Expected Outcome**: Cycle files generated for TDD runbooks instead of step files.

**Unexpected Result Handling**:
- If cycle content malformed → Report and STOP

**Error Conditions**:
- File write failure → Report error and exit
- Invalid cycle data → Report and exit

**Validation**:
- Cycle files created in correct location
- File naming matches pattern `cycle-X-Y.md`
- File content includes cycle header and full content
- Output messages accurate

**Success Criteria**:
- `generate_cycle_file()` function implemented
- Function creates correctly formatted cycle files
- Main logic routes to appropriate generator
- Output messages updated
- Changes tested (documented in report)

**Report Path**: `plans/prepare-runbook-tdd/reports/step-6-report.md`

---

## Step 7: Implement Cycle Validation

**Objective**: Add validation checks for TDD cycle structure (mandatory phases, stop conditions).

**Script Evaluation**: Prose description (40-60 line modification)

**Execution Model**: Sonnet

**Implementation**:

1. Create `validate_cycle_structure()` function:
   - Parameter: cycle content (string)
   - Check for mandatory subsections:
     - RED phase (heading or keyword)
     - GREEN phase (heading or keyword)
     - Stop conditions section
   - Return validation errors list
2. Implement subsection detection:
   - Search for "RED", "GREEN", "REFACTOR" keywords or headings
   - Search for "Stop Conditions" or similar
   - Case-insensitive matching
3. Add validation to cycle extraction process:
   - Call `validate_cycle_structure()` for each cycle
   - Collect validation errors
   - Report errors before generation
4. Implement error messages:
   - "ERROR: Cycle {X}.{Y} missing required section: RED phase"
   - "ERROR: Cycle {X}.{Y} missing required section: GREEN phase"
   - "ERROR: Cycle {X}.{Y} missing required section: Stop Conditions"
   - "WARNING: Cycle {X}.{Y} missing dependencies section"
5. Add validation summary output:
   - Report total cycles validated
   - Report total errors found
   - Stop if critical errors present

**Expected Outcome**: Validation ensures TDD cycles have required structure.

**Unexpected Result Handling**:
- If test runbook cycles don't pass validation → report and STOP (may need design adjustment)

**Error Conditions**:
- Missing mandatory sections → Report and exit
- Malformed cycle structure → Report and exit

**Validation**:
- Validation detects missing RED phase
- Validation detects missing GREEN phase
- Validation detects missing Stop Conditions
- Warning issued for missing dependencies (non-critical)

**Success Criteria**:
- `validate_cycle_structure()` function implemented
- Validation checks all mandatory sections
- Error messages clear and actionable
- Validation integrated into extraction process
- Changes tested (documented in report)

**Report Path**: `plans/prepare-runbook-tdd/reports/step-7-report.md`

---

## Step 8: Update Help Text and Error Messages

**Objective**: Update CLI help text, error messages, and output to reflect TDD support.

**Script Evaluation**: Prose description (20-30 line modification)

**Execution Model**: Sonnet

**Implementation**:

1. Update `main()` help text or usage string:
   ```
   Transforms runbook markdown into execution artifacts:
     - Plan-specific agent (.claude/agents/<runbook-name>-task.md)
     - Step/Cycle files (plans/<runbook-name>/steps/)
     - Orchestrator plan (plans/<runbook-name>/orchestrator-plan.md)

   Supports:
     - General runbooks (## Step N:)
     - TDD runbooks (## Cycle X.Y:, requires type: tdd in frontmatter)
   ```
2. Update error messages:
   - "ERROR: No steps found in general runbook"
   - "ERROR: No cycles found in TDD runbook"
   - "ERROR: TDD runbook missing 'type: tdd' in frontmatter"
3. Update success output summary:
   - Report runbook type (general/TDD)
   - Report steps or cycles count
   - Show appropriate file type (step-N.md vs cycle-X-Y.md)
4. Review all print statements and ensure consistency:
   - Use "step" for general runbooks
   - Use "cycle" for TDD runbooks
   - Clear distinction in output

**Expected Outcome**: Help text and messages reflect TDD support.

**Unexpected Result Handling**:
- If help text conflicts with actual behavior → revise text

**Error Conditions**:
- Inconsistent terminology → Fix all instances

**Validation**:
- Help text mentions both general and TDD runbooks
- Error messages use correct terminology
- Output summary shows correct type and counts

**Success Criteria**:
- Help text updated to mention TDD support
- At least 3 error messages updated
- Output summary reflects runbook type
- All terminology consistent (steps vs cycles)
- Changes documented in report

**Report Path**: `plans/prepare-runbook-tdd/reports/step-8-report.md`

---

## Step 9: Integration Test with TDD Runbook

**Objective**: Run modified `prepare-runbook.py` on existing TDD runbook and verify correct outputs.

**Script Evaluation**: Small script (≤25 lines)

**Execution Model**: Sonnet

**Implementation**:

```bash
#!/usr/bin/env bash
set -euo pipefail

echo "=== Integration Test: prepare-runbook.py with TDD Runbook ==="
echo ""

# Test runbook path
RUNBOOK="plans/tdd-integration/runbook.md"
echo "Test runbook: $RUNBOOK"
echo ""

# Run prepare-runbook.py
echo "Running prepare-runbook.py..."
python3 agent-core/bin/prepare-runbook.py "$RUNBOOK"
echo ""

# Verify outputs
echo "=== Verification ==="

# Check plan-specific agent uses tdd-task baseline
echo "1. Checking agent baseline..."
if grep -q "tdd-task.md" .claude/agents/tdd-integration-task.md; then
    echo "   ✓ Agent uses tdd-task.md baseline"
else
    echo "   ✗ ERROR: Agent does not use tdd-task baseline"
    exit 1
fi

# Check cycle files created (not step files)
echo "2. Checking cycle files..."
CYCLE_COUNT=$(ls plans/tdd-integration/steps/cycle-*.md 2>/dev/null | wc -l | tr -d ' ')
STEP_COUNT=$(ls plans/tdd-integration/steps/step-*.md 2>/dev/null | wc -l | tr -d ' ')

echo "   Cycle files: $CYCLE_COUNT"
echo "   Step files: $STEP_COUNT"

if [ "$CYCLE_COUNT" -gt 0 ] && [ "$STEP_COUNT" -eq 0 ]; then
    echo "   ✓ Cycle files created, no step files"
else
    echo "   ✗ ERROR: Expected cycle files, found $CYCLE_COUNT cycles and $STEP_COUNT steps"
    exit 1
fi

# Check orchestrator plan exists
echo "3. Checking orchestrator plan..."
if [ -f "plans/tdd-integration/orchestrator-plan.md" ]; then
    echo "   ✓ Orchestrator plan created"
else
    echo "   ✗ ERROR: Orchestrator plan not found"
    exit 1
fi

echo ""
echo "=== Integration Test: PASSED ==="
```

**Expected Outcome**: Script passes all verification checks.

**Unexpected Result Handling**:
- If any check fails → report which check failed, expected vs actual, and STOP

**Error Conditions**:
- Script execution failure → Report error and STOP
- Verification failure → Report expected vs actual and STOP

**Validation**:
- Agent uses `tdd-task.md` baseline (grep check)
- Cycle files created, not step files (file count check)
- Orchestrator plan exists (file existence check)
- Script returns exit code 0

**Success Criteria**:
- Integration test script executes without errors
- All 3 verification checks pass
- Output shows "Integration Test: PASSED"

**Report Path**: `plans/prepare-runbook-tdd/reports/step-9-report.md`

---

## Design Decisions

**Decision 1: Cycle File Location**
- Decision: Use same `plans/<runbook-name>/steps/` directory for cycle files
- Rationale: Maintains consistent structure, orchestrator pattern unchanged
- Alternative considered: Separate `cycles/` directory - rejected for simplicity

**Decision 2: Baseline Selection**
- Decision: Conditional loading based on frontmatter `type` field
- Rationale: Explicit declaration, clear intent, backward compatible
- Alternative considered: Auto-detect from headers - rejected as implicit

**Decision 3: Validation Timing**
- Decision: Validate during extraction, before file generation
- Rationale: Fail fast, clear error messages, no partial outputs
- Alternative considered: Validate during generation - rejected as too late

**Decision 4: Cycle Numbering**
- Decision: Major.Minor format (X.Y) allows sub-cycle organization
- Rationale: Matches design spec, flexible for complex TDD workflows
- Alternative considered: Flat numbering - rejected as less flexible

**Decision 5: Error Handling**
- Decision: Stop on critical errors, warn on minor issues
- Rationale: Prevents incorrect artifacts, but flexible for edge cases
- Alternative considered: Strict validation - may be too rigid

---

## Dependencies

**Before This Runbook**:
- `agent-core/bin/prepare-runbook.py` functional for general runbooks (✓)
- `agent-core/agents/tdd-task.md` baseline exists (✓ Step 3 of tdd-integration)
- `plans/tdd-integration/runbook.md` available for testing (✓)

**After This Runbook**:
- `prepare-runbook.py` supports both general and TDD runbooks
- Can execute Step 7 planning request (/plan-tdd skill creation)
- Can process any TDD runbook with cycle format
- Ready for TDD workflow integration testing

---

## Notes

**Backward Compatibility**: All changes preserve existing general runbook processing. Default behavior (no `type` field) remains unchanged.

**Testing Strategy**: Integration test (Step 9) uses real TDD runbook to validate end-to-end functionality. This is more reliable than unit tests for script modifications.

**Future Enhancements**: Could add support for REFACTOR validation (currently optional), cycle dependency checking, or cycle metadata.

**Reference Planning Request**: `plans/tdd-integration/reports/step-6-planning-request.md` contains detailed requirements and design specifications.
