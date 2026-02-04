---
name: statusline-wiring
type: tdd
model: haiku
---

# Statusline Wiring TDD Runbook

**Context**: Wire statusline command to display two-line status with model, directory, git, cost, context, and account mode/usage — matching proven shell script behavior
**Design**: plans/statusline-wiring/design.md
**Status**: Draft
**Created**: 2026-02-04

## Weak Orchestrator Metadata

**Total Steps**: 28
**Execution Model**: All cycles: Haiku (TDD execution)
**Step Dependencies**: Sequential within phases, parallel across independent modules
**Error Escalation**: Haiku → User on stop conditions/regression
**Report Locations**: plans/statusline-wiring/reports/
**Success Criteria**: All cycles GREEN, no regressions, two-line statusline output working
**Prerequisites**: Python 3.11+, pytest, anthropic SDK, existing account/model modules

## Common Context

**Requirements (from design):**
- R1: Two-line output format — addressed by CLI composition + StatuslineFormatter
- R2: Context display accuracy after resume — addressed by transcript fallback in context.py
- R3: Switchback time display in API mode — addressed by read_switchback_plist() in api_usage.py
- R4: Usage cache TTL: 10 seconds — addressed by updating UsageCache.TTL_SECONDS
- R5: Always exit 0 — addressed by CLI error handling
- R6: Use existing rewritten infrastructure — addressed by calling account.state/usage/switchback modules

**Scope boundaries:**
- In scope: Two-line display, context calculation, git status, plan/API usage, switchback time
- Out of scope: Cost calculation for API mode, advanced git features (detached HEAD), performance optimization

**Key Design Decisions:**
1. D1: Pydantic models for JSON schema parsing (StatuslineInput with 8 fields)
2. D2: Context calculation with transcript fallback (primary: current_usage sum, fallback: parse transcript)
3. D3: Three module separation (context.py, plan_usage.py, api_usage.py by data domain)
4. D4: CLI composition layer stays thin (orchestrate, don't implement)
5. D5: Use subprocess for git (not GitPython — lightweight, no memory leaks)
6. D6: Pydantic models for all structured data (6 models total)
7. D7: LaunchAgent plist with Month/Day fields (one-shot display)
8. D8: Error handling: fail safe with logging (sensible defaults, always exit 0)

**TDD Protocol:**
Strict RED-GREEN-REFACTOR: 1) RED: Write failing test, 2) Verify RED, 3) GREEN: Minimal implementation, 4) Verify GREEN, 5) Verify Regression, 6) REFACTOR (optional)

**Project Paths:**
- Source: src/claudeutils/statusline/ (models.py, context.py, plan_usage.py, api_usage.py, cli.py, display.py)
- Source: src/claudeutils/account/ (switchback.py, usage.py)
- Tests: tests/test_statusline_*.py

**Conventions:**
- Use Read/Write/Edit/Grep tools (not Bash for file ops)
- Report errors explicitly (never suppress)
- Write notes to plans/statusline-wiring/reports/cycle-{X}-{Y}-notes.md
- Use Pydantic BaseModel for all data structures
- Mock external dependencies (subprocess, file I/O, API calls)
- Test behavior not presentation (content assertions required)

**Test file creation strategy:**
- Test files do not exist before runbook execution
- RED phase creates test file with failing test
- GREEN phase creates source module to pass test
- Pattern: RED writes test → GREEN writes implementation

**Module creation order:**
- Phase 1: models.py (Pydantic schemas)
- Phase 2: context.py (git, thinking, context calculation)
- Phase 3: plan_usage.py (OAuth API usage)
- Phase 4: api_usage.py (stats-cache.json parsing), update switchback.py
- Phase 5: cli.py (orchestration)
- Phase 6: display.py (formatting — already exists, enhancement only)

**Regression testing scope:**
- Phases 1-5: No existing tests (net-new modules) — regression verification skipped
- Phase 6: Existing display.py tests must pass (true regression check)

**Stop Conditions (all cycles):**
STOP IMMEDIATELY if: RED phase test passes (expected failure) • RED phase failure message doesn't match expected • GREEN phase tests don't pass after implementation • Any phase existing tests break (regression)

Actions when stopped: 1) Document in reports/cycle-{X}-{Y}-notes.md 2) Test passes unexpectedly → Investigate if feature exists 3) Regression → STOP, report broken tests 4) Scope unclear → STOP, document ambiguity

**Dependencies (all cycles):**
Sequential within phases (default). Cross-phase dependencies marked explicitly with [DEPENDS: X.Y].

**Output Optimization Note:** Factorize repetitive content (stop conditions, dependencies, conventions, common patterns) to Common Context. Cycles inherit context during runbook compilation.

## Cycle 1.1: Create StatuslineInput model with Claude Code JSON schema

**Objective**: Define Pydantic model for parsing Claude Code stdin JSON
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** tests/test_statusline_models.py parses valid Claude Code JSON into StatuslineInput model with 8 fields (model.display_name, workspace.current_dir, transcript_path, context_window.current_usage, context_window.context_window_size, cost.total_cost_usd, version, session_id)

**Expected failure:**
```
ModuleNotFoundError: No module named 'claudeutils.statusline.models'
```

**Why it fails:** models.py doesn't exist yet

**Verify RED:** pytest tests/test_statusline_models.py::test_parse_valid_json -xvs
- Must fail with ModuleNotFoundError
- If passes, STOP - models.py may already exist

---

**GREEN Phase:**

**Implementation:** Create src/claudeutils/statusline/models.py with StatuslineInput Pydantic model matching Claude Code JSON schema (8 fields, nested structures for model/workspace/context_window/cost)

**Changes:**
- File: src/claudeutils/statusline/models.py
  Action: Create with StatuslineInput, ContextUsage, ModelInfo, WorkspaceInfo, ContextWindowInfo, CostInfo Pydantic models

**Verify GREEN:** pytest tests/test_statusline_models.py::test_parse_valid_json -xvs
- Must pass

**Verify no regression:** pytest tests/test_statusline_*.py
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/statusline-wiring/reports/cycle-1-1-notes.md

---

## Cycle 1.2: Handle current_usage as optional (null case)

**Objective**: StatuslineInput.context_window.current_usage can be None (session resume case per R2)
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** tests/test_statusline_models.py parses JSON with context_window.current_usage=null without validation error

**Expected failure:**
```
ValidationError: current_usage field required
```

**Why it fails:** ContextUsage not marked as Optional

**Verify RED:** pytest tests/test_statusline_models.py::test_parse_null_current_usage -xvs
- Must fail with ValidationError
- If passes, STOP - field may already be optional

---

**GREEN Phase:**

**Implementation:** Update ContextUsage field in ContextWindowInfo to Optional[ContextUsage]

**Changes:**
- File: src/claudeutils/statusline/models.py
  Action: Change current_usage: ContextUsage to current_usage: ContextUsage | None = None

**Verify GREEN:** pytest tests/test_statusline_models.py::test_parse_null_current_usage -xvs
- Must pass

**Verify no regression:** pytest tests/test_statusline_*.py
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/statusline-wiring/reports/cycle-1-2-notes.md

---

## Cycle 1.3: Validate ContextUsage has 4 token fields

**Objective**: Ensure ContextUsage model has all 4 token fields (input_tokens, output_tokens, cache_creation_input_tokens, cache_read_input_tokens)
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** tests/test_statusline_models.py parses JSON with all 4 token fields in current_usage and sums them correctly

**Expected failure:**
```
AttributeError: 'ContextUsage' object has no attribute 'cache_read_input_tokens'
```

**Why it fails:** ContextUsage missing one or more token fields

**Verify RED:** pytest tests/test_statusline_models.py::test_context_usage_has_four_token_fields -xvs
- Must fail with AttributeError
- If passes, STOP - all fields may already exist

---

**GREEN Phase:**

**Implementation:** Define ContextUsage model with 4 int fields

**Changes:**
- File: src/claudeutils/statusline/models.py
  Action: Add ContextUsage(BaseModel) with input_tokens, output_tokens, cache_creation_input_tokens, cache_read_input_tokens: int fields

**Verify GREEN:** pytest tests/test_statusline_models.py::test_context_usage_has_four_token_fields -xvs
- Must pass

**Verify no regression:** pytest tests/test_statusline_*.py
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/statusline-wiring/reports/cycle-1-3-notes.md

---

## Cycle 2.1: Detect git repository and return branch name

**Objective**: get_git_status() calls subprocess to detect if in git repo and get branch name
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** tests/test_statusline_context.py mocks subprocess.run, tests get_git_status() returns GitStatus(branch="main", dirty=False) when git commands succeed

**Expected failure:**
```
ModuleNotFoundError: No module named 'claudeutils.statusline.context'
```

**Why it fails:** context.py doesn't exist yet

**Verify RED:** pytest tests/test_statusline_context.py::test_get_git_status_in_repo -xvs
- Must fail with ModuleNotFoundError
- If passes, STOP - context.py may already exist

---

**GREEN Phase:**

**Implementation:** Create src/claudeutils/statusline/context.py with get_git_status() using subprocess.run for git commands

**Changes:**
- File: src/claudeutils/statusline/context.py
  Action: Create with get_git_status() → GitStatus, call subprocess.run(["git", "rev-parse", "--git-dir"]) and subprocess.run(["git", "branch", "--show-current"])
- File: src/claudeutils/statusline/models.py
  Action: Add GitStatus(BaseModel) with branch: str | None, dirty: bool fields

**Verify GREEN:** pytest tests/test_statusline_context.py::test_get_git_status_in_repo -xvs
- Must pass

**Verify no regression:** pytest tests/test_statusline_*.py
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/statusline-wiring/reports/cycle-2-1-notes.md

---

## Cycle 2.2: Detect dirty git status with porcelain output

**Objective**: get_git_status() detects dirty working tree using git status --porcelain
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** tests/test_statusline_context.py mocks subprocess to return non-empty porcelain output, asserts get_git_status() returns dirty=True

**Expected failure:**
```
AssertionError: assert False == True
```

**Why it fails:** get_git_status() doesn't check git status --porcelain yet

**Verify RED:** pytest tests/test_statusline_context.py::test_get_git_status_dirty -xvs
- Must fail with AssertionError (dirty=False when expected True)
- If passes, STOP - dirty detection may already exist

---

**GREEN Phase:**

**Implementation:** Add subprocess call for git status --porcelain, set dirty=True if output non-empty

**Changes:**
- File: src/claudeutils/statusline/context.py
  Action: Add subprocess.run(["git", "status", "--porcelain"]) call, set dirty = bool(result.stdout.strip())

**Verify GREEN:** pytest tests/test_statusline_context.py::test_get_git_status_dirty -xvs
- Must pass

**Verify no regression:** pytest tests/test_statusline_*.py
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/statusline-wiring/reports/cycle-2-2-notes.md

---

## Cycle 2.3: Handle not in git repo case

**Objective**: get_git_status() returns GitStatus(branch=None, dirty=False) when not in git repo
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** tests/test_statusline_context.py mocks subprocess to raise CalledProcessError, asserts get_git_status() returns GitStatus(branch=None, dirty=False)

**Expected failure:**
```
CalledProcessError: not caught, test crashes
```

**Why it fails:** No exception handling for subprocess failures

**Verify RED:** pytest tests/test_statusline_context.py::test_get_git_status_not_in_repo -xvs
- Must fail with CalledProcessError
- If passes, STOP - exception handling may already exist

---

**GREEN Phase:**

**Implementation:** Wrap subprocess calls in try/except, return GitStatus(branch=None, dirty=False) on subprocess.CalledProcessError or FileNotFoundError

**Changes:**
- File: src/claudeutils/statusline/context.py
  Action: Add try/except around subprocess calls, catch subprocess.CalledProcessError and FileNotFoundError, return default GitStatus

**Verify GREEN:** pytest tests/test_statusline_context.py::test_get_git_status_not_in_repo -xvs
- Must pass

**Verify no regression:** pytest tests/test_statusline_*.py
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/statusline-wiring/reports/cycle-2-3-notes.md

---

## Cycle 2.4: Parse thinking state from settings.json

**Objective**: get_thinking_state() reads ~/.claude/settings.json and returns ThinkingState(enabled=bool)
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** tests/test_statusline_context.py mocks Path.open to return settings JSON with alwaysThinkingEnabled=true, asserts get_thinking_state() returns ThinkingState(enabled=True)

**Expected failure:**
```
AttributeError: module 'claudeutils.statusline.context' has no attribute 'get_thinking_state'
```

**Why it fails:** get_thinking_state() function doesn't exist yet

**Verify RED:** pytest tests/test_statusline_context.py::test_get_thinking_state_enabled -xvs
- Must fail with AttributeError
- If passes, STOP - function may already exist

---

**GREEN Phase:**

**Implementation:** Add get_thinking_state() function that reads ~/.claude/settings.json and parses alwaysThinkingEnabled field

**Changes:**
- File: src/claudeutils/statusline/context.py
  Action: Add get_thinking_state() → ThinkingState, read Path.home() / ".claude" / "settings.json", parse JSON, extract alwaysThinkingEnabled
- File: src/claudeutils/statusline/models.py
  Action: Add ThinkingState(BaseModel) with enabled: bool field

**Verify GREEN:** pytest tests/test_statusline_context.py::test_get_thinking_state_enabled -xvs
- Must pass

**Verify no regression:** pytest tests/test_statusline_*.py
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/statusline-wiring/reports/cycle-2-4-notes.md

---

## Cycle 2.5: Handle missing or malformed settings.json

**Objective**: get_thinking_state() returns ThinkingState(enabled=False) when settings.json missing or invalid JSON
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** tests/test_statusline_context.py mocks Path.exists() to return False, asserts get_thinking_state() returns ThinkingState(enabled=False)

**Expected failure:**
```
FileNotFoundError: [Errno 2] No such file or directory: '~/.claude/settings.json'
```

**Why it fails:** No exception handling for missing file

**Verify RED:** pytest tests/test_statusline_context.py::test_get_thinking_state_missing_file -xvs
- Must fail with FileNotFoundError
- If passes, STOP - exception handling may already exist

---

**GREEN Phase:**

**Implementation:** Wrap file read and JSON parse in try/except, return ThinkingState(enabled=False) on FileNotFoundError or json.JSONDecodeError

**Changes:**
- File: src/claudeutils/statusline/context.py
  Action: Add try/except around Path.open and json.load, catch FileNotFoundError and json.JSONDecodeError, return ThinkingState(enabled=False)

**Verify GREEN:** pytest tests/test_statusline_context.py::test_get_thinking_state_missing_file -xvs
- Must pass

**Verify no regression:** pytest tests/test_statusline_*.py
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/statusline-wiring/reports/cycle-2-5-notes.md

---

## Cycle 2.6: Calculate context tokens from current_usage (primary path)

**Objective**: calculate_context_tokens() sums 4 token fields from StatuslineInput.context_window.current_usage when present
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** tests/test_statusline_context.py creates StatuslineInput with current_usage containing 4 token values (100, 50, 25, 25), asserts calculate_context_tokens() returns 200

**Expected failure:**
```
AttributeError: module 'claudeutils.statusline.context' has no attribute 'calculate_context_tokens'
```

**Why it fails:** calculate_context_tokens() function doesn't exist yet

**Verify RED:** pytest tests/test_statusline_context.py::test_calculate_context_tokens_from_current_usage -xvs
- Must fail with AttributeError
- If passes, STOP - function may already exist

---

**GREEN Phase:**

**Implementation:** Add calculate_context_tokens(input_data: StatuslineInput) → int that sums 4 token fields when current_usage is not None

**Changes:**
- File: src/claudeutils/statusline/context.py
  Action: Add calculate_context_tokens() function, check if current_usage exists, sum input_tokens + output_tokens + cache_creation_input_tokens + cache_read_input_tokens

**Verify GREEN:** pytest tests/test_statusline_context.py::test_calculate_context_tokens_from_current_usage -xvs
- Must pass

**Verify no regression:** pytest tests/test_statusline_*.py
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/statusline-wiring/reports/cycle-2-6-notes.md

---

## Cycle 2.7: Parse transcript for context tokens (fallback path)

**Objective**: calculate_context_tokens() parses transcript file when current_usage is None (R2 requirement)
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** tests/test_statusline_context.py creates StatuslineInput with current_usage=None, mocks Path.open to return transcript JSONL with assistant message containing usage tokens, asserts calculate_context_tokens() returns sum of tokens

**Expected failure:**
```
AssertionError: assert 0 == 200
```

**Why it fails:** calculate_context_tokens() returns 0 when current_usage is None (no fallback yet)

**Verify RED:** pytest tests/test_statusline_context.py::test_calculate_context_tokens_from_transcript -xvs
- Must fail with AssertionError (returns 0 instead of token sum)
- If passes, STOP - transcript fallback may already exist

---

**GREEN Phase:**

**Implementation:** Add parse_transcript_context() helper that reads last 1MB of transcript file, parses JSONL in reverse, finds first assistant message with non-zero tokens

**Changes:**
- File: src/claudeutils/statusline/context.py
  Action: Add parse_transcript_context(transcript_path: str) → int, read last 1MB with seek, parse lines in reverse, filter type=="assistant" and not isSidechain, sum 4 token fields, return first non-zero
- File: src/claudeutils/statusline/context.py
  Action: Update calculate_context_tokens() to call parse_transcript_context() when current_usage is None

**Verify GREEN:** pytest tests/test_statusline_context.py::test_calculate_context_tokens_from_transcript -xvs
- Must pass

**Verify no regression:** pytest tests/test_statusline_*.py
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/statusline-wiring/reports/cycle-2-7-notes.md

---

## Cycle 2.8: Handle missing transcript file gracefully

**Objective**: calculate_context_tokens() returns 0 when transcript file doesn't exist (fail-safe per D8)
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** tests/test_statusline_context.py creates StatuslineInput with current_usage=None and non-existent transcript_path, asserts calculate_context_tokens() returns 0 without raising exception

**Expected failure:**
```
FileNotFoundError: [Errno 2] No such file or directory: 'nonexistent.json'
```

**Why it fails:** parse_transcript_context() doesn't handle missing file

**Verify RED:** pytest tests/test_statusline_context.py::test_calculate_context_tokens_missing_transcript -xvs
- Must fail with FileNotFoundError
- If passes, STOP - exception handling may already exist

---

**GREEN Phase:**

**Implementation:** Wrap file open in try/except, catch FileNotFoundError, return 0

**Changes:**
- File: src/claudeutils/statusline/context.py
  Action: Add try/except around open() in parse_transcript_context(), catch FileNotFoundError, return 0

**Verify GREEN:** pytest tests/test_statusline_context.py::test_calculate_context_tokens_missing_transcript -xvs
- Must pass

**Verify no regression:** pytest tests/test_statusline_*.py
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/statusline-wiring/reports/cycle-2-8-notes.md

---

**Light Checkpoint** (end of Phase 2)
1. Fix: Run `just dev`. Sonnet quiet-task fixes failures. Commit when green.
2. Functional: Review Phase 2 implementations against design. Check for stubs.

---

## Cycle 3.1: Update UsageCache TTL from 30s to 10s

**Objective**: Change UsageCache.TTL_SECONDS constant to 10 (R4 requirement)
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** tests/test_statusline_plan_usage.py imports account.usage.UsageCache, asserts TTL_SECONDS == 10

**Expected failure:**
```
AssertionError: assert 30 == 10
```

**Why it fails:** UsageCache.TTL_SECONDS is currently 30

**Verify RED:** pytest tests/test_statusline_plan_usage.py::test_usage_cache_ttl -xvs
- Must fail with AssertionError (30 != 10)
- If passes, STOP - TTL may already be 10

---

**GREEN Phase:**

**Implementation:** Change TTL_SECONDS constant in UsageCache class

**Changes:**
- File: src/claudeutils/account/usage.py
  Action: Change UsageCache.TTL_SECONDS = 30 to UsageCache.TTL_SECONDS = 10

**Verify GREEN:** pytest tests/test_statusline_plan_usage.py::test_usage_cache_ttl -xvs
- Must pass

**Verify no regression:** pytest tests/
- All existing tests pass (may need to update test expectations if any rely on 30s TTL)

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/statusline-wiring/reports/cycle-3-1-notes.md

---

## Cycle 3.2: Fetch plan usage from OAuth API with cache

**Objective**: get_plan_usage() calls account.usage.UsageCache to fetch 5h/7d limits from Claude OAuth API
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** tests/test_statusline_plan_usage.py mocks UsageCache.get() to return mock usage data, asserts get_plan_usage() returns PlanUsageData with 5h/7d percentages and reset times

**Expected failure:**
```
ModuleNotFoundError: No module named 'claudeutils.statusline.plan_usage'
```

**Why it fails:** plan_usage.py doesn't exist yet

**Verify RED:** pytest tests/test_statusline_plan_usage.py::test_get_plan_usage -xvs
- Must fail with ModuleNotFoundError
- If passes, STOP - plan_usage.py may already exist

---

**GREEN Phase:**

**Implementation:** Create src/claudeutils/statusline/plan_usage.py with get_plan_usage() that uses UsageCache.get()

**Changes:**
- File: src/claudeutils/statusline/plan_usage.py
  Action: Create with get_plan_usage() → PlanUsageData | None, call account.usage.UsageCache(...).get(), parse 5h and 7d limits
- File: src/claudeutils/statusline/models.py
  Action: Add PlanUsageData(BaseModel) with hour5_pct: float, hour5_reset: str, day7_pct: float fields

**Verify GREEN:** pytest tests/test_statusline_plan_usage.py::test_get_plan_usage -xvs
- Must pass

**Verify no regression:** pytest tests/test_statusline_*.py
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/statusline-wiring/reports/cycle-3-2-notes.md

---

## Cycle 3.3: Handle OAuth API failures gracefully

**Objective**: get_plan_usage() returns None when UsageCache.get() fails (fail-safe per D8)
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** tests/test_statusline_plan_usage.py mocks UsageCache.get() to raise exception, asserts get_plan_usage() returns None without propagating exception

**Expected failure:**
```
Exception: API call failed
```

**Why it fails:** No exception handling for UsageCache.get() failures

**Verify RED:** pytest tests/test_statusline_plan_usage.py::test_get_plan_usage_api_failure -xvs
- Must fail with Exception
- If passes, STOP - exception handling may already exist

---

**GREEN Phase:**

**Implementation:** Wrap UsageCache.get() in try/except, return None on any exception

**Changes:**
- File: src/claudeutils/statusline/plan_usage.py
  Action: Add try/except around UsageCache.get(), catch all exceptions, return None

**Verify GREEN:** pytest tests/test_statusline_plan_usage.py::test_get_plan_usage_api_failure -xvs
- Must pass

**Verify no regression:** pytest tests/test_statusline_*.py
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/statusline-wiring/reports/cycle-3-3-notes.md

---

**Light Checkpoint** (end of Phase 3)
1. Fix: Run `just dev`. Sonnet quiet-task fixes failures. Commit when green.
2. Functional: Review Phase 3 implementations against design. Check for stubs.

---

## Cycle 4.1: Update create_switchback_plist to include Month and Day

**Objective**: account.switchback.create_switchback_plist() adds Month and Day to StartCalendarInterval (D7)
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** tests/test_switchback.py (or new test file) mocks plistlib.dump, asserts create_switchback_plist() writes plist with Month and Day fields in StartCalendarInterval

**Expected failure:**
```
AssertionError: 'Month' not in plist_data['StartCalendarInterval']
```

**Why it fails:** create_switchback_plist() currently only writes Hour/Minute/Second

**Verify RED:** pytest tests/test_account_switchback.py::test_create_switchback_plist_includes_month_day -xvs
- Must fail with KeyError or AssertionError (Month/Day missing)
- If passes, STOP - Month/Day may already be included

---

**GREEN Phase:**

**Implementation:** Update create_switchback_plist() to add target_time.month and target_time.day to StartCalendarInterval dict

**Changes:**
- File: src/claudeutils/account/switchback.py
  Action: Add "Month": target_time.month and "Day": target_time.day to StartCalendarInterval dict

**Verify GREEN:** pytest tests/test_account_switchback.py::test_create_switchback_plist_includes_month_day -xvs
- Must pass

**Verify no regression:** pytest tests/
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/statusline-wiring/reports/cycle-4-1-notes.md

---

## Cycle 4.2: Add read_switchback_plist function

**Objective**: account.switchback.read_switchback_plist() parses plist and returns datetime (D7)
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** tests/test_account_switchback.py mocks Path.exists() to return True and plistlib.load() to return mock plist, asserts read_switchback_plist() returns datetime with correct month/day/hour/minute

**Expected failure:**
```
AttributeError: module 'claudeutils.account.switchback' has no attribute 'read_switchback_plist'
```

**Why it fails:** read_switchback_plist() function doesn't exist yet

**Verify RED:** pytest tests/test_account_switchback.py::test_read_switchback_plist -xvs
- Must fail with AttributeError
- If passes, STOP - function may already exist

---

**GREEN Phase:**

**Implementation:** Add read_switchback_plist() → datetime | None that reads plist from ~/Library/LaunchAgents/com.anthropic.claude.switchback.plist, extracts Month/Day/Hour/Minute, constructs datetime

**Changes:**
- File: src/claudeutils/account/switchback.py
  Action: Add read_switchback_plist() function, check Path.exists(), load plist with plistlib, extract StartCalendarInterval fields, build datetime, handle past dates (add year)

**Verify GREEN:** pytest tests/test_account_switchback.py::test_read_switchback_plist -xvs
- Must pass

**Verify no regression:** pytest tests/
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/statusline-wiring/reports/cycle-4-2-notes.md

---

## Cycle 4.3: Handle missing switchback plist gracefully

**Objective**: read_switchback_plist() returns None when plist doesn't exist (fail-safe per D8)
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** tests/test_account_switchback.py mocks Path.exists() to return False, asserts read_switchback_plist() returns None

**Expected failure:**
```
FileNotFoundError: [Errno 2] No such file or directory: '~/Library/LaunchAgents/...'
```

**Why it fails:** read_switchback_plist() doesn't check if file exists before reading

**Verify RED:** pytest tests/test_account_switchback.py::test_read_switchback_plist_missing -xvs
- Must fail with FileNotFoundError
- If passes, STOP - file existence check may already exist

---

**GREEN Phase:**

**Implementation:** Check Path.exists() before attempting to load plist, return None if doesn't exist

**Changes:**
- File: src/claudeutils/account/switchback.py
  Action: Add if not plist_path.exists(): return None at start of read_switchback_plist()

**Verify GREEN:** pytest tests/test_account_switchback.py::test_read_switchback_plist_missing -xvs
- Must pass

**Verify no regression:** pytest tests/
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/statusline-wiring/reports/cycle-4-3-notes.md

---

## Cycle 4.4: Parse stats-cache.json and aggregate by tier

**Objective**: get_api_usage() reads ~/.claude/stats-cache.json and aggregates tokens by model tier (opus/sonnet/haiku)
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** tests/test_statusline_api_usage.py mocks Path.open to return stats-cache.json with dailyModelTokens, asserts get_api_usage() returns ApiUsageData with today_opus, today_sonnet, today_haiku counts

**Expected failure:**
```
ModuleNotFoundError: No module named 'claudeutils.statusline.api_usage'
```

**Why it fails:** api_usage.py doesn't exist yet

**Verify RED:** pytest tests/test_statusline_api_usage.py::test_get_api_usage -xvs
- Must fail with ModuleNotFoundError
- If passes, STOP - api_usage.py may already exist

---

**GREEN Phase:**

**Implementation:** Create src/claudeutils/statusline/api_usage.py with get_api_usage() and aggregate_by_tier() helper

**Changes:**
- File: src/claudeutils/statusline/api_usage.py
  Action: Create with get_api_usage() → ApiUsageData | None, read stats-cache.json, parse dailyModelTokens, aggregate today and last 7 days by tier
- File: src/claudeutils/statusline/api_usage.py
  Action: Add aggregate_by_tier(tokens_by_model: dict) → dict helper that does keyword matching (opus/sonnet/haiku in model name)
- File: src/claudeutils/statusline/models.py
  Action: Add ApiUsageData(BaseModel) with today_opus, today_sonnet, today_haiku, week_opus, week_sonnet, week_haiku: int fields

**Verify GREEN:** pytest tests/test_statusline_api_usage.py::test_get_api_usage -xvs
- Must pass

**Verify no regression:** pytest tests/test_statusline_*.py
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/statusline-wiring/reports/cycle-4-4-notes.md

---

## Cycle 4.5: Calculate week stats by summing last 7 days

**Objective**: get_api_usage() sums last 7 days of token counts for week_* fields
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** tests/test_statusline_api_usage.py mocks stats-cache.json with 7 days of data, asserts get_api_usage() returns week_opus/sonnet/haiku as sum of all 7 days

**Expected failure:**
```
AssertionError: assert 100 == 700  # week_opus should be 7 days * 100
```

**Why it fails:** get_api_usage() only aggregates today's stats, not week

**Verify RED:** pytest tests/test_statusline_api_usage.py::test_get_api_usage_week_aggregation -xvs
- Must fail with AssertionError (week counts don't sum 7 days)
- If passes, STOP - week aggregation may already exist

---

**GREEN Phase:**

**Implementation:** Add loop to sum last 7 days from dailyModelTokens array, aggregate each day by tier, accumulate totals

**Changes:**
- File: src/claudeutils/statusline/api_usage.py
  Action: Add week_stats = data["dailyModelTokens"][-7:], loop through days, aggregate each day, sum to week_by_tier dict

**Verify GREEN:** pytest tests/test_statusline_api_usage.py::test_get_api_usage_week_aggregation -xvs
- Must pass

**Verify no regression:** pytest tests/test_statusline_*.py
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/statusline-wiring/reports/cycle-4-5-notes.md

---

## Cycle 4.6: Handle missing stats-cache.json gracefully

**Objective**: get_api_usage() returns None when stats-cache.json doesn't exist (fail-safe per D8)
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** tests/test_statusline_api_usage.py mocks Path.exists() to return False, asserts get_api_usage() returns None without raising exception

**Expected failure:**
```
FileNotFoundError: [Errno 2] No such file or directory: '~/.claude/stats-cache.json'
```

**Why it fails:** No file existence check or exception handling

**Verify RED:** pytest tests/test_statusline_api_usage.py::test_get_api_usage_missing_file -xvs
- Must fail with FileNotFoundError
- If passes, STOP - exception handling may already exist

---

**GREEN Phase:**

**Implementation:** Check Path.exists() before reading, return None if doesn't exist

**Changes:**
- File: src/claudeutils/statusline/api_usage.py
  Action: Add if not stats_file.exists(): return None at start of get_api_usage()

**Verify GREEN:** pytest tests/test_statusline_api_usage.py::test_get_api_usage_missing_file -xvs
- Must pass

**Verify no regression:** pytest tests/test_statusline_*.py
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/statusline-wiring/reports/cycle-4-6-notes.md

---

## Cycle 4.7: Format switchback time as MM/DD HH:MM [DEPENDS: 4.2]

**Objective**: get_switchback_time() calls read_switchback_plist() and formats datetime as "MM/DD HH:MM" (R3)
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** tests/test_statusline_api_usage.py mocks read_switchback_plist() to return datetime(2026, 2, 3, 14, 30), asserts get_switchback_time() returns "02/03 14:30"

**Expected failure:**
```
AttributeError: module 'claudeutils.statusline.api_usage' has no attribute 'get_switchback_time'
```

**Why it fails:** get_switchback_time() function doesn't exist yet

**Verify RED:** pytest tests/test_statusline_api_usage.py::test_get_switchback_time -xvs
- Must fail with AttributeError
- If passes, STOP - function may already exist

---

**GREEN Phase:**

**Implementation:** Add get_switchback_time() → str | None that calls read_switchback_plist(), formats with strftime("%m/%d %H:%M")

**Changes:**
- File: src/claudeutils/statusline/api_usage.py
  Action: Add get_switchback_time() function, call account.switchback.read_switchback_plist(), return None if None, else format as "MM/DD HH:MM"

**Verify GREEN:** pytest tests/test_statusline_api_usage.py::test_get_switchback_time -xvs
- Must pass

**Verify no regression:** pytest tests/test_statusline_*.py
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/statusline-wiring/reports/cycle-4-7-notes.md

---

**Light Checkpoint** (end of Phase 4)
1. Fix: Run `just dev`. Sonnet quiet-task fixes failures. Commit when green.
2. Functional: Review Phase 4 implementations against design. Check for stubs.

---

## Cycle 5.1: Parse JSON stdin into StatuslineInput in CLI

**Objective**: statusline() CLI command reads stdin, parses JSON into StatuslineInput model (D1)
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** tests/test_statusline_cli.py uses Click CliRunner to invoke statusline with JSON stdin, asserts JSON parsing succeeds without error

**Expected failure:**
```
AssertionError: exit_code == 0, but no real output (still returns "OK" stub)
```

**Why it fails:** CLI doesn't import or use StatuslineInput yet

**Verify RED:** pytest tests/test_statusline_cli.py::test_statusline_parses_json -xvs
- Must fail with stub behavior (output == "OK" instead of real statusline)
- If passes with real output, STOP - StatuslineInput parsing may already exist

---

**GREEN Phase:**

**Implementation:** Update statusline() to parse JSON into StatuslineInput model (no output yet, just parse)

**Changes:**
- File: src/claudeutils/statusline/cli.py
  Action: Import StatuslineInput, replace json.loads() with StatuslineInput.model_validate_json(input_data)

**Verify GREEN:** pytest tests/test_statusline_cli.py::test_statusline_parses_json -xvs
- Must pass (no exception raised)

**Verify no regression:** pytest tests/test_statusline_*.py
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/statusline-wiring/reports/cycle-5-1-notes.md

---

## Cycle 5.2: Call context.py functions in CLI orchestration

**Objective**: statusline() calls get_git_status(), get_thinking_state(), calculate_context_tokens() (D4 thin CLI)
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** tests/test_statusline_cli.py mocks context module functions, asserts statusline() calls all three functions

**Expected failure:**
```
AssertionError: mock not called
```

**Why it fails:** CLI doesn't call context functions yet

**Verify RED:** pytest tests/test_statusline_cli.py::test_statusline_calls_context_functions -xvs
- Must fail with mock not called
- If passes, STOP - context calls may already exist

---

**GREEN Phase:**

**Implementation:** Add calls to context.py functions in statusline() (store results in local vars, no output yet)

**Changes:**
- File: src/claudeutils/statusline/cli.py
  Action: Import context functions, call get_git_status(), get_thinking_state(), calculate_context_tokens(input_data)

**Verify GREEN:** pytest tests/test_statusline_cli.py::test_statusline_calls_context_functions -xvs
- Must pass (all mocks called)

**Verify no regression:** pytest tests/test_statusline_*.py
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/statusline-wiring/reports/cycle-5-2-notes.md

---

## Cycle 5.3: Call get_account_state and route to plan_usage or api_usage

**Objective**: statusline() calls account.state.get_account_state(), branches on mode (D4 orchestration)
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** tests/test_statusline_cli.py mocks get_account_state() to return mode="plan", mocks get_plan_usage(), asserts statusline() calls get_plan_usage() but not get_api_usage()

**Expected failure:**
```
AssertionError: get_plan_usage mock not called
```

**Why it fails:** CLI doesn't call get_account_state() or route to usage functions yet

**Verify RED:** pytest tests/test_statusline_cli.py::test_statusline_routes_to_plan_usage -xvs
- Must fail with mock not called
- If passes, STOP - routing may already exist

---

**GREEN Phase:**

**Implementation:** Add account_state = get_account_state(), if mode == "plan": call get_plan_usage(), elif mode == "api": call get_api_usage()

**Changes:**
- File: src/claudeutils/statusline/cli.py
  Action: Import account.state.get_account_state, plan_usage.get_plan_usage, api_usage.get_api_usage, add mode routing logic

**Verify GREEN:** pytest tests/test_statusline_cli.py::test_statusline_routes_to_plan_usage -xvs
- Must pass (get_plan_usage called)

**Verify no regression:** pytest tests/test_statusline_*.py
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/statusline-wiring/reports/cycle-5-3-notes.md

---

## Cycle 5.4: Format and output two-line statusline with real data

**Objective**: statusline() uses StatuslineFormatter to format and print two lines (R1)
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** tests/test_statusline_cli.py provides full JSON stdin with all fields, mocks all data functions, asserts output contains two lines with model emoji, directory, git branch, cost, context tokens

**Expected failure:**
```
AssertionError: "OK" == "<line1>\\n<line2>"
```

**Why it fails:** CLI still outputs "OK" stub

**Verify RED:** pytest tests/test_statusline_cli.py::test_statusline_outputs_two_lines -xvs
- Must fail with output mismatch (stub vs real output)
- If passes, STOP - real output may already exist

---

**GREEN Phase:**

**Implementation:** Replace click.echo("OK") with StatuslineFormatter calls to format line 1 and line 2, print both lines

**Changes:**
- File: src/claudeutils/statusline/cli.py
  Action: Import StatuslineFormatter, create formatter instance, format line 1 (model + dir + git + cost + context), format line 2 (mode + usage), click.echo() both lines

**Verify GREEN:** pytest tests/test_statusline_cli.py::test_statusline_outputs_two_lines -xvs
- Must pass (two-line output with real data)

**Verify no regression:** pytest tests/test_statusline_*.py
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/statusline-wiring/reports/cycle-5-4-notes.md

---

## Cycle 5.5: Wrap CLI in try/except and always exit 0

**Objective**: statusline() catches all exceptions, logs to stderr, always exits 0 (R5, D8)
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** tests/test_statusline_cli.py mocks one of the data functions to raise Exception, asserts CLI exits 0 and logs error to stderr (not stdout)

**Expected failure:**
```
SystemExit: 1
```

**Why it fails:** CLI doesn't catch exceptions yet, lets them propagate

**Verify RED:** pytest tests/test_statusline_cli.py::test_statusline_exits_zero_on_error -xvs
- Must fail with non-zero exit code
- If passes with exit 0, STOP - exception handling may already exist

---

**GREEN Phase:**

**Implementation:** Wrap entire statusline() body in try/except, catch all exceptions, log to stderr with click.echo(err=True), always return (implicit exit 0)

**Changes:**
- File: src/claudeutils/statusline/cli.py
  Action: Add try/except around entire function body, except Exception as e: click.echo(f"Error: {e}", err=True), ensure no explicit exit(1) calls

**Verify GREEN:** pytest tests/test_statusline_cli.py::test_statusline_exits_zero_on_error -xvs
- Must pass (exit code 0, error on stderr)

**Verify no regression:** pytest tests/test_statusline_*.py
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/statusline-wiring/reports/cycle-5-5-notes.md

---

**Light Checkpoint** (end of Phase 5)
1. Fix: Run `just dev`. Sonnet quiet-task fixes failures. Commit when green.
2. Functional: Review Phase 5 implementations against design. Check for stubs.

---

## Cycle 6.1: Add format_tokens helper for humanized token display

**Objective**: StatuslineFormatter.format_tokens() converts token counts to human-readable strings (1234 → "1k", 150000 → "150k")
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** tests/test_statusline_display.py tests format_tokens(1234) == "1k", format_tokens(150000) == "150k", format_tokens(1500000) == "1.5M"

**Expected failure:**
```
AttributeError: 'StatuslineFormatter' object has no attribute 'format_tokens'
```

**Why it fails:** format_tokens() method doesn't exist yet

**Verify RED:** pytest tests/test_statusline_display.py::test_format_tokens -xvs
- Must fail with AttributeError
- If passes, STOP - method may already exist

---

**GREEN Phase:**

**Implementation:** Add format_tokens(tokens: int) → str method to StatuslineFormatter class

**Changes:**
- File: src/claudeutils/statusline/display.py
  Action: Add format_tokens() method that checks ranges: <1000 → str(n), <1000000 → "Nk", ≥1000000 → "N.NM"

**Verify GREEN:** pytest tests/test_statusline_display.py::test_format_tokens -xvs
- Must pass

**Verify no regression:** pytest tests/test_statusline_*.py
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/statusline-wiring/reports/cycle-6-1-notes.md

---

## Cycle 6.2: Replace limit_display with format_plan_limits

**Objective**: StatuslineFormatter.format_plan_limits() creates compact format for both 5h and 7d limits on one line
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** tests/test_statusline_display.py tests format_plan_limits(PlanUsageData(hour5_pct=87, hour5_reset="14:23", day7_pct=42)) returns string with "87%", "42%", "14:23", and vertical bars

**Expected failure:**
```
AttributeError: 'StatuslineFormatter' object has no attribute 'format_plan_limits'
```

**Why it fails:** format_plan_limits() method doesn't exist yet

**Verify RED:** pytest tests/test_statusline_display.py::test_format_plan_limits -xvs
- Must fail with AttributeError
- If passes, STOP - method may already exist

---

**GREEN Phase:**

**Implementation:** Add format_plan_limits(data: PlanUsageData) → str method, delete limit_display() method (dead code)

**Changes:**
- File: src/claudeutils/statusline/display.py
  Action: Add format_plan_limits() method that formats "5h {pct}% {bar} {reset} / 7d {pct}% {bar}", use vertical_bar() for bars
- File: src/claudeutils/statusline/display.py
  Action: Delete limit_display() method (no longer used)

**Verify GREEN:** pytest tests/test_statusline_display.py::test_format_plan_limits -xvs
- Must pass

**Verify no regression:** pytest tests/test_statusline_*.py
- All existing tests pass (update/remove tests for old limit_display if any)

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/statusline-wiring/reports/cycle-6-2-notes.md

---

**Full Checkpoint** (end of Phase 6 - final phase)
1. Fix: Run `just dev`. Sonnet quiet-task fixes failures. Commit when green.
2. Vet: Review all changes for quality, clarity, design alignment. Apply high/medium fixes. Commit.
3. Functional: Review all implementations against design. Check for stubs.

---

## Design Decisions

**D1. Parse Claude Code JSON stdin schema:**
- Create `StatuslineInput` Pydantic model matching official JSON schema from https://code.claude.com/docs/en/statusline
- Fields used: model.display_name, workspace.current_dir, transcript_path, context_window.current_usage (optional), context_window.context_window_size, cost.total_cost_usd, version, session_id

**D2. Context calculation with transcript fallback:**
- Primary path: sum 4 token fields from current_usage when present
- Fallback path: parse transcript JSONL (last 1MB, reverse order), filter assistant messages, sum tokens from last non-zero entry
- Rationale: Primary fast and accurate, fallback handles session resume (R2)

**D3. Three module separation by data domain:**
- statusline/context.py - Git + thinking state + context calculation
- statusline/plan_usage.py - Plan mode usage limits (OAuth API)
- statusline/api_usage.py - API mode token counts (stats-cache.json)

**D4. CLI composition layer stays thin:**
- CLI orchestrates: parse stdin → call context → get account state → route to plan_usage OR api_usage → format with StatuslineFormatter → print
- No business logic in CLI, all logic in domain modules

**D5. Use subprocess for git (not GitPython):**
- Subprocess: lightweight, no memory leaks, matches codebase pattern
- Commands: git rev-parse --git-dir, git branch --show-current, git status --porcelain

**D6. Pydantic models for all structured data:**
- StatuslineInput, ContextUsage, GitStatus, ThinkingState, PlanUsageData, ApiUsageData
- Type safety, validation, testability

**D7. LaunchAgent plist with Month/Day fields:**
- Update create_switchback_plist() to include Month and Day in StartCalendarInterval
- Add read_switchback_plist() → datetime | None to parse and format switchback time
- Display as "MM/DD HH:MM" in API mode line 2

**D8. Error handling: fail safe with logging:**
- Each data function returns sensible defaults on error (None, empty, "—")
- CLI catches all exceptions at top level, logs to stderr, always exits 0
- Rationale: statusline must never break user workflow (R5)

## Dependencies

**Before**: Existing account/model modules complete (account.state, account.usage, account.switchback, account.keychain), StatuslineFormatter class exists and tested
**After**: Two-line statusline output working end-to-end, all modules tested, ready for production use
