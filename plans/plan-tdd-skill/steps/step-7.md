# Step 7

**Plan**: `plans/plan-tdd-skill/runbook.md`
**Common Context**: See plan file for context

---

## Step 7: Add Error Handling and Edge Cases

**Objective**: Add error handling and edge case guidance to skill.md.

**Script Evaluation**: Direct execution (enhancement task)

**Execution Model**: Sonnet

**Tool Usage**:
- Use Read to read skill.md
- Use Edit to add section
- Never use heredocs

**Implementation**:

Add "Error Handling and Edge Cases" section to skill.md with:

1. **Input Validation Errors**:
   - Design document not found → Report path, stop
   - Missing TDD sections → Report missing sections, ask if general runbook instead
   - Unresolved `(REQUIRES CONFIRMATION)` → List items, stop for user input

2. **Cycle Generation Errors**:
   - Empty cycle (no assertions) → Report warning, skip cycle
   - Circular dependencies detected → Report cycles involved, stop
   - Invalid cycle ID format → Report invalid IDs, stop
   - Duplicate cycle IDs → Report duplicates, stop

3. **Integration Errors**:
   - Cannot write runbook file → Report path and permissions, stop
   - prepare-runbook.py not available → Report path, stop

4. **Edge Cases**:
   - Single-cycle feature → Valid, generate single cycle
   - No dependencies between cycles → Valid, mark all as parallel-safe
   - All cycles are regressions → Valid, entire test suite verification
   - Cycle depends on future cycle → Invalid, report ordering issue

5. **Recovery Protocols**:
   - Validation failure → Report specific issue, provide fix guidance
   - Partial runbook generation → Clean up partial files, report error
   - User intervention needed → Save state, clear next action

**Expected Outcome**: Comprehensive error handling guidance added.

**Error Conditions**:
- Edit fails → STOP, report error

**Validation**:
- Section "Error Handling and Edge Cases" exists
- All 5 subsections present
- Recovery protocols documented

**Success Criteria**:
- All error conditions documented
- Edge cases handled gracefully
- Recovery protocols clear

**Report Path**: `plans/plan-tdd-skill/reports/step-7-report.md`

---
