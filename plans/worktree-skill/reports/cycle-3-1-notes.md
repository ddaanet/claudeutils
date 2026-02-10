# Cycle 3.1: Phase 1 pre-checks (clean tree gate)

**Execution Date:** 2026-02-10

## Status: STOP_CONDITION

### RED Phase
- Test name: `test_merge_dirty_tree_gate_rejects_source_changes`
- Expected: Exit 1 with dirty tree error
- Actual: Exit 2 (command not found) before implementation
- Result: **FAIL as expected** ✓

### GREEN Phase
- Implementation: `merge` subcommand with Phase 1 pre-checks
- Location: `src/claudeutils/worktree/cli.py` lines 416-443
- Changes:
  - Extracted `_get_dirty_files()` helper (lines 78-115)
  - Refactored `_check_clean_tree()` helper (lines 118-136)
  - Implemented `merge()` subcommand (lines 416-443)
  - Updated `clean_tree()` to use extracted helper (lines 225-232)
- Behavior:
  - Phase 1: Clean tree validation (source files only, session files exempt)
  - Phase 1: Branch validation (verify slug branch exists)
  - Phase 1: Worktree directory check (warn if missing, continue)
  - Early return on pre-check failures
- Test results: **2/2 tests PASS** ✓
- Regression check: 765/766 passed, 1 xfail (known bug) ✓

### REFACTOR Phase
- Formatting: `just lint` passed ✓
- Precommit validation: **FAILED** ❌
  - Violation: `src/claudeutils/worktree/cli.py`: 443 lines (exceeds 400 limit)
  - Root cause: Extracted helpers (40 lines) + merge command (27 lines) exceed limit
  - Code quality: Extraction is necessary refactoring (DRY principle), not architectural debt

### Architecture Analysis
- Module structure: All worktree CLI in single file (as designed)
- File size: 400 → 443 lines
- Change breakdown: 93 insertions, 35 deletions (net +58)
- Complexity: Simple extraction + minimal Phase 1 implementation
- Natural boundary: No obvious split point without architectural redesign

### Stop Condition
- Type: **Architectural refactoring required**
- Issue: Line limit violation (443 > 400) is hard requirement
- Action: Escalate to sonnet for module organization decision
- Constraint: Design specified single cli.py module, but line limit may require split (cli.py vs subcommands)

## Files Modified
- `src/claudeutils/worktree/cli.py` — Added merge command + extracted helpers
- `tests/test_worktree_clean_tree.py` — Added 2 behavioral verification tests

## Commit Hash
- WIP: d48d309 "WIP: Cycle 3.1 merge clean tree gate implementation"

## Decision Made
- Verified tests pass GREEN phase ✓
- Verified no regressions (765/766 tests pass) ✓
- Escalation needed for architectural module organization

## Next Steps
1. Escalate to sonnet for architectural refactoring decision
2. Options:
   - Split cli.py into subcommand modules
   - Raise line limit for worktree module
   - Extract subcommands to separate file (e.g., commands.py)
3. Resume after architectural guidance received
