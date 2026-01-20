# Step 7

**Plan**: `plans/prepare-runbook-tdd/runbook.md`
**Common Context**: See plan file for context

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
