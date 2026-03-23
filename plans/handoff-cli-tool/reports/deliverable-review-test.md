# Test Deliverable Review: handoff-cli-tool (RC6)

Reviewed 20 test files (~3438 lines) against `plans/handoff-cli-tool/outline.md`.

## RC5 Fix Verification

| RC5 Finding | Status | Evidence |
|---|---|---|
| m-8: Local `_init_git_repo` helpers replaced with `init_repo_minimal` | **Fixed** | `grep -r _init_git_repo tests/` returns zero matches. `test_planstate_aggregation.py` and `test_planstate_aggregation_integration.py` both import from `tests.pytest_helpers`. |
| m-9: `test_strip_hints_multi_continuation` added | **Fixed** | test_session_commit_pipeline.py:121-128 — multi-line continuations (line1, line2, line3) all filtered after `hint:` prefix, `"normal"` preserved. |
| m-9: `test_strip_hints_single_space_not_continuation` added | **Fixed** | test_session_commit_pipeline.py:132-138 — single-space indent `" not a continuation"` passes through, not stripped. |
| m-10: `startswith("- ")` assertion added to `test_status_format_merged_next` | **Fixed** | test_status_rework.py:112 — `assert second_line.startswith("- ")` pins dash-prefix format for non-first tasks. |

All three RC5 fix items verified present and correct.

## Coverage Matrix

| Design Section | Test File(s) | Coverage Assessment |
|---|---|---|
| S-1: Package structure | test_session_commit_cli.py, test_git_cli.py, test_session_integration.py | Registration tested via CliRunner for `_handoff`, `_commit`, `_status`, `_git changes`. |
| S-2: `_git()` + submodule discovery | test_git_helpers.py | `_git_ok` (success/failure), `discover_submodules` (none/present), `_is_submodule_dirty` (clean/dirty/nonexistent), `git_status` porcelain preservation, `_is_dirty` with `exclude_path`. |
| S-3: Output and error conventions | test_session_commit_cli.py, test_session_commit_format.py, test_commit_pipeline_errors.py | Exit codes 0/1/2 verified. Structured markdown errors (`**Error:**`, `**Warning:**`), `STOP:` directive (via CleanFileError), hint/advice stripping with multi-line continuations and single-space boundary. |
| S-4: Session.md parser | test_session_parser.py | Status line, completed section, in-tree tasks (3 with model/command/plan_dir), worktree tasks (slug and `wt` markers), blockers extraction, blank line preservation, old format defaults, empty sections, missing file error. |
| S-5: Git changes utility | test_git_cli.py | Clean repo, dirty parent (status + diff content), dirty submodule with prefixed paths, clean submodule section omitted. |
| H-1: Domain boundaries | test_session_handoff.py, test_session_handoff_cli.py | Status overwrite, completed section write. Other sections (In-tree Tasks) preserved intact after writes. |
| H-2: Completed section write mode | test_session_handoff.py | Overwrite (fresh), accumulated content replacement, empty section, idempotent (double-write), committed-state overwrite with real git repo. |
| H-3: Diagnostic output | test_session_handoff_cli.py | Fresh handoff asserts `"Git status"` in output. Submodule diagnostics tested with real `git submodule add` setup. |
| H-4: State caching | test_session_handoff.py, test_session_handoff_cli.py | save/load/clear state cycle, resume mode (pre-populated state), no-stdin-no-state exits 2, `step_reached` field default `"write_session"`, state file cleanup after success. |
| C-1: Scripted vet check | test_session_commit.py, test_session_commit_validation.py | No config passes, fresh report passes (mtime-pinned), unreviewed fails (reason + file list), stale fails with file names and timestamps in `stale_info`. |
| C-2: Submodule coordination | test_session_commit_pipeline_ext.py | Four-cell matrix: files+message (both committed, verified via git log), files-only (error), message-only (warning text matches spec), neither (parent-only, no warning). |
| C-3: Input validation | test_session_commit.py, test_session_commit_cli.py | Clean file error with STOP, amend accepts HEAD files, amend rejects non-HEAD clean files, CleanFileError exits 2 at CLI level. |
| C-4: Validation levels | test_session_commit_validation.py | just-lint routes to lint not precommit, no-vet skips vet_check, default calls vet_check, combined just-lint+amend, stale vet failure includes detail, unknown reason fallback. |
| C-5: Amend semantics | test_session_commit_pipeline_ext.py, test_commit_pipeline_errors.py | Parent amend (replaces commit, verifies count=2), submodule amend (both amended, sub_log count=2), amend validation (HEAD-only files accepted), amend+no-edit (preserves message, verifies via git log). |
| ST-0: Worktree-destined tasks | test_status_rework.py, test_session_status.py | Worktree-marked tasks skipped for `Next:` selection (`▶` on second task). Both `wt` and slug markers rendered in Worktree section. |
| ST-1: Parallel group detection | test_session_status.py, test_status_rework.py | Different plans (group of 3), single task (None), shared plan (None), mixed consecutive (largest subset), blocker exclusion (unit + e2e with session.md + lifecycle.md), cap at 5 (7 tasks, returns 5). |
| ST-2: Preconditions and degradation | test_session_status.py, test_status_rework.py | Missing session.md exits 2, old-format tasks exit 2, old section name `"Pending Tasks"` rejected with exit 2. |

## Findings

### Critical

None.

### Major

**M-1: No test for `_split_sections` `in_message` flag — `## ` lines within Message section treated as body** (test_session_commit.py, coverage)

The design specifies (outline.md:163-164): "Everything from `## Message` to EOF is message body. ... Unknown `## ` within blockquotes treated as message body." The `_split_sections` function implements this via an `in_message` flag (commit.py:61-71) that stops `## ` heading detection after encountering `## Message`. No test verifies this behavior. A commit message containing `> ## Heading` inside the `## Message` section would be silently truncated if the `in_message` flag were removed, and no test would catch the regression.

Test input example:
```markdown
## Files
- foo.py

## Message
> ✨ Add feature
>
> ## Details
> - Implementation notes
```

Expected: `result.message` contains `"## Details"` as body text, not parsed as a new section.

### Minor

**m-1: `test_commit_cli_success` does not verify the commit actually happened** (test_session_commit_cli.py:18-36, specificity)

The test asserts `exit_code == 0` and `"foo" in result.output.lower()` but does not check `git log` to confirm a commit was created. Compare with `test_commit_parent_only` (test_session_commit_pipeline.py:46-53) which verifies via `git log`. The CLI test could pass even if the pipeline returned success without committing. Low severity because the pipeline test covers this path, but the CLI wiring test itself is vacuous on the commit side.

**m-2: `test_handoff_shows_submodule_changes` assertion is imprecise** (test_session_handoff_cli.py:234, specificity)

The test asserts `"## Submodule" in result.output` but the implementation outputs `**Git status:**` followed by the `git_changes()` output which contains `## Submodule: agent-core`. The assertion matches both the exact format (`## Submodule: agent-core`) and any hypothetical partial format (`## Submodule stuff`). A more specific assertion like `"## Submodule: agent-core" in result.output` would pin the actual output format.

**m-3: `SESSION_FIXTURE` defined after first usage in test_session_status.py** (test_session_status.py:280 vs :253, quality)

The module-level `SESSION_FIXTURE` string is defined at line 280 but first referenced at line 253 by `test_session_status_cli`. Python resolves module-level names at call time so this works, but harms readability. Carried forward from RC5 m-4.

**m-4: `test_session_parser.py` and `test_session_status.py` import `ParsedTask` from different modules** (consistency)

`test_session_parser.py:8` imports from `claudeutils.session.parse` while `test_session_status.py:17` imports from `claudeutils.validation.task_parsing`. Both are valid (the parse module re-exports from validation), but the inconsistency could confuse readers about the canonical import path.

**m-5: Submodule commit order not tested** (test_session_commit_pipeline_ext.py, coverage)

The design specifies (outline.md:265-267): "Multiple submodules committed in discovery order, each staged before parent commit." The tests only cover single-submodule cases. No test verifies ordering with 2+ submodules, or that submodule pointers are staged before the parent commit. Low severity because the multi-submodule case is a rare real-world scenario.

## Summary

| Severity | Count |
|----------|-------|
| Critical | 0 |
| Major | 1 |
| Minor | 5 |

**Delta from RC5:** RC5 had 0C/0M/5m (after fixes). This round finds 0C/1M/5m.

- RC5 m-8 (init_repo_minimal consolidation): Verified fixed, no local `_init_git_repo` helpers remain.
- RC5 m-9 (strip_hints edge cases): Verified fixed, both tests present and correct.
- RC5 m-10 (startswith assertion): Verified fixed.
- New M-1: `in_message` flag behavior untested — a design-specified scenario (outline.md:163-164) with no test coverage. The `_split_sections` function has a branch specifically for this, but a regression removing the flag would go undetected.
- RC5 m-4 (SESSION_FIXTURE placement) persists as m-3 — pre-existing quality issue, not addressed by RC5 fixes.
