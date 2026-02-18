# Runbook Review: Holistic Cross-Phase Review

**Artifact**: `plans/runbook-quality-gates/runbook-phase-{1-5}.md`
**Date**: 2026-02-17T00:00:00Z
**Mode**: review + fix-all (holistic scope — per-phase reviews already done)
**Phase types**: TDD (all 5 phases, 13 cycles total)

## Summary

Cross-phase review of all 5 phase files for consistency, fixture compatibility, file references, requirements coverage, and LLM failure modes. Per-phase reviews are complete; this review focuses exclusively on cross-phase concerns. Three fixable issues found: one misleading skip-flag RED assertion, one orphaned VALID_GENERAL fixture with no cycle usage, and one VALID_TDD specification that is fragmented across phases without a unified cross-phase definition in the Common Context. All three are fixed below.

**Overall Assessment**: Ready

---

## Findings

### Critical Issues

None.

### Major Issues

**1. VALID_TDD cross-phase specification gap**

- Location: Common Context (phase-1.md:37-40), plus phase-specific fixture descriptions in phases 2, 3, 4
- Problem: `VALID_TDD` is used as the happy-path fixture for all four subcommands (Phases 1–4), but its specification is fragmented. Phase 1 defines it with "non-architectural file references and sonnet model tag." Phase 2 adds "src/module.py created in Cycle 1.1, modified in Cycle 1.2." Phase 3 adds "RED phase with `**Test:** \`test_foo\`` and checkpoint 'All 1 tests pass'." Phase 4 adds "Cycle 1.1 RED expects ImportError on src.module; no prior GREEN creates it." An executor building VALID_TDD during Phase 1 has no visibility into Phase 4's constraint. If they omit the ImportError requirement, Phase 4's test will fail unexpectedly — not from a missing feature but from an insufficient fixture.
- Fix: Added a unified VALID_TDD cross-phase specification to the Common Context Fixture Plan section, listing all four constraints together.
- **Status**: FIXED

**2. Skip-flag RED assertion ambiguous for parametrized cases**

- Location: Phase 5, Cycle 5.1 RED Phase, Skip flags section (phase-5.md:32-36)
- Problem: The assertion says "Running `model-tags --skip-model-tags <path>` exits with code 0 without running the check" for ALL 4 parametrized cases. The parametrization covers `--skip-lifecycle`, `--skip-test-counts`, `--skip-red-plausibility` as well — these flags belong to their respective subcommands (`lifecycle`, `test-counts`, `red-plausibility`), not to `model-tags`. An executor reading this literally would invoke `model-tags --skip-model-tags` four times, testing only one case instead of four distinct ones.
- Fix: Clarified the assertion to specify that each parametrized case invokes its own subcommand with its own skip flag (e.g., `lifecycle --skip-lifecycle`, `test-counts --skip-test-counts`, etc.).
- **Status**: FIXED

### Minor Issues

**3. VALID_GENERAL fixture defined but no cycle references it**

- Location: Common Context Fixture Plan (phase-1.md:40), outline fixture table (runbook-outline.md:98)
- Problem: `VALID_GENERAL` is declared in the Fixture Plan as "General steps, correct model tags, no TDD — used by phase 1 (model-tags)." However, no cycle in Phase 1 or any other phase actually uses it. Cycle 1.2 uses `VALID_TDD`, Cycle 1.3 uses `VIOLATION_MODEL_TAGS`. The fixture is listed but is an orphan — executor may create a constant that goes unused, or may be confused about which fixture to use.
- Fix: Removed `VALID_GENERAL` from the Fixture Plan in Common Context and noted that `VALID_TDD` serves as the happy-path fixture for all four subcommands. If `VALID_GENERAL` is needed for a future test, it should be added when that test is defined.
- **Status**: FIXED

---

## Cross-Phase Validation Results

### Item Numbering Consistency
Cycles 1.1–1.3, 2.1–2.3, 3.1–3.3, 4.1–4.3, 5.1 = 13 total. Matches outline. No gaps or duplicates.

### Dependency Ordering
- Phase 2 depends on Phase 1 (declared). No forward references.
- Phase 3 depends on Phase 1 (declared). No forward references.
- Phase 4 depends on Phase 1 (declared). No forward references.
- Phase 5 depends on Phases 1–4 (declared). No forward references.
- Within phases: ordering is foundation-first. No intra-phase dependency violations.

### File Reference Validation
- `agent-core/bin/validate-runbook.py` — new file (correct: all cycles mark it as new/modify)
- `tests/test_validate_runbook.py` — new file (correct: all cycles mark it as new/modify)
- `agent-core/bin/prepare-runbook.py` — exists at line 985 `__main__` guard (verified). All 6 imported functions exist: `parse_frontmatter` (line 63), `extract_cycles` (line 103), `extract_sections` (line 298), `assemble_phase_files` (line 396), `extract_step_metadata` (line 539), `extract_file_references` (line 575).

### Checkpoint Spacing
- Phase 1 checkpoint after 3 cycles (cycle 1.3). Within limit.
- Phase 2 checkpoint after 3 cycles. Within limit.
- Phase 3 checkpoint after 3 cycles. Within limit.
- Phase 4 checkpoint after 3 cycles. Within limit.
- Phase 5 final checkpoint after 1 cycle. Within limit.
- All checkpoints use `just test tests/test_validate_runbook.py`. Consistent.

### Execution Model Tags
All cycles: Sonnet. No cycle modifies architectural files (skills/, fragments/, agents/, workflow-*.md). No model-tag violations.

### Restart Metadata
No phase claims restart required. No agent/hook/plugin/MCP changes. Correct.

### Requirements Coverage
- FR-2 (mechanical): Phases 1 Cycles 1.2–1.3. Covered.
- FR-3: Phase 2 Cycles 2.1–2.3. Covered.
- FR-4 (structural): Phase 4 Cycles 4.1–4.3. Covered.
- FR-4 (semantic, exit 2): Phase 4 Cycle 4.3 (ambiguous case). Covered.
- FR-5: Phase 3 Cycles 3.1–3.3. Covered.
- FR-6: Addressed by design (mandatory uniform execution). No cycles needed. Correct.
- NFR-1: Phase 1 Cycle 1.1 (argparse CLI), Phase 5 Cycle 5.1 (directory input). Covered.
- NFR-2: Phase 5 Cycle 5.1 (skip flags). Covered.

### LLM Failure Modes (Cross-Phase)
- **Vacuity**: No cross-phase vacuous cycles detected. Each cycle adds distinct behavior.
- **Density**: Adjacent cycles test meaningfully different violation types. No collapsible pairs across phase boundaries.
- **Checkpoints**: One per phase, spacing ≤3 cycles. No gaps.
- **File growth**: validate-runbook.py projected ~260 lines, test_validate_runbook.py projected ~245 lines (both under 350-line threshold per outline growth projection). No split needed.

---

## Fixes Applied

- Common Context (phase-1.md) — Added unified VALID_TDD cross-phase specification with all four constraints (model-tags, lifecycle, test-counts, red-plausibility) in one place
- Common Context (phase-1.md) — Removed orphaned VALID_GENERAL from Fixture Plan; added note that VALID_TDD serves all happy-path tests
- Phase 5 Cycle 5.1 RED (phase-5.md) — Clarified skip-flag parametrized assertions to specify each case invokes its own subcommand (not always `model-tags`)

## Unfixable Issues (Escalation Required)

None — all issues fixed.

---

**Ready for next step**: Yes
