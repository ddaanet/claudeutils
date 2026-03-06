# Command Lint Gate — Runbook Outline

**Tier:** 2 (Lightweight Delegation)
**Type:** TDD throughout — all cycles are behavioral code (new functions, conditional branches)
**Test convention:** Pure function tests for validation; CliRunner for worktree CLI integration

## Phase 1: Command presence validation (type: tdd)

FR-1: Pending/in-progress tasks must have backtick commands.

- Cycle 1.1: `check_command_presence()` — pending `[ ]` without command → error
  - RED: test pending task without backtick command produces error with line number and task name
  - GREEN: new function in `session_commands.py` using `parse_task_line()`, check `parsed.command is None` for pending checkbox
- Cycle 1.2: Checkbox exemptions — completed/blocked/failed/canceled pass without commands
  - RED: test `[x]`, `[!]`, `[†]`, `[-]` tasks without commands produce no errors; `[>]` (in-progress) without command produces error
  - GREEN: filter on checkbox value — only `' '` and `'>'` require commands

**Files:** `src/claudeutils/validation/session_commands.py`, `tests/test_validation_session_commands.py`

## Phase 2: Skill allowlist validation (type: tdd)

FR-2: Slash-command prefix must be in workflow skill allowlist.

- Cycle 2.1: `check_skill_allowlist()` — known skill passes, unknown fails
  - RED: test `/design plans/foo/` passes; `/frobnicate plans/foo/` produces error with skill name in message
  - GREEN: new function in `session_commands.py`, extract skill name from command via regex (`^/([a-z][-a-z]*)`) , check against `WORKFLOW_SKILLS` frozenset
- Cycle 2.2: Non-skill commands pass through
  - RED: test commands without `/` prefix (plain description, `just recipe`) produce no errors
  - GREEN: skip check when command doesn't match `/` prefix pattern
- Cycle 2.3: Multi-word skill commands (e.g., `/requirements` then `/design`)
  - RED: test task with command `/requirements` followed by prose "then /design" — only `/requirements` validated (first backtick command)
  - GREEN: extraction handles the parsed `command` field from `parse_task_line()` which already isolates the first backtick command

**Files:** `src/claudeutils/validation/session_commands.py`, `tests/test_validation_session_commands.py`

## Phase 3: Precommit integration (type: tdd)

FR-3: Wire new checks into `session_structure.py` validation pipeline.

- Cycle 3.1: `validate()` in session_structure calls new checks
  - RED: test `validate()` returns errors for task with missing command and invalid skill name (e2e through session_structure)
  - GREEN: add `check_command_presence()` and `check_skill_allowlist()` calls alongside existing `check_command_semantics()` call at line 371

**Files:** `src/claudeutils/validation/session_structure.py`, `tests/test_validation_session_structure.py`

## Phase 4: Worktree creation gate (type: tdd)

FR-4: Validate command before worktree creation.

- Cycle 4.1: `_worktree new` with task missing command → fails early
  - RED: CliRunner invokes `new` with task name matching a session.md task that has no command → exit code non-zero, error message mentions missing command, no worktree directory created
  - GREEN: in `cli.py` `new()`, after `focus_session()` extracts task, parse the task line and validate command presence + skill allowlist before `_setup_worktree_safe()`

**Files:** `src/claudeutils/worktree/cli.py`, `tests/test_worktree_new_creation.py`

## Recall Entries (for delegation prompts)

- "when preferring e2e over mocked subprocess" — real git repos in tmp_path
- "when testing CLI tools" — Click CliRunner, in-process
- "when splitting validation into mechanical and semantic" — script deterministic checks
- "when choosing script vs agent judgment" — non-cognitive = script
