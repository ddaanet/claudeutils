# Cycle 2.9

**Plan**: `plans/claude-tools-rewrite/runbook.md`
**Common Context**: See plan file for context

---

### Cycle 2.9: Model override file write

**Objective**: Write env var dict to claude-model-overrides file
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** write_overrides() writes dict as bash export statements

**Expected failure:**
```
AttributeError: module 'claudeutils.model.overrides' has no attribute 'write_overrides'
```

**Why it fails:** Function doesn't exist

**Verify RED:** `pytest tests/test_model_overrides.py::test_write_overrides -xvs`
- Must fail with AttributeError
- If passes, STOP - function may already exist

---

**GREEN Phase:**

**Implementation:** Create write_overrides() function

**Changes:**
- File: src/claudeutils/model/overrides.py
  Action: Create write_overrides(path, vars) writing "export KEY=value\n" lines
- File: tests/test_model_overrides.py
  Action: Test with tmp_path, verify file format

**Verify GREEN:** `pytest tests/test_model_overrides.py::test_write_overrides -xvs`
- Must pass

**Verify no regression:** `pytest`
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/claude-tools-rewrite/reports/cycle-2-9-notes.md

---

**Checkpoint**
1. Fix: Run `just dev`. Sonnet quiet-task fixes failures. Commit when green.
2. Vet: Review LiteLLM config parsing robustness, override file format correctness. Commit fixes.

---
