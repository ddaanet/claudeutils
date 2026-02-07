# Design Review: Memory Index Recall

**Design Document**: plans/memory-index-recall/design.md
**Review Date**: 2026-02-08T12:00:00Z
**Reviewer**: design-vet-agent (opus)

## Summary

The design presents a well-structured retrospective analysis pipeline for measuring memory-index effectiveness. It defines 8 functional requirements, 7 design decisions with clear rationale, and a modular architecture that fits existing codebase patterns. The design is consistent with the validated outline and addresses all outline review findings (baseline comparison, success criteria, temporal constraints). Documentation Perimeter referenced non-existent files and infrastructure table had incorrect function names — both fixed.

**Overall Assessment**: Ready

## Issues Found and Fixed

### Critical Issues

None found.

### Major Issues

1. **Documentation Perimeter references non-existent files**
   - Problem: `agents/decisions/architecture.md` does not exist (actual file: `agents/decisions/data-processing.md`). Exploration reports `plans/memory-index-recall/reports/explore-instrumentation.md` and `plans/memory-index-recall/reports/explore-jsonl-format.md` do not exist in this worktree.
   - Impact: Planner would fail to load required reading, potentially missing module patterns and path handling conventions. Missing explore reports would block JSONL format verification context.
   - Fix Applied: Replaced `architecture.md` with `data-processing.md`, removed non-existent explore reports, added `cli.md` for CLI pattern reference.

### Minor Issues

1. **Incorrect function name in infrastructure table**
   - Problem: Design referenced `discovery.list_sessions()` but actual function is `discovery.list_top_level_sessions()`.
   - Fix Applied: Corrected to `discovery.list_top_level_sessions()`.

2. **Incorrect module for `get_project_history_dir`**
   - Problem: Design referenced `discovery.get_project_history_dir()` but function is in `paths` module.
   - Fix Applied: Corrected to `paths.get_project_history_dir()`.

3. **Missing `__init__.py` in module table**
   - Problem: New `recall/` subpackage needs `__init__.py` per project convention (minimal init). Module table omitted it.
   - Fix Applied: Added `__init__.py` row to module table with project convention note.

4. **No CLI integration pattern guidance**
   - Problem: Design specified `recall/cli.py` but didn't explain how it integrates with the main click group. Existing `statusline` and `account` subpackages follow a specific pattern.
   - Fix Applied: Added CLI integration pattern note referencing `statusline` and `account` patterns.

## Requirements Alignment

**Requirements Source:** Inline (design.md Requirements section)

| Requirement | Addressed | Design Reference |
|-------------|-----------|------------------|
| FR-1 | Yes | D-1: Tool Call Extraction |
| FR-2 | Yes | D-2: Memory-Index Parser |
| FR-3 | Yes | D-3: Session Topic Classification |
| FR-4 | Yes | D-4: Relevance Scoring |
| FR-5 | Yes | D-5: Recall Calculation |
| FR-6 | Yes | D-5: Discovery pattern classification table |
| FR-7 | Yes | D-6: Report Format |
| FR-8 | Yes | D-7: CLI Integration |
| NFR-1 | Yes | D-1: Placement note about future promotion |
| NFR-2 | Yes | Architecture: local session JSONL files, no API calls |
| NFR-3 | Yes | D-1: Verification note; Implementation Notes: graceful handling pattern from existing infra |

**Gaps:** None. All requirements traceable to design elements.

## Positive Observations

- **Strong outline-to-design traceability**: All outline review findings (baseline comparison, success criteria, research hypothesis, temporal constraints, discovery patterns) are addressed in the design.
- **Pragmatic special section handling (D-2)**: Explicitly excluding "Behavioral Rules" and "Technical Decisions" sections from recall analysis with clear rationale (ambient context, no clear Read target) prevents false negatives.
- **Pipeline dependency analysis**: Explicitly stating which stages are independent (1-3) and which depend on others (4 on 2+3, 5 on 1+4) guides implementation ordering and potential parallelization.
- **Concrete JSONL format example**: Including the exact JSON structure in D-1 gives the planner an unambiguous specification, with appropriate caveat about verification.
- **Existing infrastructure reuse**: Identifying 6 reusable components from the existing codebase minimizes new code and ensures consistency.
- **Calibration methodology**: The threshold calibration approach (manual pilot on 5 sessions, F1 optimization) is practical and well-scoped.
- **User-directed pattern**: Upgrading the outline's "Ambiguous" category to "User-directed" is a concrete improvement — it identifies a specific confounding factor rather than a vague catch-all.

## Recommendations

1. **Index versioning**: The outline mentioned tracking "index version per session (git commit hash at session timestamp)" and the outline review flagged this. The design doesn't address versioning. Consider whether the planner should track which memory-index version was active during each analyzed session, since entries added recently wouldn't apply to older sessions.

2. **Stopword list specification**: D-3 mentions removing stopwords but doesn't specify the list. Consider whether the planner should define this or if it's appropriately deferred to implementation.

3. **Success criteria from outline not in design**: The outline defines specific thresholds (recall >=50%, lift >=20%, direct discovery >70%). The design's D-6 report format includes the metrics but doesn't reference these thresholds. The report generator could flag results against these criteria. This is acceptable as an implementation detail but worth noting.

## Next Steps

1. Route to `/plan-adhoc` as specified in design Next Steps
2. Planner should load required reading from Documentation Perimeter (now corrected)
3. First implementation step should verify JSONL format against real session files as noted in Implementation Notes
