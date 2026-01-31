# Cycle 2.1

**Plan**: `plans/claude-tools-recovery/runbook.md`
**Common Context**: See plan file for context

---

## Cycle 2.1: Strengthen account status with filesystem mocking

**Objective**: Test account status reads real filesystem and outputs actual values
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** tests/test_cli_account.py::test_account_status should verify output contains mode from file

**Expected failure:**
```
AssertionError: assert "Mode: api" in result.output
(current hardcoded implementation outputs "Mode: plan")
```

**Why it fails:** CLI hardcodes state instead of reading from files

**Verify RED:**
```bash
pytest tests/test_cli_account.py::test_account_status -v
```
- Edit test to use `tmp_path` fixture, create `.claude/account-mode` with content "api"
- Mock `pathlib.Path.home` at usage location `claudeutils.account.cli.Path.home` to return `tmp_path`
- Assert `"Mode: api" in result.output`
- Test should FAIL (CLI returns hardcoded "Mode: plan")

---

**GREEN Phase:**

**Implementation:** Create account state factory and use it in status command

**Changes:**
- File: src/claudeutils/account/state.py
  Action: Add `get_account_state()` function that reads `Path.home() / ".claude" / "account-mode"` and `"account-provider"` files, returns AccountState with file values (default "plan"/"anthropic" if missing)
- File: src/claudeutils/account/cli.py
  Action: Replace hardcoded AccountState in status() with `state = get_account_state()`
- File: tests/test_cli_account.py
  Action: Update test with tmp_path, file creation, Path.home mock, output assertion

**Verify GREEN:**
```bash
pytest tests/test_cli_account.py::test_account_status -v
```
- Test passes with output from real file reads

**Verify no regression:**
```bash
pytest tests/test_cli_account.py -v
```
- All CLI account tests pass

---

**Expected Outcome**: account status test creates fixtures and verifies output content
**Error Conditions**: Path.home() mock incorrect → verify patch at usage location
**Validation**: Test asserts specific mode value from fixture
**Success Criteria**: CLI reads real files, outputs actual state
**Report Path**: plans/claude-tools-recovery/reports/cycle-2-1-notes.md

---
