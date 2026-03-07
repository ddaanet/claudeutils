---
name: handoff-cli-tool
model: sonnet
---

# Session CLI Tool

**Context**: `claudeutils _session` command group — mechanical CLI for handoff, commit, and status operations. Internal (underscore prefix, hidden from `--help`). Skills remain the user interface; CLI handles writes, validation, subprocess orchestration.
**Design**: `plans/handoff-cli-tool/outline.md`
**Status**: Ready
**Created**: 2026-03-07

---

## Weak Orchestrator Metadata

**Total Steps**: 29

**Execution Model**:
- Steps 1.1-1.3: Sonnet (infrastructure extraction, package setup, git CLI)
- Cycles 2.1-2.2: Sonnet (session.md parser)
- Cycles 3.1-3.4: Sonnet (status subcommand rendering + CLI wiring)
- Cycles 4.1-4.7: Sonnet (handoff pipeline with state caching)
- Cycles 5.1-5.3: Sonnet (commit parser + vet check)
- Cycles 6.1-6.6: Sonnet (commit pipeline + submodule coordination)
- Cycles 7.1-7.4: Sonnet (integration tests)

**Step Dependencies**: Sequential within phases, phases sequential (2 depends on 1, 3 on 2, 4 on 2, 5 independent, 6 on 5, 7 on all)

**Error Escalation**:
- Sonnet → User: Architectural ambiguity, design gaps, test failures after 2 attempts

**Report Locations**: `plans/handoff-cli-tool/reports/`

**Success Criteria**: All three subcommands (`_session status`, `_session handoff`, `_session commit`) functional with full test coverage. `just precommit` passes.

**Prerequisites**:
- `src/claudeutils/worktree/git_ops.py` exists with `_git()` function (verified via Glob)
- `src/claudeutils/cli.py` exists with `cli.add_command()` pattern (verified via Glob)
- `src/claudeutils/validation/task_parsing.py` exists with `ParsedTask` (verified via Glob)
- `src/claudeutils/worktree/session.py` exists with `extract_task_blocks()` (verified via Glob)

---

## Common Context

**Requirements (from design):**
- S-1: Package structure — `_session` command group registered in main cli.py
- S-2: `_git()` extraction — move from worktree to shared `claudeutils/git.py` with submodule discovery
- S-3: Output/error — all stdout, exit code carries signal, no stderr
- S-4: Session.md parser — shared parser extending existing `worktree/session.py`
- S-5: Git status/diff — unified parent + submodule view CLI
- Handoff: stdin parsing, session.md writes, committed detection, state caching, diagnostics
- Commit: stdin parsing, scripted vet check, submodule coordination, structured output
- Status: pure data transformation, session.md + filesystem → STATUS format

**Scope boundaries:**
- IN: `_session` group (handoff, commit, status), `_git` group (status, diff), shared parser, git extraction, tests
- OUT: Gate A (LLM judgment), commit message drafting, gitmoji, skill modifications, pending task mutations

**Key Constraints:**
- All output to stdout as structured markdown — no stderr (S-3)
- Exit codes: 0=success, 1=pipeline error, 2=input validation
- `_fail()` pattern with `Never` return type for error termination
- CliRunner + real git repos via `tmp_path` for all tests
- Reuse existing `ParsedTask`, `extract_task_blocks()`, `find_section_bounds()` — do not duplicate

**Project Paths:**
- `src/claudeutils/worktree/git_ops.py`: Source of `_git()`, `_is_submodule_dirty()` for extraction
- `src/claudeutils/worktree/session.py`: Existing session.md parsing (TaskBlock, extract_task_blocks, find_section_bounds)
- `src/claudeutils/validation/task_parsing.py`: ParsedTask, parse_task_line, TASK_PATTERN
- `src/claudeutils/cli.py`: Main CLI with `cli.add_command()` registration pattern
- `src/claudeutils/exceptions.py`: Project exception hierarchy

**Stop/Error Conditions (all cycles):**
- RED fails to fail → STOP, diagnose test (assertion may be vacuous)
- GREEN passes without implementation → STOP, test too weak
- `just precommit` fails after GREEN → fix lint/test issues before proceeding
- Implementation needs architectural decision → STOP, escalate to user

**Dependencies (all cycles):**
- Phases are sequential: Phase N depends on Phase N-1 unless noted otherwise
- Phase 5 is independent of Phases 3-4 (commit parser has no dependency on status/handoff)
- Phase 6 depends on Phase 5 (commit pipeline uses commit parser + vet check)
- Phase 7 depends on all prior phases (integration tests)

### Phase 1: Shared infrastructure (type: general, model: sonnet)

Extract git utilities and establish package structure. Foundation for all subcommands.

---

## Step 1.1: Extract git helpers to `claudeutils/git.py`

**Objective:** Move `_git()` and `_is_submodule_dirty()` from `worktree/git_ops.py` to new `claudeutils/git.py`, add `discover_submodules()`, `_git_ok()`, and `_fail()`. Update all import sites.

**Script Evaluation:** Medium (~60 lines new code + import updates across 5 files)

**Execution Model:** Sonnet

**Prerequisite:** Read `src/claudeutils/worktree/git_ops.py:9-23` (current `_git()` implementation) and `src/claudeutils/worktree/git_ops.py:78-112` (current `_is_parent_dirty()` at lines 78-97 and `_is_submodule_dirty()` at lines 100-112 — submodule check hardcodes `"agent-core"`)

**Implementation:**

Create `src/claudeutils/git.py` containing:

1. **`_git(*args, check=True, env=None, input_data=None) -> str`** — moved verbatim from `worktree/git_ops.py:9-23`

2. **`_git_ok(*args) -> bool`** — uses `subprocess.run(["git", *args], check=False, capture_output=True)` and returns `True` if returncode == 0. Must use `subprocess.run` directly (not `_git()`) because `_git()` returns stdout string, not returncode.

3. **`_fail(msg: str, code: int = 1) -> Never`** — `click.echo(msg)` (stdout, not stderr — S-3 convention) then `raise SystemExit(code)`. Return type `Never` informs type checkers.

4. **`discover_submodules() -> list[str]`** — parse `git submodule status` output. Each line starts with space/+/- then commit hash then space then path. Extract path field. Return empty list if no submodules.

5. **`_is_submodule_dirty(path: str) -> bool`** — generalized from `_is_submodule_dirty()`. Accepts submodule path instead of hardcoded `"agent-core"`. Checks `Path(path).exists()` before querying.

6. **`_is_dirty(exclude_path: str | None = None) -> bool`** — moved from `worktree/git_ops.py:78-97` (`_is_parent_dirty`). Renamed to `_is_dirty` in the new module (no callers outside git_ops.py so no import update needed).

**Import updates** (verify scope with `grep -r "from claudeutils.worktree.git_ops import" src/`):
- `worktree/git_ops.py`: Remove `_git`, `_is_submodule_dirty`, `_is_parent_dirty` definitions. Import from `claudeutils.git` instead. Keep worktree-specific functions (`wt_path`, `_classify_branch`, etc.)
- `worktree/cli.py`: Update `from claudeutils.worktree.git_ops import _git, _is_submodule_dirty` → `from claudeutils.git import _git, _is_submodule_dirty`
- `worktree/merge.py`: Same import update pattern
- `worktree/merge_state.py`: Same import update pattern
- `worktree/resolve.py`: Same import update pattern
- `worktree/remerge.py`: Update `from claudeutils.worktree.git_ops import _git` → `from claudeutils.git import _git`

**Tests:** `tests/test_git_helpers.py`
- `test_git_ok_success`: `_git_ok("status")` returns True in a valid git repo
- `test_git_ok_failure`: `_git_ok("log", "--invalidflag")` returns False
- `test_fail_exits`: `_fail("error msg", code=2)` raises SystemExit(2), output contains "error msg"
- `test_discover_submodules_none`: In repo without submodules, returns `[]`
- `test_discover_submodules_present`: In repo with submodule, returns `["submod-name"]`
- `test_is_submodule_dirty_parametrized`: Tests with clean/dirty submodule, nonexistent path

**Expected Outcome:** `just precommit` passes. All existing tests pass (no broken imports). New tests pass.

**Error Conditions:**
- Import site missed → existing tests fail (caught by precommit)
- Function signature change → grep for all call sites before modifying

**Validation:** `just precommit` (runs full test suite + lint)

---

## Step 1.2: Create `claudeutils/session/` package structure

**Objective:** Create package skeleton for all three subcommands. Register `_session` group in main CLI.

**Script Evaluation:** Small (~30 lines, mostly `__init__.py` stubs)

**Execution Model:** Sonnet

**Prerequisite:** Read `src/claudeutils/cli.py:145-152` — understand existing `cli.add_command(worktree)` registration pattern to replicate for `_session` group.

**Implementation:**

Create directory structure:
```
src/claudeutils/session/
  __init__.py           (empty)
  cli.py                Click group: `_session`
  handoff/
    __init__.py          (empty)
  commit/
    __init__.py          (empty)
  status/
    __init__.py          (empty)
```

`session/cli.py`:
- Define `@click.group(name="_session", hidden=True)` group
- Add help text: "Session management (internal)"

Main `cli.py` registration:
- `from claudeutils.session.cli import session_group`
- `cli.add_command(session_group)` — same pattern as line 152 (`cli.add_command(worktree)`)

**Expected Outcome:** `claudeutils _session --help` shows group with no subcommands. `claudeutils --help` does NOT show `_session` (hidden).

**Error Conditions:**
- Missing `__init__.py` → import failures

**Validation:** `claudeutils _session --help` succeeds; `just precommit` passes.

---

## Step 1.3: Add `claudeutils _git status` and `claudeutils _git diff` subcommands

**Objective:** Unified parent + submodule git status/diff view as structured markdown. Consumers: commit skill, commit CLI validation, handoff diagnostics.

**Script Evaluation:** Medium (~80 lines new code + tests)

**Execution Model:** Sonnet

**Prerequisite:** Read `src/claudeutils/git.py` (Step 1.1 output) — uses `_git()` and `discover_submodules()`

**Implementation:**

Create `src/claudeutils/git_cli.py` (CLI commands for the `_git` group):
- `@click.group(name="_git", hidden=True)` group
- `@git_group.command(name="status")` — runs `git status --porcelain` for parent, then for each discovered submodule. Output format:

```markdown
## Parent
<git status --porcelain output or "(clean)">

## Submodule: agent-core
<git -C agent-core status --porcelain output or "(clean)">
```

- `@git_group.command(name="diff")` — same pattern with `git diff` (staged + unstaged). Output format:

```markdown
## Parent
<git diff output or "(no changes)">

## Submodule: agent-core
<git -C agent-core diff output or "(no changes)">
```

Register in main `cli.py`: `from claudeutils.git_cli import git_group` + `cli.add_command(git_group)`

**Tests:** `tests/test_git_cli.py`
- Tests use `tmp_path` to create real git repos with submodules
- `test_git_status_clean_repo`: CliRunner invokes `_git status`, output contains `## Parent` and `(clean)`
- `test_git_status_dirty_repo`: Create dirty file, output contains filename in parent section
- `test_git_status_with_submodule`: Create repo with submodule, output contains `## Submodule:` section
- `test_git_diff_with_changes`: Stage a change, verify diff output appears under correct section

**Expected Outcome:** `claudeutils _git status` and `claudeutils _git diff` produce structured markdown output. Exit 0 always (status is informational).

**Error Conditions:**
- Not in a git repo → `_git()` raises CalledProcessError. Let it propagate (informational command).

**Validation:** `just precommit` — all tests pass.

---

**Phase 1 Checkpoint:** `just precommit` — all existing tests pass, new infrastructure tests pass.

### Phase 2: Session.md parser (type: tdd, model: sonnet)

Shared parser for session.md consumed by both status and handoff subcommands. Extends existing `worktree/session.py` parsing.

---

## Cycle 2.1: Parse all session.md sections with parametrized tests

**RED Phase:**

**Test:** `test_parse_session_sections[status_line]`, `test_parse_session_sections[completed]`, `test_parse_session_sections[in_tree_tasks]`, `test_parse_session_sections[worktree_tasks]`
**File:** `tests/test_session_parser.py`

**Assertions:**
- `parse_status_line(content)` returns the text between `# Session Handoff:` date line and first `## ` heading, stripped
- `parse_completed_section(content)` returns list of lines under `## Completed This Session` heading (up to next `## `)
- `parse_tasks(content, section="In-tree Tasks")` returns list of `ParsedTask` objects with `model`, `command`, `restart`, `worktree_marker` fields populated. Task with `→ slug` has `worktree_marker="slug"`. Task with `→ wt` has `worktree_marker="wt"`
- `parse_tasks(content, section="Worktree Tasks")` returns same structure for worktree section
- Each task has `plan_dir` attribute populated from continuation lines (`Plan:` or `plans/<name>/` in command)

**Edge case tests:**
- `test_parse_status_line_missing` — content without `# Session Handoff:` returns None
- `test_parse_tasks_old_format` — task line without pipe-separated metadata returns ParsedTask with `model=None`, `restart=False`
- `test_parse_tasks_empty_section` — section heading present but no tasks returns `[]`
- `test_parse_completed_section_empty` — heading present, no content returns `[]`

**Fixture:** `SESSION_MD_FIXTURE` — realistic session.md with:
```markdown
# Session Handoff: 2026-03-07

**Status:** Phase 1 complete — infrastructure ready.

## Completed This Session

**Phase 1 infrastructure:**
- Extracted git helpers
- Created package structure

## In-tree Tasks

- [ ] **Build parser** — `/runbook plans/parser/design.md` | sonnet
  - Plan: parser | Status: outlined
- [ ] **Fix bug** — `just fix-bug` | haiku
- [x] **Done task** — `/commit` | sonnet

## Worktree Tasks

- [ ] **Parallel work** → `my-slug` — `/design plans/parallel/problem.md` | opus | restart
- [ ] **Future work** → `wt` — `/design plans/future/problem.md` | sonnet
```

**Expected failure:** `ImportError` or `AttributeError` — functions don't exist yet

**Why it fails:** No `session/parse.py` module with these functions

**Verify RED:** `pytest tests/test_session_parser.py -v`

---

**GREEN Phase:**

**Implementation:** Create `src/claudeutils/session/parse.py` with section parsing functions

**Behavior:**
- `parse_status_line(content: str) -> str | None` — find `# Session Handoff:` line, return text between it and first `## ` heading. Uses existing `find_section_bounds()` pattern from `worktree/session.py`
- `parse_completed_section(content: str) -> list[str]` — extract lines under `## Completed This Session` heading up to next `## ` or EOF
- `parse_tasks(content: str, section: str = "In-tree Tasks") -> list[ParsedTask]` — reuse `extract_task_blocks(content, section=section)` from `worktree/session.py` to get TaskBlocks, then call `parse_task_line()` from `validation/task_parsing.py` for each block's first line. Extend `ParsedTask` with `plan_dir` by calling existing `_extract_plan_from_block()` from `worktree/session.py`
- Section name parameter makes in-tree and worktree parsing identical — single function, different section argument

**Approach:** Compose existing functions rather than rewriting. Import `find_section_bounds`, `extract_task_blocks`, `_extract_plan_from_block` from `worktree/session.py` and `parse_task_line` from `validation/task_parsing.py`.

**Changes:**
- File: `src/claudeutils/session/parse.py`
  Action: Create with `parse_status_line`, `parse_completed_section`, `parse_tasks`
  Location hint: New file

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_session_parser.py -v`
**Verify no regression:** `just precommit`

---

## Cycle 2.2: Full session.md parse — SessionData dataclass

**RED Phase:**

**Test:** `test_parse_session`, `test_parse_session_missing_file`, `test_parse_session_old_format`
**File:** `tests/test_session_parser.py`

**Assertions:**
- `parse_session(path)` returns `SessionData` with fields: `status_line: str | None`, `completed: list[str]`, `in_tree_tasks: list[ParsedTask]`, `worktree_tasks: list[ParsedTask]`, `date: str | None`
- All fields populated from the fixture session.md file
- `data.in_tree_tasks[0].name == "Build parser"` and `data.in_tree_tasks[0].plan_dir == "parser"`
- `data.worktree_tasks[0].worktree_marker == "my-slug"`
- `data.date` extracted from `# Session Handoff: 2026-03-07` → `"2026-03-07"`

**Error handling tests:**
- `test_parse_session_missing_file` — `parse_session(Path("nonexistent.md"))` raises `SessionFileError` (custom exception, not generic FileNotFoundError) — ST-2 fatal error
- `test_parse_session_old_format` — session.md with tasks lacking pipe-separated metadata → `ParsedTask` objects with `model=None`, `restart=False` (defaults, not error)

**Expected failure:** `ImportError` — `SessionData` class doesn't exist

**Why it fails:** No `SessionData` dataclass or `parse_session()` function

**Verify RED:** `pytest tests/test_session_parser.py::test_parse_session -v`

---

**GREEN Phase:**

**Implementation:** Add `SessionData` dataclass and `parse_session()` to `session/parse.py`

**Behavior:**
- `SessionData` dataclass with typed fields for all sections
- `parse_session(path: Path) -> SessionData` — reads file, calls section parsers from Cycle 2.1, assembles into `SessionData`
- Missing file → raise `SessionFileError` (defined in `session/parse.py` or `claudeutils/exceptions.py`)
- Date extraction: parse from `# Session Handoff: YYYY-MM-DD` header line via regex

**Approach:** Thin orchestration function composing the section parsers.

**Changes:**
- File: `src/claudeutils/session/parse.py`
  Action: Add `SessionData` dataclass and `parse_session()` function
  Location hint: After section parser functions
- File: `src/claudeutils/exceptions.py` (if appropriate)
  Action: Add `SessionFileError(ClaudeUtilsError)` if exceptions are centralized there

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_session_parser.py -v`
**Verify no regression:** `just precommit`

---

**Phase 2 Checkpoint:** All parser tests pass, `just precommit` clean.

### Phase 3: Status subcommand (type: tdd, model: sonnet)

Pure data transformation: session.md + filesystem state → STATUS output. No mutations, no stdin.

---

## Cycle 3.1: Render Next task

**RED Phase:**

**Test:** `test_render_next_task`, `test_render_next_skips_worktree_markers`, `test_render_next_no_pending`
**File:** `tests/test_session_status.py`

**Assertions:**
- `render_next(tasks)` where first task is pending (checkbox `" "`) with no `→` marker returns:
  ```
  Next: Build parser
    `/runbook plans/parser/design.md`
    Model: sonnet | Restart: no
  ```
- `render_next(tasks)` where first task has `worktree_marker="my-slug"` and second has `worktree_marker="wt"` and third is plain pending → returns third task's info
- `render_next([])` returns `""` (empty string, no Next section)
- Tasks with checkbox `"x"`, `"!"`, `"†"`, `"-"` are all skipped (only `" "` without marker is eligible)

**Expected failure:** `ImportError` — `render_next` doesn't exist

**Why it fails:** No `session/status/render.py` module

**Verify RED:** `pytest tests/test_session_status.py::test_render_next_task -v`

---

**GREEN Phase:**

**Implementation:** Create `src/claudeutils/session/status/render.py` with `render_next()`

**Behavior:**
- Iterate tasks, find first with `checkbox == " "` and `worktree_marker is None`
- Format as `Next:` block with command, model, restart
- Model defaults to "sonnet" if None. Restart shows "yes" if True, "no" if False

**Changes:**
- File: `src/claudeutils/session/status/render.py`
  Action: Create with `render_next(tasks: list[ParsedTask]) -> str`

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_session_status.py -v`
**Verify no regression:** `just precommit`

---

## Cycle 3.2: Render list sections with parametrized tests

**RED Phase:**

**Test:** `test_render_section[pending]`, `test_render_section[worktree]`, `test_render_section[unscheduled]`, `test_render_empty_section[pending]`, `test_render_empty_section[worktree]`, `test_render_empty_section[unscheduled]`
**File:** `tests/test_session_status.py`

**Assertions — Pending section:**
- `render_pending(tasks, plan_states)` with two tasks returns:
  ```
  Pending:
  - Build parser (sonnet)
    - Plan: parser | Status: outlined
  - Fix bug (haiku)
  ```
- Task with non-default model shows `(model)`. Default (sonnet) omitted
- Task with associated plan directory shows nested plan/status line
- Completed tasks (`checkbox == "x"`) excluded

**Assertions — Worktree section:**
- `render_worktree(tasks)` with branched task returns:
  ```
  Worktree:
  - Parallel work → my-slug
  - Future work → wt
  ```
- `→ slug` for branched tasks, `→ wt` for destined-but-not-yet-branched

**Assertions — Unscheduled Plans section:**
- `render_unscheduled(all_plans, task_plan_dirs)` with plans not associated to any task returns:
  ```
  Unscheduled Plans:
  - orphan-plan — designed
  ```
- Plans with status `delivered` excluded
- Sorted alphabetically
- Plans associated to any pending task excluded

**Empty section assertions (all three):**
- Each render function returns `""` when input list is empty

**Expected failure:** `ImportError` — render functions don't exist

**Why it fails:** No rendering functions for these sections

**Verify RED:** `pytest tests/test_session_status.py -k "render_section or render_empty" -v`

---

**GREEN Phase:**

**Implementation:** Add `render_pending()`, `render_worktree()`, `render_unscheduled()` to `session/status/render.py`

**Behavior:**
- `render_pending(tasks, plan_states)`: Filter to pending tasks (checkbox `" "`), format with optional plan status. Non-default model shown in parens. Plan status from `plan_states` dict mapping plan name → status string
- `render_worktree(tasks)`: Format worktree tasks with `→` markers
- `render_unscheduled(all_plans, task_plan_dirs)`: Filter plans not in `task_plan_dirs` set, exclude `delivered`, sort alphabetically, format with `—` separator

**Approach:** Each function produces a section string or empty string. Caller concatenates non-empty sections.

**Changes:**
- File: `src/claudeutils/session/status/render.py`
  Action: Add three rendering functions

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_session_status.py -v`
**Verify no regression:** `just precommit`

---

## Cycle 3.3: Parallel group detection

**RED Phase:**

**Test:** `test_detect_parallel_group`, `test_detect_parallel_no_group`, `test_detect_parallel_shared_plan`
**File:** `tests/test_session_status.py`

**Assertions:**
- `detect_parallel(tasks, blockers)` with 3 tasks having different `plan_dir` values and no blockers returns group of all 3 task names
- `detect_parallel(tasks, blockers)` with single task returns `None` (no group)
- `detect_parallel(tasks, blockers)` with 2 tasks sharing `plan_dir="parser"` returns `None` (shared plan = dependent)
- `detect_parallel(tasks, blockers)` with 4 tasks where 2 share a plan returns group of 2 independent tasks (largest independent subset)
- Blocker text mentioning task name creates dependency (excluded from group)

**Expected failure:** `ImportError` — `detect_parallel` doesn't exist

**Why it fails:** No parallel detection function

**Verify RED:** `pytest tests/test_session_status.py::test_detect_parallel_group -v`

---

**GREEN Phase:**

**Implementation:** Add `detect_parallel()` to `session/status/render.py`

**Behavior:**
- `detect_parallel(tasks: list[ParsedTask], blockers: list[list[str]]) -> list[str] | None`
- Build dependency graph: tasks with shared `plan_dir` are dependent. Tasks mentioned in blocker text are dependent on the blocker
- Find largest independent set (no shared plan_dir, no blocker references between them)
- Return task names if group has 2+ members, else None

**Approach:** Simple graph algorithm — build dependency edges (shared plan_dir, blocker reference), then find the largest independent set (no edges between members). For small task lists (<20), brute-force over subsets is fine: enumerate all subsets of pending tasks in descending size order, return first subset with no dependency edges between any pair.

**Changes:**
- File: `src/claudeutils/session/status/render.py`
  Action: Add `detect_parallel()` function

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_session_status.py -v`
**Verify no regression:** `just precommit`

---

## Cycle 3.4: CLI wiring — `claudeutils _session status`

**RED Phase:**

**Test:** `test_session_status_cli`, `test_session_status_missing_session`
**File:** `tests/test_session_status.py`

**Assertions:**
- CliRunner invoking `_session status` with a real session.md file in cwd produces output containing:
  - `Next:` section with first pending task
  - `Pending:` section
  - Output exits with code 0
- CliRunner invoking `_session status` without session.md file → exit code 2, output contains `**Error:**`

**Expected failure:** Command `_session status` not registered — Click returns non-zero with "No such command"

**Why it fails:** No status subcommand registered in session CLI group

**Verify RED:** `pytest tests/test_session_status.py::test_session_status_cli -v`

---

**GREEN Phase:**

**Implementation:** Create `src/claudeutils/session/status/cli.py` with Click command, register in session group

**Behavior:**
- `@click.command(name="status")` function
- Read `agents/session.md` (cwd-relative) → `parse_session()`
- Call `claudeutils _worktree ls` via subprocess for plan states
- Parse `_worktree ls` output for plan status: lines matching `  Plan: {name} [{status}] → ...` — extract name and status into a dict `{name: status}` passed to `render_pending()`
- Call render functions (Next, Pending, Worktree, Unscheduled, Parallel)
- Concatenate non-empty sections with blank line separators
- Output to stdout, exit 0
- Missing session.md → `_fail("**Error:** Session file not found: agents/session.md", code=2)`

**Changes:**
- File: `src/claudeutils/session/status/cli.py`
  Action: Create with `status` Click command
- File: `src/claudeutils/session/cli.py`
  Action: Import and register: `from claudeutils.session.status.cli import status; session_group.add_command(status)`

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_session_status.py -v`
**Verify no regression:** `just precommit`

---

**Phase 3 Checkpoint:** `just precommit` — status subcommand fully functional.

### Phase 4: Handoff pipeline (type: tdd, model: sonnet)

Stdin parsing, session.md writes, committed detection, state caching, diagnostics.

---

## Cycle 4.1: Parse handoff stdin

**RED Phase:**

**Test:** `test_parse_handoff_input`, `test_parse_handoff_missing_status`, `test_parse_handoff_missing_completed`
**File:** `tests/test_session_handoff.py`

**Assertions:**
- `parse_handoff_input(text)` with valid input returns `HandoffInput` with:
  - `status_line == "Design Phase A complete — outline reviewed."`
  - `completed_lines` is list of strings under `## Completed This Session`
- `parse_handoff_input(text)` without `**Status:**` line raises `HandoffInputError` with message containing "Status"
- `parse_handoff_input(text)` without `## Completed This Session` heading raises `HandoffInputError` with message containing "Completed"

**Input fixture:**
```
**Status:** Design Phase A complete — outline reviewed.

## Completed This Session

**Handoff CLI tool design (Phase A):**
- Produced outline
- Review by outline-review-agent
```

**Expected failure:** `ImportError` — no `parse_handoff_input` function

**Why it fails:** No `session/handoff/` module with parsing

**Verify RED:** `pytest tests/test_session_handoff.py::test_parse_handoff_input -v`

---

**GREEN Phase:**

**Implementation:** Create `src/claudeutils/session/handoff/parse.py`

**Behavior:**
- `HandoffInput` dataclass: `status_line: str`, `completed_lines: list[str]`
- `parse_handoff_input(text: str) -> HandoffInput` — locate `**Status:**` line, extract text after marker. Locate `## Completed This Session` heading, extract all lines until next `## ` or EOF
- `HandoffInputError` exception for missing required markers

**Changes:**
- File: `src/claudeutils/session/handoff/parse.py`
  Action: Create with `HandoffInput`, `HandoffInputError`, `parse_handoff_input()`

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_session_handoff.py -v`
**Verify no regression:** `just precommit`

---

## Cycle 4.2: Status line overwrite in session.md

**RED Phase:**

**Test:** `test_overwrite_status_line`, `test_overwrite_status_line_multiline`
**File:** `tests/test_session_handoff.py`

**Assertions:**
- `overwrite_status(session_path, "New status text.")` modifies file: line after `# Session Handoff:` heading becomes `**Status:** New status text.`
- Subsequent call with different text overwrites again (not append)
- Other sections of session.md unchanged
- When status text has multiple lines, each line preserved between heading and first `##`

**Expected failure:** `AttributeError` — `overwrite_status` doesn't exist

**Why it fails:** No status overwrite function

**Verify RED:** `pytest tests/test_session_handoff.py::test_overwrite_status_line -v`

---

**GREEN Phase:**

**Implementation:** Add `overwrite_status()` to `src/claudeutils/session/handoff/pipeline.py`

**Behavior:**
- Read session.md, find line after `# Session Handoff:` and before first `## ` heading
- Replace that region with `**Status:** {new_text}\n`
- Preserve blank line between status and first `##`
- Write back to file

**Changes:**
- File: `src/claudeutils/session/handoff/pipeline.py`
  Action: Create with `overwrite_status(session_path: Path, status_text: str) -> None`

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_session_handoff.py -v`
**Verify no regression:** `just precommit`

---

## Cycle 4.3: Completed section write with committed detection (H-2)

**RED Phase:**

**Test:** `test_write_completed_overwrite`, `test_write_completed_append`, `test_write_completed_auto_strip`
**File:** `tests/test_session_handoff.py`

Tests use real git repos via `tmp_path` — committed detection requires `git diff HEAD`. Fixture must have a committed `agents/session.md` with an existing `## Completed This Session` section so that diff modes can be distinguished.

**Assertions — overwrite mode (no prior diff):**
- First handoff or prior content already committed → `write_completed(session_path, new_lines)` overwrites `## Completed This Session` section entirely with `new_lines`; section contains exactly `new_lines` and no prior content

**Assertions — append mode (old removed by agent):**
- Agent cleared old completed content from working tree, new additions provided → `write_completed()` writes only `new_lines` to section (prior committed lines NOT restored); resulting section contains exactly `new_lines`

**Assertions — auto-strip mode (old preserved with additions):**
- Prior committed content still present + new additions → `write_completed()` strips content that matches HEAD version, keeps only new additions

**Detection mechanism:**
- `git diff HEAD -- agents/session.md` extracts completed section from both sides
- If no diff in completed section region → overwrite
- If diff shows old lines removed → append
- If diff shows old lines preserved + new lines → auto-strip committed

**Expected failure:** Function doesn't exist

**Why it fails:** No committed detection logic

**Verify RED:** `pytest tests/test_session_handoff.py::test_write_completed_overwrite -v`

---

**GREEN Phase:**

**Implementation:** Add `write_completed()` to `session/handoff/pipeline.py`

**Behavior:**
- Compare completed section in working tree vs HEAD via `git diff HEAD -- agents/session.md`
- Parse diff to determine which mode applies
- Execute appropriate write (overwrite, append, or strip-committed-then-keep-new)

**Approach:** Use `_git("diff", "HEAD", "--", str(session_path))` to get diff. Parse for completed section hunk. Absence of hunk → overwrite mode. Hunk with only additions → append mode. Hunk with preserved old + new → auto-strip mode.

**Changes:**
- File: `src/claudeutils/session/handoff/pipeline.py`
  Action: Add `write_completed(session_path: Path, new_lines: list[str]) -> None`

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_session_handoff.py -v`
**Verify no regression:** `just precommit`

---

## Cycle 4.4: State caching (H-4)

**RED Phase:**

**Test:** `test_state_cache_create`, `test_state_cache_resume`, `test_state_cache_cleanup`
**File:** `tests/test_session_handoff.py`

**Assertions:**
- `save_state(input_md, step="write_session")` creates `tmp/.handoff-state.json` with `input_markdown`, `timestamp` (ISO format), `step_reached` fields
- `load_state()` returns `HandoffState` with same fields, or `None` if no state file
- `clear_state()` removes the state file
- `step_reached` values: `"write_session"`, `"precommit"`, `"diagnostics"`
- State file survives across function calls (not deleted on load)

**Expected failure:** `ImportError` — state caching functions don't exist

**Why it fails:** No state management module

**Verify RED:** `pytest tests/test_session_handoff.py::test_state_cache_create -v`

---

**GREEN Phase:**

**Implementation:** Add state caching to `src/claudeutils/session/handoff/pipeline.py`

**Behavior:**
- `HandoffState` dataclass: `input_markdown: str`, `timestamp: str`, `step_reached: str`
- `save_state(input_md: str, step: str) -> None` — write JSON to `tmp/.handoff-state.json`. Create `tmp/` if needed
- `load_state() -> HandoffState | None` — read and parse JSON, return None if file missing
- `clear_state() -> None` — delete state file if exists

**Changes:**
- File: `src/claudeutils/session/handoff/pipeline.py`
  Action: Add `HandoffState`, `save_state()`, `load_state()`, `clear_state()`

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_session_handoff.py -v`
**Verify no regression:** `just precommit`

---

**Mid-phase checkpoint:** `just precommit` — mutations + recovery established before external tool integration.

---

## Cycle 4.5: Precommit integration

**RED Phase:**

**Test:** `test_handoff_precommit_pass`, `test_handoff_precommit_fail`
**File:** `tests/test_session_handoff.py`

**Assertions:**
- `run_precommit()` calls `just precommit` subprocess, returns `PrecommitResult` with `success: bool`, `output: str`
- On failure: `success == False`, `output` contains the precommit failure text
- On success: `success == True`, `output` contains passing summary

**Expected failure:** `ImportError` — `run_precommit` doesn't exist

**Why it fails:** No precommit integration

**Verify RED:** `pytest tests/test_session_handoff.py::test_handoff_precommit_pass -v`

---

**GREEN Phase:**

**Implementation:** Add `run_precommit()` to `session/handoff/pipeline.py`

**Behavior:**
- `PrecommitResult` dataclass: `success: bool`, `output: str`
- `run_precommit() -> PrecommitResult` — `subprocess.run(["just", "precommit"], capture_output=True, text=True, check=False)`. Return success based on returncode.

**Changes:**
- File: `src/claudeutils/session/handoff/pipeline.py`
  Action: Add `PrecommitResult`, `run_precommit()`

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_session_handoff.py -v`
**Verify no regression:** `just precommit`

---

## Cycle 4.6: Diagnostic output (H-3)

**RED Phase:**

**Test:** `test_diagnostics_precommit_pass`, `test_diagnostics_precommit_fail`, `test_diagnostics_learnings_age`
**File:** `tests/test_session_handoff.py`

**Assertions:**
- `format_diagnostics(precommit_result, git_status, learnings_age)` when precommit passed:
  - Contains precommit output
  - Contains git status/diff markdown
  - No learnings age warning if all entries < 7 days
- When precommit failed:
  - Contains precommit failure output
  - Does NOT contain git status/diff (conditional — only on pass)
  - Contains learnings age summary if any ≥ 7 days
- When learnings have entries ≥ 7 active days:
  - Output contains `**Learnings:** N entries ≥7 days — consider /codify`

**Expected failure:** `ImportError`

**Why it fails:** No diagnostics formatting function

**Verify RED:** `pytest tests/test_session_handoff.py::test_diagnostics_precommit_pass -v`

---

**GREEN Phase:**

**Implementation:** Add `format_diagnostics()` to `session/handoff/context.py`

**Behavior:**
- `format_diagnostics(precommit: PrecommitResult, git_output: str | None, learnings_age_days: int | None) -> str`
- Always include precommit result block
- If precommit passed: include git status/diff output
- If any learnings ≥ 7 days: append age summary line
- All output as structured markdown

**Changes:**
- File: `src/claudeutils/session/handoff/context.py`
  Action: Create with `format_diagnostics()`

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_session_handoff.py -v`
**Verify no regression:** `just precommit`

---

## Cycle 4.7: CLI wiring — `claudeutils _session handoff`

**RED Phase:**

**Test:** `test_session_handoff_cli_fresh`, `test_session_handoff_cli_resume`, `test_session_handoff_cli_no_stdin_no_state`
**File:** `tests/test_session_handoff.py`

**Assertions:**
- CliRunner with stdin input → exit 0, session.md status line updated, completed section written, diagnostics output
- CliRunner without stdin but with existing state file → exit 0, resumes from `step_reached`
- CliRunner without stdin and no state file → exit 2, output contains error message about missing input

**Expected failure:** Command not registered

**Why it fails:** No handoff subcommand

**Verify RED:** `pytest tests/test_session_handoff.py::test_session_handoff_cli_fresh -v`

---

**GREEN Phase:**

**Implementation:** Create `src/claudeutils/session/handoff/cli.py` with Click command, wire full pipeline

**Behavior:**
- `@click.command(name="handoff")` function
- Read stdin (if available) → `parse_handoff_input()`
- If no stdin: check for state file → `load_state()` → resume
- If no stdin and no state: `_fail("**Error:** No input on stdin and no state file", code=2)`
- Fresh pipeline: parse → save_state → overwrite_status → write_completed → run_precommit → diagnostics → clear_state
- Resume: load state → skip to `step_reached` → continue pipeline
- On precommit failure: output result + diagnostics, leave state file, exit 1

**Changes:**
- File: `src/claudeutils/session/handoff/cli.py`
  Action: Create with `handoff` Click command orchestrating full pipeline
- File: `src/claudeutils/session/cli.py`
  Action: Register: `from claudeutils.session.handoff.cli import handoff; session_group.add_command(handoff)`

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_session_handoff.py -v`
**Verify no regression:** `just precommit`

---

**Phase 4 Checkpoint:** `just precommit` — handoff subcommand fully functional.

### Phase 5: Commit parser + vet check (type: tdd, model: sonnet)

Markdown stdin parser (commit-specific format) and scripted vet check.

---

## Cycle 5.1: Parse commit markdown stdin — all sections with parametrized tests

**RED Phase:**

**Test:** `test_parse_commit_input[files]`, `test_parse_commit_input[options]`, `test_parse_commit_input[submodule]`, `test_parse_commit_input[message]`, `test_parse_commit_input_edge_cases`
**File:** `tests/test_session_commit.py`

**Input fixture:**
```markdown
## Files
- src/commit/cli.py
- src/commit/gate.py
- agent-core/fragments/vet-requirement.md

## Options
- no-vet
- amend

## Submodule agent-core
> 🤖 Update vet-requirement fragment
>
> - Add scripted gate classification reference

## Message
> ✨ Add commit CLI with scripted vet check
>
> - Structured markdown I/O
> - Submodule-aware commit pipeline
```

**Assertions — Files:**
- `result.files == ["src/commit/cli.py", "src/commit/gate.py", "agent-core/fragments/vet-requirement.md"]`

**Assertions — Options:**
- `result.options == {"no-vet", "amend"}`
- Input with unknown option `"foobar"` raises `CommitInputError` with message containing "Unknown option"
- Input without `## Options` → `result.options == set()`

**Assertions — Submodule:**
- `result.submodules` is dict mapping path → message: `{"agent-core": "🤖 Update vet-requirement fragment\n\n- Add scripted gate classification reference"}`
- Multiple `## Submodule <path>` sections each parsed independently
- Blockquote `> ` prefix stripped from message lines

**Assertions — Message:**
- `result.message == "✨ Add commit CLI with scripted vet check\n\n- Structured markdown I/O\n- Submodule-aware commit pipeline"`
- Blockquote `> ` prefix stripped
- `## ` lines within blockquote treated as message body (not section boundaries)
- Missing `## Message` → `CommitInputError`
- Missing `## Files` → `CommitInputError`

**Expected failure:** `ImportError` — no commit parser module

**Why it fails:** No `session/commit/parse.py`

**Verify RED:** `pytest tests/test_session_commit.py -k "parse_commit" -v`

---

**GREEN Phase:**

**Implementation:** Create `src/claudeutils/session/commit/parse.py`

**Behavior:**
- `CommitInput` dataclass: `files: list[str]`, `options: set[str]`, `submodules: dict[str, str]`, `message: str`
- `parse_commit_input(text: str) -> CommitInput` — section-based parsing
- Split on `## ` at line start. Known section names: `Files`, `Options`, `Submodule <path>`, `Message`
- `## Message` is always last — everything from `## Message` to EOF is message body
- Blockquote stripping: remove leading `> ` or `>` from each line
- Valid options: `no-vet`, `just-lint`, `amend`. Unknown → raise `CommitInputError`
- `CommitInputError` exception for missing required sections or unknown options

**Approach:** Sequential parsing — find each `## ` boundary, classify section, delegate to section-specific parser. Message section greedily consumes to EOF (safe for `## ` in blockquotes).

**Changes:**
- File: `src/claudeutils/session/commit/parse.py`
  Action: Create with `CommitInput`, `CommitInputError`, `parse_commit_input()`

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_session_commit.py -v`
**Verify no regression:** `just precommit`

---

## Cycle 5.2: Input validation — clean files check (C-3)

**RED Phase:**

**Test:** `test_validate_files_dirty`, `test_validate_files_clean_error`, `test_validate_files_amend`
**File:** `tests/test_session_commit.py`

Tests use real git repos via `tmp_path`.

**Assertions:**
- `validate_files(files, amend=False)` with all files appearing in `git status --porcelain` → returns normally (no error)
- `validate_files(files, amend=False)` with a clean file (not in `git status --porcelain`) → raises `CleanFileError` with:
  - `clean_files` attribute listing the clean file paths
  - String representation matching exact format: `**Error:** Listed files have no uncommitted changes\n- <path>\n\nSTOP: Do not remove files and retry.`
- `validate_files(files, amend=True)` with a file that's clean in working tree but present in HEAD commit (via `git diff-tree`) → returns normally (amend allows HEAD-committed files)
- `validate_files(files, amend=True)` with a file in neither working tree changes nor HEAD commit → raises `CleanFileError`

**Expected failure:** `ImportError`

**Why it fails:** No validation function

**Verify RED:** `pytest tests/test_session_commit.py::test_validate_files_dirty -v`

---

**GREEN Phase:**

**Implementation:** Add `validate_files()` to `src/claudeutils/session/commit/gate.py`

**Behavior:**
- `CleanFileError` exception with `clean_files: list[str]` attribute
- `validate_files(files: list[str], amend: bool = False) -> None`
- Get dirty files: `_git("status", "--porcelain")` → parse paths (column 3+)
- If amend: also get HEAD files: `_git("diff-tree", "--no-commit-id", "--name-only", "HEAD")`
- For each file in `files`: check presence in dirty set (or HEAD set if amend)
- Collect clean files → raise `CleanFileError` with STOP directive

**Changes:**
- File: `src/claudeutils/session/commit/gate.py`
  Action: Create with `CleanFileError`, `validate_files()`

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_session_commit.py -v`
**Verify no regression:** `just precommit`

---

## Cycle 5.3: Scripted vet check (C-1)

**RED Phase:**

**Test:** `test_vet_check_no_config`, `test_vet_check_pass`, `test_vet_check_unreviewed`, `test_vet_check_stale`
**File:** `tests/test_session_commit.py`

Tests use `tmp_path` with pyproject.toml and plan report directories.

**Assertions:**
- `vet_check(files)` with no `[tool.claudeutils.commit]` section in pyproject.toml → passes (opt-in, returns `VetResult(passed=True)`)
- `vet_check(files)` with `require-review = ["src/**/*.py"]` and file `src/foo.py` in files, with report `plans/bar/reports/vet-review.md` newer than `src/foo.py` → passes
- `vet_check(files)` with matching pattern but no report file → fails with `VetResult(passed=False, reason="unreviewed", unreviewed_files=["src/foo.py"])`
- `vet_check(files)` with report older than newest matching file → fails with `VetResult(passed=False, reason="stale", stale_info=...)`
- Files not matching any pattern are not checked (non-production files pass freely)

**Expected failure:** `ImportError`

**Why it fails:** No vet check function

**Verify RED:** `pytest tests/test_session_commit.py::test_vet_check_no_config -v`

---

**GREEN Phase:**

**Implementation:** Add vet check to `src/claudeutils/session/commit/gate.py`

**Behavior:**
- `VetResult` dataclass: `passed: bool`, `reason: str | None`, `unreviewed_files: list[str]`, `stale_info: str | None`
- `vet_check(files: list[str]) -> VetResult`
- Read `pyproject.toml` (cwd-relative), parse `[tool.claudeutils.commit].require-review` patterns
- No section or no patterns → return `VetResult(passed=True)`
- Match files against patterns using `fnmatch` or `pathlib.PurePath.match`
- For matched files: discover reports in `plans/*/reports/` matching `*vet*` or `*review*` (excluding `tmp/`)
- No reports → unreviewed. Reports exist → check freshness: `mtime` of newest production file vs newest report
- Stale (production newer) → fail with stale info

**Changes:**
- File: `src/claudeutils/session/commit/gate.py`
  Action: Add `VetResult`, `vet_check()`

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_session_commit.py -v`
**Verify no regression:** `just precommit`

---

**Phase 5 Checkpoint:** `just precommit` — parser and vet check tests pass.

### Phase 6: Commit pipeline + output (type: tdd, model: sonnet)

Staging, submodule coordination, amend semantics, structured output.

---

## Cycle 6.1: Parent-only commit pipeline

**RED Phase:**

**Test:** `test_commit_parent_only`, `test_commit_precommit_failure`
**File:** `tests/test_session_commit_pipeline.py`

Tests use real git repos via `tmp_path`.

**Assertions:**
- `commit_pipeline(commit_input)` with files in parent repo only (no submodule files), precommit passing:
  - Stages listed files via `git add`
  - Runs `just precommit`
  - Commits with message from `CommitInput.message`
  - Returns `CommitResult(success=True, output="[branch hash] message\n N files changed...")` — raw git output
  - Exit code 0
- `commit_pipeline(commit_input)` with precommit failure:
  - Returns `CommitResult(success=False, output="**Precommit:** failed\n\n<error output>")`
  - Files staged but NOT committed
  - Exit code 1

**Expected failure:** `ImportError` — no commit pipeline

**Why it fails:** No `session/commit/pipeline.py`

**Verify RED:** `pytest tests/test_session_commit_pipeline.py::test_commit_parent_only -v`

---

**GREEN Phase:**

**Implementation:** Create `src/claudeutils/session/commit/pipeline.py`

**Behavior:**
- `CommitResult` dataclass: `success: bool`, `output: str`
- `commit_pipeline(input: CommitInput) -> CommitResult`
- Stage files via `git add`
- Run `just precommit` (validation level dispatch added in Cycle 6.4)
- Run vet check via `vet_check(input.files)` (option-gating added in Cycle 6.4)
- Commit with message from `CommitInput.message`
- Return raw git commit output on success

**Changes:**
- File: `src/claudeutils/session/commit/pipeline.py`
  Action: Create with `CommitResult`, `commit_pipeline()`

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_session_commit_pipeline.py -v`
**Verify no regression:** `just precommit`

---

## Cycle 6.2: Submodule coordination (C-2)

**RED Phase:**

**Test:** `test_commit_with_submodule`, `test_commit_submodule_no_message`, `test_commit_submodule_orphan_message`, `test_commit_no_submodule_changes`
**File:** `tests/test_session_commit_pipeline.py`

Tests use real git repos with submodules via `tmp_path` (shared fixture).

**Assertions — four-cell matrix from C-2:**

| Submodule files in Files | `## Submodule` present | Expected |
|---|---|---|
| Yes | Yes | Submodule committed first, pointer staged, parent committed. Output has `<path>:` prefix for submodule |
| Yes | No | `CommitResult(success=False)`, output contains `**Error:**` about missing submodule message. Exit 1 |
| No | Yes | `CommitResult(success=True)`, output contains `**Warning:**` about orphaned submodule message. Warning prepended to git output |
| No | No | Parent-only commit (same as 6.1) |

**Submodule commit sequence:**
- Files partitioned by submodule path prefix
- Per-submodule: `git -C <path> add <files>` → `git -C <path> commit -m <submodule_message>`
- Stage submodule pointer: `git add <path>`
- Parent commit includes pointer change

**Expected failure:** Pipeline doesn't handle submodule files

**Why it fails:** No submodule partitioning or coordination logic

**Verify RED:** `pytest tests/test_session_commit_pipeline.py::test_commit_with_submodule -v`

---

**GREEN Phase:**

**Implementation:** Add submodule coordination to `commit_pipeline()`

**Behavior:**
- Partition `input.files` by submodule path prefix (using `discover_submodules()`)
- For each submodule with files:
  - Check `input.submodules` has message for this path → error if missing
  - Stage submodule files: `_git("-C", path, "add", *submod_files)`
  - Commit submodule: `_git("-C", path, "commit", "-m", submod_message)`
  - Stage pointer: `_git("add", path)`
- For orphaned submodule messages (path in `input.submodules` but no files): emit warning
- Commit parent with remaining files + staged pointers
- Output: submodule output prefixed with `<path>:`, parent output unlabeled

**Changes:**
- File: `src/claudeutils/session/commit/pipeline.py`
  Action: Add submodule partitioning and coordination to `commit_pipeline()`

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_session_commit_pipeline.py -v`
**Verify no regression:** `just precommit`

---

## Cycle 6.3: Amend semantics (C-5)

**RED Phase:**

**Test:** `test_commit_amend_parent`, `test_commit_amend_submodule`, `test_commit_amend_validation`
**File:** `tests/test_session_commit_pipeline.py`

Tests use real git repos via `tmp_path`.

**Assertions:**
- `commit_pipeline(input)` with `amend` in options:
  - Passes `--amend` to `git commit`
  - Output shows amend format with `Date:` line
  - Message is the full provided message (no `--no-edit`)
- Amend with submodule files:
  - Submodule amended first → pointer re-staged → parent amended
  - Output labeled correctly
- Amend validation:
  - File present in HEAD commit but not in working tree changes → valid for amend (no error)
  - File in neither HEAD nor working tree → `CleanFileError` (same as non-amend)

**Expected failure:** Pipeline doesn't pass `--amend` flag

**Why it fails:** No amend support in pipeline

**Verify RED:** `pytest tests/test_session_commit_pipeline.py::test_commit_amend_parent -v`

---

**GREEN Phase:**

**Implementation:** Add amend support to `commit_pipeline()`

**Behavior:**
- If `amend` in `input.options`: add `--amend` to `git commit` args
- Pass `amend=True` to `validate_files()` — enables HEAD file acceptance
- Submodule amend: `_git("-C", path, "commit", "--amend", "-m", message)` then re-stage pointer
- Message always provided (never `--no-edit`)

**Changes:**
- File: `src/claudeutils/session/commit/pipeline.py`
  Action: Add amend flag handling throughout pipeline

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_session_commit_pipeline.py -v`
**Verify no regression:** `just precommit`

---

## Cycle 6.4: Validation levels (C-4)

**RED Phase:**

**Test:** `test_commit_just_lint`, `test_commit_no_vet`, `test_commit_combined_options`
**File:** `tests/test_session_commit_pipeline.py`

**Assertions:**
- `just-lint` option → pipeline runs `just lint` instead of `just precommit`
- `no-vet` option → vet check skipped entirely
- `just-lint` + `no-vet` → lint only, no vet
- `amend` + `no-vet` → full precommit, amend, no vet
- `amend` + `just-lint` → lint only, amend
- Options are orthogonal — any combination valid

**Expected failure:** Options not affecting validation behavior

**Why it fails:** No option dispatch for validation levels

**Verify RED:** `pytest tests/test_session_commit_pipeline.py::test_commit_just_lint -v`

---

**GREEN Phase:**

**Implementation:** Add option-based validation dispatch to `commit_pipeline()`

**Behavior:**
- Inspect `input.options` set before dispatching validation:
  - `just-lint` present → run `just lint` instead of `just precommit`
  - `no-vet` present → skip vet check entirely
  - Both absent → default: `just precommit` + vet check
  - Orthogonal: each option controls one aspect independently

**Changes:**
- File: `src/claudeutils/session/commit/pipeline.py`
  Action: Add option dispatch logic before validation calls

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_session_commit_pipeline.py -v`
**Verify no regression:** `just precommit`

---

## Cycle 6.5: Output formatting

**RED Phase:**

**Test:** `test_format_success_parent`, `test_format_success_submodule`, `test_format_warning`, `test_format_failure`
**File:** `tests/test_session_commit_pipeline.py`

**Assertions:**
- `format_commit_output(result)` with parent-only success:
  ```
  [session-cli-tool a7f38c2] ✨ Add commit CLI
   3 files changed, 142 insertions(+), 8 deletions(-)
  ```
  Raw git output, no prefix
- With submodule success:
  ```
  agent-core:
  [session-cli-tool 4b2c1a0] 🤖 Update fragment
   1 file changed, 5 insertions(+), 2 deletions(-)
  [session-cli-tool a7f38c2] ✨ Add commit CLI
   4 files changed, 142 insertions(+), 8 deletions(-)
  ```
  Submodule output labeled with `<path>:`, parent unlabeled
- Warning + success:
  ```
  **Warning:** Submodule message provided but no changes found for: agent-core. Ignored.

  [session-cli-tool a7f38c2] ✨ Add commit CLI
  ```
  Warning prepended to git output
- Failure: gate-specific diagnostic (vet, precommit, clean-files) — format varies by gate

**Expected failure:** No dedicated formatting function

**Why it fails:** Output formatting inline in pipeline, not testable in isolation

**Verify RED:** `pytest tests/test_session_commit_pipeline.py::test_format_success_parent -v`

---

**GREEN Phase:**

**Implementation:** Extract output formatting to testable functions

**Behavior:**
- Extract output formatting to a dedicated function that accepts submodule outputs (keyed by path), parent output string, and any warning messages
- Submodule outputs labeled with `<path>:` prefix
- Parent output appended unlabeled
- Warnings prepended as `**Warning:**` lines with blank line separator
- For failures: separate formatting per gate type already produces structured markdown

**Changes:**
- File: `src/claudeutils/session/commit/pipeline.py`
  Action: Extract `format_commit_output()` from pipeline logic

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_session_commit_pipeline.py -v`
**Verify no regression:** `just precommit`

---

## Cycle 6.6: CLI wiring — `claudeutils _session commit`

**RED Phase:**

**Test:** `test_session_commit_cli_success`, `test_session_commit_cli_validation_error`
**File:** `tests/test_session_commit_pipeline.py`

**Assertions:**
- CliRunner with valid commit markdown on stdin (real git repo via `tmp_path`, file staged) → exit 0, stdout contains `[branch hash] message` format line
- CliRunner with files that have no changes → exit 2, stdout contains `**Error:**` and `STOP:`
- CliRunner with empty stdin → exit 2, stdout contains `**Error:**` and references missing required section

**Expected failure:** Command not registered

**Why it fails:** No commit subcommand

**Verify RED:** `pytest tests/test_session_commit_pipeline.py::test_session_commit_cli_success -v`

---

**GREEN Phase:**

**Implementation:** Create `src/claudeutils/session/commit/cli.py` with Click command

**Behavior:**
- `@click.command(name="commit")` function
- Read all stdin → `parse_commit_input()`
- Call `commit_pipeline(input)` → `CommitResult`
- Output `result.output` to stdout
- Exit 0 on success, 1 on pipeline error, 2 on input validation error

**Changes:**
- File: `src/claudeutils/session/commit/cli.py`
  Action: Create with `commit` Click command
- File: `src/claudeutils/session/cli.py`
  Action: Import and register the commit command with the session group (same pattern as worktree subcommand registration in main cli.py)

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_session_commit_pipeline.py -v`
**Verify no regression:** `just precommit`

---

**Phase 6 Checkpoint:** `just precommit` — commit subcommand fully functional.

### Phase 7: Integration tests (type: tdd, model: sonnet)

End-to-end tests with real git repos via `tmp_path`. Verifies complete pipelines through CLI entry points.

---

## Cycle 7.1: Status integration

**RED Phase:**

**Test:** `test_status_integration`
**File:** `tests/test_session_integration.py`

**Prerequisite:** Read `src/claudeutils/session/status/cli.py` — understand full pipeline from CLI entry

**Assertions:**
- Create `tmp_path` git repo with:
  - `agents/session.md` (realistic fixture with in-tree tasks, worktree tasks, reference files)
  - `plans/parser/` directory with design artifacts (triggers plan state inference)
  - At least one plan directory not referenced by any task (triggers unscheduled detection)
- CliRunner invokes `_session status`
- Output contains `Next:` section with correct task name and command
- Output contains `Pending:` section with plan status
- Output contains `Worktree:` section with slug markers
- Output contains `Unscheduled Plans:` section with orphan plan
- Exit code 0

**Expected failure:** Integration path not fully wired — individual components may work but full pipeline from CLI to output untested

**Why it fails:** End-to-end path through CliRunner exercises wiring gaps

**Verify RED:** `pytest tests/test_session_integration.py::test_status_integration -v`

---

**GREEN Phase:**

**Implementation:** Fix any wiring gaps discovered by integration test

**Behavior:**
- The test exercises: CLI command → parse_session() → render functions → formatted output
- Fixes are targeted at wiring issues (import paths, function signatures, data threading)
- No new production code expected — all components built in Phases 2-3

**Changes:**
- Fix any import or wiring issues discovered
- May require adjusting function signatures for data threading

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_session_integration.py::test_status_integration -v`
**Verify no regression:** `just precommit`

---

## Cycle 7.2: Handoff integration

**RED Phase:**

**Test:** `test_handoff_fresh_integration`, `test_handoff_resume_integration`
**File:** `tests/test_session_integration.py`

**Prerequisite:** Read `src/claudeutils/session/handoff/cli.py` — understand full pipeline

**Assertions — fresh mode:**
- Create `tmp_path` git repo with `agents/session.md` (committed initial state)
- CliRunner invokes `_session handoff` with stdin:
  ```
  **Status:** Phase 1 complete.

  ## Completed This Session

  **Infrastructure work:**
  - Extracted git helpers
  ```
- After invocation:
  - `agents/session.md` status line updated to "Phase 1 complete."
  - Completed section contains "Infrastructure work:" and "Extracted git helpers"
  - Output contains diagnostics (precommit result)
  - No state file remains (cleaned up on success)
  - Exit code 0

**Assertions — resume mode:**
- Create state file at `tmp/.handoff-state.json` with `step_reached: "precommit"`
- CliRunner invokes `_session handoff` without stdin
- Pipeline resumes from precommit step (skips write steps)
- Exit code 0

**Expected failure:** End-to-end pipeline wiring gaps

**Why it fails:** Fresh/resume modes exercise different pipeline paths

**Verify RED:** `pytest tests/test_session_integration.py::test_handoff_fresh_integration -v`

---

**GREEN Phase:**

**Implementation:** Fix wiring issues discovered by integration test

**Behavior:**
- Fresh mode exercises: stdin → parse → state cache → status overwrite → completed write → precommit → diagnostics → cleanup
- Resume mode exercises: state load → skip to step → precommit → diagnostics → cleanup
- Fixes targeted at data threading and error propagation

**Changes:**
- Fix any discovered wiring issues

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_session_integration.py -v`
**Verify no regression:** `just precommit`

---

## Cycle 7.3: Commit integration

**RED Phase:**

**Test:** `test_commit_parent_integration`, `test_commit_submodule_integration`, `test_commit_amend_integration`
**File:** `tests/test_session_integration.py`

**Prerequisite:** Shared `tmp_path` fixture creating git repo with submodule (from conftest)

**Assertions — parent-only:**
- Create modified file in `tmp_path` repo (uncommitted change, appears in `git status --porcelain`)
- CliRunner invokes `_session commit` with stdin specifying the file + message
- Git log shows new commit with expected message
- Output contains `[branch hash] message` format
- Exit code 0

**Assertions — submodule:**
- Create dirty file in submodule directory
- CliRunner with stdin specifying submodule file, submodule message, and parent message
- Submodule git log shows new commit
- Parent git log shows new commit (with submodule pointer update)
- Output contains `<path>:` labeled submodule output followed by parent output
- Exit code 0

**Assertions — amend:**
- Create initial commit, then create new dirty file
- CliRunner with `amend` option → amend the previous commit
- Git log shows only one commit (amended, not new)
- Output contains `Date:` line (amend output format)
- Exit code 0

**Expected failure:** End-to-end commit pipeline wiring

**Why it fails:** Full pipeline through real git operations

**Verify RED:** `pytest tests/test_session_integration.py::test_commit_parent_integration -v`

---

**GREEN Phase:**

**Implementation:** Fix wiring issues in commit pipeline

**Behavior:**
- Parent-only: stdin → parse → validate → precommit → stage → commit → output
- Submodule: partition → submodule commit → pointer stage → parent commit
- Amend: same pipeline with `--amend` flag propagation

**Changes:**
- Fix any discovered wiring issues

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_session_integration.py -v`
**Verify no regression:** `just precommit`

---

## Cycle 7.4: Cross-subcommand — handoff then status

**RED Phase:**

**Test:** `test_handoff_then_status`
**File:** `tests/test_session_integration.py`

**Assertions:**
- Create `tmp_path` git repo with `agents/session.md`
- CliRunner invokes `_session handoff` with stdin (updates session.md)
- Then CliRunner invokes `_session status` (reads updated session.md)
- Status output reflects the new status line from handoff input
- Status output reflects the updated completed section
- Verifies parser consistency: handoff writes → status reads the same format

**Expected failure:** Parser asymmetry between write and read paths

**Why it fails:** Integration verifies round-trip consistency

**Verify RED:** `pytest tests/test_session_integration.py::test_handoff_then_status -v`

---

**GREEN Phase:**

**Implementation:** Fix any format asymmetries between handoff writes and status reads

**Behavior:**
- Handoff writes status line and completed section in format that status parser expects
- Any format divergence between write and read is a bug

**Changes:**
- Fix any discovered format mismatches

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_session_integration.py -v`
**Verify no regression:** `just precommit`

---

**Phase 7 Checkpoint (full):** `just precommit` — all tests pass, full suite green. Final checkpoint covers all 7 phases.
