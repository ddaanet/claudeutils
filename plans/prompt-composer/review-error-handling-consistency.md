# Review: Token Counter Error Handling Consistency

- **Date**: 2026-01-01
- **Plan**: plan-error-handling-consistency.md
- **Status**: ✅ Complete

---

## Plan Conformity

All plan steps implemented:

- ✅ Phase 1, Step 1.1-1.2: Proactive API key validation added
- ✅ Phase 1, Step 1.3: TypeError handling removed
- ✅ Phase 2, Step 2.1: Upfront file existence check removed
- ✅ Phase 2, Step 2.2-2.3: Permission and decode error tests added

All 155 tests pass.

---

## Issues Found

### Critical Issues

None.

### Important Issues

#### 1. Incorrect Type Annotations (5 occurrences)

**Location**: `tests/test_cli_tokens.py`

Multiple test functions use wrong type hint for `mocker` parameter:

```python
# Lines 181, 213, 245, 342, 379
def test_foo(..., mocker: pytest.MonkeyPatch) -> None:
```

**Problem**: `mocker` is from `pytest-mock` (MockerFixture), not MonkeyPatch. Type
checker would catch this.

**Fix**: Change to `mocker: MockerFixture` with proper import:

```python
from pytest_mock import MockerFixture

def test_foo(..., mocker: MockerFixture) -> None:
```

**Affected tests**:

- `test_cli_auth_error_shows_helpful_message` (line 180)
- `test_cli_rate_limit_error_shows_message` (line 210)
- `test_cli_file_error_shows_message` (line 242)
- `test_cli_detects_empty_api_key_before_sdk` (line 337)
- `test_cli_detects_missing_api_key_before_sdk` (line 374)

---

#### 2. Test Environment Dependency

**Location**: `tests/test_cli_tokens.py:60-72`

`test_cli_reports_missing_file` doesn't mock Anthropic client or resolve_model_alias:

```python
def test_cli_reports_missing_file(tmp_path: Path) -> None:
    """Test that CLI reports missing file."""
    missing_file = tmp_path / "missing.md"
    old_stderr = sys.stderr
    sys.stderr = io.StringIO()
    try:
        with pytest.raises(SystemExit) as exc_info:
            handle_tokens("haiku", [str(missing_file)])
        assert exc_info.value.code == 1
        error_output = sys.stderr.getvalue()
        assert "missing.md" in error_output
    finally:
        sys.stderr = old_stderr
```

**Problems**:

1. Depends on `ANTHROPIC_API_KEY` in environment - if not set, fails with API key error
   instead of file error
2. Manually redirects stderr instead of using `capsys` fixture (inconsistent with other
   tests)

**Fix**: Use `cli_base_mocks` fixture and `capsys`:

```python
def test_cli_reports_missing_file(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    cli_base_mocks: dict[str, Mock],
) -> None:
    """Test that CLI reports missing file."""
    missing_file = tmp_path / "missing.md"

    cli_base_mocks["anthropic"].return_value = Mock()
    cli_base_mocks["resolve"].return_value = "claude-haiku-4-5-20251001"

    with pytest.raises(SystemExit) as exc_info:
        handle_tokens("haiku", [str(missing_file)])

    assert exc_info.value.code == 1
    captured = capsys.readouterr()
    assert "missing.md" in captured.err or "Failed to read" in captured.err
```

---

### Preferred Improvements

#### 3. Redundant Unit Test

**Location**: `tests/test_cli_tokens.py:242-272`

`test_cli_file_error_shows_message` mocks `count_tokens_for_file` to raise
`FileReadError`. This is a unit test of the CLI error handler.

**Redundancy**: Already covered by integration tests:

- `test_cli_reports_missing_file` - file not found
- `test_cli_permission_error_propagates` - permission denied
- `test_cli_decode_error_propagates` - binary file

These integration tests create real problematic files and verify the full error
propagation path from `tokens.py` → CLI handler → stderr.

**Recommendation**: Delete `test_cli_file_error_shows_message` to reduce redundancy and
prefer integration tests per project guidelines.

---

#### 4. Minor Readability: API Key Check

**Location**: `src/claudeutils/tokens_cli.py:35-37`

Current implementation:

```python
api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key or api_key.strip() == "":
    raise ApiAuthenticationError
```

**Observation**: The logic is correct due to short-circuit evaluation:

- `not api_key` handles None and empty string
- `api_key.strip() == ""` only evaluated if api_key is truthy (whitespace-only)

**Optional improvement** for clarity:

```python
api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key or not api_key.strip():
    raise ApiAuthenticationError
```

Both versions work identically. Current version is acceptable.

---

## Code Quality Review

### Correctness ✅

- API key validation logic correct (short-circuit prevents AttributeError)
- Exception handling hierarchy correct
- Error propagation follows "catch at source, raise custom with chaining" pattern
- All tests pass

### Security ✅

- No security vulnerabilities identified
- API keys properly validated before SDK usage
- No secrets in test files

### Over-Engineering ✅

- No unnecessary complexity
- Removed redundant upfront validation as planned
- Exception messages clear and actionable

### Expressiveness ✅

- Function names clear
- Variable names descriptive
- Error messages user-friendly

### Factorization ✅

- Good use of fixtures in `conftest.py`:
  - `api_key_unset`, `api_key_empty` - single-purpose, reusable
  - `cli_base_mocks` - factorizes common mock setup
- All mocks use `autospec=True` - excellent!

### Test Quality

**Strengths**:

- Heavy use of integration tests (external API mocked, file operations real)
- Good coverage of error paths
- Fixtures well-designed and reused

**Weaknesses**:

- Type annotations incorrect (mocker parameter)
- One test depends on environment state
- One test uses manual stderr redirect instead of capsys
- One redundant unit test

---

## Summary

**Changes Implemented**:

1. ✅ Fixed 5 incorrect type annotations (`mocker: pytest.MonkeyPatch` →
   `mocker: MockerFixture`)
2. ✅ Fixed `test_cli_reports_missing_file` to use `cli_base_mocks` fixture and `capsys`
3. ✅ Deleted redundant `test_cli_file_error_shows_message` unit test
4. ✅ Removed unused `FileReadError` import
5. ✅ Added `noqa: TRY301` comment for intentional raise in try block

**Final Status**:

- All plan requirements met
- All 154 tests pass
- Linting passes (ruff, mypy)
- Formatting consistent
- Error handling patterns correct
- Test suite now fully integration-focused with consistent pytest-mock usage
