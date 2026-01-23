# Step 3

**Plan**: `/Users/david/code/claudeutils/plans/test-refactor/runbook.md`
**Common Context**: See plan file for context

---

## Step 3: Redistribute unique tests to appropriate files

**Objective**: Copy unique tests from test_markdown.py to their target files based on redistribution map

**Script Evaluation**: Prose description (requires extracting and inserting test code)

**Execution Model**: Haiku

**Implementation**:

1. Read redistribution map from Step 2 (tmp/redistribution-map.txt)
2. For each test in the map:
   - Extract test function from test_markdown.py (including docstring)
   - Read target file
   - Append test to end of target file (before any closing comments)
   - Verify imports in target file include all needed functions

3. Verify line counts after additions:
   - If any file >400 lines: Stop and report
   - Document new line counts

4. Check for any import additions needed in target files

**Expected Outcome**: All unique tests redistributed, all target files still ≤ 400 lines

**Unexpected Result Handling**:
- If target file would exceed 400 lines: Stop and report - need user decision on where to put test
- If imports conflict: Stop and report

**Error Conditions**:
- File write errors → Escalate to user
- Test extraction fails → Escalate to sonnet

**Validation**:
- All tests from redistribution map added to target files
- All target files ≤ 400 lines
- No syntax errors in modified files

**Success Criteria**:
- All unique tests redistributed
- All 5 target files ≤ 400 lines
- Imports updated correctly

**Report Path**: `/Users/david/code/claudeutils/plans/test-refactor/reports/step-3.md`

---
