---
name: claude-tools-rewrite
type: tdd
model: haiku
---

# Claude Tools Rewrite - Python Implementation TDD Runbook

**Context**: Implement account, model, and statusline modules in claudeutils package with full test coverage, replacing ~2000 lines of untested shell scripts

**Design**: plans/claude-tools-rewrite/design.md
**Status**: Draft
**Created**: 2026-01-30
**Repository**: /Users/david/code/claudeutils/

## Weak Orchestrator Metadata

**Total Steps**: 45 cycles across 3 phases
**Execution Model**: All cycles: Haiku (TDD execution)
**Step Dependencies**: Sequential within phases, some cross-phase dependencies
**Error Escalation**: Haiku → User on stop conditions/regression
**Report Locations**: plans/claude-tools-rewrite/reports/
**Success Criteria**: All cycles GREEN, no regressions, Python modules complete
**Prerequisites**:
- claudeutils package installed in development mode
- pytest, mypy, ruff configured
- Access to ~/.claude/ directory for integration tests

## Common Context

**Key Design Decisions:**

1. **Pydantic AccountState model** - Replace scattered file reads with single state object having `validate_consistency()` returning list of issues
2. **Provider as Protocol** - Strategy pattern for anthropic/openrouter/litellm with per-provider env vars and validation
3. **LiteLLM config structured parsing** - Regex-based YAML parsing (no PyYAML for this file), Decimal pricing
4. **Keychain via subprocess** - Wrap `security` commands, mockable via subprocess.run patches
5. **Statusline ANSI formatter** - Separate formatting from data fetching for testability
6. **LaunchAgent via plistlib** - Fixes heredoc bug, structured data output
7. **Usage API caching** - 30-second TTL cache, separate from API call
8. **Shell wrappers delegation** - Thin bash scripts in home repo delegate to claudeutils CLI

**TDD Protocol:**

Strict RED-GREEN-REFACTOR: 1) RED: Write failing test, 2) Verify RED, 3) GREEN: Minimal implementation, 4) Verify GREEN, 5) Verify Regression, 6) REFACTOR (optional)

**Project Paths:**

- Source: `src/claudeutils/`
- Tests: `tests/`
- State files: `~/.claude/` (account-mode, account-config.json, claude-env, etc.)

**Conventions:**

- Use Read/Write/Edit/Grep tools (not Bash for file ops)
- Report errors explicitly (never suppress)
- Write notes to plans/claude-tools-rewrite/reports/cycle-{X}-{Y}-notes.md
- Patch at usage location, not definition location
- Target ~/.claude/ files with tmp_path fixtures for integration tests

**Stop Conditions (all cycles):**

STOP IMMEDIATELY if: RED phase test passes (expected failure) • RED phase failure message doesn't match expected • GREEN phase tests don't pass after implementation • Any phase existing tests break (regression)

Actions when stopped: 1) Document in reports/cycle-{X}-{Y}-notes.md 2) Test passes unexpectedly → Investigate if feature exists 3) Regression → STOP, report broken tests 4) Scope unclear → STOP, document ambiguity

**Dependencies:**

Sequential within each phase by default. Cross-phase dependencies marked with [DEPENDS: X.Y].

---

## Phase 1: Account Module Foundation

### Cycle 1.1: Create account module structure

**Objective**: Set up account module package with __init__.py
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** Account module can be imported

**Expected failure:**
```
ModuleNotFoundError: No module named 'claudeutils.account'
```

**Why it fails:** Module doesn't exist yet

**Verify RED:** `pytest tests/test_account_structure.py::test_account_module_importable -xvs`
- Must fail with ModuleNotFoundError
- If passes, STOP - module may already exist

---

**GREEN Phase:**

**Implementation:** Create empty account module

**Changes:**
- File: src/claudeutils/account/__init__.py
  Action: Create empty file
- File: tests/test_account_structure.py
  Action: Create test that imports claudeutils.account

**Verify GREEN:** `pytest tests/test_account_structure.py::test_account_module_importable -xvs`
- Must pass

**Verify no regression:** `pytest`
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/claude-tools-rewrite/reports/cycle-1-1-notes.md

---

### Cycle 1.2: AccountState model basic structure

**Objective**: Create AccountState Pydantic model with core fields
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** AccountState model can be instantiated with required fields

**Expected failure:**
```
AttributeError: module 'claudeutils.account' has no attribute 'AccountState'
```

**Why it fails:** AccountState class doesn't exist

**Verify RED:** `pytest tests/test_account_state.py::test_account_state_creation -xvs`
- Must fail with AttributeError
- If passes, STOP - class may already exist

---

**GREEN Phase:**

**Implementation:** Create AccountState model with mode, provider, boolean flags

**Changes:**
- File: src/claudeutils/account/state.py
  Action: Create AccountState(BaseModel) with fields: mode, provider, oauth_in_keychain, api_in_claude_env, base_url, has_api_key_helper, litellm_proxy_running
- File: src/claudeutils/account/__init__.py
  Action: Add `from .state import AccountState`
- File: tests/test_account_state.py
  Action: Create test instantiating AccountState with valid values

**Verify GREEN:** `pytest tests/test_account_state.py::test_account_state_creation -xvs`
- Must pass

**Verify no regression:** `pytest`
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/claude-tools-rewrite/reports/cycle-1-2-notes.md

---

### Cycle 1.3: AccountState validation - empty issues

**Objective**: Add validate_consistency() method returning empty list for consistent state
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** AccountState.validate_consistency() returns empty list for valid plan mode with anthropic

**Expected failure:**
```
AttributeError: 'AccountState' object has no attribute 'validate_consistency'
```

**Why it fails:** Method doesn't exist

**Verify RED:** `pytest tests/test_account_state.py::test_validate_consistency_valid_state -xvs`
- Must fail with AttributeError
- If passes, STOP - method may already exist

---

**GREEN Phase:**

**Implementation:** Add validate_consistency() method stub returning empty list

**Changes:**
- File: src/claudeutils/account/state.py
  Action: Add `def validate_consistency(self) -> list[str]: return []`
- File: tests/test_account_state.py
  Action: Test that valid AccountState returns empty list from validate_consistency()

**Verify GREEN:** `pytest tests/test_account_state.py::test_validate_consistency_valid_state -xvs`
- Must pass

**Verify no regression:** `pytest`
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/claude-tools-rewrite/reports/cycle-1-3-notes.md

---

### Cycle 1.4: AccountState validation - plan mode requires OAuth

**Objective**: Detect inconsistency when mode=plan but oauth_in_keychain=False
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** validate_consistency() returns issue when plan mode missing OAuth

**Expected failure:**
```
AssertionError: assert [] == ['Plan mode requires OAuth credentials in keychain']
```

**Why it fails:** validate_consistency() returns empty list (stub)

**Verify RED:** `pytest tests/test_account_state.py::test_validate_plan_requires_oauth -xvs`
- Must fail with assertion mismatch
- If passes, STOP - validation may already exist

---

**GREEN Phase:**

**Implementation:** Add plan mode OAuth validation check

**Changes:**
- File: src/claudeutils/account/state.py
  Action: In validate_consistency(), add check: if mode == "plan" and not oauth_in_keychain, append issue
- File: tests/test_account_state.py
  Action: Test plan mode with oauth_in_keychain=False returns specific issue

**Verify GREEN:** `pytest tests/test_account_state.py::test_validate_plan_requires_oauth -xvs`
- Must pass

**Verify no regression:** `pytest`
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/claude-tools-rewrite/reports/cycle-1-4-notes.md

---

### Cycle 1.5: AccountState validation - API mode requires key

**Objective**: Detect inconsistency when mode=api but no API key available
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** validate_consistency() returns issue when API mode without key

**Expected failure:**
```
AssertionError: assert [] == ['API mode requires API key in environment or helper enabled']
```

**Why it fails:** API mode validation not implemented

**Verify RED:** `pytest tests/test_account_state.py::test_validate_api_requires_key -xvs`
- Must fail with assertion mismatch
- If passes, STOP - validation may already exist

---

**GREEN Phase:**

**Implementation:** Add API mode key validation check

**Changes:**
- File: src/claudeutils/account/state.py
  Action: In validate_consistency(), add check: if mode == "api" and not (api_in_claude_env or has_api_key_helper), append issue
- File: tests/test_account_state.py
  Action: Test API mode without key or helper returns specific issue

**Verify GREEN:** `pytest tests/test_account_state.py::test_validate_api_requires_key -xvs`
- Must pass

**Verify no regression:** `pytest`
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/claude-tools-rewrite/reports/cycle-1-5-notes.md

---

### Cycle 1.6: AccountState validation - LiteLLM requires proxy

**Objective**: Detect inconsistency when provider=litellm but proxy not running
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** validate_consistency() returns issue when LiteLLM provider without proxy

**Expected failure:**
```
AssertionError: assert [] == ['LiteLLM provider requires proxy to be running']
```

**Why it fails:** LiteLLM provider validation not implemented

**Verify RED:** `pytest tests/test_account_state.py::test_validate_litellm_requires_proxy -xvs`
- Must fail with assertion mismatch
- If passes, STOP - validation may already exist

---

**GREEN Phase:**

**Implementation:** Add LiteLLM proxy validation check

**Changes:**
- File: src/claudeutils/account/state.py
  Action: In validate_consistency(), add check: if provider == "litellm" and not litellm_proxy_running, append issue
- File: tests/test_account_state.py
  Action: Test LiteLLM provider without proxy returns specific issue

**Verify GREEN:** `pytest tests/test_account_state.py::test_validate_litellm_requires_proxy -xvs`
- Must pass

**Verify no regression:** `pytest`
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/claude-tools-rewrite/reports/cycle-1-6-notes.md

---

### Cycle 1.7: Provider Protocol definition

**Objective**: Define Provider Protocol with name, claude_env_vars, validate, settings_json_patch methods
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** Provider Protocol can be used as type annotation

**Expected failure:**
```
AttributeError: module 'claudeutils.account' has no attribute 'Provider'
```

**Why it fails:** Provider Protocol doesn't exist

**Verify RED:** `pytest tests/test_account_providers.py::test_provider_protocol_exists -xvs`
- Must fail with AttributeError
- If passes, STOP - protocol may already exist

---

**GREEN Phase:**

**Implementation:** Create Provider Protocol with method signatures

**Changes:**
- File: src/claudeutils/account/providers.py
  Action: Create Provider Protocol with name: str, claude_env_vars(), validate(), settings_json_patch() methods
- File: src/claudeutils/account/__init__.py
  Action: Add `from .providers import Provider`
- File: tests/test_account_providers.py
  Action: Test that Provider can be imported and used in type annotation

**Verify GREEN:** `pytest tests/test_account_providers.py::test_provider_protocol_exists -xvs`
- Must pass

**Verify no regression:** `pytest`
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/claude-tools-rewrite/reports/cycle-1-7-notes.md

---

### Cycle 1.8: AnthropicProvider implementation

**Objective**: Implement AnthropicProvider with claude_env_vars returning ANTHROPIC_API_KEY
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** AnthropicProvider.claude_env_vars() returns ANTHROPIC_API_KEY from keychain

**Expected failure:**
```
AttributeError: module 'claudeutils.account.providers' has no attribute 'AnthropicProvider'
```

**Why it fails:** AnthropicProvider class doesn't exist

**Verify RED:** `pytest tests/test_account_providers.py::test_anthropic_provider_env_vars -xvs`
- Must fail with AttributeError
- If passes, STOP - class may already exist

---

**GREEN Phase:**

**Implementation:** Create AnthropicProvider class implementing Provider

**Changes:**
- File: src/claudeutils/account/providers.py
  Action: Create AnthropicProvider class with name="anthropic", claude_env_vars() returning {"ANTHROPIC_API_KEY": key}
- File: src/claudeutils/account/__init__.py
  Action: Add `from .providers import AnthropicProvider`
- File: tests/test_account_providers.py
  Action: Test AnthropicProvider.claude_env_vars() with mock KeyStore

**Verify GREEN:** `pytest tests/test_account_providers.py::test_anthropic_provider_env_vars -xvs`
- Must pass

**Verify no regression:** `pytest`
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/claude-tools-rewrite/reports/cycle-1-8-notes.md

---

### Cycle 1.9: OpenRouterProvider implementation

**Objective**: Implement OpenRouterProvider with OPENROUTER_API_KEY and ANTHROPIC_BASE_URL
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** OpenRouterProvider.claude_env_vars() returns both API key and base URL

**Expected failure:**
```
AttributeError: module 'claudeutils.account.providers' has no attribute 'OpenRouterProvider'
```

**Why it fails:** OpenRouterProvider class doesn't exist

**Verify RED:** `pytest tests/test_account_providers.py::test_openrouter_provider_env_vars -xvs`
- Must fail with AttributeError
- If passes, STOP - class may already exist

---

**GREEN Phase:**

**Implementation:** Create OpenRouterProvider class

**Changes:**
- File: src/claudeutils/account/providers.py
  Action: Create OpenRouterProvider with claude_env_vars() returning OPENROUTER_API_KEY and ANTHROPIC_BASE_URL
- File: src/claudeutils/account/__init__.py
  Action: Add `from .providers import OpenRouterProvider`
- File: tests/test_account_providers.py
  Action: Test OpenRouterProvider.claude_env_vars() includes both env vars

**Verify GREEN:** `pytest tests/test_account_providers.py::test_openrouter_provider_env_vars -xvs`
- Must pass

**Verify no regression:** `pytest`
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/claude-tools-rewrite/reports/cycle-1-9-notes.md

---

### Cycle 1.10: LiteLLMProvider implementation

**Objective**: Implement LiteLLMProvider with LITELLM_API_KEY and base URL
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** LiteLLMProvider.claude_env_vars() returns LiteLLM-specific variables

**Expected failure:**
```
AttributeError: module 'claudeutils.account.providers' has no attribute 'LiteLLMProvider'
```

**Why it fails:** LiteLLMProvider class doesn't exist

**Verify RED:** `pytest tests/test_account_providers.py::test_litellm_provider_env_vars -xvs`
- Must fail with AttributeError
- If passes, STOP - class may already exist

---

**GREEN Phase:**

**Implementation:** Create LiteLLMProvider class

**Changes:**
- File: src/claudeutils/account/providers.py
  Action: Create LiteLLMProvider with claude_env_vars() returning appropriate env vars
- File: src/claudeutils/account/__init__.py
  Action: Add `from .providers import LiteLLMProvider`
- File: tests/test_account_providers.py
  Action: Test LiteLLMProvider.claude_env_vars() returns expected variables

**Verify GREEN:** `pytest tests/test_account_providers.py::test_litellm_provider_env_vars -xvs`
- Must pass

**Verify no regression:** `pytest`
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/claude-tools-rewrite/reports/cycle-1-10-notes.md

---

### Cycle 1.11: Keychain wrapper - find operation

**Objective**: Implement Keychain.find() wrapping `security find-generic-password`
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** Keychain.find() returns password when keychain entry exists

**Expected failure:**
```
AttributeError: module 'claudeutils.account' has no attribute 'Keychain'
```

**Why it fails:** Keychain class doesn't exist

**Verify RED:** `pytest tests/test_account_keychain.py::test_keychain_find_success -xvs`
- Must fail with AttributeError
- If passes, STOP - class may already exist

---

**GREEN Phase:**

**Implementation:** Create Keychain class with find() method

**Changes:**
- File: src/claudeutils/account/keychain.py
  Action: Create Keychain class with find() calling subprocess.run(["security", "find-generic-password", ...])
- File: src/claudeutils/account/__init__.py
  Action: Add `from .keychain import Keychain`
- File: tests/test_account_keychain.py
  Action: Test find() with mocked subprocess returning success

**Verify GREEN:** `pytest tests/test_account_keychain.py::test_keychain_find_success -xvs`
- Must pass

**Verify no regression:** `pytest`
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/claude-tools-rewrite/reports/cycle-1-11-notes.md

---

### Cycle 1.12: Keychain wrapper - add operation

**Objective**: Implement Keychain.add() wrapping `security add-generic-password`
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** Keychain.add() calls security command with correct arguments

**Expected failure:**
```
AttributeError: 'Keychain' object has no attribute 'add'
```

**Why it fails:** add() method doesn't exist

**Verify RED:** `pytest tests/test_account_keychain.py::test_keychain_add -xvs`
- Must fail with AttributeError
- If passes, STOP - method may already exist

---

**GREEN Phase:**

**Implementation:** Add add() method to Keychain

**Changes:**
- File: src/claudeutils/account/keychain.py
  Action: Add add(account, password) calling subprocess.run(["security", "add-generic-password", ...])
- File: tests/test_account_keychain.py
  Action: Test add() with mocked subprocess, verify command arguments

**Verify GREEN:** `pytest tests/test_account_keychain.py::test_keychain_add -xvs`
- Must pass

**Verify no regression:** `pytest`
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/claude-tools-rewrite/reports/cycle-1-12-notes.md

---

### Cycle 1.13: Keychain wrapper - delete operation

**Objective**: Implement Keychain.delete() wrapping `security delete-generic-password`
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** Keychain.delete() calls security command to remove entry

**Expected failure:**
```
AttributeError: 'Keychain' object has no attribute 'delete'
```

**Why it fails:** delete() method doesn't exist

**Verify RED:** `pytest tests/test_account_keychain.py::test_keychain_delete -xvs`
- Must fail with AttributeError
- If passes, STOP - method may already exist

---

**GREEN Phase:**

**Implementation:** Add delete() method to Keychain

**Changes:**
- File: src/claudeutils/account/keychain.py
  Action: Add delete(account) calling subprocess.run(["security", "delete-generic-password", ...])
- File: tests/test_account_keychain.py
  Action: Test delete() with mocked subprocess

**Verify GREEN:** `pytest tests/test_account_keychain.py::test_keychain_delete -xvs`
- Must pass

**Verify no regression:** `pytest`
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/claude-tools-rewrite/reports/cycle-1-13-notes.md

---

**Checkpoint**
1. Fix: Run `just dev`. Sonnet quiet-task fixes failures. Commit when green.
2. Vet: Review AccountState model design, Provider strategy clarity, Keychain wrapper safety. Commit fixes.

---

## Phase 2: Model Module and Configuration

### Cycle 2.1: Create model module structure

**Objective**: Set up model module package
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** Model module can be imported

**Expected failure:**
```
ModuleNotFoundError: No module named 'claudeutils.model'
```

**Why it fails:** Module doesn't exist yet

**Verify RED:** `pytest tests/test_model_structure.py::test_model_module_importable -xvs`
- Must fail with ModuleNotFoundError
- If passes, STOP - module may already exist

---

**GREEN Phase:**

**Implementation:** Create empty model module

**Changes:**
- File: src/claudeutils/model/__init__.py
  Action: Create empty file
- File: tests/test_model_structure.py
  Action: Create test that imports claudeutils.model

**Verify GREEN:** `pytest tests/test_model_structure.py::test_model_module_importable -xvs`
- Must pass

**Verify no regression:** `pytest`
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/claude-tools-rewrite/reports/cycle-2-1-notes.md

---

### Cycle 2.2: LiteLLMModel Pydantic model

**Objective**: Create LiteLLMModel with name, litellm_model, tiers, pricing fields
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** LiteLLMModel can be instantiated with required fields

**Expected failure:**
```
AttributeError: module 'claudeutils.model' has no attribute 'LiteLLMModel'
```

**Why it fails:** LiteLLMModel class doesn't exist

**Verify RED:** `pytest tests/test_model_config.py::test_litellm_model_creation -xvs`
- Must fail with AttributeError
- If passes, STOP - class may already exist

---

**GREEN Phase:**

**Implementation:** Create LiteLLMModel Pydantic model

**Changes:**
- File: src/claudeutils/model/config.py
  Action: Create LiteLLMModel(BaseModel) with name, litellm_model, tiers, arena_rank, input_price, output_price, api_key_env, api_base
- File: src/claudeutils/model/__init__.py
  Action: Add `from .config import LiteLLMModel`
- File: tests/test_model_config.py
  Action: Test instantiating LiteLLMModel with valid data

**Verify GREEN:** `pytest tests/test_model_config.py::test_litellm_model_creation -xvs`
- Must pass

**Verify no regression:** `pytest`
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/claude-tools-rewrite/reports/cycle-2-2-notes.md

---

### Cycle 2.3: Parse single model entry from YAML

**Objective**: Parse one model_list entry extracting model_name and litellm_params
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** parse_model_entry() extracts name and litellm_model from YAML entry

**Expected failure:**
```
AttributeError: module 'claudeutils.model.config' has no attribute 'parse_model_entry'
```

**Why it fails:** Function doesn't exist

**Verify RED:** `pytest tests/test_model_config.py::test_parse_model_entry_basic -xvs`
- Must fail with AttributeError
- If passes, STOP - function may already exist

---

**GREEN Phase:**

**Implementation:** Create parse_model_entry() using regex to extract fields

**Changes:**
- File: src/claudeutils/model/config.py
  Action: Create parse_model_entry(yaml_text) using regex for model_name and litellm_params.model
- File: tests/test_model_config.py
  Action: Test with sample YAML entry, verify extracted fields

**Verify GREEN:** `pytest tests/test_model_config.py::test_parse_model_entry_basic -xvs`
- Must pass

**Verify no regression:** `pytest`
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/claude-tools-rewrite/reports/cycle-2-3-notes.md

---

### Cycle 2.4: Parse comment metadata (tiers)

**Objective**: Extract tier tags (haiku, sonnet, opus) from comment line
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** parse_model_entry() extracts tiers from comment

**Expected failure:**
```
AssertionError: assert model.tiers == []
Expected: ['haiku', 'sonnet']
```

**Why it fails:** Tier parsing not implemented

**Verify RED:** `pytest tests/test_model_config.py::test_parse_model_entry_tiers -xvs`
- Must fail with empty tiers
- If passes, STOP - tier parsing may already exist

---

**GREEN Phase:**

**Implementation:** Add tier extraction from comment line

**Changes:**
- File: src/claudeutils/model/config.py
  Action: Extend parse_model_entry() to regex-extract tier tags from comment
- File: tests/test_model_config.py
  Action: Test with entry having "# haiku,sonnet - arena:5" comment

**Verify GREEN:** `pytest tests/test_model_config.py::test_parse_model_entry_tiers -xvs`
- Must pass

**Verify no regression:** `pytest`
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/claude-tools-rewrite/reports/cycle-2-4-notes.md

---

### Cycle 2.5: Parse comment metadata (arena rank and pricing)

**Objective**: Extract arena rank and pricing from comment
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** parse_model_entry() extracts arena_rank, input_price, output_price from comment

**Expected failure:**
```
AssertionError: assert model.arena_rank is None
Expected: 5
```

**Why it fails:** Arena/pricing parsing not implemented

**Verify RED:** `pytest tests/test_model_config.py::test_parse_model_entry_metadata -xvs`
- Must fail with None values
- If passes, STOP - metadata parsing may already exist

---

**GREEN Phase:**

**Implementation:** Add arena rank and pricing extraction

**Changes:**
- File: src/claudeutils/model/config.py
  Action: Extend parse_model_entry() to extract arena:N, $X.XX/$Y.YY from comment
- File: tests/test_model_config.py
  Action: Test with entry having "arena:5 - $0.25/$1.25" in comment

**Verify GREEN:** `pytest tests/test_model_config.py::test_parse_model_entry_metadata -xvs`
- Must pass

**Verify no regression:** `pytest`
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/claude-tools-rewrite/reports/cycle-2-5-notes.md

---

### Cycle 2.6: Load full LiteLLM config file

**Objective**: Read config.yaml and parse all model entries into list[LiteLLMModel]
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** load_litellm_config() returns list of models from YAML file

**Expected failure:**
```
AttributeError: module 'claudeutils.model.config' has no attribute 'load_litellm_config'
```

**Why it fails:** Function doesn't exist

**Verify RED:** `pytest tests/test_model_config.py::test_load_litellm_config -xvs`
- Must fail with AttributeError
- If passes, STOP - function may already exist

---

**GREEN Phase:**

**Implementation:** Create load_litellm_config() reading file and parsing entries

**Changes:**
- File: src/claudeutils/model/config.py
  Action: Create load_litellm_config(path) reading file, splitting on model_list entries, parsing each
- File: tests/test_model_config.py
  Action: Test with tmp_path fixture containing sample config.yaml

**Verify GREEN:** `pytest tests/test_model_config.py::test_load_litellm_config -xvs`
- Must pass

**Verify no regression:** `pytest`
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/claude-tools-rewrite/reports/cycle-2-6-notes.md

---

### Cycle 2.7: Filter models by tier

**Objective**: Add filter_by_tier() returning models matching tier
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** filter_by_tier(models, "haiku") returns only haiku-tier models

**Expected failure:**
```
AttributeError: module 'claudeutils.model.config' has no attribute 'filter_by_tier'
```

**Why it fails:** Function doesn't exist

**Verify RED:** `pytest tests/test_model_config.py::test_filter_by_tier -xvs`
- Must fail with AttributeError
- If passes, STOP - function may already exist

---

**GREEN Phase:**

**Implementation:** Create filter_by_tier() function

**Changes:**
- File: src/claudeutils/model/config.py
  Action: Create filter_by_tier(models, tier) returning [m for m in models if tier in m.tiers]
- File: tests/test_model_config.py
  Action: Test filtering list of models by tier

**Verify GREEN:** `pytest tests/test_model_config.py::test_filter_by_tier -xvs`
- Must pass

**Verify no regression:** `pytest`
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/claude-tools-rewrite/reports/cycle-2-7-notes.md

---

### Cycle 2.8: Model override file read

**Objective**: Read claude-model-overrides file returning env var dict
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** read_overrides() parses bash env var file into dict

**Expected failure:**
```
AttributeError: module 'claudeutils.model' has no attribute 'read_overrides'
```

**Why it fails:** Function doesn't exist

**Verify RED:** `pytest tests/test_model_overrides.py::test_read_overrides -xvs`
- Must fail with AttributeError
- If passes, STOP - function may already exist

---

**GREEN Phase:**

**Implementation:** Create read_overrides() in overrides.py

**Changes:**
- File: src/claudeutils/model/overrides.py
  Action: Create read_overrides(path) parsing "export VAR=value" lines
- File: src/claudeutils/model/__init__.py
  Action: Add `from .overrides import read_overrides`
- File: tests/test_model_overrides.py
  Action: Test with tmp_path fixture containing sample override file

**Verify GREEN:** `pytest tests/test_model_overrides.py::test_read_overrides -xvs`
- Must pass

**Verify no regression:** `pytest`
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/claude-tools-rewrite/reports/cycle-2-8-notes.md

---

### Cycle 2.9: Model override file write

**Objective**: Write env var dict to claude-model-overrides file
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** write_overrides() writes dict as bash export statements

**Expected failure:**
```
AttributeError: module 'claudeutils.model.overrides' has no attribute 'write_overrides'
```

**Why it fails:** Function doesn't exist

**Verify RED:** `pytest tests/test_model_overrides.py::test_write_overrides -xvs`
- Must fail with AttributeError
- If passes, STOP - function may already exist

---

**GREEN Phase:**

**Implementation:** Create write_overrides() function

**Changes:**
- File: src/claudeutils/model/overrides.py
  Action: Create write_overrides(path, vars) writing "export KEY=value\n" lines
- File: tests/test_model_overrides.py
  Action: Test with tmp_path, verify file format

**Verify GREEN:** `pytest tests/test_model_overrides.py::test_write_overrides -xvs`
- Must pass

**Verify no regression:** `pytest`
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/claude-tools-rewrite/reports/cycle-2-9-notes.md

---

**Checkpoint**
1. Fix: Run `just dev`. Sonnet quiet-task fixes failures. Commit when green.
2. Vet: Review LiteLLM config parsing robustness, override file format correctness. Commit fixes.

---

## Phase 3: Statusline Module and CLI Integration

### Cycle 3.1: Create statusline module structure

**Objective**: Set up statusline module package
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** Statusline module can be imported

**Expected failure:**
```
ModuleNotFoundError: No module named 'claudeutils.statusline'
```

**Why it fails:** Module doesn't exist yet

**Verify RED:** `pytest tests/test_statusline_structure.py::test_statusline_module_importable -xvs`
- Must fail with ModuleNotFoundError
- If passes, STOP - module may already exist

---

**GREEN Phase:**

**Implementation:** Create empty statusline module

**Changes:**
- File: src/claudeutils/statusline/__init__.py
  Action: Create empty file
- File: tests/test_statusline_structure.py
  Action: Create test that imports claudeutils.statusline

**Verify GREEN:** `pytest tests/test_statusline_structure.py::test_statusline_module_importable -xvs`
- Must pass

**Verify no regression:** `pytest`
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/claude-tools-rewrite/reports/cycle-3-1-notes.md

---

### Cycle 3.2: StatuslineFormatter - colored text

**Objective**: Implement colored() method returning ANSI-wrapped text
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** StatuslineFormatter.colored() wraps text in ANSI color codes

**Expected failure:**
```
AttributeError: module 'claudeutils.statusline' has no attribute 'StatuslineFormatter'
```

**Why it fails:** StatuslineFormatter class doesn't exist

**Verify RED:** `pytest tests/test_statusline_display.py::test_colored_text -xvs`
- Must fail with AttributeError
- If passes, STOP - class may already exist

---

**GREEN Phase:**

**Implementation:** Create StatuslineFormatter with colored() method

**Changes:**
- File: src/claudeutils/statusline/display.py
  Action: Create StatuslineFormatter class with colored(text, color) returning ANSI-wrapped text
- File: src/claudeutils/statusline/__init__.py
  Action: Add `from .display import StatuslineFormatter`
- File: tests/test_statusline_display.py
  Action: Test colored() with various colors, verify ANSI codes

**Verify GREEN:** `pytest tests/test_statusline_display.py::test_colored_text -xvs`
- Must pass

**Verify no regression:** `pytest`
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/claude-tools-rewrite/reports/cycle-3-2-notes.md

---

### Cycle 3.3: StatuslineFormatter - token bar

**Objective**: Implement token_bar() returning Unicode block progress bar
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** StatuslineFormatter.token_bar() generates progress bar with Unicode blocks

**Expected failure:**
```
AttributeError: 'StatuslineFormatter' object has no attribute 'token_bar'
```

**Why it fails:** token_bar() method doesn't exist

**Verify RED:** `pytest tests/test_statusline_display.py::test_token_bar -xvs`
- Must fail with AttributeError
- If passes, STOP - method may already exist

---

**GREEN Phase:**

**Implementation:** Add token_bar() method

**Changes:**
- File: src/claudeutils/statusline/display.py
  Action: Add token_bar(tokens, max_tokens) calculating percentage and rendering Unicode blocks
- File: tests/test_statusline_display.py
  Action: Test token_bar() with various values, verify block characters and colors

**Verify GREEN:** `pytest tests/test_statusline_display.py::test_token_bar -xvs`
- Must pass

**Verify no regression:** `pytest`
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/claude-tools-rewrite/reports/cycle-3-3-notes.md

---

### Cycle 3.4: StatuslineFormatter - vertical bar

**Objective**: Implement vertical_bar() for usage percentage display
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** StatuslineFormatter.vertical_bar() generates vertical bar character

**Expected failure:**
```
AttributeError: 'StatuslineFormatter' object has no attribute 'vertical_bar'
```

**Why it fails:** vertical_bar() method doesn't exist

**Verify RED:** `pytest tests/test_statusline_display.py::test_vertical_bar -xvs`
- Must fail with AttributeError
- If passes, STOP - method may already exist

---

**GREEN Phase:**

**Implementation:** Add vertical_bar() method

**Changes:**
- File: src/claudeutils/statusline/display.py
  Action: Add vertical_bar(percentage) returning colored vertical bar based on percentage
- File: tests/test_statusline_display.py
  Action: Test vertical_bar() with various percentages, verify colors

**Verify GREEN:** `pytest tests/test_statusline_display.py::test_vertical_bar -xvs`
- Must pass

**Verify no regression:** `pytest`
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/claude-tools-rewrite/reports/cycle-3-4-notes.md

---

### Cycle 3.5: StatuslineFormatter - limit display

**Objective**: Implement limit_display() formatting name, percentage, reset time
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** StatuslineFormatter.limit_display() formats limit info with colors

**Expected failure:**
```
AttributeError: 'StatuslineFormatter' object has no attribute 'limit_display'
```

**Why it fails:** limit_display() method doesn't exist

**Verify RED:** `pytest tests/test_statusline_display.py::test_limit_display -xvs`
- Must fail with AttributeError
- If passes, STOP - method may already exist

---

**GREEN Phase:**

**Implementation:** Add limit_display() method

**Changes:**
- File: src/claudeutils/statusline/display.py
  Action: Add limit_display(name, pct, reset) formatting string with vertical bar and colored reset time
- File: tests/test_statusline_display.py
  Action: Test limit_display() with various inputs, verify format

**Verify GREEN:** `pytest tests/test_statusline_display.py::test_limit_display -xvs`
- Must pass

**Verify no regression:** `pytest`
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/claude-tools-rewrite/reports/cycle-3-5-notes.md

---

### Cycle 3.6: LaunchAgent plist generation

**Objective**: Implement create_switchback_plist() using plistlib
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** create_switchback_plist() generates valid plist file

**Expected failure:**
```
AttributeError: module 'claudeutils.account' has no attribute 'create_switchback_plist'
```

**Why it fails:** Function doesn't exist

**Verify RED:** `pytest tests/test_account_switchback.py::test_create_switchback_plist -xvs`
- Must fail with AttributeError
- If passes, STOP - function may already exist

---

**GREEN Phase:**

**Implementation:** Create create_switchback_plist() in switchback.py

**Changes:**
- File: src/claudeutils/account/switchback.py
  Action: Create create_switchback_plist(switchback_time) using plistlib.dump()
- File: src/claudeutils/account/__init__.py
  Action: Add `from .switchback import create_switchback_plist`
- File: tests/test_account_switchback.py
  Action: Test with tmp_path, verify plist structure and calendar interval

**Verify GREEN:** `pytest tests/test_account_switchback.py::test_create_switchback_plist -xvs`
- Must pass

**Verify no regression:** `pytest`
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/claude-tools-rewrite/reports/cycle-3-6-notes.md

---

### Cycle 3.7: Usage API cache - get operation

**Objective**: Implement UsageCache.get() returning cached data if fresh
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** UsageCache.get() returns None when cache missing or stale

**Expected failure:**
```
AttributeError: module 'claudeutils.account' has no attribute 'UsageCache'
```

**Why it fails:** UsageCache class doesn't exist

**Verify RED:** `pytest tests/test_account_usage.py::test_usage_cache_get_stale -xvs`
- Must fail with AttributeError
- If passes, STOP - class may already exist

---

**GREEN Phase:**

**Implementation:** Create UsageCache class with get() method

**Changes:**
- File: src/claudeutils/account/usage.py
  Action: Create UsageCache with get() checking cache file mtime against TTL
- File: src/claudeutils/account/__init__.py
  Action: Add `from .usage import UsageCache`
- File: tests/test_account_usage.py
  Action: Test get() with tmp_path, mock timestamps

**Verify GREEN:** `pytest tests/test_account_usage.py::test_usage_cache_get_stale -xvs`
- Must pass

**Verify no regression:** `pytest`
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/claude-tools-rewrite/reports/cycle-3-7-notes.md

---

### Cycle 3.8: Usage API cache - put operation

**Objective**: Implement UsageCache.put() writing data with timestamp
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** UsageCache.put() writes cache file with current timestamp

**Expected failure:**
```
AttributeError: 'UsageCache' object has no attribute 'put'
```

**Why it fails:** put() method doesn't exist

**Verify RED:** `pytest tests/test_account_usage.py::test_usage_cache_put -xvs`
- Must fail with AttributeError
- If passes, STOP - method may already exist

---

**GREEN Phase:**

**Implementation:** Add put() method to UsageCache

**Changes:**
- File: src/claudeutils/account/usage.py
  Action: Add put(data) writing JSON with timestamp
- File: tests/test_account_usage.py
  Action: Test put() writes file, verify get() retrieves it when fresh

**Verify GREEN:** `pytest tests/test_account_usage.py::test_usage_cache_put -xvs`
- Must pass

**Verify no regression:** `pytest`
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/claude-tools-rewrite/reports/cycle-3-8-notes.md

---

### Cycle 3.9: Account CLI - status command

**Objective**: Implement `claudeutils account status` command
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku
**Dependencies**: [DEPENDS: 1.2, 1.3, 1.7]

**Implementation:**

**RED Phase:**

**Test:** CLI command `claudeutils account status` returns account state

**Expected failure:**
```
AttributeError: 'Group' object has no attribute 'status'
```

**Why it fails:** status command doesn't exist

**Verify RED:** `pytest tests/test_cli_account.py::test_account_status -xvs`
- Must fail with AttributeError
- If passes, STOP - command may already exist

---

**GREEN Phase:**

**Implementation:** Create account status command in cli.py

**Changes:**
- File: src/claudeutils/account/cli.py
  Action: Create Click command group 'account' with 'status' command reading state and calling validate_consistency()
- File: src/claudeutils/cli.py
  Action: Add account command group
- File: tests/test_cli_account.py
  Action: Test with CliRunner, mock state files

**Verify GREEN:** `pytest tests/test_cli_account.py::test_account_status -xvs`
- Must pass

**Verify no regression:** `pytest`
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/claude-tools-rewrite/reports/cycle-3-9-notes.md

---

### Cycle 3.10: Account CLI - plan command

**Objective**: Implement `claudeutils account plan` switching to plan mode
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku
**Dependencies**: [DEPENDS: 1.8, 1.11]

**Implementation:**

**RED Phase:**

**Test:** CLI command `claudeutils account plan` switches mode and writes files

**Expected failure:**
```
AttributeError: 'Group' object has no attribute 'plan'
```

**Why it fails:** plan command doesn't exist

**Verify RED:** `pytest tests/test_cli_account.py::test_account_plan -xvs`
- Must fail with AttributeError
- If passes, STOP - command may already exist

---

**GREEN Phase:**

**Implementation:** Create account plan command

**Changes:**
- File: src/claudeutils/account/cli.py
  Action: Add 'plan' command calling mode switching logic, writing account-mode and claude-env files
- File: tests/test_cli_account.py
  Action: Test with CliRunner and tmp_path, verify files written

**Verify GREEN:** `pytest tests/test_cli_account.py::test_account_plan -xvs`
- Must pass

**Verify no regression:** `pytest`
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/claude-tools-rewrite/reports/cycle-3-10-notes.md

---

### Cycle 3.11: Account CLI - api command

**Objective**: Implement `claudeutils account api` switching to API mode
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku
**Dependencies**: [DEPENDS: 1.9, 1.11]

**Implementation:**

**RED Phase:**

**Test:** CLI command `claudeutils account api` switches to API mode

**Expected failure:**
```
AttributeError: 'Group' object has no attribute 'api'
```

**Why it fails:** api command doesn't exist

**Verify RED:** `pytest tests/test_cli_account.py::test_account_api -xvs`
- Must fail with AttributeError
- If passes, STOP - command may already exist

---

**GREEN Phase:**

**Implementation:** Create account api command

**Changes:**
- File: src/claudeutils/account/cli.py
  Action: Add 'api' command with provider selection, mode switching
- File: tests/test_cli_account.py
  Action: Test with CliRunner, verify mode and provider files

**Verify GREEN:** `pytest tests/test_cli_account.py::test_account_api -xvs`
- Must pass

**Verify no regression:** `pytest`
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/claude-tools-rewrite/reports/cycle-3-11-notes.md

---

### Cycle 3.12: Model CLI - list command

**Objective**: Implement `claudeutils model list` showing available models
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku
**Dependencies**: [DEPENDS: 2.6, 2.7]

**Implementation:**

**RED Phase:**

**Test:** CLI command `claudeutils model list` outputs model names

**Expected failure:**
```
AttributeError: 'Group' object has no attribute 'list'
```

**Why it fails:** list command doesn't exist

**Verify RED:** `pytest tests/test_cli_model.py::test_model_list -xvs`
- Must fail with AttributeError
- If passes, STOP - command may already exist

---

**GREEN Phase:**

**Implementation:** Create model list command

**Changes:**
- File: src/claudeutils/model/cli.py
  Action: Create Click command group 'model' with 'list' command calling load_litellm_config()
- File: src/claudeutils/cli.py
  Action: Add model command group
- File: tests/test_cli_model.py
  Action: Test with CliRunner, mock config file

**Verify GREEN:** `pytest tests/test_cli_model.py::test_model_list -xvs`
- Must pass

**Verify no regression:** `pytest`
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/claude-tools-rewrite/reports/cycle-3-12-notes.md

---

### Cycle 3.13: Model CLI - set command

**Objective**: Implement `claudeutils model set` writing override file
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku
**Dependencies**: [DEPENDS: 2.8, 2.9]

**Implementation:**

**RED Phase:**

**Test:** CLI command `claudeutils model set <model>` writes override file

**Expected failure:**
```
AttributeError: 'Group' object has no attribute 'set'
```

**Why it fails:** set command doesn't exist

**Verify RED:** `pytest tests/test_cli_model.py::test_model_set -xvs`
- Must fail with AttributeError
- If passes, STOP - command may already exist

---

**GREEN Phase:**

**Implementation:** Create model set command

**Changes:**
- File: src/claudeutils/model/cli.py
  Action: Add 'set' command calling write_overrides()
- File: tests/test_cli_model.py
  Action: Test with CliRunner and tmp_path, verify override file

**Verify GREEN:** `pytest tests/test_cli_model.py::test_model_set -xvs`
- Must pass

**Verify no regression:** `pytest`
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/claude-tools-rewrite/reports/cycle-3-13-notes.md

---

### Cycle 3.14: Model CLI - reset command

**Objective**: Implement `claudeutils model reset` removing override file
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** CLI command `claudeutils model reset` deletes override file

**Expected failure:**
```
AttributeError: 'Group' object has no attribute 'reset'
```

**Why it fails:** reset command doesn't exist

**Verify RED:** `pytest tests/test_cli_model.py::test_model_reset -xvs`
- Must fail with AttributeError
- If passes, STOP - command may already exist

---

**GREEN Phase:**

**Implementation:** Create model reset command

**Changes:**
- File: src/claudeutils/model/cli.py
  Action: Add 'reset' command removing override file
- File: tests/test_cli_model.py
  Action: Test with CliRunner, verify file deletion

**Verify GREEN:** `pytest tests/test_cli_model.py::test_model_reset -xvs`
- Must pass

**Verify no regression:** `pytest`
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/claude-tools-rewrite/reports/cycle-3-14-notes.md

---

### Cycle 3.15: Statusline CLI - basic structure

**Objective**: Implement `claudeutils statusline` reading stdin JSON
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** CLI command `claudeutils statusline` reads JSON from stdin

**Expected failure:**
```
AttributeError: 'MultiCommand' object has no attribute 'statusline'
```

**Why it fails:** statusline command doesn't exist

**Verify RED:** `pytest tests/test_cli_statusline.py::test_statusline_reads_stdin -xvs`
- Must fail with AttributeError
- If passes, STOP - command may already exist

---

**GREEN Phase:**

**Implementation:** Create statusline command

**Changes:**
- File: src/claudeutils/statusline/cli.py
  Action: Create Click command 'statusline' reading stdin JSON
- File: src/claudeutils/cli.py
  Action: Add statusline command
- File: tests/test_cli_statusline.py
  Action: Test with CliRunner, mock stdin

**Verify GREEN:** `pytest tests/test_cli_statusline.py::test_statusline_reads_stdin -xvs`
- Must pass

**Verify no regression:** `pytest`
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/claude-tools-rewrite/reports/cycle-3-15-notes.md

---

**Checkpoint**
1. Fix: Run `just dev`. Sonnet quiet-task fixes failures. Commit when green.
2. Vet: Review CLI command structure, help text clarity, error handling. Commit fixes.

---

## Design Decisions

**1. Pydantic AccountState model** - Replace scattered file reads with single state object having `validate_consistency()` returning list of issues. Enables testable validation logic with clear error messages.

**2. Provider as Protocol** - Strategy pattern for anthropic/openrouter/litellm providers. Each provider implements claude_env_vars(), validate(), and settings_json_patch(). Consolidates per-provider logic scattered across multiple functions.

**3. LiteLLM config structured parsing** - Regex-based YAML parsing with Decimal pricing. No PyYAML dependency needed since config is read-only. Parse comment metadata for tiers, arena rank, and pricing.

**4. Keychain via subprocess** - Wrap macOS `security` commands in Keychain class. Mockable via subprocess.run patches. No third-party keychain library dependencies.

**5. Statusline ANSI formatter** - Separate StatuslineFormatter class for terminal output. Makes display logic testable without running Claude Code instance. Methods: colored(), token_bar(), vertical_bar(), limit_display().

**6. LaunchAgent via plistlib** - Use stdlib plistlib.dump() to generate LaunchAgent plist. Fixes heredoc variable expansion bug from shell version. Structured data → structured output.

**7. Usage API caching** - 30-second TTL cache with UsageCache class. Separate cache logic from API call. Get/put operations check mtime against TTL.

**8. Shell wrappers delegation** - Thin bash scripts (~10 lines) in home/claude/ delegate to claudeutils CLI. Handle direnv sourcing for mode switches. Python CLI is self-contained, shell provides integration.

## Dependencies

**Before**: claudeutils package installed in development mode, pytest/mypy/ruff configured, ~/.claude/ directory accessible

**After**: Complete Python implementation of account, model, and statusline modules with full test coverage, ready for shell wrapper integration (executed in home repo)
