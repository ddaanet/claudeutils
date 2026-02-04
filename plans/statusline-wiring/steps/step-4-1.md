# Cycle 4.1

**Plan**: `plans/statusline-wiring/runbook.md`
**Execution Model**: haiku
**Report Path**: `plans/statusline-wiring/reports/cycle-4-1-notes.md`

---

## Cycle 4.1: Update create_switchback_plist to include Month and Day

**Objective**: account.switchback.create_switchback_plist() adds Month and Day to StartCalendarInterval (D7)
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** tests/test_switchback.py (or new test file) mocks plistlib.dump, asserts create_switchback_plist() writes plist with Month and Day fields in StartCalendarInterval

**Expected failure:**
```
AssertionError: 'Month' not in plist_data['StartCalendarInterval']
```

**Why it fails:** create_switchback_plist() currently only writes Hour/Minute/Second

**Verify RED:** pytest tests/test_account_switchback.py::test_create_switchback_plist_includes_month_day -xvs
- Must fail with KeyError or AssertionError (Month/Day missing)
- If passes, STOP - Month/Day may already be included

---

**GREEN Phase:**

**Implementation:** Update create_switchback_plist() to add target_time.month and target_time.day to StartCalendarInterval dict

**Changes:**
- File: src/claudeutils/account/switchback.py
  Action: Add "Month": target_time.month and "Day": target_time.day to StartCalendarInterval dict

**Verify GREEN:** pytest tests/test_account_switchback.py::test_create_switchback_plist_includes_month_day -xvs
- Must pass

**Verify no regression:** pytest tests/
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/statusline-wiring/reports/cycle-4-1-notes.md

---
