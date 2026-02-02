# Cycle 2.8

**Plan**: `plans/claude-tools-rewrite/runbook.md`
**Common Context**: See plan file for context

---

### Cycle 2.8: Model override file read

**Objective**: Read claude-model-overrides file returning env var dict
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** read_overrides() parses bash env var file into dict

**Expected failure:**
```
AttributeError: module 'claudeutils.model' has no attribute 'read_overrides'
```

**Why it fails:** Function doesn't exist

**Verify RED:** `pytest tests/test_model_overrides.py::test_read_overrides -xvs`
- Must fail with AttributeError
- If passes, STOP - function may already exist

---

**GREEN Phase:**

**Implementation:** Create read_overrides() in overrides.py

**Changes:**
- File: src/claudeutils/model/overrides.py
  Action: Create read_overrides(path) parsing "export VAR=value" lines
- File: src/claudeutils/model/__init__.py
  Action: Add `from .overrides import read_overrides`
- File: tests/test_model_overrides.py
  Action: Test with tmp_path fixture containing sample override file

**Verify GREEN:** `pytest tests/test_model_overrides.py::test_read_overrides -xvs`
- Must pass

**Verify no regression:** `pytest`
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/claude-tools-rewrite/reports/cycle-2-8-notes.md

---
