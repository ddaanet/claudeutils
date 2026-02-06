# Vet Review: Phase 4 Runbook (learnings-consolidation)

**Scope**: `plans/learnings-consolidation/runbook-phase-4.md`
**Date**: 2026-02-06T00:00:00Z

## Summary

Phase 4 runbook provides comprehensive testing specification for the learnings consolidation system. Test coverage maps directly to design Component 6 requirements with 7 test categories (A-G). Git mocking strategy uses subprocess patches correctly. Edge cases are well-covered. Manual validation procedures are detailed but have minor clarity gaps. Agent validation checklists are thorough but lack concrete comparison guidance.

**Overall Assessment**: Needs Minor Changes

## Issues Found

### Critical Issues

None.

### Major Issues

1. **Missing preamble skip validation in parsing tests**
   - Location: Step 4.1, test category A (lines 36-69)
   - Problem: `test_extract_h2_headers()` creates 10 preamble lines but doesn't verify they're actually skipped in extraction. The test shows line 11 as "first extracted" but doesn't assert that lines 1-10 are excluded from results.
   - Fix: Add assertion checking that extracted headers don't include any from lines 1-10, or verify header line numbers are all >10

2. **Integration test git mock incomplete for staleness**
   - Location: Step 4.1, integration test (lines 248-293)
   - Problem: `test_full_pipeline` mocks git log -p for staleness detection but doesn't verify the staleness calculation appears in output. Mock returns consolidation date "2026-01-20" but test only checks for presence of "**Last consolidation:**" header, not the actual value.
   - Fix: Add assertion verifying staleness calculation: `assert "12 active days ago" in output` or similar based on mocked dates

3. **Agent validation lacks comparison methodology**
   - Location: Step 4.2, section 3 (lines 382-440)
   - Problem: Validation checklists reference "compare with remember skill steps 1-4a" and "cross-reference Implementation Components 2 and 3" but don't specify how to perform comparison. Agent definitions won't match skill text verbatim (they're adapted, not copied), so validator needs concrete guidance on what level of fidelity is required.
   - Suggestion: Add comparison guidance — e.g., "Verify protocol steps are present in same order, terminology matches, thresholds are identical" or provide example diff showing acceptable vs unacceptable deviation

### Minor Issues

1. **Test function naming inconsistency**
   - Location: Step 4.1, test category E (line 219)
   - Note: `test_boundary_exactly_7_days()` duplicates the boundary test from `test_freshness_filter_includes_gte_7_days()` (which already includes 7-day boundary at line 217). Either consolidate or clarify that one tests filter function, other tests threshold constant.

2. **Staleness fallback wording mismatch**
   - Location: Step 4.1, test category C (lines 158-170)
   - Note: Test expects `last_consolidation is None` with comment "Script formats this as 'N/A (...)'" but doesn't verify the actual formatting. Design § D-2 shows format as "N/A (no prior consolidation detected)" but test stops at None check. Consider adding formatting test or clarifying that formatting happens in calling code.

3. **Manual test branching guidance vague**
   - Location: Step 4.2, manual handoff trigger test (lines 346-371)
   - Note: Option A suggests "add temp entries to exceed 150 lines (Do this in a test branch)" but doesn't specify cleanup procedure or branch naming. Could lead to test branches proliferating in repo.

4. **Unexpected result handling references wrong step**
   - Location: Step 4.2, unexpected result handling (lines 466-482)
   - Note: "Compare handoff step 4c thresholds with design D-3" — correct, but also should reference Implementation Component 4 (handoff skill modification) which specifies the actual step content. Minor precision issue.

5. **Success criteria duplication**
   - Location: Step 4.1 and 4.2 success criteria (lines 315-322, 484-492)
   - Note: Step 4.1 includes "All tests pass: pytest tests/test_learning_ages.py" (line 322) and step 4.2 duplicates it (line 485). Step 4.2 also says "All unit tests pass" (line 485) — these are redundant with step 4.1 completion.

## Positive Observations

**Strong test categorization structure:**
- 7 test categories (A-G) map exactly to design Component 6 specification
- Categories progress logically from parsing → calculation → detection → integration
- Each category has clear scope and test cases

**Comprehensive git mocking:**
- Uses `@patch('subprocess.run')` correctly for all git operations
- Mocks cover git blame (line attribution), git log (active days), git log -p (staleness)
- Edge cases well-represented: merge commits (line 115-128), entry added today (line 105-112), no prior consolidation (line 158-170)

**Good edge case coverage:**
- Boundary conditions tested (exactly 7 days, exactly 150 lines, exactly 14 days)
- Error handling paths covered (missing file, git unavailable, malformed content)
- Zero-value cases tested (0 active days, no consolidation history)

**Clear validation structure:**
- Step 4.1 focuses on automated tests
- Step 4.2 separates manual procedures, agent validation, and integration
- Success criteria are explicit and measurable

**Realistic integration test:**
- Full pipeline test (lines 248-293) includes complete mock scenario with multiple git operations
- Tests interaction between components (parsing → blame → log → output formatting)
- Uses `tmp_path` fixture correctly for file isolation

## Recommendations

1. **Strengthen parsing test validation**
   - Add explicit assertion that preamble lines (1-10) are excluded from extraction
   - Verify line number tracking is correct (headers[0][0] == 11, not just header text)

2. **Complete integration test assertions**
   - Verify staleness calculation value in output, not just header presence
   - Add assertion for active days count in entry sections
   - Check that all 4 summary fields contain plausible values

3. **Add agent validation comparison examples**
   - Provide example diff showing acceptable protocol adaptation (e.g., skill uses numbered list, agent uses prose)
   - Specify threshold value comparison (must be exact match vs design)
   - Clarify expectation: semantic equivalence or verbatim match?

4. **Consolidate or clarify boundary tests**
   - Either merge `test_boundary_exactly_7_days()` into `test_freshness_filter_includes_gte_7_days()` or add comment explaining why separate (e.g., one tests function, other tests constant)

5. **Add manual test cleanup guidance**
   - Specify test branch naming convention (e.g., `test/consolidation-size-trigger`)
   - Add cleanup step: delete test branch after validation
   - Consider using git stash instead of branch for temporary changes

## Next Steps

1. Apply fixes to runbook-phase-4.md:
   - Add preamble skip assertion to parsing test (major issue #1)
   - Add staleness value assertion to integration test (major issue #2)
   - Add agent validation comparison guidance (major issue #3)
2. Address minor issues if time permits (test naming, cleanup guidance)
3. Ready for execution after fixes applied

---

**Review conducted by vet-agent (sonnet)**
