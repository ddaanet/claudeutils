# Session: Worktree — Worktree merge session loss diagnosis

**Status:** Focused worktree for parallel execution.

## Pending Tasks

- [ ] **Worktree merge session loss diagnosis** — RCA why `_worktree merge` autostrategy drops session.md context | sonnet
  - Root cause: focused session.md in branch lacks main's Worktree Tasks, autostrategy favors branch version
  - Observed: Merge 1 (`f525d705`) dropped WT entry, Merge 2 (`c91c7628`) left orphan + malformed blocker. Pre-merge: `0c91d969`
  - Observed: Merge 3 (`8a97fb71` planstate-delivered) appended 5 `[from: planstate-delivered]` entries into Blockers section. Merge 4 (`50e37ede` wt-merge-dirty-tree) clean — code-only branch, no session.md changes
  - Fix target: `src/claudeutils/worktree/merge.py` session autostrategy
  - Two manifestations: (1) WT Tasks entries dropped, (2) branch-only content appended to wrong section (Blockers)
  - Related: planstate-delivered (plan: planstate-delivered) would prevent "completed but no record" class
