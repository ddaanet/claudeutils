# Cycle 1.5

**Plan**: `plans/claude-tools-recovery/runbook.md`
**Common Context**: See plan file for context

---

## Cycle 1.5: Test Keychain entry not found

**Objective**: Test Keychain.find() returns None when entry doesn't exist
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** tests/test_account_keychain.py should test find() returns None on subprocess failure

**Expected failure:**
```
AssertionError: assert result is None
(may return empty string or raise exception)
```

**Why it fails:** Keychain.find() doesn't handle subprocess returncode != 0

**Verify RED:**
```bash
pytest tests/test_account_keychain.py::test_keychain_find_not_found -v
```
- Create test with mock returncode=1, stdout=""
- Assert `Keychain().find("service", "account") is None`
- Test should FAIL if error handling missing

---

**GREEN Phase:**

**Implementation:** Update Keychain.find() to return None on subprocess failure

**Changes:**
- File: src/claudeutils/account/keychain.py
  Action: Check `result.returncode`, return `None` if != 0, else return `result.stdout.strip()`
- File: tests/test_account_keychain.py
  Action: Add test with mock returncode=1, assert find() returns None

**Verify GREEN:**
```bash
pytest tests/test_account_keychain.py::test_keychain_find_not_found -v
```
- Test passes with None return

**Verify no regression:**
```bash
pytest tests/test_account_keychain.py -v
```
- Both find tests pass (success and not found)

---

**Expected Outcome**: Keychain handles missing entries gracefully with None return
**Error Conditions**: Exception raised instead → add try/except
**Validation**: Test verifies None return on subprocess failure
**Success Criteria**: Keychain.find() returns None for missing entries
**Report Path**: plans/claude-tools-recovery/reports/cycle-1-5-notes.md

---

**Checkpoint**

1. Fix: Run `just dev`. Sonnet quiet-task fixes failures. Commit when green.
2. Vet: Review provider and keychain test quality, mock patterns. Commit fixes.
3. Functional review: Verify all provider implementations call keystore (not return stubs). Check Keychain calls subprocess. If any stubs remain, STOP and report.

---
