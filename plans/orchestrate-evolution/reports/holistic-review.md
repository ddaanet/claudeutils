# Runbook Review: Orchestrate Evolution — Holistic Cross-Phase Review

**Artifact**: `plans/orchestrate-evolution/runbook-phase-{1,2,3,4}.md`
**Date**: 2026-02-24T00:00:00Z
**Mode**: review + fix-all (holistic — individual phase reviews already completed)
**Phase types**: Mixed — Phase 1 (TDD, 4 cycles), Phase 2 (TDD, 4 cycles), Phase 3 (TDD, 4 cycles), Phase 4 (General, 2 steps)

## Summary

All four phase files were previously reviewed individually (reports: `phase-1-review.md`, `phase-2-review.md`, `phase-3-review.md`, `phase-4-review.md`). This holistic review examines cross-phase consistency, metadata accuracy, requirements coverage, dependency ordering, file path validity, and test file routing. Two minor cross-phase inconsistencies were found and fixed. No critical or major issues. The runbook is ready for execution.

**Overall Assessment**: Ready

## Findings

### Critical Issues

None.

### Major Issues

None.

### Minor Issues

1. **Line count inconsistency for `test_prepare_runbook_agents.py` between Phase 1 and Phase 3**
   - Location: Phase 3 preamble, Key constraints section, line 17
   - Problem: Phase 3 said `test_prepare_runbook_agents.py` is "(353 lines, near 400-line threshold)". The actual file is 354 lines, consistent with Phase 1's preamble ("currently 354 lines"). The discrepancy (1 line) traces to different measurement points during authoring, but creates confusion: an executor reading Phase 3 would see a different number than Phase 1 and could question whether changes happened between phases.
   - Fix: Updated Phase 3 to "354 lines" — matches Phase 1 and actual file.
   - **Status**: FIXED

2. **refactor.md line count off by 1 in Phase 4 Step 4.2**
   - Location: Phase 4 Step 4.2, Implementation section, refactor.md description
   - Problem: Step 4.2 stated "refactor.md (244 lines → ~274 lines)" but the file is 243 lines. Small inaccuracy; an executor verifying their changes against "expected ~274" would be off by 1.
   - Fix: Updated to "243 lines → ~273 lines" to match actual file.
   - **Status**: FIXED

## Cross-Phase Validation

### Metadata Accuracy

**Total Steps count:** Claimed "14 (12 TDD cycles + 2 general steps)" in Weak Orchestrator Metadata.
- Phase 1: Cycles 1.1, 1.2, 1.3, 1.4 = 4
- Phase 2: Cycles 2.1, 2.2, 2.3, 2.4 = 4
- Phase 3: Cycles 3.1, 3.2, 3.3, 3.4 = 4
- Phase 4: Steps 4.1, 4.2 = 2
- **Total: 14 — CORRECT**

**Execution model assignments:**
- Cycles 1.1-1.4: Sonnet — appropriate (restructuring existing logic, agent composition)
- Cycles 2.1-2.4: Sonnet — appropriate (new format generation, shell script with E2E tests)
- Cycles 3.1-3.4: Sonnet — appropriate (extending Phase 1 patterns)
- Steps 4.1-4.2: Opus — correct (architectural artifacts: SKILL.md, refactor.md, delegation.md)

### Cross-Phase Dependency Ordering

Dependencies correctly declared and respected:
- Phase 1: No dependencies (foundation phase)
- Phase 2: Depends on Phase 1 (agent naming in orchestrator plan header)
- Phase 3: Depends on Phase 1 (`generate_task_agent`, `read_baseline_agent`) + Phase 2 (orchestrator plan format, `generate_default_orchestrator`)
- Phase 4: Depends on Phases 1+2+3 (all infrastructure must exist before prose rewrite)

No cross-phase dependency ordering violations found. Cycle 3.1 correctly references `generate_task_agent` (created in Phase 1 Cycle 1.1) rather than attempting to use it before creation.

### Test File Routing (No Duplicate Targets)

- Phase 1 (Cycles 1.1-1.4): all target `tests/test_prepare_runbook_agents.py` (extend)
- Phase 2 (Cycles 2.1-2.3): target `tests/test_prepare_runbook_orchestrator.py` (extend)
- Phase 2 (Cycle 2.4): creates `tests/test_verify_step.py` (new)
- Phase 3 (Cycles 3.1-3.3): target `tests/test_prepare_runbook_tdd_agents.py` (new — SEPARATE from Phase 1 target)
- Phase 3 (Cycle 3.4): creates `tests/test_verify_red.py` (new)
- **No duplicate test file targets across phases. CORRECT.**

### File Path Validation

Files that must currently exist (all verified via Glob):
- `agent-core/bin/prepare-runbook.py` — EXISTS
- `agent-core/skills/orchestrate/SKILL.md` — EXISTS
- `agent-core/agents/refactor.md` — EXISTS
- `agent-core/fragments/delegation.md` — EXISTS
- `agent-core/agents/artisan.md` — EXISTS
- `agent-core/agents/test-driver.md` — EXISTS
- `agent-core/agents/corrector.md` — EXISTS
- `tests/test_prepare_runbook_agents.py` — EXISTS
- `tests/test_prepare_runbook_orchestrator.py` — EXISTS

Files correctly marked as "(create)" (do not currently exist — expected for TDD):
- `agent-core/skills/orchestrate/scripts/verify-step.sh` — NOT YET (Phase 2 Cycle 2.4 creates it)
- `agent-core/skills/orchestrate/scripts/verify-red.sh` — NOT YET (Phase 3 Cycle 3.4 creates it)
- `tests/test_prepare_runbook_tdd_agents.py` — NOT YET (Phase 3 Cycle 3.1 creates it)
- `tests/test_verify_step.py` — NOT YET (Phase 2 Cycle 2.4 creates it)
- `tests/test_verify_red.py` — NOT YET (Phase 3 Cycle 3.4 creates it)

**Advisory — design/phase terminology:** The design.md references `tdd-task.md` and `quiet-task` as baseline names. These files do not exist. Phase files correctly use `test-driver.md` and `artisan.md`. The runbook-outline.md (line 37) provides the explicit mapping: "Design references 'quiet-task' and 'tdd-task' — these map to artisan.md and test-driver.md respectively." No phase file fix needed.

### Requirements Coverage

All requirements from design.md verified against phase assignments:

| Requirement | Phase | Cycle/Step | Status |
|------------|-------|------------|--------|
| FR-2 (post-step remediation) | 4 | Step 4.1 | Covered |
| FR-3 (RCA task generation) | 4 | Step 4.1 | Covered |
| FR-4 (delegation prompt dedup) | 1 | Cycles 1.1-1.3 | Covered |
| FR-5 (commit instruction) | 1 | Cycle 1.1 | Covered |
| FR-6 (scope constraint) | 1 | Cycle 1.1 | Covered |
| FR-7 (precommit verification) | 2+4 | Cycle 2.4 + Step 4.1 | Covered |
| FR-8 (ping-pong TDD) | 3+4 | Phase 3 + Step 4.1 | Covered |
| FR-8a (RED gate) | 3 | Cycle 3.4 | Covered |
| FR-8b (GREEN gate) | 2+4 | Cycle 2.4 + Step 4.1 | Covered |
| FR-8c (role-specific correctors) | 3 | Cycle 3.1 | Covered |
| FR-8d (agent resume) | 4 | Step 4.1 | Covered |
| NFR-1 (context bloat) | 1+2 | Agent caching + plan format | Covered |
| NFR-2 (backward compat) | All | Clean break throughout | Covered |
| NFR-3 (orchestrator model) | 4 | Step 4.1 | Covered |

All 14 requirements covered. No gaps.

### Common Context Consistency

Common Context recall entries (Phase 1 preamble lines 35-41) do not conflict with phase-specific instructions:

- "DO commit all changes before reporting success" — consistent with all phase GREEN requirements
- "DO verify GREEN with `just check && just test`" — all 12 TDD cycles use this exact command
- "DO use file references in dispatch prompts" — Phase 4 Step 4.1 implements exactly this pattern
- "DO NOT edit generated agent files" — no phase instructs direct agent file editing
- "DO NOT substitute built-in agent types" — no phase introduces substitution patterns

No conflicts found between Common Context and phase-specific instructions.

### TDD Phase Compliance (Phases 1-3)

All 12 TDD cycles verified in individual phase reviews:
- RED phases: behaviorally specific assertions with exact expected values/patterns
- GREEN phases: behavior-only, no prescriptive code blocks
- GREEN verification: all 12 cycles use `just check && just test`
- RED/GREEN sequencing: incremental, each cycle extends previous

### General Phase Compliance (Phase 4)

Phase 4 general steps verified in phase-4-review:
- Both steps have Objective, Implementation, Expected Outcome, Error Conditions, Validation
- Model assignment correct: opus for all architectural artifacts
- Design decision coverage explicit with D-1 through D-6 checklist
- D+B hybrid compliance added to validation checklist (fixed in phase-4-review)

### LLM Failure Mode Scan (Cross-Phase)

- **Vacuity:** No vacuous items found across phases. Each cycle adds distinct, non-composable behavior.
- **Dependency ordering:** Foundation-first within each phase. No cross-phase ordering violations.
- **Density:** 4 cycles per TDD phase is appropriate (each covers 1 independent behavioral concern). Phase 4 has 2 steps grouping related prose artifacts.
- **Checkpoint spacing:** 14 total items across 4 phases. Outline checkpoint plan specifies light checkpoints at Phase 1→2, 2→3, 3→4 boundaries, and a full checkpoint after Phase 4. Spacing is within bounds (no gap >10 items without checkpoint).
- **File growth:**
  - `test_prepare_runbook_agents.py` (354 lines): Phase 1 adds ~80-120 lines → projects to ~434-474. Proactive split guidance added in Phase 1 preamble (phase-1-review fix).
  - `test_prepare_runbook_tdd_agents.py` (new): Phase 3 creates fresh, no growth risk.
  - `prepare-runbook.py` (~1500 lines): Growth across Phases 1-3. Key constraints note to monitor growth and extract helpers before splitting.

## Fixes Applied

- Phase 3 preamble: Updated `test_prepare_runbook_agents.py` line count from "(353 lines)" to "(354 lines)" — cross-phase consistency with Phase 1
- Phase 4 Step 4.2: Updated refactor.md line count from "(244 lines → ~274 lines)" to "(243 lines → ~273 lines)" — matches actual file

## Unfixable Issues (Escalation Required)

None — all issues fixed.

---

**Ready for next step**: Yes
