# Runbook Outline Review: userpromptsubmit-topic

**Artifact**: plans/userpromptsubmit-topic/runbook-outline.md
**Design**: plans/userpromptsubmit-topic/outline.md
**Requirements**: plans/userpromptsubmit-topic/requirements.md
**Date**: 2026-02-28
**Mode**: review + fix-all

## Summary

The outline is well-structured with clean phase progression (matching pipeline -> caching -> hook integration), complete requirements coverage, and no vacuous cycles. All 13 TDD cycles test real branch points. Fixes applied: resolved a deferred implementation decision (heading reconstruction), improved dependency declarations with post-phase state awareness, and added internal caller specificity for API promotions.

**Overall Assessment**: Ready

## Requirements Coverage

| Requirement | Phase | Cycles | Coverage | Notes |
|-------------|-------|--------|----------|-------|
| FR-1 | 1 | 1.1 | Complete | Inverted index from parsed entries |
| FR-2 | 1 | 1.2, 1.3 | Complete | Candidate matching + scoring |
| FR-3 | 1 | 1.4, 1.5 | Complete | Resolution + error handling |
| FR-4 | 2 | 2.1, 2.2, 2.3 | Complete | Cache build, hit, invalidation |
| FR-5 | 3 | 3.1, 3.2, 3.3 | Complete | Hook integration, additive, passthrough |
| FR-6 | 1 | 1.6 | Complete | Entry count cap |
| FR-7 | 1 | 1.7 | Complete | Dual-channel output format |
| NFR-1 | 2 | 2.1, 2.2 | Partial | Cache avoids reparse; no explicit timeout test (deployment constraint) |
| NFR-2 | 3 | 3.2, 3.3 | Complete | Additive + passthrough verification |

**Coverage Assessment**: All functional requirements fully covered. NFR-1 partial — timeout is a deployment constraint better validated by profiling than unit tests.

## Phase Structure Analysis

### Phase Balance

| Phase | Cycles | Complexity | Percentage | Assessment |
|-------|--------|------------|------------|------------|
| 1 | 7 | Medium | 54% | Acceptable — new module with 7 distinct functions |
| 2 | 3 | Low | 23% | Balanced |
| 3 | 3 | Medium | 23% | Balanced |

**Balance Assessment**: Phase 1 at 54% exceeds the 40% guideline but is justified — it builds the entire matching pipeline (7 functions with distinct responsibilities). Splitting would create artificial phase boundaries within tightly coupled build-up. Each cycle adds a real function.

### Complexity Distribution

- Low complexity phases: 1 (Phase 2)
- Medium complexity phases: 2 (Phases 1, 3)
- High complexity phases: 0

**Distribution Assessment**: Appropriate. No high-complexity phases; Phase 2 reuses established caching patterns.

## Review Findings

### Critical Issues

None.

### Major Issues

1. **Heading reconstruction decision deferred to implementation**
   - Location: Phase 1 preamble, heading reconstruction note
   - Problem: Original text said "prefer (a) for clean API if backward-compatible, fall back to (b)" — deferring a design decision to cycle 1.4 GREEN. Two approaches named without commitment.
   - Fix: Resolved to approach (b): try both heading forms (`## When {key}`, `## How to {key}`). `_extract_section` returns empty on miss, making fallback free. No `IndexEntry` model change needed. Simpler, no backward compatibility concern.
   - **Status**: FIXED

### Minor Issues

1. **NFR-1 mapping too narrow**
   - Location: Requirements Mapping table
   - Problem: NFR-1 mapped only to "2.1 (cache performance)" — but cache hit (2.2) also contributes to timeout compliance
   - Fix: Updated to "2.1, 2.2 (cache avoids reparse)"
   - **Status**: FIXED

2. **Missing internal callers for `_extract_section` promotion**
   - Location: Cycle 1.4 GREEN description
   - Problem: Promotion note didn't list internal callers (resolver.py lines 117, 225) that need updating
   - Fix: Added explicit line references for internal callers
   - **Status**: FIXED

3. **Post-phase state missing from Phase 3 dependency**
   - Location: Cycle 3.1 dependency declaration
   - Problem: "Depends on: Phase 1, Phase 2" without noting expected state of those phases' outputs
   - Fix: Added state context: "Phase 1 (complete matching pipeline in topic_matcher.py), Phase 2 (cache layer via get_or_build_index)"
   - **Status**: FIXED

4. **Collapsible cycle candidates not noted**
   - Location: Expansion Guidance section
   - Problem: Cycles 1.5 and 1.6 are thin (1 branch point each) but not flagged for potential consolidation
   - Fix: Added consolidation candidates to Expansion Guidance
   - **Status**: FIXED

## Fixes Applied

- Requirements Mapping: NFR-1 broadened to cover cycles 2.1 and 2.2
- Phase 1 preamble: Heading reconstruction resolved to try-both-forms approach (no model change needed)
- Cycle 1.4 GREEN: Added internal caller line references for `_extract_section` promotion (lines 117, 225)
- Cycle 3.1: Added post-phase state context to dependency declaration
- Expansion Guidance: Restructured with consolidation candidates, cycle expansion details, checkpoint guidance, and reference sections

## Design Alignment

- **Architecture**: Aligned — outline builds `topic_matcher.py` as specified, integrates as parallel detector block per D-3
- **Module structure**: Aligned — all affected files from design covered (new: topic_matcher.py, test files; modified: hook, index_parser, resolver)
- **Key decisions**: All 10 design decisions (D-1 through D-10) referenced appropriately in Key Decisions Reference section. D-8 (dropped), D-10 (calibration — out of scope) correctly excluded from cycle mapping.

## Growth Projection

| File | Current Lines | Estimated Growth | Projected | Status |
|------|--------------|-----------------|-----------|--------|
| topic_matcher.py (new) | 0 | ~210 (7 cycles) | ~210 | OK |
| test_recall_topic_matcher.py (new) | 0 | ~175 (7 cycles) | ~175 | OK |
| test_ups_topic_integration.py (new) | 0 | ~90 (3 cycles) | ~90 | OK |
| userpromptsubmit-shortcuts.py | 958 | ~40 (1 detector block) | ~998 | Already >350, additive only |
| index_parser.py | 186 | ~2 (rename) | ~188 | OK |
| resolver.py | 339 | ~2 (rename) | ~341 | OK |

No new files approach the 350-line threshold. Hook file is already large but receives only a small additive block — no structural split needed.

## Vacuity Assessment

All 13 cycles test real branch points:
- 1.1: Data structure construction (inverted index)
- 1.2: Set membership filtering (candidates)
- 1.3: Numerical ranking + threshold filtering
- 1.4: File I/O + section extraction
- 1.5: Error path handling (2 failure modes)
- 1.6: Collection slicing with ordering preservation
- 1.7: Dual-format output assembly
- 2.1-2.3: Cache lifecycle (create, hit, invalidate)
- 3.1-3.3: Integration behaviors (inject, combine, passthrough)

## Positive Observations

- Clean dependency chain with no circular references
- API promotions handled as side effects of GREEN phases (not separate cycles)
- Recall entries specified per-phase for context priming
- xfail integration test pattern in Phase 3 preamble provides early regression detection
- Complexity assessment is realistic and well-justified
- Key Decisions Reference section provides quick lookup for expanding agents

## Recall Context Applied

Resolved 4 recall entries; all consistent with outline approach:
- "when too many rules in context" — D-6 cap (max 3) addresses the ~150 rule budget
- "when hook fragment alignment needed" — additionalContext reinforces, doesn't contradict fragment content
- "when mapping hook output channel audiences" — D-7 correctly maps additionalContext (agent-only) and systemMessage (user-only)
- "when writing hook user-visible messages" — ~60 char terminal constraint noted in Expansion Guidance for cycle 1.7

---

**Ready for full expansion**: Yes
