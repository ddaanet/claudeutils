# Cycle 1.5

**Plan**: `plans/statusline-parity/runbook.md`
**Execution Model**: haiku
**Phase**: 1
**Report Path**: `plans/statusline-parity/reports/cycle-1-5-notes.md`

---

## Cycle 1.5: Format Git Status with Emoji

**Objective**: Add `format_git_status()` method with ✅/🟡 emoji and branch color

**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

### RED Phase

**Test:** `test_format_git_status` in `tests/test_statusline_display.py`

**Assertions:**
- `format_git_status(GitStatus(branch="main", dirty=False))` returns string containing "✅" emoji
- Output contains "main" branch name
- Output contains ANSI green color code (`\033[32m`)
- `format_git_status(GitStatus(branch="feature", dirty=True))` returns string containing "🟡" emoji
- Output contains "feature" branch name
- Output contains ANSI yellow color code (`\033[33m`) and bold code (`\033[1m`)
- Format is `{emoji} {colored_branch}` (e.g., "✅ main" or "🟡 feature")

**Expected failure:** `AttributeError: 'StatuslineFormatter' object has no attribute 'format_git_status'`

**Why it fails:** Method doesn't exist yet

**Verify RED:** `pytest tests/test_statusline_display.py::test_format_git_status -v`

---

### GREEN Phase

**Implementation:** Add `format_git_status()` method to StatuslineFormatter

**Behavior:**
- Accept GitStatus model (branch: str, dirty: bool)
- If dirty is False: Use "✅" emoji, apply GREEN color to branch
- If dirty is True: Use "🟡" emoji, apply YELLOW + BOLD to branch
- Return formatted string: `{emoji} {colored_branch}`

**Approach:** Conditional emoji and color per dirty state. Shell reference lines 459-461.

**Changes:**
- File: `src/claudeutils/statusline/display.py`
  Action: Add format_git_status(status: GitStatus) method
  Location hint: After format_directory()

**Verify GREEN:** `pytest tests/test_statusline_display.py::test_format_git_status -v`
- Must pass

**Verify no regression:** `just test`
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED (AttributeError), passes during GREEN, no breaks
**Report Path**: plans/statusline-parity/reports/cycle-1-5-notes.md

---
