# Cycle 2.1

**Plan**: `plans/statusline-wiring/runbook.md`
**Execution Model**: haiku
**Report Path**: `plans/statusline-wiring/reports/cycle-2-1-notes.md`

---

## Cycle 2.1: Detect git repository and return branch name

**Objective**: get_git_status() calls subprocess to detect if in git repo and get branch name
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** tests/test_statusline_context.py mocks subprocess.run, tests get_git_status() returns GitStatus(branch="main", dirty=False) when git commands succeed

**Expected failure:**
```
ModuleNotFoundError: No module named 'claudeutils.statusline.context'
```

**Why it fails:** context.py doesn't exist yet

**Verify RED:** pytest tests/test_statusline_context.py::test_get_git_status_in_repo -xvs
- Must fail with ModuleNotFoundError
- If passes, STOP - context.py may already exist

---

**GREEN Phase:**

**Implementation:** Create src/claudeutils/statusline/context.py with get_git_status() using subprocess.run for git commands

**Changes:**
- File: src/claudeutils/statusline/context.py
  Action: Create with get_git_status() → GitStatus, call subprocess.run(["git", "rev-parse", "--git-dir"]) and subprocess.run(["git", "branch", "--show-current"])
- File: src/claudeutils/statusline/models.py
  Action: Add GitStatus(BaseModel) with branch: str | None, dirty: bool fields

**Verify GREEN:** pytest tests/test_statusline_context.py::test_get_git_status_in_repo -xvs
- Must pass

**Verify no regression:** pytest tests/test_statusline_*.py
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/statusline-wiring/reports/cycle-2-1-notes.md

---
