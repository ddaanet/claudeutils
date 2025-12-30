# Token Counter Implementation Review

- **Date**: 2025-12-30
- **Branch**: `token` (squash merged, not committed)
- **Reviewer**: Claude Code
- **Status**: ⚠️ Requires fixes before commit

## Executive Summary

The token counter implementation is **well-architected** with good separation of
concerns, comprehensive test coverage, and thoughtful error handling. However, it has
**critical issues** in both implementation and test code that must be addressed before
committing.

**Key Strengths:**

- ✅ Excellent test coverage (unit, integration, e2e)
- ✅ Type safety with Pydantic models
- ✅ Smart caching strategy (24h TTL)
- ✅ Flexible output formats (JSON + text)
- ✅ Good documentation

**Critical Problems:**

- ❌ Inefficient API client creation (per-file overhead)
- ❌ Missing exception handling in CLI
- ❌ Test code uses `unittest.mock` instead of `pytest-mock`
- ❌ Mocks lack `autospec`/`spec` for type safety
- ❌ Massive code duplication in tests (~40% reducible)

## Implementation Review

### Critical Issues (Must Fix)

#### 1. Inefficient Client Creation

**Location**: `src/claudeutils/tokens.py:128`

```python
# PROBLEM: New client created for each file
def count_tokens_for_file(path: Path, model: str) -> int:
    content = path.read_text()
    if not content:
        return 0

    client = Anthropic()  # ❌ Created every call
    response = client.messages.count_tokens(...)
```

**Impact**:

- Unnecessary overhead for multi-file operations
- Slower batch processing
- Redundant initialization

**Solution**: Create client once and reuse:

```python
def count_tokens_for_file(path: Path, model: str, client: Anthropic | None = None) -> int:
    if client is None:
        client = Anthropic()
    # ... rest of function
```

Or refactor `count_tokens_for_files` to create client once for the batch.

---

#### 2. Uncaught Exceptions in CLI

**Location**: `src/claudeutils/tokens_cli.py:19-67`

```python
def handle_tokens(model: str, files: list[str], *, json_output: bool = False) -> None:
    # ❌ No try/except for:
    # - ApiAuthenticationError (line 41: resolve_model_alias)
    # - ApiRateLimitError (line 47/61: count_tokens_for_file)
    # - ModelResolutionError (line 41: resolve_model_alias)

    resolved_model = resolve_model_alias(model, client, cache_dir)
    count = count_tokens_for_file(filepath, resolved_model)
```

**Impact**: Users see Python tracebacks instead of friendly error messages.

**Solution**: Add proper exception handling:

```python
def handle_tokens(...):
    try:
        # ... existing code
    except ApiAuthenticationError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except ApiRateLimitError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except ModelResolutionError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
```

---

#### 3. Duplicate Code in CLI

**Location**: `src/claudeutils/tokens_cli.py:43-66`

Token counting loop duplicated in JSON and text output paths:

- Lines 44-48 (JSON path)
- Lines 59-63 (text path)

**Solution**: Extract common logic:

```python
# Count tokens for all files first
results = []
for filepath_str in file_paths:
    filepath = Path(filepath_str)
    count = count_tokens_for_file(filepath, resolved_model)
    results.append(TokenCount(path=str(filepath), count=count))

# Then format output
if json_output:
    # ... format as JSON
else:
    # ... format as text
```

---

#### 4. Missing File Reading Error Handling

**Location**: `src/claudeutils/tokens.py:123`

```python
def count_tokens_for_file(path: Path, model: str) -> int:
    content = path.read_text()  # ❌ Can raise UnicodeDecodeError, PermissionError, etc.
```

**Solution**: Add error handling:

```python
try:
    content = path.read_text()
except (UnicodeDecodeError, PermissionError) as e:
    raise ClaudeUtilsError(f"Failed to read {path}: {e}") from e
```

### Medium Priority Issues

#### 5. Unused Cache Metadata

**Location**: `src/claudeutils/tokens.py:29`

`CacheData.fetched_at` is stored but never used. Cache TTL uses file modification time
(line 62) instead.

**Options**:

1. Use `fetched_at` for TTL check (more reliable)
2. Remove `fetched_at` field (simpler)

---

#### 6. Incomplete API Error Handling

**Location**: `src/claudeutils/tokens.py:134-137`

```python
except AuthenticationError as e:
    raise ApiAuthenticationError from e
except RateLimitError as e:
    raise ApiRateLimitError from e
# ❌ Missing: NetworkError, APIError, etc.
```

**Solution**: Add catch-all for other API errors:

```python
except (AuthenticationError, ...) as e:
    # ... existing handlers
except APIError as e:
    raise ClaudeUtilsError(f"API error: {e}") from e
```

---

#### 7. Hardcoded Cache TTL

**Location**: `src/claudeutils/tokens.py:59`

```python
cache_ttl_hours = 24  # ❌ Hardcoded
```

**Solution**: Make it a module constant:

```python
CACHE_TTL_HOURS = 24  # At module level
```

### Minor Issues

#### 8. Missing Operation Logging

Logger is defined but barely used. Consider adding:

- Debug: cache hits/misses
- Debug: API calls
- Info: file processing progress

#### 9. Undocumented Case-Insensitive Matching

**Location**: `src/claudeutils/tokens.py:40-53`

Model alias matching is case-insensitive (line 70) but not documented in docstring.

---

## Test Code Review

### Critical Test Issues

#### 1. Using unittest.mock Instead of pytest-mock

**Affected Files**: All test files

- `tests/test_tokens_count.py:4` - `from unittest.mock import Mock`
- `tests/test_tokens_resolve.py:8` - `from unittest.mock import Mock`
- `tests/test_cli_tokens.py:8` - `from unittest.mock import patch`

**Problem**: Not following pytest best practices. Should use `mocker` fixture.

**Solution**:

```python
# ❌ Current
from unittest.mock import Mock

def test_something(tmp_path, monkeypatch):
    mock_client = Mock()
    monkeypatch.setattr("claudeutils.tokens.Anthropic", Mock(return_value=mock_client))

# ✅ Should be
def test_something(tmp_path, mocker):
    mock_client = mocker.Mock()
    mocker.patch("claudeutils.tokens.Anthropic", return_value=mock_client)
```

**Impact**: All 8 test files need updating.

---

#### 2. No autospec on Mocks (Type Safety Issue)

**Instances**: 16+ occurrences across test files

**Problem**: Mocks without `autospec=True` or `spec=` accept ANY method call, allowing
invalid usage to pass tests.

**Current pattern** (test_tokens_count.py:35-38):

```python
mock_client = Mock()  # ❌ Accepts ANY method/attribute
mock_response = Mock()  # ❌ No validation
mock_response.input_tokens = 5
mock_client.messages.count_tokens.return_value = mock_response
```

**Solution**:

```python
from anthropic import Anthropic

def test_something(mocker):
    # Option 1: spec parameter
    mock_client = mocker.Mock(spec=Anthropic)

    # Option 2: autospec (better)
    mocker.patch("claudeutils.tokens.Anthropic", autospec=True)
```

**Impact**: Tests can currently pass even with invalid API usage.

---

#### 3. Massive Code Duplication in Test Setup

**Location**: Primarily `tests/test_tokens_count.py`

**Repeated 8 times** (lines 35-44, 78-87, 126-134, 162-166, 193-202, 227-235, 266-280,
327-344):

```python
# Mock Anthropic client
mock_client = Mock()
mock_response = Mock()
mock_response.input_tokens = 5
mock_client.messages.count_tokens.return_value = mock_response

# Patch the Anthropic client initialization
monkeypatch.setattr(
    "claudeutils.tokens.Anthropic",
    Mock(return_value=mock_client),
)
```

**Solution**: Create fixture:

```python
@pytest.fixture
def mock_anthropic_client(mocker):
    """Create a mocked Anthropic client with configurable token count."""
    from anthropic import Anthropic

    def _make_client(token_count: int = 5, side_effect=None):
        mock_response = mocker.Mock()
        mock_response.input_tokens = token_count

        mock_client = mocker.Mock(spec=Anthropic)
        if side_effect:
            mock_client.messages.count_tokens.side_effect = side_effect
        else:
            mock_client.messages.count_tokens.return_value = mock_response

        mocker.patch(
            "claudeutils.tokens.Anthropic",
            return_value=mock_client,
            autospec=True
        )
        return mock_client

    return _make_client

# Usage:
def test_count_tokens(tmp_path, mock_anthropic_client):
    mock_anthropic_client(token_count=42)
    # ... rest of test
```

**Impact**: Would reduce test code by ~40%.

---

#### 4. Duplicated Test File Creation

**Location**: `tests/test_tokens_count.py`

**Repeated 7 times**:

```python
test_file = tmp_path / "test.md"
test_file.write_text("Hello world")
```

**Solution**: Create fixture:

```python
@pytest.fixture
def test_markdown_file(tmp_path):
    """Create a test markdown file with content."""
    def _make_file(content: str = "Hello world", filename: str = "test.md"):
        file_path = tmp_path / filename
        file_path.write_text(content)
        return file_path
    return _make_file

# Usage:
def test_something(test_markdown_file, mock_anthropic_client):
    test_file = test_markdown_file("Custom content")
    # ...
```

---

#### 5. Duplicated Models API Mocking

**Location**: `tests/test_tokens_resolve.py`

The models.list() API mocking pattern is repeated 6+ times.

**Solution**: Create fixture:

```python
@pytest.fixture
def mock_models_api(mocker):
    """Mock the Anthropic models.list() API."""
    from anthropic import Anthropic
    from datetime import datetime

    def _setup(models: list[dict] | None = None, raise_error=None):
        if raise_error:
            mock_client = mocker.Mock(spec=Anthropic)
            mock_client.models.list.side_effect = raise_error
            return mock_client

        if models is None:
            models = [{"id": "claude-sonnet-4-5-20250929",
                      "created_at": "2025-09-29T00:00:00Z"}]

        mock_model_objs = [
            mocker.Mock(
                id=m["id"],
                created_at=datetime.fromisoformat(m["created_at"])
            )
            for m in models
        ]

        mock_client = mocker.Mock(spec=Anthropic)
        mock_client.models.list.return_value = mock_model_objs
        return mock_client

    return _setup

# Usage:
def test_resolve_alias(tmp_path, mock_models_api):
    client = mock_models_api([
        {"id": "claude-haiku-4-5-20251001", "created_at": "2025-10-01T00:00:00Z"}
    ])
    # ...
```

---

#### 6. Duplicated CLI Patch Patterns

**Location**: `tests/test_cli_tokens.py`

Lines 38-42, 78-82, 103-107 all use identical patterns.

**Solution**: Create fixture:

```python
@pytest.fixture
def mock_token_counting(mocker):
    """Mock token counting dependencies for CLI tests."""
    def _setup(model_id: str = "claude-sonnet-4-5-20250929",
               counts: int | list[int] = 42):
        if isinstance(counts, int):
            counts = [counts]

        mocker.patch(
            "claudeutils.tokens_cli.resolve_model_alias",
            return_value=model_id
        )
        mocker.patch(
            "claudeutils.tokens_cli.count_tokens_for_file",
            side_effect=counts
        )
    return _setup
```

---

### Test Issues Summary

| Issue                                      | Count         | Files Affected         | Priority     |
| ------------------------------------------ | ------------- | ---------------------- | ------------ |
| Using unittest.mock instead of pytest-mock | 3 files       | All test files         | **Critical** |
| Missing autospec/spec on mocks             | 16+ instances | test_tokens_*.py       | **Critical** |
| Duplicated mock setup (Anthropic client)   | 8 instances   | test_tokens_count.py   | **High**     |
| Duplicated mock setup (models API)         | 6+ instances  | test_tokens_resolve.py | **High**     |
| Duplicated test file creation              | 7 instances   | test_tokens_count.py   | **Medium**   |
| Duplicated patch patterns                  | 3 instances   | test_cli_tokens.py     | **Medium**   |

---

## Recommendations

### Must Fix Before Committing (Critical)

**Implementation:**

1. ✅ Fix inefficient client creation (#1) - `tokens.py:128`
2. ✅ Add exception handling in CLI (#2) - `tokens_cli.py:19-67`
3. ✅ Eliminate duplicate code in CLI (#3) - `tokens_cli.py:43-66`
4. ✅ Add file reading error handling (#4) - `tokens.py:123`

**Tests:**

5. ✅ Replace `unittest.mock` with `pytest-mock` (use `mocker` fixture)
6. ✅ Add `autospec=True` or `spec=` to all mocks

### Should Fix (High Priority)

**Implementation:**

7. ⚠️ Use or remove `fetched_at` field (#5) - `tokens.py:29`
8. ⚠️ Handle all API errors (#6) - `tokens.py:134-137`
9. ⚠️ Make cache TTL configurable (#7) - `tokens.py:59`

**Tests:**

10. ⚠️ Create `mock_anthropic_client` fixture
11. ⚠️ Create `mock_models_api` fixture
12. ⚠️ Create `test_markdown_file` fixture
13. ⚠️ Consolidate CLI patch patterns with fixture

### Nice to Have (Low Priority)

14. 💡 Add operation logging (#8)
15. 💡 Document case-insensitive matching (#9)

---

## File-by-File Changes Required

### Implementation Files

#### `src/claudeutils/tokens.py`

- [ ] Refactor `count_tokens_for_file` to accept optional client parameter
- [ ] Refactor `count_tokens_for_files` to create client once
- [ ] Add file reading error handling with try/except
- [ ] Add catch-all for API errors
- [ ] Move `cache_ttl_hours = 24` to module constant
- [ ] Document case-insensitive matching in `resolve_model_alias` docstring
- [ ] Consider: use `fetched_at` or remove it

#### `src/claudeutils/tokens_cli.py`

- [ ] Extract common token counting logic from JSON/text paths
- [ ] Add try/except for `ApiAuthenticationError`
- [ ] Add try/except for `ApiRateLimitError`
- [ ] Add try/except for `ModelResolutionError`
- [ ] Consider: create client once and pass to counting functions

### Test Files

#### `tests/test_tokens_count.py`

- [ ] Remove `from unittest.mock import Mock`
- [ ] Add `mocker` fixture to all test functions
- [ ] Add `spec=Anthropic` to all mock clients
- [ ] Create `mock_anthropic_client` fixture
- [ ] Create `test_markdown_file` fixture
- [ ] Update all 8 tests to use new fixtures
- [ ] Verify autospec catches invalid API usage

#### `tests/test_tokens_resolve.py`

- [ ] Remove `from unittest.mock import Mock`
- [ ] Add `mocker` fixture to all test functions
- [ ] Create `mock_models_api` fixture
- [ ] Update all tests to use new fixture with spec
- [ ] Add autospec to Anthropic client mocks

#### `tests/test_cli_tokens.py`

- [ ] Remove `from unittest.mock import patch`
- [ ] Add `mocker` fixture to all test functions
- [ ] Create `mock_token_counting` fixture
- [ ] Update all tests to use new fixture
- [ ] Consider adding tests for exception handling

#### `tests/test_tokens_integration.py`

- [ ] Add `mocker` fixture if needed
- [ ] Verify e2e test still works after refactoring

#### New file: `tests/conftest.py` (if needed)

- [ ] Consider adding shared fixtures here if used across multiple test files

---

## Impact Assessment

### Code Quality Improvements

- **Test code reduction**: ~40% fewer lines via fixtures
- **Type safety**: autospec prevents invalid API usage bugs
- **Maintainability**: Single source of truth for mock setup
- **Performance**: Client reuse reduces overhead
- **User experience**: Friendly error messages instead of tracebacks

### Risk Assessment

- **Low risk**: Changes are mostly refactoring with existing test coverage
- **Test coverage**: Comprehensive (unit + integration + e2e)
- **Breaking changes**: None (all internal refactoring)

### Effort Estimate

- **Critical fixes (1-6)**: ~2-3 hours
- **High priority fixes (7-13)**: ~2-3 hours
- **Total**: ~4-6 hours for all recommended changes

---

## Next Steps for Planning Agent

### Phase 1: Critical Fixes (Required for Commit)

1. Fix implementation issues #1-4
2. Migrate tests to pytest-mock with autospec (#5-6)
3. Run full test suite to verify
4. Commit with message: "feat: add token counter with critical fixes"

### Phase 2: Test Quality Improvements (Follow-up PR)

1. Create shared test fixtures (#10-13)
2. Refactor tests to use fixtures
3. Verify test coverage maintained
4. Commit with message: "test: refactor token counter tests with fixtures"

### Phase 3: Polish (Optional Follow-up)

1. Address medium/low priority items (#7-9, #14-15)
2. Consider additional improvements discovered during implementation
3. Update documentation if needed

### Context for Planning

- **Branch status**: `token` branch was squash merged but not committed
- **Git status**: Multiple modified and new files staged
- **Test framework**: pytest with pytest-mock available
- **Dependencies**: anthropic SDK, pydantic, platformdirs
- **Related files**: See git status for complete list of affected files

### Questions for Planning Agent

1. Should Phase 1 and Phase 2 be combined into a single commit, or separate PRs?
2. Should we create a `tests/conftest.py` for shared fixtures?
3. Should cache TTL be configurable via environment variable or just a constant?
4. Should we add more comprehensive API error handling or keep it minimal?

---

## Appendix: Key Locations

### Implementation

- Token counting: `src/claudeutils/tokens.py`
- CLI handler: `src/claudeutils/tokens_cli.py`
- Main CLI: `src/claudeutils/cli.py` (integration point)
- Exceptions: `src/claudeutils/exceptions.py`

### Tests

- Token counting tests: `tests/test_tokens_count.py`
- Model resolution tests: `tests/test_tokens_resolve.py`
- CLI tests: `tests/test_cli_tokens.py`
- Integration tests: `tests/test_tokens_integration.py`
- CLI help tests: `tests/test_cli_help.py` (may need updating)

### Related Files

- Project config: `pyproject.toml`
- Lock file: `uv.lock`
- Documentation: `README.md`, `AGENTS.md`, etc.
