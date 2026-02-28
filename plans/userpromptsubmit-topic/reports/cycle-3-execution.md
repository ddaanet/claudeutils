# Cycle 3.0: Multi-command Warning (FR-3)

**Timestamp:** 2026-02-28

## Status: GREEN_VERIFIED

## Test Command
```bash
pytest tests/test_userpromptsubmit_shortcuts.py::TestTier1Commands::test_multi_command_first_wins tests/test_userpromptsubmit_shortcuts.py::TestTier1Commands::test_multi_command_reverse_order tests/test_userpromptsubmit_shortcuts.py::TestTier1Commands::test_single_command_no_warning -v
```

## Phase Results

### RED Phase
- **Test**: test_multi_command_first_wins
  - **Expected**: KeyError on systemMessage (no warning implemented yet)
  - **Actual**: FAIL - KeyError: 'systemMessage' ✓
- **Other tests**: test_multi_command_reverse_order and test_single_command_no_warning
  - **Expected**: PASS (test existing behavior)
  - **Actual**: PASS ✓

### GREEN Phase
- **Implementation**: Modified `main()` to collect all command matches, emit only first expansion, add warning to systemMessage when multiple commands found
- **All three new tests**: PASS ✓
- **Full regression suite**: 1324/1325 passed, 1 xfail (known baseline) ✓

## Regression Check
- Pre-existing xfail: test_markdown_fixtures.py::test_full_pipeline_remark[02-inline-backticks]
- All other tests: PASS
- Result: 0 NEW failures

## Refactoring
- Linting: PASS (no warnings)
- Precommit: PASS (no warnings)
- Code quality: No architectural warnings found

## Files Modified
- `agent-core/hooks/userpromptsubmit-shortcuts.py` — Tier 1 command scanning logic
- `tests/test_userpromptsubmit_shortcuts.py` — Added 3 new test cases

## Stop Condition
None

## Decision Made
The implementation collects all command matches on separate lines and:
1. Emits only the first match's expansion to additionalContext (first-wins behavior)
2. Adds warning to systemMessage when >1 command found (new feature)
3. For single-line exact matches, systemMessage contains the expansion
4. For multi-line prompts, warning goes into systemMessage separately (not mixed into status bar)

This satisfies FR-3 requirements and maintains backward compatibility with existing tests.
