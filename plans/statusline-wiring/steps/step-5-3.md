# Cycle 5.3

**Plan**: `plans/statusline-wiring/runbook.md`
**Execution Model**: haiku
**Report Path**: `plans/statusline-wiring/reports/cycle-5-3-notes.md`

---

## Cycle 5.3: Call get_account_state and route to plan_usage or api_usage

**Objective**: statusline() calls account.state.get_account_state(), branches on mode (D4 orchestration)
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** tests/test_statusline_cli.py mocks get_account_state() to return mode="plan", mocks get_plan_usage(), asserts statusline() calls get_plan_usage() but not get_api_usage()

**Expected failure:**
```
AssertionError: get_plan_usage mock not called
```

**Why it fails:** CLI doesn't call get_account_state() or route to usage functions yet

**Verify RED:** pytest tests/test_statusline_cli.py::test_statusline_routes_to_plan_usage -xvs
- Must fail with mock not called
- If passes, STOP - routing may already exist

---

**GREEN Phase:**

**Implementation:** Add account_state = get_account_state(), if mode == "plan": call get_plan_usage(), elif mode == "api": call get_api_usage()

**Changes:**
- File: src/claudeutils/statusline/cli.py
  Action: Import account.state.get_account_state, plan_usage.get_plan_usage, api_usage.get_api_usage, add mode routing logic

**Verify GREEN:** pytest tests/test_statusline_cli.py::test_statusline_routes_to_plan_usage -xvs
- Must pass (get_plan_usage called)

**Verify no regression:** pytest tests/test_statusline_*.py
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/statusline-wiring/reports/cycle-5-3-notes.md

---
