# Cycle 3.1

**Plan**: `plans/statusline-wiring/runbook.md`
**Execution Model**: haiku
**Report Path**: `plans/statusline-wiring/reports/cycle-3-1-notes.md`

---

## Cycle 3.1: Update UsageCache TTL from 30s to 10s

**Objective**: Change UsageCache.TTL_SECONDS constant to 10 (R4 requirement)
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** tests/test_statusline_plan_usage.py imports account.usage.UsageCache, asserts TTL_SECONDS == 10

**Expected failure:**
```
AssertionError: assert 30 == 10
```

**Why it fails:** UsageCache.TTL_SECONDS is currently 30

**Verify RED:** pytest tests/test_statusline_plan_usage.py::test_usage_cache_ttl -xvs
- Must fail with AssertionError (30 != 10)
- If passes, STOP - TTL may already be 10

---

**GREEN Phase:**

**Implementation:** Change TTL_SECONDS constant in UsageCache class

**Changes:**
- File: src/claudeutils/account/usage.py
  Action: Change UsageCache.TTL_SECONDS = 30 to UsageCache.TTL_SECONDS = 10

**Verify GREEN:** pytest tests/test_statusline_plan_usage.py::test_usage_cache_ttl -xvs
- Must pass

**Verify no regression:** pytest tests/
- All existing tests pass (may need to update test expectations if any rely on 30s TTL)

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/statusline-wiring/reports/cycle-3-1-notes.md

---
