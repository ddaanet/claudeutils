# Deliverable Review: vet-false-positives

**Date:** 2026-03-06
**Methodology:** agents/decisions/deliverable-review.md

## Inventory

| Type | File | Lines (+/-) |
|------|------|-------------|
| Agentic prose | agent-core/agents/corrector.md | +22 / -0 |
| Agentic prose | agent-core/agents/runbook-corrector.md | +20 / -0 |
| Configuration | .claude/settings.json | +29 / -2 |
| Configuration | justfile | +2 / -2 |

**Design conformance:** No design.md exists — classified as Simple (see classification.md). Requirements.md serves as conformance baseline. The two agentic prose files are the specified deliverables. Configuration changes are unspecified — from earlier branch work (plugin exploration, bash prolog fix) with their own commits.

## Critical Findings

None.

## Major Findings

None.

## Minor Findings

### Traceability

1. **Linter-catchable category lacks explicit decision record**
   - File: agent-core/agents/corrector.md:95
   - Axis: conformance (NFR-1)
   - NFR-1 requires every suppression category trace to documented false positive evidence in `agents/decisions/`. Three of four corrector categories have clear traceability:
     - Pre-existing issues → `operational-practices.md` (validate-runbook flags pre-existing files)
     - OUT-scope items → `pipeline-contracts.md` (vet flags out-of-scope items)
     - Pattern-consistent style → `pipeline-contracts.md` (vet escalation calibration — `_git` naming)
   - Linter-catchable issues had no reference in requirements.md. Grounding found in `execution-strategy.md` line 30: "corrector serves as sole semantic review, post-step lint catches mechanical drift" — establishes the division of responsibility. Reference added to requirements.md.
   - **Status: FIXED** — added `execution-strategy.md` reference to requirements.md

### Precision

2. **runbook-corrector "instead" phrasing slightly less specific than corrector**
   - File: agent-core/agents/runbook-corrector.md:122
   - Axis: actionability
   - corrector.md's "instead" directives name specific actions ("Constrain review to lines/sections introduced or modified", "Scan existing patterns in the file/module"). runbook-corrector.md's were slightly more general. Now revised to match corrector's specificity — each "instead" names the artifact to read and the verification to perform.
   - **Status: FIXED** — all 4 "instead" directives in runbook-corrector.md revised

## Gap Analysis

| Requirement | Status | Reference |
|-------------|--------|-----------|
| FR-1: Corrector suppression taxonomy (4 categories) | Covered | corrector.md:79-97 |
| FR-1 acceptance: definition + anti-pattern + instead | Covered | All 4 categories have all 3 elements |
| FR-2: Runbook-corrector suppression taxonomy (4 categories) | Covered | runbook-corrector.md:116-134 |
| FR-2 acceptance: definition + example | Covered | All 4 categories have definition + anti-pattern + instead (exceeds minimum) |
| FR-3: Relationship to status taxonomy | Covered | corrector.md:81,99; runbook-corrector.md:118 |
| FR-3 acceptance: suppression vs classification distinction | Covered | Both contain "Suppression is pre-finding; classification is post-finding" |
| NFR-1: Evidence-grounded categories | Covered | All 8 categories traced; linter-catchable → execution-strategy.md |
| NFR-2: No confidence scoring | Covered | Taxonomy is categorical throughout |
| C-1: Opus model tier | N/A | Classification as Simple; no design session needed |
| C-2: Additive, not restructuring | Covered | New sections only; no structural changes |
| C-3: Line budget | Covered | +22 and +20 lines; categories are 3 lines each |

## Fixes Applied

- requirements.md:64 — added `execution-strategy.md` reference for linter-catchable traceability (NFR-1)
- runbook-corrector.md:122 — revised "instead" to name specific artifact and verification ("Read the outline/design source...")
- runbook-corrector.md:126 — revised "instead" to include matching step ("Match finding text against OUT items...")
- runbook-corrector.md:130 — revised "instead" to reference specific section ("Read the design's architectural decisions section...")
- runbook-corrector.md:134 — revised "instead" to state conformance logic ("If the guidance directs the approach used, suppress...")

## Summary

- **Critical:** 0
- **Major:** 0
- **Minor:** 2 (both FIXED)

All requirements satisfied. Both minor findings resolved: NFR-1 traceability gap closed with execution-strategy.md reference, runbook-corrector "instead" directives revised to match corrector's specificity. No structural or correctness issues.
