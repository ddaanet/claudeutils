# Cycle 4.1

**Plan**: `plans/statusline-parity/runbook.md`
**Execution Model**: haiku
**Phase**: 4
**Report Path**: `plans/statusline-parity/reports/cycle-4-1-notes.md`

---

## Cycle 4.1: CLI Line 1 Composition

**Objective**: Integrate format methods into Line 1 composition, replacing plain string concatenation

**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

### RED Phase

**Test:** `test_cli_line1_integration` in `tests/test_statusline_cli.py`

**Test Description (prose):**

Test that CLI Line 1 composes all formatted elements in correct order with proper spacing. The test should:

- Mock the UsageData context with model "Claude Sonnet 4", directory "claudeutils", git branch "tools-rewrite" (clean), cost $0.05, and context 1500 tokens
- Mock thinking state as enabled
- Call the CLI to generate Line 1
- Assert output contains formatted model component (emoji + color + abbreviated name)
- Assert output contains formatted directory component (📁 emoji + CYAN colored name)
- Assert output contains formatted git status (✅ emoji for clean state + GREEN colored branch)
- Assert output contains formatted cost (💰 emoji + dollar amount)
- Assert output contains formatted context (🧠 emoji + colored token count + horizontal token bar)
- Assert ordering: model appears first, then directory, then git, then cost, then context
- Assert spacing between elements (single space separator)
- Verify no raw plain text like "Claude Sonnet" in output (should be formatted)
- Test with dirty git state and verify 🟡 emoji and YELLOW+BOLD branch formatting
- Test with thinking disabled and verify 😶 emoji after model medal

**Expected failure:** Output doesn't match expected formatted strings; may contain unfiled format method calls or raw unformatted data

**Why it fails:** CLI hasn't been updated to use formatter methods yet

**Verify RED:** `pytest tests/test_statusline_cli.py::test_cli_line1_integration -v`

---

### GREEN Phase

**Implementation:** Update CLI Line 1 composition to call formatter methods

**Behavior:**
- Replace inline formatting with formatter method calls
- Call `format_model()` with model name and thinking state
- Call `format_directory()` with directory name
- Call `format_git_status()` with git status data
- Call `format_cost()` with cost value
- Call `format_context()` with token count
- Join formatted elements with single space separator
- Result should match shell output format (emoji, colors, ordering)

**Hints:**
- Formatter methods are already implemented in display.py
- Each format method returns a formatted string with emoji and ANSI color codes
- Model formatter needs thinking state parameter
- Shell reference lines 441-488 shows expected output format

**Changes:**
- File: `src/claudeutils/statusline/cli.py`
  Action: Refactor Line 1 composition function to use formatter methods
  Location hint: Within the function that generates Line 1 output

**Verify GREEN:** `pytest tests/test_statusline_cli.py::test_cli_line1_integration -v`
- Must pass

**Verify no regression:** `just test`
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED (output format mismatch), passes during GREEN, no breaks
**Report Path**: plans/statusline-parity/reports/cycle-4-1-notes.md

---
