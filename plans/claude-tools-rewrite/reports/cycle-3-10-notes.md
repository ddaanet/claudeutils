# Cycle 3.10: Account CLI - plan command

## Summary
Implemented `claudeutils account plan` command to switch to plan mode and write configuration files.

## RED Phase
- Test: CLI command `claudeutils account plan` switches mode and writes files
- Expected failure: "No such command 'plan'"
- Actual failure: Click error message "Error: No such command 'plan'."
- Status: VERIFIED

## GREEN Phase
- Implementation: Added `plan` command to account group
- Changes:
  - Added `@account.command()` decorator with plan function
  - Function writes account-mode file to ~/.claude/account-mode with "plan" content
  - Function writes claude-env file to ~/.claude/claude-env (empty)
  - Returns success message
- Test update: Added tmp_path fixture and mock Path.home() to avoid filesystem access
- Status: PASSED

## Regression Check
- Full test suite: 310/310 passed
- Status: NO REGRESSIONS

## Refactoring
- Lint: Fixed PLC0415 (moved Path import to top-level)
- Precommit: PASSED (no quality warnings)
- Status: NONE NEEDED

## Files Modified
- src/claudeutils/account/cli.py (added plan command, fixed imports)
- tests/test_cli_account.py (added test_account_plan with tmp_path and mock)

## Decision Made
Minimal implementation: plan command writes two files to ~/.claude/ directory (account-mode with "plan" content, claude-env empty). Uses tmp_path fixture with mock to avoid filesystem access in tests.

## Status
COMPLETE - GREEN verified, no regressions, precommit passed
