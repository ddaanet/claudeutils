# Cycle 3.14

**Plan**: `plans/claude-tools-rewrite/runbook.md`
**Common Context**: See plan file for context

---

### Cycle 3.14: Model CLI - reset command

**Objective**: Implement `claudeutils model reset` removing override file
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** CLI command `claudeutils model reset` deletes override file

**Expected failure:**
```
AttributeError: 'Group' object has no attribute 'reset'
```

**Why it fails:** reset command doesn't exist

**Verify RED:** `pytest tests/test_cli_model.py::test_model_reset -xvs`
- Must fail with AttributeError
- If passes, STOP - command may already exist

---

**GREEN Phase:**

**Implementation:** Create model reset command

**Changes:**
- File: src/claudeutils/model/cli.py
  Action: Add 'reset' command removing override file
- File: tests/test_cli_model.py
  Action: Test with CliRunner, verify file deletion

**Verify GREEN:** `pytest tests/test_cli_model.py::test_model_reset -xvs`
- Must pass

**Verify no regression:** `pytest`
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/claude-tools-rewrite/reports/cycle-3-14-notes.md

---
