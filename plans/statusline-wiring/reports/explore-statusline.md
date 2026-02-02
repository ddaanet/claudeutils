# Exploration: Statusline Architecture and Implementation

## Summary

The claudeutils statusline module is a partial implementation of the design specification. The formatting/display layer (`StatuslineFormatter`) is complete with ANSI color support, but the data-gathering modules (context.py, plan_usage.py, api_usage.py) and full CLI integration are not yet implemented. The CLI command exists as a placeholder that validates JSON input from stdin but does not perform actual statusline rendering.

## Key Findings

### Design Specification Location
**File:** `/Users/david/code/claudeutils-tools/plans/claude-tools-rewrite/design.md` (lines 54-60)

**Statusline Module Layout (designed, partially implemented):**
```
src/claudeutils/statusline/
  __init__.py          # Re-exports for convenience [DONE]
  display.py           # Formatting: token bars, usage bars, colors [DONE]
  context.py           # Transcript/context window parsing [NOT IMPLEMENTED]
  plan_usage.py        # Plan mode display (limits, percentages, reset times) [NOT IMPLEMENTED]
  api_usage.py         # API mode display (token counts by model, switchback time) [NOT IMPLEMENTED]
  cli.py               # Click command: statusline (reads JSON stdin, outputs 2 lines) [PLACEHOLDER]
```

**Original shell script reference:** Only mentioned in design doc (line 22): `statusline-command.sh → claudeutils statusline CLI command`. No actual shell script found in codebase.

### Existing Implementation Files

#### 1. `/Users/david/code/claudeutils-tools/src/claudeutils/statusline/__init__.py`
- **Status:** Complete
- **Exports:** `StatuslineFormatter` from display module
- **Code:** 5 lines, minimal re-export pattern

#### 2. `/Users/david/code/claudeutils-tools/src/claudeutils/statusline/display.py`
- **Status:** Complete with full feature set
- **Lines:** 97 lines
- **Class:** `StatuslineFormatter`
- **Methods:**
  - `colored(text: str, color: str) -> str` — Wraps text in ANSI color codes (8 colors: red, green, yellow, blue, magenta, cyan, white)
  - `token_bar(tokens: int, max_tokens: int) -> str` — Returns Unicode block character (▁▂▃▄▅▆▇█) scaled to percentage
  - `vertical_bar(percentage: int) -> str` — Returns colored vertical bar based on percentage (green <50%, yellow <80%, red ≥80%)
  - `limit_display(name: str, pct: int, reset: str) -> str` — Formats display as `"{name} {bar} {pct}% │ resets {reset}"`
- **ANSI Codes:**
  - Red: `\033[31m`, Green: `\033[32m`, Yellow: `\033[33m`, etc.
  - Reset: `\033[0m`

#### 3. `/Users/david/code/claudeutils-tools/src/claudeutils/statusline/cli.py`
- **Status:** Placeholder implementation
- **Lines:** 15 lines
- **Current behavior:**
  - Command: `@click.command("statusline")`
  - Input: Reads JSON from stdin, validates it with `json.loads()`
  - Output: Hardcoded `click.echo("OK")`
  - **NOT IMPLEMENTED:** Actual statusline rendering logic
- **Contract (from design, line 375):** "Statusline contract: Always exit 0, two lines to stdout, ANSI colors"

#### 4. CLI Registration
- **File:** `/Users/david/code/claudeutils-tools/src/claudeutils/cli.py`
- **Lines:** 152-154
- **Code:**
  ```python
  from claudeutils.statusline.cli import statusline
  ...
  cli.add_command(statusline)
  ```
- **Integration:** Registered as top-level command in main CLI group

### Test Files

#### 1. `/Users/david/code/claudeutils-tools/tests/test_statusline_structure.py`
- **Status:** Minimal smoke test
- **Content:** Single test verifying module is importable
- **Coverage:** Does NOT test actual functionality

#### 2. `/Users/david/code/claudeutils-tools/tests/test_statusline_display.py`
- **Status:** Comprehensive formatter tests
- **Lines:** 91 lines
- **Coverage:** All `StatuslineFormatter` methods
- **Tests:**
  - `test_colored_text()` — Verifies ANSI codes for red/green/yellow (checks for `\033[31m`, `\033[32m`, `\033[33m`, reset code)
  - `test_token_bar()` — Tests progress bar generation at 0%, 50%, 100% usage
  - `test_vertical_bar()` — Tests vertical bar character selection and coloring at 0%, 50%, 100%
  - `test_limit_display()` — Tests complete limit display formatting with name/percentage/reset time
- **Assertions:** All verify Unicode block presence and ANSI code presence (not exact format)

#### 3. `/Users/david/code/claudeutils-tools/tests/test_cli_statusline.py`
- **Status:** Placeholder test
- **Lines:** 13 lines
- **Coverage:** Single test (`test_statusline_reads_stdin()`)
- **Content:** Verifies command accepts JSON from stdin and exits with code 0
- **Missing:** No tests for actual output format, usage parsing, or multi-line rendering

### Design Decisions Referenced in Implementation

#### ANSI Color Thresholds (from design, applied in display.py lines 75-80)
```python
if percentage < 50:
    color = "green"
elif percentage < 80:
    color = "yellow"
else:
    color = "red"
```

#### Unicode Block Characters (design mentions token_bar, implemented lines 48, 65)
- Used: `▁▂▃▄▅▆▇█` (8 blocks for 0-100% range)
- Calculation: `block_index = int((percentage / 100) * 8)` clamped to valid range

#### Vertical Bar Display Format (implemented line 96)
- Pattern: `"{name} {bar} {pct}% │ resets {reset}"`
- Separator: U+2502 VERTICAL LINE (`│`)

### Missing Implementation Gaps

#### 1. Context Module (Planned: `context.py`)
- **Purpose:** Transcript/context window parsing
- **Expected inputs:** Git branch name, dirty status (from design line 265: `git`)
- **Not found:** No file, no tests
- **Dependency:** Design references git subprocess calls for status

#### 2. Plan Usage Module (Planned: `plan_usage.py`)
- **Purpose:** Plan mode display (limits, percentages, reset times)
- **Expected responsibility:** Calculate usage percentages, parse reset times from account.usage data
- **Not found:** No file, no tests
- **Dependency:** Should use data from `claudeutils.account.usage` module

#### 3. API Usage Module (Planned: `api_usage.py`)
- **Purpose:** API mode display (token counts by model, switchback time)
- **Expected responsibility:** Parse token counts by model, display switchback scheduling info
- **Not found:** No file, no tests
- **Dependency:** Should use data from `claudeutils.account.usage` and `claudeutils.account.switchback` modules

#### 4. CLI Integration (Current: placeholder in `cli.py`)
- **Expected (design line 60):** "Click command: statusline (reads JSON stdin, outputs 2 lines)"
- **Current:** Placeholder reading stdin, outputting "OK"
- **Not implemented:**
  - JSON schema/structure expected from stdin
  - Two-line output format (line 1: what?, line 2: what?)
  - Actual formatting logic (dispatcher to plan_usage/api_usage)
  - Error handling (design line 300: "Statusline catches all exceptions and exits 0")

### Pattern References from Related Modules

#### AccountState Model (Pattern for statusline models)
- **File:** `/Users/david/code/claudeutils-tools/src/claudeutils/account/state.py`
- **Pattern:** Pydantic BaseModel with field validation
- **Example:**
  ```python
  class AccountState(BaseModel):
      mode: str
      provider: str
      oauth_in_keychain: bool
      api_in_claude_env: bool
      base_url: str | None = None
      has_api_key_helper: bool
      litellm_proxy_running: bool

      def validate_consistency(self) -> list[str]:
          """Return list of issue strings."""
  ```
- **Applicable to:** StatuslineContext, PlanUsageData, ApiUsageData models

#### Account Module CLI Pattern
- **File:** `/Users/david/code/claudeutils-tools/src/claudeutils/account/cli.py`
- **Pattern:** Click command group with subcommands
- **Pattern:** Error handling with custom exceptions
- **Applicable to:** Statusline CLI structure (though statusline is single command, not group)

#### Existing Modules Referenced by Statusline
- `/Users/david/code/claudeutils-tools/src/claudeutils/account/usage.py` — OAuth usage API, caching, limit detection
- `/Users/david/code/claudeutils-tools/src/claudeutils/account/switchback.py` — Switchback scheduling info
- `/Users/david/code/claudeutils-tools/src/claudeutils/model/config.py` — Model metadata (for API usage display)

### CLI Entry Point Wiring

**File:** `/Users/david/code/claudeutils-tools/src/claudeutils/cli.py`

**Import (line 22):**
```python
from claudeutils.statusline.cli import statusline
```

**Registration (line 154):**
```python
cli.add_command(statusline)
```

**Invocation pattern (from design line 234):**
```bash
exec claudeutils statusline
```

**Current status:** ✓ Wiring complete, ✗ Implementation placeholder

### Design Specification Contract Details

From design.md section "Statusline: ANSI formatting module" (lines 145-159):

**Five distinct components in the design:**

1. **StatuslineFormatter** (IMPLEMENTED)
   - Responsible for: ANSI formatting, color codes, Unicode block rendering
   - Output: Formatted strings with ANSI codes

2. **Context parsing** (NOT IMPLEMENTED)
   - Responsible for: Reading git status, transcript info
   - Subprocess calls: `git` command (design line 265)

3. **Plan mode data** (NOT IMPLEMENTED)
   - Responsible for: Limits calculation, percentage math, reset time parsing

4. **API mode data** (NOT IMPLEMENTED)
   - Responsible for: Token counts by model, switchback scheduling

5. **CLI orchestration** (PLACEHOLDER)
   - Responsible for: Read JSON stdin, dispatch to plan/api handlers, format 2-line output

**Output contract (design line 375):**
- Always exit 0
- Two lines to stdout
- ANSI colors enabled

**Error handling (design line 300):**
- Statusline catches all exceptions and exits 0 (matching current shell behavior)

## Patterns

### Formatter Architecture
- Single class `StatuslineFormatter` with multiple formatting methods
- Each method is independently testable
- Color thresholds (50%, 80%) are hard-coded constants suitable for extraction to class variables
- Unicode block selection uses modulo arithmetic (percentage → block index)

### Testing Coverage Structure
- Display layer: ✓ comprehensive (4 test functions, all formatter methods covered)
- CLI layer: ✗ minimal (only stub test, no actual rendering verification)
- Integration: ✗ missing (no end-to-end tests with real data)

### Module Dependencies
- `display.py` has zero external dependencies (pure stdlib strings)
- `cli.py` imports `click`, `json`, `sys` (minimal set)
- Missing modules will need: `pathlib`, `re`, `decimal`, `subprocess` (all stdlib)

### Error Handling Pattern (from design)
- All exceptions caught at CLI level
- Exit code always 0 (matching async render contract)
- Error details logged/output not specified in current placeholder

## Gaps and Unresolved Questions

1. **JSON stdin schema not specified** — What structure is expected? Fields for mode, usage data, context?
2. **Two-line output format undefined** — Line 1: context/header? Line 2: usage/limits?
3. **Mode detection missing** — How does CLI determine plan vs. api mode? Read from `~/.claude/account-mode`?
4. **Usage data source unclear** — Does CLI read `~/.claude/stats-cache.json` directly or call `account.usage` module?
5. **Context window parsing scope** — What transcript info is needed? Full history or just current session?
6. **Reset time format** — Design shows "2026-02-01" format but no parsing spec (hours/minutes?)
7. **Model filtering for API mode** — Which models should appear in the output? All tiers or filtered?
8. **Colorization scope** — Should plan mode limits also use green/yellow/red thresholds like bars?
9. **Performance expectations** — Async render tolerates <100ms (design line 371), but Python startup overhead?
10. **Exception types to catch** — Should CLI define custom `StatuslineError` exception or catch generic Exception?

## File Locations (Absolute Paths)

### Specification
- `/Users/david/code/claudeutils-tools/plans/claude-tools-rewrite/design.md`

### Implementation
- `/Users/david/code/claudeutils-tools/src/claudeutils/statusline/__init__.py`
- `/Users/david/code/claudeutils-tools/src/claudeutils/statusline/display.py`
- `/Users/david/code/claudeutils-tools/src/claudeutils/statusline/cli.py`
- `/Users/david/code/claudeutils-tools/src/claudeutils/cli.py`

### Tests
- `/Users/david/code/claudeutils-tools/tests/test_statusline_structure.py`
- `/Users/david/code/claudeutils-tools/tests/test_statusline_display.py`
- `/Users/david/code/claudeutils-tools/tests/test_cli_statusline.py`

### Related Modules (for reference during implementation)
- `/Users/david/code/claudeutils-tools/src/claudeutils/account/state.py`
- `/Users/david/code/claudeutils-tools/src/claudeutils/account/usage.py`
- `/Users/david/code/claudeutils-tools/src/claudeutils/account/switchback.py`
- `/Users/david/code/claudeutils-tools/src/claudeutils/model/config.py`
