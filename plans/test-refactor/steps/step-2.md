# Step 2

**Plan**: `/Users/david/code/claudeutils/plans/test-refactor/runbook.md`
**Common Context**: See plan file for context

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
