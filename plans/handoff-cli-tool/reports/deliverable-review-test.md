# Test Deliverable Review — Layer 1 (RC15)

**Date:** 2026-03-26
**Scope:** Full-scope review of 22 test files (17 new + 5 modified, ~4200 lines)
**Design spec:** `plans/handoff-cli-tool/outline.md` (S-1..S-5, H-1..H-4, C-1..C-5, ST-0..ST-2)
**Prior:** RC14 0C/0M/10m (7 active + 3 dismissed); RC14 fix addressed all 7 active minors

## RC14 Fix Verification

| RC14 Finding | Status | Evidence |
|-------------|--------|----------|
| m-1 `_strip_hints` redundant assignment | **FIXED** | `commit_pipeline.py:193-213` — `prev_was_hint = True` only on hint detection (line 202); no longer duplicated in sub-branches |
| m-2 `_git_output` duplication in commit_gate | **FIXED** | `commit_gate.py` — no `_git_output` function remains; `_dirty_files` uses raw `subprocess.run` with `cwd` param (line 37-43); `_git()` in `git.py` gained `cwd` parameter (line 13) |
| m-3 inconsistent submodule helpers | **FIXED** | `test_git_cli.py:12` imports canonical `create_submodule_origin` + `add_submodule`; `test_session_handoff_cli.py:15-16` same; git plumbing approach (`update-index --cacheinfo 160000`) eliminated from all test files |
| m-4 tight assertion in orphan message test | **FIXED** | `test_session_commit_pipeline_ext.py:132-134` — key fragments (`"**Warning:**"`, `"no changes found"`, `"agent-core"`) instead of full prose string |
| m-5 exact arrow-line string equality | **FIXED** | `test_session_status.py:131-138` — fragment assertions (`"▶" in arrow_line`, `"Build widget" in arrow_line`, `"sonnet" in arrow_line`) replace exact string match |
| m-6 vacuous accumulated content test | **FIXED** | `test_session_handoff.py:221` — `init_repo_at(tmp_path)` + commit at lines 225-233 creates git baseline for `_detect_write_mode`; test now exercises autostrip path |
| m-7 resume state file not asserted cleared | **FIXED** | `test_session_handoff_cli.py:358` — `assert not (tmp_path / "tmp" / ".handoff-state.json").exists()` |
| m-8 SKILL.md scope (dismissed) | **CONFIRMED** — Not a handoff-cli test deliverable |
| m-9 settings.local.json (dismissed) | **CONFIRMED** — POSIX trailing newline only |
| m-10 .gitignore (dismissed) | **CONFIRMED** — Sandbox artifact handling |

## Findings

### [minor] m-1: render_worktree test missing assertion for wt-destined marker

- **File:** `tests/test_session_status.py:75-83`
- **Axis:** specificity
- **Description:** `test_render_section` (worktree parametrization) constructs a task with `worktree_marker="wt"` (line 77) but only asserts `"Future work" in result` (line 83). Does not assert `"→ wt" in result`. The slug-based marker gets asserted (`"→ my-slug"` at line 82) but the `wt` marker — which exercises the ST-0 worktree-destined rendering path — is not verified in the output. The assertion passes even if `render_worktree` silently drops the `→ wt` suffix.

### [minor] m-2: `_task` helper constructs ParsedTask without plan_dir attribute

- **File:** `tests/test_session_status.py:20-38`
- **Axis:** independence
- **Description:** The `_task()` helper constructs `ParsedTask` via positional/keyword init but `plan_dir` is not in the constructor defaults dict. It relies on `ParsedTask` having a mutable `plan_dir` attribute that can be set post-construction (e.g., `test_session_status.py:56` does `t1.plan_dir = "parser"`). This couples the test helper to the implementation detail that `plan_dir` is a mutable attribute settable after construction rather than part of the dataclass init. If `ParsedTask` were refactored to use `__slots__` or frozen dataclass, these tests would fail for the wrong reason.

### [minor] m-3: test_session_integration covers only happy path

- **File:** `tests/test_session_integration.py:17-80`
- **Axis:** coverage
- **Description:** The single integration test verifies handoff-then-status round-trip (happy path). The outline specifies "Integration tests — end-to-end across subcommands, real git repos" (line 389). No negative integration test exists (e.g., handoff failure leaves session.md consistent for subsequent status, or commit after handoff verifying the two-stage flow). The happy path alone is sufficient for Phase 7 TDD but the absence of an error-recovery integration scenario is a minor coverage gap against "end-to-end across subcommands."

### [minor] m-4: Three dismissed scope findings carried forward

- **File:** N/A (not test files)
- **Axis:** excess
- **Description:** Dismissals m-8, m-9, m-10 from RC14 (SKILL.md change, settings.local.json, .gitignore) are not test-layer findings. They appeared in the combined deliverable review and were correctly dismissed. Noting for report completeness — they are not test artifacts.

## Coverage Matrix

| Design Requirement | Test File(s) | Status |
|-------------------|-------------|--------|
| **S-1: Package structure** | Imports across all test files verify `session/`, `session/handoff/`, `session/status/`, `session/commit*.py` | Covered |
| **S-2: `_git()` extraction + submodule discovery** | `test_git_helpers.py:22-94` (_git_ok, discover_submodules, _is_submodule_dirty), `test_git_helpers.py:123-219` (porcelain format, _is_dirty exclude_path) | Covered |
| **S-3: Output and error conventions** | `test_session_commit_cli.py:24-155` (exit 0/1/2), `test_session_handoff_cli.py:120-249` (exit 2, structured), `test_session_status.py:287-326` (exit 2 missing/malformed) | Covered |
| **S-4: Session.md parser** | `test_session_parser.py:17-213` (status_line, completed, in-tree, worktree, plan_dir, date, markers, blockers, blank lines, missing file, old format) | Covered |
| **S-5: Git changes utility** | `test_git_cli.py:27-113` (clean, dirty parent, dirty submodule with prefixed paths, clean submodule omitted) | Covered |
| **H-1: Domain boundaries** | `test_session_handoff.py`, `test_session_handoff_cli.py` (writes status + completed only; In-tree Tasks section preserved) | Covered |
| **H-2: Committed detection** | `test_session_handoff_committed.py:49-319` (overwrite/append/autostrip, direct `_detect_write_mode` unit test, trailing whitespace, indentation, error fallback, blank line preservation) | Covered |
| **H-3: Diagnostic output** | `test_session_handoff_cli.py:72-96` (git diagnostics emitted), `test_session_handoff_cli.py:309-331` (empty output suppressed), `test_session_handoff_cli.py:145-201` (submodule changes) | Covered |
| **H-4: State caching** | `test_session_handoff.py:253-332` (create, load, clear, step_reached, backward compat), `test_session_handoff_cli.py:99-120,207-358` (CLI resume from diagnostics/write_session, state cleared) | Covered |
| **C-1: Scripted vet check** | `test_session_commit.py:263-362` (no config, pass with report, unreviewed, stale, explicit cwd), `test_session_commit_validation.py:217-257` (stale file detail) | Covered |
| **C-2: Submodule coordination** | `test_session_commit_pipeline_ext.py:41-163` (4-cell matrix: files+msg, files-no-msg, no-files+msg, no-files-no-msg), `test_session_commit_pipeline_ext.py:330-391` (multi-submodule ordering), `test_session_commit_cli.py:129-155` (missing message exit 2) | Covered |
| **C-3: Input validation + STOP** | `test_session_commit.py:183-257` (dirty passes, clean error with STOP, amend accepts HEAD, amend rejects non-HEAD), `test_session_commit_pipeline.py:157-212` (submodule full path) | Covered |
| **C-4: Validation levels** | `test_session_commit_validation.py:21-291` (just-lint, default vet, no-vet skip, just-lint+amend, just-lint+no-vet, stale detail, unknown reason) | Covered |
| **C-5: Amend semantics** | `test_session_commit_pipeline_ext.py:166-324` (parent amend, submodule amend, amend validation), `test_commit_pipeline_errors.py:251-284` (amend+no-edit), `test_session_commit.py:86-98` (no-edit rules) | Covered |
| **ST-0: Worktree-destined tasks** | `test_status_rework.py:151-180` (worktree marker skips Next), `test_session_status.py:75-83` (render_worktree with wt marker) | Covered |
| **ST-1: Parallel group detection** | `test_session_status.py:168-227` (group, no-group, shared-plan, mixed, cap-at-5, blocker-excludes), `test_status_rework.py:218-267` (blockers wired end-to-end) | Covered |
| **ST-2: Preconditions** | `test_session_status.py:290-326` (missing session.md exit 2, malformed task error), `test_status_rework.py:118-145,186-212` (old format exit 2, old section name exit 2) | Covered |
| **Registration** | CLI invocations: `_status` (`test_session_status.py:273`), `_handoff` (`test_session_handoff_cli.py:81`), `commit_cmd` (`test_session_commit_cli.py:39`) | Covered |
| **Error propagation** | `test_commit_pipeline_errors.py:22-245` (git commit, stage, structured errors, validation ordering, submodule failure) | Covered |
| **Output formatting** | `test_session_commit_format.py:10-74` (parent-only, submodule labeled, warning, hints stripped, empty parent) | Covered |
| **Cross-subcommand integration** | `test_session_integration.py:17-80` (handoff → status round-trip) | Covered |

## Modified Files Review

| File | Change | Assessment |
|------|--------|------------|
| `test_planstate_aggregation.py` (+73/-69) | Refactored to use `init_repo_minimal` from pytest_helpers, split conflated tests into independent functions | Clean — addresses RC13 m-10 |
| `test_planstate_aggregation_integration.py` (+19/-34) | Updated imports to use `init_repo_minimal` | Clean — consistent helper usage |
| `test_worktree_merge_errors.py` (+4/-2) | Updated `_git` import path from `claudeutils.git` | Clean — follows S-2 extraction |
| `test_worktree_rm_dirty.py` (+6/-5) | Updated `_is_dirty` and `_is_submodule_dirty` import paths | Clean — follows S-2 extraction |
| `test_worktree_utils.py` (+2/-1) | Updated `_fail` import path | Clean — follows S-2 extraction |

## Summary

| Severity | Count |
|----------|-------|
| Critical | 0 |
| Major | 0 |
| Minor | 4 (3 active + 1 administrative note) |

**RC14 closure:** All 7 active minors verified fixed. All 3 dismissed items reconfirmed.

**New findings:** 3 active minors. m-1 is a missing assertion for `→ wt` rendering in the worktree section test. m-2 is post-construction attribute mutation coupling in the test helper. m-3 is integration test happy-path-only coverage. None affect functional correctness.

**Trend:** RC12 0C/0M/22m → RC13 0C/0M/10m → RC14 0C/0M/10m (7 active) → RC15 0C/0M/4m (3 active). Monotonic improvement. All design requirements (S-1..S-5, H-1..H-4, C-1..C-5, ST-0..ST-2) have test coverage. H-2 (committed detection) remains the deepest-covered area with 10+ tests across three modes plus edge cases.
