# Runbook Review: Phase 2 — `lifecycle` subcommand

**Artifact**: `plans/runbook-quality-gates/runbook-phase-2.md`
**Date**: 2026-02-17T00:00:00Z
**Mode**: review + fix-all
**Phase types**: TDD (3 cycles)

## Summary

Phase 2 implements the `lifecycle` subcommand across 3 TDD cycles (happy path, modify-before-create violation, duplicate creation violation). The overall structure is sound: correct RED/GREEN sequencing, incremental violation detection, appropriate Sonnet model assignment for Python script work, and no prescriptive implementation code in GREEN phases. Three minor prose-specificity issues were found in RED phase assertions and one fixture description ambiguity. All four issues were fixed directly.

**Overall Assessment**: Ready

## Findings

### Critical Issues

None.

### Major Issues

None.

### Minor Issues

1. **Underspecified report path assertion in Cycle 2.1 RED**
   - Location: Cycle 2.1, RED Phase assertions
   - Problem: "Report file written to expected path" does not state the expected path, making the assertion ambiguous — any path would satisfy it.
   - Fix: Replaced with `plans/valid-tdd/reports/validation-lifecycle.md` (job name derived from fixture stem), matching the design's `plans/<job>/reports/validation-{subcommand}.md` pattern.
   - **Status**: FIXED

2. **Fixture cycle reference ambiguity in Cycle 2.1**
   - Location: Cycle 2.1, RED Phase — `**Fixture:**` description
   - Problem: "file `src/module.py` is created in Cycle 1.1 and modified in Cycle 1.2" uses bare cycle numbers that an executor could confuse with Phase 1 of this runbook (which is also Cycles 1.1/1.2).
   - Fix: Added "fixture-internal" qualifier and parenthetical clarifying these are cycle IDs within the fixture content, not Phase 1 of this runbook.
   - **Status**: FIXED

3. **Vague violation file reference in Cycle 2.2 RED**
   - Location: Cycle 2.2, RED Phase assertions
   - Problem: "Report `Violations` section names the file that was modified before creation" and "Report shows the modify cycle ID" do not specify the expected values. An executor could write `assert "file" in report` and satisfy the prose.
   - Fix: Replaced with specific expected strings from the fixture: `src/widget.py`, `Cycle 1.1`, and `no prior creation found`.
   - **Status**: FIXED

4. **Vague violation file reference in Cycle 2.3 RED**
   - Location: Cycle 2.3, RED Phase assertions
   - Problem: "Report `Violations` section names the duplicated file and both creation cycle IDs" does not specify the expected file or cycle IDs. An executor could write `assert "file" in report` and satisfy the prose.
   - Fix: Replaced with specific expected strings from the fixture: `src/module.py`, `Cycle 1.1`, and `Cycle 2.1`.
   - **Status**: FIXED

## Fixes Applied

- Cycle 2.1 RED, assertion 2 — specified report path as `plans/valid-tdd/reports/validation-lifecycle.md`
- Cycle 2.1 RED, Fixture description — added "fixture-internal" qualifier with parenthetical disambiguating from Phase 1 cycle numbers
- Cycle 2.2 RED, assertions 3–4 — replaced vague "names the file" with `src/widget.py`, `Cycle 1.1`, `no prior creation found`
- Cycle 2.3 RED, assertion 3 — replaced vague "names the duplicated file and both creation cycle IDs" with `src/module.py`, `Cycle 1.1`, `Cycle 2.1`

## Unfixable Issues (Escalation Required)

None — all issues fixed.

---

**Ready for next step**: Yes
