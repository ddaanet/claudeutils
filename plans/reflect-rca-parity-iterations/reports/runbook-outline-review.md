# Runbook Outline Review: Parity Test Quality Gap Fixes

**Artifact**: plans/reflect-rca-parity-iterations/runbook-outline.md
**Design**: plans/reflect-rca-parity-iterations/design.md
**Date**: 2026-02-08T19:45:00Z
**Mode**: review + fix-all

## Summary

The outline provides a well-structured 4-phase implementation plan for closing 5 remaining parity test quality gaps plus 3 Opus-identified concerns. The tier-based sequencing aligns with design decisions, and all functional requirements are traced to implementation steps. The original outline had several structural and traceability issues that have been fixed.

**Overall Assessment**: Ready

## Requirements Coverage

| Requirement | Phase | Steps | Coverage | Notes |
|-------------|-------|-------|----------|-------|
| FR-1 | 3 | 9 | Complete | Added DD-1 reference and dependency note |
| FR-2 | 2 | 4-5 | Complete | Added DD-2 reference and prerequisite status |
| FR-3 | 1 | 1 | Complete | Added DD-3 reference |
| FR-4 | 2 | 6-7 | Complete | Added DD-4 reference |
| FR-5 | 3 | 10 | Complete | Added DD-5 reference |
| FR-6 | 2 | 3 | Complete | Added DD-6 reference |
| FR-7 | 2 | 8 | Complete | Added DD-7 reference and conditional note |
| FR-8 | 1 | 2 | Complete | Added DD-8 reference |
| NFR-1 | All | All | Missing | Added to mapping table |
| NFR-2 | All | All | Missing | Added to mapping table |
| NFR-3 | 1-2 | 1, 6-7, 8 | Missing | Added to mapping table with affected decisions |

**Coverage Assessment**: All requirements now covered. NFR-* requirements were missing from original mapping table.

## Phase Structure Analysis

### Phase Balance

| Phase | Steps | Complexity | Percentage | Assessment |
|-------|-------|------------|------------|------------|
| 1 | 2 | Low | 18% | Balanced (Tier 1 trivial work) |
| 2 | 6 | Low-Medium | 55% | Acceptable (parallelizable substeps) |
| 3 | 2 | Medium | 18% | Balanced (depends on Phase 2) |
| 4 | 1 | Low | 9% | Balanced (append-only) |

**Balance Assessment**: Well-balanced. Phase 2 is larger but contains 4 independent substeps (3, 6, 7, 8) that can run in parallel, and 2 dependent substeps (4-5) that are prerequisites for Phase 3.

### Complexity Distribution

- **Low complexity phases**: 2 (Phase 1, Phase 4)
- **Low-medium complexity phases**: 1 (Phase 2)
- **Medium complexity phases**: 1 (Phase 3)
- **High complexity phases**: 0

**Distribution Assessment**: Appropriate. No high-complexity phases. The medium-complexity phase (Phase 3) is correctly sequenced after its prerequisite (Gap 4 in Phase 2).

## Review Findings

### Critical Issues

None found.

### Major Issues

1. **Requirements Mapping Incomplete — NFR-* Requirements Missing**
   - Location: Requirements Mapping section (lines 9-20)
   - Problem: Mapping table included only FR-1 through FR-8, but design specifies three NFR-* requirements (NFR-1, NFR-2, NFR-3) that are constraints applying across all phases
   - Fix: Added NFR-1, NFR-2, NFR-3 rows to mapping table with appropriate scope notes
   - **Status**: FIXED

2. **Requirements Mapping Missing DD-* Design Decision References**
   - Location: Requirements Mapping section (lines 9-20)
   - Problem: Table had only two columns (Requirement, Implementation Phase/Step) but didn't show which design decision addresses each requirement
   - Fix: Added "Design Decision" column mapping each FR-* to corresponding DD-*, added "Notes" column for dependency/scope clarifications
   - **Status**: FIXED

3. **Phase 2 Step Numbering Inconsistency**
   - Location: Requirements Mapping table rows for FR-1, FR-2, FR-4 referencing Phase 2/3 steps
   - Problem: Requirements Mapping referenced "Phase 2, Step 4" and "Phase 3, Step 7-8" but Phase Structure shows different numbering (Phase 2 has steps 3-8, Phase 3 has steps 9-10)
   - Fix: Corrected all step number references to match Phase Structure actual numbering (FR-2 → Steps 4-5, FR-1 → Step 9)
   - **Status**: FIXED

4. **Parallelization Guidance Incomplete**
   - Location: Phase 2 checkpoint note (line 54)
   - Problem: Stated "Steps 3-7 can run in parallel (no dependencies)" but Gap 4 (steps 4-5) is a prerequisite for Gap 1 (Phase 3 step 9) per design dependency graph (line 58)
   - Fix: Replaced "Note" with structured "Parallelization" section clarifying which steps are fully independent (3, 6, 7, 8) and which are prerequisites for Phase 3 (4-5)
   - **Status**: FIXED

### Minor Issues

1. **Cross-Phase Dependency Not Explicit in Critical Constraints**
   - Location: Critical Constraints → Sequencing section (lines 113-116)
   - Problem: Listed phase-to-phase sequencing but didn't explicitly state the Gap 4 → Gap 1 cross-phase dependency
   - Fix: Added "Cross-phase dependency" subsection explicitly stating Gap 4 (Phase 2 Steps 4-5) is prerequisite for Gap 1 (Phase 3 Step 9) with rationale
   - **Status**: FIXED

2. **File Coverage Verification Implicit**
   - Location: Critical Constraints → Conditional logic section (lines 127-129)
   - Problem: Outline mentioned "Implementation notes table (design lines 179-191)" in Notes but didn't verify all 11 rows were covered in phase structure
   - Fix: Added "File coverage verification" subsection listing all 11 files and their phases, confirming complete coverage
   - **Status**: FIXED

3. **Conditional Logic Documentation Incomplete**
   - Location: Critical Constraints → Conditional logic section (lines 127-129)
   - Problem: Documented N1 audit produces conditional output but didn't note that audit report should document both paths (lint ships or not)
   - Fix: Added clarification that audit report documents decision rationale for both outcomes
   - **Status**: FIXED

4. **Phase 2 Conditional Output Not Explicit**
   - Location: Phase 2 checkpoint section (line 52)
   - Problem: Step 8 (N1 audit) has conditional output but this wasn't stated in the phase section, only in Critical Constraints
   - Fix: Added "Conditional output" subsection to Phase 2 listing both possible outcomes from Step 8
   - **Status**: FIXED

5. **Out of Scope Items Not Documented**
   - Location: Notes section (lines 159-165)
   - Problem: Design specifies 6 out-of-scope items (lines 263-271) but outline didn't document what's NOT being addressed
   - Fix: Added out-of-scope items to Notes section for completeness
   - **Status**: FIXED

## Fixes Applied

- Requirements Mapping table — added NFR-1, NFR-2, NFR-3 rows with scope notes
- Requirements Mapping table — added "Design Decision" and "Notes" columns for traceability
- Requirements Mapping table — corrected all step number references to match Phase Structure
- Phase 2 section — replaced "Note" with structured "Parallelization" section clarifying independence vs prerequisites
- Phase 2 section — added "Conditional output" subsection documenting N1 audit outcomes
- Critical Constraints → Sequencing — added "Cross-phase dependency" subsection for Gap 4 → Gap 1
- Critical Constraints → Conditional logic — added "File coverage verification" subsection listing all 11 files by phase
- Critical Constraints → Conditional logic — clarified audit report documents both paths
- Notes section — added out-of-scope items from design lines 263-271
- Expansion Guidance section — appended comprehensive guidance for runbook expansion with cycle references, checkpoint guidance, sequencing reminders, and conditional branch handling

## Design Alignment

**Architecture**: Aligned. No new systems, all changes are guidance updates to existing files.

**Module structure**: N/A (no code modules, only guidance documents).

**Key decisions**: All 8 design decisions (DD-1 through DD-8) are explicitly referenced in Requirements Mapping table and covered in phase structure.

**Change topology**: Phase structure correctly implements the dependency graph from design line 58 (Gap 4 → Gap 1, all others independent).

**Tier sequencing**: Phase 1 (Tier 1), Phase 2 (Tier 2), Phase 3 (Tier 3), Phase 4 (Memory Index) matches design sequencing (lines 243-258).

**File coverage**: All 11 files from design Implementation Notes table (lines 179-191) are addressed across the 4 phases.

## Dependency Sanity

**No circular dependencies**: Verified. Gap 4 → Gap 1 is a one-way knowledge dependency (conformance precision guidance must exist before mandating conformance test cycles).

**Prerequisites satisfied**: Gap 4 (Phase 2 Steps 4-5) completes before Gap 1 (Phase 3 Step 9) begins. Phase boundaries enforce this ordering.

**External dependencies**: None. All changes are internal guidance updates.

**Missing dependencies**: None identified. The Gap 4 → Gap 1 dependency is now explicitly documented in both the Phase 2 Parallelization section and Critical Constraints Cross-phase dependency section.

## Positive Observations

- **Clear tier-based sequencing**: The 3-tier structure (trivial → low-complexity → moderate) provides natural phase boundaries and enables parallelization within Phase 2.
- **Comprehensive requirements traceability**: All FR-* requirements map to specific design decisions and implementation steps.
- **Explicit parallelization opportunities**: Phase 2 identifies 4 independent substeps (3, 6, 7, 8) that can run concurrently, optimizing execution time.
- **Conservative complexity assessment**: Phase 2 marked as "Low-Moderate" despite being 55% of total work because substeps are parallelizable and have clear scope.
- **Conditional logic well-documented**: N1 audit decision point (DD-7) has clear success criteria (≥80% compliance) and fallback path documented.
- **Memory index sequenced last**: Phase 4 correctly defers memory index updates until all prior changes are committed, ensuring complete coverage.
- **Expansion Guidance comprehensive**: Added section provides actionable guidance for cycle expansion with specific design line references, checkpoint reminders, and conditional branch handling.

## Recommendations

1. **During Phase 2 execution**: Commit steps 4-5 (Gap 4) before proceeding to Phase 3, even if other Phase 2 steps are still in progress. The Gap 4 → Gap 1 dependency is a knowledge dependency that benefits from atomic commits.

2. **N1 audit approach**: Use a structured audit report with three categories (compliant, legitimately exempt, non-compliant) to support the ≥80% decision threshold. This provides clear evidence for the conditional branch.

3. **Vet checkpoint consideration**: Although outline states "No intermediate vet checkpoints," consider vet review after Phase 2 Step 3 (defense-in-depth.md) since it's a new decision document that will be referenced by future work. This is optional, not required.

4. **Commit message discipline**: Use distinct commit messages for each phase to maintain traceability between tier structure and git history. Example: "🏗️ Tier 1 parity gap fixes (Gap 5 + N3)" for Phase 1.

---

**Ready for full expansion**: Yes

All requirements are traced, phase structure is balanced, dependencies are satisfied, and all issues have been fixed. The outline provides a solid foundation for runbook expansion.
