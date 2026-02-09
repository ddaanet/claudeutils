# Runbook Review: Parity Test Quality Gap Fixes

**Scope**: Complete runbook assembled at `plans/reflect-rca-parity-iterations/runbook.md`
**Date**: 2026-02-08T17:45:00Z

## Summary

Reviewed 4-phase, 11-step runbook addressing 5 RCA gaps and 3 Opus concerns through guidance updates, convention changes, and conditional tooling. Runbook is well-structured with clear dependencies, accurate metadata, and comprehensive implementation guidance.

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

None.

### Major Issues

None.

### Minor Issues

#### 1. Path Inconsistency in Design Reference (Step 2)

**Location**: runbook.md:189 (Step 2 report path)

**Issue**: Step 2 references report path as `plans/reflect-rca-parity-iterations/reports/d-b-validation.md`, but design.md:188 uses `plans/reflect-rca-prose-gates/reports/d-b-validation.md`.

**Evidence**:
- Runbook line 189, 217: `plans/reflect-rca-parity-iterations/reports/d-b-validation.md`
- Design line 169, 188: `plans/reflect-rca-prose-gates/reports/d-b-validation.md`

**Recommendation**: Use runbook path (`reflect-rca-parity-iterations`). The D+B fix was implemented under `reflect-rca-prose-gates/` job, but empirical validation belongs to the current job tracking parity gap fixes.

**Impact**: Low - Does not block execution. Executor will use runbook path, not design path.

#### 2. Outline Review Status Missing in Report Structure

**Location**: runbook.md:34 (Metadata section)

**Note**: Metadata line 10 shows "Reviewed: 2026-02-08 (runbook-outline-review-agent, phase vet reviews)", confirming outline was reviewed. However, runbook review agent instructions specify a dedicated "Outline Validation" section for runbooks. This is not a runbook (it's a general-workflow runbook without a preceding outline needing validation).

**Clarification**: This runbook did have an outline (`outline.md`), but the "Outline Validation" section applies only when reviewing phase-expanded runbooks derived from a previously-validated outline. This runbook was assembled from design, not expanded from outline. No issue.

**Action**: None needed.

## Requirements Validation

All 8 FR requirements and 3 NFR requirements from design.md Common Context are addressed:

| Requirement | Status | Evidence |
|-------------|--------|----------|
| FR-1: Conformance test cycles mandatory | Satisfied | Step 9 (plan-tdd, plan-adhoc updates with trigger condition) |
| FR-2: Test descriptions with exact strings | Satisfied | Steps 4-5 (testing.md, workflow-advanced.md conformance exception) |
| FR-3: `--test`/`--lint` WIP-only restriction | Satisfied | Step 1 (commit skill flag scope clarification) |
| FR-4: Planning-time file size awareness | Satisfied | Steps 6-7 (plan-tdd, plan-adhoc convention with 350-line threshold) |
| FR-5: Vet alignment standard criterion | Satisfied | Step 10 (vet-fix-agent alignment addition) |
| FR-6: Defense-in-depth pattern documented | Satisfied | Step 3 (new decision doc with 4-layer pattern) |
| FR-7: Skill step tool-call-first audit | Satisfied | Step 8 (manual audit with conditional lint decision) |
| FR-8: D+B empirical validation | Satisfied | Step 2 (commit execution with gate verification) |
| NFR-1: No orchestration pipeline changes | Satisfied | All changes via existing mechanisms (skills, agents, decision docs) |
| NFR-2: Changes apply going forward | Satisfied | No retroactive fixes mentioned, all guidance-level changes |
| NFR-3: Hard limits or no limits | Satisfied | Step 8 conditional on ≥80% threshold, ships as hard fail or not at all |

**Gaps**: None. All requirements satisfied by implementation steps.

## Outline Validation

**Outline Review Status**: Present at `plans/reflect-rca-parity-iterations/reports/runbook-outline-review.md`

This runbook was NOT expanded from the outline in incremental phases. The outline served as planning artifact, then design was produced, then runbook was generated from design (not outline). The outline-review validated structural approach and decision resolution.

**Requirements Coverage** (from outline.md):
- All 7 gaps from outline (Gap 1, 2, 4, 5, N1, N2, N3, Q5) are addressed by runbook steps
- Outline resolved 5 decisions (D1-D3, Q1-Q5) - all reflected in design decisions DD-1 through DD-8
- Tier sequencing from outline matches runbook Phase grouping

**Alignment**: Runbook correctly implements outline structure with 3-tier phasing and Gap 4 → Gap 1 dependency.

---

## Positive Observations

**Dependency Management**:
- Gap 4 prerequisite for Gap 1 explicitly documented in Phase 2 checkpoint (line 625-627) and Phase 3 context (line 635, 645-653)
- Phase 2 Steps 4-5 must be committed before Phase 3 Step 9 — clearly stated
- Dependency reasoning explained (Gap 4 defines "precise test descriptions", Gap 1 mandates when required)

**Metadata Accuracy**:
- Total steps: 11 (verified by counting Step 1-11 headers)
- Model assignments: Haiku for Steps 1-7, 9-11; Sonnet for Step 8 (semantic categorization) — justified
- Step dependencies: Accurate topology (Phase 1 sequential, Phase 2 partially parallel with 4-5 pair, Phase 3 sequential after Phase 2, Phase 4 final)
- Parallelization guidance: Steps 3, 6, 7, 8 marked as fully independent (verified — different files, no shared dependencies)

**File Path Validation**:
- All 7 prerequisite files verified to exist (metadata lines 41-48)
- All target files for edits exist (verified via Glob)
- Report directory pattern consistent (`plans/reflect-rca-parity-iterations/reports/step-N-execution.md`)

**Conditional Logic Clarity**:
- Step 8 conditional output clearly specified: Path A (ship lint if ≥80%) vs Path B (don't ship if <80%)
- Decision threshold explicit (80% compliance, <10% false positives)
- Outputs for each path documented (audit report + script + justfile OR audit report with decision rationale)

**Implementation Guidance Precision**:
- Each step includes: Objective, Design Reference (DD-N), Current State, Changes Required, Implementation, Expected Outcome, Validation, Success Criteria, Error Conditions
- DD references traceable to design.md (verified: DD-1 line 64-77, DD-2 line 79-93, DD-3 line 95-106, etc.)
- Examples provided where clarity needed (Step 1: TDD workflow pattern update, Step 4: contrast table, Step 6: notation example)

**Cross-Phase Coherence**:
- Phase 1 outputs feed Phase 2 (Step 1 changes committed via Step 2)
- Phase 2 outputs prerequisite for Phase 3 (Gap 4 in Steps 4-5 enables Gap 1 in Step 9)
- Phase 4 (Step 11) indexes all prior phase changes (coverage list explicitly enumerates 6 items from Phases 1-3)

**Error Handling**:
- Step 2 "Unexpected Result Handling" comprehensive (lines 201-206) — covers gate failures, precommit errors, session.md missing, commit failures
- Escalation paths clear (haiku → sonnet for ambiguity/mismatch, sonnet → user for threshold/conflict)
- Validation criteria measurable (file exists, line count, content elements present)

**Checkpoint Gates**:
- Each phase ends with completion criteria (lines 224-230, 614-628, 803-815, 921-931)
- Verification steps explicit (e.g., Phase 2 checkpoint requires Gap 4 committed before Phase 3)
- Success criteria include both file-level (exists, line count) and content-level (elements present) checks

## Recommendations

**For Step 2 (D+B Validation):**
- Consider using `agent-core/bin/task-context.sh` pattern to recover session where commit skill was last modified, providing additional context for D+B validation review.
- Optional: Include commit skill modification date in validation report for temporal context.

**For Step 8 (N1 Audit):**
- Audit report should explicitly list skills audited (file paths) for traceability.
- If shipping lint (Path A), include script test procedure: run on all skills, verify no false positives beyond those marked with exemption comment.

**For Step 11 (Memory Index):**
- Template shows `##` section headers for new files. Verify `defense-in-depth.md` and `n1-audit.md` sections don't already exist before creating.
- Entry keyword richness excellent ("layered mitigation", "exact expected strings", "350-line threshold") — maintain this pattern.

**General:**
- Runbook references design.md extensively (DD-1 through DD-8) — ensure design.md remains accessible during execution (already in prerequisites, verified).
- Step 9 spans 2 files (plan-tdd, plan-adhoc) — consider tracking completion per-file in execution report (e.g., "plan-tdd: ✓, plan-adhoc: ✓").

## Next Steps

**Immediate:**
1. Proceed with runbook execution (all gates passed)
2. Use `/orchestrate plans/reflect-rca-parity-iterations` to begin Phase 1

**During Execution:**
1. At Phase 2 checkpoint (after Step 8): Verify Gap 4 changes (Steps 4-5) committed before proceeding to Phase 3
2. At Step 8: If lint ships (≥80% compliance), test script on all skills before committing
3. At Step 11: Verify no duplicate `##` sections in memory-index.md before appending

**Post-Execution:**
1. Update agents/jobs.md: Change status from `designed` to `complete`
2. Archive execution reports in git (all under `plans/reflect-rca-parity-iterations/reports/`)
3. Verify all 8 design decisions (DD-1 through DD-8) reflected in updated files
