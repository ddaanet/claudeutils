# Cycle 2.3

**Plan**: `plans/statusline-wiring/runbook.md`
**Execution Model**: haiku
**Report Path**: `plans/statusline-wiring/reports/cycle-2-3-notes.md`

---

## Cycle 2.3: Handle not in git repo case

**Objective**: get_git_status() returns GitStatus(branch=None, dirty=False) when not in git repo
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** tests/test_statusline_context.py mocks subprocess to raise CalledProcessError, asserts get_git_status() returns GitStatus(branch=None, dirty=False)

**Expected failure:**
```
CalledProcessError: not caught, test crashes
```

**Why it fails:** No exception handling for subprocess failures

**Verify RED:** pytest tests/test_statusline_context.py::test_get_git_status_not_in_repo -xvs
- Must fail with CalledProcessError
- If passes, STOP - exception handling may already exist

---

**GREEN Phase:**

**Implementation:** Wrap subprocess calls in try/except, return GitStatus(branch=None, dirty=False) on subprocess.CalledProcessError or FileNotFoundError

**Changes:**
- File: src/claudeutils/statusline/context.py
  Action: Add try/except around subprocess calls, catch subprocess.CalledProcessError and FileNotFoundError, return default GitStatus

**Verify GREEN:** pytest tests/test_statusline_context.py::test_get_git_status_not_in_repo -xvs
- Must pass

**Verify no regression:** pytest tests/test_statusline_*.py
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/statusline-wiring/reports/cycle-2-3-notes.md

---
