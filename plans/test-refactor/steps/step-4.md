# Step 4

**Plan**: `/Users/david/code/claudeutils/plans/test-refactor/runbook.md`
**Common Context**: See plan file for context

---

## Step 4: Shrink test_markdown_parsing.py if needed

**Objective**: If test_markdown_parsing.py is still >400 lines, move tests to other files to get under limit

**Script Evaluation**: Prose description (requires identifying movable tests)

**Execution Model**: Haiku

**Implementation**:

1. Check line count of test_markdown_parsing.py
2. If ≤ 400 lines: Skip this step, proceed to Step 5
3. If > 400 lines:
   - Identify integration-style tests that could move to test_markdown_inline.py (if space available)
   - Calculate how many lines need to be removed
   - Select tests to move (prefer moving largest tests first)
   - Extract and move tests to target file
   - Update imports if needed
4. Verify final line count ≤ 400

**Expected Outcome**: test_markdown_parsing.py ≤ 400 lines

**Unexpected Result Handling**:
- If no suitable tests to move: Stop and report - may need to create new file or get user decision
- If target file would exceed 400: Stop and report

**Error Conditions**:
- Cannot get under 400 lines → Escalate to user for decision

**Validation**:
- test_markdown_parsing.py ≤ 400 lines
- Moved tests still work in target file

**Success Criteria**:
- test_markdown_parsing.py ≤ 400 lines
- All files remain ≤ 400 lines

**Report Path**: `/Users/david/code/claudeutils/plans/test-refactor/reports/step-4.md`

---
