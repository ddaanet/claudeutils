# Token Counter Implementation Fixes

- **Date**: 2025-12-30
- **Type**: Bug fixes and test quality improvements
- **Branch**: main (current staged changes)
- **Executor**: Code agent (Haiku)

---

## Overview

This plan addresses 23 issues identified in two review documents:

- `review-token-counter.md` (original review)
- `review-token-counter-addendum-1.md` (additional findings)

**Scope**: Fix critical bugs, improve error handling, migrate tests to pytest-mock,
reduce test duplication.

**Workflow**: Each step includes test (if behavioral change) and implementation. Every
step must pass test suite before proceeding.

---

## Phase 1: Type Safety

### Step 1.1: Define ModelId NewType

**Files**: `src/claudeutils/tokens.py`

Add after imports: `ModelId = NewType("ModelId", str)`

Import NewType: `from typing import NewType`

Update type hints:

- `resolve_model_alias` return type: `-> ModelId`
- `count_tokens_for_file` model parameter: `model: ModelId`
- `count_tokens_for_files` model parameter: `model: ModelId`

This prevents passing unresolved aliases to API calls (compile-time safety).

**Test**: None (type annotations only, verified by mypy)

---

### Step 1.2: Extract Cache TTL Constant

**Files**: `src/claudeutils/tokens.py`

Locate hardcoded value `cache_ttl_hours = 24` inside `resolve_model_alias`. Create
module-level constant `CACHE_TTL_HOURS = 24` near the top after imports and logging
configuration. Replace hardcoded value with the constant.

**Test**: None (refactoring, no behavior change)

---

## Phase 2: Bug Fixes

### Step 2.1: Add Required Client Parameter to count_tokens_for_file

**Test (RED)**: `tests/test_tokens_count.py`

Add test `test_count_tokens_uses_resolved_model_id`:

- **Given**: Test file containing "Hello world", mock Anthropic client
- **When**: `count_tokens_for_file` is called with file path,
  `ModelId("claude-sonnet-4-5-20250929")`, and mock client
- **Then**: Returns token count AND mock's `messages.count_tokens` was called with exact
  model ID "claude-sonnet-4-5-20250929" and messages=[{"role": "user", "content": "Hello
  world"}]

Use `assert_called_once_with` to verify API receives resolved model ID (not an alias
like "sonnet").

Add test `test_count_tokens_for_files_reuses_single_client`:

- **Given**: Three test files with different content ("Hello", "World", "Test"), mock
  Anthropic client
- **When**: `count_tokens_for_files` is called with paths and resolved model ID
- **Then**: Returns three TokenCount objects, client's `messages.count_tokens` called
  exactly 3 times (proves client reuse)

**Implementation (GREEN)**: `src/claudeutils/tokens.py`

Modify `count_tokens_for_file` signature to accept required `client: Anthropic`
parameter (no Optional, no default). Update all callers to provide client.

Modify `count_tokens_for_files` to create Anthropic client once before loop, pass it to
each `count_tokens_for_file` call.

Update `count_tokens_for_file` docstring: add client parameter to Args, add Raises
section documenting ApiAuthenticationError and ApiRateLimitError.

Update `src/claudeutils/tokens_cli.py` to pass client to `count_tokens_for_file` calls
(uses existing client created on line 39).

---

### Step 2.2: Resolve Versioned Model IDs to Full IDs

**Test (RED)**: `tests/test_tokens_resolve.py`

Add test `test_resolve_versioned_model_id_to_full_id`:

- **Given**: Mock Anthropic client returning models including
  "claude-sonnet-4-5-20250929" and "claude-sonnet-4-5-20241022", cache directory
- **When**: `resolve_model_alias` is called with "claude-sonnet-4-5" (versioned model ID
  without date)
- **Then**: Returns "claude-sonnet-4-5-20250929" (latest 4-5 version with full date
  suffix)

API supports versioned model IDs like "claude-sonnet-4-5" but we must use and output the
full ID with date suffix ("claude-sonnet-4-5-20250929") for consistency and
explicitness.

**Implementation (GREEN)**: `src/claudeutils/tokens.py`

In `resolve_model_alias`, update model matching logic:

If input model string starts with "claude-" but doesn't match a full model ID (no date
suffix), treat it as a versioned prefix. Match models where ID starts with this prefix
and return the latest (most recent date).

For example:

- Input: "claude-sonnet-4-5" → matches "claude-sonnet-4-5-*" → returns
  "claude-sonnet-4-5-20250929"
- Input: "sonnet" → matches "claude-sonnet-*" → returns latest sonnet
- Input: "claude-sonnet-4-5-20250929" → exact match, return as-is

Current implementation only handles unversioned aliases ("sonnet"). Must also handle
versioned model IDs ("claude-sonnet-4-5").

---

### Step 2.3: Handle File Reading Errors with Specific Exception

**Test (RED)**: `tests/test_tokens_count.py`

Add test `test_count_tokens_unreadable_file_shows_reason`:

- **Given**: Test file with permissions 000 (unreadable), mock Anthropic client
- **When**: `count_tokens_for_file` is called
- **Then**: Raises FileReadError with message containing "Failed to read", the file
  path, and "Permission denied" (or similar OS error text)

Add test `test_count_tokens_binary_file_shows_decode_error`:

- **Given**: Binary file (write PNG header bytes `b'\x89PNG'`), mock Anthropic client
- **When**: `count_tokens_for_file` is called
- **Then**: Raises FileReadError with message containing "Failed to read", file path,
  and decode error description

**Implementation (GREEN)**: `src/claudeutils/tokens.py`, `src/claudeutils/exceptions.py`

In `exceptions.py`, define `FileReadError(ClaudeUtilsError)` subclass.

In `tokens.py`:

- Import FileReadError from exceptions
- Wrap `path.read_text()` in try/except catching UnicodeDecodeError, PermissionError,
  OSError
- Raise `FileReadError(f"Failed to read {path}: {e}") from e` (always use exception
  chaining)
- Update docstring Raises section to include FileReadError

---

### Step 2.4a: Use fetched_at for Expired Cache Detection

**Test (RED)**: `tests/test_tokens_resolve.py`

Add test `test_cache_expired_by_fetched_at_not_mtime`:

- **Given**: Cache file with `fetched_at` from 25 hours ago, use `os.utime()` to set
  file mtime to 1 hour ago, mock Anthropic API
- **When**: `resolve_model_alias` is called
- **Then**: Cache treated as expired, API `models.list()` called (cache bypassed)

**Implementation (GREEN)**: `src/claudeutils/tokens.py`

In `resolve_model_alias`, move cache data reading into try block BEFORE TTL check.
Calculate cache age from `cache_data.fetched_at` to `datetime.now(tz=UTC)`.

**Critical implementation requirement for proper test progression**: Implement the
expiry check as: expire if EITHER fetched_at age >= CACHE_TTL_HOURS OR mtime age >=
CACHE_TTL_HOURS. This makes test 2.4a pass (expired by fetched_at) but keeps test 2.4b
failing (mtime still checked).

If expired, log debug message with age and fall through to API call.

---

### Step 2.4b: Use fetched_at ONLY for Valid Cache Detection

**Test (RED)**: `tests/test_tokens_resolve.py`

Add test `test_cache_valid_by_fetched_at_ignores_old_mtime`:

- **Given**: Cache file with `fetched_at` from 1 hour ago, use `os.utime()` to set file
  mtime to 25 hours ago, mock Anthropic API
- **When**: `resolve_model_alias` is called
- **Then**: Cached data used, API `models.list()` NOT called

This test will FAIL with implementation from 2.4a because it still checks mtime (expires
cache when mtime old).

**Implementation (GREEN)**: `src/claudeutils/tokens.py`

Remove ALL mtime checks from cache validation logic. Use ONLY `cache_data.fetched_at`
for TTL.

Restructure cache reading with try/except/else:

- Try block: Read cache, check if `fetched_at` age < CACHE_TTL_HOURS
- If valid, use else block to return cached result
- If expired, fall through to API call
- Except block: Catch (ValueError, OSError, UnicodeDecodeError), log warning, fall
  through to API

Remove any remaining references to `cache_file.stat().st_mtime` in TTL logic.

---

### Step 2.5: Add CLI Exception Handling for Friendly Errors

**Test (RED)**: `tests/test_cli_tokens.py`

Add test `test_cli_auth_error_shows_helpful_message`:

- **Given**: Test file exists, mock Anthropic() constructor to raise
  AuthenticationError("Invalid API key")
- **When**: `handle_tokens` is called with model="sonnet", files=["test.md"]
- **Then**: Exits with code 1, stderr contains "Error: Authentication failed" and
  "Please set ANTHROPIC_API_KEY"

Add test `test_cli_rate_limit_error_shows_message`:

- **Given**: Mock Anthropic API to raise RateLimitError during token counting
- **When**: `handle_tokens` is called
- **Then**: Exit code 1, stderr contains "Error: Rate limit exceeded"

Add test `test_cli_file_error_shows_message`:

- **Given**: Mock to raise FileReadError (from step 2.3)
- **When**: `handle_tokens` is called
- **Then**: Exit code 1, stderr contains "Error:" followed by file error message

Use pytest.raises(SystemExit) and capsys to verify exit code and stderr.

Note: Lower-level error handling (raising ApiAuthenticationError) already exists in
tokens.py. This step adds user-facing CLI error messages.

**Implementation (GREEN)**: `src/claudeutils/tokens_cli.py`

Wrap entire `handle_tokens` function body in try/except with handlers:

- `ApiAuthenticationError as e`: Print to stderr
  `f"Error: Authentication failed. {e}"` + newline +
  `"Please set ANTHROPIC_API_KEY environment variable."`, call `sys.exit(1)`
- `ApiRateLimitError as e`: Print to stderr `f"Error: Rate limit exceeded. {e}"`, call
  `sys.exit(1)`
- `ClaudeUtilsError as e`: Print to stderr `f"Error: {e}"`, call `sys.exit(1)` (catches
  FileReadError, ModelResolutionError as subclasses)

Import exception types from claudeutils.exceptions.

---

### Step 2.6: Extract Duplicate CLI Code

**Files**: `src/claudeutils/tokens_cli.py`

In `handle_tokens` within try block, consolidate duplicated token counting loops
(currently in both JSON and text branches, lines 44-48 and 59-63).

Extract into single loop before output formatting: collect all results into list, then
format based on `json_output` flag.

Pass client parameter to all `count_tokens_for_file` calls (uses client from line 39).

**Test**: None (refactoring covered by existing tests)

---

## Phase 3: Defensive Improvements

### Step 3.1: Handle Generic API Errors

**Test (RED)**: `tests/test_tokens_count.py`

Add test `test_count_tokens_handles_network_error`:

- **Given**: Test file with content, mock to raise APIConnectionError("Connection
  timeout")
- **When**: `count_tokens_for_file` is called
- **Then**: Raises ClaudeUtilsError with message containing "API error" and "Connection
  timeout"

Alternative: Integration test with real network condition if possible (preferred).

**Implementation (GREEN)**: `src/claudeutils/tokens.py`

Add `APIError` to imports from anthropic (base class for all API errors).

In `count_tokens_for_file`, add catch-all handler after AuthenticationError and
RateLimitError to catch `APIError`. Raise `ClaudeUtilsError(f"API error: {e}") from e`
(use exception chaining).

Note: `resolve_model_alias` already has APIError catch-all, no changes needed.

---

### Step 3.2: Handle Cache Write Failures Gracefully

**Test (RED)**: `tests/test_tokens_resolve.py`

Add test `test_cache_write_failure_continues_successfully`:

- **Given**: Integration test with read-only cache directory (create actual directory
  with restricted permissions), mock Anthropic API with model data
- **When**: `resolve_model_alias` is called (attempts cache write after API call)
- **Then**: Returns correct model ID successfully (write failure is non-fatal)

Prefer integration test with real filesystem permissions over mocking Path.write_text.

**Implementation (GREEN)**: `src/claudeutils/tokens.py`

In `resolve_model_alias`, wrap cache write operations (cache_dir.mkdir and
cache_file.write_text) in try/except catching OSError.

On exception: Log warning `f"Failed to write cache at {cache_file}: {e}"`, continue
execution On success: Log debug `f"Cached models list to {cache_file}"`

---

### Step 3.3: Document Case-Insensitive Matching

**Files**: `src/claudeutils/tokens.py`

Update `resolve_model_alias` docstring: mention model alias matching is
case-insensitive, add "(case-insensitive)" to model parameter in Args section, add
Raises section documenting ModelResolutionError.

**Test**: None (documentation only)

---

## Phase 4: Test Migration

### Step 4.1: Add pytest-mock Dependency

Run: `uv add --dev pytest-mock`

Adds pytest-mock to dev dependencies, updates lockfile.

**Test**: None (dependency installation)

---

### Step 4.2: Create Shared Test Fixtures

**Files**: `tests/conftest.py` (create new file)

Create shared pytest fixtures:

1. **mock_anthropic_client(mocker)**: Factory fixture returning function accepting
   `token_count` (int, default 5) or `side_effect` parameters. Creates mock with
   `spec=Anthropic`, patches `claudeutils.tokens.Anthropic` with `autospec=True`.
   Returns mock client with configured `messages.count_tokens`.

2. **test_markdown_file(tmp_path)**: Factory fixture returning function accepting
   `content` (str, default "Hello world") and `filename` (str, default "test.md").
   Creates file in tmp_path, returns Path.

3. **mock_models_api(mocker)**: Factory fixture returning function accepting `models`
   (list of dicts with id/created_at) or `raise_error`. Creates mock client with
   `spec=Anthropic`, mocks `client.models.list()`. Default: claude-sonnet-4-5-20250929
   from 2025-09-29T00:00:00Z.

4. **mock_token_counting(mocker)**: Factory fixture for CLI tests. Accepts `model_id`
   (str) and `counts` (int or list). Patches `resolve_model_alias` and
   `count_tokens_for_file`.

**Test**: None (fixture definitions)

---

### Step 4.3: Migrate test_tokens_count.py

**Files**: `tests/test_tokens_count.py`

Remove `from unittest.mock import Mock`.

For each test:

- Replace manual mock setup with `mock_anthropic_client` fixture
- Replace file creation with `test_markdown_file` fixture
- Add `assert_called_once_with` for API calls where appropriate
- Apply to all existing tests

**Test**: None (refactoring)

---

### Step 4.4: Migrate test_tokens_resolve.py

**Files**: `tests/test_tokens_resolve.py`

Remove `from unittest.mock import Mock`.

Replace manual model mocking with `mock_models_api` fixture in all tests.

**Test**: None (refactoring)

---

### Step 4.5: Migrate test_cli_tokens.py

**Files**: `tests/test_cli_tokens.py`

Remove `from unittest.mock import patch`.

Replace patch context managers with `mock_token_counting` fixture in all tests.

**Test**: None (refactoring)

---

### Step 4.6: Configure E2E Test Marker

**Files**: `tests/test_tokens_integration.py`, `pyproject.toml`

In integration test:

- Add `@pytest.mark.e2e` decorator
- Use monkeypatch to override `platformdirs.user_cache_dir` returning path under
  tmp_path (isolate cache)
- Do NOT add pytest.skip or skipif - test should fail loudly if ANTHROPIC_API_KEY
  missing

In pyproject.toml `[tool.pytest.ini_options]`:

- Add `markers = ["e2e: end-to-end tests requiring API credentials"]`
- Do NOT add addopts to skip e2e by default - run all tests by default

E2E tests will fail if API key not configured (correct behavior - explicit failure
better than silent skip).

**Test**: None (configuration)

---

## Phase 5: Verification

### Step 5.1: Run Test Suite

Run: `just test`

All tests must pass. If failures, STOP and report.

### Step 5.2: Manual CLI Testing (Optional)

If ANTHROPIC_API_KEY available:

- `uv run claudeutils tokens sonnet README.md`
- `uv run claudeutils tokens haiku pyproject.toml --json`
- `uv run claudeutils tokens opus README.md pyproject.toml`
- `ANTHROPIC_API_KEY="" uv run claudeutils tokens sonnet README.md`

Expected: Friendly error messages, no tracebacks.

---

## Notes for Code Agent

**Critical Rules**:

- Client parameters are REQUIRED (no Optional, no None) - fail fast on logic errors
- Always use exception chaining: `raise NewError(...) from e`
- Define specific exception subclasses (FileReadError), don't use ClaudeUtilsError
  directly
- ModelId NewType prevents passing unresolved aliases to API
- E2E tests fail loudly if misconfigured (no silent skips)

**Workflow**:

- Use `just role-code <module>` after changes to run relevant tests
- Each step must pass tests before proceeding
- If any step fails, STOP and report

**Key Points**:

- Client reuse: Create once per CLI invocation, pass to all functions
- Error messages: Include specific reasons from underlying exceptions
- Exception handling: In tokens_cli.py, use ClaudeUtilsError base to catch subclasses
- Cache failures: Non-fatal, log warnings and continue
- Versioned aliases: Support both "sonnet" and "sonnet-4-5" formats
