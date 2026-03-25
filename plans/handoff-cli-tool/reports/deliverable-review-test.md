# Test Review: handoff-cli-tool (RC12)

**Date:** 2026-03-25
**Scope:** 22 test files (+3866 lines), full-scope review
**Axes:** conformance, functional correctness, functional completeness, vacuity, excess, specificity, coverage, independence

## RC11 Fix Verification

| Finding | Status | Evidence |
|---------|--------|----------|
| m-11: SESSION_FIXTURE before first usage | FIXED | test_session_status.py:280-298 — `SESSION_FIXTURE` is now defined at line 280, but first usage is `test_session_status_cli` at line 249 which references it at line 253. Forward reference remains. **NOT FIXED** — the constant is still defined after its first usage. |
| m-12: Improved assertion strings | PARTIAL | test_session_commit_pipeline.py:128-134 — `test_strip_hints_single_space_then_double` assertions use `"single-space-line"`, `"double-space-cont"`, `"normal-line"` which are now more specific to the test data. However, `test_strip_hints_filters_continuation_lines` at line 108-125 still uses generic words `"continuation"`, `"other line"`. Improved but not fully addressed. |
| m-13: test_git_metadata_helpers conflates paths | NOT FIXED | test_planstate_aggregation.py:102-197 — still creates two repos in one test function (positive path at line 159, negative path at line 161-190). Same finding persists. |
| m-14: Two tests exercise same code path | NOT FIXED | test_session_handoff.py:217-248 — `test_write_completed_with_accumulated_content` and `test_write_completed_overwrites_not_appends` still exercise same `_write_completed_section` code path. Same finding persists. |
| m-15: Inconsistent submodule setup helpers | NOT FIXED | test_session_commit_pipeline.py:157-212 uses `create_submodule_origin` + `add_submodule` while test_session_commit_pipeline_ext.py:22-35 uses `_init_repo_with_submodule`. Same finding persists. |

**Corrector review claim (dead mock removed from step_reached test):** Verified. test_session_handoff.py:300-332 `test_save_state_includes_step_reached` and `test_load_state_backward_compat_missing_step_reached` operate on real state files with no mocks. No dead mock present.

## Coverage Checklist

| # | Scenario | Covered | Test Reference |
|---|----------|---------|----------------|
| 1 | H-2 overwrite (no prior diff) | Y | test_session_handoff_committed.py:46-60 `test_write_completed_overwrite_when_no_diff` |
| 2 | H-2 append (old cleared, new present) | Y | test_session_handoff_committed.py:88-116 `test_write_completed_appends_when_prior_uncommitted` |
| 3 | H-2 autostrip (old preserved with additions) | Y | test_session_handoff_committed.py:122-151 `test_write_completed_autostrip_when_old_preserved` |
| 4 | H-4 step_reached resume: skip to diagnostics | Y | test_session_handoff_cli.py:291-315 `test_handoff_resume_from_diagnostics_skips_writes` |
| 5 | H-4 step_reached: value persistence | Y | test_session_handoff_cli.py:318-338 `test_handoff_updates_step_reached_after_writes` |
| 6 | C-1 vet check: no config passes | Y | test_session_commit.py:263-268 |
| 7 | C-1 vet check: unreviewed fails | Y | test_session_commit.py:295-309 |
| 8 | C-1 vet check: stale fails | Y | test_session_commit.py:312-336, test_session_commit_validation.py:217-257 |
| 9 | C-2 submod files+msg | Y | test_session_commit_pipeline_ext.py:41-81 |
| 10 | C-2 submod files, no msg | Y | test_session_commit_pipeline_ext.py:84-106 |
| 11 | C-2 no submod files, msg present | Y | test_session_commit_pipeline_ext.py:109-136 |
| 12 | C-2 no submod files, no msg | Y | test_session_commit_pipeline_ext.py:139-162 |
| 13 | C-3 clean files exit 2 + STOP | Y | test_session_commit.py:203-222, test_session_commit_cli.py:95-121 |
| 14 | C-4 default (precommit + vet) | Y | test_session_commit_validation.py:48-72 |
| 15 | C-4 no-vet | Y | test_session_commit_validation.py:75-98 |
| 16 | C-4 just-lint | Y | test_session_commit_validation.py:21-45 |
| 17 | C-4 just-lint + no-vet | Y | test_session_commit_validation.py:259-291 |
| 18 | C-5 amend parent-only | Y | test_session_commit_pipeline_ext.py:168-210 |
| 19 | C-5 amend submodule+parent | Y | test_session_commit_pipeline_ext.py:213-284 |
| 20 | C-5 amend+no-edit | Y | test_commit_pipeline_errors.py:251-284 |
| 21 | C-5 no-edit without amend error | Y | test_session_commit.py:86-88 |
| 22 | ST-0 worktree marker skip | Y | test_status_rework.py:151-180 |
| 23 | ST-1 parallel: consecutive, cap 5, dep exclusion | Y | test_session_status.py:165-225 |
| 24 | ST-2 missing session.md exit 2 | Y | test_session_status.py:266-277 |
| 25 | ST-2 old format exit 2 | Y | test_status_rework.py:118-145 |
| 26 | S-3 exit 0 success | Y | test_session_commit_cli.py:18-46 |
| 27 | S-3 exit 1 pipeline error | Y | test_session_commit_cli.py:63-89 |
| 28 | S-3 exit 2 input validation | Y | test_session_commit_cli.py:49-60, test_session_status.py:266-277 |

All 28 design scenarios have test coverage.

## New Findings

**F-1** `test_session_status.py:280-298` — conformance — Minor
`SESSION_FIXTURE` defined at line 280, after first usage at line 253 (`test_session_status_cli`). Forward reference works in Python (module-level names resolved at call time, not definition time) but violates conventional top-of-module fixture placement. Carried across RC8 through RC11 as m-11 with claimed fix. The claimed fix (m-11 from RC11) is incorrect — the constant is still after its first usage.

**F-2** `test_session_commit_pipeline.py:108-125` — specificity — Minor
`test_strip_hints_filters_continuation_lines` assertions use generic words: `"continuation"`, `"other line"`, `"normal line"`. These match the inline test data, but are common English words that could produce false passes if test data drifted. The related tests at lines 128-154 use more distinctive test data (`"single-space-line"`, `"double-space-cont"`, `"normal-line"`) which is better. Carried from RC10 m-9 / RC11 m-12.

**F-3** `test_planstate_aggregation.py:102-197` — independence — Minor
`test_git_metadata_helpers` tests both the positive path (3 commits after session.md anchor = count 3) and the negative path (no session.md in history = count 0) in one test function. Creates a second repo at line 161. Splitting would improve failure diagnosis. Carried from RC11 m-13.

**F-4** `test_session_handoff.py:217-248` — independence — Minor
`test_write_completed_with_accumulated_content` (line 217) and `test_write_completed_overwrites_not_appends` (line 234) exercise the same code path (`write_completed` which delegates to `_write_completed_section`). Both verify replacement behavior; the first from a state with accumulated content, the second via two sequential calls. Not vacuous (different initial states), but near-redundant. Carried from RC11 m-14.

**F-5** `test_session_commit_pipeline.py:157-212` — conformance — Minor
Submodule setup uses `create_submodule_origin` + `add_submodule` from pytest_helpers.py. Meanwhile `test_session_commit_pipeline_ext.py:22-35` defines its own `_init_repo_with_submodule` wrapper around the same helpers. Inconsistent patterns for the same operation. Carried from RC11 m-15.

**F-6** `test_session_handoff_committed.py:88-116` — functional correctness — Minor
`test_write_completed_appends_when_prior_uncommitted` simulates the "append" mode by replacing old content with new before calling `write_completed`. The test verifies both prior and new content present. However, the simulation replaces `"- Old task A\n- Old task B\n"` with `"- First handoff.\n"` — this means HEAD still has `"- Old task A\n- Old task B\n"` while working copy has `"- First handoff.\n"`. The detection logic (`_detect_write_mode`) checks whether committed lines are a subset of current lines. Since committed lines (`Old task A`, `Old task B`) are NOT a subset of current lines (`First handoff.`), and committed != current, mode correctly resolves to "append". Test logic is correct, but the comment at line 99-100 ("Simulate prior uncommitted handoff: replace old content with new (removing old, writing new)") is misleading — it describes the agent behavior but not the mode detection rationale.

**F-7** `test_session_handoff_committed.py:122-151` — functional correctness — Minor
`test_write_completed_autostrip_when_old_preserved` tests the autostrip path. The source implementation at `pipeline.py:217` has `except ValueError, subprocess.CalledProcessError:` which in Python 3.14 (PEP 758) catches both exceptions. The test correctly exercises the non-error path (successful `git show`), so this except clause is not tested. The autostrip error fallback path (`_find_repo_root` raising `ValueError` or `git show` failing) has no dedicated test.

**F-8** `test_session_handoff_cli.py:291-315` — coverage — Minor
`test_handoff_resume_from_diagnostics_skips_writes` tests resume from `step_reached="diagnostics"`. There is no test for resume from `step_reached="write_session"` — this would exercise the path where writes are performed during resume (state exists but writes haven't completed). The fresh-handoff test (`test_session_handoff_cli_fresh`) covers the write path from stdin, but resume-from-write_session is a distinct entry point (state file exists, stdin empty, writes still needed).

**F-9** `test_session_handoff.py:217-231` — excess — Minor
`test_write_completed_with_accumulated_content` at line 217 tests `write_completed` on a file where the committed content has been appended to (adding `"- New task done.\n"` after `"- Old task B\n"`). This is actually testing simple overwrite behavior — the function always replaces the section regardless of accumulated content. The H-2 committed-detection tests in `test_session_handoff_committed.py` now properly exercise the detection-aware paths. This test is a residual from pre-H-2 implementation; it still passes and verifies a valid invariant (section replacement works), but overlaps with the new committed detection tests.

**F-10** `test_session_handoff_committed.py` — coverage — Minor
The three H-2 mode tests initialize repos but all use `init_repo_minimal` which requires explicit `git add` + `git commit` via `_commit_session`. The autostrip test (line 122) modifies the file after committing, creating a diff. However, none of the three tests assert which mode was actually selected by `_detect_write_mode`. They verify the final output (correct content in file), which is the important thing, but a mode-detection unit test (testing `_detect_write_mode` directly for each case) would strengthen coverage and catch silent mode misclassification.

## Summary

| Severity | Count |
|----------|-------|
| Critical | 0 |
| Major | 0 |
| Minor | 10 |

**RC11 fix verification:**
- m-11 (SESSION_FIXTURE ordering): NOT FIXED — still defined after first usage (F-1)
- m-12 (assertion strings): PARTIAL — some tests improved, others unchanged (F-2)
- m-13 (conflated paths): NOT FIXED (F-3)
- m-14 (same code path): NOT FIXED (F-4)
- m-15 (inconsistent helpers): NOT FIXED (F-5)
- Corrector dead mock removal: VERIFIED — no dead mocks remain

**New findings (not carried):**
- F-6: Misleading comment in append mode test
- F-7: Autostrip error fallback path untested
- F-8: No test for resume from `step_reached="write_session"`
- F-9: Pre-H-2 accumulated content test now redundant with committed detection tests
- F-10: No direct `_detect_write_mode` unit test

**Trend:** RC11 0C/0M/5m → RC12 0C/0M/10m. Minor count increased because: 5 carried (m-11 through m-15 not addressed as stated), 5 new from fresh full-scope review of newly added test_session_handoff_committed.py (3 findings) and gaps in H-2/H-4 test coverage (2 findings).

| Axis | Status |
|------|--------|
| Conformance | 3 minors (F-1 fixture ordering, F-5 helper inconsistency, F-6 misleading comment) |
| Functional correctness | Pass — all tests verify correct behavior |
| Functional completeness | 2 minors (F-7 untested error path, F-8 missing resume-from-write_session) |
| Vacuity | Pass — no ceremonial tests |
| Excess | 1 minor (F-9 pre-H-2 test now redundant) |
| Specificity | 1 minor (F-2 generic assertion strings) |
| Coverage | Pass — all 28 design scenarios covered (see checklist) |
| Independence | 2 minors (F-3 conflated scenarios, F-4 near-redundant tests) |
