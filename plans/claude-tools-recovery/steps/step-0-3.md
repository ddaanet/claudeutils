# Cycle 0.3

**Plan**: `plans/claude-tools-recovery/runbook.md`
**Common Context**: See plan file for context

---

## Cycle 0.3: Delete isinstance-only model tests

**Objective**: Remove tests that only verify model objects are correct type

**Script Evaluation**: Direct execution (TDD cycle)

**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** Verify test file doesn't contain isinstance-only tests

**Expected failure:**
```
AssertionError: isinstance-only model tests still exist
```

**Why it fails:** Tests haven't been deleted yet

**Verify RED:** Grep tests/test_model.py for tests that:
- Only use `assert isinstance(result, SomeClass)`
- No behavior assertions
- Likely pattern: instantiation tests without method calls

---

**GREEN Phase:**

**Implementation:** Delete isinstance-only test functions

**Changes:**
- File: tests/test_model.py
  Action: Remove test functions that only check isinstance

**Verify GREEN:** Read tests/test_model.py
- Verify removed tests no longer present

**Verify no regression:** `pytest tests/test_model.py`
- All remaining tests pass

---

**Expected Outcome**: Isinstance-only tests removed, remaining tests pass

**Error Conditions**: Tests not found → STOP; Regression → STOP

**Validation**: Tests deleted ✓, No regressions ✓

**Success Criteria**: No isinstance-only tests remain

**Report Path**: plans/claude-tools-recovery/reports/cycle-0-3-notes.md

---
