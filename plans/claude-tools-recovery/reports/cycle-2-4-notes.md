# Cycle 2.4: Test account api writes provider selection

**Timestamp:** 2026-01-31

## Execution Summary

- **Status:** GREEN_VERIFIED
- **Test command:** `pytest tests/test_cli_account.py::test_account_api -v`
- **RED result:** FAIL as expected (claude-env file not created with credentials)
- **GREEN result:** PASS (implementation generates provider-specific claude-env)
- **Regression check:** 4/4 passed (no regressions)
- **Refactoring:** Lint and formatting applied, type hints added for mypy satisfaction
- **Files modified:**
  - `tests/test_cli_account.py` - Strengthened test to verify claude-env content
  - `src/claudeutils/account/cli.py` - Implemented provider factory and claude-env generation
- **Stop condition:** none
- **Decision made:** Used factory pattern with provider_map to route to correct provider class based on --provider argument

## Phase Results

### RED Phase
Test was strengthened to verify behavioral requirements:
1. Mock keychain to return test credentials for OpenRouter provider
2. Run account api with --provider=openrouter flag
3. Verify claude-env file exists
4. Verify claude-env contains OPENROUTER_API_KEY with test credentials

Test failed with expected error: claude-env file not created.

### GREEN Phase
Implementation in `src/claudeutils/account/cli.py::api()`:
1. Created KeychainAdapter inline (consistent with plan() function)
2. Built provider_map dictionary mapping provider names to classes
3. Retrieved provider class from map (default to AnthropicProvider)
4. Instantiated provider with keystore
5. Called provider.claude_env_vars() to get credentials
6. Formatted and wrote claude-env file alongside account-mode and account-provider

Test now passes. Test verifies:
- account-mode file contains "api"
- account-provider file contains provider name
- claude-env file exists and contains provider-specific credentials

### Regression Check
All 4 tests in test_cli_account.py pass:
- test_account_status
- test_account_plan
- test_account_api (strengthened)
- test_account_status_with_issues

No regressions introduced.

### Refactoring
- Ran `just lint` - Fixed docstring formatting (summary line too long)
- Added import: `from typing import cast`
- Added cast wrapper for provider_class to satisfy mypy type checking
- Ran `just precommit` - All checks pass

## Implementation Notes

The api() command now mirrors the plan() command in structure:
- Both use inline KeychainAdapter pattern
- Both create provider instance from factory
- Both write account configuration files including claude-env

The --provider argument properly routes to the correct provider class:
- "anthropic" → AnthropicProvider (generates ANTHROPIC_API_KEY)
- "openrouter" → OpenRouterProvider (generates OPENROUTER_API_KEY)
- Unknown/missing → Defaults to AnthropicProvider

This satisfies the cycle requirement: "account api command writes selected provider and generates credentials"
