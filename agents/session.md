# Session Handoff: 2026-02-23

**Status:** Design triaged and outline validated for worktree error output fix. Ready for `/runbook`.

## Completed This Session

**Design triage:**
- Discovered root cause of "duplicated traceback": Bash tool error envelope repeats stderr on non-zero exit — confirmed with isolated test
- Scope expanded from `derive_slug` fix to full `_worktree` stderr→stdout migration per cli.md "When CLI Commands Are LLM-Native" convention
- Found `merge.py`/`merge_state.py`/`resolve.py` already use stdout; only `cli.py` has `err=True` (8 error sites, 4 warning sites)
- Outline validated: `plans/worktree-error-output/outline.md`

## Pending Tasks

- [ ] **Worktree new error formatting** — `/runbook plans/worktree-error-output/outline.md` | sonnet
  - Scope: drop `err=True` from 12 sites in cli.py, add `_fail()` helper, catch `derive_slug` ValueError in `new()`
  - cli.md decisions pre-loaded: LLM-native convention, error exit code consolidation, error handling layers

## Next Steps

Run `/runbook` against the outline. TDD phases for `_fail()` helper and ValueError catch; general phase for `err=True` removal (mechanical substitution).
