# Runbook Review: Phase 1 — Agent Caching Model

**Artifact**: `plans/orchestrate-evolution/runbook-phase-1.md`
**Date**: 2026-02-24T00:00:00Z
**Mode**: review + fix-all
**Phase types**: TDD (4 cycles)

## Summary

Phase 1 is a well-structured TDD phase covering the agent caching model restructure across 4 incremental cycles. RED assertions are behaviorally specific throughout. GREEN phases describe behavior without prescriptive code. Three issues found: GREEN verification commands omitted the lint gate (all 4 cycles), projected test file growth exceeds the 400-line threshold with no split guidance, and one location hint was misleading (line number pointed to wrong function). All issues fixed.

**Overall Assessment**: Ready

## Findings

### Critical Issues

None.

### Major Issues

1. **GREEN verification missing lint gate (all 4 cycles)**
   - Location: Cycles 1.1, 1.2, 1.3, 1.4 — "Verify GREEN" lines
   - Problem: All cycles specified `just lint` as a separate "Verify lint" step followed by `pytest tests/test_prepare_runbook_agents.py -v` as "Verify GREEN". Running lint and tests as separate gates creates a loophole where an executor can commit after the test passes but before lint runs. Recall artifact explicitly documents this failure mode: "GREEN verification command must be `just check && just test`."
   - Fix: Collapsed "Verify lint" + "Verify GREEN" + "Verify no regression" into single `just check && just test` command for all 4 cycles.
   - **Status**: FIXED

2. **Test file growth exceeds 400-line threshold with no split guidance**
   - Location: Phase preamble
   - Problem: `tests/test_prepare_runbook_agents.py` is 354 lines. 4 new test functions (~20-30 lines each) project to 434-474 lines, exceeding the 400-line enforcement threshold (noted in outline at line 42 and in learnings). No conditional split instruction was present in the phase file, meaning an executor would hit the threshold at Cycle 1.3 or 1.4 with no guidance.
   - Fix: Added "File growth constraint" note to phase preamble instructing executor to check line count before Cycle 1.3 and extract to `tests/test_prepare_runbook_agent_caching.py` if over 380 lines.
   - **Status**: FIXED

### Minor Issues

1. **Misleading location hint in Cycle 1.1 GREEN**
   - Location: Cycle 1.1, GREEN phase Changes section, first file entry
   - Problem: Location hint said "around line 858" for `generate_agent_frontmatter`. Line 844 is `generate_agent_frontmatter`; line 858 is `generate_phase_agent`. The hint named the wrong function relative to its actual line number, which could cause an executor to look at the wrong function.
   - Fix: Updated hint to read "line 858 (`generate_phase_agent` function — rename/replace this function)" — matches actual location and function name.
   - **Status**: FIXED

## Fixes Applied

- Cycle 1.1 Verify GREEN: replaced `just lint` + `pytest tests/test_prepare_runbook_agents.py -v` + `just test` with `just check && just test`
- Cycle 1.2 Verify GREEN: same consolidation
- Cycle 1.3 Verify GREEN: same consolidation
- Cycle 1.4 Verify GREEN: same consolidation
- Phase preamble: added "File growth constraint" paragraph with check threshold (380 lines) and split target (`test_prepare_runbook_agent_caching.py`)
- Cycle 1.1 GREEN location hint: corrected line 858 annotation to identify `generate_phase_agent` (the function to replace)

## Unfixable Issues (Escalation Required)

None — all issues fixed.

---

**Ready for next step**: Yes
