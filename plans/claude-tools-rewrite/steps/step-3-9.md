# Cycle 3.9

**Plan**: `plans/claude-tools-rewrite/runbook.md`
**Common Context**: See plan file for context

---

### Cycle 3.9: Account CLI - status command

**Objective**: Implement `claudeutils account status` command
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku
**Dependencies**: [DEPENDS: 1.2, 1.3, 1.7]

**Implementation:**

**RED Phase:**

**Test:** CLI command `claudeutils account status` returns account state

**Expected failure:**
```
AttributeError: 'Group' object has no attribute 'status'
```

**Why it fails:** status command doesn't exist

**Verify RED:** `pytest tests/test_cli_account.py::test_account_status -xvs`
- Must fail with AttributeError
- If passes, STOP - command may already exist

---

**GREEN Phase:**

**Implementation:** Create account status command in cli.py

**Changes:**
- File: src/claudeutils/account/cli.py
  Action: Create Click command group 'account' with 'status' command reading state and calling validate_consistency()
- File: src/claudeutils/cli.py
  Action: Add account command group
- File: tests/test_cli_account.py
  Action: Test with CliRunner, mock state files

**Verify GREEN:** `pytest tests/test_cli_account.py::test_account_status -xvs`
- Must pass

**Verify no regression:** `pytest`
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/claude-tools-rewrite/reports/cycle-3-9-notes.md

---
