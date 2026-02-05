# Phase 5: TTL Update (1 cycle)

## Cycle 5.1: Update UsageCache TTL

**Objective**: Update UsageCache TTL from 30 seconds to 10 seconds per design spec

**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

### RED Phase

**Test:** `test_usage_cache_ttl` in `tests/test_account_usage.py`

**Test Description:**

Create a test that verifies the UsageCache TTL constant is set to exactly 10 seconds. The test should import the TTL constant from the usage module and assert its value. Include checks for:
- TTL value equals 10 (not 30, not any other value)
- TTL is an integer (not float or string)
- TTL is positive (non-zero, greater than zero)

The test validates that the cache expiration timeout matches the design specification (D7, lines 215-220 in design.md). This ensures cached usage data is refreshed frequently enough to keep displayed account status current during active CLI sessions.

**Expected failure:** Assertion error - TTL constant is currently 30, test expects 10

**Why it fails:** UsageCache TTL has not been updated from original 30-second value

**Verify RED:** `pytest tests/test_account_usage.py::test_usage_cache_ttl -v`

---

### GREEN Phase

**Implementation:** Update TTL constant in UsageCache class

**Behavior:**

Locate the TTL constant definition in the UsageCache class (in `src/claudeutils/account/usage.py`) and change its value from 30 to 10. This is a single-line constant update with no algorithmic changes. The cache behavior remains identical; only the expiration timeout is reduced from 30 seconds to 10 seconds.

**Approach:** Direct constant update per D7. Minimal risk change affecting only cache freshness interval.

**Changes:**
- File: `src/claudeutils/account/usage.py`
  Action: Update TTL constant from 30 to 10
  Location hint: Look for `TTL = 30` or similar constant assignment in UsageCache class definition

**Verify GREEN:** `pytest tests/test_account_usage.py::test_usage_cache_ttl -v`
- Must pass

**Verify no regression:** `just test`
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED (TTL is 30), passes during GREEN (TTL is 10), no breaks
**Report Path**: plans/statusline-parity/reports/cycle-5-1-notes.md

---

**No Checkpoint** (Phase 5 complete)

Phase 5 is the final trivial phase requiring only a single constant update. No checkpoint needed — the cycle completes Phase 5 and the entire runbook. Proceed to orchestration completion.
