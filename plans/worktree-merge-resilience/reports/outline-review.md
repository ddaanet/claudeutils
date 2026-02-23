# Outline Review: worktree-merge-resilience

**Artifact**: plans/worktree-merge-resilience/outline.md
**Date**: 2026-02-23
**Mode**: review + fix-all

## Summary

The outline correctly identifies the two-layer defense approach (prevention + detection) and grounds the design in codebase reality. The resolver fix is well-scoped and the ours-wins strategy is consistent with existing conventions. Two major gaps existed: the pipeline integration underspecified how validation reaches all 5 state machine paths, and the detection checks did not cover the primary failure mode from brief.md (bullets misplaced under wrong heading, not trailing orphans). Both fixed.

**Overall Assessment**: Needs Iteration

## Requirements Traceability

| Requirement | Outline Section | Coverage | Notes |
|-------------|-----------------|----------|-------|
| FR-1: Detect orphaned content | Detection: Post-merge validation | Complete | Three checks cover orphaned, misplaced, and duplicate content |
| FR-2: Heading-aware merge | Prevention: Heading-aware learnings resolver | Complete | Entry-level dedup replacing line-set dedup |
| FR-3: Integration into merge pipeline | Pipeline integration | Complete | Option A (single insertion in _phase4) covers all 5 state paths |
| NFR-1: Block on detection | Pipeline integration (On failure) | Complete | Exit non-zero, emit line numbers |
| NFR-2: No false positives on clean files | False positive prevention | Complete | Preamble alignment, heuristic constraints, clean-file test fixture |

**Traceability Assessment**: All requirements covered after fixes.

## Review Findings

### Critical Issues

None.

### Major Issues

1. **Pipeline integration underspecified for state machine**
   - Location: Pipeline integration section
   - Problem: Outline said "all merge paths converge before _phase4" and suggested inserting validation "after file resolution, before commit." In reality, `merge()` has 5 distinct paths through its state machine, and 4 of them call `_phase4` directly without any shared pre-phase4 convergence point. A single insertion "between resolution and commit" would only work if placed inside `_phase4` itself, which the outline did not specify.
   - Fix: Added explicit state machine path analysis (5 paths enumerated) and two options with Option A (insert at top of `_phase4`) as preferred approach.
   - **Status**: FIXED

2. **Detection check #3 did not cover brief.md failure mode**
   - Location: Detection checks, item 3
   - Problem: Original "Trailing orphans" check described content after the last heading's body. But brief.md's actual failure was bullets from entries X/Y/Z appended under entry W's heading — not trailing content, but *misplaced* content under the wrong heading. The original check would miss this entirely.
   - Fix: Replaced "Trailing orphans" with "Misplaced content under wrong heading" check that addresses the actual observed failure mode. Added acknowledgment that this is heuristic-based and harder than the outline originally suggested. Moved to Open Questions for design discussion.
   - **Status**: FIXED

3. **NFR-2 (false positives) not addressed**
   - Location: (missing)
   - Problem: No explicit section addressing how the validator avoids false positives on clean learnings files.
   - Fix: Added "False positive prevention (NFR-2)" subsection with preamble alignment note, heuristic constraints, and clean-file test fixture requirement.
   - **Status**: FIXED

### Minor Issues

1. **Line number reference inaccurate**
   - Location: Prevention section, Affected file line
   - Problem: "replace lines 155-162" — line 155 is `ours_content = _git(...)` which is not part of the dedup logic. The line-set dedup logic starts at line 156 (`ours_lines = set(...)`).
   - Fix: Changed to "replace lines 156-162"
   - **Status**: FIXED

2. **Preamble definition mismatched existing validator**
   - Location: Detection section, structural invariant
   - Problem: Outline said "first 10 lines + `---` separator" but `extract_titles()` in learnings.py only skips the first 10 lines (line 30: `if i <= 10: continue`). The `---` separator is not part of the validator's preamble boundary. Using a different preamble definition would create divergence and potential false positives.
   - Fix: Changed to "first 10 lines, consistent with `extract_titles()` skip logic"
   - **Status**: FIXED

3. **No testing approach despite "tests for both" in scope**
   - Location: Scope section
   - Problem: Scope declares tests are in-scope but no section describes what tests or where they go.
   - Fix: Added "Testing approach" section with resolver tests, validator tests, and integration test, each referencing existing test files.
   - **Status**: FIXED

4. **Duplicate headings check framing unclear**
   - Location: Detection checks, item 2
   - Problem: Listed as a new check to implement, but this already exists in `validate()` via `extract_titles()`. Unclear whether new code is needed.
   - Fix: Added clarification that this is existing behavior, no new implementation needed, just confirming it runs post-merge.
   - **Status**: FIXED

5. **Open questions claimed "None" despite design uncertainty**
   - Location: Open questions section
   - Problem: The "misplaced content" detection heuristic has real design uncertainty — how to distinguish legitimate multi-bullet entries from orphaned content without a heading. Claiming no open questions is premature.
   - Fix: Added open question about detection fidelity and alternative simpler invariants.
   - **Status**: FIXED

## Fixes Applied

- Line 13: "lines 155-162" changed to "lines 156-162" (accurate line reference)
- Lines 22-27: Replaced preamble definition and all 3 detection checks — aligned preamble with `extract_titles()`, replaced trailing orphans with misplaced-content check, clarified duplicate headings is existing
- Lines 33-37: Rewrote pipeline integration with state machine analysis and Option A/B
- After line 39: Added "False positive prevention (NFR-2)" subsection
- After scope IN/OUT: Added "Testing approach" section
- Lines 53-54: Replaced "None" open questions with misplaced-content detection fidelity question

## Positive Observations

- Two-layer defense (prevention + detection) is sound architectural thinking — resolver fix reduces orphan frequency, validator catches any that slip through
- Ours-wins strategy is correctly cross-referenced to D-5 (session.md strategy consistency)
- Edge cases for the resolver (same heading different body, preamble lines) are well considered
- Scope boundaries are clear and appropriate — session.md, custom merge drivers, and rebase strategy correctly excluded
- Block-not-warn decision is well-justified with cost asymmetry argument

## Recommendations

- The "misplaced content under wrong heading" check is the hardest part of this design. Consider whether a simpler structural invariant (e.g., count of `## When` headings must equal count of `- Anti-pattern:` occurrences) is sufficient. This should be a user discussion topic.
- The resolver's entry-level parsing approach should define what constitutes an "entry" precisely — heading line regex, body termination condition (next heading or EOF), handling of blank lines between entries.
- Consider whether the validation should also run during `just precommit` (not just merge pipeline) to catch manual-edit orphans.

---

**Ready for user presentation**: Yes — all issues fixed, one open question flagged for design discussion (misplaced content heuristic).
