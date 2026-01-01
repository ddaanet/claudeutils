# Token Counter Error Handling Consistency

- **Date**: 2026-01-01
- **Type**: Error handling improvements
- **Branch**: tokens
- **Executor**: Code agent (Haiku)

---

## Overview

Improve error handling consistency by:

1. **Prevent TypeError**: Check API key proactively before SDK instantiation, raise
   custom error
2. **Remove redundant validation**: CLI should not duplicate file existence checks
   already handled by lower layers
3. **Remove TypeError handling**: TypeError is a bug indicator, not an expected error to
   catch

**Core principle**: Catch exceptions close to their source, raise custom exceptions with
chaining. Do not let low-level exceptions propagate to high-level handlers.

**Workflow**: Each step adds exactly one test (or zero for refactoring). After every
test, run `just test` to verify. No step may proceed until tests pass.

---

## Phase 1: Proactive API Key Validation

Prevent TypeError from SDK by checking API key before instantiation. Test at CLI layer
with mocks.

### Step 1.1: CLI Validates Empty API Key Before SDK Call

**Test (RED)**: `tests/test_cli_tokens.py`

Add test `test_cli_detects_empty_api_key_before_sdk`:

- **Given**: Test file "test.md" with content "Hello", `ANTHROPIC_API_KEY=""` (empty
  string), model="sonnet"
- **When**: `handle_tokens("sonnet", [test_file])` called
- **Then**: Raises `SystemExit` with code 1, stderr contains "Authentication failed" and
  "ANTHROPIC_API_KEY"

**Test requirements**:

- Create real file in tmp_path
- Use `monkeypatch.setenv("ANTHROPIC_API_KEY", "")`
- Use `pytest.raises(SystemExit)` with `capsys` to check stderr
- Mock `Anthropic` client with `patch("claudeutils.tokens_cli.Anthropic")` (should not
  be called)
- Mock `resolve_model_alias` and `count_tokens_for_file` (should not be called)

**What this requires**: API key validation in `tokens_cli.py` before `Anthropic()` call

**What this does NOT require**: Catching TypeError

**Implementation (GREEN)**: `src/claudeutils/tokens_cli.py`

Add after line 31 (inside try block, before line 33):

```python
# Check API key before SDK instantiation to avoid TypeError
api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key or api_key.strip() == "":
    raise ApiAuthenticationError
```

Add import at top: `import os`

**Verify**: Run
`just test tests/test_cli_tokens.py::test_cli_detects_empty_api_key_before_sdk` - test
should pass

---

### Step 1.2: CLI Validates Missing API Key Before SDK Call

**Test (RED)**: `tests/test_cli_tokens.py`

Add test `test_cli_detects_missing_api_key_before_sdk`:

- **Given**: Test file "test.md" with content "Hello", `ANTHROPIC_API_KEY` not set in
  environment, model="haiku"
- **When**: `handle_tokens("haiku", [test_file])` called
- **Then**: Raises `SystemExit` with code 1, stderr contains "Authentication failed" and
  "ANTHROPIC_API_KEY"

**Test requirements**:

- Create real file in tmp_path
- Use `monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)`
- Use `pytest.raises(SystemExit)` with `capsys` to check stderr
- Mock `Anthropic` client (should not be called)
- Mock `resolve_model_alias` and `count_tokens_for_file` (should not be called)

**What this requires**: Same API key validation as Step 1.1 (handles both empty and
missing)

**Implementation (GREEN)**: None needed - same code from Step 1.1 handles both cases

**Verify**: Run
`just test tests/test_cli_tokens.py::test_cli_detects_missing_api_key_before_sdk` - test
should pass

---

### Step 1.3: Remove TypeError Handling

**Test**: Delete `tests/test_cli_tokens.py::test_cli_handles_empty_api_key_error` (lines
267-294)

**Reason**: We no longer catch TypeError - if we get one, it's a bug

**Implementation**: `src/claudeutils/tokens_cli.py`

Replace exception handling (lines 70-75):

```python
except (AuthenticationError, ApiAuthenticationError, TypeError) as e:
    if isinstance(e, TypeError) and "authentication method" not in str(e).lower():
        raise
    print(f"Error: Authentication failed. {e}", file=sys.stderr)
    print("Please set ANTHROPIC_API_KEY environment variable.", file=sys.stderr)
    sys.exit(1)
```

With:

```python
except (AuthenticationError, ApiAuthenticationError) as e:
    print(f"Error: Authentication failed. {e}", file=sys.stderr)
    print("Please set ANTHROPIC_API_KEY environment variable.", file=sys.stderr)
    sys.exit(1)
```

**Verify**: Run `just dev` - all tests should pass

---

## Checkpoint 1: Proactive Validation Complete

**Run**: `just dev`

**Expected**:

- API key validated before SDK instantiation (both empty and missing)
- No TypeError handling (TypeErrors are bugs)
- All tests pass

**Status**: Awaiting user approval to continue

---

## Phase 2: Remove Redundant File Validation

CLI currently validates file existence upfront (lines 39-43), but
`count_tokens_for_file` already handles file errors by catching
`(PermissionError, OSError, UnicodeDecodeError)` and raising `FileReadError` with
chaining (tokens.py:151-152).

**Principle**: Don't duplicate error handling. Let `FileReadError` propagate from the
function that reads the file.

### Step 2.1: Remove Upfront File Existence Check

**Test**: Modify existing test `test_cli_reports_missing_file` (line 60)

Current test uses upfront validation. Modify to verify `FileReadError` propagates:

- **Given**: File does not exist, model="haiku"
- **When**: `handle_tokens("haiku", [missing_file])` called
- **Then**: Raises `SystemExit` with code 1, stderr contains "Error:" and "file not
  found" or "Failed to read"

**Test modification**: Test currently expects specific error message from upfront check.
After removing upfront check, test should verify FileReadError message appears in
stderr.

**Implementation**: `src/claudeutils/tokens_cli.py`

Delete lines 39-43:

```python
for filepath_str in file_paths:
    filepath = Path(filepath_str)
    if not filepath.exists():
        print(f"Error: {filepath_str} file not found", file=sys.stderr)
        sys.exit(1)
```

**Note**: `FileReadError` is already caught by `except ClaudeUtilsError as e` handler
(line 79), so no new exception handling needed.

**Verify**: Run `just test tests/test_cli_tokens.py::test_cli_reports_missing_file` -
test should pass with FileReadError message

---

### Step 2.2: Verify Permission Errors Propagate

**Test**: Add test `test_cli_permission_error_propagates` in `tests/test_cli_tokens.py`

- **Given**: File with permissions 000 (unreadable), mock `resolve_model_alias` only,
  model="haiku"
- **When**: `handle_tokens("haiku", [unreadable_file])` called
- **Then**: Raises `SystemExit` with code 1, stderr contains "Permission denied" or
  "Failed to read"

**Test requirements**:

- Create file with `chmod(0o000)`
- Mock only `resolve_model_alias` (not `count_tokens_for_file` - need real file
  operation)
- Mock `Anthropic` client creation
- Verify `FileReadError` propagates to CLI handler

**Implementation**: None needed - `count_tokens_for_file` already catches
`PermissionError` and raises `FileReadError`

**Verify**: Run
`just test tests/test_cli_tokens.py::test_cli_permission_error_propagates` - test should
pass

---

### Step 2.3: Verify Decode Errors Propagate

**Test**: Add test `test_cli_decode_error_propagates` in `tests/test_cli_tokens.py`

- **Given**: Binary file (PNG header bytes), mock `resolve_model_alias` only,
  model="opus"
- **When**: `handle_tokens("opus", [binary_file])` called
- **Then**: Raises `SystemExit` with code 1, stderr contains "Failed to read"

**Test requirements**:

- Create binary file with `write_bytes(b"\x89PNG\r\n\x1a\n")`
- Mock only `resolve_model_alias`
- Mock `Anthropic` client creation
- Verify `FileReadError` propagates

**Implementation**: None needed - `count_tokens_for_file` already catches
`UnicodeDecodeError` and raises `FileReadError`

**Verify**: Run `just test tests/test_cli_tokens.py::test_cli_decode_error_propagates` -
test should pass

---

## Checkpoint 2: Error Handling Consistency Complete

**Run**: `just dev`

**Expected**:

- All file errors (not found, permission, decode) caught close to source in `tokens.py`
- Raised as `FileReadError` with exception chaining
- CLI handles `FileReadError` via `ClaudeUtilsError` base class
- No redundant upfront validation
- All tests pass, lint passes

**Status**: Final verification before completion

---

## Summary

**Files modified**:

1. `src/claudeutils/tokens_cli.py` - Add API key validation, remove TypeError handling,
   remove upfront file checks
2. `tests/test_cli_tokens.py` - Add 2 API key validation tests, delete TypeError test,
   add/modify file error tests

**Error handling pattern**:

- **API key**: Proactive check before SDK call → `ApiAuthenticationError`
- **File errors**: Caught in `tokens.py` near `path.read_text()` → `FileReadError` with
  chaining
- **Rate limit**: Caught in `tokens.py` near API call → `ApiRateLimitError` with
  chaining
- **Other API errors**: Caught in `tokens.py` near API call → `ApiError` with chaining
- **TypeError**: Not caught - indicates a bug
