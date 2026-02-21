# Session: Worktree — Runbook generation fixes

**Status:** Focused worktree for parallel execution.

## Pending Tasks

- [ ] **Runbook generation fixes** — `/design` | sonnet
  - prepare-runbook.py: model propagation, phase numbering, phase context loss, single agent instead of per-phase
  - Phase expansion: introduces defects requiring review+fix on every phase
  - Orchestrator plan: unjustified interleaving
  - Evidence: `plans/hook-batch/reports/runbook-pre-execution-review.md` (3 critical, 4 major, 3 minor)
