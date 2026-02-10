# Session: Worktree — RCA: Expansion agents omit cycle metadata

**Status:** Focused worktree for parallel execution.

## Pending Tasks

- [ ] **RCA: Expansion agents omit cycle metadata** — 42 cycles missing Stop/Error Conditions required by prepare-runbook.py, fix expansion prompt or plan-tdd skill | sonnet

## Blockers / Gotchas

- prepare-runbook.py validates cycle metadata — check what fields are required
- Expansion happens in plan-tdd skill phase expansion step

## Reference Files

- agent-core/bin/prepare-runbook.py — metadata validation logic
