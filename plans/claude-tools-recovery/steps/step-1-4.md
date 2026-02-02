# Cycle 1.4

**Plan**: `plans/claude-tools-recovery/runbook.md`
**Common Context**: See plan file for context

---

## Cycle 1.4: Add Keychain wrapper with subprocess mock

**Objective**: Create Keychain class with find() method tested via subprocess mock
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** Create tests/test_account_keychain.py with test for Keychain.find() mocking subprocess.run

**Expected failure:**
```
ModuleNotFoundError: No module named 'test_account_keychain'
or test fails because Keychain.find() doesn't exist
```

**Why it fails:** Keychain class or find() method doesn't exist yet

**Verify RED:**
```bash
pytest tests/test_account_keychain.py::test_keychain_find_success -v
```
- Create test file with mock for `subprocess.run` at `claudeutils.account.keychain.subprocess.run`
- Mock returns stdout="test-password\n", returncode=0
- Assert `Keychain().find("service", "account") == "test-password"`
- Test should FAIL (implementation missing)

---

**GREEN Phase:**

**Implementation:** Create Keychain class with find() method calling subprocess

**Changes:**
- File: src/claudeutils/account/keychain.py
  Action: Create Keychain class with `find(service, account)` using `subprocess.run(["security", "find-generic-password", "-s", service, "-a", account, "-w"], capture_output=True, text=True)`, return stdout.strip()
- File: tests/test_account_keychain.py
  Action: Create test with subprocess mock, verify command and return value

**Verify GREEN:**
```bash
pytest tests/test_account_keychain.py::test_keychain_find_success -v
```
- Test passes with mocked subprocess

**Verify no regression:**
```bash
pytest
```
- All existing tests pass

---

**Expected Outcome**: Keychain test mocks subprocess and verifies command structure
**Error Conditions**: subprocess mock not called → verify patch location (usage site)
**Validation**: Mock verifies security find-generic-password command
**Success Criteria**: Keychain.find() constructs correct subprocess command
**Report Path**: plans/claude-tools-recovery/reports/cycle-1-4-notes.md

---
