# Cycle 1.4

**Plan**: `plans/statusline-parity/runbook.md`
**Execution Model**: haiku
**Phase**: 1
**Report Path**: `plans/statusline-parity/reports/cycle-1-4-notes.md`

---

## Cycle 1.4: Format Directory with Emoji

**Objective**: Add `format_directory()` method with 📁 prefix and CYAN color

**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

### RED Phase

**Test:** `test_format_directory` in `tests/test_statusline_display.py`

**Assertions:**
- `format_directory("claudeutils")` returns string containing "📁" emoji
- Output contains directory name "claudeutils"
- Output contains ANSI cyan color code (`\033[36m`)
- Format is `{emoji} {colored_name}` (e.g., "📁 claudeutils")

**Expected failure:** `AttributeError: 'StatuslineFormatter' object has no attribute 'format_directory'`

**Why it fails:** Method doesn't exist yet

**Verify RED:** `pytest tests/test_statusline_display.py::test_format_directory -v`

---

### GREEN Phase

**Implementation:** Add `format_directory()` method to StatuslineFormatter

**Behavior:**
- Accept directory name as string
- Prefix with "📁" emoji
- Apply CYAN color to directory name
- Return formatted string: `📁 {cyan_name}`

**Approach:** Simple emoji prefix + color application per D1. Shell reference line 448.

**Changes:**
- File: `src/claudeutils/statusline/display.py`
  Action: Add format_directory(name: str) method
  Location hint: After format_model()

**Verify GREEN:** `pytest tests/test_statusline_display.py::test_format_directory -v`
- Must pass

**Verify no regression:** `just test`
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED (AttributeError), passes during GREEN, no breaks
**Report Path**: plans/statusline-parity/reports/cycle-1-4-notes.md

---
