# Step 3

**Plan**: `plans/prepare-runbook-tdd/runbook.md`
**Common Context**: See plan file for context

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
