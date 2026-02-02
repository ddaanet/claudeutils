# Cycle 1.7

**Plan**: `plans/claude-tools-rewrite/runbook.md`
**Common Context**: See plan file for context

---

### Cycle 1.7: Provider Protocol definition

**Objective**: Define Provider Protocol with name, claude_env_vars, validate, settings_json_patch methods
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** Provider Protocol can be used as type annotation

**Expected failure:**
```
AttributeError: module 'claudeutils.account' has no attribute 'Provider'
```

**Why it fails:** Provider Protocol doesn't exist

**Verify RED:** `pytest tests/test_account_providers.py::test_provider_protocol_exists -xvs`
- Must fail with AttributeError
- If passes, STOP - protocol may already exist

---

**GREEN Phase:**

**Implementation:** Create Provider Protocol with method signatures

**Changes:**
- File: src/claudeutils/account/providers.py
  Action: Create Provider Protocol with name: str, claude_env_vars(), validate(), settings_json_patch() methods
- File: src/claudeutils/account/__init__.py
  Action: Add `from .providers import Provider`
- File: tests/test_account_providers.py
  Action: Test that Provider can be imported and used in type annotation

**Verify GREEN:** `pytest tests/test_account_providers.py::test_provider_protocol_exists -xvs`
- Must pass

**Verify no regression:** `pytest`
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/claude-tools-rewrite/reports/cycle-1-7-notes.md

---
