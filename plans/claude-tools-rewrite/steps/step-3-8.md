# Cycle 3.8

**Plan**: `plans/claude-tools-rewrite/runbook.md`
**Common Context**: See plan file for context

---

### Cycle 3.8: Usage API cache - put operation

**Objective**: Implement UsageCache.put() writing data with timestamp
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** UsageCache.put() writes cache file with current timestamp

**Expected failure:**
```
AttributeError: 'UsageCache' object has no attribute 'put'
```

**Why it fails:** put() method doesn't exist

**Verify RED:** `pytest tests/test_account_usage.py::test_usage_cache_put -xvs`
- Must fail with AttributeError
- If passes, STOP - method may already exist

---

**GREEN Phase:**

**Implementation:** Add put() method to UsageCache

**Changes:**
- File: src/claudeutils/account/usage.py
  Action: Add put(data) writing JSON with timestamp
- File: tests/test_account_usage.py
  Action: Test put() writes file, verify get() retrieves it when fresh

**Verify GREEN:** `pytest tests/test_account_usage.py::test_usage_cache_put -xvs`
- Must pass

**Verify no regression:** `pytest`
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/claude-tools-rewrite/reports/cycle-3-8-notes.md

---
