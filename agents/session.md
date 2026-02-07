# Session: Worktree — Empirical testing of memory index recall

**Status:** Focused worktree for parallel execution.

## Pending Tasks

- [ ] **Empirical testing of memory index recall** — Design testing methodology for memory index effectiveness | opus

## Context

The memory index (agents/memory-index.md) is designed to help agents discover relevant documentation on-demand. We need empirical testing to validate:
- Do agents actually consult the index when needed?
- Do they find the right entries?
- Do they read the referenced files?
- What's the recall rate vs. baseline (no index)?

## Design Questions

- Test methodology: synthetic scenarios vs. real task sampling?
- Metrics: recall rate, precision, time-to-discovery?
- Control group: same tasks without memory index loaded?
- Sample size and task diversity?
- How to instrument/measure index usage?

## Blockers / Gotchas

None specific to this task.

## Reference Files

- **agents/memory-index.md** — Current memory index implementation
