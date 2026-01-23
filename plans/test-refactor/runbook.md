---
name: test-refactor
model: haiku
---

# Test File Refactoring Runbook

**Context**: Two test files exceed the 400-line limit:
- `tests/test_markdown_parsing.py`: 501 lines (22 tests)
- `tests/test_markdown.py`: 1256 lines (77 tests)

Four smaller split files already exist:
- `tests/test_markdown_block.py`: 113 lines (5 tests) ✓
- `tests/test_markdown_core.py`: 126 lines (9 tests) ✓
- `tests/test_markdown_inline.py`: 314 lines (27 tests) ✓
- `tests/test_markdown_list.py`: 216 lines (14 tests) ✓

Total: 154 tests across 6 files

**Source**: Line limit check failure from `just dev`

**Status**: Draft (Revision 1 - corrected test counts and file inventory)
**Created**: 2026-01-23
**Reviewed**: 2026-01-23 (sonnet, NEEDS_REVISION - critical issues identified)
**Revised**: 2026-01-23

---

## Weak Orchestrator Metadata

**Total Steps**: 5

**Execution Model**:
- Steps 1-5: Haiku (file operations, refactoring)

**Step Dependencies**: Sequential

**Error Escalation**:
- Haiku → Sonnet: If test structure analysis requires semantic judgment
- Sonnet → User: If splitting strategy is ambiguous or breaking tests

**Report Locations**: `plans/test-refactor/reports/step-N.md`

**Success Criteria**:
- All tests passing (154/154 markdown tests minimum)
- `test_markdown_parsing.py` ≤ 400 lines
- `test_markdown.py` removed (tests redistributed)
- No duplicate test functions across all 5 final files
- All imports properly organized
- Line limit check passes

**Prerequisites**:
- Current markdown tests: 154 tests across 6 files
- Target files exist: test_markdown_parsing.py (501 lines), test_markdown.py (1256 lines)
- Existing split files: test_markdown_block.py, test_markdown_core.py, test_markdown_inline.py, test_markdown_list.py
- Test files in: `/Users/david/code/claudeutils/tests/`

---

## Common Context

**Key Constraints**:
- Must maintain 100% test coverage - all 154 tests must remain functional
- Test file naming convention: `test_<module>.py`
- Each test file must have proper imports
- Line limit: 400 lines per file
- All tests must pass after refactoring
- Cannot overwrite existing test_markdown_*.py files

**Project Paths**:
- Test directory: `/Users/david/code/claudeutils/tests/`
- Source module: `/Users/david/code/claudeutils/claudeutils/markdown.py`

**Conventions**:
- Use pytest framework
- Test function naming: `test_<description>`
- Docstrings required for all test functions
- Import only what's needed from `claudeutils.markdown`

**Existing Files Analysis**:

Existing split files (under limit, keep as-is):
- `test_markdown_block.py`: 113 lines, 5 tests ✓
- `test_markdown_core.py`: 126 lines, 9 tests ✓
- `test_markdown_inline.py`: 314 lines, 27 tests ✓
- `test_markdown_list.py`: 216 lines, 14 tests ✓

Over limit files (need refactoring):
- `test_markdown_parsing.py`: 501 lines, 22 tests ❌
- `test_markdown.py`: 1256 lines, 77 tests ❌

**Refactoring Strategy**:

1. **Identify duplicates**: Find tests in test_markdown.py that duplicate existing split files or test_markdown_parsing.py
2. **Redistribute test_markdown.py tests**: Move unique tests to appropriate existing split files (block, core, inline, list) or to test_markdown_parsing.py
3. **Shrink test_markdown_parsing.py**: Move tests to existing split files if needed to get under 400 lines
4. **Delete test_markdown.py**: Once all tests are redistributed, remove the file

**Expected Outcome**: 5 test files, all ≤ 400 lines, 154 tests total

---

## Step 1: Identify all duplicates across test files

**Objective**: Find duplicate test function names across all 6 markdown test files

**Script Evaluation**: Small script

**Execution Model**: Haiku

**Implementation**:
```bash
# Create temp directory in project
mkdir -p /Users/david/code/claudeutils/tmp

# Extract test names from each file
for file in block core inline list parsing; do
  grep -E "^def test_" /Users/david/code/claudeutils/tests/test_markdown_${file}.py 2>/dev/null | \
    sed 's/def \(test_[^(]*\).*/\1/' > /Users/david/code/claudeutils/tmp/${file}_tests.txt || true
done

grep -E "^def test_" /Users/david/code/claudeutils/tests/test_markdown.py | \
  sed 's/def \(test_[^(]*\).*/\1/' > /Users/david/code/claudeutils/tmp/main_tests.txt

# Find duplicates (tests in test_markdown.py that exist in other files)
echo "Duplicates between test_markdown.py and split files:"
for file in block core inline list parsing; do
  echo ""
  echo "=== Duplicates in test_markdown_${file}.py ==="
  comm -12 <(sort /Users/david/code/claudeutils/tmp/main_tests.txt) \
    <(sort /Users/david/code/claudeutils/tmp/${file}_tests.txt) | tee /Users/david/code/claudeutils/tmp/dup_${file}.txt
done

# Count total duplicates
cat /Users/david/code/claudeutils/tmp/dup_*.txt | sort -u > /Users/david/code/claudeutils/tmp/all_duplicates.txt
echo ""
echo "Total unique duplicates: $(wc -l < /Users/david/code/claudeutils/tmp/all_duplicates.txt)"
echo "Unique tests in test_markdown.py: $(($(wc -l < /Users/david/code/claudeutils/tmp/main_tests.txt) - $(wc -l < /Users/david/code/claudeutils/tmp/all_duplicates.txt)))"
```

**Expected Outcome**: List of duplicate tests and count of unique tests to redistribute

**Unexpected Result Handling**:
- If >50 duplicates: Most of test_markdown.py is duplicated - just delete it and verify tests still pass
- If <10 duplicates: Unexpected, stop and report for manual review

**Error Conditions**:
- File read errors → Escalate to user

**Validation**:
- Duplicate lists generated for each split file
- Total duplicate count calculated
- Unique test count calculated

**Success Criteria**:
- Duplicate analysis complete (written to tmp/ directory)
- Know how many tests need redistribution vs deletion

**Report Path**: `/Users/david/code/claudeutils/plans/test-refactor/reports/step-1.md`

---

## Step 2: Analyze unique tests in test_markdown.py

**Objective**: Read test_markdown.py and categorize unique (non-duplicate) tests by which existing file they belong in

**Script Evaluation**: Prose description (requires reading test content and understanding categorization)

**Execution Model**: Haiku

**Implementation**:

1. Read duplicate list from Step 1 (tmp/all_duplicates.txt)
2. Read test_markdown.py and extract all test function names
3. For each unique test (not in duplicate list):
   - Read the test function and its imports
   - Determine which existing split file it belongs to:
     - `test_markdown_block.py`: tests for fix_markdown_code_blocks
     - `test_markdown_core.py`: tests for process_lines, process_file
     - `test_markdown_inline.py`: tests for escape_inline_backticks, fix_backtick_spaces
     - `test_markdown_list.py`: tests for fix_metadata_blocks, fix_warning_lines, fix_metadata_list_indentation
     - `test_markdown_parsing.py`: integration tests, segment-aware tests, fence protection tests
4. Create categorization map: unique_test_name → target_file
5. Write map to tmp/redistribution-map.txt

**Expected Outcome**: Redistribution map showing which unique tests go to which file

**Unexpected Result Handling**:
- If test doesn't fit any category: Add to test_markdown_parsing.py (catch-all)
- If all tests are duplicates: Great! Just delete test_markdown.py

**Error Conditions**:
- Cannot read test_markdown.py → Escalate to user

**Validation**:
- Redistribution map created
- All unique tests accounted for
- Map specifies target file for each test

**Success Criteria**:
- Redistribution map complete (tmp/redistribution-map.txt)
- Every unique test has a target file assignment

**Report Path**: `/Users/david/code/claudeutils/plans/test-refactor/reports/step-2.md`

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

## Step 5: Delete test_markdown.py and validate

**Objective**: Remove test_markdown.py and verify all 154 tests still pass

**Script Evaluation**: Direct execution (simple bash commands)

**Execution Model**: Haiku

**Implementation**:
```bash
cd /Users/david/code/claudeutils

# Run tests FIRST to verify everything works
pytest tests/test_markdown*.py -v --tb=short

# If tests pass, check counts
TEST_COUNT=$(pytest tests/test_markdown*.py --collect-only -q 2>&1 | grep -E "^[0-9]+ test" | awk '{print $1}')
echo "Test count: $TEST_COUNT"

# Verify test count is 154
if [ "$TEST_COUNT" != "154" ]; then
  echo "ERROR: Expected 154 tests, got $TEST_COUNT"
  exit 1
fi

# Delete test_markdown.py
rm tests/test_markdown.py

# Run tests again to verify still pass
pytest tests/test_markdown*.py -v --tb=short

# Check line counts
echo ""
echo "Final line counts:"
wc -l tests/test_markdown*.py

# Run full line limit check
./scripts/check_line_limits.sh
```

**Expected Outcome**: All 154 tests pass, all test files ≤ 400 lines, line limit check passes

**Unexpected Result Handling**:
- If tests fail before deletion: Stop and report - Step 3/4 introduced issues
- If tests fail after deletion: Rollback - some tests weren't properly redistributed
- If line limits still exceeded: Stop and report - Step 4 incomplete

**Error Conditions**:
- Test failures → Escalate to sonnet for analysis
- Line limit failures → Escalate to user

**Validation**:
- All 154 tests pass
- No test files exceed 400 lines
- test_markdown.py deleted
- Line limit check passes

**Success Criteria**:
- All tests passing (154/154 markdown tests minimum)
- All markdown test files ≤ 400 lines
- Line limit check passes
- No regressions in functionality

**Report Path**: `/Users/david/code/claudeutils/plans/test-refactor/reports/step-5.md`

---

## Design Decisions

**Decision 1: Redistribute instead of split**
- Rationale: Four split files already exist (block, core, inline, list), so redistribute test_markdown.py tests to them
- Avoids creating new files or file naming conflicts
- Leverages existing organization

**Decision 2: Delete test_markdown.py after redistribution**
- Rationale: test_markdown.py appears to be the "old monolithic file" before splitting was started
- Most tests are likely duplicates of the split files
- Unique tests can be redistributed to appropriate existing files

**Decision 3: Use tmp/ directory for analysis artifacts**
- Rationale: Follows project convention (not /tmp/claude/)
- Keeps analysis artifacts for debugging if needed
- Allows iterative refinement

**Decision 4: Validate before deleting**
- Rationale: Run tests before deleting test_markdown.py to ensure redistribution is complete
- Prevents accidental test loss
- Allows rollback if issues found

**Decision 5: Shrink test_markdown_parsing.py if needed**
- Rationale: May naturally shrink after test_markdown.py deletion removes duplicates
- If still over limit, move tests to existing split files where they fit
- Prefer moving to inline or integration-focused files

---

## Dependencies

**Before This Runbook**:
- All tests passing (315/315)
- Both test files exist and are readable

**After This Runbook**:
- Four test files under line limits
- All tests still passing
- Can proceed with normal development

---

## Notes

- The duplicate count from Step 1 will inform redistribution strategy
- If most tests are duplicates (likely scenario), deletion is straightforward
- Test count should remain constant (154 total) distributed across 5 files
- This is a pure refactoring - no test behavior changes
- Existing split files suggest previous refactoring attempt - we're completing it
