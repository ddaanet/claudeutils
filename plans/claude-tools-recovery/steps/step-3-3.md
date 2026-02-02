# Cycle 3.3

**Plan**: `plans/claude-tools-recovery/runbook.md`
**Common Context**: See plan file for context

---

## Cycle 3.3: Integration test for mode switching round-trip

**Objective**: Test full workflow switching modes and verifying file state
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** tests/test_cli_account.py should test sequential mode switches with file verification

**Expected failure:**
```
May fail if file writes don't persist or state reads incorrect
```

**Why it fails:** Integration gaps between commands

**Verify RED:**
```bash
pytest tests/test_cli_account.py::test_account_mode_round_trip -v
```
- Create test that invokes account plan, then account api, then account plan again
- Verify files after each command
- Test should FAIL if any step doesn't persist state correctly

---

**GREEN Phase:**

**Implementation:** Ensure all commands read/write state correctly (should already work from previous cycles)

**Changes:**
- File: tests/test_cli_account.py
  Action: Add integration test with sequential CLI invocations within same CliRunner context, verify file state after each

**Verify GREEN:**
```bash
pytest tests/test_cli_account.py::test_account_mode_round_trip -v
```
- Test passes with all mode switches verified

**Verify no regression:**
```bash
pytest tests/test_cli_account.py -v
```
- All CLI tests pass

---

**Expected Outcome**: Integration test verifies full workflow end-to-end
**Error Conditions**: File state inconsistent → check write/read paths match
**Validation**: Test verifies files after each command
**Success Criteria**: Round-trip mode switching works correctly
**Report Path**: plans/claude-tools-recovery/reports/cycle-3-3-notes.md

---

**Checkpoint**

1. Fix: Run `just dev`. Sonnet quiet-task fixes failures. Commit when green.
2. Vet: Review error handling, integration test coverage. Commit fixes.
3. Functional review: Manual test `account status`, `account plan`, `account api` commands with real ~/.claude/ directory. Verify actual output (mode/provider read from files, claude-env generated with credentials). If commands still return stubs or hardcoded values, STOP and report.

---
