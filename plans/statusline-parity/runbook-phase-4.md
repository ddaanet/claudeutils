# Phase 4: TTL Update

**Objective:** Update UsageCache TTL to match design spec

**Files:**
- Source: `src/claudeutils/account/usage.py`
- Tests: `tests/test_account_usage.py` (if exists) or integration test in CLI tests

**Design reference:** D7 — TTL adjustment from 30s to 10s (non-critical)

---

## Cycle 4.1: TTL Constant Update

**Objective:** Update UsageCache TTL from 30 seconds to 10 seconds

**Script Evaluation:** Direct execution (TDD cycle)
**Execution Model:** Haiku

**Implementation:**

**RED Phase:**

**Test:** `test_usage_cache_ttl`
**Assertions:**
- UsageCache instance has TTL attribute equal to 10 (seconds)
- Or if TTL is class-level constant: `UsageCache.TTL == 10`
- Verify cache expires after 10 seconds (mock time.time() if needed)

**Expected failure:** Test assertion failure — TTL is 30, not 10

**Why it fails:** TTL constant still set to 30 seconds

**Verify RED:** `pytest tests/test_account_usage.py::test_usage_cache_ttl -v` (or appropriate test location)

---

**GREEN Phase:**

**Implementation:** Update TTL constant in UsageCache

**Behavior:**
- Change TTL from 30 to 10
- No other logic changes
- Cache expiration behavior unchanged (just shorter TTL)

**Approach:** Single constant assignment

**Changes:**
- File: `src/claudeutils/account/usage.py`
  Action: Update TTL constant from 30 to 10
  Location hint: Find TTL constant definition (likely near class definition or __init__)

**Verify GREEN:** `pytest tests/test_account_usage.py::test_usage_cache_ttl -v`
- Must pass

**Verify no regression:** `pytest tests/test_account_usage.py -v` or `just test`
- All existing tests pass

**Expected Outcome:** GREEN verification, no regressions
**Report Path:** plans/statusline-parity/reports/cycle-4-1-notes.md

---

**Light Checkpoint** (end of Phase 4)
1. Fix: Run `just dev`. Sonnet quiet-task diagnoses and fixes failures. Commit when passing.
2. Functional: Review Phase 4 implementation. Verify TTL change only.
