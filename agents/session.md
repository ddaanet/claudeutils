# Session: Worktree — Orchestrate evolution

**Status:** Focused worktree for parallel execution.

## Pending Tasks

- [ ] **Orchestrate evolution** — `/runbook plans/orchestrate-evolution/design.md` | sonnet
  - Design complete with Phase 1 (foundation) + Phase 2 (ping-pong TDD), ready for runbook planning
  - Insights input: ping-pong TDD agent pattern — alternating tester/implementer agents with mechanical RED/GREEN gates between handoffs. Tester holds spec context (can't mirror code structure), implementer holds codebase context (can't over-implement beyond test demands). Resume-based context preservation avoids startup cost per cycle
  - Absorbs: Task agent guardrails — tool-call limits, regression detection, model escalation (haiku→sonnet→opus on capability mismatch) all additive. Design covers agent→user escalation and context-size heuristic but not inter-tier promotion or tool-call budgets
  - Absorbs: RED pass protocol — classification taxonomy, blast radius procedure, defect impact evaluation. Design has remediation + escalation patterns but not formal classification or blast radius assessment
