# Design: Claude Tools Rewrite Recovery

## Problem

The claude-tools-rewrite TDD runbook executed 37 cycles. All tests pass, but features don't work. Implementations are stubs: hardcoded state, empty credential strings, "OK" output instead of formatted statusline.

**Current state** (branch: tools-rewrite, commit b40e34e):
- All classes and methods exist (correct structure)
- All tests pass (but tests only verify structure)
- `just dev` passes (tests, mypy, ruff)
- CLI commands return exit code 0 with hardcoded/empty output
- No component is wired to real I/O (files, keychain, APIs)

**Prerequisite:** Skill improvements from `plans/skill-improvements/design.md` must be applied first. This recovery dogfoods the improved plan-tdd.

Full analysis: `plans/claude-tools-rewrite/runbook-analysis.md`
Original design: `plans/claude-tools-rewrite/design.md`

## Scope

**In scope:**
- Delete vacuous tests that verify only structure
- Rewrite weak tests with behavioral assertions
- Wire stub implementations to real I/O
- Add missing integration cycles (the 8 gap from original runbook)
- End-to-end tests with mocked filesystem and keychain

**Out of scope:**
- Changing module structure (already correct)
- Changing Pydantic models (already correct)
- Changing CLI command names or options (already correct)
- statusline display modules (display.py, context.py, plan_usage.py, api_usage.py) — these have more complex I/O and should be a follow-up

## Architecture

No architectural changes. The existing module layout from the original design is correct.
All changes are internal: replacing stubs with real implementations and weak tests
with behavioral assertions.

### Key Integration Points

**1. Account state reads filesystem**
- `~/.claude/account-mode` → AccountState.mode
- `~/.claude/account-provider` → AccountState.provider
- Keychain query → AccountState.oauth_in_keychain
- `~/.claude/.env` existence → AccountState.api_in_claude_env

**2. Providers read keychain/config**
- AnthropicProvider: keychain entry `anthropic-api-key` → API key
- OpenRouterProvider: keychain entry `openrouter-api-key` → API key + base URL
- LiteLLMProvider: localhost URL (no credentials needed)

**3. CLI commands use real state**
- `account status`: reads filesystem + keychain → displays real state
- `account plan/api`: switches mode, writes files, generates claude-env
- `model list/set/reset`: reads/writes model override file
- `statusline`: reads JSON stdin → formats with StatuslineFormatter → outputs ANSI

## Phases

### Phase R0: Clean up vacuous tests

Delete tests that bring no value — they pass with stubs and would pass with real
implementations too. No information content.

**Candidates:**
- Tests that only check `exit_code == 0` with no output assertions
- Tests that only check `hasattr` or `isinstance`
- Tests that only verify a class can be instantiated with no behavior check

**Do not delete:**
- Tests with any content assertion (even weak ones — those get strengthened in R1/R2)
- Tests that verify error cases (even if currently stubbed)

### Phase R1: Strengthen provider and keychain tests

**Target:** Cycles 1.9-1.13 equivalents

For each provider (Anthropic, OpenRouter, LiteLLM):
- Mock `subprocess.run` for keychain `security find-generic-password` calls
- Assert `claude_env_vars()` returns non-empty values from mocked keychain
- Assert correct keychain service/account parameters in mock calls
- Test missing keychain entry → appropriate error/fallback

For Keychain wrapper:
- Mock `subprocess.run` for `security` commands
- Assert correct command construction (find-generic-password, add-generic-password)
- Test keychain not found → KeychainError
- Test entry not found → None or specific error

### Phase R2: Strengthen CLI tests

**Target:** Cycles 3.9-3.15 equivalents

**account status:**
- Create `tmp_path / .claude/` with mode and provider files
- Mock `Path.home()` → tmp_path
- Mock keychain queries
- Assert output contains actual mode, provider, OAuth status from fixtures
- Assert `validate_consistency()` output appears when issues exist

**account plan / account api:**
- Mock filesystem and keychain
- Assert mode file written with correct value
- Assert claude-env file generated with provider credentials
- Assert output confirms switch

**model list:**
- Mock LiteLLM config file
- Assert output contains model names from config
- Test tier filtering (if applicable)

**model set / model reset:**
- Use tmp_path for override file
- Assert file written/deleted
- Assert output confirms action

**statusline:**
- Pipe JSON input via CliRunner
- Assert output is ANSI-formatted (not just "OK")
- Assert StatuslineFormatter is used (mock or check output structure)

### Phase R3: Wire implementations

Replace stubs with real I/O code. Each cycle: the strengthened test from R1/R2
already fails (RED), implement real behavior (GREEN).

**Account state factory:**
- Read `~/.claude/account-mode`, `~/.claude/account-provider` files
- Query keychain for OAuth token presence
- Check `~/.claude/.env` existence
- Return populated AccountState (not hardcoded)

**Provider credential retrieval:**
- AnthropicProvider.claude_env_vars() → call Keychain.find() → return real key
- OpenRouterProvider.claude_env_vars() → call Keychain.find() → return key + base URL
- LiteLLMProvider.claude_env_vars() → return localhost URL (no keychain needed)

**CLI wiring:**
- account status: call state factory, display real state
- account plan/api: call provider, write files, generate claude-env
- statusline: read stdin JSON, pass to StatuslineFormatter, output result

### Phase R4: Error handling and integration tests

**Error handling:**
- Keychain not installed or not accessible → clear error message
- Config files missing → sensible defaults or error
- Invalid JSON on statusline stdin → error message (not crash)
- Provider keychain entry missing → error with setup instructions

**Integration tests:**
- Full `account status` flow with mocked filesystem + keychain
- Full `account plan` → `account api` → `account plan` round-trip
- Full `model set` → `model list` → `model reset` flow
- Statusline with realistic JSON input

## Design Decisions

**1. Approach: Strengthen tests then wire (Option 2 from analysis)**
- Structure is correct, only internals need work
- Strengthened tests create RED phase naturally (stubs fail behavioral assertions)
- Dogfoods improved plan-tdd skill
- Option 1 (new cycles only) doesn't fix existing weak tests
- Option 3 (manual) bypasses TDD, loses coverage guarantees

**2. Phase R0 deletes before strengthening**
- Vacuous tests add noise and false confidence
- Removing them first clarifies what actually needs behavioral assertions
- Prevents confusion during R1/R2 about which tests to edit vs delete

**3. Statusline display modules deferred**
- display.py, context.py, plan_usage.py, api_usage.py have complex formatting
- These need their own design for test strategy (snapshot testing? golden files?)
- Current recovery focuses on I/O wiring and state management
- StatuslineFormatter basic integration tested, not internal formatting

**4. Mock strategy: patch at usage location**
- `unittest.mock.patch("claudeutils.account.state.subprocess.run")` not
  `patch("subprocess.run")`
- `patch("claudeutils.account.state.Path.home")` not `patch("pathlib.Path.home")`
- Consistent with existing project mock patterns
- More precise, less likely to affect unrelated code

## Dependencies

**Before:**
- Skill improvements applied (`plans/skill-improvements/design.md`)
- Improved plan-tdd generates behavioral RED tests
- Improved review-tdd-plan catches weak assertions

**After:**
- CLI commands functional with real I/O
- Statusline display modules (follow-up design)
- Shell script deprecation (replace shell callers with Python CLI)

## Execution

Route: `/plan-tdd` → review → prepare-runbook.py → `/orchestrate` → `/vet`

This is feature development with test-first methodology. The improved plan-tdd
skill should generate behavioral RED tests that force real implementations —
validating both the recovery and the skill improvements.
