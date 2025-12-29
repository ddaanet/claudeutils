# Plan: Token Counter Tool

**Goal:** Implement `tokens` subcommand to count tokens in files using Anthropic API.

**Priority:** HIGH - Required before module composition to validate prompt size
assumptions.

**Approach:** Test-Driven Development with incremental capability building.

---

## Architecture

### CLI Interface

```bash
# Single file
uv run claudeutils tokens sonnet file.md

# Multiple files
uv run claudeutils tokens opus file1.md file2.md

# Output format
uv run claudeutils tokens haiku file.md           # text (default)
uv run claudeutils tokens sonnet file.md --json   # JSON format
```

**Note:** Model is first positional argument because token counts vary by model.

### Implementation Modules

- `src/claudeutils/tokens.py` - Core token counting logic
- `src/claudeutils/tokens_cli.py` - CLI handler for tokens subcommand
- `tests/test_tokens_count.py` - Unit tests for count_tokens_for_file function
- `tests/test_tokens_resolve.py` - Unit tests for resolve_model_alias function
- `tests/test_tokens_integration.py` - End-to-end integration tests
- `tests/test_cli_tokens.py` - Integration tests for CLI
- `cli.py` - Add `tokens` subcommand handler

### Dependencies

- `anthropic` - Official Anthropic SDK for API access
- `platformdirs` - Cross-platform cache directory resolution

---

## Test Specification

### Group 0: End-to-End Integration Test

**Module:** `tests/test_tokens_integration.py`

**Note:** This test requires real API keys and network access. Mark as `xfail`
initially.

#### Test 0.1: End-to-end token counting with alias resolution

- **Given:** Environment has valid `ANTHROPIC_API_KEY`, no models cache exists, real
  file "fixture.md" with known content, model="sonnet" (unversioned alias)
- **When:** `uv run claudeutils tokens sonnet fixture.md` executed
- **Then:**
  - Exits 0
  - First line shows resolved model ID (e.g., "Using model: claude-sonnet-4-5-20250929")
  - Second line shows file with token count
  - Cache file created in user directory

**Requires:**

- **Real API calls** - no mocking
- Models API call to resolve "sonnet" alias
- Count tokens API call
- Cache writing
- Text output with model ID on first line

**Does NOT require:** Multiple files, JSON format, error handling

**Mark as:** `@pytest.mark.xfail` initially, remove xfail after full implementation

**Checkpoint 0:** Run `just test tests/test_tokens_integration.py` - expect xfail
initially

---

### Group 1: Core Token Counting (Unit Tests)

**Module:** `tests/test_tokens_count.py`

#### Test 1.1: Count tokens for simple text

- **Given:** File with content "Hello world", model="sonnet"
- **When:** `count_tokens_for_file(path, model)` called
- **Then:** Returns integer token count > 0

**Requires:**

- `count_tokens_for_file(path: Path, model: str)` function signature
- Read file content
- Mock Anthropic API call with model parameter
- Return integer count

**Does NOT require:** Multiple files, CLI, model validation

#### Test 1.2: Count tokens for markdown with code blocks

- **Given:** File with markdown content including code block, model="opus"
- **When:** `count_tokens_for_file(path, model)` called
- **Then:** Returns token count reflecting full content

**Requires:**

- Handle multi-line content
- Preserve whitespace/formatting
- Pass model to API

**Does NOT require:** Error handling, API key validation

#### Test 1.3: Handle empty file

- **Given:** Empty file, model="haiku"
- **When:** `count_tokens_for_file(path, model)` called
- **Then:** Returns 0

**Requires:**

- Handle empty content case
- Don't make API call for empty files

**Does NOT require:** Special error handling

**Note:** FileNotFoundError is stdlib behavior, no explicit test needed.

**Checkpoint 1:** Run `just test tests/test_tokens_count.py` - awaiting approval

---

### Group 2: Model Alias Resolution

**Module:** `tests/test_tokens_resolve.py`

#### Test 2.1: Pass Anthropic aliases through unchanged

- **Given:** model="claude-sonnet-4-5" (official Anthropic alias)
- **When:** `resolve_model_alias(model)` called
- **Then:** Returns same ID unchanged (no API call, no cache check)

**Requires:**

- New function `resolve_model_alias(model: str, client: Anthropic, cache_dir: Path)`
- Detect if model starts with "claude-"
- Short-circuit and return unchanged
- **MUST NOT** call API or check cache for official aliases

**Does NOT require:** Validation of model ID format

#### Test 2.2: Resolve unversioned alias from fresh cache

- **Given:** Cache file exists with valid models list (created < 24h ago), includes
  `claude-haiku-4-5-20251001` and `claude-3-5-haiku-20241022`, model="haiku"
- **When:** `resolve_model_alias(model)` called
- **Then:** Returns `claude-haiku-4-5-20251001` from cache (no API call)

**Requires:**

- Read cache file from user directory
- Check cache timestamp against 24-hour TTL
- Parse cached models list
- Filter models where ID contains "haiku" (case-insensitive)
- Select latest by `created_at` timestamp
- Return full model ID

**Does NOT require:** Writing cache (already exists), API call

#### Test 2.3: Resolve unversioned alias with cache miss

- **Given:** No cache file exists, mock API returns models list, model="sonnet"
- **When:** `resolve_model_alias(model)` called
- **Then:** Queries API, writes cache, returns latest sonnet model ID

**Requires:**

- Call `client.models.list()` API endpoint
- Write models list + timestamp to cache file as JSON
- Create cache directory if needed
- Return resolved model ID

**Does NOT require:** Cache expiry logic (tested separately)

#### Test 2.4: Resolve with expired cache

- **Given:** Cache file exists but created > 24h ago, model="opus"
- **When:** `resolve_model_alias(model)` called
- **Then:** Ignores stale cache, queries API, updates cache

**Requires:**

- Check cache file modification time
- If > 24 hours old, treat as cache miss
- Query API and update cache file

**Does NOT require:** Preserving old cache data

#### Test 2.5: Handle corrupted cache file

- **Given:** Cache file exists but contains invalid JSON, model="haiku"
- **When:** `resolve_model_alias(model)` called
- **Then:** Treats as cache miss, queries API, overwrites corrupted cache

**Requires:**

- Try/except around cache file reading and JSON parsing
- On error, log warning and proceed with API query
- Overwrite corrupted cache with fresh data

**Does NOT require:** Attempting to repair corrupted cache

#### Test 2.6: Create cache directory if missing

- **Given:** Cache directory does not exist, model="sonnet"
- **When:** `resolve_model_alias(model)` called
- **Then:** Cache directory is created, cache file written successfully

**Requires:**

- Check if cache directory exists
- Create directory (including parents) if missing
- Use platform-appropriate permissions

**Does NOT require:** Error handling for permission denied

**Checkpoint 2:** Run `just test tests/test_tokens_resolve.py` - awaiting approval

---

### Group 3: API Error Handling

**Module:** `tests/test_tokens_count.py` and `tests/test_tokens_resolve.py` (mixed -
tests for both functions)

#### Test 3.1: Handle unknown model alias

- **Given:** API returns models list, model="unknown-alias"
- **When:** `resolve_model_alias(model)` called
- **Then:** Returns "unknown-alias" unchanged (pass through to API)

**Requires:**

- If no models match the alias pattern, return original input
- Let Anthropic API handle invalid model error

**Does NOT require:** Custom error message for unknown alias

#### Test 3.2: Fail when models API error prevents resolution

- **Given:** `client.models.list()` raises API error, model="sonnet" (unversioned alias)
- **When:** `resolve_model_alias(model)` called
- **Then:** Raises RuntimeError with message explaining models API is unreachable and
  cannot resolve alias (transient failure, suggest retry)

**Requires:**

- Try/except around models.list() call
- On API error, raise RuntimeError with clear message about transient failure
- **MUST** fail for unversioned aliases when API unreachable

**Does NOT require:** Retry logic, suggesting full model IDs

#### Test 3.3: Handle API authentication error

- **Given:** Invalid/missing API key
- **When:** `count_tokens_for_file(path, model)` called
- **Then:** Raises ValueError with clear message

**Requires:**

- Try/except for API authentication errors
- Descriptive error message

**Does NOT require:** Retry logic, key validation

#### Test 3.4: Handle API rate limit error

- **Given:** API returns rate limit error
- **When:** `count_tokens_for_file(path, model)` called
- **Then:** Raises RuntimeError with rate limit message

**Requires:**

- Catch rate limit exceptions
- Specific error for rate limits

**Does NOT require:** Retry/backoff logic

**Checkpoint 3:** Run
`just test tests/test_tokens_count.py tests/test_tokens_resolve.py` - awaiting approval

---

### Group 4: Multiple Files and Aggregation

**Module:** `tests/test_tokens_count.py`

#### Test 4.1: Count tokens for multiple files

- **Given:** Two files: "Hello" (file1), "World" (file2), model="sonnet"
- **When:** `count_tokens_for_files(paths, model)` called
- **Then:** Returns list of TokenCount objects with per-file counts

**Requires:**

- New function `count_tokens_for_files(paths: list[Path], model: str)`
- TokenCount data class/model: `{path: str, count: int}`
- Loop over files, collect results

**Does NOT require:** Total calculation

#### Test 4.2: Calculate total across files

- **Given:** TokenCount results for 3 files: [5, 10, 8]
- **When:** `calculate_total(results)` called
- **Then:** Returns 23

**Requires:**

- New function `calculate_total(results: list[TokenCount])`
- Sum token counts

**Does NOT require:** File I/O, API calls

#### Test 4.3: Preserve file order in results

- **Given:** Files [b.md, a.md, c.md] in that order, model="haiku"
- **When:** `count_tokens_for_files(paths, model)` called
- **Then:** Results maintain input order [b.md, a.md, c.md]

**Requires:**

- Process files in input order
- Don't sort results

**Does NOT require:** Path normalization

**Checkpoint 4:** Run `just test tests/test_tokens_count.py` - awaiting approval

---

### Group 5: CLI Integration

**Module:** `tests/test_cli_tokens.py`

#### Test 5.1: CLI requires model argument

- **Given:** File "test.md" exists
- **When:** `uv run claudeutils tokens test.md` executed (no model)
- **Then:** Exits 1, stderr shows error about missing model argument

**Requires:**

- Add `tokens` subparser in cli.py
- Model as first positional argument
- Error message for missing model

**Does NOT require:** File processing

#### Test 5.2: CLI accepts single file with model

- **Given:** File "test.md" exists
- **When:** `uv run claudeutils tokens sonnet test.md` executed
- **Then:** Exits 0, stdout contains filename and count

**Requires:**

- `handle_tokens()` function
- Wire up to tokens module
- Text output format
- Parse model from first positional arg

**Does NOT require:** JSON format

#### Test 5.3: CLI reports missing file

- **Given:** File "missing.md" does not exist
- **When:** `uv run claudeutils tokens haiku missing.md` executed
- **Then:** Exits 1, stderr contains "missing.md" and error message

**Requires:**

- Catch FileNotFoundError
- Print to stderr
- Exit with code 1

**Does NOT require:** Detailed error messages

#### Test 5.4: CLI handles multiple files

- **Given:** Files "a.md" and "b.md" exist
- **When:** `uv run claudeutils tokens opus a.md b.md` executed
- **Then:** Stdout shows both files with counts + total

**Requires:**

- Multiple file path arguments after model
- Display per-file counts
- Display total at end

**Does NOT require:** Table formatting

**Checkpoint 5:** Run `just test tests/test_cli_tokens.py` - awaiting approval

---

### Group 6: Output Formats

**Module:** `tests/test_cli_tokens.py` (continued)

#### Test 6.1: Default text format shows human-readable output with model ID

- **Given:** File "test.md" with 42 tokens, model="sonnet" resolves to
  "claude-sonnet-4-5-20250929"
- **When:** `uv run claudeutils tokens sonnet test.md` executed
- **Then:** Output contains:

```
Using model: claude-sonnet-4-5-20250929
test.md: 42 tokens
```

**Requires:**

- First line: "Using model: {resolved_model_id}"
- Subsequent lines: "{path}: {count} tokens"
- Last line (if multiple files): "Total: {sum} tokens"

**Does NOT require:** Column alignment, colors

#### Test 6.2: JSON format outputs structured data with model ID

- **Given:** File "test.md" with 42 tokens, model="haiku" resolves to
  "claude-haiku-4-5-20251001"
- **When:** `uv run claudeutils tokens haiku test.md --json` executed
- **Then:** Output is valid JSON:

```json
{"model": "claude-haiku-4-5-20251001", "files": [{"path": "test.md", "count": 42}], "total": 42}
```

**Requires:**

- Add `--json` flag (option, not positional)
- JSON serialization of TokenCount
- JSON structure with "model", "files" and "total" keys
- Include resolved model ID in output

**Does NOT require:** Pretty-printing

#### Test 6.3: JSON format with multiple files

- **Given:** Two files with counts [10, 20], model="opus" resolves to
  "claude-opus-4-5-20251101"
- **When:** `uv run claudeutils tokens opus file1 file2 --json` executed
- **Then:** JSON includes model, files, and total:

```json
{"model": "claude-opus-4-5-20251101", "files": [...], "total": 30}
```

**Requires:**

- Array of per-file results in JSON
- Total calculation in JSON output
- Model ID in output

**Does NOT require:** Additional metadata

**Checkpoint 6:** Run `just test tests/test_cli_tokens.py` - awaiting approval

---

### Group 7: API Key Management

**Module:** `tests/test_tokens_count.py`

#### Test 7.1: Read API key from environment

- **Given:** `ANTHROPIC_API_KEY` environment variable set
- **When:** Anthropic client initialized
- **Then:** Client uses environment variable value

**Requires:**

- Anthropic SDK's default env var handling
- **MUST NOT** implement custom key reading

**Does NOT require:** Custom env var logic, key validation

#### Test 7.2: Error message guides user to set API key

- **Given:** No `ANTHROPIC_API_KEY` environment variable
- **When:** Token counting attempted
- **Then:** Error message includes "ANTHROPIC_API_KEY" and setup instructions

**Requires:**

- Catch authentication error
- Custom error message with guidance

**Does NOT require:** Interactive prompts, key storage

**Checkpoint 7:** Run `just test` - awaiting approval

**Note:** Group 8 tests are in a separate module (`tests/test_cli_help.py`) to isolate
help text validation.

---

### Group 8: Help Text and Documentation

**Module:** `tests/test_cli_help.py`

#### Test 8.1: Help text is complete and accurate

- **Given:** CLI installed
- **When:** `uv run claudeutils tokens --help` executed
- **Then:** Help contains expected text (see full text below)

**Requires:**

- Exact help text specified below
- **MUST NOT** delegate prose writing to haiku

**Full help text to implement:**

```
usage: claudeutils tokens [-h] [--json] {haiku,sonnet,opus} FILE [FILE ...]

Count tokens in files using Anthropic API. Requires ANTHROPIC_API_KEY
environment variable.

positional arguments:
  {haiku,sonnet,opus}   Model alias for token counting. Aliases automatically
                        resolve to the latest available model version. You may
                        also provide a full model ID like claude-sonnet-4-5.
                        Token counts vary by model.
  FILE                  File path(s) to count tokens

options:
  -h, --help            show this help message and exit
  --json                Output JSON format instead of text

Examples:
  uv run claudeutils tokens sonnet prompt.md
  uv run claudeutils tokens opus file1.md file2.md --json
  uv run claudeutils tokens claude-sonnet-4-5-20250929 prompt.md
```

**Checkpoint 8:** Run `just test tests/test_cli_help.py` - awaiting approval

---

## Implementation Order

**Note:** Start with xfail integration test, then implement incrementally via unit
tests.

1. Group 0: End-to-end integration test (xfail initially)
2. Group 1: Core token counting (unit tests)
3. Group 2: Model alias resolution (runtime probing)
4. Group 3: API error handling
5. Group 4: Multiple files and aggregation
6. Group 5: CLI integration
7. Group 6: Output formats (includes model ID in output)
8. Group 7: API key management
9. Group 8: Help text

---

## Design Decisions to Document

After implementation, add to `agents/DESIGN_DECISIONS.md`:

### Model as First Positional Argument

**Decision:** Model is first positional argument in CLI, required parameter in functions

**Rationale:** Token counts vary by model; explicit model choice ensures accurate counts

**Implementation:** `count_tokens_for_file(path: Path, model: str)` and CLI positional
arg

### Model Alias Support

**Decision:** Hybrid approach - support Anthropic's official aliases directly, with
runtime probing fallback for unversioned aliases

**Rationale:**

- Anthropic provides official aliases like `claude-sonnet-4-5` that auto-update to
  latest snapshots
- Power users can use full model IDs (`claude-sonnet-4-5-20250929`) or official aliases
  (`claude-sonnet-4-5`)
- Casual users can use simple aliases ("sonnet", "haiku", "opus") which resolve via
  runtime probing
- 24-hour cache avoids repeated API calls

**Implementation:**

1. **Pass-through**: If model starts with "claude-", use unchanged (no resolution
   needed)
2. **Unversioned alias resolution**: For simple aliases like "sonnet":
   - Check cache first (24-hour TTL in user config directory)
   - If cache miss/expired, query `client.models.list()` API
   - Filter models where ID contains the alias (case-insensitive)
   - Select latest by `created_at` timestamp
   - Cache full model list with timestamp
3. **Fallback**: If alias not found or API error, pass through unchanged (API will
   error)
4. **Cache location**: Use platform-appropriate user cache directory
   - Unix/Linux: `~/.cache/claudeutils/models_cache.json`
   - macOS: `~/Library/Caches/claudeutils/models_cache.json`
   - Windows: `%LOCALAPPDATA%\claudeutils\models_cache.json`

### Anthropic API Integration

**Decision:** Use official Anthropic SDK with default environment variable handling

**Rationale:** SDK handles API details, retries, error types; no custom HTTP logic
needed

**Implementation:** `tokens.py:count_tokens_for_file()`

### Empty File Optimization

**Decision:** Return 0 for empty files without API call

**Rationale:** Avoid unnecessary API calls; empty content always has 0 tokens across all
models

### Output Format Default

**Decision:** Human-readable text format by default, JSON optional; include resolved
model ID in all outputs

**Rationale:**

- Text format for humans, JSON for tools (matches existing CLI commands)
- Show resolved model ID so users know which exact model version was used
- Critical for debugging and reproducibility (especially when using aliases that
  auto-update)

### No Glob Expansion (Initial Release)

**Decision:** Defer glob pattern expansion to future release

**Rationale:** Simplify initial implementation; users can use shell expansion if needed

**Future:** May add `expand_glob_patterns()` in later version

---

## Notes for Implementation

- Keep `tokens.py` under 300 lines (hard limit: 400)
- Use Pydantic for TokenCount model (consistency with codebase)
- Follow existing error handling pattern (stderr + exit 1)
- Use `Path` for all file operations (consistency)
- Mock Anthropic client in tests (no real API calls for count_tokens; mock models.list()
  for alias resolution)
- Add fixtures in `tests/fixtures/` for test files

### Model Resolution Implementation

- **Pass-through:** If model starts with "claude-", return unchanged (supports both full
  IDs and official aliases)
- **Cache location:** Use `platformdirs` library to get platform-appropriate cache
  directory
- **Cache format:** JSON file with structure:

```json
{
  "fetched_at": "2025-12-29T10:30:00Z",
  "models": [
    {"id": "claude-sonnet-4-5-20250929", "created_at": "2025-09-29T00:00:00Z", "display_name": "Claude Sonnet 4.5", ...},
    ...
  ]
}
```

- **Cache TTL:** 24 hours from `fetched_at` timestamp
- **Alias matching:** Filter models where `id` contains the alias string
  (case-insensitive substring match)
- **Latest selection:** Sort filtered models by `created_at` timestamp descending,
  return first match
- **Error handling:** If cache corrupted, treat as cache miss; if API fails, pass
  through unchanged
- **Dependencies:** Add `platformdirs` to project dependencies for cache directory
  resolution
