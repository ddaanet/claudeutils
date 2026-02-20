# Design Review: Orchestrate Evolution D-5 (Ping-Pong TDD)

**Design Document**: plans/orchestrate-evolution/design.md
**Outline Document**: plans/orchestrate-evolution/outline.md
**Review Date**: 2026-02-20
**Reviewer**: design-vet-agent (opus)

## Summary

D-5 adds ping-pong TDD orchestration as Phase 2 — alternating tester/implementer agents with mechanical RED/GREEN gates and role-specific correctors. The architecture is well-designed with clear agent role separation, step file splitting, and resume strategy. Six issues were found and fixed: one critical (agent output paths), three major (GREEN gate mechanism, missing baselines, cleanup/principle contradiction), and two minor (outline stale reference, documentation perimeter gap).

**Overall Assessment**: Ready

## Issues Found and Fixed

### Critical Issues

1. **Phase 2 generated agents placed in wrong directory**
   - Problem: Files changed table listed TDD agents at `plans/<plan>/<plan>-tester.md` etc. Agent discovery requires `.claude/agents/` placement — agents in `plans/` would never be found by Claude Code.
   - Impact: Generated agents would be invisible to the orchestrator at runtime. Phase 2 would fail completely.
   - Fix Applied: Changed all 4 TDD agent paths to `.claude/agents/<plan>-*.md` in the files changed table.

### Major Issues

1. **GREEN gate conflated with verify-step.sh**
   - Problem: Orchestration loop step 5 said "GREEN gate: verify-step.sh (includes full test suite)" but verify-step.sh checks git clean + precommit, not test suite pass. The GREEN gate has a different concern (test suite passes) than post-step verification (clean tree).
   - Impact: Planner would implement GREEN gate as only verify-step.sh, missing the actual test suite verification.
   - Fix Applied: Changed step 5 to "GREEN gate: run full test suite (e.g., `just test`), then verify-step.sh (git clean + precommit)" with three distinct failure paths (test failure, dirty tree, precommit). Added clarifying note in testing strategy that GREEN gate composes existing infrastructure.

2. **No baseline templates specified for TDD agent types**
   - Problem: Phase 1 clearly specifies `quiet-task` and `tdd-task` as baselines for `<plan>-task.md`. Phase 2 introduced 4 new agent types without specifying derivation. Planner would not know whether to create new baselines or extend existing ones.
   - Impact: Planner would need to make an architectural decision (new baselines vs. extend existing) that should be resolved at design time.
   - Fix Applied: Added baseline template specification: tester/implementer derive from `tdd-task.md`, test-vet/impl-vet derive from `vet-fix-agent.md`. Added explanation that prepare-runbook.py appends cached plan context to each baseline, same pattern as D-2.

3. **Q-2 cleanup and agent caching principle contradict D-5 agent count**
   - Problem: Q-2 said "Up to two agent types per plan" and cleanup listed only `<plan>-task.md` and `<plan>-vet.md`. Key Orchestration Principles said "No phase-specific agent variants -- up to two agent types per plan." D-5 introduces up to 6 agent types. These pre-D-5 statements would confuse the planner about whether D-5's 4 additional agents are permitted.
   - Impact: Conflicting constraints in outline would cause planner confusion about agent generation scope.
   - Fix Applied (outline): Updated Q-2 to distinguish general plans (up to 2) from TDD plans (up to 6). Updated cleanup to use glob pattern `<plan>-*.md`. Updated agent caching principle to reflect type-dependent agent count.

### Minor Issues

1. **Outline approach paragraph references "Parallel dispatch" (deferred FR-1)**
   - Problem: Approach summary said "Parallel dispatch, post-step remediation, and agent caching model replace..." but parallel dispatch was deferred to `plans/parallel-orchestration/`.
   - Fix Applied: Replaced "Parallel dispatch" with "ping-pong TDD orchestration" in outline approach.

2. **Outline scope says "RED/GREEN verification scripts" implying two new scripts**
   - Problem: Scope listed "RED/GREEN verification scripts" but only verify-red.sh is a new script. GREEN gate composes existing `just test` + Phase 1's `verify-step.sh`.
   - Fix Applied: Changed to "RED verification script (verify-red.sh) -- mechanical gate; GREEN gate composes existing `just test` + `verify-step.sh`".

3. **Documentation perimeter missing Phase 2 baseline references**
   - Problem: Required reading listed only Phase 1 artifacts. Phase 2 planning requires understanding existing `tdd-task.md` and `vet-fix-agent.md` baselines since the 4 new agent types derive from them.
   - Fix Applied: Added `agent-core/agents/tdd-task.md` and `agent-core/agents/vet-fix-agent.md` to required reading with Phase 2 derivation context.

## Requirements Alignment

**Requirements Source:** inline (design.md Requirements section)

| Requirement | Addressed | Design Reference |
|-------------|-----------|------------------|
| FR-8 | Yes | D-5 orchestration loop, agent roles |
| FR-8a | Yes | D-5 RED gate script (verify-red.sh), mechanical exit code check |
| FR-8b | Yes | D-5 GREEN gate (just test + verify-step.sh composition) |
| FR-8c | Yes | D-5 test-vet and impl-vet with role-specific cached context |
| FR-8d | Yes | D-5 agent resume strategy (resume within phase, fresh on overflow) |

**Gaps:** None. All FR-8 sub-requirements traced to concrete mechanisms in D-5.

**Traceability table (design.md lines 46-50):** Verified all FR-8* entries map to D-5 sections. Traceability complete.

## Positive Observations

- **Context specialization is well-motivated.** "Tester never sees implementation hints; implementer never sees test specs" prevents two known failure modes (over-implementation and test-mirroring). This is a concrete design decision with clear rationale.
- **RED gate mechanism separation is correct.** Keeping the gate mechanical (exit code only) and delegating "fails for right reason" to the test-vet is the right layering. Mechanical gates are reliable; semantic judgment belongs in review agents.
- **Resume strategy is consistent with D-3.** Same >15 message heuristic, same escalation path. Correctors explicitly excluded from resume (each review independent). No new patterns introduced unnecessarily.
- **Step file separation enables role dispatch without content reading.** Orchestrator dispatches by role marker in plan, never reads step content. This is consistent with the bloat prevention principle.
- **Phase dependency is explicit.** "Depends on: Phase 1 infrastructure (agent caching D-2, remediation D-3, verification script)" gives the planner clear ordering.

## Recommendations

1. Consider whether the existing `tdd-task.md` baseline needs modification before Phase 2 uses it as a derivation source. The current baseline assumes a single agent doing RED/GREEN/REFACTOR. The tester agent only does RED; the implementer only does GREEN. Phase 2 may need to either subset the baseline or create role-specific variants. This is a planning-time decision, not a design gap, but worth flagging.

2. The cleanup glob pattern (`<plan>-*.md`) should be cautious about false positives if other files match the pattern. The planner should verify no non-agent files exist with matching names in `.claude/agents/`.

## Next Steps

1. Proceed to runbook planning. All design issues resolved.
