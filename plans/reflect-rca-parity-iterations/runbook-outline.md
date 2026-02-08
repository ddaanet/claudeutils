# Runbook Outline: Parity Test Quality Gap Fixes

**Source:** `design.md` (8 design decisions, 3-tier sequencing)
**Plan:** reflect-rca-parity-iterations
**Status:** Outline (awaiting review)

---

## Requirements Mapping

| Requirement | Design Decision | Implementation Phase/Step | Notes |
|-------------|-----------------|---------------------------|-------|
| FR-1: Conformance test cycles mandatory when design has external reference | DD-1 | Phase 3, Step 9 (plan-tdd + plan-adhoc) | Depends on Gap 4 completion |
| FR-2: Test descriptions for conformance work include exact expected strings | DD-2 | Phase 2, Steps 4-5 (testing.md + workflow-advanced.md) | Prerequisite for Gap 1 |
| FR-3: `--test`/`--lint` commit modes restricted to WIP commits | DD-3 | Phase 1, Step 1 (commit skill) | — |
| FR-4: Planning-time file size awareness | DD-4 | Phase 2, Steps 6-7 (plan-tdd + plan-adhoc) | — |
| FR-5: Vet alignment includes conformance checking as standard | DD-5 | Phase 3, Step 10 (vet-fix-agent) | — |
| FR-6: Defense-in-depth pattern documented | DD-6 | Phase 2, Step 3 (defense-in-depth.md) | — |
| FR-7: Skill step tool-call-first convention audit | DD-7 | Phase 2, Step 8 (N1 manual audit) | Conditional: lint ships only if audit supports |
| FR-8: D+B empirical validation | DD-8 | Phase 1, Step 2 (N3 execution test) | — |
| NFR-1: No orchestration pipeline changes | All decisions | All phases | Conformance via existing mechanisms |
| NFR-2: Changes apply going forward | All decisions | All phases | No retroactive plan fixes |
| NFR-3: Hard limits or no limits | DD-3, DD-4, DD-7 | Phases 1-2 | WIP-only restriction, 350-line threshold, conditional lint

---

## Phase Structure

### Phase 1: Tier 1 Fixes (Trivial, Immediate)

**Estimated scope:** 2 steps, ~20 lines of changes, single session
**Model:** Haiku execution
**Complexity:** Low (single-file edits with clear instructions)

**Steps:**
1. Gap 5: Add WIP-only restriction to commit skill `--test`/`--lint` flags
2. N3: D+B empirical validation (execute `/commit`, document evidence)

**Checkpoint:** Both steps complete → commit Tier 1 changes → proceed to Phase 2

### Phase 2: Tier 2 Fixes (Low Complexity, Parallelizable)

**Estimated scope:** 6 steps, ~200 lines total (4 edits + 2 new files), single session
**Model:** Haiku execution (steps 3-7), Sonnet for N1 audit (step 8)
**Complexity:** Low-moderate (multi-file edits, clear scope, internal sequencing for Gap 4 → Gap 1)

**Steps:**
3. Q5: Create defense-in-depth.md decision document (~70 lines)
4. Gap 4 (testing.md): Expand "Conformance Validation for Migrations" section (~20 lines added)
5. Gap 4 (workflow-advanced.md): Add conformance exception to "Prose Test Descriptions Save Tokens" (~10 lines added)
6. Gap 2 (plan-tdd): Add planning-time file size awareness convention (~15 lines)
7. Gap 2 (plan-adhoc): Add planning-time file size awareness convention (~15 lines)
8. N1: Manual skill audit → decision on lint script (sonnet-driven audit, conditional script creation)

**Checkpoint:** Steps 3-8 complete → commit Tier 2 changes → proceed to Phase 3

**Parallelization:**
- Steps 3, 6, 7, 8 are fully independent and can run in parallel
- Steps 4-5 (Gap 4) are prerequisites for Phase 3 Step 9 (Gap 1)
- All Phase 2 steps must complete before Phase 3 starts

**Conditional output:**
- Step 8 produces either: (a) audit report + `scripts/check_skill_steps.py` + justfile entry, OR (b) audit report documenting decision not to ship lint

### Phase 3: Tier 3 Fixes (Moderate, Depends on Gap 4)

**Estimated scope:** 2 steps, ~40 lines total, single session
**Model:** Haiku execution
**Complexity:** Moderate (multi-file skill edits, dependency on Gap 4 completion)

**Steps:**
9. Gap 1 (plan-tdd + plan-adhoc): Mandatory conformance test cycles when design has external reference (~30 lines across 2 files)
10. N2 (vet-fix-agent): Add explicit alignment criterion to standard review criteria (~5 lines)

**Checkpoint:** Steps 9-10 complete → commit Tier 3 changes → proceed to Phase 4

**Dependency:** Phase 3 starts AFTER Phase 2 is fully committed. Gap 4 (Phase 2 Steps 4-5) defines what "precise test descriptions" means; Gap 1 (Phase 3 Step 9) mandates when they're required.

### Phase 4: Memory Index Update

**Estimated scope:** 1 step, ~15 lines added, single session
**Model:** Haiku execution
**Complexity:** Low (append-only operation)

**Steps:**
11. Add memory-index entries for all new decisions: defense-in-depth.md, conformance precision (testing.md + workflow-advanced.md), WIP-only restriction (commit skill), planning-time file size awareness (plan-tdd + plan-adhoc), vet alignment (vet-fix-agent), tool-call-first audit decision

**Checkpoint:** Memory index updated → commit Phase 4 → runbook complete

**Coverage verification:** All files from design Implementation Notes table (lines 179-191) covered across Phases 1-4

---

## Key Decisions Reference

| Decision | Location in Design | Implementation Phase/Step |
|----------|-------------------|---------------------------|
| DD-1: Conformance tests as executable contracts | Lines 64-77 | Phase 3, Step 9 |
| DD-2: Conformance exception to prose test descriptions | Lines 79-93 | Phase 2, Steps 4-5 |
| DD-3: WIP-only restriction for `--test`/`--lint` | Lines 95-106 | Phase 1, Step 1 |
| DD-4: Planning-time file size awareness | Lines 108-119 | Phase 2, Steps 6-7 |
| DD-5: Vet alignment as standard practice | Lines 121-135 | Phase 3, Step 10 |
| DD-6: Defense-in-depth documentation | Lines 137-146 | Phase 2, Step 3 |
| DD-7: Skill step tool-call-first audit | Lines 148-158 | Phase 2, Step 8 |
| DD-8: D+B empirical validation | Lines 160-172 | Phase 1, Step 2 |

---

## Complexity Distribution

| Phase | Lines Changed | Files Affected | Parallelizable | Model | Estimated Time |
|-------|--------------|----------------|----------------|-------|----------------|
| Phase 1 | ~20 | 2 (commit skill + validation report) | Sequential | Haiku | 10-15 min |
| Phase 2 | ~200 | 6 (4 edits + 2 new) | Partial (steps 3-7 parallel, step 8 independent) | Haiku (3-7), Sonnet (8) | 30-45 min |
| Phase 3 | ~40 | 3 (plan-tdd, plan-adhoc, vet-fix-agent) | Sequential | Haiku | 15-20 min |
| Phase 4 | ~15 | 1 (memory-index.md) | N/A | Haiku | 5 min |

**Total:** ~275 lines across 9 files (6 edits + 3 new), 11 steps, estimated 60-85 minutes execution time.

---

## Critical Constraints

**Sequencing:**
- Phase 1 → Phase 2 (no dependency, but Tier 1 first per design sequencing)
- Phase 2 → Phase 3 (Gap 4 must land before Gap 1 — Phase 2 must be fully committed)
- Phase 3 → Phase 4 (memory index last — covers all prior changes)

**Cross-phase dependency:** Gap 4 (Phase 2 Steps 4-5) is a prerequisite for Gap 1 (Phase 3 Step 9). The conformance precision guidance must exist before mandating conformance test cycles.

**Model selection:**
- Phases 1, 2 (except step 8), 3, 4: Haiku
- Phase 2 Step 8 (N1 audit): Sonnet (requires semantic judgment for audit categorization)

**Validation:**
- After each phase: commit via `/commit` (default precommit validation)
- No intermediate vet checkpoints (changes are guidance updates, not code)

**Conditional logic:**
- N1 audit (Phase 2 Step 8): Creates `scripts/check_skill_steps.py` + justfile entry ONLY if audit finds ≥80% compliance with few false positives (per DD-7)
- Otherwise: Documents decision not to ship lint in audit report
- Audit report documents both path (lint ships or not) with rationale

**File coverage verification:**
All 11 files from design Implementation Notes table (lines 179-191) are addressed:
- Phase 1: commit/SKILL.md, d-b-validation.md (new)
- Phase 2: defense-in-depth.md (new), testing.md, workflow-advanced.md, plan-tdd/SKILL.md, plan-adhoc/SKILL.md, check_skill_steps.py (conditional), justfile (conditional)
- Phase 3: plan-tdd/SKILL.md, plan-adhoc/SKILL.md, vet-fix-agent.md
- Phase 4: memory-index.md

---

## Open Questions

None. All design decisions resolved per `outline.md`.

---

## Notes

- This outline was generated after tier assessment determined Tier 3 (full runbook) was appropriate
- All file paths verified via Glob during Point 0.5 discovery
- Design document provides detailed rationale for each decision (lines 64-172)
- Implementation notes table (design lines 179-191) provides file-level change details — all 11 files covered across 4 phases
- Out of scope items (design lines 263-271): no orchestration changes, no persistent test artifacts, no retroactive fixes, no pre-write hooks, no D+B changes, no concurrent pipeline evolution

---

## Expansion Guidance

The following recommendations should be incorporated during full runbook expansion:

**Consolidation candidates:**
- None identified — Phase 1 and Phase 4 are already minimal (2 steps and 1 step respectively)
- All phases represent logically distinct work tiers and should remain separate

**Cycle expansion:**
- Phase 1 Step 1: Reference design lines 95-106 for exact WIP-only restriction language
- Phase 1 Step 2: Include all three gate verifications (Gate A Read, Gate B git diff, validation execution) with evidence capture
- Phase 2 Steps 4-5: Include the example contrast table from DD-2 (design lines 86-91) in expanded cycles
- Phase 2 Step 3: Reference design lines 137-146 for defense-in-depth layering structure
- Phase 2 Step 8: Audit must catalog three categories (compliant, legitimately exempt, non-compliant) per DD-7
- Phase 3 Step 9: Reference DD-1 (design lines 64-77) for conformance test cycle requirements
- Phase 3 Step 10: Reference DD-5 (design lines 121-135) for alignment criterion language

**Checkpoint guidance:**
- After Phase 2: Verify Gap 4 changes (steps 4-5) are committed before proceeding to Phase 3
- After Phase 3: Verify all 9 changed/new files are committed before memory index update
- No vet checkpoints needed — guidance document changes validated by precommit only

**References to include:**
- Design lines 179-191: Implementation Notes table with file-level change details
- Design lines 64-172: All 8 design decisions with full rationale
- Design line 58: Dependency graph showing Gap 4 → Gap 1 sequencing
- Design lines 202-238: Affected Files Detail section for exact change locations

**Critical sequencing reminder:**
- Phase 2 Steps 4-5 (Gap 4) MUST be committed before Phase 3 Step 9 (Gap 1) begins
- This is a knowledge dependency, not a file dependency — Gap 1 references the conformance precision guidance that Gap 4 creates

**Conditional branch handling:**
- Phase 2 Step 8 (N1 audit) has two possible outcomes — expanded cycle should include clear branching logic with success criteria (≥80% compliance) from DD-7 line 154
