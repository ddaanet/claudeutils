# Design Outline: Error Handling Framework

## Problem Statement

Error handling is fragmented across three subsystems — each with ad-hoc patterns, inconsistent semantics, and gaps:

1. **Runbook orchestration** — Has escalation levels and dirty-tree checks but no rollback strategy, no escalation acceptance criteria, no timeout handling
2. **Task lifecycle** — Only pending/in-progress/complete states. No blocked/failed states, no error recording
3. **CPS skill chains** — Five cooperative skills chain via tail-calls with zero error handling. Chain failure = orphaned continuation, stale session state

The existing `error-handling.md` fragment covers only "don't suppress errors." The `error-classification.md` fragment covers orchestration-only taxonomy. Neither addresses cross-system error propagation.

See `plans/error-handling/reports/explore-error-handling.md` for detailed gap analysis.

## Approach

Unify error handling into a layered framework that respects existing patterns while filling gaps:

**Layer 1: Error taxonomy** — Extend existing 4-category classification to cover all subsystems (not just orchestration)
**Layer 2: Orchestration hardening** — Escalation acceptance criteria, rollback strategy, timeout handling
**Layer 3: Task failure lifecycle** — Add blocked/failed states to session.md task notation
**Layer 4: CPS chain error recovery** — Define what happens when a skill fails mid-chain (abort, retry, resume)
**Layer 5: Documentation consolidation** — Merge scattered error patterns into coherent framework

Layers are ordered by implementation dependency: taxonomy provides foundation, orchestration and task are independent, CPS builds on task states, documentation consolidates all.

## Key Decisions

**D-1: CPS error propagation model** — When a skill fails mid-chain, abort remaining continuation and record it in session.md Blockers section for manual resume. No automatic retry (consistent with "error gates are hard stops" pattern in interactive chains). The orphaned continuation is recorded with error context so `r` (resume) can pick up from the failed skill.

**D-2: Task failure notation** — Add `- [!]` (blocked) and `- [✗]` (failed) states to session.md. Both include reason text. Blocked transitions back to pending when unblocked; failed is terminal (requires user decision to retry or abandon).

**D-3: Escalation acceptance criteria** — Define per-error-type what "fixed" means: (a) `just dev` passes, (b) git tree clean, (c) output validates against step acceptance criteria. All three criteria are required for successful escalation resolution.

**D-4: Fragment allocation strategy** — Create targeted fragments for new subsystems (task failure lifecycle, escalation acceptance). Extend existing fragments only where natural fit (CPS error recovery → `continuation-passing.md`). Don't force extensions into minimalist fragments (`error-handling.md` is 12 lines by design).

**D-5: Rollback is "revert to step start"** — When escalation fails partway through a step, revert to the last clean commit before that step. Don't attempt partial undo.

**D-6: Hook error protocol** — Hook failures should be visible (stderr output) but non-fatal for the session. CPS hook already silently catches errors; formalize this as intentional degraded mode. Document expected behavior for hook crash, timeout, and invalid output.

## Open Questions

- Should orchestrator timeout be configurable per-step or per-runbook? (Per-step is more flexible but adds complexity to orchestrator plan format.)
- Should `- [✗]` (failed) tasks be auto-cleaned on handoff, or persist until user explicitly removes them? (Persistence maintains audit trail but clutters session.md over time.)

## Scope Boundaries

**In scope:**
- CPS chain error recovery protocol (continuation-passing.md update)
- Task lifecycle error states (session.md notation, handoff skill update)
- Orchestration escalation hardening (orchestrate skill update, acceptance criteria)
- Error taxonomy extension (error-classification.md update)
- error-handling.md consolidation (cross-system patterns)

**Out of scope:**
- Hook system architecture changes (Claude Code internals, not modifiable). Hook error *protocol* (stderr visibility, degraded mode) IS in-scope as D-6.
- Agent crash recovery automation (workaround exists: `run_in_background=true`)
- Vet over-escalation pattern library (optimization, not framework)
- Prerequisite validation enforcement in tooling (script change to plan-reviewer, separate task)

## Architecture

### Three Subsystems

**1. Runbook Orchestration (Layer 2)**
- Escalation flow: Agent → Haiku orchestrator → Sonnet diagnostic → User
- Error classification at agent level using 4-category taxonomy
- Acceptance criteria for escalation resolution (dev passes, tree clean, output validates)
- Rollback strategy: revert to last clean commit before failed step
- Timeout handling with configurable limits per step or runbook

**2. Task Lifecycle (Layer 3)**
- Extended state notation: `[ ]` pending, `[>]` in-progress, `[x]` complete, `[!]` blocked, `[✗]` failed
- State transitions: pending → in-progress → (complete | blocked | failed)
- Blocked tasks record reason and can transition back to pending when unblocked
- Failed tasks are terminal, requiring user decision to retry or abandon
- Error context recorded inline with task notation

**3. CPS Skill Chains (Layer 4)**
- Continuation passing via hook injection + skill tail-calls
- Error propagation: skill failure aborts remaining continuation
- Orphaned continuations recorded in session.md Blockers section
- Manual resume via `r` command from recorded error context
- No automatic retry (errors are hard stops in interactive chains)

### Error Flow

```
Agent executes → Error occurs → Classify (4 categories) → Escalate
  ↓
Orchestrator receives error → Check acceptance criteria
  ↓
If fixable: Sonnet diagnostic → Apply fix → Verify acceptance → Retry step
If not fixable: Record in session.md → Escalate to user
  ↓
User resolves → Manual resume from recorded context
```

### Integration Points

- **Taxonomy (Layer 1)** provides error categories for all three subsystems
- **Task states (Layer 3)** used by CPS chains to record blocked/failed continuations
- **Orchestration acceptance (Layer 2)** defines verification protocol reused in CPS skill error handling
- **Documentation (Layer 5)** consolidates patterns from all subsystems into unified fragments

## Implementation Plan

### Phase 1: Foundation (Layer 1)
- Extend `error-classification.md` to cover task lifecycle errors and CPS chain errors
- Add agent-level classification examples for each subsystem
- Document error category decision tree for agents

### Phase 2: Orchestration (Layer 2)
- Create `escalation-acceptance.md` fragment defining success criteria
- Update `orchestrate/SKILL.md` with rollback protocol and timeout handling
- Document recovery paths for dirty tree violations

### Phase 3: Task Lifecycle (Layer 3)
- Create `task-failure-lifecycle.md` fragment with state notation and transitions
- Update `handoff/SKILL.md` to handle blocked/failed task states
- Add task error recording template for session.md

### Phase 4: CPS Chains (Layer 4)
- Extend `continuation-passing.md` with error propagation model
- Update cooperative skills (`/design`, `/runbook`, `/orchestrate`, `/handoff`) with error handling
- Document orphaned continuation recovery protocol

### Phase 5: Consolidation (Layer 5)
- Review all error-related fragments for consistency
- Add cross-references between subsystems
- Document common patterns (mechanical detection, clean tree requirements, prevention over recovery)

## Success Metrics

**Completeness:**
- All three subsystems have documented error handling protocols
- Error taxonomy covers runbook, task, and CPS subsystem failures
- Every error category has defined escalation path and acceptance criteria

**Clarity:**
- Agent-level classification decision tree is actionable (agents can self-classify)
- Rollback procedures are unambiguous (no "it depends" guidance)
- Task state transitions are explicit with documented triggers

**Feasibility:**
- No changes required to Claude Code internals (hook protocol only)
- Existing patterns preserved (weak orchestrator, continuation passing)
- Implementation can proceed in phases without breaking existing workflows

**Validation:**
- Test each error category with real scenarios from exploration report
- Verify acceptance criteria are measurable (dev output, git status, validation checks)
- Confirm CPS error recovery works for multi-skill chains (`/design, /runbook, /orchestrate`)
- Validate hook error protocol with intentional hook failures
