---
name: claude-tools-recovery
type: tdd
model: haiku
---

# Claude Tools Recovery TDD Runbook

**Context**: Fix stub implementations in claude-tools rewrite by strengthening tests and wiring real I/O

**Design**: plans/claude-tools-recovery/design.md

**Status**: Draft

**Created**: 2026-01-30

## Weak Orchestrator Metadata

**Total Steps**: 43

**Execution Model**: All cycles: Haiku (TDD execution)

**Step Dependencies**: Sequential within phases

**Error Escalation**: Haiku → User on stop conditions/regression

**Report Locations**: plans/claude-tools-recovery/reports/

**Success Criteria**: All cycles GREEN, no regressions, CLI commands functional with real I/O

**Prerequisites**: Skill improvements from plans/skill-improvements/design.md applied

## Common Context

**Key Design Decisions:**

1. **Approach: Strengthen tests then wire**
   - Structure is correct, only internals need work
   - Strengthened tests create RED phase naturally (stubs fail behavioral assertions)
   - Dogfoods improved plan-tdd skill

2. **Phase R0 deletes before strengthening**
   - Vacuous tests add noise and false confidence
   - Removing them first clarifies what needs behavioral assertions

3. **Statusline display modules deferred**
   - Complex formatting needs separate design
   - Focus on I/O wiring and state management first

4. **Mock strategy: patch at usage location**
   - `patch("claudeutils.account.state.subprocess.run")` not `patch("subprocess.run")`
   - More precise, consistent with project patterns

**TDD Protocol:**

Strict RED-GREEN-REFACTOR: 1) RED: Write failing test, 2) Verify RED, 3) GREEN: Minimal implementation, 4) Verify GREEN, 5) Verify Regression, 6) REFACTOR (optional)

**Project Paths:**

- Source: `claudeutils/` (account/, model/, statusline/)
- Tests: `tests/` (test_account.py, test_model.py, test_statusline.py)
- Config: `~/.claude/` (account-mode, account-provider, .env)
- Keychain: macOS keychain services

**Conventions:**

- Use Read/Write/Edit/Grep tools (not Bash for file ops)
- Report errors explicitly (never suppress)
- Write notes to plans/claude-tools-recovery/reports/cycle-{X}-{Y}-notes.md

**Stop Conditions (all cycles):**

STOP IMMEDIATELY if: RED phase test passes (expected failure) • RED phase failure message doesn't match expected • GREEN phase tests don't pass after implementation • Any phase existing tests break (regression)

Actions when stopped: 1) Document in reports/cycle-{X}-{Y}-notes.md 2) Test passes unexpectedly → Investigate if feature exists 3) Regression → STOP, report broken tests 4) Scope unclear → STOP, document ambiguity

**Dependencies:**

Sequential within each phase. Phases must complete in order: R0 → R1 → R2 → R3 → R4

---

## Phase R0: Clean up vacuous tests

## Cycle 0.1: Delete exit-code-only account status test

**Objective**: Remove test_account_status_basic that only checks exit_code == 0

**Script Evaluation**: Direct execution (TDD cycle)

**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** Verify test file doesn't contain the vacuous test

**Expected failure:**
```
AssertionError: test_account_status_basic still exists in test_account.py
```

**Why it fails:** Test hasn't been deleted yet

**Verify RED:** Read tests/test_account.py and grep for "test_account_status_basic"
- Must find the function definition
- If not found, STOP - test may already be deleted

---

**GREEN Phase:**

**Implementation:** Delete test_account_status_basic function from tests/test_account.py

**Changes:**
- File: tests/test_account.py
  Action: Remove test_account_status_basic function (including decorator and docstring)

**Verify GREEN:** Read tests/test_account.py
- Must NOT contain "test_account_status_basic"

**Verify no regression:** `pytest tests/test_account.py`
- All remaining tests pass

---

**Expected Outcome**: Vacuous test removed, remaining tests pass

**Error Conditions**: Test not found → STOP (may be already deleted); Regression → STOP

**Validation**: Test deleted ✓, No regressions ✓

**Success Criteria**: Test file doesn't contain vacuous test, other tests still pass

**Report Path**: plans/claude-tools-recovery/reports/cycle-0-1-notes.md

---

## Cycle 0.2: Delete hasattr-only provider tests

**Objective**: Remove tests that only verify providers have methods via hasattr

**Script Evaluation**: Direct execution (TDD cycle)

**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** Verify test file doesn't contain hasattr-only tests for providers

**Expected failure:**
```
AssertionError: hasattr-only provider tests still exist
```

**Why it fails:** Tests haven't been deleted yet

**Verify RED:** Grep tests/test_account.py for tests that:
- Only use `assert hasattr(provider, "method_name")`
- No behavior assertions
- Likely names: test_anthropic_provider_has_methods, test_openrouter_provider_has_methods

---

**GREEN Phase:**

**Implementation:** Delete hasattr-only provider test functions

**Changes:**
- File: tests/test_account.py
  Action: Remove test functions that only check hasattr on providers

**Verify GREEN:** Grep tests/test_account.py
- Must NOT find hasattr-only provider tests

**Verify no regression:** `pytest tests/test_account.py`
- All remaining tests pass

---

**Expected Outcome**: Hasattr-only tests removed, remaining tests pass

**Error Conditions**: Tests not found → STOP; Regression → STOP

**Validation**: Tests deleted ✓, No regressions ✓

**Success Criteria**: No hasattr-only provider tests remain

**Report Path**: plans/claude-tools-recovery/reports/cycle-0-2-notes.md

---

## Cycle 0.3: Delete isinstance-only model tests

**Objective**: Remove tests that only verify model objects are correct type

**Script Evaluation**: Direct execution (TDD cycle)

**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** Verify test file doesn't contain isinstance-only tests

**Expected failure:**
```
AssertionError: isinstance-only model tests still exist
```

**Why it fails:** Tests haven't been deleted yet

**Verify RED:** Grep tests/test_model.py for tests that:
- Only use `assert isinstance(result, SomeClass)`
- No behavior assertions
- Likely pattern: instantiation tests without method calls

---

**GREEN Phase:**

**Implementation:** Delete isinstance-only test functions

**Changes:**
- File: tests/test_model.py
  Action: Remove test functions that only check isinstance

**Verify GREEN:** Read tests/test_model.py
- Verify removed tests no longer present

**Verify no regression:** `pytest tests/test_model.py`
- All remaining tests pass

---

**Expected Outcome**: Isinstance-only tests removed, remaining tests pass

**Error Conditions**: Tests not found → STOP; Regression → STOP

**Validation**: Tests deleted ✓, No regressions ✓

**Success Criteria**: No isinstance-only tests remain

**Report Path**: plans/claude-tools-recovery/reports/cycle-0-3-notes.md

---

## Cycle 0.4: Delete statusline OK-output test

**Objective**: Remove test that only checks statusline returns "OK" string

**Script Evaluation**: Direct execution (TDD cycle)

**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** Verify test file doesn't contain OK-output test

**Expected failure:**
```
AssertionError: statusline OK test still exists
```

**Why it fails:** Test hasn't been deleted yet

**Verify RED:** Grep tests/test_statusline.py for test checking output == "OK" or similar stub
- Likely name: test_statusline_basic or test_statusline_output

---

**GREEN Phase:**

**Implementation:** Delete statusline OK-output test function

**Changes:**
- File: tests/test_statusline.py
  Action: Remove test that checks for "OK" output

**Verify GREEN:** Read tests/test_statusline.py
- Test no longer present

**Verify no regression:** `pytest tests/test_statusline.py`
- All remaining tests pass

---

**Expected Outcome**: OK-output test removed, remaining tests pass

**Error Conditions**: Test not found → STOP; Regression → STOP

**Validation**: Test deleted ✓, No regressions ✓

**Success Criteria**: No stub output test remains

**Report Path**: plans/claude-tools-recovery/reports/cycle-0-4-notes.md

---

**Checkpoint**

1. Fix: Run `just dev`. Sonnet quiet-task fixes failures. Commit when green.
2. Vet: Review test deletions (confirm no valuable tests removed). Commit.
3. Functional review: Verify remaining tests have some behavioral content (even if weak - will strengthen in R1/R2).

---

## Phase R1: Strengthen provider and keychain tests

## Cycle 1.1: Strengthen Anthropic provider keychain test

**Objective**: Add mock keychain query and assert non-empty API key in claude_env_vars()

**Script Evaluation**: Direct execution (TDD cycle)

**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** Test AnthropicProvider.claude_env_vars() returns actual keychain value

**Expected failure:**
```
AssertionError: expected ANTHROPIC_API_KEY='sk-ant-test123', got ANTHROPIC_API_KEY=''
```

**Why it fails:** Stub implementation returns empty string

**Verify RED:** Run `pytest tests/test_account.py::test_anthropic_provider_credentials -v`
- Must fail with empty credential assertion
- If passes, STOP - implementation may already be real

---

**GREEN Phase:**

**Implementation:** Mock subprocess.run for keychain query, assert non-empty API key

**Changes:**
- File: tests/test_account.py
  Action: Update test_anthropic_provider_credentials (or create if missing):
    - Import: `from unittest.mock import patch, MagicMock`
    - Mock: `patch("claudeutils.account.providers.subprocess.run")`
    - Return: keychain password "sk-ant-test123"
    - Assert: `env_vars["ANTHROPIC_API_KEY"] == "sk-ant-test123"`
    - Assert: subprocess called with correct service/account args

**Verify GREEN:** `pytest tests/test_account.py::test_anthropic_provider_credentials -v`
- Must pass

**Verify no regression:** `pytest tests/test_account.py`
- All existing tests pass

---

**Expected Outcome**: Test verifies keychain integration with mocked subprocess

**Error Conditions**: Test passes on RED → STOP; GREEN doesn't pass → Debug

**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓

**Success Criteria**: Test asserts on keychain value, not empty string

**Report Path**: plans/claude-tools-recovery/reports/cycle-1-1-notes.md

---

## Cycle 1.2: Strengthen OpenRouter provider keychain test

**Objective**: Add mock keychain query and assert non-empty API key + base URL

**Script Evaluation**: Direct execution (TDD cycle)

**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** Test OpenRouterProvider.claude_env_vars() returns keychain value and base URL

**Expected failure:**
```
AssertionError: expected OPENROUTER_API_KEY='sk-or-test456', got OPENROUTER_API_KEY=''
```

**Why it fails:** Stub implementation returns empty string

**Verify RED:** Run `pytest tests/test_account.py::test_openrouter_provider_credentials -v`
- Must fail with empty credential or missing base URL assertion
- If passes, STOP

---

**GREEN Phase:**

**Implementation:** Mock keychain, assert API key and OPENROUTER_BASE_URL

**Changes:**
- File: tests/test_account.py
  Action: Update test_openrouter_provider_credentials:
    - Mock: `patch("claudeutils.account.providers.subprocess.run")`
    - Return: keychain password "sk-or-test456"
    - Assert: `env_vars["OPENROUTER_API_KEY"] == "sk-or-test456"`
    - Assert: `env_vars["OPENROUTER_BASE_URL"] == "https://openrouter.ai/api/v1"`
    - Assert: subprocess called with correct service/account

**Verify GREEN:** `pytest tests/test_account.py::test_openrouter_provider_credentials -v`
- Must pass

**Verify no regression:** `pytest tests/test_account.py`
- All tests pass

---

**Expected Outcome**: Test verifies keychain integration and base URL setting

**Error Conditions**: RED passes → STOP; GREEN fails → Debug

**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓

**Success Criteria**: Test asserts keychain value and base URL, not empty

**Report Path**: plans/claude-tools-recovery/reports/cycle-1-2-notes.md

---

## Cycle 1.3: Strengthen LiteLLM provider test

**Objective**: Assert LiteLLMProvider returns localhost URL without keychain dependency

**Script Evaluation**: Direct execution (TDD cycle)

**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** Test LiteLLMProvider.claude_env_vars() returns localhost URL

**Expected failure:**
```
AssertionError: expected LITELLM_BASE_URL='http://localhost:4000', got LITELLM_BASE_URL=''
```

**Why it fails:** Stub returns empty or hardcoded "OK"

**Verify RED:** Run `pytest tests/test_account.py::test_litellm_provider_credentials -v`
- Must fail with localhost URL assertion
- If passes, STOP

---

**GREEN Phase:**

**Implementation:** Assert localhost URL in env vars (no keychain mock needed)

**Changes:**
- File: tests/test_account.py
  Action: Update test_litellm_provider_credentials:
    - Assert: `env_vars["LITELLM_BASE_URL"] == "http://localhost:4000"`
    - No keychain mock (LiteLLM doesn't use credentials)

**Verify GREEN:** `pytest tests/test_account.py::test_litellm_provider_credentials -v`
- Must pass

**Verify no regression:** `pytest tests/test_account.py`
- All tests pass

---

**Expected Outcome**: Test verifies localhost URL without keychain

**Error Conditions**: RED passes → STOP; GREEN fails → Debug

**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓

**Success Criteria**: Test asserts localhost URL

**Report Path**: plans/claude-tools-recovery/reports/cycle-1-3-notes.md

---

## Cycle 1.4: Test Anthropic provider missing keychain entry

**Objective**: Mock missing keychain entry and verify error handling

**Script Evaluation**: Direct execution (TDD cycle)

**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** Test AnthropicProvider handles missing keychain entry gracefully

**Expected failure:**
```
FAILED - KeychainError not raised when keychain entry missing
```

**Why it fails:** Stub doesn't query keychain, can't fail

**Verify RED:** Run `pytest tests/test_account.py::test_anthropic_missing_keychain -v`
- Must fail (KeychainError not raised or wrong error type)
- If passes, STOP

---

**GREEN Phase:**

**Implementation:** Mock subprocess CalledProcessError (keychain not found), assert error raised

**Changes:**
- File: tests/test_account.py
  Action: Create test_anthropic_missing_keychain:
    - Mock: `patch("claudeutils.account.providers.subprocess.run")` raises CalledProcessError
    - Call: `provider.claude_env_vars()`
    - Assert: Raises KeychainError or returns empty with error message

**Verify GREEN:** `pytest tests/test_account.py::test_anthropic_missing_keychain -v`
- Must pass

**Verify no regression:** `pytest tests/test_account.py`
- All tests pass

---

**Expected Outcome**: Test verifies error handling for missing credentials

**Error Conditions**: RED passes → STOP; GREEN fails → Debug

**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓

**Success Criteria**: Test asserts error on missing keychain entry

**Report Path**: plans/claude-tools-recovery/reports/cycle-1-4-notes.md

---

## Cycle 1.5: Test keychain wrapper find operation

**Objective**: Mock subprocess for keychain find, assert correct command construction

**Script Evaluation**: Direct execution (TDD cycle)

**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** Test Keychain.find() constructs correct security command

**Expected failure:**
```
AssertionError: subprocess.run not called with expected security find-generic-password args
```

**Why it fails:** Stub doesn't call subprocess

**Verify RED:** Run `pytest tests/test_account.py::test_keychain_find -v`
- Must fail with mock call assertion
- If passes, STOP

---

**GREEN Phase:**

**Implementation:** Mock subprocess, assert find-generic-password command with service/account

**Changes:**
- File: tests/test_account.py
  Action: Create/update test_keychain_find:
    - Mock: `patch("claudeutils.account.keychain.subprocess.run")`
    - Return: MagicMock with stdout containing password
    - Call: `Keychain.find(service="test-service", account="test-account")`
    - Assert: subprocess.run called with ["security", "find-generic-password", "-s", "test-service", "-a", "test-account", "-w"]
    - Assert: Returns password from stdout

**Verify GREEN:** `pytest tests/test_account.py::test_keychain_find -v`
- Must pass

**Verify no regression:** `pytest tests/test_account.py`
- All tests pass

---

**Expected Outcome**: Test verifies keychain find command construction

**Error Conditions**: RED passes → STOP; GREEN fails → Debug

**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓

**Success Criteria**: Test asserts subprocess called with correct args

**Report Path**: plans/claude-tools-recovery/reports/cycle-1-5-notes.md

---

## Cycle 1.6: Test keychain wrapper add operation

**Objective**: Mock subprocess for keychain add, assert correct command construction

**Script Evaluation**: Direct execution (TDD cycle)

**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** Test Keychain.add() constructs correct security command

**Expected failure:**
```
AssertionError: subprocess.run not called with expected add-generic-password args
```

**Why it fails:** Stub doesn't call subprocess

**Verify RED:** Run `pytest tests/test_account.py::test_keychain_add -v`
- Must fail with mock call assertion
- If passes, STOP

---

**GREEN Phase:**

**Implementation:** Mock subprocess, assert add-generic-password command

**Changes:**
- File: tests/test_account.py
  Action: Create/update test_keychain_add:
    - Mock: `patch("claudeutils.account.keychain.subprocess.run")`
    - Call: `Keychain.add(service="test-service", account="test-account", password="test-pass")`
    - Assert: subprocess.run called with ["security", "add-generic-password", "-s", "test-service", "-a", "test-account", "-w", "test-pass"]

**Verify GREEN:** `pytest tests/test_account.py::test_keychain_add -v`
- Must pass

**Verify no regression:** `pytest tests/test_account.py`
- All tests pass

---

**Expected Outcome**: Test verifies keychain add command construction

**Error Conditions**: RED passes → STOP; GREEN fails → Debug

**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓

**Success Criteria**: Test asserts subprocess called with add args

**Report Path**: plans/claude-tools-recovery/reports/cycle-1-6-notes.md

---

## Cycle 1.7: Test keychain entry not found

**Objective**: Mock CalledProcessError from keychain, verify error handling

**Script Evaluation**: Direct execution (TDD cycle)

**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** Test Keychain.find() raises KeychainError when entry not found

**Expected failure:**
```
FAILED - KeychainError not raised on entry not found
```

**Why it fails:** Stub doesn't detect missing entry

**Verify RED:** Run `pytest tests/test_account.py::test_keychain_not_found -v`
- Must fail (no error raised or wrong type)
- If passes, STOP

---

**GREEN Phase:**

**Implementation:** Mock subprocess CalledProcessError, assert KeychainError raised

**Changes:**
- File: tests/test_account.py
  Action: Create test_keychain_not_found:
    - Mock: `patch("claudeutils.account.keychain.subprocess.run")` raises CalledProcessError(returncode=44)
    - Call: `Keychain.find(service="missing", account="missing")`
    - Assert: Raises KeychainError with appropriate message

**Verify GREEN:** `pytest tests/test_account.py::test_keychain_not_found -v`
- Must pass

**Verify no regression:** `pytest tests/test_account.py`
- All tests pass

---

**Expected Outcome**: Test verifies error on missing keychain entry

**Error Conditions**: RED passes → STOP; GREEN fails → Debug

**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓

**Success Criteria**: Test asserts KeychainError raised

**Report Path**: plans/claude-tools-recovery/reports/cycle-1-7-notes.md

---

**Checkpoint**

1. Fix: Run `just dev`. Sonnet quiet-task fixes failures. Commit when green.
2. Vet: Review provider/keychain test quality. Commit fixes.
3. Functional review: Verify tests mock real I/O (subprocess), assert on behavior (not just structure).

---

## Phase R2: Strengthen CLI tests

## Cycle 2.1: Strengthen account status test - mode and provider files

**Objective**: Mock filesystem with mode/provider files, assert output contains actual values

**Script Evaluation**: Direct execution (TDD cycle)

**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** Test account status displays mode and provider from fixture files

**Expected failure:**
```
AssertionError: expected output to contain 'Mode: plan', got 'Mode: <hardcoded>'
```

**Why it fails:** Stub returns hardcoded output, doesn't read files

**Verify RED:** Run `pytest tests/test_account.py::test_account_status_reads_files -v`
- Must fail with fixture value assertion
- If passes, STOP

---

**GREEN Phase:**

**Implementation:** Mock Path.home(), create tmp_path fixtures, assert output contains fixture values

**Changes:**
- File: tests/test_account.py
  Action: Create/update test_account_status_reads_files:
    - Fixture: Use pytest tmp_path
    - Setup: Create tmp_path/.claude/account-mode with "plan\n"
    - Setup: Create tmp_path/.claude/account-provider with "anthropic\n"
    - Mock: `patch("claudeutils.account.state.Path.home", return_value=tmp_path)`
    - Run: `account status` via CliRunner
    - Assert: Output contains "Mode: plan"
    - Assert: Output contains "Provider: anthropic"

**Verify GREEN:** `pytest tests/test_account.py::test_account_status_reads_files -v`
- Must pass

**Verify no regression:** `pytest tests/test_account.py`
- All tests pass

---

**Expected Outcome**: Test verifies filesystem reading with mocked home directory

**Error Conditions**: RED passes → STOP; GREEN fails → Debug

**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓

**Success Criteria**: Test asserts output contains fixture file values

**Report Path**: plans/claude-tools-recovery/reports/cycle-2-1-notes.md

---

## Cycle 2.2: Strengthen account status test - keychain OAuth check

**Objective**: Mock keychain query for OAuth token, assert output shows OAuth status

**Script Evaluation**: Direct execution (TDD cycle)

**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** Test account status displays OAuth status from keychain query

**Expected failure:**
```
AssertionError: expected output to contain 'OAuth: Yes', got 'OAuth: <hardcoded>'
```

**Why it fails:** Stub doesn't query keychain

**Verify RED:** Run `pytest tests/test_account.py::test_account_status_oauth -v`
- Must fail with OAuth status assertion
- If passes, STOP

---

**GREEN Phase:**

**Implementation:** Mock keychain find for OAuth token, assert output shows status

**Changes:**
- File: tests/test_account.py
  Action: Create/update test_account_status_oauth:
    - Fixture: tmp_path with mode/provider files
    - Mock: `patch("claudeutils.account.state.Path.home", return_value=tmp_path)`
    - Mock: `patch("claudeutils.account.state.subprocess.run")` returns OAuth token
    - Run: `account status`
    - Assert: Output contains "OAuth: Yes" or "OAuth in keychain: Yes"

**Verify GREEN:** `pytest tests/test_account.py::test_account_status_oauth -v`
- Must pass

**Verify no regression:** `pytest tests/test_account.py`
- All tests pass

---

**Expected Outcome**: Test verifies keychain OAuth query integration

**Error Conditions**: RED passes → STOP; GREEN fails → Debug

**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓

**Success Criteria**: Test asserts OAuth status from mocked keychain

**Report Path**: plans/claude-tools-recovery/reports/cycle-2-2-notes.md

---

## Cycle 2.3: Strengthen account status test - API key in .env check

**Objective**: Mock .env file existence, assert output shows API key status

**Script Evaluation**: Direct execution (TDD cycle)

**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** Test account status displays API key status from .env file check

**Expected failure:**
```
AssertionError: expected output to contain 'API key in .env: Yes', got hardcoded value
```

**Why it fails:** Stub doesn't check .env file

**Verify RED:** Run `pytest tests/test_account.py::test_account_status_env -v`
- Must fail with .env status assertion
- If passes, STOP

---

**GREEN Phase:**

**Implementation:** Create .env file in fixture, assert output shows API key status

**Changes:**
- File: tests/test_account.py
  Action: Create/update test_account_status_env:
    - Fixture: tmp_path with mode/provider files
    - Setup: Create tmp_path/.claude/.env file (can be empty)
    - Mock: `patch("claudeutils.account.state.Path.home", return_value=tmp_path)`
    - Run: `account status`
    - Assert: Output contains "API key in .env: Yes" or similar

**Verify GREEN:** `pytest tests/test_account.py::test_account_status_env -v`
- Must pass

**Verify no regression:** `pytest tests/test_account.py`
- All tests pass

---

**Expected Outcome**: Test verifies .env file existence check

**Error Conditions**: RED passes → STOP; GREEN fails → Debug

**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓

**Success Criteria**: Test asserts .env status from fixture

**Report Path**: plans/claude-tools-recovery/reports/cycle-2-3-notes.md

---

## Cycle 2.4: Strengthen account status test - consistency validation

**Objective**: Create inconsistent state fixture, assert output shows validation warnings

**Script Evaluation**: Direct execution (TDD cycle)

**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** Test account status displays consistency warnings for mismatched state

**Expected failure:**
```
AssertionError: expected validation warning in output, not found
```

**Why it fails:** Stub doesn't run validation

**Verify RED:** Run `pytest tests/test_account.py::test_account_status_validation -v`
- Must fail (no validation output)
- If passes, STOP

---

**GREEN Phase:**

**Implementation:** Create inconsistent fixture (mode=api + OAuth in keychain), assert warning

**Changes:**
- File: tests/test_account.py
  Action: Create test_account_status_validation:
    - Fixture: tmp_path/.claude/account-mode = "api"
    - Mock: OAuth token in keychain (mode=api shouldn't have OAuth)
    - Mock: `patch("claudeutils.account.state.Path.home", return_value=tmp_path)`
    - Run: `account status`
    - Assert: Output contains validation warning or inconsistency message

**Verify GREEN:** `pytest tests/test_account.py::test_account_status_validation -v`
- Must pass

**Verify no regression:** `pytest tests/test_account.py`
- All tests pass

---

**Expected Outcome**: Test verifies validation logic runs and outputs warnings

**Error Conditions**: RED passes → STOP; GREEN fails → Debug

**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓

**Success Criteria**: Test asserts validation warning present

**Report Path**: plans/claude-tools-recovery/reports/cycle-2-4-notes.md

---

## Cycle 2.5: Strengthen account plan command test

**Objective**: Mock filesystem, assert mode file written and output confirms switch

**Script Evaluation**: Direct execution (TDD cycle)

**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** Test account plan writes mode file and outputs confirmation

**Expected failure:**
```
AssertionError: mode file not written or contains wrong value
```

**Why it fails:** Stub doesn't write file

**Verify RED:** Run `pytest tests/test_account.py::test_account_plan_switch -v`
- Must fail (file not written or wrong content)
- If passes, STOP

---

**GREEN Phase:**

**Implementation:** Mock filesystem, run account plan, assert mode file and output

**Changes:**
- File: tests/test_account.py
  Action: Create/update test_account_plan_switch:
    - Fixture: tmp_path
    - Mock: `patch("claudeutils.account.state.Path.home", return_value=tmp_path)`
    - Run: `account plan` via CliRunner
    - Assert: tmp_path/.claude/account-mode file exists
    - Assert: File content == "plan\n"
    - Assert: Output contains "Switched to plan mode" or similar

**Verify GREEN:** `pytest tests/test_account.py::test_account_plan_switch -v`
- Must pass

**Verify no regression:** `pytest tests/test_account.py`
- All tests pass

---

**Expected Outcome**: Test verifies mode file write and confirmation output

**Error Conditions**: RED passes → STOP; GREEN fails → Debug

**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓

**Success Criteria**: Test asserts file written with correct mode value

**Report Path**: plans/claude-tools-recovery/reports/cycle-2-5-notes.md

---

## Cycle 2.6: Strengthen account api command test

**Objective**: Mock filesystem and keychain, assert mode file and claude-env generated

**Script Evaluation**: Direct execution (TDD cycle)

**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** Test account api writes mode file and generates claude-env with credentials

**Expected failure:**
```
AssertionError: claude-env file not created or missing credentials
```

**Why it fails:** Stub doesn't generate claude-env

**Verify RED:** Run `pytest tests/test_account.py::test_account_api_switch -v`
- Must fail (claude-env not created or empty)
- If passes, STOP

---

**GREEN Phase:**

**Implementation:** Mock keychain, run account api, assert mode file and claude-env

**Changes:**
- File: tests/test_account.py
  Action: Create/update test_account_api_switch:
    - Fixture: tmp_path
    - Mock: `patch("claudeutils.account.state.Path.home", return_value=tmp_path)`
    - Mock: `patch("claudeutils.account.providers.subprocess.run")` returns API key
    - Run: `account api`
    - Assert: tmp_path/.claude/account-mode == "api\n"
    - Assert: tmp_path/.claude/.env exists and contains ANTHROPIC_API_KEY (or provider key)
    - Assert: Output confirms switch

**Verify GREEN:** `pytest tests/test_account.py::test_account_api_switch -v`
- Must pass

**Verify no regression:** `pytest tests/test_account.py`
- All tests pass

---

**Expected Outcome**: Test verifies mode file and claude-env generation

**Error Conditions**: RED passes → STOP; GREEN fails → Debug

**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓

**Success Criteria**: Test asserts both files written with correct content

**Report Path**: plans/claude-tools-recovery/reports/cycle-2-6-notes.md

---

## Cycle 2.7: Strengthen model list command test

**Objective**: Mock LiteLLM config, assert output contains model names

**Script Evaluation**: Direct execution (TDD cycle)

**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** Test model list displays models from LiteLLM config

**Expected failure:**
```
AssertionError: expected model names in output, got empty or hardcoded list
```

**Why it fails:** Stub doesn't read config

**Verify RED:** Run `pytest tests/test_model.py::test_model_list_output -v`
- Must fail (no model names or wrong names)
- If passes, STOP

---

**GREEN Phase:**

**Implementation:** Mock LiteLLM config file, assert output contains model names

**Changes:**
- File: tests/test_model.py
  Action: Create/update test_model_list_output:
    - Fixture: tmp_path with LiteLLM config YAML containing model_list
    - Mock: Config path to point to fixture
    - Run: `model list`
    - Assert: Output contains model names from fixture (e.g., "claude-sonnet-4-5")

**Verify GREEN:** `pytest tests/test_model.py::test_model_list_output -v`
- Must pass

**Verify no regression:** `pytest tests/test_model.py`
- All tests pass

---

**Expected Outcome**: Test verifies LiteLLM config reading and model display

**Error Conditions**: RED passes → STOP; GREEN fails → Debug

**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓

**Success Criteria**: Test asserts model names from config in output

**Report Path**: plans/claude-tools-recovery/reports/cycle-2-7-notes.md

---

## Cycle 2.8: Strengthen model set command test

**Objective**: Mock filesystem, assert override file written with model name

**Script Evaluation**: Direct execution (TDD cycle)

**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** Test model set writes override file with specified model

**Expected failure:**
```
AssertionError: override file not written or contains wrong model
```

**Why it fails:** Stub doesn't write file

**Verify RED:** Run `pytest tests/test_model.py::test_model_set_writes_file -v`
- Must fail (file not written)
- If passes, STOP

---

**GREEN Phase:**

**Implementation:** Mock override file path, run model set, assert file content

**Changes:**
- File: tests/test_model.py
  Action: Create/update test_model_set_writes_file:
    - Fixture: tmp_path for override file
    - Mock: Override file path to tmp_path
    - Run: `model set claude-opus-4`
    - Assert: Override file exists
    - Assert: File content == "claude-opus-4\n"
    - Assert: Output confirms model set

**Verify GREEN:** `pytest tests/test_model.py::test_model_set_writes_file -v`
- Must pass

**Verify no regression:** `pytest tests/test_model.py`
- All tests pass

---

**Expected Outcome**: Test verifies override file write with model name

**Error Conditions**: RED passes → STOP; GREEN fails → Debug

**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓

**Success Criteria**: Test asserts file written with correct model

**Report Path**: plans/claude-tools-recovery/reports/cycle-2-8-notes.md

---

## Cycle 2.9: Strengthen model reset command test

**Objective**: Mock filesystem, assert override file deleted

**Script Evaluation**: Direct execution (TDD cycle)

**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** Test model reset deletes override file

**Expected failure:**
```
AssertionError: override file still exists after reset
```

**Why it fails:** Stub doesn't delete file

**Verify RED:** Run `pytest tests/test_model.py::test_model_reset_deletes_file -v`
- Must fail (file not deleted)
- If passes, STOP

---

**GREEN Phase:**

**Implementation:** Create override file in fixture, run model reset, assert deleted

**Changes:**
- File: tests/test_model.py
  Action: Create/update test_model_reset_deletes_file:
    - Fixture: tmp_path with existing override file
    - Mock: Override file path to tmp_path
    - Run: `model reset`
    - Assert: Override file does not exist
    - Assert: Output confirms reset

**Verify GREEN:** `pytest tests/test_model.py::test_model_reset_deletes_file -v`
- Must pass

**Verify no regression:** `pytest tests/test_model.py`
- All tests pass

---

**Expected Outcome**: Test verifies override file deletion

**Error Conditions**: RED passes → STOP; GREEN fails → Debug

**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓

**Success Criteria**: Test asserts file deleted

**Report Path**: plans/claude-tools-recovery/reports/cycle-2-9-notes.md

---

## Cycle 2.10: Strengthen statusline command test

**Objective**: Pipe JSON input, assert ANSI-formatted output (not "OK" stub)

**Script Evaluation**: Direct execution (TDD cycle)

**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** Test statusline produces ANSI output from JSON input

**Expected failure:**
```
AssertionError: expected ANSI escape codes in output, got "OK"
```

**Why it fails:** Stub returns "OK" string

**Verify RED:** Run `pytest tests/test_statusline.py::test_statusline_formats_json -v`
- Must fail (no ANSI codes in output)
- If passes, STOP

---

**GREEN Phase:**

**Implementation:** Pipe JSON via CliRunner stdin, assert output contains ANSI codes

**Changes:**
- File: tests/test_statusline.py
  Action: Create/update test_statusline_formats_json:
    - Fixture: JSON string with statusline data (e.g., `{"mode": "plan", "usage": {...}}`)
    - Run: `statusline` via CliRunner with input=json_fixture
    - Assert: Output contains ANSI escape codes (e.g., `\x1b[` pattern)
    - Assert: Output is NOT just "OK"

**Verify GREEN:** `pytest tests/test_statusline.py::test_statusline_formats_json -v`
- Must pass

**Verify no regression:** `pytest tests/test_statusline.py`
- All tests pass

---

**Expected Outcome**: Test verifies JSON parsing and ANSI formatting

**Error Conditions**: RED passes → STOP; GREEN fails → Debug

**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓

**Success Criteria**: Test asserts ANSI codes in output, not stub

**Report Path**: plans/claude-tools-recovery/reports/cycle-2-10-notes.md

---

**Checkpoint**

1. Fix: Run `just dev`. Sonnet quiet-task fixes failures. Commit when green.
2. Vet: Review CLI test quality (mocking, assertions). Commit fixes.
3. Functional review: Verify tests mock real I/O (filesystem, keychain, stdin), assert on output content.

---

## Phase R3: Wire implementations

## Cycle 3.1: Wire AccountState factory to read filesystem

**Objective**: Replace hardcoded AccountState with real file reading

**Script Evaluation**: Direct execution (TDD cycle)

**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** Strengthened test from Cycle 2.1 should now fail

**Expected failure:**
```
AssertionError: expected 'Mode: plan', got 'Mode: <hardcoded>'
```

**Why it fails:** AccountState still returns hardcoded values

**Verify RED:** Run `pytest tests/test_account.py::test_account_status_reads_files -v`
- Must fail with fixture assertion
- If passes, STOP - implementation may already be real

---

**GREEN Phase:**

**Implementation:** Update AccountState factory to read ~/.claude/account-mode and account-provider files

**Changes:**
- File: claudeutils/account/state.py
  Action: Update create_account_state() or AccountState constructor:
    - Read: Path.home() / ".claude" / "account-mode"
    - Read: Path.home() / ".claude" / "account-provider"
    - Parse: Strip whitespace, set AccountState.mode and AccountState.provider
    - Handle: Missing files → default values or None

**Verify GREEN:** `pytest tests/test_account.py::test_account_status_reads_files -v`
- Must pass

**Verify no regression:** `pytest tests/test_account.py`
- All tests pass

---

**Expected Outcome**: AccountState reads real files instead of hardcoded values

**Error Conditions**: RED passes → STOP; GREEN fails → Debug

**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓

**Success Criteria**: Implementation reads filesystem, test passes

**Report Path**: plans/claude-tools-recovery/reports/cycle-3-1-notes.md

---

## Cycle 3.2: Wire AccountState OAuth keychain check

**Objective**: Query keychain for OAuth token instead of returning hardcoded status

**Script Evaluation**: Direct execution (TDD cycle)

**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** Strengthened test from Cycle 2.2 should fail

**Expected failure:**
```
AssertionError: expected 'OAuth: Yes', got 'OAuth: <hardcoded>'
```

**Why it fails:** AccountState doesn't query keychain

**Verify RED:** Run `pytest tests/test_account.py::test_account_status_oauth -v`
- Must fail
- If passes, STOP

---

**GREEN Phase:**

**Implementation:** Update AccountState to query keychain for OAuth token

**Changes:**
- File: claudeutils/account/state.py
  Action: Update create_account_state() or property:
    - Call: Keychain.find(service="claude-oauth", account=<username>) or similar
    - Set: AccountState.oauth_in_keychain = True if found, False if not
    - Handle: KeychainError → False

**Verify GREEN:** `pytest tests/test_account.py::test_account_status_oauth -v`
- Must pass

**Verify no regression:** `pytest tests/test_account.py`
- All tests pass

---

**Expected Outcome**: AccountState queries keychain for OAuth token

**Error Conditions**: RED passes → STOP; GREEN fails → Debug

**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓

**Success Criteria**: Implementation queries keychain, test passes

**Report Path**: plans/claude-tools-recovery/reports/cycle-3-2-notes.md

---

## Cycle 3.3: Wire AccountState .env file check

**Objective**: Check ~/.claude/.env existence instead of hardcoded value

**Script Evaluation**: Direct execution (TDD cycle)

**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** Strengthened test from Cycle 2.3 should fail

**Expected failure:**
```
AssertionError: expected 'API key in .env: Yes', got hardcoded value
```

**Why it fails:** AccountState doesn't check .env file

**Verify RED:** Run `pytest tests/test_account.py::test_account_status_env -v`
- Must fail
- If passes, STOP

---

**GREEN Phase:**

**Implementation:** Update AccountState to check .env file existence

**Changes:**
- File: claudeutils/account/state.py
  Action: Update create_account_state():
    - Check: (Path.home() / ".claude" / ".env").exists()
    - Set: AccountState.api_in_claude_env = True/False

**Verify GREEN:** `pytest tests/test_account.py::test_account_status_env -v`
- Must pass

**Verify no regression:** `pytest tests/test_account.py`
- All tests pass

---

**Expected Outcome**: AccountState checks .env file existence

**Error Conditions**: RED passes → STOP; GREEN fails → Debug

**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓

**Success Criteria**: Implementation checks file, test passes

**Report Path**: plans/claude-tools-recovery/reports/cycle-3-3-notes.md

---

## Cycle 3.4: Wire Anthropic provider keychain retrieval

**Objective**: Query keychain for API key instead of returning empty string

**Script Evaluation**: Direct execution (TDD cycle)

**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** Strengthened test from Cycle 1.1 should fail

**Expected failure:**
```
AssertionError: expected ANTHROPIC_API_KEY='sk-ant-test123', got ''
```

**Why it fails:** Provider doesn't query keychain

**Verify RED:** Run `pytest tests/test_account.py::test_anthropic_provider_credentials -v`
- Must fail
- If passes, STOP

---

**GREEN Phase:**

**Implementation:** Update AnthropicProvider.claude_env_vars() to query keychain

**Changes:**
- File: claudeutils/account/providers.py
  Action: Update AnthropicProvider.claude_env_vars():
    - Call: Keychain.find(service="anthropic-api-key", account=<account>)
    - Return: {"ANTHROPIC_API_KEY": <keychain_value>}
    - Handle: KeychainError → raise or return empty with error

**Verify GREEN:** `pytest tests/test_account.py::test_anthropic_provider_credentials -v`
- Must pass

**Verify no regression:** `pytest tests/test_account.py`
- All tests pass

---

**Expected Outcome**: Anthropic provider queries keychain for API key

**Error Conditions**: RED passes → STOP; GREEN fails → Debug

**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓

**Success Criteria**: Implementation queries keychain, test passes

**Report Path**: plans/claude-tools-recovery/reports/cycle-3-4-notes.md

---

## Cycle 3.5: Wire OpenRouter provider keychain retrieval

**Objective**: Query keychain for API key and set base URL

**Script Evaluation**: Direct execution (TDD cycle)

**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** Strengthened test from Cycle 1.2 should fail

**Expected failure:**
```
AssertionError: expected OPENROUTER_API_KEY='sk-or-test456', got ''
```

**Why it fails:** Provider doesn't query keychain

**Verify RED:** Run `pytest tests/test_account.py::test_openrouter_provider_credentials -v`
- Must fail
- If passes, STOP

---

**GREEN Phase:**

**Implementation:** Update OpenRouterProvider.claude_env_vars() to query keychain and set base URL

**Changes:**
- File: claudeutils/account/providers.py
  Action: Update OpenRouterProvider.claude_env_vars():
    - Call: Keychain.find(service="openrouter-api-key", account=<account>)
    - Return: {"OPENROUTER_API_KEY": <keychain_value>, "OPENROUTER_BASE_URL": "https://openrouter.ai/api/v1"}

**Verify GREEN:** `pytest tests/test_account.py::test_openrouter_provider_credentials -v`
- Must pass

**Verify no regression:** `pytest tests/test_account.py`
- All tests pass

---

**Expected Outcome**: OpenRouter provider queries keychain and sets base URL

**Error Conditions**: RED passes → STOP; GREEN fails → Debug

**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓

**Success Criteria**: Implementation queries keychain, test passes

**Report Path**: plans/claude-tools-recovery/reports/cycle-3-5-notes.md

---

## Cycle 3.6: Wire LiteLLM provider localhost URL

**Objective**: Return localhost URL instead of empty string

**Script Evaluation**: Direct execution (TDD cycle)

**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** Strengthened test from Cycle 1.3 should fail

**Expected failure:**
```
AssertionError: expected LITELLM_BASE_URL='http://localhost:4000', got ''
```

**Why it fails:** Provider returns empty

**Verify RED:** Run `pytest tests/test_account.py::test_litellm_provider_credentials -v`
- Must fail
- If passes, STOP

---

**GREEN Phase:**

**Implementation:** Update LiteLLMProvider.claude_env_vars() to return localhost URL

**Changes:**
- File: claudeutils/account/providers.py
  Action: Update LiteLLMProvider.claude_env_vars():
    - Return: {"LITELLM_BASE_URL": "http://localhost:4000"}

**Verify GREEN:** `pytest tests/test_account.py::test_litellm_provider_credentials -v`
- Must pass

**Verify no regression:** `pytest tests/test_account.py`
- All tests pass

---

**Expected Outcome**: LiteLLM provider returns localhost URL

**Error Conditions**: RED passes → STOP; GREEN fails → Debug

**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓

**Success Criteria**: Implementation returns localhost, test passes

**Report Path**: plans/claude-tools-recovery/reports/cycle-3-6-notes.md

---

## Cycle 3.7: Wire Keychain.find() to subprocess

**Objective**: Call subprocess.run for security find-generic-password

**Script Evaluation**: Direct execution (TDD cycle)

**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** Strengthened test from Cycle 1.5 should fail

**Expected failure:**
```
AssertionError: subprocess.run not called
```

**Why it fails:** Keychain.find() is stub

**Verify RED:** Run `pytest tests/test_account.py::test_keychain_find -v`
- Must fail
- If passes, STOP

---

**GREEN Phase:**

**Implementation:** Update Keychain.find() to call subprocess with security command

**Changes:**
- File: claudeutils/account/keychain.py
  Action: Update Keychain.find():
    - Call: subprocess.run(["security", "find-generic-password", "-s", service, "-a", account, "-w"], capture_output=True, text=True, check=True)
    - Return: result.stdout.strip()
    - Handle: CalledProcessError → raise KeychainError

**Verify GREEN:** `pytest tests/test_account.py::test_keychain_find -v`
- Must pass

**Verify no regression:** `pytest tests/test_account.py`
- All tests pass

---

**Expected Outcome**: Keychain.find() calls subprocess

**Error Conditions**: RED passes → STOP; GREEN fails → Debug

**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓

**Success Criteria**: Implementation calls subprocess, test passes

**Report Path**: plans/claude-tools-recovery/reports/cycle-3-7-notes.md

---

## Cycle 3.8: Wire Keychain.add() to subprocess

**Objective**: Call subprocess.run for security add-generic-password

**Script Evaluation**: Direct execution (TDD cycle)

**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** Strengthened test from Cycle 1.6 should fail

**Expected failure:**
```
AssertionError: subprocess.run not called
```

**Why it fails:** Keychain.add() is stub

**Verify RED:** Run `pytest tests/test_account.py::test_keychain_add -v`
- Must fail
- If passes, STOP

---

**GREEN Phase:**

**Implementation:** Update Keychain.add() to call subprocess

**Changes:**
- File: claudeutils/account/keychain.py
  Action: Update Keychain.add():
    - Call: subprocess.run(["security", "add-generic-password", "-s", service, "-a", account, "-w", password], check=True)

**Verify GREEN:** `pytest tests/test_account.py::test_keychain_add -v`
- Must pass

**Verify no regression:** `pytest tests/test_account.py`
- All tests pass

---

**Expected Outcome**: Keychain.add() calls subprocess

**Error Conditions**: RED passes → STOP; GREEN fails → Debug

**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓

**Success Criteria**: Implementation calls subprocess, test passes

**Report Path**: plans/claude-tools-recovery/reports/cycle-3-8-notes.md

---

## Cycle 3.9: Wire account plan command to write file

**Objective**: Write mode file instead of returning stub output

**Script Evaluation**: Direct execution (TDD cycle)

**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** Strengthened test from Cycle 2.5 should fail

**Expected failure:**
```
AssertionError: mode file not written
```

**Why it fails:** Command doesn't write file

**Verify RED:** Run `pytest tests/test_account.py::test_account_plan_switch -v`
- Must fail
- If passes, STOP

---

**GREEN Phase:**

**Implementation:** Update account plan command to write mode file

**Changes:**
- File: claudeutils/account/cli.py
  Action: Update plan() command:
    - Write: (Path.home() / ".claude" / "account-mode").write_text("plan\n")
    - Output: "Switched to plan mode" message

**Verify GREEN:** `pytest tests/test_account.py::test_account_plan_switch -v`
- Must pass

**Verify no regression:** `pytest tests/test_account.py`
- All tests pass

---

**Expected Outcome**: Command writes mode file

**Error Conditions**: RED passes → STOP; GREEN fails → Debug

**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓

**Success Criteria**: Implementation writes file, test passes

**Report Path**: plans/claude-tools-recovery/reports/cycle-3-9-notes.md

---

## Cycle 3.10: Wire account api command to write files and generate .env

**Objective**: Write mode file and generate claude-env with credentials

**Script Evaluation**: Direct execution (TDD cycle)

**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** Strengthened test from Cycle 2.6 should fail

**Expected failure:**
```
AssertionError: claude-env file not created
```

**Why it fails:** Command doesn't generate .env

**Verify RED:** Run `pytest tests/test_account.py::test_account_api_switch -v`
- Must fail
- If passes, STOP

---

**GREEN Phase:**

**Implementation:** Update account api command to write mode and generate .env

**Changes:**
- File: claudeutils/account/cli.py
  Action: Update api() command:
    - Write: (Path.home() / ".claude" / "account-mode").write_text("api\n")
    - Get: provider.claude_env_vars()
    - Write: (Path.home() / ".claude" / ".env") with env vars
    - Output: Confirmation message

**Verify GREEN:** `pytest tests/test_account.py::test_account_api_switch -v`
- Must pass

**Verify no regression:** `pytest tests/test_account.py`
- All tests pass

---

**Expected Outcome**: Command writes mode file and generates .env

**Error Conditions**: RED passes → STOP; GREEN fails → Debug

**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓

**Success Criteria**: Implementation writes both files, test passes

**Report Path**: plans/claude-tools-recovery/reports/cycle-3-10-notes.md

---

## Cycle 3.11: Wire model list command to read config

**Objective**: Read LiteLLM config and display model names

**Script Evaluation**: Direct execution (TDD cycle)

**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** Strengthened test from Cycle 2.7 should fail

**Expected failure:**
```
AssertionError: expected model names, got empty or hardcoded
```

**Why it fails:** Command doesn't read config

**Verify RED:** Run `pytest tests/test_model.py::test_model_list_output -v`
- Must fail
- If passes, STOP

---

**GREEN Phase:**

**Implementation:** Update model list command to read LiteLLM config

**Changes:**
- File: claudeutils/model/cli.py
  Action: Update list_models() command:
    - Read: LiteLLM config YAML file
    - Parse: model_list entries
    - Output: Model names (and tiers if applicable)

**Verify GREEN:** `pytest tests/test_model.py::test_model_list_output -v`
- Must pass

**Verify no regression:** `pytest tests/test_model.py`
- All tests pass

---

**Expected Outcome**: Command reads config and displays models

**Error Conditions**: RED passes → STOP; GREEN fails → Debug

**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓

**Success Criteria**: Implementation reads config, test passes

**Report Path**: plans/claude-tools-recovery/reports/cycle-3-11-notes.md

---

## Cycle 3.12: Wire model set command to write override file

**Objective**: Write override file with model name

**Script Evaluation**: Direct execution (TDD cycle)

**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** Strengthened test from Cycle 2.8 should fail

**Expected failure:**
```
AssertionError: override file not written
```

**Why it fails:** Command doesn't write file

**Verify RED:** Run `pytest tests/test_model.py::test_model_set_writes_file -v`
- Must fail
- If passes, STOP

---

**GREEN Phase:**

**Implementation:** Update model set command to write override file

**Changes:**
- File: claudeutils/model/cli.py
  Action: Update set_model() command:
    - Write: Override file path with model name
    - Output: Confirmation message

**Verify GREEN:** `pytest tests/test_model.py::test_model_set_writes_file -v`
- Must pass

**Verify no regression:** `pytest tests/test_model.py`
- All tests pass

---

**Expected Outcome**: Command writes override file

**Error Conditions**: RED passes → STOP; GREEN fails → Debug

**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓

**Success Criteria**: Implementation writes file, test passes

**Report Path**: plans/claude-tools-recovery/reports/cycle-3-12-notes.md

---

## Cycle 3.13: Wire model reset command to delete override file

**Objective**: Delete override file

**Script Evaluation**: Direct execution (TDD cycle)

**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** Strengthened test from Cycle 2.9 should fail

**Expected failure:**
```
AssertionError: file still exists
```

**Why it fails:** Command doesn't delete file

**Verify RED:** Run `pytest tests/test_model.py::test_model_reset_deletes_file -v`
- Must fail
- If passes, STOP

---

**GREEN Phase:**

**Implementation:** Update model reset command to delete override file

**Changes:**
- File: claudeutils/model/cli.py
  Action: Update reset_model() command:
    - Delete: Override file if exists
    - Output: Confirmation message

**Verify GREEN:** `pytest tests/test_model.py::test_model_reset_deletes_file -v`
- Must pass

**Verify no regression:** `pytest tests/test_model.py`
- All tests pass

---

**Expected Outcome**: Command deletes override file

**Error Conditions**: RED passes → STOP; GREEN fails → Debug

**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓

**Success Criteria**: Implementation deletes file, test passes

**Report Path**: plans/claude-tools-recovery/reports/cycle-3-13-notes.md

---

## Cycle 3.14: Wire statusline command to format JSON input

**Objective**: Read stdin JSON and output ANSI-formatted statusline

**Script Evaluation**: Direct execution (TDD cycle)

**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** Strengthened test from Cycle 2.10 should fail

**Expected failure:**
```
AssertionError: expected ANSI codes, got "OK"
```

**Why it fails:** Command returns stub

**Verify RED:** Run `pytest tests/test_statusline.py::test_statusline_formats_json -v`
- Must fail
- If passes, STOP

---

**GREEN Phase:**

**Implementation:** Update statusline command to read stdin and format with StatuslineFormatter

**Changes:**
- File: claudeutils/statusline/cli.py
  Action: Update statusline() command:
    - Read: sys.stdin or Click input
    - Parse: JSON to dict
    - Call: StatuslineFormatter.format(data)
    - Output: ANSI-formatted result

**Verify GREEN:** `pytest tests/test_statusline.py::test_statusline_formats_json -v`
- Must pass

**Verify no regression:** `pytest tests/test_statusline.py`
- All tests pass

---

**Expected Outcome**: Command reads JSON and outputs ANSI

**Error Conditions**: RED passes → STOP; GREEN fails → Debug

**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓

**Success Criteria**: Implementation formats JSON, test passes

**Report Path**: plans/claude-tools-recovery/reports/cycle-3-14-notes.md

---

**Checkpoint**

1. Fix: Run `just dev`. Sonnet quiet-task fixes failures. Commit when green.
2. Vet: Review implementation quality (error handling, edge cases). Commit fixes.
3. Functional review: Verify all I/O wired (filesystem, keychain, stdin). Check for remaining stubs.

---

## Phase R4: Error handling and integration tests

## Cycle 4.1: Test keychain not accessible error

**Objective**: Verify clear error message when keychain unavailable

**Script Evaluation**: Direct execution (TDD cycle)

**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** Test Keychain operations raise clear error when security command unavailable

**Expected failure:**
```
FAILED - Expected KeychainError with clear message, got generic error
```

**Why it fails:** Error handling not implemented

**Verify RED:** Run `pytest tests/test_account.py::test_keychain_unavailable -v`
- Must fail
- If passes, STOP

---

**GREEN Phase:**

**Implementation:** Catch subprocess errors and raise KeychainError with helpful message

**Changes:**
- File: claudeutils/account/keychain.py
  Action: Update Keychain.find():
    - Catch: FileNotFoundError (security not found)
    - Raise: KeychainError("macOS keychain not available. Are you on macOS?")

**Verify GREEN:** `pytest tests/test_account.py::test_keychain_unavailable -v`
- Must pass

**Verify no regression:** `pytest tests/test_account.py`
- All tests pass

---

**Expected Outcome**: Clear error message for missing keychain

**Error Conditions**: RED passes → STOP; GREEN fails → Debug

**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓

**Success Criteria**: Error message is clear and helpful

**Report Path**: plans/claude-tools-recovery/reports/cycle-4-1-notes.md

---

## Cycle 4.2: Test config files missing defaults

**Objective**: Verify sensible defaults when account config files don't exist

**Script Evaluation**: Direct execution (TDD cycle)

**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** Test AccountState with missing config files returns defaults

**Expected failure:**
```
FAILED - Expected default mode, got error or crash
```

**Why it fails:** Default handling not implemented

**Verify RED:** Run `pytest tests/test_account.py::test_missing_config_defaults -v`
- Must fail
- If passes, STOP

---

**GREEN Phase:**

**Implementation:** Return defaults when config files missing

**Changes:**
- File: claudeutils/account/state.py
  Action: Update create_account_state():
    - Catch: FileNotFoundError when reading mode/provider files
    - Default: mode="plan", provider="anthropic" (or None with clear indication)

**Verify GREEN:** `pytest tests/test_account.py::test_missing_config_defaults -v`
- Must pass

**Verify no regression:** `pytest tests/test_account.py`
- All tests pass

---

**Expected Outcome**: Sensible defaults when files missing

**Error Conditions**: RED passes → STOP; GREEN fails → Debug

**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓

**Success Criteria**: Defaults allow account status to work

**Report Path**: plans/claude-tools-recovery/reports/cycle-4-2-notes.md

---

## Cycle 4.3: Test invalid JSON on statusline stdin

**Objective**: Verify error message (not crash) on invalid JSON

**Script Evaluation**: Direct execution (TDD cycle)

**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** Test statusline with invalid JSON input shows error

**Expected failure:**
```
FAILED - Expected error message, got crash or unclear output
```

**Why it fails:** JSON error handling not implemented

**Verify RED:** Run `pytest tests/test_statusline.py::test_statusline_invalid_json -v`
- Must fail
- If passes, STOP

---

**GREEN Phase:**

**Implementation:** Catch JSON parse errors and show clear message

**Changes:**
- File: claudeutils/statusline/cli.py
  Action: Update statusline():
    - Catch: json.JSONDecodeError
    - Output: "Error: Invalid JSON input" with exit code 1

**Verify GREEN:** `pytest tests/test_statusline.py::test_statusline_invalid_json -v`
- Must pass

**Verify no regression:** `pytest tests/test_statusline.py`
- All tests pass

---

**Expected Outcome**: Clear error on invalid JSON

**Error Conditions**: RED passes → STOP; GREEN fails → Debug

**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓

**Success Criteria**: Error message is clear, non-zero exit

**Report Path**: plans/claude-tools-recovery/reports/cycle-4-3-notes.md

---

## Cycle 4.4: Test provider missing keychain entry error

**Objective**: Verify clear error with setup instructions when API key missing

**Script Evaluation**: Direct execution (TDD cycle)

**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** Test account api with missing provider keychain shows setup instructions

**Expected failure:**
```
FAILED - Expected setup instructions, got generic error
```

**Why it fails:** Error message not helpful

**Verify RED:** Run `pytest tests/test_account.py::test_missing_provider_key -v`
- Must fail
- If passes, STOP

---

**GREEN Phase:**

**Implementation:** Catch KeychainError and show setup instructions

**Changes:**
- File: claudeutils/account/cli.py
  Action: Update api() command:
    - Catch: KeychainError when getting provider credentials
    - Output: "API key not found. Run: claudeutils account add-key --provider <name>"

**Verify GREEN:** `pytest tests/test_account.py::test_missing_provider_key -v`
- Must pass

**Verify no regression:** `pytest tests/test_account.py`
- All tests pass

---

**Expected Outcome**: Clear setup instructions on missing key

**Error Conditions**: RED passes → STOP; GREEN fails → Debug

**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓

**Success Criteria**: Error includes actionable setup command

**Report Path**: plans/claude-tools-recovery/reports/cycle-4-4-notes.md

---

## Cycle 4.5: Integration test - full account status flow

**Objective**: End-to-end test with mocked filesystem and keychain

**Script Evaluation**: Direct execution (TDD cycle)

**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** Full account status flow with all components

**Expected failure:**
```
AssertionError: integration not complete (one component still stubbed)
```

**Why it fails:** Not all wiring complete until previous cycles

**Verify RED:** Run `pytest tests/test_account.py::test_account_status_integration -v`
- Must fail (at least one assertion fails)
- If passes, STOP

---

**GREEN Phase:**

**Implementation:** Create comprehensive integration test

**Changes:**
- File: tests/test_account.py
  Action: Create test_account_status_integration:
    - Fixture: tmp_path with mode, provider, .env files
    - Mock: Path.home() → tmp_path
    - Mock: Keychain queries (OAuth present, API key present)
    - Run: `account status`
    - Assert: Output contains mode, provider, OAuth status, API key status
    - Assert: Output contains consistency validation results

**Verify GREEN:** `pytest tests/test_account.py::test_account_status_integration -v`
- Must pass

**Verify no regression:** `pytest tests/test_account.py`
- All tests pass

---

**Expected Outcome**: Full account status flow works end-to-end

**Error Conditions**: RED passes → STOP (wiring incomplete); GREEN fails → Debug

**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓

**Success Criteria**: All components integrated, realistic flow

**Report Path**: plans/claude-tools-recovery/reports/cycle-4-5-notes.md

---

## Cycle 4.6: Integration test - account mode switching round-trip

**Objective**: Test plan → api → plan mode switches preserve state

**Script Evaluation**: Direct execution (TDD cycle)

**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** Switch plan → api → plan and verify state consistency

**Expected failure:**
```
AssertionError: round-trip state inconsistent
```

**Why it fails:** Integration not complete

**Verify RED:** Run `pytest tests/test_account.py::test_account_mode_roundtrip -v`
- Must fail
- If passes, STOP

---

**GREEN Phase:**

**Implementation:** Create round-trip integration test

**Changes:**
- File: tests/test_account.py
  Action: Create test_account_mode_roundtrip:
    - Fixture: tmp_path
    - Mock: Path.home() → tmp_path
    - Mock: Keychain (provider credentials)
    - Run: `account plan`
    - Assert: Mode file == "plan"
    - Run: `account api`
    - Assert: Mode file == "api", .env exists with credentials
    - Run: `account plan`
    - Assert: Mode file == "plan", .env still exists (or removed depending on design)

**Verify GREEN:** `pytest tests/test_account.py::test_account_mode_roundtrip -v`
- Must pass

**Verify no regression:** `pytest tests/test_account.py`
- All tests pass

---

**Expected Outcome**: Mode switching works bidirectionally

**Error Conditions**: RED passes → STOP; GREEN fails → Debug

**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓

**Success Criteria**: Round-trip preserves state correctly

**Report Path**: plans/claude-tools-recovery/reports/cycle-4-6-notes.md

---

## Cycle 4.7: Integration test - model override flow

**Objective**: Test set → list → reset model override

**Script Evaluation**: Direct execution (TDD cycle)

**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** Full model override lifecycle

**Expected failure:**
```
AssertionError: override not visible in list or not cleared by reset
```

**Why it fails:** Integration not complete

**Verify RED:** Run `pytest tests/test_model.py::test_model_override_flow -v`
- Must fail
- If passes, STOP

---

**GREEN Phase:**

**Implementation:** Create model override integration test

**Changes:**
- File: tests/test_model.py
  Action: Create test_model_override_flow:
    - Fixture: tmp_path for override file and config
    - Mock: Config and override paths
    - Run: `model set claude-opus-4`
    - Assert: Override file exists with model name
    - Run: `model list`
    - Assert: Output shows override is active (if design includes this)
    - Run: `model reset`
    - Assert: Override file deleted
    - Run: `model list`
    - Assert: No override shown

**Verify GREEN:** `pytest tests/test_model.py::test_model_override_flow -v`
- Must pass

**Verify no regression:** `pytest tests/test_model.py`
- All tests pass

---

**Expected Outcome**: Full model override lifecycle works

**Error Conditions**: RED passes → STOP; GREEN fails → Debug

**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓

**Success Criteria**: Set/list/reset flow is consistent

**Report Path**: plans/claude-tools-recovery/reports/cycle-4-7-notes.md

---

## Cycle 4.8: Integration test - statusline with realistic JSON

**Objective**: Test statusline with realistic statusline JSON input

**Script Evaluation**: Direct execution (TDD cycle)

**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** Statusline with complete JSON structure

**Expected failure:**
```
AssertionError: realistic JSON not formatted correctly
```

**Why it fails:** Edge cases in formatting not handled

**Verify RED:** Run `pytest tests/test_statusline.py::test_statusline_realistic_json -v`
- Must fail
- If passes, STOP

---

**GREEN Phase:**

**Implementation:** Create realistic statusline integration test

**Changes:**
- File: tests/test_statusline.py
  Action: Create test_statusline_realistic_json:
    - Fixture: JSON with mode, provider, usage stats, plan stats, API stats (realistic structure)
    - Run: `statusline` with fixture input
    - Assert: Output contains ANSI codes
    - Assert: Output is formatted (not just JSON dump)
    - Assert: All fields represented in output

**Verify GREEN:** `pytest tests/test_statusline.py::test_statusline_realistic_json -v`
- Must pass

**Verify no regression:** `pytest tests/test_statusline.py`
- All tests pass

---

**Expected Outcome**: Statusline handles realistic JSON

**Error Conditions**: RED passes → STOP; GREEN fails → Debug

**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓

**Success Criteria**: Realistic input produces formatted output

**Report Path**: plans/claude-tools-recovery/reports/cycle-4-8-notes.md

---

**Checkpoint**

1. Fix: Run `just dev`. Sonnet quiet-task fixes failures. Commit when green.
2. Vet: Review error handling and integration tests. Commit fixes.
3. Functional review: Verify all features functional with real I/O. Test CLI commands manually if possible.

---

## Design Decisions

**1. Approach: Strengthen tests then wire**
- Choice: Phase R1/R2 strengthen tests, R3 wires implementations
- Rationale: Strengthened tests create natural RED phase, dogfoods improved plan-tdd skill

**2. Phase R0 deletes before strengthening**
- Choice: Remove vacuous tests first
- Rationale: Reduces noise, clarifies what needs behavioral assertions

**3. Statusline display modules deferred**
- Choice: Skip display.py, context.py, plan_usage.py, api_usage.py
- Rationale: Complex formatting needs separate design, focus on I/O wiring first

**4. Mock strategy: patch at usage location**
- Choice: `patch("claudeutils.account.state.subprocess.run")`
- Rationale: More precise, consistent with project patterns

## Dependencies

**Before:**
- Skill improvements from plans/skill-improvements/design.md applied
- Branch: tools-rewrite, commit b40e34e (all tests pass but stubbed)

**After:**
- CLI commands functional with real I/O
- Statusline display modules (follow-up design)
- Shell script deprecation (replace with Python CLI)
