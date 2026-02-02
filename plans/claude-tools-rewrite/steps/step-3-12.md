# Cycle 3.12

**Plan**: `plans/claude-tools-rewrite/runbook.md`
**Common Context**: See plan file for context

---

### Cycle 3.12: Model CLI - list command

**Objective**: Implement `claudeutils model list` showing available models
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku
**Dependencies**: [DEPENDS: 2.6, 2.7]

**Implementation:**

**RED Phase:**

**Test:** CLI command `claudeutils model list` outputs model names

**Expected failure:**
```
AttributeError: 'Group' object has no attribute 'list'
```

**Why it fails:** list command doesn't exist

**Verify RED:** `pytest tests/test_cli_model.py::test_model_list -xvs`
- Must fail with AttributeError
- If passes, STOP - command may already exist

---

**GREEN Phase:**

**Implementation:** Create model list command

**Changes:**
- File: src/claudeutils/model/cli.py
  Action: Create Click command group 'model' with 'list' command calling load_litellm_config()
- File: src/claudeutils/cli.py
  Action: Add model command group
- File: tests/test_cli_model.py
  Action: Test with CliRunner, mock config file

**Verify GREEN:** `pytest tests/test_cli_model.py::test_model_list -xvs`
- Must pass

**Verify no regression:** `pytest`
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/claude-tools-rewrite/reports/cycle-3-12-notes.md

---
