# Review: Cycle 4.7 CLI Tests — test_session_handoff_cli.py

**Scope**: `tests/test_session_handoff_cli.py` — 3 CLI tests for `_handoff` command
**Date**: 2026-03-20
**Mode**: review + fix

## Summary

Three CLI tests cover the `handoff_cmd` fresh path, resume path, and no-input error path. The tests invoke the real `cli` group via CliRunner with `CLAUDEUTILS_SESSION_FILE` injection and monkeypatching of `_run_precommit`. Core behavioral coverage is present but two issues weaken the RED signal: the fresh test does not assert state-file cleanup, and the resume test does not verify the state file is cleared after a successful resume. One minor issue: helper duplication from the parent test file (`_init_repo`, `_commit_session`) is acceptable as-is (no conftest consolidation in scope), but the docstrings on those helpers are now mismatched vs the parent file's docstrings.

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

None.

### Major Issues

1. **Fresh test does not assert state-file cleanup**
   - Location: `tests/test_session_handoff_cli.py:85-111` (`test_session_handoff_cli_fresh`)
   - Problem: `clear_state()` is the last meaningful operation in a successful pipeline. If it is absent or broken, the next invocation will be misrouted to the resume path. The test asserts session.md content and output but never verifies the state file does not exist after the command completes. This makes the test fail to catch a broken `clear_state()` call.
   - Fix: Assert `(tmp_path / "tmp" / ".handoff-state.json").does_not_exist()` after the successful fresh handoff.
   - **Status**: FIXED

2. **Resume test does not assert state-file cleared after success**
   - Location: `tests/test_session_handoff_cli.py:114-138` (`test_session_handoff_cli_resume`)
   - Problem: The test writes a state file, invokes the command, asserts session.md is updated, but never checks the state file was cleared. A resume path that succeeds must clean up its state file or the next invocation will spuriously resume again. The behavior is untested.
   - Fix: Assert the state file does not exist after exit_code 0.
   - **Status**: FIXED

### Minor Issues

1. **Error assertion in no-stdin-no-state test is under-specified**
   - Location: `tests/test_session_handoff_cli.py:156-157`
   - Note: `assert "Error" in result.output` accepts any string containing "Error" including Python tracebacks. The design spec (S-3) requires output in `**Header:** content` format. A more specific assertion locks in the contract.
   - **Status**: FIXED

## Fixes Applied

- `tests/test_session_handoff_cli.py:111` — Added assertion that state file is absent after successful fresh handoff
- `tests/test_session_handoff_cli.py:138` — Added assertion that state file is absent after successful resume
- `tests/test_session_handoff_cli.py:157` — Tightened error assertion to `"**Error:**"` to match S-3 output format contract

## Positive Observations

- CliRunner invocation against the real `cli` group (not the bare command) validates actual registration — the most common wiring failure is missed.
- `CLAUDEUTILS_SESSION_FILE` env-var injection is the correct approach: avoids hardcoding `agents/session.md` in test infrastructure and matches the production path-resolution pattern in `handoff_cmd`.
- `_run_precommit` is monkeypatched at the module level (`handoff_cli_mod._run_precommit`), which is the patchable seam the implementation was designed for — correct coupling.
- `_setup_cli_repo` consolidates the three-step setup (mkdir, write, init+commit) into a single call per test — good fixture discipline.
- `save_state` is called directly in the resume test rather than through the CLI, which correctly isolates the resume behavior from the fresh path.
- No-input test correctly skips `_run_precommit` monkeypatching — the error path must exit before reaching precommit.
