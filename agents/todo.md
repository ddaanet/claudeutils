# Todo

Deferred work items and shelved context.

---

## Backlog

### 2026-01-18 - Session: unification

**Branch:** unification

**Task:** Phase 2 - Analysis Phase

**Status:** Ready to start

**This Session:**
- Resolved Phase 1 blocker: git submodule integration
- Verified Phase 2 readiness (all checks passed)
- Report: `tmp/phase2-readiness.md`

**Handoff to Next Session:**
- Phase 2 Ready
- Key files: `plans/unification/phases/phase2.md`, `plans/unification/phases/consolidation-context.md`
- Execution pattern: Delegate with context + phase file, reports to `plans/unification/reports/`

**Archived to:** `agents/shelf/unification-session.md`

---

### 2026-01-18 - Context: unification

**Project:** Rules Unification Project

**Key Documents:**
- Design: `plans/unification/design.md`
- Plans: `plans/unification/consolidation-plan.md`, `plans/unification/phases/`
- Reports: `plans/unification/reports/`

**Architecture:**
- agent-core: Shared fragments (git submodule)
- claudeutils: Generation tooling (Python module)

**Archived to:** `agents/shelf/unification-context.md`

---

### Deferred from Task Agent Pattern Session (Option A)

**Context Monitoring Skill:**
- [ ] Web search for existing Claude Code context monitoring skill
- [ ] Build context monitoring skill if not found
- [ ] Configure thresholds: >100k notify, >125k immediate handoff
- [ ] Install in agent-core for reusability

**Pattern Documentation:**
- [ ] Document pattern: Plan-specific agent (`agent-core/pattern-task-plan-agent.md`)
- [ ] Document pattern: Task phase planning (`agent-core/pattern-task-phase-planning.md`)
- [ ] Document pattern: Ad-hoc scripting (`agent-core/pattern-adhoc-scripting.md`)

**Tooling:**
- [ ] Create plan splitter input format spec (`agent-core/specs/plan-splitter-input-format.md`)
- [ ] Create plan-specific agent creation script (`agent-core/scripts/create-plan-agent.*`)

**Phase 2 Application:**
- [ ] Build Phase 2 plan using weak orchestrator pattern
- [ ] Review Phase 2 plan with fresh sonnet agent

---

- [ ] (empty - items added as needed)
