# Step 3.3 Execution Report

**Step:** Update /plan-tdd skill
**Date:** 2026-02-04
**Status:** Complete

## Objective

Add runbook outline step (Phase 1.5) and phase-by-phase cycle expansion to /plan-tdd skill.

## Changes Made

### Phase 1.5: Generate Runbook Outline (NEW)

Added new phase between Phase 1 (Intake) and Phase 2 (Analysis):

**Key features:**
- Creates `plans/<feature>/runbook-outline.md` before full cycle generation
- Includes requirements mapping table linking FRs to phases/cycles
- Uses TDD-specific format (cycles, RED/GREEN markers, test-first sequencing)
- Delegates to `runbook-outline-review-agent` (fix-all mode)
- Fallback: ≤3 phases and ≤10 cycles → generate all at once

**Rationale:** Establishes cross-phase structure before expensive cycle generation, enables early feedback on phase boundaries.

### Phase 3: Phase-by-Phase Cycle Expansion (MODIFIED)

Transformed from "Cycle Planning" to iterative phase-by-phase approach:

**Process (for each phase):**
1. Generate phase cycles: `plans/<feature>/runbook-phase-N.md`
2. Review phase cycles: delegate to `tdd-plan-reviewer` (review-only)
3. Apply fixes: planner applies critical/major fixes
4. Finalize phase: proceed to next

**Original content preserved:** Phase 3.1-3.6 subsections contain original cycle planning guidance, now applied per-phase.

**Fallback:** Small runbooks (≤3 phases, ≤10 cycles) skip phase-by-phase.

### Phase 4: Assembly and Metadata (MODIFIED)

Changed from "Runbook Generation" to "Assembly and Metadata":

**New actions:**
1. Concatenate all `runbook-phase-N.md` files into `plans/<feature>/runbook.md`
2. Add metadata sections (Weak Orchestrator Metadata, Common Context)
3. Final cross-phase consistency check (cycle numbering, no duplicates, count validation)

**Note:** References `assemble-runbook.py` script for concatenation (created in Step 3.2).

**Structure template:** Preserved original runbook structure template, now labeled "Assembled Runbook Structure."

### Phase 5: Final Review and Preparation (MODIFIED)

Renamed from "Validation and Review" to "Final Review and Preparation":

**Key changes:**
- Review step now explicitly "holistic" and checks "cross-phase consistency"
- Triggering phrase updated: "Review the **assembled** TDD runbook... for **cross-phase consistency**, prescriptive code, and RED/GREEN violations"
- Report path changed: `runbook-final-review.md` (was `runbook-review.md`)
- Emphasis on "individual phases already reviewed" to clarify scope

**Process unchanged:** Same validation, review, fix application, artifact preparation steps.

## Files Modified

- `agent-core/skills/plan-tdd/SKILL.md` — 4 phases updated, 1 phase added
  - Line 131: Added Phase 1.5 (43 lines)
  - Line 221: Modified Phase 3 title and structure (33 lines added)
  - Line 254: Renamed Phase 3 subsections to "Phase 3.1-3.6: Cycle Planning Guidance (Applied Per-Phase)"
  - Line 378: Modified Phase 4 title and actions (18 lines added)
  - Line 503: Modified Phase 5 title and review step (9 lines changed)

## Validation

**Format check:**
- ✓ Phase numbering coherent (1, 1.5, 2, 3, 4, 5)
- ✓ Phase headers match existing format (`### Phase N:` or `### Phase N.N:`)
- ✓ Subsections properly nested under Phase 3
- ✓ Fallback conditions documented in Phases 1.5 and 3
- ✓ Reference to `assemble-runbook.py` (created in Step 3.2)

**Content alignment with design:**
- ✓ Matches design Section "Skill Changes - /plan-tdd Skill" (lines 455-480)
- ✓ Outline-first approach with TDD-specific format
- ✓ Phase-by-phase expansion with `tdd-plan-reviewer` review
- ✓ Assembly with final holistic review
- ✓ Fallback for small runbooks documented

**Agent references:**
- ✓ `runbook-outline-review-agent` (fix-all mode) — Phase 1.5
- ✓ `tdd-plan-reviewer` (review-only mode) — Phases 3 and 5

## Success Criteria

- [x] Phase 1.5 creates TDD runbook outline
- [x] Phase-by-phase cycle expansion with tdd-plan-reviewer
- [x] Assembly with final review
- [x] Fallback documented for small runbooks
- [x] All changes aligned with design specification

## Notes

**Submodule context:** Changes made in `agent-core/` submodule. File shows as modified in submodule git status, but clean in parent repo.

**Next steps:** Vet review required before commit.
