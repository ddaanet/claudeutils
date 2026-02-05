# Phase 4: CLI Integration and Validation (3 cycles)

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

## Cycle 4.3: Integration Validation

**Objective**: End-to-end validation of visual parity with shell output and all requirements met

**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

### RED Phase

**Test:** `test_cli_end_to_end_visual_parity` in `tests/test_statusline_cli.py`

**Test Description (prose):**

Test end-to-end visual parity between Python and shell implementations. The test should:

- Create integration test data representing a typical session state (model, directory, git status, cost, tokens, account mode)
- Call the Python CLI to generate statusline output (both lines)
- Create equivalent shell output using the shell command with same input data (if feasible; otherwise use hardcoded expected patterns)
- Compare Python Line 1 against shell Line 1 format:
  - Verify emoji order: medal, directory folder, git status, cost, brain (🥇/🥈/🥉, 📁, ✅/🟡, 💰, 🧠)
  - Verify color codes are ANSI standard (comparing byte sequences)
  - Verify abbreviations match: "Opus"/"Sonnet"/"Haiku" not full display_name
  - Verify token bar uses correct Unicode blocks (█ for full, ▏▎▍▌▋▊▉ for partial)
  - Verify color gradient on token bar matches thresholds
- Compare Python Line 2 against shell Line 2 format:
  - Verify mode emoji: 🎫 for plan, 💳 for api
  - Verify usage data structure (time, percentages, symbols)
  - Verify mode emoji color matches mode type
- Test edge cases:
  - Missing directory (fallback behavior)
  - Unknown model name (no emoji, full display_name)
  - High token count triggering BRRED+BLINK color
  - Dirty git state with special characters in branch name
  - Cost edge cases ($0.00, $99.99, $1234.56)
- Verify all requirements from design (R1-R7) are visually present
- Test with Python environment variables set and unset (VIRTUAL_ENV, CONDA_DEFAULT_ENV)

**Expected failure:** Visual format doesn't match shell (emoji missing, wrong order, color codes incorrect, bar width wrong)

**Why it fails:** Formatter methods may have implementation gaps or CLI composition may still have bugs

**Verify RED:** `pytest tests/test_statusline_cli.py::test_cli_end_to_end_visual_parity -v`

---

### GREEN Phase

**Implementation:** Fix any presentation gaps identified during RED phase

**Behavior:**
- Review test output from RED phase
- Identify which formatting elements don't match shell output
- Apply fixes to display.py format methods if colors/emoji are incorrect
- Apply fixes to cli.py composition if ordering/spacing is wrong
- Verify token bar algorithm matches shell (blocks, Unicode characters, color thresholds)
- Verify all emoji are rendered correctly
- Verify ANSI color codes are correct
- Test visual rendering in terminal (not just byte comparison) to catch emoji/color rendering issues
- Verify fallback behavior for edge cases (unknown models, missing data)

**Approach:** Iterative validation and fix. Shell reference lines 416-488 for line format. Terminal inspection for visual rendering.

**Changes:**
- File: `src/claudeutils/statusline/display.py`
  Action: Fix any format methods that don't produce correct output
  Location hint: Within format methods, may need color code adjustments or Unicode block corrections
- File: `src/claudeutils/statusline/cli.py`
  Action: Fix composition if ordering/spacing incorrect
  Location hint: Within Line 1 and Line 2 composition functions

**Verify GREEN:**
- `pytest tests/test_statusline_cli.py::test_cli_end_to_end_visual_parity -v` passes
- Visual inspection: Run `claude-statusline` in terminal and compare against shell output visually
- Emoji render correctly (not as boxes or placeholders)
- Colors display as intended (no color code artifacts)
- Token bars align and fill correctly
- All test data cases pass

**Verify no regression:** `just test`
- All existing tests pass

---

**Expected Outcome**: GREEN verification with visual validation, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug/fix; Regression → STOP; Visual rendering broken → Debug ANSI codes
**Validation**: RED verified ✓, GREEN verified ✓, Visual inspection ✓, No regressions ✓
**Success Criteria**: All visual elements match shell output, emoji render correctly, colors display, token bar accurate, all edge cases handled
**Report Path**: plans/statusline-parity/reports/cycle-4-3-notes.md

---

## Full Checkpoint (end of Phase 4)

**Three-part checkpoint:** Fix + Vet + Functional

### Part 1: Fix

**Action:** Run `just dev`. Haiku quiet-task diagnoses and fixes failures.

**Process:**
- Run full test suite (`just test`)
- If tests fail: Quiet-task diagnoses root cause, applies fixes, re-runs tests
- Commit when all tests passing

**Verification:** All tests pass, test output shows no failures

### Part 2: Vet

**Action:** Delegate to vet-fix-agent for review + critical/major fixes.

**Process:**
- Vet agent reviews Phase 4 implementations (cycles 4.1-4.3 in cli.py and display.py)
- Checks for:
  - Format method calls are correct (parameters, return values)
  - CLI composition logic is sound (spacing, ordering, edge cases)
  - No presentation gaps (emoji, colors, bars all rendering)
  - Visual parity with shell confirmed
- Applies critical/major fixes immediately
- Writes report to `plans/statusline-parity/reports/phase-4-vet-report.md`

**Verification:** Vet report shows no unfixable issues, critical/major fixes applied

### Part 3: Functional

**Action:** End-to-end functional validation

**Process:**
1. Run `just test` to confirm all tests pass
2. Run `claude-statusline` in terminal with real session data
3. Compare output visually against shell output from same working directory
4. Verify all visual elements match:
   - Model emoji and color correct
   - Directory emoji and color correct
   - Git status emoji correct for clean/dirty state
   - Cost emoji and format correct
   - Context emoji, color, and token bar correct
   - Mode emoji and color correct for plan/api modes
   - Token bar width and Unicode blocks correct
5. Test with various edge cases:
   - High token count (should trigger BRRED+BLINK if >= 150k)
   - Unknown model name (should show full name, no emoji)
   - Dirty git state (should show 🟡 and YELLOW+BOLD)
   - Cost edge cases ($0.00, large amounts)
6. Verify no data gathering or functional behavior changes (only presentation)

**Verification:** Visual output matches shell, all edge cases behave correctly, no functional regressions, all requirements (R1-R7) visually present

**Success Criteria:**
- All tests pass (Part 1)
- Vet report shows no unfixable issues (Part 2)
- Visual inspection confirms parity with shell (Part 3)
- All edge cases handled correctly
- All requirements met

**Report Path**: plans/statusline-parity/reports/phase-4-checkpoint-report.md

---

**End of Phase 4: CLI Integration Complete**
