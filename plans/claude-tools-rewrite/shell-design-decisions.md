# Claude Account Switcher - Design Documentation

**Plan**: `~/.claude/plans/lazy-frolicking-moonbeam.md`
**Created**: 2026-01-09

## Problem Statement

When hitting Claude Pro subscription limits (5-hour session or weekly), manually switching to Anthropic API account requires:
1. Web authentication each time → generates new API key
2. Accumulation of unused API keys in Console
3. Manual tracking of when to switch back
4. Risk of forgetting and incurring unnecessary API costs

**Goal**: Seamless switching with persistent keys and automatic return to Pro when limits reset.

## Core Design Decisions

### 1. Authentication Mechanism: apiKeyHelper in settings.json

**Decision**: Use `apiKeyHelper` in `settings.json` for API mode authentication

**Implementation** (2026-01-11):
- **Plan mode**: Remove `apiKeyHelper` from settings.json → Claude Code uses OAuth from keychain
- **API mode**: Set `apiKeyHelper = "cat ~/.claude/api-key"` in settings.json → Claude Code reads API key via script
- Also set `env.ANTHROPIC_AUTH_TOKEN` in settings.local.json for subprocess injection (not for Claude Code's own auth)

**Critical Discovery** (2026-01-11): `settings.local.json` `.env` section is for subprocess injection only:
- Environment variables in `settings.local.json` inject into child processes spawned by Claude Code
- Claude Code's own authentication reads from: shell environment, keychain, or `apiKeyHelper` script
- Setting `env.ANTHROPIC_AUTH_TOKEN` alone is insufficient - Claude Code shows "auth token none" error
- **Solution**: Use `apiKeyHelper` in `settings.json` which Claude Code explicitly reads for authentication

**Previous approach** (2026-01-10): Direct API key in settings.local.json
- Attempted to use `env.ANTHROPIC_AUTH_TOKEN` in settings.local.json
- Failed because env section doesn't affect Claude Code's auth system
- Authentication conflict (GitHub [#11587](https://github.com/anthropics/claude-code/issues/11587)): Cannot have both OAuth token in keychain AND API key configured
- Only ONE authentication method can be active

**Rationale**:
- `apiKeyHelper` is Claude Code's designated API key mechanism
- Reads from secure file (`~/.claude/api-key`, chmod 600)
- OAuth saved to `~/.claude/saved-oauth-creds` during API mode, restored on switch back
- Keychain cleared in API mode prevents dual-auth conflict
- Clean separation: apiKeyHelper for auth, env vars for subprocess injection

### 2. Why Runtime Limit Detection?

**Decision**: Query `https://api.anthropic.com/api/oauth/usage` API to auto-detect which limit is active

**User requirement**: "user may know which limit is active, but should not have to provide input if auto is possible"

**Rationale**:
- Auto-detection preferred - user shouldn't have to specify
- Session limit: 5 hours from first message (rolling window)
- Weekly limit: 7 days from first weekly use (not calendar week)
- Both limits are tracked server-side with different reset schedules
- API returns `five_hour.utilization` and `seven_day.utilization` + reset times
- Logic: If utilization ≥99%, that limit is active → use its `resets_at` for scheduling

**Manual shortcuts available**:
- `claude-account api session` - Use session limit reset time from API
- `claude-account api weekly` - Use weekly limit reset time from API
- Faster if user knows which limit (skips 99% utilization check)

**Implementation requirement**: API requires `anthropic-beta: oauth-2025-04-20` header. Without this header, returns authentication error.

### 3. Why Automatic Switch-Back Scheduling?

**Decision**: Use macOS `launchd` with one-shot jobs scheduled at limit reset time

**Rationale**:
- User switches to API when hitting limits → wants to return to Pro when reset
- Manual switch-back: Easy to forget → waste money on API
- `launchd` advantages over `at`:
  - Persists across reboots
  - Better error handling
  - Native macOS integration
  - Can load/unload dynamically
- One-shot job: Runs once at reset time, then removes itself
- Job payload: `claude-account plan` (switches back and unloads plist)

**Why not cron**: Doesn't support one-time scheduled jobs natively

### 4. Why Force Switch with `api!`?

**Decision**: `claude-account api!` bypasses limit check and doesn't schedule return

**Rationale**:
- Safety: Default `api` command errors if no limit active ("save money, use plan")
- Edge cases where forced API usage is needed:
  - Testing API billing
  - Comparing API vs Pro behavior
  - Explicit user preference to use API
- `!` convention: Common pattern for "force" operations (vi `:wq!`, bash `command!` to bypass aliases)

### 5. Why Statusline Integration?

**Decision**: Remove second line (session stats), add account status with limit/token info

**User feedback**: "I do not find it [second line] useful"

**Rationale**:
- **Plan mode**: Show utilization % and reset time → visibility into limit status
  - Helps user decide when to switch to API
  - Shows ⚠️ when at limit
  - Requires OAuth token to call usage API (retrieved from keychain)
- **API mode**: Show token counts (daily/weekly) → usage awareness
  - Cost estimation deferred (complex to implement properly)
  - Token counts from `stats-cache.json` are accurate
  - Display: "💳 API 240k today | 1.2M week"
- Account badge (🎫 Plan / 💳 API) → immediate visual confirmation of mode

**Why 30-second cache**: Usage API adds ~200ms latency. Cache balances freshness vs performance.

#### Statusline Indicators (Added 2026-01-10)

**Extra usage indicator**:
- **Decision**: Bold red highlighting when utilization >= 100%
- **Display**: Entire limit section in bold red (e.g., `5h 100% ▮ 20:00`)
- **Detection**: `five_hour_util >= 100` or `seven_day_util >= 100` from oauth/usage API
- **Rationale**: Clear visual warning when hitting limits, prompts user to switch to API mode

**Thinking disabled indicator**:
- **Decision**: Show 😶 emoji immediately after model medal
- **Display**: `🥇😶 Opus` or `🥈😶 Sonnet` (no space between emojis)
- **Detection**: `~/.claude/settings.json` → `alwaysThinkingEnabled != true`
- **Limitation**: Cannot detect runtime Tab toggles (GitHub #9488 pending)
- **Rationale**: Helps user understand why responses may be different (thinking affects output quality)

### 6. Why File-Based Mode Storage?

**Decision**: Plain text file `~/.claude/account-mode` contains "plan" or "api"

**Rationale**:
- Simplicity: Both apiKeyHelper and statusline need to read mode
- No dependencies: Works with basic shell tools (cat/echo)
- Atomic writes: Single word, no parsing complexity
- Human-readable: User can inspect/debug easily (`cat ~/.claude/account-mode`)

**Alternative considered**: JSON config → Overkill for single value

### 7. Why OpenRouter Provider Support?

**Decision**: Add configurable API provider selection (Anthropic vs OpenRouter)

**User requirement**: "Their [Anthropic] latency and throughput are shit. And I have openrouter that offers exact same pricing, with better performance."

**Rationale**:
- OpenRouter offers same Claude models at identical pricing
- Better performance via multi-provider routing
- `:exacto` endpoints provide curated high-quality routing for tool use
- Qwen3 Coder :exacto as Haiku replacement (73% cheaper: $0.22/$1.80 vs $0.80/$4.00)

**Implementation** (2026-01-12):
- Provider configured in `~/.claude/account-config.json` (`api_provider` key)
- Defaults to "anthropic" for backward compatibility
- OpenRouter key stored in `~/.claude/openrouter-key` (separate from Anthropic key)
- `set_mode("api")` reads provider and configures appropriate env vars
- OpenRouter requires: `ANTHROPIC_BASE_URL`, `ANTHROPIC_AUTH_TOKEN`, `ANTHROPIC_API_KEY=""` (empty)
- Switchback scheduling uses Anthropic OAuth API regardless of provider (checks Pro limits)

**Model mapping for OpenRouter**:
- Opus/Sonnet: Use Claude models via OpenRouter (same pricing)
- Haiku: Replaced with `qwen/qwen3-coder:exacto` (optimized for tool use, 73% cheaper)

### 8. Multi-Model Provider Research: Why Helicone Doesn't Work (2026-01-25)

**User requirement**: "I have $20 Helicone credit. Can I use it for multi-model access?"

**Investigation**: Helicone was initially selected as solution for multi-model cost optimization.

**Findings**: Helicone is observability-only, not a provider-access gateway.

**Architecture limitations**:
- **Provider-specific gateway** (`https://anthropic.helicone.ai/v1`): Requires user's own Anthropic API key + Helicone auth header
  - User has Claude Pro account, not API key
  - Cannot access Claude models without bringing own Anthropic credentials
  - Only works with Claude (no multi-model)
- **Unified gateway** (`https://ai-gateway.helicone.ai/ai`): OpenAI SDK format only
  - Claude Code uses Anthropic SDK (incompatible)
  - Marketing "100+ models" = models available IF user has provider credentials
  - Does not provide model access, only routing

**Why Helicone credit doesn't help**:
- $20 credit applies to Helicone's observability features only (logging, caching, analytics)
- Does NOT subsidize model costs from Anthropic/OpenAI/Google
- User would still need separate API keys for each provider

**Solution rejected**: Helicone not viable without Anthropic API key OR alternative hosting

**Viable alternative**: LiteLLM Proxy (self-hosted, free)
- Architecture: Claude Code → LiteLLM Proxy → {Anthropic/OpenAI/Google/etc}
- Route Claude models to Anthropic (using existing Pro account or API key)
- Route cost-optimized models to OpenAI/Gemini (bring provider credentials)
- Integrate Helicone callbacks for observability (use $20 credit for monitoring)
- Token reporting works in Anthropic format (compatible with Claude Code)

**Implementation approach** (pending):
- Install LiteLLM Proxy locally (free, single-command setup)
- Configure provider routing rules
- Add LiteLLM provider to claude-account.sh
- Test multi-model access with Anthropic + OpenAI models

## Implementation Constraints

### API Mode Token Display (Cost Deferred)

**Challenge**: Accurate cost tracking requires input/output token split and cache rates

**Decision**: Show token counts only, defer cost calculation

**Rationale**:
- `stats-cache.json` has accurate daily token counts per model
- Cost estimation with assumptions ("wet finger estimates") = poor UX
- Tools like `claude-code-monitor` implement proper cost tracking (complex)
- Token counts provide useful usage awareness without misleading cost estimates
- Can implement proper cost tracking later

### OAuth Token Management and Keychain Handling

**Keychain service**: `Claude Code-credentials` (account: `$USER`)

**Mode Switching Implementation** (from `claude-account.sh:34-53`):

1. **Plan → API**:
   ```bash
   # Read API key and write to settings, save OAuth and remove from keychain
   local api_key=$(< "$API_KEY_FILE")
   update_settings ".env.ANTHROPIC_AUTH_TOKEN = \"$api_key\""
   if creds=$(read_keychain); then
       echo -n "$creds" > "$OAUTH_CREDS_FILE"
       delete_keychain
   fi
   ```

2. **API → Plan**:
   ```bash
   # Remove API key from settings, restore OAuth to keychain
   update_settings 'del(.env.ANTHROPIC_AUTH_TOKEN)'
   if [ -s "$OAUTH_CREDS_FILE" ]; then
       write_keychain "$(< "$OAUTH_CREDS_FILE")"
   fi
   ```

**Why keychain manipulation is necessary**:
- Auth conflict ([#11587](https://github.com/anthropics/claude-code/issues/11587)): Cannot have both OAuth in keychain AND API key configured
- Required manual keychain deletion during debugging to resolve stuck state
- Internet docs about keychain format were outdated (2026-01-10)

**Script exit code handling**:
- `statusline-command.sh` must always exit with code 0
- Non-zero exit causes Claude CLI to suppress statusline output
- Added explicit `exit 0` at script end (2026-01-10)
- Issue: `get_thinking_state()` returns 1 when settings missing or thinking disabled, which propagated to script exit

**Statusline OAuth usage** (for `/api/oauth/usage` API):
- Tries keychain first, falls back to `saved-oauth-creds` file
- Fails gracefully if neither available (no usage display)
- Uses `anthropic-beta: oauth-2025-04-20` header

### Context Usage Calculation

**Challenge**: Statusline JSON's `context_window` fields are cumulative session totals, not actual context usage

**Known Issue**: GitHub issue #13783 reports `total_input_tokens`/`total_output_tokens` accumulate across session and don't reflect `/context` command output

**Decision** (Updated 2026-01-19): Use `context_window.current_usage` field from statusbar.json with transcript fallback

**Previous approach** (2026-01-18): Transcript-based calculation exclusively
- Parsed most recent assistant response from `.jsonl` transcript file
- **Problem**: Failed when recent messages had all-zero usage (before being fully written)
- Required file read and jq processing per statusline render

**New Implementation** (2026-01-19): Primary: statusbar.json `current_usage` field
- Field structure: `{input_tokens, output_tokens, cache_creation_input_tokens, cache_read_input_tokens}`
- Sum all four values: `input_tokens + output_tokens + cache_creation_input_tokens + cache_read_input_tokens`
- Matches `/context` output accurately
- Can be `null` early in session (documented behavior)
- **Fallback**: Use transcript parsing when `current_usage` unavailable
- Display: `🧠 42k` (single value, no parentheses)

**Discovery**:
- GitHub #13783 still OPEN (created Dec 12, 2025) - cumulative token bug NOT fixed
- BUT `context_window.current_usage` field IS documented and accurate (official docs confirm)
- This field was present but overlooked in original implementation
- Provides faster, more reliable context measurement than transcript parsing

**Rationale**:
- Direct statusbar field faster than file parsing (already in memory)
- Matches `/context` command output accurately
- Handles zero-token edge cases properly (field is null, not zero)
- Transcript fallback ensures robustness
- Simpler display than showing multiple measurements

**Alternative considered**: Enable verbose mode via `/config` displays token counter in top-right
- Rejected: Forces verbose output even when unwanted
- Statusbar parsing allows custom statusline without verbose mode requirement

### Limit Threshold (99%)

**Decision**: Treat ≥99% utilization as "at limit"

**Rationale**:
- Sufficient margin for rounding errors
- 99%+ means user is effectively at limit
- More precise than 95%

### Statusline Color Handling

**Decision**: Use `RESET_FG` instead of `RESET` to preserve Claude CLI's dim state

**Rationale**:
- Claude CLI sets the entire statusline as dim by default
- `RESET` (`\033[0m`) clears all attributes including the dim state
- `RESET_FG` (`\033[39m`) only resets foreground color, preserving dim
- This allows colored elements to appear within the dim statusline
- Each element should end with `${RESET_FG}` not `${RESET}`
- Context value colored based on utilization level

**Example**: `🧠 ${GREEN}42k${RESET_FG}`
- Value colored based on context utilization
- Remains visually dim due to CLI's outer styling

### Context Usage Display - Input Validation (2026-01-10)

**Decision**: Validate all numeric inputs before bash arithmetic operations

**Problem**: Empty or invalid values in `TRANSCRIPT_TOKENS` caused:
1. Bash arithmetic errors in integer comparisons
2. Silent function failures returning no color codes
3. Token bar not displaying for valid small values (< 25k)
4. Numbers displaying without proper color (inheriting previous state)

**Fix**: Added comprehensive validation to both functions:
- `get_token_color()`: Check for empty, "unset", non-numeric before comparisons
- `display_token_bar()`: Same validation plus index clamping [0-7]

**Pattern**: `[ -z "$var" ] || [ "$var" = "unset" ] || ! [[ "$var" =~ ^[0-9]+$ ]]`

**Rationale**:
- Bash integer operations fail silently on empty strings
- Empty transcript values occur when file doesn't exist or parsing fails
- Validation prevents errors from propagating to display
- Index clamping prevents out-of-range case statement failures
- Defensive programming for robust statusline rendering

### Time Formatting (Human-Readable)

**Decision**: Context-aware time display using 24-hour notation

**Rationale**:
- Same day: "15:59" (just time)
- Within 7 days: "Mon 15:59" (weekday + time)
- Beyond: "Jan 9 15:59" or "Jan 9 2026 15:59" (full date)
- Always show minutes, no leading zeros for hours
- 24-hour notation (am/pm rejected as "yankee abomination")

**Preposition logic for switch messages**:
- Same day: "at 15:59" (temporal)
- Different day: "on Mon 15:59" (calendar)

### Timezone Handling (UTC to Local Conversion)

**Decision**: Use `date -u -j` to parse UTC timestamps, convert via epoch to local time

**Problem discovered** (2026-01-10): OAuth usage API returns UTC timestamps (`2026-01-10T16:00:00.000Z`), but scripts treated them as local time, causing:
1. Statusline displayed wrong reset times (UTC instead of local)
2. Launchd scheduled switchback at wrong time (UTC hour in local timezone)

**Root cause**: BSD `date -j -f` assumes local timezone when format string lacks timezone specifier
- `cut -d. -f1` strips `.000Z` → loses timezone info
- `date -j -f "%Y-%m-%dT%H:%M:%S"` interprets result as local time
- Example: UTC 16:00 treated as local 16:00 (off by timezone offset)

**Fix**: Add `-u` flag to declare input is UTC
```bash
local reset_epoch=$(date -u -j -f "%Y-%m-%dT%H:%M:%S" "$timestamp_base" +%s)
```

**Why epoch intermediate**:
- Clean separation: UTC parsing → epoch → local formatting
- `date -r $epoch` outputs in local timezone automatically
- Used for both display (`format_reset_time*`) and launchd scheduling

**Alternative rejected**: Append `Z` back and use `%Z` format specifier
- More complex string manipulation
- Same result, less clear intent

**Affected functions**:
- `statusline-command.sh:247` - `format_reset_time_short()`
- `claude-account.sh:281` - `format_reset_time()`
- `claude-account.sh:324` - `format_reset_message()`
- `claude-account.sh:154-158` - `schedule_switchback()` (refactored to use epoch)

### Shell Completions (On-Demand Generation)

**Decision**: Use `claude-account completion <shell>` subcommand to generate completions

**Rationale**:
- Single source of truth (SPOT): Command structure defined once at top of script
- Standard CLI pattern (kubectl, gh, docker use this)
- Users add `eval "$(claude-account completion bash)"` to shell RC
- No need to maintain separate static completion files
- Completions auto-update when script updates

**Command structure variables**:
```bash
COMMANDS="api api! plan status completion"
API_SUBCOMMANDS="session weekly"
COMPLETION_SUBCOMMANDS="bash zsh fish"
```

## File Structure

**Configuration Files**:
- `~/.claude/settings.json` - Global settings (version controlled, no secrets)
- `~/.claude/settings.local.json` - Local overrides (gitignored, contains API key in API mode)
- `~/.claude/account-mode` - Current mode: "plan" or "api" (plain text)
- `~/.claude/api-key` - Anthropic API key source file (user creates, chmod 600)
- `~/.claude/saved-oauth-creds` - OAuth backup during API mode (JSON from keychain)

**Debug Files**:
- `/tmp/claude/statusbar.json` - Latest statusline JSON input (system temp, for debugging)

**Why settings.local.json?**:
- Merges with settings.json (local overrides global)
- Gitignored by default
- API key written to `env.ANTHROPIC_AUTH_TOKEN` during API mode
- Prevents accidentally committing secrets

## Security Considerations

1. **API Key Storage**:
   - Source: `~/.claude/api-key` should be chmod 600 (user-only read)
   - Runtime: Copied to `settings.local.json` `env.ANTHROPIC_AUTH_TOKEN` in API mode
   - Both files gitignored
   - **CRITICAL**: Secrets must NEVER be in `settings.json` (version controlled), only in `settings.local.json` (gitignored)
2. **Keychain Manipulation**: OAuth credentials moved between keychain and file during switches
   - Saved credentials file (`saved-oauth-creds`) should be chmod 600
   - Keychain operations use macOS security command (encrypted storage)
3. **No Logging**: Scripts don't log API keys or tokens
4. **LaunchAgent**: Runs as user (not root), standard permissions
5. **Settings Isolation**: API key in settings.local.json (gitignored, never committed)

## Future Enhancements (Not Implemented)

1. **Proper cost tracking**: Implement accurate cost calculation like `claude-code-monitor`
2. **Notification on switch-back**: macOS notification when auto-switching to plan
3. **Cost alerts**: Warn if API daily cost exceeds threshold
4. **Multi-key support**: Rotate between multiple API keys for rate limiting
5. **Configurable threshold**: Allow user to set custom utilization % for "at limit"

## Reference Materials

- [Claude Pro Usage Limits](https://support.claude.com/en/articles/8324991-about-claude-s-pro-plan-usage)
- [Claude Code API Keys](https://support.claude.com/en/articles/12304248-managing-api-key-environment-variables-in-claude-code)
- [Claude Code IAM](https://code.claude.com/docs/en/iam)
- [Usage API Discussion](https://codelynx.dev/posts/claude-code-usage-limits-statusline)
- [Account Switching Request](https://github.com/anthropics/claude-code/issues/3835)
