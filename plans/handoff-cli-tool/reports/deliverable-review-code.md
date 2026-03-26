# L1 Code Review: handoff-cli-tool RC14

**Date:** 2026-03-26
**Methodology:** Full-scope review of all 26 code files against outline.md
**Review type:** Full-scope (not delta) with RC13 fix verification
**Prior:** RC13 0C/0M/22m total; 18 fixed, 4 dismissed (m-4, m-20, m-21, m-22); corrector applied 3 additional fixes

## Critical Findings

None.

## Major Findings

None.

## Minor Findings

**m-1** `commit_pipeline.py:193-215` -- functional correctness -- `_strip_hints` has a dead branch at lines 206-209. When `prev_was_hint` is True and the line starts with a single space (not tab, not double space), the code sets `prev_was_hint = True` and appends the line. But lines 204-205 also set `prev_was_hint = True` for tab/double-space (without appending). Both branches of the `if` at line 204 set `prev_was_hint = True`, making the conditional assignment on line 209 redundant. The `result.append(line)` on line 210 is the only differentiator. No functional impact (git hint lines use tab indentation), but the logic obscures intent.

**m-2** `commit_gate.py:31-50` -- modularity -- `_git_output` duplicates `git.py:_git()` with minor signature differences (`cwd` param, `check=False` default). Acknowledged via TODO on line 41. Not new (carried description from prior rounds), but the duplication persists and is the only instance of a non-consolidated git runner.

## RC13 Fix Verification

| Finding | Status | Evidence |
|---------|--------|---------|
| m-1 blank line preservation (append/autostrip) | **FIXED** | `pipeline.py:205` uses `list(current.splitlines())` (no filter) for append; `pipeline.py:213-216` autostrip filter uses `if not line.strip() or line.rstrip() not in committed_set` -- blank lines pass through |
| m-2 `_detect_write_mode` refactored to tuple return | **FIXED** | `pipeline.py:143` returns `tuple[str, str]`; `write_completed` at line 200 destructures `mode, committed_section`; autostrip at lines 209-210 uses returned committed_section instead of re-calling git show HEAD |
| m-3 status error accuracy | **FIXED** | `status/cli.py:64-65` now reports `{n} task lines without required metadata (** and —)` with concrete count; no longer misidentifies as "old-format" |
| m-5 comparison consistency (`.strip("\n")`) | **FIXED** | `pipeline.py:140` applies `.strip("\n")` to extracted section, making comparison at line 172 newline-insensitive while preserving internal newlines |
| m-6 empty diagnostics guard | **FIXED** | `handoff/cli.py:70` checks `if git_output.strip()` before emitting diagnostic block; empty git_changes produces no output |
| m-7 splitlines consistency | **FIXED** | `_extract_completed_section` (pipeline.py:124) uses `splitlines(keepends=True)` then `.strip("\n")`; `_detect_write_mode` comparison at line 172 uses `==` on `.strip("\n")`-normalized strings; writers at lines 175-179 use `.splitlines()` + `.rstrip()` for set/list construction |
| RC13 corrector: autostrip rstrip consistency | **FIXED** | `pipeline.py:209` committed_set uses `line.rstrip()` (not `line.strip()`); `pipeline.py:216` filter predicate uses `line.rstrip()` -- both match `_detect_write_mode` normalization at lines 175-179 |
| m-4 dismissal (len>3 guard) | **STILL APPROPRIATE** | `commit_gate.py:66` -- `len(line) > 3` correctly requires minimum valid porcelain line length (2 status chars + 1 space + 1+ path chars = 4 minimum). Git never produces empty-path porcelain lines |

## Gap Analysis

| Design Requirement | Status | Reference |
|-------------------|--------|-----------|
| S-1: Package structure | Covered | `session/` with `handoff/` and `status/` sub-packages |
| S-2: `_git()` extraction + submodule discovery | Covered | `git.py`; all worktree modules (`merge.py`, `merge_state.py`, `remerge.py`, `resolve.py`, `git_ops.py`, `cli.py`) import from `claudeutils.git` |
| S-3: Output and error conventions | Covered | All subcommands: stdout-only output, exit 0/1/2 semantics, `**Error:**` format, STOP directives |
| S-4: Session.md parser | Covered | `session/parse.py` composes `extract_task_blocks` + `parse_task_line` + `_extract_plan_from_block` |
| S-5: Git changes utility | Covered | `git_cli.py` -- `changes_cmd` with submodule iteration via `discover_submodules()` |
| H-1: Domain boundaries | Covered | CLI handles status overwrite + completed section; no pending task mutations |
| H-2: Committed detection | Covered | Three modes in `pipeline.py:143-219` -- overwrite/append/autostrip with correct normalization |
| H-3: Diagnostic output | Covered | `handoff/cli.py:69-71` -- git_changes() after writes, guarded against empty output |
| H-4: State caching + step_reached | Covered | `HandoffState` dataclass, save/load/clear, resume skip at `cli.py:59` |
| C-1: Scripted vet check | Covered | pyproject.toml patterns + `_AGENT_CORE_PATTERNS` + report freshness comparison |
| C-2: Submodule coordination | Covered | `_partition_by_submodule` + `_validate_inputs` + `_commit_submodule` with pointer staging |
| C-3: Input validation + STOP | Covered | `CleanFileError` with STOP directive; `CommitInputError` caught at CLI boundary |
| C-4: Validation levels | Covered | Orthogonal `just-lint` / `no-vet` options; `_validate` dispatches accordingly |
| C-5: Amend semantics | Covered | `_head_files` with `--root` flag; directional propagation in `_commit_submodule` |
| ST-0: Worktree-destined tasks | Covered | `worktree_marker` check at `render.py:45` skips marked tasks for Next selection |
| ST-1: Parallel detection | Covered | Consecutive windows, cap 5, dependency edges from shared plan_dir and blocker text |
| ST-2: Preconditions | Covered | Missing file -> exit 2 (`status/cli.py:56`); old format -> exit 2 (`_check_old_section_name`); metadata mismatch -> exit 2 |
| Registration in cli.py | Covered | Lines 155-158: `_handoff`, `_commit`, `_status`, `_git` |

## Summary

| Severity | Count |
|----------|-------|
| Critical | 0 |
| Major | 0 |
| Minor | 2 |

All 7 RC13 code minors verified fixed. RC13 corrector's 3 fixes (rstrip consistency, assertion strength, test assertion) verified in final state. m-4 dismissal remains appropriate.

m-1 (hint stripping logic clarity) is cosmetic. m-2 (_git_output duplication) has an in-code TODO and is acknowledged tech debt.

**Trend:** RC12 1C/0M/7m (code) -> RC13 0C/0M/7m -> RC14 0C/0M/2m. 5 code minors closed by RC13 fix. 2 new minors at lower severity (cosmetic/tech-debt).
