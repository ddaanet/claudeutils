# Test Plan: Statusline Shell Parity Gaps

Gaps identified by cross-referencing each parity fix against existing test coverage.

## display.py — `format_directory()` basename extraction

**Existing:** Only tests simple name (`"claudeutils"`) — never exercises path-splitting logic.

**Missing tests:**
- Full path → basename: `/Users/david/code/claudeutils` → `claudeutils`
- Trailing slash: `/Users/david/code/claudeutils/` → `claudeutils`
- Single segment (no slash): `claudeutils` → `claudeutils`
- Root-relative: `/` edge case

## display.py — `format_python_env()`

**Existing:** Zero coverage (new method, no tests).

**Missing tests:**
- Active env: `PythonEnv(name=".venv")` → `"🐍 .venv"`
- No env: `PythonEnv(name=None)` → `""`
- Conda name: `PythonEnv(name="conda-env")` → `"🐍 conda-env"`

## display.py — `format_model()` Opus bold

**Existing:** Checks `\033[35m` (magenta) for Opus but not `\033[1m` (bold). Sonnet/Haiku don't assert bold absent.

**Missing tests:**
- Opus has both `\033[1m` and `\033[35m`
- Sonnet does NOT have `\033[1m`
- Haiku does NOT have `\033[1m`

## display.py — `format_context()` integer kilos

**Existing:** Tests 1500→"1k" but doesn't cover rounding boundary behavior.

**Missing tests:**
- 1999 → `"1k"` (truncation, not rounding)
- 999 → `"999"` (below kilo threshold)
- 1000 → `"1k"` (exact boundary)
- 50500 → `"50k"` (not `"50.5k"`)

## context.py — `get_thinking_state()` null handling

**Existing:** Tests file-missing (→True) and explicit True. Missing the null case that caused the bug.

**Missing tests:**
- `alwaysThinkingEnabled: null` in JSON → `enabled=True`
- `alwaysThinkingEnabled` key absent from JSON → `enabled=True`
- `alwaysThinkingEnabled: false` → `enabled=False` (explicit disable)

## cli.py — Double-space separators

**Existing:** No test verifies section spacing.

**Missing tests:**
- Line 1 sections separated by `"  "` (double space)
- Verify pattern: `emoji text  emoji text  emoji text`

## cli.py — Python env conditional inclusion

**Existing:** `test_cli_visual_line_structure` mocks env=".venv" but doesn't verify `🐍` in output.

**Missing tests:**
- With env: `🐍` and `.venv` appear in line 1
- Without env (name=None): `🐍` absent from line 1, no extra spacing

## cli.py — ANSI color preservation

**Existing:** No test verifies ANSI codes survive `click.echo(color=True)`.

**Missing test:**
- CLI output contains `\033[` escape sequences (at least one)
