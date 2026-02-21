# Session: Worktree — Worktree CLI default

**Status:** Focused worktree for parallel execution.

## Pending Tasks

- [ ] **Worktree CLI default** — `/runbook plans/worktree-cli-default/outline.md` | sonnet
  - Plan: worktree-cli-default | Status: designed
  - Absorbs: pre-merge untracked file fix, worktree skill adhoc mode, `--slug` override, `rm --confirm` gate fix
  - Remove sandbox configuration from `_worktree new` — no more `additionalDirectories` in settings.local.json. All inter-tree operations via git or user-validated sandbox override

## Blockers / Gotchas

- Fix: worktree-cli-default adds `--branch` flag
**Merge resolution produces orphaned lines in append-only files:**

## Reference Files

- `plans/worktree-cli-default/outline.md` — CLI change design (positional=task, --branch=slug)
