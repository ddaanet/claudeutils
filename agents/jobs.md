# Jobs

Plan lifecycle tracking. Updated when plans change status.

**Status:** `requirements` → `designed` → `planned` → `complete`

## Complete

| Plan | Completed | Summary |
|------|-----------|---------|
| ambient-awareness | 2026-02-01 | Memory index ambient loading |
| commit-rca-fixes | 2026-02-01 | Submodule/artifact/stop-rule fixes |
| handoff-haiku-import | 2026-01-31 | Context recovery for haiku handoffs |
| handoff-lite-fixes | 2026-01-31 | Skill decoupling, template semantics |
| hook-output-fix | 2026-01-31 | Dual-output pattern (additionalContext + systemMessage) |
| memory-index-update | 2026-02-04 | D-3 compliance, 127 headers indexed |
| plan-skill-fast-paths | 2026-02-01 | Three-tier assessment framework |
| reflect-skill | 2026-02-01 | RCA workflow with three exit paths |
| remember-update | 2026-02-01 | Project-level memory index consolidation |
| skill-improvements | 2026-01-31 | TDD behavioral assertions, phase boundaries |
| unification | 2026-01-30 | Phase 4 complete, agent-core operational |
| workflow-controls | 2026-02-02 | Shortcuts hook + STATUS display |

## In Progress

| Plan | Status | Current Step | Task Key |
|------|--------|--------------|----------|
| design-workflow-enhancement | planned | Steps 4-7 pending | — |
| claude-tools-recovery | planned | Re-testing phase | — |
| claude-tools-rewrite | planned | Paused (stubs) | — |

## Designed

| Plan | Notes |
|------|-------|
| commit-unification | May be superseded by commit-rca-fixes |
| feedback-fixes | Awaiting runbook |
| prompt-composer | Oldest plan, at risk |

## Requirements

| Plan | Task Key | Notes |
|------|----------|-------|
| continuation-passing | #wW6G2 | Opus design needed |
| handoff-validation | #JZWhk | Requires continuation-passing |
| requirements-skill | — | New skill |
| task-prose-keys | #POn2Z | Replace hash tokens |
| validator-consolidation | #pEmoW | Move to claudeutils package |
| runbook-identifiers | — | Purpose unclear |

## Stale / Abandoned

| Plan | Days Inactive | Assessment |
|------|---------------|------------|
| markdown | 11 | No design, candidate for deletion |
| handoff-lite-issue | 5 | Only transcript, never developed |
