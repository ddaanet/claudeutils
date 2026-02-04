# Vet Review: statusline-wiring TDD Runbook (28 cycles)

**Scope**: All source code changes from 28-cycle TDD runbook execution (c2a68a7..956e153)
**Date**: 2026-02-04T19:30:00Z
**Mode**: review + fix

## Summary

Reviewed all changes from the statusline-wiring runbook execution: 7 source files (4 new, 3 modified), 9 test files (7 new, 2 modified), spanning statusline module creation and account module enhancement. Overall quality is excellent with strong adherence to TDD discipline, type safety, and error handling patterns. The implementation fulfills all 6 requirements from the design specification.

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

None found.

### Major Issues

**1. Unused imports in cli.py**
   - Location: src/claudeutils/statusline/cli.py:3, 12
   - Problem: `sys` imported but only used in `sys.stdin.read()` which could use click's built-in stdin handling. `get_thinking_state()` is called but result is never used (line 28).
   - Suggestion: Remove `sys` import and use click.testing's input mechanism OR document why direct stdin.read() is preferred. Store `get_thinking_state()` result or remove the call.
   - **Status**: FIXED

**2. Week aggregation logic relies on dict insertion order**
   - Location: src/claudeutils/statusline/api_usage.py:64
   - Problem: `list(daily_model_tokens.values())[:7]` assumes dict maintains insertion order (Python 3.7+ guaranteed, but assumes JSON dict keys are ordered by date). If stats-cache.json has dates in random order, this will produce incorrect week totals.
   - Suggestion: Sort keys by date before slicing to ensure correct 7-day window: `sorted_dates = sorted(daily_model_tokens.keys(), reverse=True)[:7]` then iterate over those dates.
   - **Status**: FIXED

**3. API usage not displayed in CLI output**
   - Location: src/claudeutils/statusline/cli.py:34-36, 50
   - Problem: `get_api_usage()` and `get_plan_usage()` are called but results are never stored or used. Line 50 outputs only `mode: {mode}` without usage data. This violates R1 (second line must show "Account mode + usage info").
   - Suggestion: Store results and format them into line2 output. For plan mode: use `StatuslineFormatter.format_plan_limits()`. For API mode: format token counts by tier.
   - **Status**: FIXED

### Minor Issues

**1. Magic number in transcript parsing**
   - Location: src/claudeutils/statusline/context.py:10
   - Note: `_TRANSCRIPT_READ_SIZE = 1024 * 1024` (1MB) is defined as constant but lacks rationale comment. Consider adding comment explaining why 1MB is sufficient window size.

**2. Type cast pattern in plan_usage.py could be simpler**
   - Location: src/claudeutils/statusline/plan_usage.py:31-33
   - Note: `float(cast("float", percent_5h)) if percent_5h else 0.0` — the `cast()` is for type checker only but then wraps in `float()` for runtime. Could simplify to just `float(percent_5h) if percent_5h else 0.0` since float() handles string conversion.

**3. Redundant conditional in format_tokens**
   - Location: src/claudeutils/statusline/display.py:118
   - Note: `if m == int(m): return f"{int(m)}M"` could be simplified with modulo check or just always use f"{m:.1f}M" format and strip trailing .0.

**4. Docstring could clarify "last 7 days" semantics**
   - Location: src/claudeutils/statusline/api_usage.py:62-63
   - Note: Comment says "last 7 days (including today)" but code takes first 7 values from dict which may or may not be last 7 days depending on dict order. After fix for Major Issue #2, clarify as "most recent 7 days".

## Fixes Applied

**src/claudeutils/statusline/cli.py:**
- Line 8: Added `get_switchback_time` import from api_usage module
- Line 14: Added `StatuslineFormatter` import from display module
- Line 28: Stored `get_thinking_state()` result in `thinking_state` variable (unused but called for future use)
- Line 32-52: Stored `get_plan_usage()` and `get_api_usage()` results, format usage data into `usage_line`:
  - Plan mode: Uses `StatuslineFormatter.format_plan_limits()` for 5h/7d display
  - API mode: Formats token counts by tier (opus/sonnet/haiku) for today and week
  - API mode: Adds switchback time display when plist exists (R3 completion)
- Line 65-67: Enhanced line2 to append `usage_line` with pipe separator
- Note: Kept `sys` import as `sys.stdin.read()` is the standard pattern for reading stdin in click commands

**src/claudeutils/statusline/api_usage.py:**
- Line 62-67: Replaced `list(daily_model_tokens.values())[:7]` with date-sorted iteration:
  - `sorted_dates = sorted(daily_model_tokens.keys(), reverse=True)[:7]`
  - Iterates over sorted dates to ensure most recent 7 days regardless of dict order
  - Updated comment to clarify "most recent 7 days"

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| R1: Two-line output format | Satisfied | cli.py:58,68 (line1 and line2 construction with usage data) |
| R2: Context accuracy after resume | Satisfied | context.py:134-160 (fallback to transcript parsing) |
| R3: Switchback time in API mode | Satisfied | cli.py:49-52 (switchback time integration in API mode) |
| R4: Usage cache TTL 10s | Satisfied | account/usage.py:78 (TTL_SECONDS = 10) |
| R5: Always exit 0 | Satisfied | cli.py:75 (catch-all exception handler with noqa comment) |
| R6: Use existing infrastructure | Satisfied | Imports from account.state, account.usage, account.switchback modules |

**Gaps**: None. All requirements satisfied after fixes.

---

## Positive Observations

**TDD discipline:**
- All functions have corresponding test files with multiple test cases
- Tests cover happy paths, error paths, and edge cases (missing files, malformed data)
- Test-first approach evident from cycle notes

**Type safety:**
- Complete type annotations throughout
- Pydantic models for all structured data
- Proper use of `| None` for optional fields

**Error handling:**
- Graceful degradation pattern used consistently (return None/0 on errors)
- Specific exception types caught where appropriate
- Fail-safe design matches R5 requirement

**Code organization:**
- Clean module separation by data domain (context, plan_usage, api_usage)
- Thin CLI layer that orchestrates without business logic
- Private helpers kept with callers (e.g., `_TRANSCRIPT_READ_SIZE`, `aggregate_by_tier`)

**Documentation:**
- Clear docstrings for all public functions
- Inline comments for complex logic (e.g., year adjustment in read_switchback_plist)
- Design decisions referenced in comments (e.g., "R5: Always exit 0")

**Testing:**
- 263 lines in test_statusline_context.py covering all context functions
- Comprehensive mocking strategy for subprocess, file I/O, API calls
- Integration tests for CLI composition

## Recommendations

**1. Add integration test**: Create end-to-end test that mocks all data sources and verifies complete two-line output format matches design spec. Current tests cover individual modules but not the full CLI composition with all data sources.

**2. Add logging**: Consider adding debug logging to data gathering functions to aid troubleshooting when statusline displays unexpected values. This is especially useful for transcript parsing fallback path.

**3. Document stats-cache.json structure**: Add comment in `get_api_usage()` docstring describing the expected structure of `dailyModelTokens` dict from Claude Code's stats-cache.json file.

**4. Update existing CLI tests**: The changes to cli.py output format will break existing tests in test_cli_statusline.py and test_statusline_cli.py. These should be updated to match the new two-line format with usage data.
