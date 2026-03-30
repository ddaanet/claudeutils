# Code Deliverable Review — Layer 1 (RC15)

**Date:** 2026-03-26
**Methodology:** Full-scope review of all code deliverables against outline.md
**Review type:** Full-scope per learnings (no delta-scoping). RC15 reviews the codebase state after RC14 fixes.
**Prior:** RC14 0C/0M/10m (7 active + 3 dismissed). RC14 fix cycle addressed all 7 active minors. Corrector review 0C/0M.

## RC14 Fix Verification

| Finding | Status | Evidence |
|---------|--------|---------|
| m-1 `_strip_hints` clarity | **FIXED** | `commit_pipeline.py:193-213` — redundant `prev_was_hint = True` removed. Named `is_continuation` boolean. Single conditional append. `prev_was_hint` only reset in `else` branch (non-hint, non-indented) — correct: indented-after-hint lines keep the hint context active until a non-indented line is seen. |
| m-2 `_git_output` consolidation | **FIXED** | `commit_gate.py` no longer defines `_git_output`. `_head_files` (line 55) calls `_git("diff-tree", ..., check=False, cwd=cwd)`. `_git()` in `git.py:10` has `cwd: Path | None = None` parameter. `subprocess` import retained for `_dirty_files`. |
| m-3 submodule helper standardization | **FIXED** | Verified via grep: no `_add_submodule_gitlink` or manual 20-call setup patterns remain. Test files use `create_submodule_origin` + `add_submodule` canonical pattern. |
| m-4 orphan-message assertion loosening | **FIXED** | Key fragment assertions replace exact prose matching. |
| m-5 arrow-line assertion loosening | **FIXED** | Four separate fragment checks replace exact string equality. |
| m-6 vacuous test fix | **FIXED** | `test_write_completed_with_accumulated_content` commits session.md before write, exercises autostrip path via `_detect_write_mode`. |
| m-7 resume state clearing | **FIXED** | `test_handoff_resume_from_write_session` asserts state file absent after resume completion. |

All 7 RC14 active minors verified fixed. No regressions from the fix cycle.

## Findings

### [minor] m-1: `_git_ok` defined but unused

- **File:** `src/claudeutils/git.py:34-37`
- **Axis:** excess
- **Description:** `_git_ok(*args)` is defined in `git.py` but has no callers anywhere in the codebase. No import reference found. Dead code from extraction. Should be removed or documented as part of the public API.

### [minor] m-2: `_STATE_FILE` uses relative path, depends on cwd

- **File:** `src/claudeutils/session/handoff/pipeline.py:12`
- **Axis:** robustness
- **Description:** `_STATE_FILE = Path("tmp") / ".handoff-state.json"` is relative to cwd. The handoff CLI (`handoff/cli.py`) does not enforce cwd == project root. If the CLI is invoked from a subdirectory, the state file is created in the wrong location. The `session_path` uses an env var override (`CLAUDEUTILS_SESSION_FILE`) but the state file does not derive its location from session_path or an equivalent anchor. Low practical risk (Click commands typically run from project root), but inconsistent with `session_path`'s env-var-based resolution.

### [minor] m-3: `_strip_hints` keeps single-space lines after hint but does not reset `prev_was_hint`

- **File:** `src/claudeutils/session/commit_pipeline.py:203-211`
- **Axis:** functional correctness
- **Description:** When a non-continuation indented line is encountered after a hint (line 207: `is_continuation` is False), the line is appended to `result` but `prev_was_hint` is not reset. The next line is still evaluated against the `prev_was_hint` condition. If the next line is indented (e.g., git commit output with leading spaces), it would be incorrectly classified as a potential hint continuation. No functional impact because git commit output lines that follow hint blocks are not indented, but the state machine has an implicit assumption about git output format that is not documented.

### [minor] m-4: `render_pending` always shows model in `▶` line, even for default model

- **File:** `src/claudeutils/session/status/render.py:44-48`
- **Axis:** conformance
- **Description:** The `▶` line always shows `({model})` including when model is the default `sonnet`. The outline STATUS format shows `▶ <first task> (<model>)` without specifying default suppression. However, the non-`▶` items on line 55 suppress the default model: `model_suffix = f" ({model})" if model != "sonnet" else ""`. Inconsistent treatment between the first-task and remaining-task display. The first task shows `(sonnet)` while remaining tasks with sonnet show no suffix.

### [minor] m-5: `detect_parallel` uses O(n^3) algorithm for consecutive window search

- **File:** `src/claudeutils/session/status/render.py:164-169`
- **Axis:** robustness
- **Description:** The nested loop iterates `range(cap, 1, -1)` * `range(n - size + 1)` with `_is_independent` checking all pairs in the subset. With cap=5 and typical task counts (<20), this is fast. However, for pathological cases (many independent tasks), the algorithm is O(n^2 * cap). No practical impact given the cap and typical session sizes, but the algorithm could be simplified to a greedy consecutive-independent scan that is O(n * edges).

### [minor] m-6: `_build_dependency_edges` blocker matching is coarse

- **File:** `src/claudeutils/session/status/render.py:120-128`
- **Axis:** functional correctness
- **Description:** Blocker text is concatenated into a single string, then both task names are checked via `in` (substring match). A task named "Fix" would match any blocker containing "Fix" anywhere (e.g., "Fixed in v2"). The conservative direction (false dependencies) is documented in the comment on line 120 ("may create false dependency edges"), and the consequence is only reduced parallelism (never unsafe parallelism). The documentation accurately captures the trade-off. This is a design-level decision, not a bug.

### [minor] m-7: `discover_submodules` strips lines before splitting

- **File:** `src/claudeutils/git.py:65-70`
- **Axis:** functional correctness
- **Description:** `line.strip()` on `git submodule status` output removes the leading status character (`+`, `-`, `U`, or space) before `split()`. This works because the hash (second field after status char) is consumed by `parts[0]` and the path is `parts[1]`. However, the strip/split approach discards the status character that distinguishes initialized (`space`), modified (`+`), uninitialized (`-`), and merge-conflict (`U`) submodules. If a submodule is uninitialized (`-`), `parts[1]` still returns the correct path. No functional impact for path extraction, but the function cannot distinguish submodule states if needed in the future.

## Gap Analysis

| Design Requirement | Status | Reference |
|-------------------|--------|-----------|
| S-1: Package structure | Covered | `session/` with `handoff/` and `status/` sub-packages (deviation from flat outline is acceptable — sub-packages for multi-file domains) |
| S-2: `_git()` extraction + submodule discovery | Covered | `git.py` with `cwd` param; all worktree modules import from `claudeutils.git`; no remaining `worktree.utils` imports |
| S-3: Output and error conventions | Covered | All subcommands: stdout-only, exit 0/1/2, `**Error:**` format, STOP directives |
| S-4: Session.md parser | Covered | `session/parse.py` composes `extract_task_blocks` + `parse_task_line` + `_extract_plan_from_block` |
| S-5: Git changes utility | Covered | `git_cli.py` — `changes_cmd` with submodule iteration, "Tree is clean." for empty output |
| H-1: Domain boundaries | Covered | CLI writes status + completed; no pending task mutations |
| H-2: Committed detection | Covered | Three modes in `pipeline.py:143-219` — overwrite/append/autostrip with `.strip("\n")` + `.rstrip()` normalization |
| H-3: Diagnostic output | Covered | `handoff/cli.py:69-71` — `git_changes()` after writes, guarded `if git_output.strip()` |
| H-4: State caching + step_reached | Covered | `HandoffState` dataclass, save/load/clear, resume skip at `cli.py:59` |
| C-1: Scripted vet check | Covered | pyproject.toml patterns + `_AGENT_CORE_PATTERNS` + `PurePath.full_match()` + report freshness |
| C-2: Submodule coordination | Covered | `_partition_by_submodule` + `_validate_inputs` + `_commit_submodule` with pointer staging; 4-cell matrix |
| C-3: Input validation + STOP | Covered | `CleanFileError` with STOP directive; `CommitInputError` caught at CLI boundary; exit 2 |
| C-4: Validation levels | Covered | Orthogonal `just-lint` / `no-vet` options in `_validate` |
| C-5: Amend semantics | Covered | `_head_files` with `--root` flag; directional propagation; `no-edit` validation |
| ST-0: Worktree-destined tasks | Covered | `worktree_marker` check at `render.py:45` skips for Next selection |
| ST-1: Parallel detection | Covered | Consecutive windows, cap 5, dependency edges, document order |
| ST-2: Preconditions | Covered | Missing file → exit 2; old section name → exit 2; metadata mismatch → exit 2 |
| Registration in cli.py | Covered | Lines 155-158: `_handoff`, `_commit`, `_status`, `_git` group |
| Porcelain safety (learning) | Covered | `_dirty_files` uses raw `result.stdout.splitlines()` (line 45); `_git()` docstring warns against porcelain use (line 19) |
| `PurePath.full_match` (learning) | Covered | `commit_gate.py:135` uses `PurePath(f).full_match(pat)` not `.match()` |

## Summary

| Severity | Count |
|----------|-------|
| Critical | 0 |
| Major | 0 |
| Minor | 7 |

All 7 RC14 active minors verified fixed. No regressions from the fix cycle.

New findings: 7 minors — 1 dead code (m-1), 1 robustness (m-2), 2 logic clarity (m-3, m-7), 1 display inconsistency (m-4), 1 algorithm note (m-5), 1 documented conservative trade-off (m-6).

No critical or major findings. All design requirements covered. The codebase is functionally complete against the outline specification.

**Trend:** RC13 0C/0M/7m (code) → RC14 0C/0M/2m → RC15 0C/0M/7m. The 7 new minors are all style/robustness-class — no functional defects.
