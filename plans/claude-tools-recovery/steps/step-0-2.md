# Cycle 0.2

**Plan**: `plans/claude-tools-recovery/runbook.md`
**Common Context**: See plan file for context

---

## Cycle 0.2: Delete hasattr-only provider tests

**Objective**: Remove tests that only verify providers have methods via hasattr

**Script Evaluation**: Direct execution (TDD cycle)

**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** Verify test file doesn't contain hasattr-only tests for providers

**Expected failure:**
```
AssertionError: hasattr-only provider tests still exist
```

**Why it fails:** Tests haven't been deleted yet

**Verify RED:** Grep tests/test_account.py for tests that:
- Only use `assert hasattr(provider, "method_name")`
- No behavior assertions
- Likely names: test_anthropic_provider_has_methods, test_openrouter_provider_has_methods

---

**GREEN Phase:**

**Implementation:** Delete hasattr-only provider test functions

**Changes:**
- File: tests/test_account.py
  Action: Remove test functions that only check hasattr on providers

**Verify GREEN:** Grep tests/test_account.py
- Must NOT find hasattr-only provider tests

**Verify no regression:** `pytest tests/test_account.py`
- All remaining tests pass

---

**Expected Outcome**: Hasattr-only tests removed, remaining tests pass

**Error Conditions**: Tests not found → STOP; Regression → STOP

**Validation**: Tests deleted ✓, No regressions ✓

**Success Criteria**: No hasattr-only provider tests remain

**Report Path**: plans/claude-tools-recovery/reports/cycle-0-2-notes.md

---
