# Cycle 3.13

**Plan**: `plans/claude-tools-rewrite/runbook.md`
**Common Context**: See plan file for context

---

### Cycle 3.13: Model CLI - set command

**Objective**: Implement `claudeutils model set` writing override file
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku
**Dependencies**: [DEPENDS: 2.8, 2.9]

**Implementation:**

**RED Phase:**

**Test:** CLI command `claudeutils model set <model>` writes override file

**Expected failure:**
```
AttributeError: 'Group' object has no attribute 'set'
```

**Why it fails:** set command doesn't exist

**Verify RED:** `pytest tests/test_cli_model.py::test_model_set -xvs`
- Must fail with AttributeError
- If passes, STOP - command may already exist

---

**GREEN Phase:**

**Implementation:** Create model set command

**Changes:**
- File: src/claudeutils/model/cli.py
  Action: Add 'set' command calling write_overrides()
- File: tests/test_cli_model.py
  Action: Test with CliRunner and tmp_path, verify override file

**Verify GREEN:** `pytest tests/test_cli_model.py::test_model_set -xvs`
- Must pass

**Verify no regression:** `pytest`
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/claude-tools-rewrite/reports/cycle-3-13-notes.md

---
