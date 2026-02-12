# Cycle 5.5

**Plan**: `plans/worktree-update/runbook.md`
**Execution Model**: haiku
**Phase**: 5

---

## Cycle 5.5: Environment initialization — `just setup` with warning on failure

**Objective:** Run `just setup` in worktree after creation, warn if unavailable (don't fall back to manual commands).

**RED Phase:**

**Test:** `test_new_environment_initialization`
**Assertions:**
- After `new <slug>`, `just setup` invoked with `cwd=<wt-path>`
- If `just` command available: `just setup` runs, exit code captured
- If `just` unavailable (command not found): warning printed, no error raised
- If `just setup` fails (exit ≠ 0): warning printed with stderr, no error raised (prerequisite failure, not fatal)
- No fallback commands executed (no `uv sync`, `direnv allow` called directly)

**Expected failure:** Error raised when `just` missing, or subprocess called without `cwd` parameter, or fallback commands attempted

**Why it fails:** Environment initialization not implemented, or incorrect error handling

**Verify RED:** `pytest tests/test_worktree_new.py::test_new_environment_initialization -v`

---

**GREEN Phase:**

**Implementation:** Add environment initialization step with graceful failure handling

**Behavior:**
- Check if `just` available: `subprocess.run(['just', '--version'], ...)` with `check=False`
- If available: run `just setup` with `cwd=<wt-path>` and `check=False`
- Capture stderr and exit code
- If exit ≠ 0: print warning with stderr (don't raise exception)
- If `just` unavailable: print warning message (prerequisite missing)
- No fallback to manual commands (user must fix prerequisite)

**Approach:** Subprocess calls with error handling, conditional warnings, no exceptions raised

**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Add environment initialization in `new` command
  Location hint: After sandbox registration, before final output
- File: `src/claudeutils/worktree/cli.py`
  Action: Check for `just` availability
  Location hint: Use subprocess.run with check=False to test command existence
- File: `src/claudeutils/worktree/cli.py`
  Action: Run `just setup` with cwd parameter if available
  Location hint: subprocess.run with cwd=<wt-path>
- File: `src/claudeutils/worktree/cli.py`
  Action: Print warning messages for failures (don't raise exceptions)
  Location hint: Check exit codes, print to stderr or stdout as appropriate

**Verify GREEN:** `pytest tests/test_worktree_new.py::test_new_environment_initialization -v`
- Must pass

**Verify no regression:** `pytest tests/test_worktree_new.py -v`
- All previous Cycle 5 tests still pass

---
