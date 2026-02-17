# Runbook Review: Phase 4 — red-plausibility subcommand

**Artifact**: `plans/runbook-quality-gates/runbook-phase-4.md`
**Date**: 2026-02-17T00:00:00Z
**Mode**: review + fix-all
**Phase types**: TDD (3 cycles)

## Summary

Phase 4 implements the `red-plausibility` subcommand across 3 TDD cycles covering the 3 exit codes (0=pass, 1=violation, 2=ambiguous). RED phases are specific and well-structured. The critical issue was a semantic flaw in the `created_names` accumulation algorithm: the original description processed current-cycle GREEN before current-cycle RED, which would cause false-positive violations on every normal TDD cycle. Two minor issues also fixed.

**Overall Assessment**: Ready

## Findings

### Major Issues

**1. created_names accumulation algorithm: current cycle's own GREEN incorrectly included**
- Location: Cycle 4.1 GREEN Behavior + Approach; Cycle 4.2 GREEN Approach
- Problem: The algorithm described processing each cycle's GREEN `Action: Create` entries into `created_names` BEFORE checking that same cycle's RED phase. This would flag any normal TDD cycle (where the current GREEN creates the exact function the current RED tests for importing) as a violation — producing false positives on every standard RED/GREEN pair. The correct semantics: when checking cycle N's RED plausibility, `created_names` must contain only cycles 1..N-1 GREENs. Cycle N's own GREEN runs AFTER the RED test is confirmed failing, so it cannot make cycle N's RED already-passing.
- Fix: Updated Behavior section to describe the correct order (check RED first, then accumulate current GREEN into `created_names` for subsequent cycles). Updated both Approach sections (4.1 and 4.2) to explicitly state "prior cycles' GREENs only (cycles 1..N-1, NOT the current cycle's own GREEN)". Updated Changes Action label from "GREEN-before-RED processing" to "sequential RED-check then GREEN-accumulate per cycle".
- **Status**: FIXED

### Minor Issues

**1. Cycle 4.2 RED "Why it fails" hedge language**
- Location: Cycle 4.2 RED phase, "Why it fails" field
- Problem: "may not implement the violation detection branch" hedges where the 4.1 GREEN spec is definitive — happy-path-only behavior is explicitly specified in cycle 4.1.
- Fix: Replaced with "4.1 GREEN spec defines happy-path-only behavior (exit 0 for all plausible inputs); violation detection branch does not exist yet."
- **Status**: FIXED

**2. Cycle 4.3 RED assertion ambiguity: `Ambiguous` section not in design spec**
- Location: Cycle 4.3 RED phase, Assertions
- Problem: "Report `Ambiguous` section" was ambiguous about whether this is a new `## Ambiguous` heading (not defined in design report format) or a subsection of `## Violations`. The design spec defines `## Violations` and `## Summary` only. For ambiguous cases, a separate `## Ambiguous` section is semantically correct (these are not violations), but the assertion needed to make the section name explicit and clarify the structure.
- Fix: Changed to "Report `## Ambiguous` section (sibling to `## Violations`) names the function..." — makes the report structure unambiguous.
- **Status**: FIXED

## Fixes Applied

- Cycle 4.1 GREEN Behavior — replaced flawed GREEN-before-RED accumulation with correct order: check cycle N RED first, then accumulate cycle N GREEN for subsequent cycles
- Cycle 4.1 GREEN Approach — added explicit statement: "Only prior cycles' GREENs (cycles 1..N-1) contribute to `created_names` when evaluating cycle N's RED"
- Cycle 4.1 GREEN Changes Action label — "GREEN-before-RED processing" → "sequential RED-check then GREEN-accumulate per cycle"
- Cycle 4.2 GREEN Approach — "all prior cycles' GREENs (and current cycle's GREEN)" → "prior cycles' GREENs only (cycles 1..N-1, NOT the current cycle's own GREEN)"
- Cycle 4.2 RED "Why it fails" — removed hedge "may not implement"; replaced with definitive statement referencing 4.1 GREEN spec
- Cycle 4.3 RED Assertions — clarified `Ambiguous` section name and structure (sibling `## Ambiguous` section, not subsection of Violations)

## Unfixable Issues (Escalation Required)

None — all issues fixed.

---

**Ready for next step**: Yes
