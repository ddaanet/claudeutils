# Cycle 1.6

**Plan**: `plans/statusline-parity/runbook.md`
**Execution Model**: haiku
**Phase**: 1
**Report Path**: `plans/statusline-parity/reports/cycle-1-6-notes.md`

---

## Cycle 1.6: Format Cost with Emoji

**Objective**: Add `format_cost()` method with 💰 prefix

**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

### RED Phase

**Test:** `test_format_cost` in `tests/test_statusline_display.py`

**Assertions:**
- `format_cost(0.05)` returns string containing "💰" emoji
- Output contains "$0.05" formatted with 2 decimal places
- Format is `{emoji} ${amount:.2f}` (e.g., "💰 $0.05")
- `format_cost(1.234)` returns "💰 $1.23" (rounded to 2 decimals)

**Expected failure:** `AttributeError: 'StatuslineFormatter' object has no attribute 'format_cost'`

**Why it fails:** Method doesn't exist yet

**Verify RED:** `pytest tests/test_statusline_display.py::test_format_cost -v`

---

### GREEN Phase

**Implementation:** Add `format_cost()` method to StatuslineFormatter

**Behavior:**
- Accept cost as float
- Format as dollar amount with 2 decimal places
- Prefix with "💰" emoji
- Return formatted string: `💰 ${amount:.2f}`

**Approach:** Simple emoji prefix + dollar formatting per D1. Shell reference line 475.

**Changes:**
- File: `src/claudeutils/statusline/display.py`
  Action: Add format_cost(amount: float) method
  Location hint: After format_git_status()

**Verify GREEN:** `pytest tests/test_statusline_display.py::test_format_cost -v`
- Must pass

**Verify no regression:** `just test`
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED (AttributeError), passes during GREEN, no breaks
**Report Path**: plans/statusline-parity/reports/cycle-1-6-notes.md

---
