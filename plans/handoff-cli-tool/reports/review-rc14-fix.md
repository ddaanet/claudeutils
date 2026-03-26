# Review: RC14 Fix — handoff-cli-tool

**Scope**: Uncommitted fixes for RC14 findings (7 active minors: 2 code clarity, 5 test style/coverage)
**Date**: 2026-03-26
**Mode**: review + fix

## Summary

Eight files modified to address RC14 minors: `cwd` param added to `_git()`, `_git_output` removed from `commit_gate.py`, `_strip_hints` logic clarified, three submodule helper standardizations, two assertion loosenings, one vacuous test corrected, and one missing state-clear assertion added. All seven RC14 active findings are addressed. The changes are correct and non-functional — no behavior changes in production code beyond consolidating `_git_output` into `_git`.

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

None.

### Major Issues

None.

### Minor Issues

**m-1** `commit_pipeline.py:203-211` — logic clarity — After the fix, `_strip_hints` sets `prev_was_hint = True` unconditionally on every indented-after-hint line, but the flag is only checked by the outer `elif` condition which requires `prev_was_hint`. The `else` branch (non-hint, non-indented-after-hint) sets `prev_was_hint = False`, which is correct. However, when `is_continuation=True`, the line is filtered but `prev_was_hint` stays `True` via the implicit fall-through — this is correct behavior. The simplified version is functionally equivalent to what it replaced. Logic is now clear. No issue.

**m-2** `commit_gate.py` — the `import subprocess` statement at line 5 is no longer needed (the only subprocess call was in the removed `_git_output` function; `_dirty_files` still uses `subprocess.run` directly). The import is still required.
- **Status**: OUT-OF-SCOPE — `subprocess` is still used by `_dirty_files` at line 37. No issue.

**m-3** `test_session_status.py:129-138` — The loosened assertions now test key fragments without asserting exact string format. The `cmd_line` assertion `assert "`/design plans/w/brief.md`" in cmd_line` verifies backtick wrapping is present but does not verify indentation. The design spec (outline.md STATUS output format) shows `  \`<command>\`` with two-space indent. Loosening to key-fragment form is appropriate per RC14 m-5 intent — format changes should not break tests when behavior is preserved. No functional regression risk since the arrow_line content is already validated by four separate assertions.
- **Status**: OUT-OF-SCOPE — loosening was the explicit intent of RC14 m-5.

**m-4** `test_session_handoff_cli.py:354-358` — The state-clear assertion added at the end of `test_handoff_resume_from_write_session` is correct. It verifies the RC14 m-7 coverage gap (resume path clears state file). The path `tmp_path / "tmp" / ".handoff-state.json"` matches the H-4 spec location. No issue.
- **Status**: OUT-OF-SCOPE — correctly implemented.

## Fixes Applied

No fixes were applied — all RC14 active minors were correctly addressed by the incoming changes. All issues found during analysis were either out of scope, correctly implemented, or not real issues.

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| S-2: `_git()` extraction | Satisfied | `cwd` param added; `_git_output` removed; `_head_files` uses `_git(check=False, cwd=cwd)` |
| RC14 m-1 (`_strip_hints` clarity) | Satisfied | Dead `prev_was_hint = True` branches removed; `is_continuation` named bool; logic path clear |
| RC14 m-2 (`_git_output` duplication) | Satisfied | `_git_output` deleted; `_head_files` migrated to `_git(check=False, cwd=cwd)` |
| RC14 m-3 (submodule helper conformance) | Satisfied | `test_git_cli.py` and `test_session_handoff_cli.py` both use `create_submodule_origin` + `add_submodule` |
| RC14 m-4 (orphan-message assertion) | Satisfied | Exact prose → key fragments (`"no changes found"`, `"agent-core"`) |
| RC14 m-5 (arrow-line assertion) | Satisfied | Exact equality → four fragment checks + separate cmd_line fragment check |
| RC14 m-6 (vacuous test) | Satisfied | `test_write_completed_with_accumulated_content` now commits session.md, exercises autostrip path |
| RC14 m-7 (resume state clearing) | Satisfied | `assert not (tmp_path / "tmp" / ".handoff-state.json").exists()` added to `test_handoff_resume_from_write_session` |

## Cross-Cutting Verification

**`_git_output` removal:** `commit_gate.py` previously had a TODO acknowledging duplication with `git.py:_git()`. The fix adds `cwd` to `_git()` and replaces the local helper. The `_head_files` caller passes `check=False` correctly — `_git_output` had `check=False` as its default, and the replacement `_git(..., check=False)` preserves this. The `import subprocess` in `commit_gate.py` is still required by `_dirty_files`.

**`_strip_hints` simplification:** Pre-fix had two branches, both setting `prev_was_hint = True`, with the distinction only in whether `result.append(line)` was called. Post-fix uses named boolean `is_continuation` and single conditional append. Behavioral equivalence confirmed: both branches of the old code set `prev_was_hint = True`; the new code does the same via implicit continuation (flag not reset in the `elif` branch). The `else` branch still resets to `False` on non-hint, non-indented lines.

**Submodule helper standardization:** `test_git_cli.py` replaced `_add_submodule_gitlink` (git plumbing approach, 20 subprocess calls) with `_add_submodule` wrapper around canonical `create_submodule_origin` + `add_submodule`. `test_session_handoff_cli.py:test_handoff_shows_submodule_changes` replaced manual 20-call setup (including `GIT_CONFIG_COUNT` env var workaround and per-submodule git config) with two-call canonical setup. Both now match the pattern in `test_session_commit_pipeline_ext.py`. RC14 m-3 resolved.

**Vacuous test fix:** `test_write_completed_with_accumulated_content` previously wrote accumulated content without a committed baseline, so `_detect_write_mode` returned `"overwrite"` (no HEAD diff), not `"autostrip"`. The fix adds `init_repo_at`, writes and commits `SESSION_WITH_COMPLETED`, then accumulates new content before calling `write_completed`. This exercises the autostrip path. The assertions verify autostrip behavior: new content kept, committed content stripped. Fix is correct.

## Positive Observations

- `_git()` signature change is backward-compatible (keyword-only `cwd` with `None` default).
- The `_add_submodule_gitlink` removal eliminates the git plumbing workaround that could break on git version differences. The canonical helper handles the `protocol.file.allow` env var internally.
- Test docstring update on `test_write_completed_with_accumulated_content` accurately describes the new behavior ("Autostrip removes committed content, keeps new additions").
- State-clear assertion in `test_handoff_resume_from_write_session` added at natural position (end of test, after behavior verification).
