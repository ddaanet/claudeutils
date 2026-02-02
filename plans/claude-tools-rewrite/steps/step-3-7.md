# Cycle 3.7

**Plan**: `plans/claude-tools-rewrite/runbook.md`
**Common Context**: See plan file for context

---

### Cycle 3.7: Usage API cache - get operation

**Objective**: Implement UsageCache.get() returning cached data if fresh
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** UsageCache.get() returns None when cache missing or stale

**Expected failure:**
```
AttributeError: module 'claudeutils.account' has no attribute 'UsageCache'
```

**Why it fails:** UsageCache class doesn't exist

**Verify RED:** `pytest tests/test_account_usage.py::test_usage_cache_get_stale -xvs`
- Must fail with AttributeError
- If passes, STOP - class may already exist

---

**GREEN Phase:**

**Implementation:** Create UsageCache class with get() method

**Changes:**
- File: src/claudeutils/account/usage.py
  Action: Create UsageCache with get() checking cache file mtime against TTL
- File: src/claudeutils/account/__init__.py
  Action: Add `from .usage import UsageCache`
- File: tests/test_account_usage.py
  Action: Test get() with tmp_path, mock timestamps

**Verify GREEN:** `pytest tests/test_account_usage.py::test_usage_cache_get_stale -xvs`
- Must pass

**Verify no regression:** `pytest`
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/claude-tools-rewrite/reports/cycle-3-7-notes.md

---
