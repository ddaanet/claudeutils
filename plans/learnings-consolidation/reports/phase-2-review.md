# Vet Review: Phase 2 Runbook (Skill Updates)

**Scope**: Phase 2 runbook for learnings consolidation
**Date**: 2026-02-06

## Summary

Phase 2 runbook defines skill updates for handoff consolidation trigger (step 4c insertion) and remember skill quality guidance (two new sections). Runbook structure is clear with detailed implementation steps, validation procedures, and error handling.

**Overall Assessment**: Needs Minor Changes

## Issues Found

### Critical Issues

None.

### Major Issues

1. **Tool permission syntax mismatch between steps**
   - Location: Step 2.1, lines 62-69 and line 111
   - Problem: Line 69 shows correct syntax `Bash(wc:*, agent-core/bin/learning-ages.py)` but line 111 adds wildcard `Bash(wc:*, agent-core/bin/learning-ages.py:*)` with argument wildcard pattern
   - Fix: Use consistent syntax. Since `learning-ages.py` takes positional argument (learnings.md path), the pattern should include wildcard: `Bash(wc:*, agent-core/bin/learning-ages.py:*)`
   - Impact: Without `:*` wildcard, skill may fail when script is invoked with path argument

2. **Refactor flow description incomplete vs design**
   - Location: Step 2.1, lines 42-47
   - Problem: Runbook describes 5-step refactor flow, but step numbering in text only goes to 4 ("5. Read second report, check for remaining escalations" missing explicit numbering)
   - Expected: Design D-6 specifies 7-step flow (1. detect limit → 2. skip entry → 3. report → 4. handoff reads → 5. spawn refactor → 6. validator autofix → 7. retry with skipped)
   - Fix: Either expand to match design's 7-step detail or clarify that the 5 substeps are the "handoff perspective" (steps handoff executes after reading report)
   - Current text is ambiguous about scope

### Minor Issues

1. **Insertion point line numbers may be stale**
   - Location: Step 2.1, lines 17-19
   - Note: Line references (~115-140, ~160-165) are approximate. If handoff skill has changed since design, these may be incorrect
   - Suggestion: Add note to verify line numbers during execution, or use content-based search patterns instead

2. **Step 4c content contains "brief-reason" placeholder**
   - Location: Step 2.1, line 56
   - Note: Template text "Note in handoff output: 'Consolidation skipped: [brief-reason]'" uses placeholder bracket syntax
   - Suggestion: Clarify this is example format showing where error message should go, not literal text to insert

3. **Validation commands show "head -1" but frontmatter has multiple lines**
   - Location: Step 2.1, line 99
   - Note: `grep "allowed-tools:" | head -1` suggests multiple matches, but there should only be one frontmatter
   - Suggestion: Either remove `head -1` or add comment explaining it's defensive (in case multiple matches from comments)

4. **Cross-reference to design uses section symbol without anchor**
   - Location: Step 2.1, line 253 and elsewhere
   - Note: Design references like "D-1: Step 4c insertion point" are clear, but "§ Implementation Component 4" syntax from design not repeated in runbook
   - Suggestion: Maintain consistent reference style (either "D-X" or "§ Component N" throughout)

5. **Remember skill sections positioned "after step 4, before step 5" but actual step is "4. Apply + Verify"**
   - Location: Step 2.2, lines 142-144, 170, 214
   - Note: Text says "after step 4" but the actual section heading is "### 4. Apply + Verify" (not just "### 4")
   - Suggestion: Use exact section heading in instructions to avoid ambiguity

6. **Success criteria duplicates validation section**
   - Location: Step 2.1, lines 122-131 and lines 73-77
   - Note: Validation checklist (lines 73-77) and Success Criteria (lines 122-131) have overlapping items
   - Suggestion: Consolidate or clarify distinction (validation = inline checks, success = final gate)

## Requirements Validation

No requirements context provided for this runbook review.

## Outline Validation

**Outline Review Status**: Missing

No `plans/learnings-consolidation/reports/runbook-outline-review.md` found. Best practice is to validate outline before runbook expansion for earlier feedback.

**Requirements Coverage**: Design document maps all 12 requirements (FR-1–9, NFR-1–3) to implementation components. Phase 2 runbook covers Implementation Components 4 and 5:
- FR-1: Trigger consolidation conditionally → Step 2.1 (handoff skill modification)
- FR-9: Learnings quality criteria → Step 2.2 (remember skill update)
- NFR-1: Failure handling → Step 2.1 lines 53-57 (try/catch pattern)

Coverage is complete for Phase 2 scope.

---

## Positive Observations

**Strong implementation guidance:**
- Detailed insertion point instructions with content-based landmarks (Step 4b, Step 5 headers)
- Explicit validation commands with expected output
- Error condition table with clear action items
- Success criteria checklist provides clear completion gate

**Good error handling:**
- Try/catch pattern documented (lines 53-57)
- Unexpected result handling section for each step
- Graceful degradation specified (consolidation failure doesn't block handoff)

**Design traceability:**
- Clear references to design decisions (D-1, D-3, D-6, D-7)
- Trigger thresholds explicitly stated and match design D-3 values
- Refactor flow described (though needs clarification per Major Issue #2)

**Quality criteria well-structured:**
- Step 2.2 quality criteria use ✅/❌ visual markers
- Three-category model (principle/incident/meta) is clear
- Staging retention guidance provides concrete keep/consolidate/drop rules

## Recommendations

1. **Standardize tool permission syntax early**: Establish `Bash(script:*)` pattern in step 2.1 line 69 to avoid confusion in error handling section line 111
2. **Expand refactor flow or clarify scope**: Either detail all 7 steps from design D-6 or explicitly note the 5 substeps are "handoff-perspective actions after reading report"
3. **Add note about line number verification**: Line references are approximate — execution should verify by content search not just line count
4. **Consider consolidating validation/success criteria**: Reduce duplication between inline validation (lines 73-77) and final success criteria (lines 122-131)

## Next Steps

1. Fix tool permission syntax inconsistency (Major Issue #1)
2. Clarify refactor flow step count and scope (Major Issue #2)
3. Apply minor fixes if desired (stale line numbers note, placeholder clarification, etc.)
4. Execute Phase 2 runbook after fixes applied
