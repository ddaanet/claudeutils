# TDD Runbook Review: statusline-parity Phase 1

## Summary

- Total cycles: 7
- Violations found: 7 critical
- Overall assessment: NEEDS REVISION

## Critical Issues

### Issue 1: Prescriptive Implementation Code in GREEN Phases

**Problem:** All 7 cycles contain complete implementation code in GREEN phases. This violates TDD principles where tests should drive implementation, not prescribe it.

**Locations and Details:**

**Cycle 1.1 (lines 39-57):**
- Complete `_extract_model_tier()` implementation with full logic
- 18 lines of prescriptive Python code
- Violates: Tests should drive discovery of tier extraction logic

**Cycle 1.2 (lines 122-160):**
- Complete class constants `MODEL_EMOJI` and `MODEL_COLORS` dictionaries
- Complete `format_model()` implementation with full logic
- 38 lines of prescriptive code
- Violates: Tests should drive discovery of emoji/color mappings and formatting logic

**Cycle 1.3 (lines 214-239):**
- Complete modified `format_model()` with thinking indicator logic
- 25 lines of prescriptive code
- Violates: Tests should drive discovery of thinking indicator placement

**Cycle 1.4 (lines 288-299):**
- Complete `format_directory()` implementation
- 11 lines of prescriptive code
- Violates: Tests should drive discovery of directory formatting

**Cycle 1.5 (lines 355-374):**
- Complete `format_git_status()` implementation with conditional logic
- 19 lines of prescriptive code
- Violates: Tests should drive discovery of status-based emoji/color selection

**Cycle 1.6 (lines 431-442):**
- Complete `format_cost()` implementation with formatting string
- 11 lines of prescriptive code
- Violates: Tests should drive discovery of cost formatting

**Cycle 1.7 (lines 497-517):**
- Complete `format_mode()` implementation with conditional logic
- 20 lines of prescriptive code
- Violates: Tests should drive discovery of mode-based emoji/color selection

**Why This Matters:**
- Agent becomes code copier instead of implementer
- No discovery process — just transcription
- Tests don't actually drive implementation
- Violates RED→GREEN TDD methodology

### Issue 2: Missing Test Functions in Test File

**Problem:** Runbook references test functions that don't exist in `tests/test_statusline_display.py`

**Missing Functions:**
- `test_extract_model_tier` (Cycle 1.1, line 26)
- `test_format_model` (Cycle 1.2, line 110)
- `test_format_model_thinking` (Cycle 1.3, line 201)
- `test_format_directory` (Cycle 1.4, line 275)
- `test_format_git_status` (Cycle 1.5, line 342)
- `test_format_cost` (Cycle 1.6, line 417)
- `test_format_mode` (Cycle 1.7, line 484)

**Current Test File Contains:**
- `test_colored_text`
- `test_token_bar`
- `test_vertical_bar`
- `test_format_tokens`
- `test_format_plan_limits`

**Impact:** Runbook execution will fail immediately at first "Verify RED" step with "test not found" error. This is a complete blocker.

**Recommendation:** Test creation should be part of RED phase instructions, or tests should exist before runbook generation.

### Issue 3: Missing Outline Review Report

**Problem:** No outline review found at `plans/statusline-parity/reports/runbook-outline-review.md`

**Impact:** Outline should be reviewed before full runbook generation for early feedback on structure and requirements coverage.

**Recommendation:** Review outline before expanding to full runbook.

## Correct Pattern Examples

### Cycle 1.1 Should Be:

**GREEN Phase:**

**Implementation:** Add `_extract_model_tier()` helper to StatuslineFormatter

**Behavior:**
- Method accepts display_name string parameter
- Returns tier string ("opus", "sonnet", "haiku") for known models
- Returns None for unknown models
- Case-insensitive matching

**Hint:** Use `str.lower()` for case-insensitive matching. Check for tier keywords in display name.

**Changes:**
- File: src/claudeutils/statusline/display.py
  Action: Add method after `RESET` constant definition

**Verify GREEN:** `pytest tests/test_statusline_display.py::test_extract_model_tier -v`

### Cycle 1.4 Should Be:

**GREEN Phase:**

**Implementation:** Add `format_directory()` method

**Behavior:**
- Accept directory name as string
- Return formatted string with 📁 emoji prefix
- Use CYAN color for directory name
- Must pass test assertions from RED phase

**Hint:** Use existing `colored()` method for color formatting. Emoji concatenation with f-string.

**Changes:**
- File: src/claudeutils/statusline/display.py
  Action: Add method after `format_model()`

**Verify GREEN:** `pytest tests/test_statusline_display.py::test_format_directory -v`

## Recommendations

### 1. Remove All Implementation Code from GREEN Phases

Replace prescriptive code blocks with:
- Behavioral descriptions
- Expected outcomes
- Implementation hints for approach
- File location and insertion point

**Do NOT provide:**
- Complete function implementations
- Exact logic and control flow
- Full code that can be copied verbatim

### 2. Create Test Functions Before Runbook Execution

Either:
- Add test creation to RED phase instructions
- Create test file with function stubs before runbook generation
- Document test creation as prerequisite step

Current runbook assumes tests exist but they don't.

### 3. Verify RED/GREEN Sequencing

For each cycle, ensure:
- RED phase test will actually fail (not pass with stub)
- GREEN phase describes minimal implementation (not complete feature)
- Stop conditions are clear and enforced

### 4. Review Outline Before Full Expansion

Follow recommended workflow:
1. Generate runbook outline
2. Review outline (outline-review-agent)
3. Expand outline to full runbook phase-by-phase
4. Review each phase before next expansion

Current runbook appears to be monolithic generation without outline checkpoint.

## Compliance Analysis

**TDD Principle:** Tests drive implementation
- Status: VIOLATED in all 7 cycles
- Evidence: Complete implementation code in every GREEN phase

**RED/GREEN Sequencing:** Tests fail before implementation
- Status: CANNOT VERIFY (test functions don't exist)
- Evidence: Referenced test functions not found in test file

**Minimal Implementation:** Smallest code to pass test
- Status: VIOLATED (all implementations are complete)
- Evidence: Full logic provided, no incremental discovery

**Behavioral Guidance:** Describe behavior, not code
- Status: VIOLATED
- Evidence: Code blocks prescribe exact implementation

## Next Steps

1. **Block execution** — Do NOT run this runbook until fixes applied
2. **Create test functions** — Add missing test functions to test file
3. **Rewrite GREEN phases** — Remove all implementation code, provide behavioral descriptions
4. **Review outline** — If outline exists, review it for requirements coverage
5. **Re-review** — After fixes, re-run review to verify compliance

---

**Review Date:** 2026-02-05
**Reviewer:** tdd-plan-reviewer agent
**Runbook:** plans/statusline-parity/runbook-phase-1.md
**Status:** BLOCKED — Critical violations prevent execution
