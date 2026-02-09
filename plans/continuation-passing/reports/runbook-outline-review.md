# Runbook Outline Review: continuation-passing

**Artifact**: plans/continuation-passing/runbook-outline.md
**Design**: plans/continuation-passing/design.md
**Date**: 2026-02-09
**Mode**: review + fix-all

## Summary

The runbook outline is well-structured with 4 phases covering hook implementation, skill modifications, testing/validation, and documentation. All functional requirements (FR-1 through FR-7) map to specific steps, constraints are addressed, and design decisions are referenced. Main issues were: missing FR-8 from traceability table, insufficient step detail for `Skill` tool additions, Phase 3 complexity underassessed, and sparse expansion guidance. All issues fixed.

**Overall Assessment**: Ready

## Requirements Coverage

| Requirement | Phase | Steps/Cycles | Coverage | Notes |
|-------------|-------|--------------|----------|-------|
| FR-1 | 1 | 1.1-1.3 | Complete | Hook parser with delimiter detection + registry lookup |
| FR-2 | 1 | 1.2 | Complete | Peel-first-pass-remainder protocol |
| FR-3 | 2 | 2.1-2.6 | Complete | Cooperative skill protocol implementation |
| FR-4 | 1 | 1.3 | Complete | Simplified from requirements to `and\n- /skill` |
| FR-5 | 1, 3 | 1.2, 3.5 | Complete | Registry matching + empirical validation (D-7) |
| FR-6 | 2 | 2.1-2.6 | Complete | Convention + explicit prohibition (D-5) |
| FR-7 | 2 | 2.1-2.6 | Complete | Frontmatter + consumption protocol (D-2) |
| FR-8 | -- | -- | Out of scope | Explicitly optional in requirements, deferred |
| NFR-1 | 2 | 2.1-2.6 | Complete | Protocol-based, no downstream coupling |
| NFR-2 | 1 | 1.1, 1.4 | Complete | Frontmatter scanning + registry cache (D-1) |
| NFR-3 | 1, 2 | 1.2, 2.1-2.6 | Complete | Ephemeral lifecycle (D-4) |
| C-1 | 2 | 2.1-2.6 | Complete | Convention-based isolation (D-5) |
| C-2 | 1, 2 | 1.2, 2.1-2.6 | Complete | Empty continuation = terminal |

**Coverage Assessment**: All requirements covered. FR-8 explicitly out of scope with justification.

## Phase Structure Analysis

### Phase Balance

| Phase | Steps | Complexity | Percentage | Assessment |
|-------|-------|------------|------------|------------|
| 1 | 4 | High | 25% | Balanced |
| 2 | 6 | Medium | 33% | Balanced (consolidation candidate noted) |
| 3 | 5 | Medium-High | 28% | Balanced (adjusted from Medium) |
| 4 | 3 | Low | 14% | Trivial (merge candidate) |

**Balance Assessment**: Well-balanced after complexity adjustment. Phase 4 is trivial and noted as consolidation candidate in expansion guidance.

### Complexity Distribution

- **Low complexity phases**: 1 (Phase 4)
- **Medium complexity phases**: 1 (Phase 2)
- **Medium-High complexity phases**: 1 (Phase 3 -- adjusted upward)
- **High complexity phases**: 1 (Phase 1)

**Distribution Assessment**: Appropriate. Complexity increases then decreases across the execution arc. Phase 3 upgraded from Medium to Medium-High to account for empirical validation (3.5) being fundamentally different from standard unit testing.

## Review Findings

### Critical Issues

None.

### Major Issues

1. **FR-8 missing from requirements mapping table**
   - Location: Requirements Mapping section
   - Problem: FR-8 (uncooperative skill wrapping) is explicitly out of scope in design but was absent from the traceability table. Incomplete traceability obscures whether the requirement was forgotten or deliberately excluded.
   - Fix: Added FR-8 row with "Out of scope" coverage and note "Explicitly optional in requirements, deferred"
   - **Status**: FIXED

2. **Missing `Skill` tool addition detail in Phase 2 steps**
   - Location: Phase 2 steps 2.1, 2.4
   - Problem: Design explicitly states /design and /orchestrate need `Skill` added to `allowed-tools` (design section "Skills requiring Skill tool addition"). Step descriptions didn't mention this, risking oversight during execution.
   - Fix: Added explicit `+ add Skill to allowed-tools` to steps 2.1 and 2.4
   - **Status**: FIXED

3. **Phase 3 complexity underassessed**
   - Location: Phase 3 header and Complexity Notes
   - Problem: Phase 3 was rated "Medium" but contains 5 steps mixing unit tests (haiku), integration tests (sonnet), and empirical validation against real user corpus (sonnet). Step 3.5 is fundamentally different from standard testing -- it requires corpus extraction, parser execution, and manual review classification.
   - Fix: Upgraded to "Medium-High", added model-per-step breakdown, expanded complexity notes to explain 3.5's unique nature
   - **Status**: FIXED

### Minor Issues

1. **FR-5 mapping referenced wrong step**
   - Location: Requirements Mapping table, FR-5 row
   - Problem: FR-5 mapped to step 3.1 (parser unit tests) for empirical validation, but empirical validation is step 3.5
   - Fix: Changed mapping from "1.2, 3.1" to "1.2, 3.5"
   - **Status**: FIXED

2. **NFR-2 mapping incomplete**
   - Location: Requirements Mapping table, NFR-2 row
   - Problem: NFR-2 mapped only to step 1.1 but registry caching (step 1.4) is also part of cooperation detection infrastructure
   - Fix: Changed mapping from "1.1" to "1.1, 1.4"
   - **Status**: FIXED

3. **Missing design decision cross-references in mapping table**
   - Location: Requirements Mapping table, Notes column
   - Problem: Mapping notes didn't reference relevant design decisions (D-1 through D-7), making it harder to trace from requirement to design rationale
   - Fix: Added D-* references to relevant rows (FR-5/D-7, FR-6/D-5, FR-7/D-2, NFR-2/D-1, NFR-3/D-4, C-1/D-5)
   - **Status**: FIXED

4. **Missing Coverage column in mapping table**
   - Location: Requirements Mapping table
   - Problem: Table lacked explicit coverage assessment column (Complete/Partial/Missing/Out of scope), requiring reader to infer coverage from Notes
   - Fix: Added Coverage column with explicit status for each requirement
   - **Status**: FIXED

5. **Phase 4 dependency description misleading**
   - Location: Dependencies section, Phase 4
   - Problem: Said "independent (can run in parallel with Phase 3)" but Phase 4 content depends on Phases 1+2 for accuracy. Documentation about hook format and skill protocol must reflect actual implementation.
   - Fix: Clarified "depends on Phases 1+2 for accurate content; can run in parallel with Phase 3 unit tests (3.1-3.3)"
   - **Status**: FIXED

6. **Step descriptions lacked specificity**
   - Location: Phase 1 and Phase 3 step lists
   - Problem: Steps like "1.1: Implement cooperative skill registry builder" lacked context about what the step entails. Expansion benefits from seed detail.
   - Fix: Added parenthetical specifics to all Phase 1 and Phase 3 steps (e.g., "3-source discovery", "8 scenarios per design Component 4")
   - **Status**: FIXED

7. **Design ordering recommendation not acknowledged**
   - Location: Phase 1 header
   - Problem: Design recommends frontmatter-first ordering for safety, but outline puts hook first. Both orderings are valid but the discrepancy should be noted and justified.
   - Fix: Added Note to Phase 1 explaining the ordering choice and confirming both orderings are safe
   - **Status**: FIXED

8. **Expansion guidance too sparse**
   - Location: Expansion Guidance section
   - Problem: Section lacked checkpoint guidance, cycle expansion detail, design reference pointers, and model assignment notes. Insufficient to guide phase expansion without re-reading design.
   - Fix: Rewrote section with consolidation candidates, cycle expansion guidance, checkpoint guidance, references to include, design ordering note, and model assignments
   - **Status**: FIXED

9. **Step 3.5 dependency incorrectly listed**
   - Location: Dependencies section, Phase 3 intra-phase
   - Problem: Listed "3.4-3.5 depend on 3.1-3.3" but 3.5 (empirical validation) is independent of unit tests -- it validates against real corpus, not test infrastructure
   - Fix: Separated to "3.4 depends on 3.1-3.3, 3.5 independent (corpus-based)"
   - **Status**: FIXED

## Fixes Applied

- Requirements Mapping: Added FR-8 row (out of scope), added Coverage column, added D-* decision references, fixed FR-5 step reference (3.1 -> 3.5), expanded NFR-2 mapping to include step 1.4
- Phase 1: Added ordering justification note, expanded step descriptions with implementation specifics
- Phase 2: Added explicit `Skill` tool addition to steps 2.1 and 2.4, clarified 2.5 (--commit flag) and 2.6 (terminal/empty default-exit)
- Phase 3: Upgraded complexity from Medium to Medium-High, added model-per-step breakdown, expanded step descriptions with scenario counts and design references
- Phase 4: Added dependency note (depends on Phases 1+2 for content accuracy)
- Complexity Notes: Updated Phase 3 section to reflect Medium-High with step 3.5 differentiation
- Dependencies: Clarified Phase 2 dependency on hook format, Phase 4 content dependency, Phase 1.4 caching relationship, Phase 3.5 independence
- Expansion Guidance: Complete rewrite with consolidation candidates, cycle expansion, checkpoint guidance, design references, ordering note, model assignments

## Design Alignment

- **Architecture**: Aligned. Three-component structure (hook parser, cooperative protocol, frontmatter declarations) maps to Phases 1, 2, and 2 respectively.
- **Module structure**: Aligned. Hook extension in userpromptsubmit-shortcuts.py, 6 skill files, test modules, documentation fragment.
- **Key decisions**: All 7 decisions (D-1 through D-7) referenced in mapping table and/or Key Decisions Reference section. No contradictions.
- **Implementation ordering**: Outline differs from design recommendation (hook-first vs frontmatter-first) but both are safe. Justification documented in Phase 1 note and expansion guidance.
- **Design review findings**: Incorporated. /orchestrate no-hardcoded-tail-call noted in step 2.4 and Complexity Notes. /design and /orchestrate `Skill` tool addition explicit in steps 2.1 and 2.4.

## Positive Observations

- Requirements mapping is comprehensive with all 13 requirements (FR/NFR/C) traced to specific steps
- Phase structure follows natural implementation flow (infrastructure -> consumers -> validation -> documentation)
- Parallelization opportunities correctly identified (Phase 2 steps, Phase 3 unit tests)
- Key Decisions Reference section provides quick lookup for design rationale during expansion
- Complexity Notes section provides per-phase justification beyond simple High/Medium/Low labels
- Handoff special case (/handoff --commit flag-dependent default exit) correctly identified as special case in both Phase 2 and Complexity Notes

---

**Ready for full expansion**: Yes
