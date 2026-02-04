# Cycle 4.2

**Plan**: `plans/statusline-wiring/runbook.md`
**Execution Model**: haiku
**Report Path**: `plans/statusline-wiring/reports/cycle-4-2-notes.md`

---

## Cycle 4.2: Add read_switchback_plist function

**Objective**: account.switchback.read_switchback_plist() parses plist and returns datetime (D7)
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** tests/test_account_switchback.py mocks Path.exists() to return True and plistlib.load() to return mock plist, asserts read_switchback_plist() returns datetime with correct month/day/hour/minute

**Expected failure:**
```
AttributeError: module 'claudeutils.account.switchback' has no attribute 'read_switchback_plist'
```

**Why it fails:** read_switchback_plist() function doesn't exist yet

**Verify RED:** pytest tests/test_account_switchback.py::test_read_switchback_plist -xvs
- Must fail with AttributeError
- If passes, STOP - function may already exist

---

**GREEN Phase:**

**Implementation:** Add read_switchback_plist() → datetime | None that reads plist from ~/Library/LaunchAgents/com.anthropic.claude.switchback.plist, extracts Month/Day/Hour/Minute, constructs datetime

**Changes:**
- File: src/claudeutils/account/switchback.py
  Action: Add read_switchback_plist() function, check Path.exists(), load plist with plistlib, extract StartCalendarInterval fields, build datetime, handle past dates (add year)

**Verify GREEN:** pytest tests/test_account_switchback.py::test_read_switchback_plist -xvs
- Must pass

**Verify no regression:** pytest tests/
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/statusline-wiring/reports/cycle-4-2-notes.md

---
