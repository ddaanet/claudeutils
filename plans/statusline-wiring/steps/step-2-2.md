# Cycle 2.2

**Plan**: `plans/statusline-wiring/runbook.md`
**Execution Model**: haiku
**Report Path**: `plans/statusline-wiring/reports/cycle-2-2-notes.md`

---

## Cycle 2.2: Detect dirty git status with porcelain output

**Objective**: get_git_status() detects dirty working tree using git status --porcelain
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** tests/test_statusline_context.py mocks subprocess to return non-empty porcelain output, asserts get_git_status() returns dirty=True

**Expected failure:**
```
AssertionError: assert False == True
```

**Why it fails:** get_git_status() doesn't check git status --porcelain yet

**Verify RED:** pytest tests/test_statusline_context.py::test_get_git_status_dirty -xvs
- Must fail with AssertionError (dirty=False when expected True)
- If passes, STOP - dirty detection may already exist

---

**GREEN Phase:**

**Implementation:** Add subprocess call for git status --porcelain, set dirty=True if output non-empty

**Changes:**
- File: src/claudeutils/statusline/context.py
  Action: Add subprocess.run(["git", "status", "--porcelain"]) call, set dirty = bool(result.stdout.strip())

**Verify GREEN:** pytest tests/test_statusline_context.py::test_get_git_status_dirty -xvs
- Must pass

**Verify no regression:** pytest tests/test_statusline_*.py
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/statusline-wiring/reports/cycle-2-2-notes.md

---
