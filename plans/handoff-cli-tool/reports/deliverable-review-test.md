# L1 Test Review: handoff-cli-tool RC14

**Date:** 2026-03-26
**Scope:** Full-scope review of 22 test files (+4158 lines)
**Design spec:** `plans/handoff-cli-tool/outline.md` (S-1..S-5, H-1..H-4, C-1..C-5, ST-0..ST-2)
**Prior:** RC13 0C/0M/22m; RC13 fix addressed 18 minors (10 test); corrector fixed 3 additional

## Critical Findings

None.

## Major Findings

None.

## Minor Findings

**m-1** `test_git_cli.py:15-67` / `test_session_commit_pipeline_ext.py:22-35` / `test_session_handoff_cli.py:142-236` — conformance — **Carried m-12: Inconsistent submodule setup helpers.** Three different approaches to submodule setup across test files: (1) `test_git_cli.py` uses local `_add_submodule_gitlink` via git plumbing (`update-index --cacheinfo 160000`), (2) commit tests use shared `pytest_helpers.create_submodule_origin` + `add_submodule`, (3) `test_session_handoff_cli.py:142-236` manually sets up from scratch (20 subprocess calls). All functionally valid for their contexts but divergent maintenance burden.

**m-2** `test_session_commit_pipeline_ext.py:133-136` — specificity — `test_commit_submodule_orphan_message` asserts exact warning prose including punctuation: `"Submodule message provided but no changes found for: agent-core. Ignored."`. Tight coupling to format — any rewording breaks the test without functional regression. Key fragments (`"no changes found"`, `"agent-core"`, `"Ignored"`) would be more resilient.

**m-3** `test_session_status.py:132` — specificity — `test_render_pending_next_task_format` asserts exact string equality on the arrow line: `assert arrow_line == "... Build widget (sonnet) | Restart: Yes"`. Any display format change (e.g., adding plan status) would break this assertion without functional regression.

**m-4** `test_session_handoff.py:217-232` — vacuity — `test_write_completed_with_accumulated_content` does not commit session.md before calling `write_completed`. Without a committed baseline, `_detect_write_mode` returns `"overwrite"` (git show fails). The test verifies the overwrite path, not a distinct accumulated-content scenario — functionally identical to `test_write_completed_replaces_section` at line 187.

**m-5** `test_session_handoff_cli.py:371-391` — coverage — `test_handoff_resume_from_write_session` verifies session.md content after resume but does not assert state file is cleared. State clearing is covered by adjacent test (`test_session_handoff_cli_resume` at line 117) and `test_handoff_resume_from_diagnostics_skips_writes` at line 315. Not a coverage gap — noted for completeness. (Carried from corrector deferred item.)

## RC13 Fix Verification

| Finding | Status | Evidence |
|---------|--------|----------|
| m-8: Fixture ordering | **FIXED** | `test_session_status.py:246` — `SESSION_FIXTURE` defined at line 246, first usage `test_session_status_cli` at line 270. All usages follow definition. |
| m-9: Assertion specificity | **FIXED** | `test_session_commit_pipeline.py:108-155` — five sub-tests use specific strings ("helpful continuation", "[main abc123] commit msg", "single-space-line") instead of generic words. Each continuation variant tested independently. |
| m-10: Split conflated tests | **FIXED** | `test_planstate_aggregation.py:102-215` — `_init_repo_with_session` helper factored out. Three independent functions: `test_commits_since_handoff_counts` (positive), `test_commits_since_handoff_zero_without_session` (negative), `test_latest_commit_returns_subject_and_timestamp` (return type). Each has focused docstring and single assertion target. |
| m-11: Removed redundant test | **FIXED** | `test_session_handoff.py` — the pre-H-2 redundant test (m-16) was removed. Remaining `test_write_completed_with_accumulated_content` (line 217) is a distinct scenario from committed-detection tests. |
| m-13: Comment rewrite | **FIXED** | `test_session_handoff_committed.py` — comments now describe mode-detection rationale: "H-2 mode: overwrite" (line 46), "H-2 mode: append" (line 88), "H-2 mode: autostrip" (line 122). Agent behavior language removed. |
| m-14: Autostrip error fallback coverage | **FIXED** | `test_session_handoff_committed.py:308-319` — `test_detect_write_mode_overwrite_on_no_head` exercises `CalledProcessError` catch in `_detect_write_mode` (file on disk, not committed). Asserts mode = `"overwrite"` and committed = `""`. |
| m-15: Resume from write_session | **FIXED** | `test_session_handoff_cli.py:371-391` — `test_handoff_resume_from_write_session` saves state with `step_reached="write_session"`, invokes CLI without stdin. Verifies status updated ("Phase 4 complete."), completed replaced ("Implemented write_completed"), prior content removed ("Previous task" absent). |
| m-17: Direct _detect_write_mode unit test | **FIXED** | `test_session_handoff_committed.py:270-303` — `test_detect_write_mode_all_three_modes` exercises all three conditions on same repo: no changes = overwrite, committed removed + new = append, committed preserved + additions = autostrip. Asserts mode string and committed content for autostrip. |
| Corrector m-5: Assertion strength | **FIXED** | `test_session_handoff_committed.py:205` — `assert mode == "append"` (specific) replaces prior `!= "autostrip"` (exclusion). Deterministic for indentation-change scenario. |
| Corrector m-6: Block header check | **FIXED** | `test_session_handoff_cli.py:365` — `assert "**Git status:**" not in result.output` verifies diagnostic block omission by header presence, not delimiter shape. |

## Coverage Matrix

| Design Requirement | Test File(s) | Status |
|-------------------|-------------|--------|
| **S-1: Package structure** | Imports across all test files verify `session/`, `session/handoff/`, `session/status/`, `session/commit*.py` | Covered |
| **S-2: _git() extraction + submodule discovery** | `test_git_helpers.py:22-94` (_git_ok, discover_submodules none/present, _is_submodule_dirty clean/dirty/nonexistent), `test_git_helpers.py:123-219` (git_status porcelain format, _is_dirty exclude_path) | Covered |
| **S-3: Output and error conventions** | `test_session_commit_cli.py:24-155` (exit 0/1/2, stdout-only, `**Error:**` format), `test_session_handoff_cli.py:120-284` (exit 2, structured error), `test_session_status.py:287-323` (exit 2 for missing/malformed) | Covered |
| **S-4: Session.md parser** | `test_session_parser.py:17-213` (status_line, completed, in-tree tasks, worktree tasks, plan_dir, date, markers, blockers, blank lines, missing file error, old format defaults) | Covered |
| **S-5: Git changes utility** | `test_git_cli.py:70-157` (clean repo, dirty parent, dirty submodule with prefixed paths, clean submodule omitted) | Covered |
| **H-1: Domain boundaries** | `test_session_handoff.py`, `test_session_handoff_cli.py` (CLI writes status + completed only; In-tree Tasks section preserved) | Covered |
| **H-2: Committed detection** | `test_session_handoff_committed.py:49-303` (overwrite/append/autostrip modes, all three via `_detect_write_mode` unit test, trailing whitespace normalization, indentation awareness, error fallback to overwrite, blank line preservation in both append and autostrip) | Covered |
| **H-3: Diagnostic output** | `test_session_handoff_cli.py:69-93` (git status/diff emitted), `test_session_handoff_cli.py:344-365` (empty output suppressed — no `**Git status:**` header), `test_session_handoff_cli.py:142-236` (submodule changes in diagnostics) | Covered |
| **H-4: State caching** | `test_session_handoff.py:237-316` (create, load, clear, step_reached, backward compat, unknown fields ignored), `test_session_handoff_cli.py:96-117,291-391` (CLI resume from diagnostics, resume from write_session, state cleared on success) | Covered |
| **C-1: Scripted vet check** | `test_session_commit.py:263-362` (no config passes, pass with fresh report, unreviewed, stale, stale with explicit cwd), `test_session_commit_validation.py:217-257` (stale with file detail) | Covered |
| **C-2: Submodule coordination** | `test_session_commit_pipeline_ext.py:41-163` (4-cell matrix), `test_session_commit_pipeline_ext.py:332-393` (multi-submodule ordering), `test_session_commit_cli.py:129-155` (missing message exit 2 via CLI) | Covered |
| **C-3: Input validation + STOP** | `test_session_commit.py:183-257` (dirty passes, clean error with STOP, amend accepts HEAD files, amend rejects non-HEAD clean files), `test_session_commit_pipeline.py:157-212` (submodule clean-file full path) | Covered |
| **C-4: Validation levels** | `test_session_commit_validation.py:21-291` (just-lint, default-calls-vet, no-vet skips, combined just-lint+amend, just-lint+no-vet, stale detail, unknown reason) | Covered |
| **C-5: Amend semantics** | `test_session_commit_pipeline_ext.py:168-327` (parent amend, submodule amend, amend validation HEAD-only), `test_commit_pipeline_errors.py:248-284` (amend+no-edit preserves message), `test_session_commit.py:86-104` (no-edit without amend error, no-edit with message contradicts) | Covered |
| **ST-0: Worktree-destined tasks** | `test_status_rework.py:151-180` (worktree-marked task skipped for Next, second task gets arrow) | Covered |
| **ST-1: Parallel group detection** | `test_session_status.py:165-225` (group, no-group, shared-plan, mixed, cap-at-5, blocker-excludes), `test_status_rework.py:218-267` (blockers wired to CLI) | Covered |
| **ST-2: Preconditions** | `test_session_status.py:287-323` (missing session.md exit 2, malformed task accurate error), `test_status_rework.py:118-145,186-212` (old format exit 2, old section name exit 2) | Covered |
| **Registration** | CLI invocation via CliRunner: `_status` (test_session_status.py:270), `_handoff` (test_session_handoff_cli.py:78), `commit_cmd` (test_session_commit_cli.py:39) | Covered |
| **Error propagation** | `test_commit_pipeline_errors.py:22-245` (git commit failure, stage failure, structured error with/without stderr, validation before submodule commit, submodule failure propagation) | Covered |
| **Output formatting** | `test_session_commit_format.py:10-74` (parent-only, submodule labeled, warning prepended, hints stripped, empty parent with submodule) | Covered |
| **Cross-subcommand integration** | `test_session_integration.py:17-80` (handoff then status round-trip) | Covered |

## Summary

| Severity | Count |
|----------|-------|
| Critical | 0 |
| Major | 0 |
| Minor | 5 |

All 10 RC13 test fix items verified clean. Both corrector fixes confirmed in place with correct assertions.

Coverage is complete: every design requirement (S-1..S-5, H-1..H-4, C-1..C-5, ST-0..ST-2) has at least one test exercising the specified behavior. H-2 (committed detection) has the deepest coverage with 10 dedicated tests across three modes plus edge cases (trailing whitespace, indentation, error fallback, blank line preservation).

Minor findings: m-1 carries m-12 (inconsistent submodule helpers, expanded scope with third variant found). m-2 and m-3 are tight string coupling in assertions. m-4 is a vacuity issue (test name implies distinct behavior, exercises same overwrite path). m-5 is a coverage note (state clearing not asserted in resume test, but covered by adjacent tests). None affect functional correctness.

**Trend:** RC12 0C/0M/10m -> RC13 0C/0M/10m -> RC14 0C/0M/5m. 8 carried minors resolved, 1 carried (m-12 expanded), 4 new style/resilience items.
