---
name: claude-tools-recovery
type: tdd
model: haiku
---

# Claude Tools Recovery TDD Runbook

**Context**: Recover claude-tools-rewrite implementation by replacing stubs with real I/O and strengthening tests from structural to behavioral assertions.

**Design**: plans/claude-tools-recovery/design.md

**Status**: Draft

**Created**: 2026-01-31

## Weak Orchestrator Metadata

**Total Steps**: 13
**Execution Model**: All cycles: Haiku (TDD execution)
**Step Dependencies**: Sequential within phases
**Error Escalation**: Haiku → User on stop conditions/regression
**Report Locations**: plans/claude-tools-recovery/reports/
**Success Criteria**: All cycles GREEN, no regressions, features functional
**Prerequisites**: Skill improvements from plans/skill-improvements/design.md applied

## Common Context

**Key Design Decisions:**

1. **Approach: Strengthen tests then wire (Option 2)**
   - Structure is correct, only internals need work
   - Strengthened tests create RED phase naturally (stubs fail behavioral assertions)
   - Dogfoods improved plan-tdd skill

2. **Phase R0 deletes before strengthening**
   - Vacuous tests add noise and false confidence
   - Removing them first clarifies what actually needs behavioral assertions

3. **Statusline display modules deferred**
   - display.py, context.py, plan_usage.py, api_usage.py have complex formatting
   - Current recovery focuses on I/O wiring and state management

4. **Mock strategy: patch at usage location**
   - `patch("claudeutils.account.state.subprocess.run")` not `patch("subprocess.run")`
   - `patch("claudeutils.account.cli.Path.home")` not `patch("pathlib.Path.home")`

**TDD Protocol:**
Strict RED-GREEN-REFACTOR: 1) RED: Write failing test, 2) Verify RED, 3) GREEN: Minimal implementation, 4) Verify GREEN, 5) Verify Regression, 6) REFACTOR (optional)

**Project Paths:**
- Source: `src/claudeutils/account/` (state.py, providers.py, keychain.py, cli.py)
- Tests: `tests/test_account_*.py`, `tests/test_cli_account.py`
- Account config: `~/.claude/account-mode`, `~/.claude/account-provider`
- Keychain service: `com.anthropic.claude`

**Conventions:**
- Use Read/Write/Edit/Grep tools (not Bash for file ops)
- Report errors explicitly (never suppress)
- Write notes to plans/claude-tools-recovery/reports/cycle-{X}-{Y}-notes.md
- Mock patching: patch at usage location (see design decisions #4)

**Stop Conditions (all cycles):**

STOP IMMEDIATELY if:
- RED phase test passes (expected failure)
- RED phase failure message doesn't match expected
- GREEN phase tests don't pass after implementation
- Any phase existing tests break (regression)

Actions when stopped:
1. Document in reports/cycle-{X}-{Y}-notes.md
2. Test passes unexpectedly → Investigate if feature exists
3. Regression → STOP, report broken tests
4. Scope unclear → STOP, document ambiguity

**Dependencies:**
Sequential within each phase. All R0 cycles complete before R1. All R1 cycles complete before R2, etc.

**Phase Numbering Note:**
Design document mentions phases R0-R4, but this runbook uses R0-R3. The design's "Phase R3: Wire implementations" is omitted because strengthened tests in R1/R2 already drive implementations during their GREEN phases. The design's R3 was a validation step; this runbook integrates implementation directly into test strengthening cycles. The design's "Phase R4: Error handling" becomes Phase R3 here.

---

## Phase R0: Clean up vacuous tests

Delete tests that verify only structure with no behavioral assertions.

## Cycle 0.1: Delete vacuous module import test

**Objective**: Remove test that only verifies module importability
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** tests/test_account_structure.py::test_account_module_importable only checks `assert claudeutils.account is not None`

**Expected failure:**
```
No failure - this is a deletion cycle
```

**Why it fails:** N/A - deletion cycle

**Verify RED:** Read tests/test_account_structure.py
- Confirm test provides no behavioral value (only structure check)

---

**GREEN Phase:**

**Implementation:** Delete tests/test_account_structure.py entirely

**Changes:**
- File: tests/test_account_structure.py
  Action: Delete file (only contains vacuous import test)

**Verify GREEN:**
```bash
pytest tests/test_account_state.py tests/test_account_providers.py -v
```
- All remaining account tests still pass

**Verify no regression:**
```bash
pytest
```
- All tests pass (one file removed, no functionality changed)

---

**Expected Outcome**: Vacuous structural test removed, remaining tests pass
**Error Conditions**: If other tests break → investigation needed
**Validation**: File deleted, test suite passes
**Success Criteria**: tests/test_account_structure.py removed
**Report Path**: plans/claude-tools-recovery/reports/cycle-0-1-notes.md

---

## Phase R1: Strengthen provider and keychain tests

Replace weak structural assertions with behavioral tests using mocks.

## Cycle 1.1: Test AnthropicProvider keystore interaction

**Objective**: Verify AnthropicProvider calls keystore method (not just checks key presence)
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** tests/test_account_providers.py::test_anthropic_provider_env_vars should verify mock keystore method called

**Expected failure:**
```
AssertionError: Expected 'get_anthropic_api_key' to be called once. Called 0 times.
```

**Why it fails:** Test doesn't verify keystore method invocation

**Verify RED:**
```bash
pytest tests/test_account_providers.py::test_anthropic_provider_env_vars -v
```
- Add `mock_keystore.get_anthropic_api_key.assert_called_once()` to test
- Test should FAIL if assertion missing or mock not called

---

**GREEN Phase:**

**Implementation:** Add mock call verification to test (implementation already calls it)

**Changes:**
- File: tests/test_account_providers.py
  Action: Add `mock_keystore.get_anthropic_api_key.assert_called_once()` after env_vars call

**Verify GREEN:**
```bash
pytest tests/test_account_providers.py::test_anthropic_provider_env_vars -v
```
- Test passes with mock call verification

**Verify no regression:**
```bash
pytest tests/test_account_providers.py -v
```
- All provider tests pass

---

**Expected Outcome**: Test verifies keystore method called, not just key presence
**Error Conditions**: If mock not called → implementation needs fixing
**Validation**: Mock call assertion added and passes
**Success Criteria**: Test verifies behavioral interaction with keystore
**Report Path**: plans/claude-tools-recovery/reports/cycle-1-1-notes.md

---

## Cycle 1.2: Strengthen OpenRouterProvider with keychain retrieval

**Objective**: Add keystore to OpenRouterProvider and test credential retrieval
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** tests/test_account_providers.py::test_openrouter_provider_env_vars should verify non-empty credentials

**Expected failure:**
```
AssertionError: assert env_vars["OPENROUTER_API_KEY"] != ""
(current returns empty string)
```

**Why it fails:** OpenRouterProvider.claude_env_vars() returns hardcoded empty strings

**Verify RED:**
```bash
pytest tests/test_account_providers.py::test_openrouter_provider_env_vars -v
```
- Edit test to add `assert env_vars["OPENROUTER_API_KEY"] != ""`
- Test should FAIL (stub returns "")

---

**GREEN Phase:**

**Implementation:** Add keystore to OpenRouterProvider and retrieve credentials

**Changes:**
- File: src/claudeutils/account/providers.py
  Action: Add `__init__(self, keystore: KeyStore)`, add `get_openrouter_api_key()` to KeyStore protocol, call it in `claude_env_vars()`
- File: tests/test_account_providers.py
  Action: Create mock keystore with `get_openrouter_api_key()` returning "test-openrouter-key", verify values

**Verify GREEN:**
```bash
pytest tests/test_account_providers.py::test_openrouter_provider_env_vars -v
```
- Test passes with real keychain values from mock

**Verify no regression:**
```bash
pytest tests/test_account_providers.py -v
```
- All provider tests pass

---

**Expected Outcome**: OpenRouterProvider test uses mock keychain and verifies retrieval
**Error Conditions**: Keychain mock setup incorrect → adjust mock pattern
**Validation**: Test has behavioral assertion for credential retrieval
**Success Criteria**: OpenRouterProvider retrieves credentials from keystore
**Report Path**: plans/claude-tools-recovery/reports/cycle-1-2-notes.md

---

## Cycle 1.3: Strengthen LiteLLMProvider with localhost URL

**Objective**: Verify LiteLLM provider returns specific localhost URL (not empty)
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** tests/test_account_providers.py::test_litellm_provider_env_vars should verify specific URL value

**Expected failure:**
```
AssertionError: assert env_vars["ANTHROPIC_BASE_URL"] == "http://localhost:4000"
(current returns empty string)
```

**Why it fails:** LiteLLMProvider.claude_env_vars() returns empty string for base URL

**Verify RED:**
```bash
pytest tests/test_account_providers.py::test_litellm_provider_env_vars -v
```
- Edit test to assert `env_vars["ANTHROPIC_BASE_URL"] == "http://localhost:4000"`
- Test should FAIL (stub returns "")

---

**GREEN Phase:**

**Implementation:** Update LiteLLMProvider to return localhost URL constant

**Changes:**
- File: src/claudeutils/account/providers.py
  Action: Replace empty ANTHROPIC_BASE_URL with "http://localhost:4000", keep LITELLM_API_KEY as "none" (doesn't need real key)
- File: tests/test_account_providers.py
  Action: Assert ANTHROPIC_BASE_URL == "http://localhost:4000"

**Verify GREEN:**
```bash
pytest tests/test_account_providers.py::test_litellm_provider_env_vars -v
```
- Test passes with correct URL

**Verify no regression:**
```bash
pytest tests/test_account_providers.py -v
```
- All provider tests pass

---

**Expected Outcome**: LiteLLM provider test verifies correct base URL value
**Error Conditions**: URL mismatch → verify localhost port convention
**Validation**: Test asserts specific URL, not just key presence
**Success Criteria**: LiteLLM returns http://localhost:4000 base URL
**Report Path**: plans/claude-tools-recovery/reports/cycle-1-3-notes.md

---

## Cycle 1.4: Add Keychain wrapper with subprocess mock

**Objective**: Create Keychain class with find() method tested via subprocess mock
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** Create tests/test_account_keychain.py with test for Keychain.find() mocking subprocess.run

**Expected failure:**
```
ModuleNotFoundError: No module named 'test_account_keychain'
or test fails because Keychain.find() doesn't exist
```

**Why it fails:** Keychain class or find() method doesn't exist yet

**Verify RED:**
```bash
pytest tests/test_account_keychain.py::test_keychain_find_success -v
```
- Create test file with mock for `subprocess.run` at `claudeutils.account.keychain.subprocess.run`
- Mock returns stdout="test-password\n", returncode=0
- Assert `Keychain().find("service", "account") == "test-password"`
- Test should FAIL (implementation missing)

---

**GREEN Phase:**

**Implementation:** Create Keychain class with find() method calling subprocess

**Changes:**
- File: src/claudeutils/account/keychain.py
  Action: Create Keychain class with `find(service, account)` using `subprocess.run(["security", "find-generic-password", "-s", service, "-a", account, "-w"], capture_output=True, text=True)`, return stdout.strip()
- File: tests/test_account_keychain.py
  Action: Create test with subprocess mock, verify command and return value

**Verify GREEN:**
```bash
pytest tests/test_account_keychain.py::test_keychain_find_success -v
```
- Test passes with mocked subprocess

**Verify no regression:**
```bash
pytest
```
- All existing tests pass

---

**Expected Outcome**: Keychain test mocks subprocess and verifies command structure
**Error Conditions**: subprocess mock not called → verify patch location (usage site)
**Validation**: Mock verifies security find-generic-password command
**Success Criteria**: Keychain.find() constructs correct subprocess command
**Report Path**: plans/claude-tools-recovery/reports/cycle-1-4-notes.md

---

## Cycle 1.5: Test Keychain entry not found

**Objective**: Test Keychain.find() returns None when entry doesn't exist
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** tests/test_account_keychain.py should test find() returns None on subprocess failure

**Expected failure:**
```
AssertionError: assert result is None
(may return empty string or raise exception)
```

**Why it fails:** Keychain.find() doesn't handle subprocess returncode != 0

**Verify RED:**
```bash
pytest tests/test_account_keychain.py::test_keychain_find_not_found -v
```
- Create test with mock returncode=1, stdout=""
- Assert `Keychain().find("service", "account") is None`
- Test should FAIL if error handling missing

---

**GREEN Phase:**

**Implementation:** Update Keychain.find() to return None on subprocess failure

**Changes:**
- File: src/claudeutils/account/keychain.py
  Action: Check `result.returncode`, return `None` if != 0, else return `result.stdout.strip()`
- File: tests/test_account_keychain.py
  Action: Add test with mock returncode=1, assert find() returns None

**Verify GREEN:**
```bash
pytest tests/test_account_keychain.py::test_keychain_find_not_found -v
```
- Test passes with None return

**Verify no regression:**
```bash
pytest tests/test_account_keychain.py -v
```
- Both find tests pass (success and not found)

---

**Expected Outcome**: Keychain handles missing entries gracefully with None return
**Error Conditions**: Exception raised instead → add try/except
**Validation**: Test verifies None return on subprocess failure
**Success Criteria**: Keychain.find() returns None for missing entries
**Report Path**: plans/claude-tools-recovery/reports/cycle-1-5-notes.md

---

**Checkpoint**

1. Fix: Run `just dev`. Sonnet quiet-task fixes failures. Commit when green.
2. Vet: Review provider and keychain test quality, mock patterns. Commit fixes.
3. Functional review: Verify all provider implementations call keystore (not return stubs). Check Keychain calls subprocess. If any stubs remain, STOP and report.

---

## Phase R2: Strengthen CLI tests

Replace exit-code-only CLI tests with tests that verify actual output and filesystem state.

## Cycle 2.1: Strengthen account status with filesystem mocking

**Objective**: Test account status reads real filesystem and outputs actual values
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** tests/test_cli_account.py::test_account_status should verify output contains mode from file

**Expected failure:**
```
AssertionError: assert "Mode: api" in result.output
(current hardcoded implementation outputs "Mode: plan")
```

**Why it fails:** CLI hardcodes state instead of reading from files

**Verify RED:**
```bash
pytest tests/test_cli_account.py::test_account_status -v
```
- Edit test to use `tmp_path` fixture, create `.claude/account-mode` with content "api"
- Mock `pathlib.Path.home` at usage location `claudeutils.account.cli.Path.home` to return `tmp_path`
- Assert `"Mode: api" in result.output`
- Test should FAIL (CLI returns hardcoded "Mode: plan")

---

**GREEN Phase:**

**Implementation:** Create account state factory and use it in status command

**Changes:**
- File: src/claudeutils/account/state.py
  Action: Add `get_account_state()` function that reads `Path.home() / ".claude" / "account-mode"` and `"account-provider"` files, returns AccountState with file values (default "plan"/"anthropic" if missing)
- File: src/claudeutils/account/cli.py
  Action: Replace hardcoded AccountState in status() with `state = get_account_state()`
- File: tests/test_cli_account.py
  Action: Update test with tmp_path, file creation, Path.home mock, output assertion

**Verify GREEN:**
```bash
pytest tests/test_cli_account.py::test_account_status -v
```
- Test passes with output from real file reads

**Verify no regression:**
```bash
pytest tests/test_cli_account.py -v
```
- All CLI account tests pass

---

**Expected Outcome**: account status test creates fixtures and verifies output content
**Error Conditions**: Path.home() mock incorrect → verify patch at usage location
**Validation**: Test asserts specific mode value from fixture
**Success Criteria**: CLI reads real files, outputs actual state
**Report Path**: plans/claude-tools-recovery/reports/cycle-2-1-notes.md

---

## Cycle 2.2: Test account status displays validation issues

**Objective**: Verify account status outputs consistency validation results
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** tests/test_cli_account.py should test account status displays issues when state is inconsistent

**Expected failure:**
```
AssertionError: assert "Plan mode requires OAuth credentials" in result.output
```

**Why it fails:** get_account_state() may not check keychain, or CLI doesn't display validation issues

**Verify RED:**
```bash
pytest tests/test_cli_account.py::test_account_status_with_issues -v
```
- Create test with tmp_path, write mode="plan" to account-mode file
- Mock keychain query (via Keychain.find) to return None (no OAuth)
- Assert validation message in output
- Test should FAIL if CLI doesn't display issues

---

**GREEN Phase:**

**Implementation:** Update get_account_state() to query keychain and CLI to display validation

**Changes:**
- File: src/claudeutils/account/state.py
  Action: In get_account_state(), create Keychain instance, call find() to check OAuth presence, set oauth_in_keychain field
- File: src/claudeutils/account/cli.py
  Action: Ensure status() calls `state.validate_consistency()` and displays issues (already exists from current implementation)
- File: tests/test_cli_account.py
  Action: Create test with mode=plan fixture, mock Keychain.find to return None, assert issue message

**Verify GREEN:**
```bash
pytest tests/test_cli_account.py::test_account_status_with_issues -v
```
- Test passes with validation output

**Verify no regression:**
```bash
pytest tests/test_cli_account.py -v
```
- All account CLI tests pass

---

**Expected Outcome**: account status test verifies validation issues displayed
**Error Conditions**: Issue message not in output → check validate_consistency() call
**Validation**: Test creates inconsistent state, asserts error message
**Success Criteria**: CLI outputs consistency validation results
**Report Path**: plans/claude-tools-recovery/reports/cycle-2-2-notes.md

---

## Cycle 2.3: Test account plan generates claude-env with credentials

**Objective**: Verify account plan command generates claude-env file with provider credentials
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** tests/test_cli_account.py::test_account_plan should verify claude-env file contains provider credentials

**Expected failure:**
```
AssertionError: assert "ANTHROPIC_API_KEY" in claude_env_content
(current writes empty file)
```

**Why it fails:** CLI writes empty claude-env file, doesn't call provider

**Verify RED:**
```bash
pytest tests/test_cli_account.py::test_account_plan -v
```
- Edit test to read claude-env file content after command
- Assert file contains "ANTHROPIC_API_KEY=test-" (from mocked keystore)
- Mock keystore to return "test-anthropic-key"
- Test should FAIL (current writes empty file)

---

**GREEN Phase:**

**Implementation:** Update account plan command to generate claude-env with provider

**Changes:**
- File: src/claudeutils/account/cli.py
  Action: In plan(), create AnthropicProvider with Keychain, call claude_env_vars(), format as KEY=value lines, write to claude-env
- File: tests/test_cli_account.py
  Action: Mock Keychain.find at `claudeutils.account.state.Keychain.find`, assert claude-env contains credentials

**Verify GREEN:**
```bash
pytest tests/test_cli_account.py::test_account_plan -v
```
- Test passes with claude-env containing credentials

**Verify no regression:**
```bash
pytest tests/test_cli_account.py -v
```
- All CLI account tests pass

---

**Expected Outcome**: account plan test verifies claude-env file content
**Error Conditions**: Missing env vars → verify provider.claude_env_vars() call
**Validation**: Test reads file, asserts credential presence
**Success Criteria**: account plan generates claude-env with provider credentials
**Report Path**: plans/claude-tools-recovery/reports/cycle-2-3-notes.md

---

## Cycle 2.4: Test account api writes provider selection

**Objective**: Verify account api command writes selected provider and generates credentials
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** tests/test_cli_account.py::test_account_api already verifies provider file, strengthen to test claude-env content

**Expected failure:**
```
AssertionError: assert "OPENROUTER_API_KEY" in claude_env_content
(may write empty or wrong provider credentials)
```

**Why it fails:** CLI may not generate provider-specific claude-env

**Verify RED:**
```bash
pytest tests/test_cli_account.py::test_account_api -v
```
- Edit test to read claude-env file, assert OPENROUTER_API_KEY present
- Mock keystore get_openrouter_api_key to return "test-openrouter-key"
- Test should FAIL if wrong provider or empty file

---

**GREEN Phase:**

**Implementation:** Update account api to create provider-specific claude-env

**Changes:**
- File: src/claudeutils/account/cli.py
  Action: In api(), create provider based on --provider argument (factory function), generate claude-env with provider.claude_env_vars()
- File: tests/test_cli_account.py
  Action: Test with --provider=openrouter, mock keystore, assert OPENROUTER_API_KEY in claude-env

**Verify GREEN:**
```bash
pytest tests/test_cli_account.py::test_account_api -v
```
- Test passes with correct provider credentials

**Verify no regression:**
```bash
pytest tests/test_cli_account.py -v
```
- All CLI account tests pass

---

**Expected Outcome**: account api test verifies correct provider credentials written
**Error Conditions**: Wrong provider used → check provider factory logic
**Validation**: Test verifies provider-specific env vars
**Success Criteria**: account api generates claude-env with selected provider
**Report Path**: plans/claude-tools-recovery/reports/cycle-2-4-notes.md

---

**Checkpoint**

1. Fix: Run `just dev`. Sonnet quiet-task fixes failures. Commit when green.
2. Vet: Review CLI test quality, fixture patterns, mock locations. Commit fixes.
3. Functional review: Verify CLI commands use real filesystem reads (get_account_state), not hardcoded stubs. Check claude-env file generation uses providers. If stubs remain, STOP and report.

---

## Phase R3: Error handling and integration tests

Add error handling for edge cases and end-to-end integration tests.

## Cycle 3.1: Handle keychain command not found

**Objective**: Test Keychain handles FileNotFoundError when security command unavailable
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** tests/test_account_keychain.py should test Keychain.find() handles FileNotFoundError gracefully

**Expected failure:**
```
FileNotFoundError not caught, test fails with unhandled exception
```

**Why it fails:** Keychain.find() doesn't catch subprocess FileNotFoundError

**Verify RED:**
```bash
pytest tests/test_account_keychain.py::test_keychain_command_not_found -v
```
- Create test with mock subprocess.run raising FileNotFoundError
- Assert Keychain().find() returns None (graceful degradation)
- Test should FAIL with uncaught exception

---

**GREEN Phase:**

**Implementation:** Add try/except to catch FileNotFoundError

**Changes:**
- File: src/claudeutils/account/keychain.py
  Action: Wrap subprocess.run in try/except, catch FileNotFoundError, return None
- File: tests/test_account_keychain.py
  Action: Add test with FileNotFoundError mock, assert find() returns None

**Verify GREEN:**
```bash
pytest tests/test_account_keychain.py::test_keychain_command_not_found -v
```
- Test passes with None return

**Verify no regression:**
```bash
pytest tests/test_account_keychain.py -v
```
- All keychain tests pass

---

**Expected Outcome**: Keychain returns None when security command unavailable
**Error Conditions**: Still raises exception → verify try/except scope
**Validation**: Test verifies None return on FileNotFoundError
**Success Criteria**: Keychain error handling for missing command
**Report Path**: plans/claude-tools-recovery/reports/cycle-3-1-notes.md

---

## Cycle 3.2: Handle missing config files gracefully

**Objective**: Test get_account_state() uses defaults when config files missing
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** tests/test_account_state.py should test factory returns default state when files missing

**Expected failure:**
```
FileNotFoundError or returns None instead of default state
```

**Why it fails:** Factory doesn't handle missing file case

**Verify RED:**
```bash
pytest tests/test_account_state.py::test_get_account_state_missing_files -v
```
- Create test with empty tmp_path (no .claude dir)
- Mock Path.home() to return tmp_path
- Assert returns AccountState with mode="plan", provider="anthropic" defaults
- Test should FAIL if factory raises exception

---

**GREEN Phase:**

**Implementation:** Add default fallback when config files don't exist

**Changes:**
- File: src/claudeutils/account/state.py
  Action: In get_account_state(), wrap file reads in try/except FileNotFoundError, use defaults
- File: tests/test_account_state.py
  Action: Create test file, add test with missing files, assert default state

**Verify GREEN:**
```bash
pytest tests/test_account_state.py::test_get_account_state_missing_files -v
```
- Test passes with default state

**Verify no regression:**
```bash
pytest tests/test_account_state.py -v
```
- All state tests pass

---

**Expected Outcome**: State factory handles missing files with defaults
**Error Conditions**: Exception raised → add try/except around file reads
**Validation**: Test verifies default state returned
**Success Criteria**: Factory robust to missing configuration
**Report Path**: plans/claude-tools-recovery/reports/cycle-3-2-notes.md

---

## Cycle 3.3: Integration test for mode switching round-trip

**Objective**: Test full workflow switching modes and verifying file state
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** tests/test_cli_account.py should test sequential mode switches with file verification

**Expected failure:**
```
May fail if file writes don't persist or state reads incorrect
```

**Why it fails:** Integration gaps between commands

**Verify RED:**
```bash
pytest tests/test_cli_account.py::test_account_mode_round_trip -v
```
- Create test that invokes account plan, then account api, then account plan again
- Verify files after each command
- Test should FAIL if any step doesn't persist state correctly

---

**GREEN Phase:**

**Implementation:** Ensure all commands read/write state correctly (should already work from previous cycles)

**Changes:**
- File: tests/test_cli_account.py
  Action: Add integration test with sequential CLI invocations within same CliRunner context, verify file state after each

**Verify GREEN:**
```bash
pytest tests/test_cli_account.py::test_account_mode_round_trip -v
```
- Test passes with all mode switches verified

**Verify no regression:**
```bash
pytest tests/test_cli_account.py -v
```
- All CLI tests pass

---

**Expected Outcome**: Integration test verifies full workflow end-to-end
**Error Conditions**: File state inconsistent → check write/read paths match
**Validation**: Test verifies files after each command
**Success Criteria**: Round-trip mode switching works correctly
**Report Path**: plans/claude-tools-recovery/reports/cycle-3-3-notes.md

---

**Checkpoint**

1. Fix: Run `just dev`. Sonnet quiet-task fixes failures. Commit when green.
2. Vet: Review error handling, integration test coverage. Commit fixes.
3. Functional review: Manual test `account status`, `account plan`, `account api` commands with real ~/.claude/ directory. Verify actual output (mode/provider read from files, claude-env generated with credentials). If commands still return stubs or hardcoded values, STOP and report.

---

## Design Decisions

Copied from plans/claude-tools-recovery/design.md:

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
- `unittest.mock.patch("claudeutils.account.state.subprocess.run")` not `patch("subprocess.run")`
- `patch("claudeutils.account.state.Path.home")` not `patch("pathlib.Path.home")`
- Consistent with existing project mock patterns
- More precise, less likely to affect unrelated code

## Dependencies

**Before:**
- Skill improvements applied (plans/skill-improvements/design.md)
- Improved plan-tdd generates behavioral RED tests
- Improved review-tdd-plan catches weak assertions

**After:**
- CLI commands functional with real I/O
- Statusline display modules (follow-up design)
- Shell script deprecation (replace shell callers with Python CLI)
