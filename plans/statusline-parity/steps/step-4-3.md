# Cycle 4.3

**Plan**: `plans/statusline-parity/runbook.md`
**Execution Model**: haiku
**Phase**: 4
**Report Path**: `plans/statusline-parity/reports/cycle-4-3-notes.md`

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
