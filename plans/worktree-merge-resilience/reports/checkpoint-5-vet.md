# Vet Review: Phase 5 Checkpoint -- Exit Code Audit, stderr Migration, SKILL.md Update

**Scope**: Phase 5 deliverables: SKILL.md Mode C update, `err=True` removal in merge scope, test assertion updates, exit code classification audit
**Date**: 2026-02-18
**Mode**: review + fix

## Summary

Exit code classification is correct across all 12 SystemExit calls in merge.py. SKILL.md Mode C step 4 (exit code 3) is well-structured with clear resolution workflow. Three `err=True` residuals found in merge_state.py (part of the merge pipeline, extracted in Phase 3) that were missed during the D-8 stdout migration. One test assertion checking the wrong output stream (stderr instead of stdout) -- passed vacuously. Two SKILL.md references to "stderr" inconsistent with D-8 stdout-only contract.

**Overall Assessment**: Needs Minor Changes

## Issues Found

### Critical Issues

(none)

### Major Issues

1. **merge_state.py retains 3 `err=True` calls**
   - Location: `src/claudeutils/worktree/merge_state.py:85,96,135`
   - Problem: `_add_and_commit_files` and `_recover_untracked_file_collision` use `click.echo(..., err=True)`. These functions are part of the merge pipeline (called from `merge.py` Phase 3 via `_recover_untracked_file_collision`). D-8 requires all merge output to stdout.
   - Fix: Remove `err=True` from all three calls
   - **Status**: FIXED

### Minor Issues

1. **Test assertion checks stderr instead of stdout**
   - Location: `tests/test_worktree_merge_correctness.py:184`
   - Note: `capsys.readouterr().err` should be `.out` -- `_validate_merge_result` writes to stdout (no `err=True`). The assertion passes vacuously (stderr is empty) but tests the wrong stream. If a regression reintroduced `err=True`, this assertion would still pass.
   - **Status**: FIXED

2. **SKILL.md step 2 references "stdout/stderr"**
   - Location: `agent-core/skills/worktree/SKILL.md:90`
   - Note: After D-8 migration, all merge output goes to stdout. "stdout/stderr" is misleading for agents parsing output.
   - **Status**: FIXED

3. **SKILL.md step 6 references "stderr"**
   - Location: `agent-core/skills/worktree/SKILL.md:107`
   - Note: Says "followed by stderr" but exit code 2 messages also go to stdout after D-8. Inconsistent with steps 4-5 which correctly say "Read stdout."
   - **Status**: FIXED

## Fixes Applied

- `src/claudeutils/worktree/merge_state.py:85` -- removed `err=True` from `click.echo` in `_add_and_commit_files` (git add failure)
- `src/claudeutils/worktree/merge_state.py:96` -- removed `err=True` from `click.echo` in `_add_and_commit_files` (commit failure)
- `src/claudeutils/worktree/merge_state.py:135` -- removed `err=True` from `click.echo` in `_recover_untracked_file_collision` (retry failure)
- `tests/test_worktree_merge_correctness.py:184` -- changed `capsys.readouterr().err` to `.out`
- `agent-core/skills/worktree/SKILL.md:90` -- replaced "stdout/stderr" with stdout-only description
- `agent-core/skills/worktree/SKILL.md:107` -- replaced "stderr" with "Read stdout for error message"

## Exit Code Audit

All 12 SystemExit calls in merge.py classified per D-1 (1=error, 2=fatal, 3=conflict-pause):

| Location | Code | Context | Classification |
|----------|------|---------|----------------|
| merge.py:87 | 1 | Dirty tree | error -- correct |
| merge.py:102 | 1 | Dirty submodule | error -- correct |
| merge.py:115 | 2 | Branch not found | fatal -- correct |
| merge.py:210 | 1 | Untracked recovery failed | error -- correct |
| merge.py:220 | 1 | Merge failed post-recovery | error -- correct |
| merge.py:223 | 1 | Merge failed (other) | error -- correct |
| merge.py:238 | 3 | Source conflicts, merge paused | conflict-pause -- correct |
| merge.py:253 | 2 | Branch not fully merged | fatal -- correct |
| merge.py:294 | 2 | Merge state lost | fatal -- correct |
| merge.py:298 | 2 | Nothing to commit, unmerged | fatal -- correct |
| merge.py:314 | 1 | Precommit failed | error -- correct |
| merge.py:333 | 3 | Conflicts in routing | conflict-pause -- correct |

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| D-1: Exit codes 1/2/3 | Satisfied | All 12 calls audited, see table above |
| D-8: All output to stdout | Satisfied after fix | merge.py clean; merge_state.py had 3 residuals (fixed) |
| C-1: SKILL.md Mode C update | Satisfied after fix | Step 4 (exit 3) present with resolution workflow; stderr refs fixed |
| NFR-1: Exit code 3 for conflicts | Satisfied | Lines 238, 333 |

## Positive Observations

- Exit code classification is precise: 1 for recoverable errors (dirty tree, precommit), 2 for fatal (branch missing, state corruption), 3 for conflict-pause
- SKILL.md step 4 resolution workflow is well-structured with clear substeps
- Merge idempotency documented in both SKILL.md and code
- cli.py merge handler already correct (no `err=True`)
