# Session: Worktree — Worktree merge resilience

**Status:** Design complete, ready for planning.

## Completed This Session

- Designed worktree merge resilience (outline as design artifact, sufficiency gate passed)
- 8 key decisions: state machine entry (D-5), exit code 3 (D-1), submodule pass-through (D-2), merge preservation (D-3), git-add for untracked (D-4), stdout unification (D-8), no-data-loss invariant (D-7), non-interactive compatibility (D-8)
- Outline reviewed by outline-review-agent (added D-7, D-8 for requirements traceability)
- User discussion refined D-4 (content comparison → `git add` + retry) and D-8 (stderr → all stdout)

## Pending Tasks

- [ ] **Worktree merge resilience** — `/runbook plans/worktree-merge-resilience/outline.md` | sonnet
  - Plan: worktree-merge-resilience | Status: designed
  - 5 FRs, 5 TDD phases + 1 general phase
  - Outline serves as design (no separate design.md)

## Blockers / Gotchas

- **Never run `git merge` without sandbox bypass** — partial checkout + sandbox failure leaves orphaned files
- Existing tests assert abort behavior (merge --abort + clean -fd) — tests need updating when behavior changes

## Reference Files

- `plans/worktree-merge-resilience/outline.md` — design (8 decisions, 5 phases)
- `plans/worktree-merge-resilience/requirements.md` — 5 FRs for merge conflict handling
- `plans/worktree-merge-resilience/reports/outline-review.md` — review report
