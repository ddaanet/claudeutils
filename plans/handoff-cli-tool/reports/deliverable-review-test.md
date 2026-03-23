# Test Deliverable Review: handoff-cli-tool (RC3)

Reviewed 19 test files (+3284 lines) against `plans/handoff-cli-tool/outline.md`.

## Critical

None.

## Major

### M1: H-2 committed detection modes not tested through git diff

- **File:** `tests/test_session_handoff.py:187-248`
- **Axis:** Coverage
- **Description:** The outline (H-2) specifies three committed-detection behaviors keyed on `git diff HEAD -- agents/session.md`: overwrite (no diff), append (old removed, new present), and auto-strip (old preserved with additions). All four `write_completed` tests operate on bare files without a git repo or HEAD reference, so committed detection never fires. The implementation collapsed all modes to overwrite (per the impl comment at `pipeline.py:85-96`), which is a valid simplification, but the tests don't verify the _precondition_ that makes this safe: that `write_completed` produces correct results when the file state differs from HEAD. A test that commits session.md, modifies it, then calls `write_completed` would confirm the overwrite-is-always-correct invariant against real git state.

### M2: Blockers never passed to `detect_parallel` in status CLI

- **File:** `tests/test_session_status.py:192-198`, `src/claudeutils/session/status/cli.py:98`
- **Axis:** Coverage
- **Description:** The outline (ST-1) specifies parallel group detection considers logical dependencies from Blockers/Gotchas. The test `test_detect_parallel_blocker_excludes` correctly tests the `detect_parallel` function with blockers. However, the status CLI hardcodes `detect_parallel(data.in_tree_tasks, [])` -- blockers are never extracted from session.md and never passed to the renderer. No integration-level test covers the full path where blockers in session.md suppress parallelism. The unit test gives false confidence that blocker-based suppression works end-to-end.

### M3: `_init_repo` duplicated across 6 test files instead of using shared helper

- **File:** `tests/test_session_commit.py:163`, `tests/test_session_commit_cli.py:16`, `tests/test_session_commit_pipeline.py:15`, `tests/test_session_commit_pipeline_ext.py:15`, `tests/test_session_commit_validation.py:15`, `tests/test_session_handoff.py:154`, `tests/test_session_handoff_cli.py:16`, `tests/test_session_integration.py:14`
- **Axis:** Excess / Independence
- **Description:** Eight test files define local `_init_repo` functions that duplicate the shared `tests/pytest_helpers.init_repo_at`. `test_commit_pipeline_errors.py` already uses the shared helper, proving the pattern works. The local copies have slightly varying implementations (some write README.md, some don't; some use `cwd=`, some use `-C`). This is not a functional defect but a maintenance risk -- divergent repo initialization can mask test fragility or produce inconsistent test environments.

### M4: `test_session_status_cli` depends on undeclared fixture `SESSION_FIXTURE`

- **File:** `tests/test_session_status.py:204-218`
- **Axis:** Functional correctness
- **Description:** `test_session_status_cli` references `SESSION_FIXTURE` at line 208, but `SESSION_FIXTURE` is defined at line 235, after the test function. Python allows this because module-level names are resolved at call time, not definition time. However, the fixture is distant from its consumer (27 lines after first use), making the test fragile to reordering and harder to read. The test also relies on a `plans/` directory existing via `list_plans()` -- if `list_plans(Path("plans"))` raises when the directory is missing, the test passes by accident (it doesn't create plans/).

### M5: `or`-disjunction assertions in commit pipeline tests

- **File:** `tests/test_session_commit_pipeline.py:65`, `tests/test_session_commit_pipeline.py:100`
- **Axis:** Specificity
- **Description:** Two assertions use `or` disjunction:
  - Line 65: `assert "foo" in result.output.lower() or "1 file" in result.output` -- passes if either condition holds, meaning the test cannot distinguish whether the output contains the committed file reference or just a file count.
  - Line 100: `assert "Precommit" in result.output or "failed" in result.output` -- similarly weak.
  These were noted in the prior round 2 review as pre-existing. They remain and weaken test specificity for the commit pipeline's core success and failure paths.

## Minor

### m1: `test_parse_commit_input` parametrized test asserts only one section per invocation

- **File:** `tests/test_session_commit.py:48-73`
- **Axis:** Vacuity
- **Description:** The parametrized test calls `parse_commit_input(COMMIT_INPUT_FIXTURE)` four times (once per section), parsing the full fixture each time but checking only one section. This means three-quarters of the parse result goes unverified per invocation. A single test asserting all four sections would be more direct. Not incorrect, but the parametrization pattern suggests four independent tests when they all share the same input and parse call.

### m2: Handoff CLI test asserts `"Git status"` string literal

- **File:** `tests/test_session_handoff_cli.py:106`
- **Axis:** Independence
- **Description:** The test asserts `"Git status" in result.output`. The actual output is `**Git status:**` (with markdown bold formatting). The assertion works due to substring match but couples to the specific formatting. If the format changes to e.g. `## Git Status` or `Git changes:`, the test breaks for a non-functional reason.

### m3: `test_handoff_then_status` integration test has no commit between handoff and status

- **File:** `tests/test_session_integration.py:60-93`
- **Axis:** Coverage
- **Description:** The outline (Phase 7) specifies end-to-end integration across subcommands. The test runs handoff then status, but skips `_commit`. The handoff-then-commit-then-status pipeline is the primary real-world flow. The test verifies handoff output feeds status input, but the commit step (the most complex pipeline) is absent from integration testing.

### m4: `test_session_status_missing_session` does not verify error message content

- **File:** `tests/test_session_status.py:221-232`
- **Axis:** Specificity
- **Description:** Asserts `"Error" in result.output` but doesn't check for the specific error text about the missing session file path. A more specific assertion would confirm the right error path was hit (SessionFileError vs some other error).

### m5: `test_format_strips_hints` doesn't verify multi-line hint removal

- **File:** `tests/test_session_commit_format.py:55-63`
- **Axis:** Coverage
- **Description:** Tests hint stripping with `hint:` prefix lines, but the outline also mentions stripping `advice` lines. No test covers git advice-prefixed output. If the implementation only strips `hint:` but not advice lines, this wouldn't be caught. (Implementation at `commit_pipeline.py:188` confirms only `hint:` is stripped, which may be sufficient, but the outline's mention of "git hint/advice lines" suggests both should be handled.)

### m6: `test_validate_files_amend` has implicit ordering dependency

- **File:** `tests/test_session_commit.py:223-255`
- **Axis:** Independence
- **Description:** The test creates file `src/bar.py`, commits it, then creates `other.py` and commits it separately. The second `validate_files(["src/bar.py"], amend=True)` call implicitly depends on `src/bar.py` being in the _previous_ HEAD commit (not the most recent), which is how `_head_files` via `diff-tree HEAD` works. But `diff-tree HEAD` returns files in the _latest_ commit only. The test passes because `other.py` is the latest commit and `bar.py` is no longer in HEAD's diff-tree. This is correct behavior but the test comment says "File not in HEAD and not dirty" without clarifying which HEAD commit is meant.

### m7: Worktree marker parsing tested in parser but `→ wt` rendering not explicitly verified

- **File:** `tests/test_session_status.py:73-83`
- **Axis:** Coverage
- **Description:** `test_render_section` checks `"→ my-slug"` appears in worktree output, but the `→ wt` marker rendering is only implicitly covered (the second task has `worktree_marker="wt"` but the assertion only checks `"Future work" in result`). An explicit check for `"→ wt"` in the output would confirm both marker types render correctly.

### m8: Modified worktree test files have minimal changes

- **File:** `tests/test_worktree_merge_errors.py` (+1/-1), `tests/test_worktree_rm_dirty.py` (+6/-5)
- **Axis:** Conformance
- **Description:** These files are listed in the review scope but contain only import-path changes (moving `_is_dirty`/`_is_submodule_dirty` from `claudeutils.worktree.utils` to `claudeutils.git`). The changes are mechanical consequences of the S-2 extraction. No new test logic. Verified correct.

## Summary

| Severity | Count |
|----------|-------|
| Critical | 0 |
| Major | 5 |
| Minor | 8 |

**Key gaps:**
- M1/M2: Design-specified behaviors (H-2 committed detection against real git state, ST-1 blocker extraction) have unit-level coverage but no integration test proving the full path works.
- M3: `_init_repo` duplication is a maintenance tax that should consolidate to the shared helper.
- M5: Or-disjunction assertions (carried forward from prior round) weaken specificity on core pipeline paths.

**Strengths:**
- Comprehensive coverage of the commit parser (C-3 validation, C-4 validation levels, C-5 amend semantics, submodule four-cell matrix).
- Good error propagation testing (pipeline errors, staging errors, submodule failures).
- Real git repos via `tmp_path` throughout (no pure mock-only tests pretending to be integration tests).
- Clean parametrized test structure in parser and render tests.
- Rework findings from round 2 (C#1, M#2, M#3, M#5, m-1 through m-6) all verified fixed.
