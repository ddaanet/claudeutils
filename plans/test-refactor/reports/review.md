# Vet Review: test-refactor Runbook

**Scope**: Runbook for splitting test files to meet 400-line limit
**Date**: 2026-01-23
**Reviewer**: Sonnet (vet skill)

## Summary

The runbook provides a structured approach to refactoring two oversized test files (test_markdown_parsing.py at 501 lines, test_markdown.py at 1256 lines) to meet the 400-line limit. The approach includes duplicate detection, file splitting, and validation. However, the runbook contains several critical issues regarding incorrect baseline assumptions and validation criteria.

**Overall Assessment**: NEEDS_REVISION

## Issues Found

### Critical Issues

1. **Incorrect Test Count Baseline**
   - Location: Lines 8-10, 35, 51, 279, 329
   - Problem: Runbook states "99 tests total" and "22 tests in parsing, 77 in markdown" but actual current state shows 154 tests across 6 test files
   - Reality Check: Current test files are:
     - test_markdown_block.py: 113 lines
     - test_markdown_core.py: 126 lines
     - test_markdown_inline.py: 314 lines
     - test_markdown_list.py: 216 lines
     - test_markdown_parsing.py: 501 lines ← over limit
     - test_markdown.py: 1256 lines ← over limit
   - Impact: Success criteria and validation steps will fail due to incorrect expectations
   - Fix: Update all references to reflect 154 total tests and acknowledge that 4 test files already exist

2. **File Naming Conflicts**
   - Location: Step 2 (lines 136-191)
   - Problem: Runbook plans to create test_markdown_core.py and test_markdown_integration.py, but test_markdown_core.py already exists (126 lines)
   - Impact: Will overwrite existing test file or create confusion about which file to use
   - Fix: Either rename new files (e.g., test_markdown_process.py, test_markdown_regression.py) or verify existing files are part of the refactor scope

3. **Unclear Split Strategy Given Existing Files**
   - Location: Lines 83-89, Step 2
   - Problem: Split strategy doesn't account for existing test_markdown_*.py files (block, core, inline, list)
   - Question: Are these existing files related to the refactor? Should they be consolidated? Are they under the line limit?
   - Impact: May create duplicate organization or miss opportunities to consolidate
   - Fix: Clarify relationship between existing split files and planned split

### Major Issues

4. **Bash Script Violations**
   - Location: Step 1 (lines 102-113)
   - Problem: Uses /tmp/claude/ instead of project-local tmp/, and uses sed in bash (should use specialized tools)
   - Project Convention: "Use tmp/ in project directory for temp files, NOT /tmp/"
   - Fix: Change /tmp/claude/ to /Users/david/code/claudeutils/tmp/ and consider using Grep tool for extraction

5. **Missing Prerequisites Validation**
   - Location: Lines 41-44
   - Problem: Prerequisites marked as "verified" but doesn't specify when/how verification occurred
   - Issue: Runbook references 315/315 tests but current state shows 154/154
   - Fix: Add verification step or remove premature checkmarks; update test count

6. **Ambiguous Duplicate Handling Strategy**
   - Location: Step 3 (lines 195-235)
   - Problem: States "prefer test_markdown_parsing.py version" but doesn't explain criteria for this preference
   - Question: What if test_markdown.py version is more comprehensive or better documented?
   - Impact: May lose better test implementations
   - Fix: Add criteria for choosing which duplicate to keep (e.g., more comprehensive assertions, better documentation, clearer test name)

### Minor Issues

7. **Inconsistent Test Count References**
   - Location: Throughout document
   - Note: "99 tests", "315 tests", "154 tests" appear in different places
   - Suggestion: Single source of truth for current test count in Common Context section

8. **Success Criteria Lacks Specificity**
   - Location: Lines 34-40, 278-284
   - Note: "All tests passing" doesn't specify what command to run or expected output format
   - Suggestion: Add specific command (pytest tests/ -v) and expected summary line format

9. **Step 4 Execution Order Risk**
   - Location: Lines 248-263
   - Note: Deletes test_markdown.py before running tests, which means no rollback if tests fail
   - Suggestion: Run tests first with all files present, then delete only if tests pass

10. **Missing Import Analysis**
    - Location: Step 2 (lines 144-167)
    - Note: Says "copy file header and imports" but doesn't specify how to determine which imports are needed
    - Suggestion: Add substep to analyze which functions each test group actually imports

## Positive Observations

- **Clear structure**: Runbook follows proper format with metadata, common context, and design decisions
- **Good error escalation**: Specifies haiku→sonnet→user escalation path appropriately
- **Validation checkpoints**: Each step includes validation criteria and expected outcomes
- **Unexpected result handling**: Most steps include guidance for unexpected results
- **Report locations specified**: Clear output paths for each step's results
- **Design rationale documented**: Design Decisions section explains key choices

## Recommendations

1. **Audit Current State First**: Add Step 0 to document actual current test file structure and line counts before planning splits

2. **Reconcile Naming Conflicts**: Decide whether to:
   - Rename planned files to avoid conflicts with existing test_markdown_core.py
   - Incorporate existing split files into the refactor scope
   - Verify existing files are unrelated to test_markdown.py splitting

3. **Update All Test Count References**: Replace 99/315 with actual count (154) throughout document

4. **Use Project-Local Temp Directory**: Change /tmp/claude/ to /Users/david/code/claudeutils/tmp/

5. **Add Rollback Strategy**: Suggest backing up test_markdown.py before deletion or running tests before deletion

## Next Steps

### Required Before Execution:

1. **Verify current test state**: Run `ls -l tests/test_markdown*.py` and `pytest tests/test_markdown*.py -v` to document baseline
2. **Resolve naming conflicts**: Decide on file naming strategy for new splits
3. **Update test count**: Replace all references to 99/315 tests with actual 154 count
4. **Fix temp directory paths**: Change /tmp/claude/ to project-local tmp/
5. **Clarify duplicate strategy**: Add criteria for choosing which duplicate version to keep

### Optional Improvements:

1. Add import dependency analysis to Step 2
2. Specify exact pytest command format in success criteria
3. Add Step 4 substep to backup test_markdown.py before deletion
4. Consider adding a final step to run full test suite (not just markdown tests)

---

**Recommendation**: Revise runbook to address critical issues 1-3 before execution. The fundamental assumptions about test count and file structure don't match current codebase state.
