# Statusline Visual Parity Design

## Problem Statement

The Python statusline implementation is **functionally correct** but **visually incomplete** compared to the shell implementation. The conformance validation (plans/statusline-wiring/reports/conformance-validation.md) identified that all data gathering and logic is conformant, but display-layer formatting lacks visual indicators present in the shell version.

### Output Comparison

**Shell output (lines 441-488 of statusline-command.sh):**
```
🥈 Sonnet  📁 code/claudeutils  ✅ tools-rewrite  💰 $0.05  🧠 1.5k [█████░░░░]
🎫 Plan  5h 45% ▆ 2:30 / 7d 23% ▂
```

**Python output (current):**
```
Claude Sonnet code/claudeutils tools-rewrite $0.05 1.5kt
mode: plan | 5h 45% ▆ 2:30 / 7d 23% ▂
```

### Gap Analysis

| Element | Shell Implementation | Python Implementation | Status |
|---------|---------------------|----------------------|--------|
| Model emoji | 🥇/🥈/🥉 (lines 416-428) | Not rendered | Missing |
| Model color | MAGENTA/YELLOW/GREEN | Not rendered | Missing |
| Thinking indicator | 😶 when disabled (line 437-438) | Calls `get_thinking_state()` but ignores result | Missing |
| Directory emoji | 📁 prefix (line 448) | Not rendered | Missing |
| Git status emoji | ✅/🟡 (lines 459-461) | Not rendered | Missing |
| Git branch color | GREEN/YELLOW (lines 459-461) | Not rendered | Missing |
| Cost emoji | 💰 prefix (line 475) | Not rendered | Missing |
| Context emoji | 🧠 prefix (line 486) | Not rendered | Missing |
| Context color | Threshold-based (lines 101-121) | Not rendered | Missing |
| Token bar | Horizontal blocks (lines 169-215) | `token_bar()` exists but unused | Missing |
| Python env | 🐍 VIRTUAL_ENV/CONDA (lines 467-471) | Not implemented | Missing |
| Cache TTL | N/A in shell | 30s (should be 10s per R4) | Non-critical gap |
| Mode emoji | 🎫/💳 (lines 632-637) | "mode:" text prefix | Missing |

---

## Requirements

### R1: Model Display with Visual Indicators

**Shell reference:** lines 416-441

The model display must include:
- Medal emoji based on model tier (🥇 Opus, 🥈 Sonnet, 🥉 Haiku)
- ANSI color coding (MAGENTA Opus, YELLOW Sonnet, GREEN Haiku)
- Abbreviated model name (Opus, Sonnet, Haiku) not full display_name
- Thinking disabled indicator (😶) when `alwaysThinkingEnabled=false`

**Input:** `display_name` from JSON (e.g., "Claude Sonnet 4")
**Output:** `🥈 Sonnet` (colored YELLOW) or `🥈😶 Sonnet` if thinking disabled

### R2: Directory Display with Prefix

**Shell reference:** lines 443-448

The directory display must include:
- 📁 emoji prefix
- CYAN color for directory name
- Basename only (already correct in Python)

**Input:** `current_dir` from JSON
**Output:** `📁 claudeutils` (colored CYAN)

### R3: Git Status with Visual Indicators

**Shell reference:** lines 450-463

The git status display must include:
- ✅ emoji for clean working tree (GREEN branch name)
- 🟡 emoji for dirty working tree (YELLOW BOLD branch name)
- Branch name colored appropriately

**Input:** `GitStatus(branch, dirty)` from `get_git_status()`
**Output:** `✅ tools-rewrite` (GREEN) or `🟡 tools-rewrite` (YELLOW BOLD)

### R4: Cost Display with Prefix

**Shell reference:** lines 474-480

The cost display must include:
- 💰 emoji prefix
- Dollar format with 2 decimal places

**Input:** `total_cost_usd` from JSON
**Output:** `💰 $0.05`

### R5: Context Display with Token Bar

**Shell reference:** lines 482-488, 169-215

The context display must include:
- 🧠 emoji prefix
- Token count formatted in kilos (1.5k, 25k, 1.2M)
- Color based on threshold (BRGREEN < 25k, GREEN < 50k, BLUE < 75k, YELLOW < 100k, RED < 125k, BRRED+BLINK >= 150k)
- Horizontal token bar showing context window fill level

**Token bar algorithm (shell lines 169-215):**
- Each full block (█) represents 25,000 tokens
- Partial blocks use 8-level Unicode characters: ▏▎▍▌▋▊▉█
- Each block colored by threshold (progressive color change)

**Input:** `context_tokens` calculated from current_usage or transcript
**Output:** `🧠 45k [██▌]` with color gradient

### R6: Mode Line with Account Indicator

**Shell reference:** lines 627-642

The mode line must include:
- 🎫 emoji for plan mode (GREEN "Plan")
- 💳 emoji for API mode (YELLOW "API")
- Usage data formatted per existing implementation

**Input:** `account_state.mode`
**Output:** `🎫 Plan  5h 45% ▆ 2:30 / 7d 23% ▂` or `💳 API  ...`

### R7: Python Environment Indicator (Optional)

**Shell reference:** lines 465-472

Display Python environment when active:
- 🐍 emoji prefix
- Environment name from VIRTUAL_ENV or CONDA_DEFAULT_ENV

**Input:** Environment variables
**Output:** `🐍 venv` or empty if no active environment

---

## Design Decisions

### D1: Extend StatuslineFormatter for Emoji Mappings

**Decision:** Add class constants for emoji mappings and color-with-emoji helper methods.

**Rationale:** Keep all display logic in `display.py` per existing architecture. StatuslineFormatter already handles colors and bars.

**Changes to display.py:**
- Add `MODEL_EMOJI` dict: `{"opus": "🥇", "sonnet": "🥈", "haiku": "🥉"}`
- Add `MODEL_COLORS` dict: `{"opus": "magenta", "sonnet": "yellow", "haiku": "green"}`
- Add `format_model()` method: returns emoji + colored name
- Add `format_directory()` method: returns 📁 + CYAN name
- Add `format_git_status()` method: returns ✅/🟡 + colored branch
- Add `format_cost()` method: returns 💰 + formatted amount
- Add `format_context()` method: returns 🧠 + colored tokens + bar
- Add `format_mode()` method: returns 🎫/💳 + colored mode name

### D2: Token Bar Integration

**Decision:** Use existing `token_bar()` method with horizontal multi-block rendering.

**Issue:** Current `token_bar()` returns single character. Shell uses multi-block bar with color gradient.

**Changes to display.py:**
- Rename existing `token_bar()` to `_single_block()` (internal helper)
- Create new `horizontal_token_bar()` method matching shell algorithm (lines 169-215)
- Each 25k tokens = one full block
- Partial block uses 8-level characters
- Progressive color per block (not per bar)

### D3: CLI Composition

**Decision:** CLI calls formatter methods and composes line strings.

**Changes to cli.py:**
- Replace string concatenation with formatter method calls
- Line 1: `format_model()` + `format_directory()` + `format_git_status()` + `format_cost()` + `format_context()`
- Line 2: `format_mode()` + existing usage formatting
- Pass thinking state to `format_model()`

### D4: Model Name Extraction

**Decision:** Extract model tier from `display_name` using substring matching.

**Shell reference:** lines 416-433 match against "Haiku ", "Sonnet ", "Opus "

**Algorithm:**
1. Check if "opus" in display_name.lower() → tier = "opus"
2. Check if "sonnet" in display_name.lower() → tier = "sonnet"
3. Check if "haiku" in display_name.lower() → tier = "haiku"
4. Else → tier = None, use full display_name with no emoji

**Implementation:** Add `_extract_model_tier()` helper in display.py

### D5: Bright Colors

**Decision:** Add bright color variants to StatuslineFormatter.

**Shell uses (lines 81-93):**
- BRGREEN (`\033[92m`) for low token counts
- BRRED (`\033[91m`) for high token counts
- BLINK (`\033[5m`) for critical thresholds

**Changes to display.py:**
- Extend COLORS dict with: `"brgreen": "\033[92m"`, `"brred": "\033[91m"`
- Add BLINK constant: `"\033[5m"`
- Add RESET_BLINK: `"\033[25m"`

### D6: Python Environment Detection

**Decision:** Add `get_python_env()` function to context.py.

**Changes to context.py:**
- New function checking `os.environ.get("VIRTUAL_ENV")` and `os.environ.get("CONDA_DEFAULT_ENV")`
- Returns `PythonEnv(name: str | None)` model
- Called from CLI, formatted with 🐍 prefix if present

**Changes to models.py:**
- Add `PythonEnv` model with optional `name` field

### D7: TTL Adjustment (Non-Critical)

**Decision:** Update `UsageCache` TTL from 30s to 10s per R4 design spec.

**Location:** `src/claudeutils/account/usage.py`
**Change:** Single constant update (low-risk)

---

## File Modification Plan

### Primary Changes

| File | Changes | Lines Added/Modified |
|------|---------|---------------------|
| `src/claudeutils/statusline/display.py` | Add emoji mappings, format methods, horizontal bar | ~80 lines added |
| `src/claudeutils/statusline/cli.py` | Replace string concat with formatter calls | ~20 lines modified |
| `src/claudeutils/statusline/context.py` | Add `get_python_env()` function | ~10 lines added |
| `src/claudeutils/statusline/models.py` | Add `PythonEnv` model | ~5 lines added |
| `src/claudeutils/account/usage.py` | Update TTL constant | 1 line modified |

### Test Changes

| File | Changes | Lines Added/Modified |
|------|---------|---------------------|
| `tests/test_statusline_display.py` | Tests for new format methods | ~100 lines added |
| `tests/test_statusline_cli.py` | Update expected output patterns | ~30 lines modified |
| `tests/test_statusline_context.py` | Tests for `get_python_env()` | ~20 lines added |

---

## Complexity Assessment

### Metrics

- **Files affected:** 5 source + 3 test = 8 files
- **Lines of code:** ~115 source + ~150 test = ~265 total
- **Cycles (TDD):** 12-15 cycles estimated
  - 6 formatter methods (R1-R6): 6 cycles
  - Horizontal token bar: 2 cycles
  - Python env detection: 1 cycle
  - CLI integration: 2 cycles
  - TTL update: 1 cycle
  - Edge cases/polish: 2-3 cycles
- **Model recommendation:** Haiku (execution-focused, patterns established)

### Tier Assessment

**Tier 2: Moderate complexity**

Justification:
- Single session execution (12-15 cycles)
- Pattern replication (shell → Python translation)
- No architectural changes
- Existing test patterns to follow
- Clear reference implementation

**Runbook creation:** Yes (>10 cycles, multi-file coordination)

---

## Risks and Mitigation

### Risk 1: Terminal Emoji Rendering

**Risk:** Some terminals don't render emoji correctly.

**Mitigation:**
- Emojis are optional visual enhancement, not functional
- Text output remains readable without emoji
- No fallback needed (shell version has same dependency)

### Risk 2: ANSI Color Compatibility

**Risk:** Color codes may not work in all terminals.

**Mitigation:**
- Already using standard 16-color ANSI (existing pattern)
- StatuslineFormatter.RESET properly clears formatting
- Same risk profile as existing vertical_bar() usage

### Risk 3: Model Name Matching

**Risk:** New model names may not contain "opus", "sonnet", "haiku".

**Mitigation:**
- Fallback to full display_name with no emoji
- Shell has same limitation (lines 430-432)
- Future: Could add model ID pattern matching

### Risk 4: Token Bar Width

**Risk:** Long token bars could wrap in narrow terminals.

**Mitigation:**
- Maximum 6-7 blocks (175k tokens = context limit)
- Shell has same width constraints
- Unicode blocks are single-width characters

---

## Implementation Order

Recommended TDD cycle order:

1. **Phase 1: Display Formatting** (6 cycles)
   - Cycle 1: `_extract_model_tier()` helper
   - Cycle 2: `format_model()` with emoji/color
   - Cycle 3: `format_directory()` with emoji/color
   - Cycle 4: `format_git_status()` with emoji/color
   - Cycle 5: `format_cost()` with emoji
   - Cycle 6: `format_mode()` with emoji/color

2. **Phase 2: Token Bar** (2 cycles)
   - Cycle 7: `horizontal_token_bar()` multi-block rendering
   - Cycle 8: `format_context()` integration

3. **Phase 3: Environment Detection** (1 cycle)
   - Cycle 9: `get_python_env()` and `PythonEnv` model

4. **Phase 4: CLI Integration** (3 cycles)
   - Cycle 10: Line 1 composition with format methods
   - Cycle 11: Line 2 composition with format methods
   - Cycle 12: Edge cases (missing data, fallbacks)

5. **Phase 5: TTL Update** (1 cycle)
   - Cycle 13: Update UsageCache TTL constant

6. **Phase 6: Validation** (1-2 cycles)
   - Cycle 14: End-to-end integration test
   - Cycle 15: Visual comparison with shell output

---

## Success Criteria

1. **Visual parity:** Python output visually matches shell output for identical input
2. **All tests pass:** Existing tests remain green, new tests cover formatting
3. **No regressions:** Functional behavior unchanged (data gathering, fallbacks)
4. **TTL conformance:** Usage cache TTL is 10 seconds per R4

---

## References

- **Shell implementation:** `/Users/david/code/claudeutils/scratch/home/claude/statusline-command.sh`
- **Conformance report:** `/Users/david/code/claudeutils/plans/statusline-wiring/reports/conformance-validation.md`
- **Architecture decisions:** `/Users/david/code/claudeutils/agents/decisions/architecture.md`
- **Display module:** `/Users/david/code/claudeutils/src/claudeutils/statusline/display.py`
- **CLI module:** `/Users/david/code/claudeutils/src/claudeutils/statusline/cli.py`
