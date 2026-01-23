# Step 1

**Plan**: `/Users/david/code/claudeutils/plans/test-refactor/runbook.md`
**Common Context**: See plan file for context

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
