# Runbook Review: Phase 2 — Orchestrator plan and verification

**Artifact**: `plans/orchestrate-evolution/runbook-phase-2.md`
**Date**: 2026-02-24T00:00:00Z
**Mode**: review + fix-all
**Phase types**: TDD (4 cycles)

## Summary

Phase 2 is a well-structured TDD phase covering orchestrator plan format restructuring (Cycles 2.1-2.3) and verify-step.sh creation with E2E tests (Cycle 2.4). RED phases have specific, behaviorally concrete assertions. GREEN phases are clean — no prescriptive code blocks, behavior-only guidance. Dependency ordering is correct: format first, then boundaries/summaries, then max_turns extraction, then the new shell script.

Two issues found: all four GREEN phases used the wrong lint verification command (`just lint` + `just test` separately instead of `just check && just test`), and Cycle 2.4's prerequisite referenced a non-existent directory as "currently empty." Both fixed.

**Overall Assessment**: Ready

## Findings

### Critical Issues

None.

### Major Issues

1. **GREEN verification command wrong across all cycles**
   - Location: Cycles 2.1, 2.2, 2.3, 2.4 — Verify GREEN sections
   - Problem: All four cycles used the three-line pattern `just lint` / `pytest <file> -v` / `just test`. Per recall artifact "When GREEN Phase Verification Includes Lint": the required pattern is `just check && just test`. Using `just lint` is incorrect — `just lint` internally calls `run-pytest` (tests run twice when followed by `just test`). The separate `pytest <file>` call was redundant. Using `just check` (style-only, no tests) followed by `just test` is the correct fail-fast pattern.
   - Fix: Replaced all three-line patterns with single `**Verify GREEN:** \`just check && just test\`` line in each cycle.
   - **Status**: FIXED

### Minor Issues

1. **Cycle 2.4 prerequisite references non-existent directory as "currently empty"**
   - Location: Cycle 2.4 RED Phase, Prerequisite line
   - Problem: `agent-core/skills/orchestrate/scripts/` directory does not exist (not empty — absent entirely). The prerequisite told the executor to "Read `agent-core/skills/orchestrate/scripts/` directory (currently empty)" which would produce a confusing error.
   - Fix: Updated prerequisite to read `agent-core/skills/orchestrate/SKILL.md` instead (which exists), with instruction to confirm the `scripts/` subdirectory doesn't exist yet and will be created.
   - **Status**: FIXED

## Fixes Applied

- Cycle 2.1 GREEN — Replaced `just lint` / `pytest tests/test_prepare_runbook_orchestrator.py -v` / `just test` with `just check && just test`
- Cycle 2.2 GREEN — Same replacement
- Cycle 2.3 GREEN — Same replacement
- Cycle 2.4 GREEN — Replaced `just lint` / `pytest tests/test_verify_step.py -v` / `just test` with `just check && just test`
- Cycle 2.4 RED prerequisite — Corrected directory reference from non-existent `scripts/` to existing `SKILL.md` with clarifying note

## Additional Validation Notes

**TDD discipline:** Clean throughout. GREEN phases contain only behavior descriptions and approach hints. No python code blocks in GREEN phases. RED phases have specific, named test functions, expected failure messages, and clear "why it fails" rationale.

**RED/GREEN sequencing:** Correctly incremental. Cycle 2.1 establishes structured format → Cycle 2.2 adds PHASE_BOUNDARY/summaries (RED explicitly depends on 2.1 output) → Cycle 2.3 adds max_turns (RED explicitly depends on 2.1 format) → Cycle 2.4 is independent (new file, new test module).

**Dependency ordering:** Foundation-first. Format before enrichment before extraction before new script. No cross-phase dependency violations (Cycle 2.1's dependency on Phase 1 agent naming is correctly declared in the phase preamble, not expected to be resolved within this phase).

**File references:**
- `agent-core/bin/prepare-runbook.py` — exists, line references valid (1065, 878 confirmed)
- `tests/test_prepare_runbook_orchestrator.py` — exists
- `tests/test_verify_step.py` — correctly marked as "(create)"
- `agent-core/skills/orchestrate/scripts/verify-step.sh` — correctly marked as "(create)"
- `agent-core/skills/orchestrate/SKILL.md` — exists (confirmed)

**LLM failure modes:**
- Vacuity: None. Each cycle tests a distinct behavioral property (format structure, boundary markers, max_turns field, script exit codes). No vacuous assertions.
- Density: 4 cycles is appropriate for 4 independent behavioral concerns. No over-granularity.
- Checkpoint spacing: Phase 2 has no internal checkpoint (4 cycles). The outline checkpoint plan places a light checkpoint at the Phase 2→3 boundary. Acceptable.
- File growth: `test_prepare_runbook_orchestrator.py` currently 201 lines. 3 new test functions (Cycles 2.1-2.3) at ~20-30 lines each → projected ~260-290 lines. Well under the 350-line warning threshold.

**Shell script E2E testing (Cycle 2.4):** Test setup specifies real git repos in `tmp_path` using `git init`/`git add`/`git commit`. Submodule test creates two repos. This matches the recall constraint "When Preferring E2E Over Mocked Subprocess." The precommit test note (hard to isolate) is documented inline with a suggested fallback (mock `just precommit` as a simple script in fixture) — acceptable.

**Requirement coverage:**
- FR-7 (precommit verification): Covered by Cycle 2.4 (verify-step.sh checks git status + submodule + just precommit)
- FR-8b (GREEN gate): Cycle 2.4 verify-step.sh provides the git-clean + submodule component; composed with `just test` per design
- NFR-1 (context bloat): Cycles 2.1-2.3 implement structured plan format that eliminates prose instructions
- NFR-3 (orchestrator model): Cycles 2.1-2.3 add `**Type:**` and `**Agent:**` header fields

## Unfixable Issues (Escalation Required)

None — all issues fixed.

---

**Ready for next step**: Yes
