# Vet Review: Cycle 0.6 — clean-tree subcommand

**Scope**: clean-tree subcommand implementation (parent + submodule status check)
**Date**: 2026-02-10
**Mode**: review + fix

## Summary

Cycle 0.6 implements the clean-tree subcommand for validating repository cleanliness. The implementation correctly executes `git status --porcelain` for both parent and submodule, exits silently on clean state, and reports dirty files otherwise. The test verifies behavior with real git repos and submodule setup.

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

None.

### Major Issues

1. **Session file filtering not implemented**
   - Location: cli.py:99-103
   - Problem: FR requirement states session files should be excluded (agents/session.md, agents/jobs.md, agents/learnings.md), but implementation concatenates raw status output without filtering
   - Suggestion: Add filtering logic after capturing status, before checking if combined is empty
   - **Status**: UNFIXABLE — Cycle scope explicitly excludes session file filtering (OUT: "Session file filtering (next cycle)")

### Minor Issues

None.

## Fixes Applied

None (UNFIXABLE issue is out of scope for this cycle).

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| Execute git status for parent and submodule | Satisfied | cli.py:83-97 |
| Exit 0 silently when clean | Satisfied | cli.py:101-103 (implicit: no output, no SystemExit) |
| Exit 1 with dirty files when dirty | Satisfied | cli.py:102-103 |
| Test with real git repos | Satisfied | test_worktree_cli.py:111-186 |

**Gaps**: Session file filtering (documented as next cycle, not a gap).

---

## Positive Observations

- Integration test correctly creates real git repos with submodule (lines 117-178)
- Submodule status check handles missing submodule gracefully (check=False, returncode check)
- Test verifies clean state assertion (exit 0, empty output)
- Docstring accurately describes behavior and session file exclusion intent
- Uses subprocess.run with check=True for parent repo (fail-fast on git errors)

## Recommendations

- When implementing session file filtering in Cycle 0.7, use line-by-line filtering on porcelain output (regex match on file paths) rather than pre-filtering in git command
- Consider adding a test case for dirty submodule state (current test only verifies clean state)
