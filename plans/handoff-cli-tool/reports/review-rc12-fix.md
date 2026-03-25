# Review: RC12 Critical Fix — CommitInputError handler in commit_cmd

**Scope**: `src/claudeutils/session/cli.py:33-34` (added except clause) + `tests/test_session_commit_cli.py::test_commit_cli_submodule_missing_message_exits_2` (new test)
**Date**: 2026-03-25
**Mode**: review + fix

## Summary

The fix adds a `CommitInputError` catch clause to the `commit_pipeline()` try-block in `commit_cmd`, closing the gap where pipeline-raised `CommitInputError` (submodule message missing, commit message absent) previously propagated uncaught as an unhandled exception. The new test verifies the exact regression path: submodule files present, `## Submodule` section absent, exits 2 with `**Error:**` prefix. Both changes are correct and complete.

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

None.

### Major Issues

None.

### Minor Issues

None.

## Fixes Applied

None required — implementation is correct.

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| S-3: All output to stdout as structured markdown | Satisfied | `_fail()` uses `click.echo(msg)` → stdout. Error prefix `**Error:** {e}` is structured markdown. |
| S-3: Exit code 2 for input validation errors | Satisfied | `_fail(f"**Error:** {e}", code=2)` — matches existing `CommitInputError` handler on line 27. |
| S-3: `**Error:**` format | Satisfied | `f"**Error:** {e}"` — consistent with line 27 and outline.md error taxonomy. |
| C-2: Submodule files without `## Submodule <path>` section → stop error | Satisfied | `_validate_inputs()` raises `CommitInputError("Files under {path}/ but no ## Submodule {path} section")` — caught by new handler, exits 2 with `**Error:**` prefix. |
| Recall: context at failure site, display at top level, never both | Satisfied | `_validate_inputs()` raises with context embedded in exception message. CLI layer calls `_fail()` — display only at top level. No double-print. |

---

## Positive Observations

- **Symmetry with existing handler**: The new clause at line 33-34 mirrors the `CommitInputError` handler from `parse_commit_input` (line 26-27) exactly — same format string, same exit code. No inconsistency introduced.
- **CleanFileError not double-wrapped**: `str(CleanFileError)` already embeds `**Error:**` (built in `_build_clean_file_error_msg`), so `_fail(str(e), code=2)` is correct. The new handler uses `f"**Error:** {e}"` because `CommitInputError` messages are plain text — no double-wrapping.
- **Test exercises real failure path**: Uses a real git repo with a real submodule rather than mocking `commit_pipeline`. The submodule file is untracked (not committed), ensuring file validation passes and `CommitInputError` from the missing submodule section is the terminal error — not `CleanFileError` from a false validation path.
- **Test assertions are tight**: Both `"**Error:**"` and `"no ## Submodule"` are verified independently, covering format (S-3) and content (C-2) separately.
