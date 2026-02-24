# Runbook Review: Phase 3 — TDD Agent Generation

**Artifact**: `plans/orchestrate-evolution/runbook-phase-3.md`
**Date**: 2026-02-24T00:00:00Z
**Mode**: review + fix-all
**Phase types**: TDD (4 cycles)

## Summary

Phase 3 is a well-structured TDD phase covering 4 cycles: TDD agent generation, step file splitting, orchestrator plan role markers, and verify-red.sh creation. GREEN phases are behavior-only with no prescriptive code. RED phases specify concrete assertions. All GREEN verification commands correctly use `just check && just test`. Test file routing correctly targets the new `tests/test_prepare_runbook_tdd_agents.py` file. Three minor issues were found and fixed: a line reference off by 11 lines, a vague assertion qualifier, and a prerequisite that referenced a non-yet-existent directory without fallback guidance.

**Overall Assessment**: Ready (all issues fixed)

- Total items: 4 cycles
- Issues found: 0 critical, 0 major, 3 minor
- Issues fixed: 3
- Unfixable: 0

## Critical Issues

None.

## Major Issues

None.

## Minor Issues

### Issue 1: Cycle 3.2 line reference inaccurate

**Location**: Cycle 3.2, RED Phase Prerequisite
**Problem**: Prerequisite said "Read lines 1020-1062 (`generate_cycle_file`)" — the function actually starts at line 1031. Off by 11 lines; executor could land in unrelated code.
**Fix**: Changed to "lines 1031-1062 (`generate_cycle_file`)" — confirmed against grep output showing `def generate_cycle_file(` at line 1031.
**Status**: FIXED

### Issue 2: Cycle 3.3 assertion qualifier is ambiguous

**Location**: Cycle 3.3, RED Phase Assertions (last bullet)
**Problem**: "Orchestrator plan header `**Agent:**` field lists tester agent for TEST steps, implementer for IMPLEMENT steps (or a mapping section)" — the "or a mapping section" makes the assertion non-binary. An executor could write tests that pass with either structure, and a reviewer could not determine which format to verify.
**Fix**: Replaced with "Orchestrator plan contains a phase-agent mapping table or header that associates TEST steps with the tester agent and IMPLEMENT steps with the implementer agent (e.g., Phase-Agent Mapping section or `**Agent:**` fields per step entry)" — this acknowledges the existing Phase-Agent Mapping pattern in `generate_default_orchestrator` while keeping the assertion verifiable against either concrete implementation form.
**Status**: FIXED

### Issue 3: Cycle 3.4 prerequisite references non-existent directory without fallback

**Location**: Cycle 3.4, RED Phase Prerequisite
**Problem**: "Read `agent-core/skills/orchestrate/scripts/` directory — confirm location for new script." The scripts directory does not currently exist in the codebase (Glob returns empty). While it will exist by Phase 3 execution (Phase 2 creates verify-step.sh and presumably the directory), an executor reading this at review time or early in Phase 3 would hit a dead end with no guidance.
**Fix**: Reordered prerequisite to prioritize the design section read (always available), then clarified the scripts directory is expected to be created in Phase 2 with fallback instruction to create it alongside the script if absent.
**Status**: FIXED

## Validation Checks (All Passed)

**GREEN phase prescriptive code:** None found. All 4 GREEN phases use behavior + approach + hints only.

**GREEN verification commands:** All 4 cycles specify `just check && just test`. PASS.

**RED phase assertion specificity:**
- Cycle 3.1: Specific filenames (`{name}-tester.md` etc.), content matching via distinctive strings from baseline agents, specific section names (`# Plan Context`, `## Design`), role-specific directive keywords. PASS.
- Cycle 3.2: Specific file names (`step-1-1-test.md`, `step-1-1-impl.md`), positive/negative content containment assertions, metadata header presence. PASS.
- Cycle 3.3: Exact format strings specified (e.g., `"- step-1-1-test.md | Phase 1 | sonnet | 25 | TEST"`), alternation ordering asserted, general runbook negative assertion. PASS.
- Cycle 3.4: Specific exit codes (0/1), specific stdout content words ("RED", "CONFIRMED", "FAIL", "REJECTED"), three test scenarios covering the full contract. PASS.

**Test file routing:** Cycle 3.1 routes to `tests/test_prepare_runbook_tdd_agents.py` (new file, not the existing `test_prepare_runbook_agents.py` at 284 lines). Correct — avoids the 400-line threshold issue documented in learnings.

**File path validation:**
- `agent-core/bin/prepare-runbook.py` — EXISTS
- `agent-core/agents/test-driver.md` — EXISTS
- `agent-core/agents/corrector.md` — EXISTS
- `agent-core/skills/orchestrate/scripts/` — does NOT currently exist; this is expected (created in Phase 2); Cycle 3.4 prerequisite updated to reflect this
- `tests/test_prepare_runbook_tdd_agents.py` — does NOT exist (to be created in Cycle 3.1 GREEN — correct for TDD)
- `tests/test_verify_red.py` — does NOT exist (to be created in Cycle 3.4 GREEN — correct for TDD)

**Line hints accuracy:**
- Cycle 3.1: `generate_phase_agent` at line 858 — CONFIRMED
- Cycle 3.1: "after per-phase agent generation loop (around line 1376)" — actual loop ends at 1375, close enough
- Cycle 3.2: `generate_cycle_file` — corrected from 1020 to 1031 (FIXED above)
- Cycle 3.2: "lines 1377-1390" — CONFIRMED
- Cycle 3.3: "lines 1109-1120" — CONFIRMED (cycle items construction loop)
- Cycle 3.3: "lines 1159-1186" — CONFIRMED (step entry output loop)

**E2E vs mocked subprocess (Cycle 3.4):** verify-red.sh runs pytest against Python test files — no git interaction. Test setup creates real Python test files in `tmp_path` and runs the real script via subprocess. This is correct E2E behavior. The recall entry "When Preferring E2E Over Mocked Subprocess" (real git repos for git-interacting scripts) does not require git repos here since verify-red.sh has no git dependency. PASS.

**RED/GREEN sequencing:** All cycles follow correct ordering — test written before implementation, each GREEN passes the RED from its own cycle.

**Dependency ordering:** Cycle 3.1 (agents) → 3.2 (step splitting) → 3.3 (plan markers) → 3.4 (verify-red.sh). Logical foundation-first ordering. Each cycle extends Phase 1 patterns or adds independent new behavior. Phase dependencies correctly noted (Depends on Phase 1 + Phase 2).

**LLM failure modes:**
- Vacuity: None. Each cycle adds distinct, non-composable behavior.
- Density: 4 cycles at medium complexity — appropriate granularity.
- Checkpoints: 4 items within one phase — within the 10-item threshold. Phase boundary checkpoint exists in outline.
- File growth: `test_prepare_runbook_tdd_agents.py` (new file, no growth risk). `test_verify_red.py` (new file, no growth risk). `prepare-runbook.py` will grow; learnings entry notes to monitor.

## Fixes Applied

- Cycle 3.2 prerequisite: "lines 1020-1062" → "lines 1031-1062" (corrected `generate_cycle_file` start line)
- Cycle 3.3 assertion: Replaced "or a mapping section" clause with specific description of both acceptable implementation forms
- Cycle 3.4 prerequisite: Reordered to prioritize design section read; clarified scripts directory will exist post-Phase 2 with fallback instruction

## Unfixable Issues (Escalation Required)

None — all issues fixed.

---

**Ready for next step**: Yes
