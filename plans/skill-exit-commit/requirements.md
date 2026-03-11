# Skill Exit Commit

`/design` and `/runbook` should commit dirty tree on exit before routing to `/inline`. Currently `/inline` checks for dirty tree on entry — this is the wrong boundary. The producer should clean up, not the consumer.

## Requirements

### Functional Requirements

**FR-1: Design skill exit commit**
When `/design` completes and routes to execution (`/inline`), commit dirty tree before the routing call. Same pattern as `/orchestrate` entry: separate planning artifacts from implementation changes.
- Acceptance: `/design` routes to `/inline` → tree is clean when `/inline` starts
- Acceptance: `/design` exits without routing to `/inline` (default-exit to `/handoff`) → no commit (handoff handles it)

**FR-2: Runbook skill exit commit**
When `/runbook` completes and routes to execution (`/inline`), commit dirty tree before the routing call.
- Acceptance: `/runbook` routes to `/inline` → tree is clean when `/inline` starts
- Acceptance: `/runbook` exits without routing to `/inline` → no commit

### Constraints

**C-1: Conditional on execution routing**
Commit only when the next step is execution (`/inline`). When routing ends at `/handoff` (default-exit), the handoff+commit flow handles persistence. No unconditional commit on every skill exit.

### Out of Scope

- Changing `/inline` entry behavior (it may keep its dirty-tree check as defense-in-depth, but should not be the primary mechanism)
- `/orchestrate` entry commit (already works correctly)
