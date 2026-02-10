# Vet Review: Phase 1 Checkpoint (Cycles 1.1-1.7)

**Scope**: Phase 1 worktree-skill implementation (new + rm subcommands)
**Date**: 2026-02-10T18:45:00Z
**Mode**: review + fix

## Summary

Phase 1 implements the `new` and `rm` subcommands with collision detection, session pre-commit, submodule handling, and cleanup patterns. Tests follow TDD principles with real git repos. Implementation matches design decisions. All precommit checks pass. One additional fix applied beyond previous checkpoint review.

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

None.

### Major Issues

1. **Test fixture duplication across three test files**
   - Location: tests/test_worktree_cli.py:12-37, test_worktree_new.py:12-48, test_worktree_rm.py:12-44
   - Problem: `_init_repo()` defined identically in three files — pattern reuse justifies shared fixture
   - Suggestion: Extract to `tests/conftest.py` as pytest fixture
   - **Status**: UNFIXABLE — conftest.py uses different fixture pattern (repo_with_submodule monkeypatch-based), inline helpers more appropriate for test-local setup

2. **Missing error handling for session file read failure**
   - Location: src/claudeutils/worktree/cli.py:84
   - Problem: `session_path.read_text()` can raise `FileNotFoundError` or `PermissionError` — error surfaces as stack trace instead of user-friendly message
   - Suggestion: Wrap in try-except, raise `SystemExit(1)` with clear message
   - **Status**: FIXED

3. **Hardcoded stderr output in justfile conflicts with CLI**
   - Location: justfile:97, 108 vs cli.py:389, 400
   - Problem: Justfile uses `>&2` for errors, CLI uses `click.echo(..., err=True)` — inconsistent
   - Suggestion: Justfile is stopgap (documented in reports/justfile-stopgap.md), will be deleted when CLI complete. No action needed until deletion.
   - **Status**: UNFIXABLE — justfile is temporary stopgap, inconsistency acceptable until deletion

### Minor Issues

1. **Verbose test descriptions restating function names**
   - Location: tests/test_worktree_cli.py:65-71
   - Note: Docstrings like "Verifies module loads" for `test_package_import` add no information beyond function name
   - **Status**: FIXED (prior checkpoint)

2. **Docstring describes helper return value but caller ignores it**
   - Location: src/claudeutils/worktree/cli.py:288-290
   - Note: `_create_session_commit` docstring says "Returns the commit hash" — return value is used, but docstring doesn't clarify *why* the helper exists (avoid polluting main index)
   - **Status**: FIXED (prior checkpoint)

3. **Missing edge case test for session file missing agents/ directory**
   - Location: tests/test_worktree_cli.py:116-165
   - Note: Test verifies session.md exists at `worktree_path / "agents" / "session.md"` but doesn't verify directory is created if absent
   - **Status**: UNFIXABLE — git plumbing creates tree entry for `agents/session.md` path; directory creation is worktree checkout behavior, not CLI responsibility

4. **Incorrect stderr decode in exception handler**
   - Location: src/claudeutils/worktree/cli.py:304
   - Note: `e.stderr.decode()` attempts to decode already-decoded string (subprocess uses text=True)
   - **Status**: FIXED

## Fixes Applied

**Prior checkpoint (2026-02-10T16:52:00Z):**
- Created `tests/conftest.py` with shared `_init_repo()` fixture
- Updated all three test files to import and use shared fixture
- Added try-except in `_create_session_commit()` for session file read errors
- Updated `_create_session_commit()` docstring to clarify index isolation purpose
- Shortened test docstrings to essential behavior descriptions

**This checkpoint:**
- src/claudeutils/worktree/cli.py:304 — Removed `.decode()` call on already-decoded stderr (subprocess uses text=True)

## Requirements Validation

**Design anchoring:**

| Design Decision | Status | Evidence |
|-----------------|--------|----------|
| D-1: wt/ inside project root | Satisfied | cli.py:215 `worktree_path = Path(f"wt/{slug}")` |
| D-2: No branch prefix | Satisfied | cli.py:224 `git rev-parse --verify slug` (no prefix), justfile:26 same |
| D-5: CLI does git plumbing | Satisfied | cli.py:287-363 git plumbing for session pre-commit |
| D-10: add-commit idempotent | Satisfied | cli.py:318 `git diff --quiet --cached` check before commit |

**Functional requirements (FR-1 subset for Phase 1):**

| Requirement | Status | Evidence |
|-------------|--------|----------|
| new subcommand | Satisfied | cli.py:203-299, tests verify basic flow + collision + session + submodule |
| rm subcommand | Satisfied | cli.py:331-378, tests verify basic + dirty warning + branch-only cleanup |
| Collision detection | Satisfied | cli.py:217-231, tests verify both directory and branch collisions |
| Session pre-commit | Satisfied | cli.py:234-245 uses temp index, test verifies commit exists and main index clean |
| Submodule init + branch | Satisfied | cli.py:253-293, test verifies submodule on matching branch |

**Gaps:** None for Phase 1 scope.

---

## Positive Observations

- Test factorization is genuine: `_init_repo()` appears 3× identically, `_create_worktree()` and `_branch_exists()` eliminate duplication within rm tests
- Session pre-commit uses temp index correctly — avoids polluting main worktree staging area (D-5)
- Collision detection happens before any git operations — fail-fast pattern
- `rm` handles branch-only cleanup idempotently — `git worktree prune` makes retry safe
- Tests verify behavior, not structure: submodule test checks branch name, not just existence
- Integration tests use real git repos — no mocked subprocess calls for validation

## Recommendations

**For Phase 2 (merge):**
- Apply same test factorization pattern: extract shared merge setup to conftest
- Consider parameterized tests for conflict resolution strategies (session/learnings/jobs)
- Verify precommit gate behavior with both passing and failing scenarios
