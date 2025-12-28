# Plan: Token Counter Tool

**Goal:** Implement `tokens` subcommand to count tokens in files using Anthropic API.

**Priority:** HIGH - Required before module composition to validate prompt size
assumptions.

**Approach:** Test-Driven Development with incremental capability building.

---

## Research: Model Alias Support

**Question:** Does Anthropic API support model aliases ("haiku", "sonnet", "opus") or
require full model IDs?

**Action:** Before implementing, verify:

1. Test if `anthropic.count_tokens(model="sonnet", ...)` works
2. Test if `anthropic.count_tokens(model="claude-sonnet-4-5-20250929", ...)` works
3. Document which format is supported

**Impact on plan:** If aliases NOT supported, add model name mapping in implementation.

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
- `tests/test_tokens.py` - Unit tests for token counting
- `tests/test_cli_tokens.py` - Integration tests for CLI
- `cli.py` - Add `tokens` subcommand handler

### Dependencies

- `anthropic` - Official Anthropic SDK for API access

---

## Test Specification

### Group 1: Core Token Counting (Unit Tests)

**Module:** `tests/test_tokens.py`

#### Test 1.1: Count tokens for simple text

**Given:** File with content "Hello world", model="sonnet" **When:**
`count_tokens_for_file(path, model)` called **Then:** Returns integer token count > 0

**Requires:**

- `count_tokens_for_file(path: Path, model: str)` function signature
- Read file content
- Mock Anthropic API call with model parameter
- Return integer count

**Does NOT require:** Multiple files, CLI, model validation

#### Test 1.2: Count tokens for markdown with code blocks

**Given:** File with markdown content including code block, model="opus" **When:**
`count_tokens_for_file(path, model)` called **Then:** Returns token count reflecting
full content

**Requires:**

- Handle multi-line content
- Preserve whitespace/formatting
- Pass model to API

**Does NOT require:** Error handling, API key validation

#### Test 1.3: Handle empty file

**Given:** Empty file, model="haiku" **When:** `count_tokens_for_file(path, model)`
called **Then:** Returns 0

**Requires:**

- Handle empty content case
- Don't make API call for empty files

**Does NOT require:** Special error handling

**Note:** FileNotFoundError is stdlib behavior, no explicit test needed.

**Checkpoint 1:** Run `just test tests/test_tokens.py` - awaiting approval

---

### Group 2: Model Parameter Handling

**Module:** `tests/test_tokens.py` (continued)

#### Test 2.1: Pass model parameter to API

**Given:** File with content, model="sonnet" **When:**
`count_tokens_for_file(path, model)` called **Then:** API call includes model parameter

**Requires:**

- Pass model string to Anthropic API
- Mock verifies model parameter

**Does NOT require:** Model validation, alias resolution

#### Test 2.2: Different models may return different counts

**Given:** Same file, model="haiku" vs model="opus" **When:** Both
`count_tokens_for_file()` calls made **Then:** Counts may differ (test framework accepts
any positive integer)

**Requires:**

- Support multiple model values
- No hardcoded model assumptions

**Does NOT require:** Actual different counts (mocked)

**Checkpoint 2:** Run `just test tests/test_tokens.py` - awaiting approval

---

### Group 3: API Error Handling

**Module:** `tests/test_tokens.py` (continued)

#### Test 3.1: Handle API authentication error

- **Given:** Invalid/missing API key **When:** `count_tokens_for_file(path, model)`
  called
- **Then:** Raises ValueError with clear message

**Requires:**

- Try/except for API authentication errors
- Descriptive error message

**Does NOT require:** Retry logic, key validation

#### Test 3.2: Handle API rate limit error

**Given:** API returns rate limit error **When:** `count_tokens_for_file(path, model)`
called **Then:** Raises RuntimeError with rate limit message

**Requires:**

- Catch rate limit exceptions
- Specific error for rate limits

**Does NOT require:** Retry/backoff logic

**Checkpoint 3:** Run `just test tests/test_tokens.py` - awaiting approval

---

### Group 4: Multiple Files and Aggregation

**Module:** `tests/test_tokens.py` (continued)

#### Test 4.1: Count tokens for multiple files

**Given:** Two files: "Hello" (file1), "World" (file2), model="sonnet" **When:**
`count_tokens_for_files(paths, model)` called **Then:** Returns list of TokenCount
objects with per-file counts

**Requires:**

- New function `count_tokens_for_files(paths: list[Path], model: str)`
- TokenCount data class/model: `{path: str, count: int}`
- Loop over files, collect results

**Does NOT require:** Total calculation

#### Test 4.2: Calculate total across files

**Given:** TokenCount results for 3 files: [5, 10, 8] **When:**
`calculate_total(results)` called **Then:** Returns 23

**Requires:**

- New function `calculate_total(results: list[TokenCount])`
- Sum token counts

**Does NOT require:** File I/O, API calls

#### Test 4.3: Preserve file order in results

**Given:** Files [b.md, a.md, c.md] in that order, model="haiku" **When:**
`count_tokens_for_files(paths, model)` called **Then:** Results maintain input order
[b.md, a.md, c.md]

**Requires:**

- Process files in input order
- Don't sort results

**Does NOT require:** Path normalization

**Checkpoint 4:** Run `just test tests/test_tokens.py` - awaiting approval

---

### Group 5: CLI Integration

**Module:** `tests/test_cli_tokens.py`

#### Test 5.1: CLI requires model argument

**Given:** File "test.md" exists **When:** `uv run claudeutils tokens test.md` executed
(no model) **Then:** Exits 1, stderr shows error about missing model argument

**Requires:**

- Add `tokens` subparser in cli.py
- Model as first positional argument
- Error message for missing model

**Does NOT require:** File processing

#### Test 5.2: CLI accepts single file with model

**Given:** File "test.md" exists **When:** `uv run claudeutils tokens sonnet test.md`
executed **Then:** Exits 0, stdout contains filename and count

**Requires:**

- `handle_tokens()` function
- Wire up to tokens module
- Text output format
- Parse model from first positional arg

**Does NOT require:** JSON format

#### Test 5.3: CLI reports missing file

**Given:** File "missing.md" does not exist **When:**
`uv run claudeutils tokens haiku missing.md` executed **Then:** Exits 1, stderr contains
"missing.md" and error message

**Requires:**

- Catch FileNotFoundError
- Print to stderr
- Exit with code 1

**Does NOT require:** Detailed error messages

#### Test 5.4: CLI handles multiple files

**Given:** Files "a.md" and "b.md" exist **When:**
`uv run claudeutils tokens opus a.md b.md` executed **Then:** Stdout shows both files
with counts + total

**Requires:**

- Multiple file path arguments after model
- Display per-file counts
- Display total at end

**Does NOT require:** Table formatting

**Checkpoint 5:** Run `just test tests/test_cli_tokens.py` - awaiting approval

---

### Group 6: Output Formats

**Module:** `tests/test_cli_tokens.py` (continued)

#### Test 6.1: Default text format shows human-readable output

**Given:** File "test.md" with 42 tokens, model="sonnet" **When:**
`uv run claudeutils tokens sonnet test.md` executed **Then:** Output contains "test.md:
42 tokens"

**Requires:**

- Format as "{path}: {count} tokens"
- Total line: "Total: {sum} tokens"

**Does NOT require:** Column alignment, colors

#### Test 6.2: JSON format outputs structured data

**Given:** File "test.md" with 42 tokens, model="haiku" **When:**
`uv run claudeutils tokens haiku test.md --json` executed **Then:** Output is valid
JSON: `{"files": [{"path": "test.md", "count": 42}], "total": 42}`

**Requires:**

- Add `--json` flag (option, not positional)
- JSON serialization of TokenCount
- JSON structure with "files" and "total" keys

**Does NOT require:** Pretty-printing

#### Test 6.3: JSON format with multiple files

**Given:** Two files with counts [10, 20], model="opus" **When:**
`uv run claudeutils tokens opus file1 file2 --json` executed **Then:** JSON includes
both files and total: `{"files": [...], "total": 30}`

**Requires:**

- Array of per-file results in JSON
- Total calculation in JSON output

**Does NOT require:** Additional metadata

**Checkpoint 6:** Run `just test tests/test_cli_tokens.py` - awaiting approval

---

### Group 7: API Key Management

**Module:** `tests/test_tokens.py` (continued)

#### Test 7.1: Read API key from environment

**Given:** `ANTHROPIC_API_KEY` environment variable set **When:** Anthropic client
initialized **Then:** Client uses environment variable value

**Requires:**

- Anthropic SDK's default env var handling
- **MUST NOT** implement custom key reading

**Does NOT require:** Custom env var logic, key validation

#### Test 7.2: Error message guides user to set API key

**Given:** No `ANTHROPIC_API_KEY` environment variable **When:** Token counting
attempted **Then:** Error message includes "ANTHROPIC_API_KEY" and setup instructions

**Requires:**

- Catch authentication error
- Custom error message with guidance

**Does NOT require:** Interactive prompts, key storage

**Checkpoint 7:** Run `just test` - awaiting approval

---

### Group 8: Help Text and Documentation

**Module:** `tests/test_cli_help.py`

#### Test 8.1: Help text is complete and accurate

**Given:** CLI installed **When:** `uv run claudeutils tokens --help` executed **Then:**
Help contains expected text (see full text below)

**Requires:**

- Exact help text specified below
- **MUST NOT** delegate prose writing to haiku

**Full help text to implement:**

```
usage: claudeutils tokens [-h] [--json] {haiku,sonnet,opus} FILE [FILE ...]

Count tokens in files using Anthropic API. Requires ANTHROPIC_API_KEY
environment variable.

positional arguments:
  {haiku,sonnet,opus}   Model to use for token counting. Token counts vary by
                        model.
  FILE                  File path(s) to count tokens

options:
  -h, --help            show this help message and exit
  --json                Output JSON format instead of text

Examples:
  uv run claudeutils tokens sonnet prompt.md
  uv run claudeutils tokens opus file1.md file2.md --json
```

**Checkpoint 8:** Run `just test tests/test_cli_help.py` - awaiting approval

---

## Implementation Order

1. Group 1: Core token counting (unit tests)
2. Group 2: Model parameter handling
3. Group 3: API error handling
4. Group 4: Multiple files and aggregation
5. Group 5: CLI integration
6. Group 6: Output formats
7. Group 7: API key management
8. Group 8: Help text

---

## Design Decisions to Document

After implementation, add to `agents/DESIGN_DECISIONS.md`:

### Model as First Positional Argument

**Decision:** Model is first positional argument in CLI, required parameter in functions

**Rationale:** Token counts vary by model; explicit model choice ensures accurate counts

**Implementation:** `count_tokens_for_file(path: Path, model: str)` and CLI positional
arg

### Model Alias Support

**Decision:** Support short aliases: "haiku", "sonnet", "opus" (if API supports them)

**Rationale:** User-friendly CLI; avoid typing full model IDs

**Fallback:** If API requires full IDs, implement mapping in `tokens.py`

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

**Decision:** Human-readable text format by default, JSON optional

**Rationale:** Matches existing CLI commands (analyze, rules); text for humans, JSON for
tools

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
- Mock Anthropic client in tests (no real API calls)
- Add fixtures in `tests/fixtures/` for test files
