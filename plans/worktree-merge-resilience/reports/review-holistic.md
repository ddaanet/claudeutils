# Runbook Review: Holistic — Worktree Merge Resilience

**Artifact**: `plans/worktree-merge-resilience/runbook-phase-{1-5}.md`
**Date**: 2026-02-18T00:00:00Z
**Mode**: review + fix-all (holistic cross-phase)
**Phase types**: Mixed — Phases 1–4 TDD (11 cycles), Phase 5 General (3 steps)

## Summary

All five phases were reviewed for cross-phase dependency ordering, state continuity, exit code consistency, `_detect_merge_state` incremental build correctness, model assignments, and LLM failure modes. Per-phase issues were already caught and fixed by the individual phase review passes. One cross-phase issue found: Phase 2 Cycle 2.1 asserted exit code 3, but the test scenario (submodule-only conflict) resolves to exit 0 via Phase 3's auto-resolution of the agent-core pointer — Phase 3's exit-3 removal of the abort block happens in Phase 3, which executes after Phase 2. This was fixed.

**Overall Assessment**: Ready

## Findings

### Critical Issues

None.

### Major Issues

1. **Phase 2 Cycle 2.1 exit code assertion incorrect for the test scenario**
   - Location: `runbook-phase-2.md`, Cycle 2.1, RED Phase, Assertions, bullet 3
   - Problem: Cycle 2.1 asserted `exit code == 3` after Phase 2 GREEN. The test scenario creates conflicts only inside agent-core (not parent source files). Execution flow after Phase 2's `check=False` fix:
     1. Phase 2 leaves agent-core mid-merge (MERGE_HEAD in agent-core), returns normally.
     2. Phase 3 runs `git merge --no-commit --no-ff slug` → agent-core pointer conflict detected.
     3. Phase 3 auto-resolves via `git checkout --ours agent-core` (lines 162-165 in current `_phase3_merge_parent`).
     4. No remaining conflicts → `if conflicts:` block skipped → Phase 4 runs → exit 0.
     At Phase 2 execution time, Phase 3 still has the abort block (Phase 3 changes happen in Phase 3). But even after Phase 3's fix (no more abort), the submodule-only conflict scenario yields exit 0, not exit 3. Exit 3 only occurs when source files (non-session, non-learnings, non-agent-core) have unresolved conflicts — this test does not create that scenario.
     Note: the REDs expected failure (`SystemExit(1)` from `CalledProcessError`) is still correct.
   - Fix: Changed assertion from "Exit code is 3" to "Exit code is 0 or 3 (not 1) — Phase 2 no longer raises; parent merge auto-resolves the submodule pointer (Phase 3 `checkout --ours agent-core`), so exit 0 is the most likely outcome for a submodule-only conflict."
   - **Status**: FIXED

### Minor Issues

None beyond the major issue above.

## Cross-Phase Dependency Ordering

### Phase 1 → Phase 2 (submodule_conflicts routing)

Phase 1 Cycle 1.4 adds `submodule_conflicts` state, which routes to `_phase3_merge_parent` directly (skips Phase 2). Phase 2 "Depends on: Cycle 1.4" correctly gates Phase 2 on this routing existing. The `submodule_conflicts` routing in Phase 1 Cycle 1.2 Green is: "call `_phase3_merge_parent(slug)` then `_phase4_merge_commit_and_precommit(slug)`" — consistent with D-5.

### Phase 2 → Phase 3 (exit 3 path)

Phase 3 "Depends on: Cycles 1.3 and 2.1" correctly gates. Phase 3's changes (remove abort block, exit 3) are not needed for Phase 2's tests to pass — Phase 2 Cycle 2.1 only needs Phase 2's own `check=False` change to work. The exit code assertion fix above resolves the false dependency.

### Phase 3 → Phase 4 (_format_conflict_report call sites)

Phase 4 "Depends on: Cycle 3.1 (exit 3 path exists)". Both call sites for `_format_conflict_report` are correctly identified across phases:
- `_phase3_merge_parent` `if conflicts:` block (Phase 3 Cycle 3.1 introduces this path)
- `parent_conflicts` branch in `merge()` (Phase 1 Cycle 1.3 stub, Phase 4 replaces the stub with the formatted call)

No missing call sites across phases.

### Phase 4 → Phase 5 (exit code stability before threading)

Phase 5 "Depends on: Phases 1–4 (all exit code semantics stable)". Phase 5 Step 5.1 audits after all TDD phases complete. Correct ordering — threading after behavior is correct.

## State Continuity: `_detect_merge_state` Incremental Build

- Cycle 1.1 GREEN: `merged`/`clean` only
- Cycle 1.2 GREEN: extends with `parent_resolved`/`parent_conflicts` (required for routing test)
- Cycle 1.4 GREEN: extends with `submodule_conflicts` (between `merged` and parent MERGE_HEAD check)
- Cycle 1.5 GREEN: no detection changes, confirms `clean` routing uses all phases

Each extension is additive. Prior cycles' tests are not broken by later extensions because:
- `merged` check occurs before submodule check (D-5 order) — 1.1 tests unaffected by 1.4 addition
- `parent_resolved`/`parent_conflicts` added in 1.2 — 1.1 test uses a merged branch, hits `merged` first, unaffected
- Full detection order after Cycle 1.4: `merged` → `submodule_conflicts` → `parent_resolved`/`parent_conflicts` → `clean` — matches D-5

## Exit Code Consistency

Tracing all `SystemExit` paths through the five phases:

| Path | Code | Phase | Notes |
|------|------|-------|-------|
| Branch not found | 2 | 1 (Phase 1 validate) | Correct (fatal) |
| Clean tree required | 1 | 1 (Phase 1 validate) | Correct (error) |
| Merge failed (no MERGE_HEAD) | 1 | 3 Cycle 3.2 | Preserved for unrecognized errors |
| Source conflicts | 3 | 3 Cycle 3.1 | Correct (conflict-pause) |
| Parent conflicts (state machine entry) | 3 | 1 Cycle 1.3 | Correct (conflict-pause) |
| Merge state lost | 2 | 4 | Correct (fatal) |
| Nothing to commit + not merged | 2 | 4 | Correct (fatal) |
| Precommit failure | 1 | 4 | Correct (error, not conflict) |
| Branch not fully merged (validate) | 2 | 4 | Correct (fatal) |

Phase 5 Step 5.1 audits all of these. No remaining exit 1 on conflict-pause paths after Phases 1–4 complete.

## Model Assignment Review

- Phase 5 Step 5.3 (SKILL.md edit): `Execution Model: Opus` — correct, skill file edit requires opus per artifact-type override rule.
- Phase 5 Step 5.1 (audit + judgment): `Execution Model: Sonnet` — correct for code audit with classification judgment.
- Phase 5 Step 5.2 (mechanical substitution): `Execution Model: Haiku` — correct for grep-and-delete.
- Phases 1–4: no explicit model tags; TDD behavioral changes in merge.py are moderate complexity, consistent with sonnet.

No advisory flags.

## LLM Failure Mode Cross-Phase Analysis

**Vacuity:** No vacuous cycles across phases. Each cycle tests a discrete behavioral change: merged/clean detection, routing, parent-conflicts-preserve, submodule-pass-through, untracked-retry, conflict-output.

**Dependency ordering:** Foundation-first order verified across phases: state machine (P1) → submodule behavior (P2) → parent behavior (P3) → output format (P4) → exit threading (P5). Within phases, incremental build order is correct (see above).

**Density:** 11 TDD cycles across 4 phases. No adjacent cycles test the same function with <1 branch point difference. Each cycle has a distinct behavioral boundary.

**Checkpoint spacing:** Checkpoints at:
- After Cycle 1.3 (routing verification)
- After Cycle 3.1 (NFR-2 grep for no --abort)
- Phase 5 Step 5.1 includes inline validation

3 phases between Cycle 1.3 checkpoint and the Phase 5 validation. Item count: 1.3 → 1.4 → 1.5 → 2.1 → 2.2 → 3.1 → 3.2 → 4.1 = 8 items. Within the <10 item limit.

**File growth:** `merge.py` currently 263 lines. Projected additions: Phase 1 routing (~25 lines), Phase 2 check=False path (~10 lines), Phase 3 untracked retry (~20 lines), Phase 4 `_format_conflict_report` (~30 lines), Phase 5 exit threading (~0-5 net). Projected total: ~350 lines. Approaches threshold — Phase 5 executor should monitor and may want to extract helpers, but does not breach 400-line enforcement threshold.

## Requirements Coverage

All 5 FRs and 2 NFRs covered:
- FR-1 (submodule pass-through): Phase 2 Cycle 2.1
- FR-2 (parent merge preservation): Phase 3 Cycle 3.1
- FR-3 (untracked file handling): Phase 3 Cycle 3.2
- FR-4 (conflict context output): Phase 4 Cycle 4.1
- FR-5 (idempotent resume): Phase 1 Cycles 1.1–1.5
- NFR-1 (exit code backward compat): Phase 5 Step 5.1 + Phase 1 Cycle 1.3
- NFR-2 (no data loss): Phase 3 Cycle 3.1 + checkpoint grep

Constraints C-1 and C-2 covered by Phase 5 Step 5.3 (SKILL.md) and D-8 (stdout unification).

## Fixes Applied

- `plans/worktree-merge-resilience/runbook-phase-2.md`, Cycle 2.1, Assertions bullet 3 — corrected exit code assertion from `exit_code == 3` to `exit_code is 0 or 3 (not 1)` with explanation of why exit 0 is expected for submodule-only conflict scenario

## Unfixable Issues (Escalation Required)

None — all issues fixed.

---

**Ready for next step**: Yes
