# Test Deliverable Review: handoff-cli-tool (RC5)

Reviewed 20 test files against `plans/handoff-cli-tool/outline.md`.

## RC4 Fix Verification

| RC4 Finding | Status | Evidence |
|---|---|---|
| M-1: `test_write_completed_overwrites_committed_state` | **Fixed** | test_session_handoff.py:258-274 — calls `init_repo_minimal`, commits session.md via `_commit_session`, modifies, calls `write_completed`, asserts old content removed. |
| M-2: `init_repo_minimal` in pytest_helpers.py | **Fixed** | pytest_helpers.py:79-89 — `init_repo_minimal` exists, used by 5 files (test_session_commit.py, test_session_handoff.py, test_session_handoff_cli.py, test_session_integration.py, test_status_rework.py). See m-1 below for residual. |
| m-5: `test_detect_parallel_caps_at_five` | **Fixed** | test_session_status.py:208-213 — creates 7 independent tasks, asserts `len(result) == 5`. |
| m-6: split or-disjunction assertions | **Fixed** | test_session_commit_pipeline.py:43 asserts `"foo" in result.output.lower()` as a standalone assertion; line 79 asserts `"Precommit" in result.output` and `"failed" in result.output` as separate assertions. |
| m-7: extended `test_handoff_then_status` | **Fixed** | test_session_integration.py:72-77 — session.md content assertions added: `"Phase 6 complete"`, `"Implemented commit pipeline"`, `"Added amend semantics"` present; `"Nothing yet."` absent. |

All five RC4 fixes verified present and correct.

## Coverage Matrix

| Design Section | Test File(s) | Coverage Assessment |
|---|---|---|
| S-1: Package structure | test_session_commit_cli.py, test_git_cli.py, test_session_integration.py | Registration tested via CliRunner invocation of `_handoff`, `_commit`, `_status`, `_git changes`. Adequate. |
| S-2: `_git()` extraction + submodule discovery | test_git_helpers.py | `_git_ok`, `discover_submodules` (none/present), `_is_submodule_dirty` (clean/dirty/nonexistent), `git_status` porcelain preservation, `_is_dirty` with `exclude_path`. Adequate. |
| S-3: Output and error conventions | test_session_commit_cli.py, test_session_commit_format.py, test_commit_pipeline_errors.py | Exit codes 0/1/2 tested. Structured markdown errors (`**Error:**`, `**Warning:**`), `STOP:` directive, hint/advice stripping with continuations. Adequate. |
| S-4: Session.md parser | test_session_parser.py | Status line, completed section, in-tree tasks, worktree tasks, plan_dir, worktree markers (`my-slug`, `wt`), blockers extraction, blank line preservation, old format defaults, empty sections. Adequate. |
| S-5: Git changes utility | test_git_cli.py | Clean repo, dirty parent, dirty submodule with prefixed paths, clean submodule omitted. Adequate. |
| H-1: Domain boundaries | test_session_handoff.py, test_session_handoff_cli.py | Status overwrite, completed section write. Other sections (In-tree Tasks) preserved. Adequate. |
| H-2: Completed section write mode | test_session_handoff.py | Overwrite, accumulated content replacement, empty section, idempotent, committed-state overwrite (M-1 fix). Adequate. |
| H-3: Diagnostic output | test_session_handoff_cli.py | Fresh handoff asserts `"Git status"` in output. Submodule diagnostics tested with real submodule setup. Adequate. |
| H-4: State caching | test_session_handoff.py, test_session_handoff_cli.py | save/load/clear state, resume mode, no-stdin-no-state exits 2, `step_reached` field with default `"write_session"`. Adequate. |
| C-1: Scripted vet check | test_session_commit.py, test_session_commit_validation.py | No config passes, fresh report passes, unreviewed fails, stale fails with per-file detail. Adequate. |
| C-2: Submodule coordination | test_session_commit_pipeline_ext.py | Four-cell matrix: files+message (both committed), files-only (error, needs message), message-only (warning, ignored), neither (parent-only). Adequate. |
| C-3: Input validation | test_session_commit.py, test_session_commit_cli.py | Clean file error with STOP, amend accepts HEAD files, amend rejects non-HEAD clean files, CleanFileError exits 2. Adequate. |
| C-4: Validation levels | test_session_commit_validation.py | just-lint calls lint not precommit, no-vet skips vet, default calls vet, combined just-lint+amend, stale vet detail, unknown reason. Adequate. |
| C-5: Amend semantics | test_session_commit_pipeline_ext.py, test_commit_pipeline_errors.py | Parent amend (replaces commit, verifies message and count), submodule amend (both amended, counts verified), amend validation (HEAD-only files accepted), amend+no-edit (preserves existing message). Adequate. |
| ST-0: Worktree-destined tasks | test_status_rework.py, test_session_status.py | Worktree-marked tasks skipped for `Next:` selection. Both `wt` and slug marker types rendered. Adequate. |
| ST-1: Parallel group detection | test_session_status.py, test_status_rework.py | Different plans (group), single task (None), shared plan (None), mixed consecutive, blocker exclusion (unit + e2e), cap at 5. Adequate. |
| ST-2: Preconditions and degradation | test_session_status.py, test_status_rework.py | Missing session.md exits 2, old format exits 2, old section name `"Pending Tasks"` rejected with exit 2. Adequate. |

## Findings

### Critical

None.

### Major

None.

### Minor

1. **m-1: `_init_git_repo` local helper persists in test_planstate_aggregation_integration.py** (test_planstate_aggregation_integration.py:14-33, excess/consistency)
   - RC4 M-2 introduced `init_repo_minimal` in `pytest_helpers.py` and replaced 5 local variants. `test_planstate_aggregation_integration.py` still defines `_init_git_repo` (12 lines, str-based interface). This file is pre-existing (predates the handoff-cli-tool plan), so the local helper is not a regression introduced by this deliverable. The file's +15/-9 diff was for `aggregate_trees` no-dedup test logic, not init helper consolidation. Nonetheless, it is a remaining inconsistency in the test suite.

2. **m-2: `test_planstate_aggregation.py` does not use `init_repo_minimal`** (test_planstate_aggregation.py:65-115, consistency)
   - `test_dirty_state_detection` and `test_git_metadata_helpers` each inline 9 lines of `git init` + `git config` setup. Same class as m-1: pre-existing file, not a deliverable regression, but inconsistent with the shared helper pattern established by RC4 M-2.

3. **m-3: `test_strip_hints_filters_continuation_lines` relies on implementation detail of indentation threshold** (test_session_commit_pipeline.py:101-118, specificity)
   - The test uses `"  (helpful continuation)"` (2-space indent) and `"\tcontinuation here"` (tab indent) as continuation lines. The `_strip_hints` implementation at commit_pipeline.py:198 treats tab and double-space as continuations to strip, but single-space lines pass through. The design (outline.md:233) says only "Strip git hint: and advice lines" without specifying continuation behavior. The test accurately pins the implemented behavior, but the continuation-filtering logic itself has a subtle branch: `line[0] == "\t" or (line[0] == " " and len(line) > 1 and line[1] == " ")` sets `prev_was_hint = False` and strips the line, while single-space lines are kept. No test covers the single-space edge case (a continuation line with exactly one leading space). Low severity since git's actual hint output uses consistent indentation.

4. **m-4: `SESSION_FIXTURE` defined after first usage in test_session_status.py** (test_session_status.py:280 vs :249, quality)
   - The module-level `SESSION_FIXTURE` string is defined at line 280 but first referenced at line 253 by `test_session_status_cli`. Python resolves module-level names at call time so this works, but harms readability. Carried forward from RC4 m-6.

5. **m-5: `test_status_format_merged_next` asserts second task lacks command but does not verify the expected dash-prefix format** (test_status_rework.py:111, specificity)
   - The test asserts `"just fix" not in second_line` for the non-first task, confirming the command is omitted. It does not assert the dash-prefix format (`"- Second (haiku)"`) specified in the outline for non-first tasks. A `startswith("- ")` assertion on the second task line would pin the format.

## Summary

| Severity | Count |
|----------|-------|
| Critical | 0 |
| Major | 0 |
| Minor | 5 |

**Delta from RC4:** RC4 had 2M/6m. This round finds 0M/5m.

- RC4 M-1 (committed detection gap) resolved: `test_write_completed_overwrites_committed_state` added.
- RC4 M-2 (init_repo duplication) resolved: `init_repo_minimal` in pytest_helpers.py, adopted by 5 deliverable test files. Residual local helpers in pre-existing files downgraded to m-1/m-2.
- RC4 m-5 (parallel cap) resolved: `test_detect_parallel_caps_at_five` added.
- RC4 m-6 (or-disjunction) resolved: assertions split in test_session_commit_pipeline.py.
- RC4 m-7 (integration test assertions) resolved: session.md content checks added.

All RC4 fixes verified. No Major or Critical findings remain. The 5 minor findings are quality/consistency items, none affecting functional correctness.
