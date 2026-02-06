# Session: Worktree — Fix quiet-explore agent usage pattern

**Status:** Parallel worktree session. Execute task and commit.

## Pending Tasks

- [x] **Fix quiet-explore agent usage pattern** — persistent artifacts for reuse across context/audit, not ephemeral tmp/

## Blockers / Gotchas

**Problem:** quiet-explore agent writes reports to tmp/ (gitignored, ephemeral). The intent is persistent artifacts reusable in followup context or for audit.

**Constraint:** tmp/ is for throwaway (execution logs, scratch). Persistent research artifacts go to plans/ directories where they're tracked and committed. See learnings.md "Deliverables in gitignored tmp/" entry.

**Scope:** Fix the quiet-explore agent definition so its instructions/examples guide callers toward persistent output locations (plans/) instead of tmp/. The caller specifies output path, but agent guidance shapes behavior.

## Reference Files

- **agents/learnings.md** — "Deliverables in gitignored tmp/" learning (line 99-103)
