# Session: Worktree — Worktree merge data loss

**Status:** Focused worktree for parallel execution.

## Completed This Session

- Design document generated and vetted (`plans/worktree-merge-data-loss/design.md`)
  - Three tracks: removal safety guard (cli.py rm), merge correctness (merge.py Phase 4), skill update (SKILL.md Mode C)
  - Design review: Ready, 1 major + 2 minor issues fixed by vet, no UNFIXABLE
  - Report: `plans/worktree-merge-data-loss/reports/design-review.md`
  - Checkpoint commit: 9f7c51e

## Pending Tasks

- [ ] **Worktree merge data loss** — `/runbook plans/worktree-merge-data-loss/design.md` | sonnet
  - Design: `plans/worktree-merge-data-loss/design.md` (vetted, ready)
  - Phase 1 (TDD): removal guard + merge correctness — cli.py, merge.py, utils.py
  - Phase 2 (general): skill update — SKILL.md Mode C
  - Key decisions: D-1 marker text detection, D-2 exit codes (0/1/2), D-3 no destructive output, D-4 MERGE_HEAD checkpoint, D-5 ancestry validation, D-6 guard before destruction, D-7 shared helper in utils.py
  - Reports: `plans/worktree-merge-data-loss/reports/` (explore-merge-logic, explore-git-history, outline-review, design-review)
