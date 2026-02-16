# Session: Worktree — Worktree merge data loss

**Status:** Focused worktree for parallel execution.

## Completed This Session

- Design document generated and vetted (`plans/worktree-merge-data-loss/design.md`)
  - Three tracks: removal safety guard (cli.py rm), merge correctness (merge.py Phase 4), skill update (SKILL.md Mode C)
  - Design review: Ready, 1 major + 2 minor issues fixed by vet, no UNFIXABLE
  - Report: `plans/worktree-merge-data-loss/reports/design-review.md`
  - Checkpoint commit: 9f7c51e

- Runbook outline reviewed and fixed (`plans/worktree-merge-data-loss/runbook-outline.md`)
  - Delegated to runbook-outline-review-agent (fix-all mode)
  - Fixed: 2 critical (dependency declarations, traceability table), 3 major (vacuous diagnostic cycle removed, growth projection, collapsible cycle evaluation), 3 minor (expansion guidance, cycle count, design reference)
  - All 9 FRs covered with implementation notes
  - Structure: Phase 1 (11 TDD cycles), Phase 2 (1 general step)
  - Ready for phase-by-phase expansion
  - Report: `plans/worktree-merge-data-loss/reports/runbook-outline-review.md`

## Pending Tasks

- [ ] **Worktree merge data loss** — Continue `/runbook` phase-by-phase expansion | sonnet
  - Design: `plans/worktree-merge-data-loss/design.md` (vetted, ready)
  - Outline: `plans/worktree-merge-data-loss/runbook-outline.md` (reviewed, ready)
  - Phase 1 (TDD): 11 cycles — removal guard + merge correctness (cli.py, merge.py, utils.py)
  - Phase 2 (general): 1 step — skill update (SKILL.md Mode C)
  - Key decisions: D-1 marker text detection, D-2 exit codes (0/1/2), D-3 no destructive output, D-4 MERGE_HEAD checkpoint, D-5 ancestry validation, D-6 guard before destruction, D-7 shared helper in utils.py
  - Next: Expand Phase 1 (TDD cycles), delegate to plan-reviewer, repeat for Phase 2
  - Reports: `plans/worktree-merge-data-loss/reports/` (explore-merge-logic, explore-git-history, outline-review, design-review, runbook-outline-review)
