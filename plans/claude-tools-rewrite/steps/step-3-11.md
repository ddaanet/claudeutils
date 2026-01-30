# Cycle 3.11

**Plan**: `plans/claude-tools-rewrite/runbook.md`
**Common Context**: See plan file for context

---

### Cycle 3.11: Account CLI - api command

**Objective**: Implement `claudeutils account api` switching to API mode
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku
**Dependencies**: [DEPENDS: 1.9, 1.11]

**Implementation:**

**RED Phase:**

**Test:** CLI command `claudeutils account api` switches to API mode

**Expected failure:**
```
AttributeError: 'Group' object has no attribute 'api'
```

**Why it fails:** api command doesn't exist

**Verify RED:** `pytest tests/test_cli_account.py::test_account_api -xvs`
- Must fail with AttributeError
- If passes, STOP - command may already exist

---

**GREEN Phase:**

**Implementation:** Create account api command

**Changes:**
- File: src/claudeutils/account/cli.py
  Action: Add 'api' command with provider selection, mode switching
- File: tests/test_cli_account.py
  Action: Test with CliRunner, verify mode and provider files

**Verify GREEN:** `pytest tests/test_cli_account.py::test_account_api -xvs`
- Must pass

**Verify no regression:** `pytest`
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/claude-tools-rewrite/reports/cycle-3-11-notes.md

---
