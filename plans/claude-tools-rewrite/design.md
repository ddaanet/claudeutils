# Design: Rewrite Claude Shell Tools as Python in claudeutils

## Problem

Five shell scripts (~2000 lines, 58 functions) manage Claude Code authentication, provider switching, model overrides, and statusline rendering. Zero automated tests. Known bugs (LaunchAgent heredoc, model set grep). Complex state validation logic with many code paths that are impossible to test without full environment mocking. The shell scripts have become a maintenance liability.

## Decision: claudeutils Package

New modules live in `claudeutils` (not `home`). Rationale:

- Already a proper Python package with pytest, mypy strict, ruff, click CLI, pydantic
- Purpose statement fits: "foundational tools to support Claude-based development processes"
- `home` is dotfiles/config/shell glue — not a Python package
- claudeutils already handles API keys (token counting uses ANTHROPIC_API_KEY)
- Test infrastructure exists: conftest.py with factory fixtures, monkeypatch patterns

## Scope

**In scope:**

- `claude-account.sh` → `claudeutils account` CLI group
- `statusline-command.sh` → `claudeutils statusline` CLI command
- `claude-model.sh` → `claudeutils model` CLI group
- `lib/account-validation.sh` → `claudeutils.account.state` module
- `claude-model-info.py` → absorbed into `claudeutils.model` module

**Out of scope:**

- `litellm-start.sh` — 12-line wrapper, stays bash
- Shell completion registration (bash/zsh/fish boilerplate that calls CLI)
- `.envrc` / direnv integration (stays in home repo)
- LiteLLM health check (separate design exists)

## Architecture

### Module Layout

```
src/claudeutils/
  account/
    __init__.py          # Re-exports for convenience
    state.py             # State model, validation, transitions (replaces lib/account-validation.sh)
    mode.py              # Mode switching logic (set_mode, write_claude_env, keychain ops)
    usage.py             # OAuth usage API, caching, limit detection
    switchback.py        # LaunchAgent plist generation, schedule/unschedule
    cli.py               # Click command group: account {status,plan,api,provider}

  model/
    __init__.py
    config.py            # LiteLLM config parsing (replaces claude-model-info.py + grep/sed)
    overrides.py         # Override file management (read/write/reset)
    cli.py               # Click command group: model {show,list,set,reset}

  statusline/
    __init__.py
    display.py           # Formatting: token bars, usage bars, colors
    context.py           # Transcript/context window parsing
    plan_usage.py        # Plan mode display (limits, percentages, reset times)
    api_usage.py         # API mode display (token counts by model, switchback time)
    cli.py               # Click command: statusline (reads JSON stdin, outputs 2 lines)

  # Existing modules unchanged
  cli.py                 # Add: account, model, statusline groups
  models.py              # Add: AccountState, LiteLLMModel, etc.
  exceptions.py          # Add: AccountError, StateError, etc.
```

### Key Design Decisions

**1. Account state as a Pydantic model**

Replace scattered file reads + boolean flags with a single state object:

```python
class AccountState(BaseModel):
    mode: Literal["plan", "api"]
    provider: Literal["anthropic", "openrouter", "litellm"]
    oauth_in_keychain: bool
    api_in_claude_env: bool
    base_url: str | None
    has_api_key_helper: bool
    litellm_proxy_running: bool

    def validate_consistency(self) -> list[str]:
        """Return list of inconsistency descriptions. Empty = consistent."""
```

Rationale: Current `validate_state()` has 10+ branches returning 0/1 with no detail. A model with named fields makes every check testable independently. Returning a list of issues (not just bool) aids diagnostics.

**2. Provider as a protocol/strategy**

Each provider (anthropic, openrouter, litellm) has different env vars, validation rules, and claude-env content. Model this explicitly:

```python
class Provider(Protocol):
    name: str
    def claude_env_vars(self, keys: KeyStore) -> dict[str, str]: ...
    def validate(self, state: AccountState) -> list[str]: ...
    def settings_json_patch(self) -> dict: ...
```

Three implementations: `AnthropicProvider`, `OpenRouterProvider`, `LiteLLMProvider`.

Rationale: Current code has `if provider == "anthropic" ... elif provider == "openrouter" ...` scattered across `set_mode()`, `validate_state()`, `write_claude_env()`, and `cmd_status()`. Consolidating per-provider logic makes adding providers trivial and each provider independently testable.

**3. LiteLLM config as structured data**

Replace grep/sed YAML parsing with proper parsing. The config format is simple enough for regex-based parsing (no nested structures beyond `litellm_params`), but the comment metadata (tiers, arena rank, pricing) needs careful extraction.

```python
class LiteLLMModel(BaseModel):
    name: str                          # model_name field
    litellm_model: str                 # model field in litellm_params
    tiers: list[str]                   # from comment: haiku,sonnet
    arena_rank: int | None             # from comment: arena:N
    input_price: Decimal | None        # per million tokens
    output_price: Decimal | None       # per million tokens
    api_key_env: str                   # os.environ/KEY_NAME
    api_base: str | None               # optional override
```

Use `Decimal` for pricing (not float). Parse with regex like existing `claude-model-info.py` but with proper structure. Optionally enrich from `litellm.model_cost` at runtime.

Rationale: Proper types eliminate the fragile `echo "$info_json" | jq -r --arg m "$model" '.[$m].in_price'` chains. Config is read-only (no YAML write needed), so regex parsing is fine — no PyYAML dependency needed for this specific file.

**4. Keychain operations via subprocess**

No Python keychain library needed. Wrap `security` commands:

```python
class Keychain:
    def __init__(self, service: str = "Claude Code-credentials"):
        self.service = service

    def find(self) -> str | None:
        """Return password or None if not found."""
    def add(self, account: str, password: str) -> None: ...
    def delete(self, account: str) -> None: ...
```

Each method calls `subprocess.run(["security", ...], capture_output=True)` and parses output. Easily mockable: `mocker.patch("claudeutils.account.mode.Keychain")`.

Rationale: macOS `security` CLI is the stable interface. No third-party keychain bindings needed. subprocess is the right tool here — these are OS-level operations, not data processing.

**5. Statusline: ANSI formatting module**

Current statusline has inline ANSI escape codes everywhere. Extract a small formatter:

```python
class StatuslineFormatter:
    """ANSI formatting for terminal statusline output."""
    def colored(self, text: str, color: str) -> str: ...
    def bold(self, text: str) -> str: ...
    def token_bar(self, tokens: int, max_tokens: int) -> str: ...
    def vertical_bar(self, percentage: float) -> str: ...
    def limit_display(self, name: str, pct: float, reset: str) -> str: ...
```

Rationale: The display logic is the hardest part of statusline to test. By separating formatting from data fetching, we can test `token_bar(75000, 200000)` returns the right Unicode blocks with the right colors — without needing a running Claude Code instance.

**6. LaunchAgent plist via plistlib**

Replace the broken heredoc with `plistlib.dump()`:

```python
def create_switchback_plist(switchback_time: datetime) -> Path:
    plist = {
        "Label": "com.claude.account-switch",
        "ProgramArguments": [str(CLAUDE_ACCOUNT_BIN), "plan"],
        "StartCalendarInterval": {
            "Month": switchback_time.month,
            "Day": switchback_time.day,
            "Hour": switchback_time.hour,
            "Minute": switchback_time.minute,
        },
    }
    path = Path.home() / "Library/LaunchAgents/com.claude.account-switch.plist"
    with path.open("wb") as f:
        plistlib.dump(plist, f)
    return path
```

Rationale: Fixes the known heredoc variable expansion bug. `plistlib` is stdlib, no dependency. Structured data → structured output. Trivially testable with `tmp_path`.

**7. Usage API caching**

Port the 30-second TTL cache:

```python
class UsageCache:
    def __init__(self, cache_path: Path, ttl_seconds: int = 30):
        self.cache_path = cache_path
        self.ttl = ttl_seconds

    def get(self) -> UsageData | None:
        """Return cached data if fresh, None if stale/missing."""

    def put(self, data: UsageData) -> None:
        """Write data with current timestamp."""
```

Separate from the API call itself. `UsageData` is a pydantic model with `five_hour` and `seven_day` utilization fields.

**8. Output contract: shell wrappers**

Python commands output structured data. Thin shell wrappers in `home/claude/` handle the shell-specific parts:

**claude-account wrapper (~10 lines):**
```bash
#!/bin/bash
# Thin wrapper: delegates to claudeutils, handles env sourcing
result=$(claudeutils account "$@")
exit_code=$?

# If mode switch, source the updated env
if [[ "$1" == "api" || "$1" == "plan" ]] && [[ $exit_code -eq 0 ]]; then
    direnv allow "$HOME" 2>/dev/null
fi

echo "$result"
exit $exit_code
```

**statusline wrapper (~3 lines):**
```bash
#!/bin/bash
exec claudeutils statusline
```

**claude-model wrapper (~3 lines):**
```bash
#!/bin/bash
exec claudeutils model "$@"
```

Completions stay as bash/zsh/fish scripts that call `claudeutils model completions` or `claudeutils account completions` for the dynamic parts.

### State Files (unchanged)

The file layout in `~/.claude/` stays identical. Python reads/writes the same files in the same formats. This means:

- No migration needed
- Shell wrappers and Python CLI are interchangeable during transition
- direnv integration unchanged
- Existing `.envrc` works as-is

Files managed:
- `account-mode` — plain text "plan" or "api"
- `account-config.json` — `{"api_provider": "..."}`
- `claude-env` — bash env var assignments (sourced by direnv)
- `claude-model-overrides` — bash env var assignments (sourced by direnv)
- `saved-oauth-creds` — JSON OAuth credentials backup
- `settings.json` — Claude Code settings (apiKeyHelper toggling)
- `stats-cache.json` — Claude Code token usage (read-only)

### External Command Usage

Python subprocess calls (all mockable via `mocker.patch("subprocess.run")`):

| Command | Used By | Purpose |
|---------|---------|---------|
| `security` | `account.mode.Keychain` | macOS keychain CRUD |
| `launchctl` | `account.switchback` | LaunchAgent load/unload |
| `curl` | `account.usage` | OAuth usage API |
| `git` | `statusline.context` | Branch name, dirty status |
| `pgrep` | `account.state` | LiteLLM proxy detection |
| `direnv` | shell wrapper only | Not called from Python |

Note: `jq`, `bc`, `date`, `sed`, `grep` are **eliminated** — their work moves to Python stdlib.

### Dependencies

**New dependencies for claudeutils:**
- None. Everything uses stdlib (`subprocess`, `plistlib`, `json`, `pathlib`, `re`, `datetime`, `decimal`).
- `pyyaml` is already a dependency but not needed here (regex parsing suffices for the simple YAML structure).
- `litellm` remains optional (runtime pricing enrichment).

**Existing dependencies leveraged:**
- `pydantic` — state models, config models, usage data
- `click` — CLI groups and commands

### Error Handling

Custom exceptions added to `exceptions.py`:

```python
class AccountError(ClaudeUtilsError): ...
class StateInconsistentError(AccountError):
    def __init__(self, issues: list[str]): ...
class KeychainError(AccountError): ...
class UsageApiError(AccountError): ...
class ProviderError(AccountError): ...
class ModelError(ClaudeUtilsError): ...
class ModelNotFoundError(ModelError): ...
class TierMismatchError(ModelError): ...
class ConfigParseError(ModelError): ...
class StatuslineError(ClaudeUtilsError): ...
```

Statusline catches all exceptions and exits 0 (matching current behavior — errors must not break the display).

### Testing Strategy

**Unit tests (fast, no I/O):**
- `AccountState.validate_consistency()` — all branch combinations
- Provider implementations — env var generation, validation rules
- `LiteLLMConfig` parsing — model extraction, tier filtering, pricing
- `StatuslineFormatter` — token bar rendering, color thresholds, vertical bars
- Override file generation — format correctness
- Plist generation — calendar interval correctness (fixes heredoc bug)
- Usage data parsing — limit detection, reset time extraction
- Reset time formatting — same-day, same-week, same-year display

**Integration tests (subprocess mocks):**
- Keychain operations — mock `security` command output
- LaunchAgent operations — mock `launchctl`, verify plist written correctly
- Usage API — mock `curl` response, verify caching behavior
- Git status — mock `git` output, verify statusline formatting
- Mode switching — verify all files written/deleted correctly (using `tmp_path`)

**CLI tests:**
- Click test client (`CliRunner`) for all commands
- Verify exit codes, stdout/stderr content
- Test completion output generation

**Fixtures needed (conftest.py):**
- `claude_home(tmp_path)` — mock `~/.claude/` with configurable state files
- `mock_keychain(mocker)` — factory for keychain responses
- `mock_subprocess(mocker)` — factory for subprocess.run responses
- `litellm_config(tmp_path)` — write test config YAML with known models
- `usage_response()` — factory for OAuth usage API JSON

### Migration Path

**Phase 1: Core modules (account, model)**
- Port state validation, mode switching, model config parsing
- Full test coverage from day one
- Shell wrappers delegate to `claudeutils` CLI

**Phase 2: Statusline**
- Port formatting and display logic
- Verify async statusline works with Python entry point
- Performance validation (Python startup acceptable with async render)

**Phase 3: Cutover**
- Update `justfile install` to install `claudeutils` wrappers
- Update shell completion registration
- Remove old shell scripts

Each phase is independently deployable — shell wrappers can fall back to old scripts if needed.

### Completion Generation

Python generates completion scripts that shells source:

```
claudeutils account completions fish  →  fish completion script
claudeutils model completions fish    →  fish completion script
```

Dynamic model lists call back into Python:
```fish
complete -c claude-model -n '__fish_tier_haiku' \
    -a "(claudeutils model list --tier haiku --names-only)"
```

Static command lists are embedded in the generated script (no callback needed for subcommand completion).

## Non-Functional Requirements

- **Startup latency:** <100ms for statusline (async render tolerates this)
- **Cache TTL:** 30 seconds for usage API (matches current behavior)
- **File permissions:** claude-env and key files written with 0o600
- **Exit codes:** 0 success, 1 general error, 2 usage error (matches click defaults)
- **Statusline contract:** Always exit 0, two lines to stdout, ANSI colors

## What This Design Does NOT Cover

- LiteLLM health check (separate design: `plans/litellm-provider-fix/`)
- OpenRouter custom statusline (npx/tsx integration — low priority, can add later)
- Transcript file parsing for context usage (may move to claudeutils later)
- `stats-cache.json` format (owned by Claude Code, read-only)
