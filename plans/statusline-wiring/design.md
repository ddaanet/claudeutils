# Design: Statusline Wiring

## Problem

The claudeutils statusline command is a stub that reads JSON from stdin and outputs "OK". It should display a two-line status showing model, directory, git status, cost, context usage, and account mode with usage limits/token counts — matching the proven 575-line shell script behavior.

**Current state:**
- `StatuslineFormatter` (display.py) is complete and tested
- CLI reads stdin and validates JSON but doesn't render statusline
- Missing: data gathering modules (context, git, account integration)
- Missing: composition logic to format two lines

**User requirement:** Context display must be accurate after session resume to support the decision "continue session or clear context."

## Requirements

These are user-provided constraints. Changes require user conversation.

### R1. Two-line output format
First line: Model (with emoji) + Directory + Git (branch/dirty) + Cost + Context (with token bar)
Second line: Account mode + usage info (plan limits OR API token counts)

**Rationale:** Proven shell script design, efficient information density.

### R2. Context display accuracy after session resume
When user resumes a session (no new API call yet), context usage must display the actual context from the previous turn, not "—" or "0".

**Implementation requirement:** Fallback to transcript parsing when `context_window.current_usage` is null.

**Rationale:** User needs accurate context to decide whether to continue session or clear.

### R3. Switchback time display in API mode
Second line must show "Switchback: MM/DD HH:MM" when LaunchAgent plist exists.

**Rationale:** User needs to know when automatic switchback to plan mode will occur (requires Claude Code restart).

### R4. Usage cache TTL: 10 seconds
OAuth usage API responses must be cached for 10 seconds to avoid rate limiting.

**Current state:** `account.usage.UsageCache` has 30s TTL (needs change to 10s).

**Rationale:** Balance between API efficiency and display freshness.

### R5. Always exit 0
Statusline must never fail visibly to the user (Claude Code async render contract).

**Implementation requirement:** Catch all exceptions, log/suppress errors, always return exit code 0.

**Rationale:** Shell script behavior (line 575: `exit 0`), matches async statusline expectations.

### R6. Use existing rewritten infrastructure
Do not rewrite account/model modules. Use:
- `account.state.get_account_state()` for mode detection
- `account.usage.UsageCache` for OAuth usage API (update TTL to 10s)
- `account.switchback.create_switchback_plist()` for plist structure reference
- `account.keychain.Keychain` for credential access
- `account.providers` (Anthropic, OpenRouter, LiteLLM)
- `model.config` for LiteLLM model metadata

**Rationale:** Python rewrite already complete, proven working, avoid duplication.

## Design Decisions

These are technical choices made by the design agent. Can be changed by design agent in revised design.

### D1. Parse Claude Code JSON stdin schema
**Decision:** Create `StatuslineInput` Pydantic model matching official JSON schema from https://code.claude.com/docs/en/statusline

**Fields used:**
- `model.display_name` (str)
- `workspace.current_dir` (str)
- `transcript_path` (str, for context fallback)
- `context_window.current_usage` (dict | None, has 4 token fields)
- `context_window.context_window_size` (int)
- `cost.total_cost_usd` (float)
- `version` (str, unused but in schema)
- `session_id` (str, unused but in schema)

**Rationale:** Type-safe parsing, validation, clear documentation of what we consume from Claude Code.

**Alternative considered:** Parse JSON ad-hoc with dict access. Rejected: no validation, harder to test, no IDE support.

### D2. Context calculation with transcript fallback
**Decision:** Two-path context usage calculation:

**Primary path:**
```python
if current_usage := input_data.context_window.current_usage:
    return (current_usage.input_tokens +
            current_usage.output_tokens +
            current_usage.cache_creation_input_tokens +
            current_usage.cache_read_input_tokens)
```

**Fallback path (when current_usage is null):**
Parse transcript file:
- Filter: type=="assistant", isSidechain==false
- Extract: message.usage (4 token fields)
- Sum tokens, skip zeros, take last entry

**Rationale:** Primary path is fast and accurate when present. Fallback handles session resume case per R2. Matches shell script behavior (lines 295-312 of shell-design-decisions.md).

**Alternative considered:** Display "—" when null. Rejected: violates R2 (user requirement for accuracy after resume).

### D3. Three module separation by data domain
**Decision:**
- `statusline/context.py` - Git + thinking state + context calculation (subprocess + file I/O + transcript parsing)
- `statusline/plan_usage.py` - Plan mode usage limits (account.usage integration)
- `statusline/api_usage.py` - API mode token counts by model tier (stats-cache.json parsing)

**Rationale:** Each module owns one data domain, independently testable with mocks. Matches the shell script's three data-gathering domains.

**Alternative considered:** Single large module. Rejected: harder to test, violates SRP.

### D4. CLI composition layer stays thin
**Decision:** `statusline/cli.py` orchestrates but doesn't contain business logic:
1. Parse JSON stdin → StatuslineInput model
2. Call context.py to get git/thinking/context data
3. Call account.state.get_account_state() to determine mode
4. Call plan_usage.py OR api_usage.py based on mode
5. Format two lines using StatuslineFormatter
6. Print to stdout, always exit 0

**Rationale:** CLI is wiring, not logic. Makes testing easier (test business logic in modules, test composition in CLI integration tests).

**Alternative considered:** Put logic in CLI. Rejected: harder to test, violates separation of concerns.

### D5. Use subprocess for git (not GitPython)
**Decision:** Call git commands via subprocess.run():
- `git branch --show-current` for branch name
- `git status --porcelain` for dirty detection (non-empty output = dirty)
- `git rev-parse --git-dir` to check if in git repo

**Rationale:**
- Lightweight (stdlib only)
- No memory leak concerns (GitPython has known leaks, unsuitable for frequent calls)
- GitPython is in maintenance mode (no active development)
- Matches existing codebase pattern (account.keychain uses subprocess)
- Shell script proved subprocess works

**Alternative considered:** GitPython dependency. Rejected: heavyweight, memory leaks, maintenance mode, still needs git in PATH.

### D6. Pydantic models for all structured data
**Decision:** Define models for:
- `StatuslineInput` (stdin JSON schema)
- `ContextUsage` (current_usage 4 token fields, optional)
- `GitStatus` (branch: str | None, dirty: bool)
- `ThinkingState` (enabled: bool)
- `PlanUsageData` (5h/7d limits with percentages and reset times)
- `ApiUsageData` (token counts by model tier, today + 7d)

**Rationale:** Type safety, validation, testability, self-documenting code. Follows existing codebase pattern (AccountState model in account.state).

**Alternative considered:** Use dicts/tuples. Rejected: no validation, harder to test, no IDE support.

### D7. LaunchAgent plist with Month/Day fields
**Decision:**
- Update `account.switchback.create_switchback_plist()` to include Month and Day in `StartCalendarInterval`
- Add `account.switchback.read_switchback_plist() -> datetime | None` to parse existing plist and extract switchback time

**Rationale:**
- Switchback display is required (R3)
- Current implementation only stores Hour/Minute/Second (repeating daily event)
- Need Month/Day for one-shot display: "Switchback: 02/03 14:30"
- Use stdlib plistlib for consistency
- Return None if plist doesn't exist or can't be parsed

**Alternative considered:** Infer date from plist mtime. Rejected: fragile (file mtime can change), explicit is better.

### D8. Error handling: fail safe with logging
**Decision:**
- Each data-gathering function returns sensible defaults on error (None, empty dict, "—")
- CLI catches all exceptions at top level
- Log errors to stderr (visible in Claude Code debug logs)
- Always exit 0 (R5)

**Rationale:** Statusline must never break user workflow. Degraded display better than no display. Matches shell script behavior.

**Alternative considered:** Exit with error codes. Rejected: violates R5, breaks async statusline contract.

## Architecture

### Module Layout

```
src/claudeutils/statusline/
  __init__.py          # Re-exports (already exists)
  display.py           # StatuslineFormatter (already exists, complete)
  models.py            # Pydantic models (NEW)
  context.py           # Git + thinking + context calculation (NEW)
  plan_usage.py        # Plan mode usage display (NEW)
  api_usage.py         # API mode token display (NEW)
  cli.py               # Composition + output (REPLACE STUB)
```

### Data Flow

```
Claude Code stdin JSON
  ↓
StatuslineInput (Pydantic parse)
  ↓
CLI orchestration:
  ├─→ context.py → GitStatus, ThinkingState, context_tokens
  ├─→ account.state.get_account_state() → mode
  ├─→ plan_usage.py (if mode=="plan") → PlanUsageData
  └─→ api_usage.py (if mode=="api") → ApiUsageData
  ↓
StatuslineFormatter (format with colors/bars)
  ↓
Two lines to stdout
```

### Module Responsibilities

**statusline/models.py** (NEW):
- `StatuslineInput`: Parse Claude Code JSON schema
- `ContextUsage`: Optional 4-token-field structure
- `GitStatus`: branch + dirty boolean
- `ThinkingState`: enabled boolean
- `PlanUsageData`: 5h/7d limits with percentages and reset times
- `ApiUsageData`: token counts by model tier (opus/sonnet/haiku)

**statusline/context.py** (NEW):
- `get_git_status() -> GitStatus`: subprocess git calls
- `get_thinking_state() -> ThinkingState`: parse ~/.claude/settings.json
- `calculate_context_tokens(input_data: StatuslineInput) -> int`: sum current_usage OR parse transcript

**statusline/plan_usage.py** (NEW):
- `get_plan_usage() -> PlanUsageData | None`: fetch usage from Claude OAuth API (via anthropic.Anthropic client), cache for 10s using account.usage.UsageCache, parse 5h/7d limits
- Requires: ANTHROPIC_API_KEY environment variable (from keychain via account.keychain), anthropic SDK dependency

**statusline/api_usage.py** (NEW):
- `get_api_usage() -> ApiUsageData | None`: parse ~/.claude/stats-cache.json, aggregate by model tier (opus/sonnet/haiku)
- `get_switchback_time() -> str | None`: call account.switchback.read_switchback_plist() (NEW function), format as "MM/DD HH:MM"

**statusline/cli.py** (REPLACE):
- `statusline()`: Click command, orchestrates data gathering, formats output, always exits 0

**account/switchback.py** (EXTEND):
- Update `create_switchback_plist()`: add Month and Day to StartCalendarInterval (currently only has Hour/Minute/Second)
- `read_switchback_plist() -> datetime | None` (NEW): parse ~/Library/LaunchAgents/com.anthropic.claude.switchback.plist, extract Month/Day/Hour/Minute

**account/usage.py** (MODIFY):
- Change `UsageCache.TTL_SECONDS` from 30 to 10 (per R4)

**statusline/display.py** (MODIFY):
- Replace `limit_display()` with `format_plan_limits()`: compact format for two limits on one line (5h and 7d together)
- Add `format_tokens(tokens: int) -> str`: humanize token counts (1234 → "1k", 150000 → "150k", 1500000 → "1.5M")

### Testing Strategy

**Unit tests (with mocks):**
- `test_context.py`: Mock subprocess.run (git commands), mock Path.read_text (settings.json), mock Path.open (transcript)
- `test_plan_usage.py`: Mock account.usage.UsageCache.get()
- `test_api_usage.py`: Mock Path.read_text (stats-cache.json), mock account.switchback.read_switchback_plist()
- `test_models.py`: Pydantic validation (valid/invalid JSON inputs)

**Integration test:**
- `test_cli_statusline.py`: Full stdin JSON → two-line output, golden file comparison
- Mock: subprocess (git), file reads (settings.json, stats-cache.json), account.usage calls

**Edge cases to test:**
- context_window.current_usage is null (triggers transcript fallback)
- transcript file doesn't exist (display "—")
- Not in git repo (no branch/dirty display)
- stats-cache.json missing (no API usage display)
- LaunchAgent plist missing (no switchback time display)
- git command fails (subprocess error)
- settings.json malformed (thinking state unknown)

## Implementation Notes

### Context Calculation Details

**Primary path (current_usage present):**
```python
def calculate_context_tokens(input_data: StatuslineInput) -> int:
    """Calculate context window usage from Claude Code JSON.

    Args:
        input_data: Parsed StatuslineInput from stdin JSON

    Returns:
        Total context tokens (sum of 4 fields) or 0 if unavailable
    """
    if usage := input_data.context_window.current_usage:
        # Sum all 4 token fields
        return (usage.input_tokens + usage.output_tokens +
                usage.cache_creation_input_tokens +
                usage.cache_read_input_tokens)
    # Fallback to transcript parsing
    return parse_transcript_context(input_data.transcript_path)
```

**Fallback path (transcript parsing):**
Shell script reference (lines 295-312):
```bash
jq -c 'select(.type == "assistant" and (.isSidechain | not)) |
       .message.usage |
       (input_tokens + cache_creation_input_tokens +
        cache_read_input_tokens + output_tokens)' transcript.json \
  | grep -v '^0$' | tail -1
```

Python equivalent (memory-efficient, reads last 1MB only):
```python
def parse_transcript_context(transcript_path: str) -> int:
    """Parse transcript file for most recent context usage.

    Reads file from end (last 1MB) to avoid loading large transcripts.
    Filters for main-session assistant messages with non-zero tokens.

    Args:
        transcript_path: Path to transcript JSONL file

    Returns:
        Total tokens from most recent assistant message, or 0 if none found
    """
    try:
        MAX_READ_SIZE = 1024 * 1024  # 1MB - reasonable for ~1000 messages

        with open(transcript_path, 'rb') as f:
            # Seek to end, read last MAX_READ_SIZE bytes
            f.seek(0, 2)  # Seek to end
            file_size = f.tell()
            start_pos = max(0, file_size - MAX_READ_SIZE)
            f.seek(start_pos)

            # Skip partial first line if we didn't start at beginning
            if start_pos > 0:
                f.readline()

            lines = f.readlines()

        # Parse lines in reverse order
        for line_bytes in reversed(lines):
            try:
                entry = json.loads(line_bytes.decode('utf-8'))
                if (entry.get("type") == "assistant" and
                    not entry.get("isSidechain", False)):
                    usage = entry.get("message", {}).get("usage", {})
                    tokens = (usage.get("input_tokens", 0) +
                             usage.get("output_tokens", 0) +
                             usage.get("cache_creation_input_tokens", 0) +
                             usage.get("cache_read_input_tokens", 0))
                    if tokens > 0:
                        return tokens
            except (json.JSONDecodeError, UnicodeDecodeError):
                continue  # Skip malformed lines

    except FileNotFoundError:
        pass

    return 0  # Default: no context found
```

### Git Status Detection

```python
def get_git_status() -> GitStatus:
    try:
        # Check if in git repo
        subprocess.run(["git", "rev-parse", "--git-dir"],
                      capture_output=True, check=True)

        # Get branch name
        result = subprocess.run(["git", "branch", "--show-current"],
                               capture_output=True, text=True)
        branch = result.stdout.strip() or None

        # Check if dirty
        result = subprocess.run(["git", "status", "--porcelain"],
                               capture_output=True, text=True)
        dirty = bool(result.stdout.strip())

        return GitStatus(branch=branch, dirty=dirty)
    except (subprocess.CalledProcessError, FileNotFoundError):
        return GitStatus(branch=None, dirty=False)
```

### Output Format

**Line 1 format:**
```
🥈 Sonnet  📁 claudeutils-tools  ✅ main  💰 $0.12  🧠 42k ▅
```

Components:
- Model emoji (🥉 Haiku, 🥈 Sonnet, 🥇 Opus) + thinking indicator (😶 if disabled, from `~/.claude/settings.json` → `alwaysThinkingEnabled` field)
- Directory basename (use `Path(workspace.current_dir).name`)
- Git: ✅ (clean) or 🟡 (dirty) + branch name (or just indicator if not in git repo / detached HEAD)
- Cost with 2 decimals
- Context: token count (humanized via `format_tokens()`) + token bar (from StatuslineFormatter.token_bar())

**Line 2 format (Plan mode):**
```
🎫 Plan  5h 87% ▇ 14:23 / 7d 42% ▄
```

Components:
- "🎫 Plan" badge
- Compact format: both limits on one line
- 5h limit: percentage + vertical bar + reset time (HH:MM)
- "/" separator
- 7d limit: percentage + vertical bar (no reset time, different cadence)

**Line 2 format (API mode):**
```
💳 API  42k/15k/8k today  156k/89k/34k 7d  Switchback: 02/03 14:30
```

Components:
- "💳 API" badge
- Token counts by tier (opus/sonnet/haiku) in color (magenta/yellow/green), humanized via `format_tokens()`
- Switchback time if LaunchAgent plist exists (MM/DD HH:MM format)

### LaunchAgent Plist Updates

Update `account/switchback.py`:

**1. Update `create_switchback_plist()` to include Month/Day:**
```python
def create_switchback_plist(plist_path: Path, switchback_time: int) -> None:
    """Create a macOS LaunchAgent plist for switchback scheduling."""
    target_time = datetime.now(UTC) + timedelta(seconds=switchback_time)

    plist_data = {
        "Label": "com.anthropic.claude.switchback",
        "ProgramArguments": ["/usr/local/bin/claudeutils", "account", "switchback"],
        "StartCalendarInterval": {
            "Month": target_time.month,      # NEW
            "Day": target_time.day,          # NEW
            "Hour": target_time.hour,
            "Minute": target_time.minute,
            "Second": target_time.second,
        },
    }

    with plist_path.open("wb") as f:
        plistlib.dump(plist_data, f)
```

**2. Add `read_switchback_plist()` function:**
```python
def read_switchback_plist() -> datetime | None:
    """Read switchback time from LaunchAgent plist.

    Returns None if plist doesn't exist or can't be parsed.
    """
    plist_path = (Path.home() / "Library" / "LaunchAgents" /
                  "com.anthropic.claude.switchback.plist")
    if not plist_path.exists():
        return None

    try:
        with plist_path.open("rb") as f:
            plist = plistlib.load(f)
            interval = plist["StartCalendarInterval"]

            # Build datetime from Month/Day/Hour/Minute fields
            # Note: plist doesn't store year, assume current or next year
            now = datetime.now()
            target = datetime(
                year=now.year,
                month=interval["Month"],
                day=interval["Day"],
                hour=interval["Hour"],
                minute=interval["Minute"]
            )

            # If target is in the past, it must be next year
            if target < now:
                target = target.replace(year=now.year + 1)

            return target
    except (KeyError, plistlib.InvalidFileException):
        return None
```

### Stats Cache Parsing

Shell script reference: aggregates `stats-cache.json` by model tier (opus/sonnet/haiku keyword matching).

**File format (example):**
```json
{
  "dailyModelTokens": [
    {
      "date": "2026-02-01",
      "tokensByModel": {
        "claude-opus-4": 125000,
        "claude-sonnet-4": 45000,
        "claude-haiku-4": 12000
      }
    }
  ]
}
```

**Implementation:**
```python
def get_api_usage() -> ApiUsageData | None:
    stats_file = Path.home() / ".claude" / "stats-cache.json"
    if not stats_file.exists():
        return None

    try:
        with stats_file.open() as f:
            data = json.load(f)

        # Aggregate today's tokens by tier
        today = datetime.now().strftime("%Y-%m-%d")
        today_stats = next((d for d in data["dailyModelTokens"]
                           if d["date"] == today), None)
        today_by_tier = aggregate_by_tier(today_stats["tokensByModel"]) if today_stats else {"opus": 0, "sonnet": 0, "haiku": 0}

        # Aggregate last 7 days
        week_stats = data["dailyModelTokens"][-7:]
        week_by_tier = {"opus": 0, "sonnet": 0, "haiku": 0}
        for day in week_stats:
            day_tiers = aggregate_by_tier(day["tokensByModel"])
            for tier in week_by_tier:
                week_by_tier[tier] += day_tiers[tier]

        return ApiUsageData(
            today_opus=today_by_tier["opus"],
            today_sonnet=today_by_tier["sonnet"],
            today_haiku=today_by_tier["haiku"],
            week_opus=week_by_tier["opus"],
            week_sonnet=week_by_tier["sonnet"],
            week_haiku=week_by_tier["haiku"],
        )
    except (json.JSONDecodeError, KeyError, IndexError):
        return None

def aggregate_by_tier(tokens_by_model: dict) -> dict:
    """Aggregate token counts by model tier (opus/sonnet/haiku).

    Uses keyword matching on model IDs (case-insensitive).
    """
    result = {"opus": 0, "sonnet": 0, "haiku": 0}
    for model_id, tokens in tokens_by_model.items():
        model_lower = model_id.lower()
        if "opus" in model_lower:
            result["opus"] += tokens
        elif "sonnet" in model_lower:
            result["sonnet"] += tokens
        elif "haiku" in model_lower:
            result["haiku"] += tokens
    return result
```

## Documentation Perimeter

**Required reading (planner must load before starting):**

Design documents:
- `plans/statusline-wiring/design.md` (this file)
- `plans/claude-tools-rewrite/migration-learnings.md` (avoid code duplication, use existing modules)
- `plans/claude-tools-rewrite/shell-design-decisions.md` (original shell implementation details, context calculation logic lines 295-312)

Codebase references:
- `agents/decisions/architecture.md` — module patterns, Pydantic models, error handling
- `src/claudeutils/account/state.py` — AccountState model pattern to follow
- `src/claudeutils/account/usage.py` — UsageCache pattern (update TTL to 10s)
- `src/claudeutils/account/switchback.py` — Update create function (add Month/Day), add read function
- `src/claudeutils/account/keychain.py` — OAuth token retrieval for usage API
- `src/claudeutils/statusline/display.py` — StatuslineFormatter methods (replace limit_display, add format_tokens)

External specifications:
- https://code.claude.com/docs/en/statusline — Claude Code JSON stdin schema
- anthropic SDK usage API: https://docs.anthropic.com/ (for OAuth usage endpoint)

**Additional research allowed:** Planner may read additional test files or explore related modules for implementation details not covered above.

## Instruction for Plan Vet Agent

**Validation scope:** Review plan adherence to design decisions (D1-D8), not requirements (requirements validated during implementation vet).

**Check for:**
1. **Module separation (D3, D4):** Does plan have 3 separate modules (context/plan_usage/api_usage)? Is CLI thin (composition only)?
2. **Pydantic models (D1, D6):** Does plan define StatuslineInput and other models? Are they used for parsing?
3. **Context calculation (D2):** Does plan implement primary path (current_usage sum) AND fallback path (memory-efficient transcript parsing)?
4. **Subprocess git (D5):** Does plan use subprocess.run for git (not GitPython)?
5. **Error handling (D8):** Does plan catch exceptions and return defaults? Does CLI always exit 0?
6. **Existing infrastructure (R6):** Does plan call account.state/usage/switchback instead of reimplementing?
7. **LaunchAgent updates (D7):** Does plan update create_switchback_plist() to add Month/Day AND add read_switchback_plist()?
8. **Cache TTL (R4):** Does plan change UsageCache.TTL_SECONDS from 30 to 10?
9. **OAuth usage API (CO2 fix):** Does plan implement usage API call in plan_usage.py with OAuth token from keychain?
10. **StatuslineFormatter updates:** Does plan replace limit_display() with format_plan_limits() compact format AND add format_tokens()?

**Red flags:**
- Plan puts business logic in CLI (violates D4)
- Plan uses dict parsing instead of Pydantic (violates D1, D6)
- Plan only implements current_usage path without transcript fallback (violates D2, breaks R2)
- Plan reads entire transcript into memory (violates memory-efficient fix)
- Plan adds GitPython dependency (violates D5)
- Plan reimplements account/model logic (violates R6)
- Plan keeps old limit_display() method (violates "no dead code" principle)

**Report format:** List issues found with references to specific design decisions violated. If plan passes all checks, state "Plan adheres to design decisions."

## Out of Scope (Follow-up Work)

Deferred to later designs:

1. **Cost calculation for API mode** - Shell script doesn't compute cost, just shows tokens. Cost requires model-specific pricing data.
2. **OpenRouter custom statusline** - Shell script delegated to TypeScript script. Not needed (user confirmed LiteLLM replaces OpenRouter).
3. **Performance optimization** - <100ms startup acceptable for async render (design.md line 371). Optimize only if users report slowness.
4. **Advanced git features** - Detached HEAD, rebase in progress, etc. Shell script handles basic branch/dirty only.

## Next Steps

1. Load `/plan-tdd` skill before planning
2. Create TDD runbook from this design
3. Execute runbook with TDD discipline (RED/GREEN/REFACTOR)
4. Vet plan against design decisions (D1-D8) before execution
