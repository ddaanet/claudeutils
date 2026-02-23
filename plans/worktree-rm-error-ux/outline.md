# Worktree rm Error UX

## Approach

Two independent changes to `claudeutils _worktree rm`:

1. **Remove `--confirm` gate** — The `--confirm` flag was a safety mechanism to ensure callers use the worktree skill. It's unnecessary friction — the skill already invokes the CLI, and direct CLI invocation should be allowed.

2. **Git error → clean message** — When git operations fail during `rm`, the `CalledProcessError` bubbles up as an unhandled exception showing a Python traceback. Wrap in try/except and print the git error message, same pattern as the `merge` command.

## Key Decisions

- D-1: Delete `_check_confirm()` function and `--confirm` Click option entirely. Don't deprecate — remove.
- D-2: Wrap `rm()` body in `try: ... except CalledProcessError as e: _fail(f"git error: {stderr or e}")` — matches merge command pattern.
- D-3: Delete `test_rm_refuses_without_confirm` test entirely (tests behavior being removed).
- D-4: Remove `--confirm` from all 33 test invocations across 7 files.

## Scope

**IN:** `cli.py` (source), 7 test files (mechanical `--confirm` removal + 1 test deletion + 1 new error handling test)

**OUT:** Skill file changes (skill doesn't pass `--confirm`), merge command, git_ops module

## Affected Files

Source:
- `src/claudeutils/worktree/cli.py` — delete `_check_confirm`, remove `--confirm` option, add try/except in `rm()`

Tests (mechanical `--confirm` removal):
- `tests/test_worktree_rm.py` — 7 occurrences + delete `test_rm_refuses_without_confirm`
- `tests/test_worktree_rm_guard.py` — 9 occurrences
- `tests/test_worktree_commands.py` — 9 occurrences
- `tests/test_worktree_rm_dirty.py` — 3 occurrences
- `tests/test_worktree_rm_amend.py` — 1 occurrence
- `tests/test_worktree_submodule.py` — 2 occurrences
- `tests/test_worktree_session_automation.py` — 2 occurrences

New test:
- `tests/test_worktree_rm.py` — test that git failure during rm shows error message, not traceback

## Phase Typing

- Phase 1 (TDD): New error handling behavior — write test for git error output first, then implement
- Phase 2 (general): Mechanical removal of `--confirm` across source + tests
