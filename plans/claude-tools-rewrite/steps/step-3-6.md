# Cycle 3.6

**Plan**: `plans/claude-tools-rewrite/runbook.md`
**Common Context**: See plan file for context

---

### Cycle 3.6: LaunchAgent plist generation

**Objective**: Implement create_switchback_plist() using plistlib
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** create_switchback_plist() generates valid plist file

**Expected failure:**
```
AttributeError: module 'claudeutils.account' has no attribute 'create_switchback_plist'
```

**Why it fails:** Function doesn't exist

**Verify RED:** `pytest tests/test_account_switchback.py::test_create_switchback_plist -xvs`
- Must fail with AttributeError
- If passes, STOP - function may already exist

---

**GREEN Phase:**

**Implementation:** Create create_switchback_plist() in switchback.py

**Changes:**
- File: src/claudeutils/account/switchback.py
  Action: Create create_switchback_plist(switchback_time) using plistlib.dump()
- File: src/claudeutils/account/__init__.py
  Action: Add `from .switchback import create_switchback_plist`
- File: tests/test_account_switchback.py
  Action: Test with tmp_path, verify plist structure and calendar interval

**Verify GREEN:** `pytest tests/test_account_switchback.py::test_create_switchback_plist -xvs`
- Must pass

**Verify no regression:** `pytest`
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/claude-tools-rewrite/reports/cycle-3-6-notes.md

---
