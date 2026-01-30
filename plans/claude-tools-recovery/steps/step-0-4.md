# Cycle 0.4

**Plan**: `plans/claude-tools-recovery/runbook.md`
**Common Context**: See plan file for context

---

## Cycle 0.4: Delete statusline OK-output test

**Objective**: Remove test that only checks statusline returns "OK" string

**Script Evaluation**: Direct execution (TDD cycle)

**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** Verify test file doesn't contain OK-output test

**Expected failure:**
```
AssertionError: statusline OK test still exists
```

**Why it fails:** Test hasn't been deleted yet

**Verify RED:** Grep tests/test_statusline.py for test checking output == "OK" or similar stub
- Likely name: test_statusline_basic or test_statusline_output

---

**GREEN Phase:**

**Implementation:** Delete statusline OK-output test function

**Changes:**
- File: tests/test_statusline.py
  Action: Remove test that checks for "OK" output

**Verify GREEN:** Read tests/test_statusline.py
- Test no longer present

**Verify no regression:** `pytest tests/test_statusline.py`
- All remaining tests pass

---

**Expected Outcome**: OK-output test removed, remaining tests pass

**Error Conditions**: Test not found → STOP; Regression → STOP

**Validation**: Test deleted ✓, No regressions ✓

**Success Criteria**: No stub output test remains

**Report Path**: plans/claude-tools-recovery/reports/cycle-0-4-notes.md

---

**Checkpoint**

1. Fix: Run `just dev`. Sonnet quiet-task fixes failures. Commit when green.
2. Vet: Review test deletions (confirm no valuable tests removed). Commit.
3. Functional review: Verify remaining tests have some behavioral content (even if weak - will strengthen in R1/R2).

---
