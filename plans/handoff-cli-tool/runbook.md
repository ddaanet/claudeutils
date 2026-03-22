# Runbook: Fix handoff-cli round 2 (Tier 2)

**Input:** `plans/handoff-cli-tool/reports/deliverable-review.md` (round 2)
**Scope:** C#1, M#2, M#3, M#5, m-1 through m-6 (10 findings)
**Discipline:** Integration-first TDD — tests are executable specifications of contracts

## Recall Entries (for delegation)

- `when adding error handling to call chain` — context at failure site, display at top level
- `when cli error messages are llm-consumed` — facts only, STOP directive for data-loss
- `when testing CLI tools` — Click CliRunner, in-process
- `when preferring e2e over mocked subprocess` — real git repos via tmp_path, mock only for error injection
- `when writing red phase assertions` — verify behavior not structure

## Phase 1: Commit pipeline fixes (type: tdd)

C#1 (`_commit_submodule` returncode) + M#3 (`_error()` formatting). Same subsystem, same test file.

### Cycle 1.1: Submodule commit failure propagates error

**Contract:** When a submodule's `git commit` fails (hook rejection, nothing staged), `commit_pipeline` returns `success=False` with a structured error message — not silent success.

**RED:** Write integration test in `tests/test_commit_pipeline_errors.py`:
- Set up real git repo with submodule structure (reuse existing pattern from `test_pipeline_validates_before_submodule_commit`)
- Mock `_commit_submodule` to raise `CalledProcessError` with stderr containing a reason
- Call `commit_pipeline` → assert `result.success is False`
- Assert `result.output` contains `**Error:**` (structured markdown)
- Assert `result.output` does NOT contain `CalledProcessError` or `Command '['git'` (no raw repr)

Currently: `_commit_submodule` uses `check=False` (line 139), returns `result.stdout.strip()` without checking returncode (line 148). The pipeline's `try/except CalledProcessError` at lines 296-306 catches this because `_commit_submodule`'s `git add` uses `check=True` (line 122) — but NOT the git commit itself. If only the commit fails (not git add), no exception raised, silent "success."

**GREEN:** Change `_commit_submodule` git commit call: `check=False` → `check=True` (line 134-139). `CalledProcessError` propagates to the pipeline's existing `try/except` at line 296-306 which calls `_error(f"submodule {path} failed", e)`.

**Verify:** `pytest tests/test_commit_pipeline_errors.py -x`

### Cycle 1.2: Error messages are structured, not raw repr

**Contract:** `_error()` produces structured markdown output — never raw Python exception repr.

**RED:** Write test in `tests/test_commit_pipeline_errors.py`:
- Create `CalledProcessError` with empty stderr (the problematic path)
- Call `_error("staging failed", exc)` directly
- Assert output contains `**Error:** staging failed`
- Assert output does NOT contain `Command '['git'` (raw repr pattern)
- Also test with populated stderr: assert stderr content appears in output

Currently: `_error()` at line 219 uses `exc.stderr or exc` — when stderr is empty string, `str(exc)` produces `Command '['git', 'commit', ...]' returned non-zero exit status 1`.

**GREEN:** Change `_error()` fallback from `str(exc)` to meaningful info:
- If `exc.stderr` non-empty: use it (current, good)
- If `exc.stderr` empty: `f"exit code {exc.returncode}"`
- Never `str(exc)` which produces Python repr

**Verify:** `pytest tests/test_commit_pipeline_errors.py -x`

## Phase 2: Worktree aggregation fix (type: tdd)

M#5: `aggregate_trees` deduplicates plans by name; main always wins.

### Cycle 2.1: Plans shown per-tree, not deduplicated to main

**Contract:** When a plan exists in multiple worktrees with different lifecycle states, each tree shows its own plan state. Main does not overwrite worktree-specific state.

**RED:** Write test for `aggregate_trees`:
- Mock git worktree list to return two trees (main + worktree)
- Create plan directories in both with different lifecycle.md states (e.g., main=`ready`, worktree=`rework`)
- Call `aggregate_trees` → assert both plan states appear, each with correct `tree_path`
- Assert plan count equals 2 (not deduplicated to 1)

Currently: `aggregate_trees` (aggregation.py:202-219) uses `plans_dict[plan.name]` — main loop runs second and unconditionally overwrites worktree entry.

**GREEN:** Remove dedup. Collect all plans across all trees into a flat list (each `PlanState` already has `tree_path` set). `format_rich_ls` already groups by `plan.tree_path == tree.path` (display.py:28) — display layer unaffected.

Change `plans_dict: dict[str, PlanState]` to `all_plans: list[PlanState]`. Single loop over trees, append all plans. Sorting by session.md order still works (sort key uses `plan.name`).

**Verify:** `pytest tests/ -k "aggregate" -x` and `pytest tests/test_session_status.py -x`

## Phase 3: Status CLI fixes (type: tdd)

m-2 (▶ skip worktree tasks), m-5 (old section name bypass).

### Cycle 3.1: Old section name detected and rejected

**Contract:** Session.md using `## Pending Tasks` (old name) causes `_status` to exit 2 with informative error — not silent "No in-tree tasks."

**RED:** Write test in `tests/test_status_rework.py`:
- Create session.md with `## Pending Tasks` containing valid task lines
- Invoke `_status` via CliRunner
- Assert `exit_code == 2`
- Assert output references the old section name

Currently: `_count_raw_tasks("In-tree Tasks")` returns 0, `parse_session` returns 0 in-tree tasks, `0 != 0` is False → passes silently.

**GREEN:** In `status/cli.py`, before the count comparison, check for `## Pending Tasks` in content. If found: `_fail("**Error:** Old section name 'Pending Tasks' — rename to 'In-tree Tasks'", code=2)`.

**Verify:** `pytest tests/test_status_rework.py -x`

### Cycle 3.2: ▶ skips worktree-marked tasks

**Contract:** `render_pending` assigns ▶ to first pending task WITHOUT a worktree marker.

**RED:** Write test in `tests/test_status_rework.py`:
- Task list: first task has `worktree_marker="slug"`, second has `worktree_marker=None`
- Call `render_pending` → assert ▶ appears on second task name
- Assert first task rendered without ▶

Currently: `render_pending` line 67 checks `task.checkbox == " "` but not `task.worktree_marker`.

**GREEN:** Add `and task.worktree_marker is None` to the condition at line 67.

**Verify:** `pytest tests/test_status_rework.py -x`

## Phase 4: Git helper fix (type: tdd)

m-3: `_is_dirty()` uses `_git()` which strips leading space from porcelain format.

### Cycle 4.1: _is_dirty exclude_path works with unstaged modifications

**Contract:** `_is_dirty(exclude_path=X)` correctly excludes files under path X even when porcelain output has ` M` prefix (space-M, unstaged only).

**RED:** Write test:
- Create real git repo, add and commit `subdir/file.py`, then modify it (unstaged)
- `git status --porcelain` → ` M subdir/file.py` (leading space)
- Call `_is_dirty(exclude_path="subdir")` → assert returns `False` (file is excluded)
- Currently returns `True` because `_git()` strips leading space → `M subdir/file.py` → `line[3:]` = `bdir/file.py` → doesn't match exclude prefix `subdir/` → not excluded

**GREEN:** Change `_is_dirty` to use `subprocess.run` directly instead of `_git()`, preserving porcelain format's fixed-width XY+space prefix.

**Verify:** `pytest tests/ -k "is_dirty" -x`

## Phase 5: Cleanup (type: general)

Non-behavioral changes.

### Step 5.1: Delete dead `render_next`

- Delete function from `src/claudeutils/session/status/render.py` (lines 24-47)
- Remove any imports/references (grep `render_next`)
- Verify: `just lint`

### Step 5.2: Delete dead `step_reached`

- Remove `step_reached: str` from `HandoffState` in `src/claudeutils/session/handoff/pipeline.py:20`
- Update `save_state` to remove `step` parameter
- Grep for `step_reached` references and remove
- Verify: `just lint` and `just test`

### Step 5.3: Add `claudeutils:*` to handoff SKILL.md

- Edit `agent-core/skills/handoff/SKILL.md` line 4
- `Bash(just:*,wc:*,git:*)` → `Bash(just:*,wc:*,git:*,claudeutils:*)`

### Step 5.4: Fix weak test assertion

- `tests/test_status_rework.py:143`: split `or` → two `assert` statements

### Step 5.5: Final verification

- `just precommit`
