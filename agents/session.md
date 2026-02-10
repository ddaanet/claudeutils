# Session: Worktree — RCA: Background agents crash (classifyHandoffIfNeeded)

**Status:** Focused worktree for parallel execution.

## Pending Tasks

- [ ] **RCA: Background agents crash (classifyHandoffIfNeeded)** — Affects both user-backgrounded AND code-backgrounded agents. Two opus+sonnet agents crashed this session after writing output. Not a user-vs-code distinction | sonnet

## Blockers / Gotchas

- Learnings note: classifyHandoffIfNeeded crashes code-backgrounded agents too
- Agents write output before crashing — partial work recoverable
- This is a Claude Code platform bug, RCA scope is understanding triggers and mitigations

## Reference Files

- agents/learnings.md — existing learnings on background agent crashes
