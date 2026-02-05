# Cycle 4.2

**Plan**: `plans/statusline-parity/runbook.md`
**Execution Model**: haiku
**Phase**: 4
**Report Path**: `plans/statusline-parity/reports/cycle-4-2-notes.md`

---

## Cycle 4.2: CLI Line 2 Composition

**Objective**: Integrate format_mode() into Line 2 composition with usage data

**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

### RED Phase

**Test:** `test_cli_line2_integration` in `tests/test_statusline_cli.py`

**Test Description (prose):**

Test that CLI Line 2 composes mode indicator with usage data. The test should:

- Mock the UsageData context with account mode "plan" and usage statistics
- Call the CLI to generate Line 2
- Assert output contains formatted mode component (🎫 emoji + GREEN "Plan" text)
- Assert output is composed of mode indicator followed by usage data (session time, percentage, patterns)
- Test with account mode "api" and verify 💳 emoji + YELLOW "API" text
- Assert formatting differs between modes (emoji/color change but structure stays same)
- Assert usage data portion remains unchanged (time, percentages, bar charts)
- Verify no raw "mode:" text prefix in output (should be emoji + colored text instead)
- Test with missing/null account mode and verify graceful fallback (perhaps no mode displayed or default mode)

**Expected failure:** Output contains "mode:" text prefix instead of formatted emoji; or mode formatting method not called

**Why it fails:** CLI hasn't been updated to use `format_mode()` yet

**Verify RED:** `pytest tests/test_statusline_cli.py::test_cli_line2_integration -v`

---

### GREEN Phase

**Implementation:** Update CLI Line 2 composition to call format_mode()

**Behavior:**
- Replace "mode:" text prefix with formatter method call
- Call `format_mode()` with account mode string
- Prepend formatted mode to existing usage data string
- Maintain existing usage data formatting (time, percentages, bar charts)
- Handle null/missing mode gracefully (skip display or use default)

**Hints:**
- format_mode() returns emoji + colored mode text
- Shell reference lines 632-642 shows Line 2 format
- Spacing between mode and usage data should be two spaces

**Approach:** Replace "mode:" text prefix with `format_mode()` result. Shell reference lines 632-642 shows Line 2 format with mode indicator.

**Changes:**
- File: `src/claudeutils/statusline/cli.py`
  Action: Refactor Line 2 composition to use `format_mode()`
  Location hint: Within the function that generates Line 2 output

**Verify GREEN:** `pytest tests/test_statusline_cli.py::test_cli_line2_integration -v`
- Must pass

**Verify no regression:** `just test`
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED (no emoji formatting for mode), passes during GREEN, no breaks
**Report Path**: plans/statusline-parity/reports/cycle-4-2-notes.md

---
