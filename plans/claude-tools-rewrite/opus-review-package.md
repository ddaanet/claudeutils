# Opus Review Package: Orchestration Failure Recovery

**Date:** 2026-01-30
**Context:** claude-tools-rewrite runbook execution failed due to parallel execution of sequential TDD cycles
**Status:** Blocked at Cycle 1.3 (completed: 1.1, 1.2 only)
**Remaining:** 35 cycles across 3 phases

## Purpose

Design session to determine:
1. **Recovery strategy** - How to safely resume execution
2. **Orchestration improvements** - Prevent recurrence
3. **Checkpoint strategy** - For remaining 35 cycles

## Reference Documents

### Failure Analysis
- **File:** `plans/claude-tools-rewrite/orchestration-failure-analysis.md`
- **Summary:** What happened, evidence, impact assessment

### Root Cause Analysis
- **File:** `plans/claude-tools-rewrite/why-parallel-execution.md`
- **Summary:** WHY orchestrator parallelized despite sequential instruction
- **Key finding:** System prompt parallelization directive (strong) overrode orchestrate skill sequential requirement (weak) due to syntactic vs semantic dependency mismatch

### Execution Evidence
- **Reports:** `plans/claude-tools-rewrite/reports/step-1-*.md`
  - step-1-2-execution.md (SUCCESS)
  - step-1-3-execution.md (STOP_CONDITION - RED violation)
  - step-1-4-execution.md (FALSE SUCCESS - changes didn't persist)

### Current State
- **Git snapshot:** `plans/claude-tools-rewrite/git-state-snapshot.txt`
- **Source code:** src/claudeutils/account/state.py (has AccountState model, no validate_consistency)
- **Tests:** tests/test_account_state.py (has basic instantiation test only)

### Original Plan
- **Runbook:** `plans/claude-tools-rewrite/runbook.md`
- **Steps:** `plans/claude-tools-rewrite/steps/step-*.md` (37 files)
- **Orchestrator plan:** `plans/claude-tools-rewrite/orchestrator-plan.md`

## Core Issue: Directive Conflict

**System prompt parallelization directive:**
- "Maximize use of parallel tool calls where possible"
- "MUST send a single message with multiple tool calls" (for parallel execution)
- Strong emphasis, repeated multiple times

**Orchestrate skill sequential requirement:**
- "Always sequential unless orchestrator plan explicitly allows parallel"
- Weak phrasing, stated once, no emphasis

**Result:** System prompt won. Orchestrator applied syntactic dependency check (no parameter dependencies between Task calls) and triggered parallel execution, ignoring semantic state dependencies (git commits, file edits).

**See:** `why-parallel-execution.md` for detailed analysis

## Key Questions for Design Session

### 0. Directive Conflict Resolution (NEW - HIGHEST PRIORITY)

**Question:** How should skills override system prompt directives when they conflict?

**Specific case:** Orchestrate skill needs sequential execution but system prompt strongly encourages parallelization.

**Proposed solutions:**
- **A. Explicit override syntax:** Skill says "CRITICAL: Override system prompt parallelization directive"
- **B. Stronger skill language:** Use all-caps emphasis matching system prompt strength
- **C. Execution mode metadata:** Step files include `execution_mode: sequential-required` that orchestrator checks
- **D. System prompt modification:** Add exception for orchestration workflows
- **E. All of the above**

**Tradeoffs:**
- Override syntax = clear but verbose
- Stronger language = simple but may still lose to system prompt
- Metadata = robust but requires runbook changes
- System prompt change = affects all Claude Code behavior

### 1. Recovery Strategy

**Question:** How should we safely resume from current state (end of Cycle 1.2)?

**Options:**
- **A. Sequential resume:** Execute 1.3, 1.4, 1.5, ... one at a time
- **B. Batched sequential:** Execute 3-5 cycles, checkpoint, continue
- **C. Phase-by-phase:** Complete Phase 1 (11 remaining), checkpoint, Phase 2, Phase 3
- **D. Restart from 1.1:** Reset to beginning and re-execute all with strict sequential

**Considerations:**
- 35 cycles remaining
- Current git state is clean (only 1.1, 1.2 committed)
- Source code matches git
- No corruption or partial states

### 2. Orchestration Enforcement

**Question:** Should orchestrate skill enforce sequential execution when plan specifies it?

**Current behavior:** Orchestrator CAN violate plan by batching Task calls in single message

**Proposed fix:** Add enforcement logic:
```
if execution_mode == "sequential":
    for step in steps:
        execute_step(step)  # One Task call per message
        wait_for_completion()
        verify_success()
        continue_or_escalate()
```

**Tradeoff:** Slower execution (more messages) but prevents race conditions

### 3. TDD-Specific Constraints

**Question:** Should TDD workflow have stricter orchestration than oneshot workflow?

**Rationale:** TDD cycles are always sequential (RED→GREEN→REFACTOR, cycle N+1 depends on cycle N)

**Proposed:** TDD runbooks get `execution_mode: sequential-strict` with:
- Explicit prohibition on parallel execution
- Mandatory checkpoint after each cycle (git verify, test run)
- Automatic rollback on RED violation

**Tradeoff:** Much slower but safer for 37-cycle runbooks

### 4. Checkpoint Frequency

**Question:** For remaining 35 cycles, how often should we checkpoint?

**Options:**
- **Every cycle:** Safest but slowest (35 checkpoints)
- **Every phase:** 3 checkpoints total (end of Phase 1, 2, 3)
- **Every N cycles:** e.g., every 5 cycles = 7 checkpoints
- **Natural boundaries:** After clusters of related cycles

**Checkpoint actions:**
- Verify git state (commits match expected sequence)
- Run full test suite
- Verify no regressions
- Continue or escalate

### 5. Dependency Tracking

**Question:** Should step files explicitly declare dependencies on previous steps?

**Current:** Dependencies implicit (cycle order in runbook)

**Proposed:** Add metadata to step files:
```yaml
---
cycle: 1.3
depends_on: [1.2]  # Requires AccountState model from 1.2
blocks: []  # Nothing blocks until this completes
execution: sequential-required
---
```

**Benefit:** Orchestrator can validate execution order before starting agents

**Tradeoff:** More metadata overhead in step files

## Design Session Outputs Needed

1. **Recovery plan:** Specific strategy for resuming from Cycle 1.3 (chosen from options A-D)
2. **Orchestration improvements:** Whether to enforce sequential execution in skill
3. **Checkpoint specification:** Frequency and actions for remaining 35 cycles
4. **TDD workflow changes:** Whether to add TDD-specific constraints
5. **Runbook metadata:** Whether to add dependency tracking to step files

## Success Criteria for Recovery

- All 37 cycles complete successfully (GREEN_VERIFIED)
- Git history clean and sequential (Cycle 1.1, 1.2, 1.3, ..., 3.9)
- Full test suite passes (`just dev` green)
- No RED violations or regression failures
- Implementation matches design (plans/claude-tools-rewrite/design.md)

## Time Sensitivity

**Low urgency** - This is a learning opportunity, not a critical production failure. Take time to design proper fixes rather than rushing to completion.
