# Cycle 3.10

**Plan**: `plans/claude-tools-rewrite/runbook.md`
**Common Context**: See plan file for context

---

### Cycle 3.10: Account CLI - plan command

**Objective**: Implement `claudeutils account plan` switching to plan mode
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku
**Dependencies**: [DEPENDS: 1.8, 1.11]

**Implementation:**

**RED Phase:**

**Test:** CLI command `claudeutils account plan` switches mode and writes files

**Expected failure:**
```
AttributeError: 'Group' object has no attribute 'plan'
```

**Why it fails:** plan command doesn't exist

**Verify RED:** `pytest tests/test_cli_account.py::test_account_plan -xvs`
- Must fail with AttributeError
- If passes, STOP - command may already exist

---

**GREEN Phase:**

**Implementation:** Create account plan command

**Changes:**
- File: src/claudeutils/account/cli.py
  Action: Add 'plan' command calling mode switching logic, writing account-mode and claude-env files
- File: tests/test_cli_account.py
  Action: Test with CliRunner and tmp_path, verify files written

**Verify GREEN:** `pytest tests/test_cli_account.py::test_account_plan -xvs`
- Must pass

**Verify no regression:** `pytest`
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/claude-tools-rewrite/reports/cycle-3-10-notes.md

---
