# Outline Review: remove-fuzzy-recall

**Artifact**: plans/remove-fuzzy-recall/outline.md
**Date**: 2026-03-14
**Mode**: review + fix-all

## Summary

Well-structured outline with thorough function-level detail, clear sequencing rationale, and good scope boundaries. One major gap: artifact-form error message (FR-2) was not specified despite the brief explicitly differentiating two failure modes. Fixed inline. Minor clarity improvements applied to D3, D4, and scope OUT rationale.

**Overall Assessment**: Ready

## Requirements Traceability

Requirements extracted from brief.md (no numbered FR-* identifiers in brief; mapped from Proposed Change section):

| Requirement | Outline Section | Coverage | Notes |
|-------------|-----------------|----------|-------|
| Keyword-form error message | D3, Affected Functions | Complete | Message matches brief specification |
| Artifact-form error message | D3 | Complete (after fix) | Was missing; added differentiated artifact-form message |
| Remove `_get_suggestions()` | Affected Functions (resolver.py) | Complete | Marked for deletion |
| Remove `_handle_no_match()` | Affected Functions (resolver.py) | Complete | Marked for deletion |
| Hard failure + guidance | D1, D2, D3 | Complete | Exact matching with context-differentiated errors |
| Update tests expecting "Did you mean:" | Test Changes | Complete | 3 tests rewritten, 2 deleted |

**Traceability Assessment**: All requirements covered after fix.

## Scope-to-Component Traceability

Outline uses file-based grouping rather than named components. Mapping scope IN items to implementation sections:

| Scope IN Item | Implementation Section | Notes |
|---------------|----------------------|-------|
| `resolver.py` — 3 fuzzy paths | Affected Functions: resolver.py | All 3 paths specified (D1 trigger, D2 heading, deleted functions) |
| `memory_index_checks.py` — 1 fuzzy path | Affected Functions: validation/memory_index_checks.py | D4, D5 cover changes |
| `memory_index.py` — 1 fuzzy path | Affected Functions: validation/memory_index.py | D5 covers changes |
| `test_when_resolver.py` — 3 tests | Test Changes: test_when_resolver.py | All 3 tests addressed |
| `test_when_resolver_errors.py` — 3 tests | Test Changes: test_when_resolver_errors.py | All 3 tests addressed (1 rewrite, 2 delete) |
| `test_validation_memory_index_formats.py` — 2 tests | Test Changes: test_validation_memory_index_formats.py | Both tests addressed |
| `agents/memory-index.md` — data fixes | Sequencing step 2, D6 | Covered via pre-flight + data fix phase |
| `agents/decisions/*.md` — heading fixes | Sequencing step 2, D6 | Covered via pre-flight + data fix phase |

**Scope Assessment**: All items assigned. No orphans.

## Review Findings

### Critical Issues

None.

### Major Issues

1. **Artifact-form error message not specified (FR-2)**
   - Location: D3 (Key Decisions)
   - Problem: Brief explicitly differentiates keyword-form and artifact-form failures with different error messages and different recovery guidance (keyword: "read index"; artifact: no guidance, upstream problem). D3 only specified keyword-form message.
   - Fix: Added artifact-form error specification to D3 with rationale from brief ("upstream artifact problem, not recoverable by reading index")
   - **Status**: FIXED

### Minor Issues

1. **D4 title says "redundant" but body says "simplify"**
   - Location: D4 (Key Decisions)
   - Problem: Title "becomes redundant" implies deletion, but body says "Simplify to exact-only lookup" — function is simplified, not removed. Misleading title could cause implementer to delete rather than simplify.
   - Fix: Changed title to "simplified to exact-only" and added clarifying parenthetical
   - **Status**: FIXED

2. **Scope OUT fuzzy.py rationale is terse**
   - Location: Scope OUT, first item
   - Problem: "retained (used by compress.py)" — a reader unfamiliar with the codebase might question why fuzzy.py survives a "remove fuzzy" change. Needs brief rationale.
   - Fix: Expanded to note compress.py's separate concern (compression suggestions vs recall resolve)
   - **Status**: FIXED

3. **Affected Functions table vague on `_resolve_trigger()` error behavior**
   - Location: Affected Functions, resolver.py table
   - Problem: "hard error on miss" doesn't reflect D3's context-differentiated error messages. Implementer reading only the table would miss the keyword/artifact distinction.
   - Fix: Changed to "context-differentiated error per D3"
   - **Status**: FIXED

## Fixes Applied

- D3 — Added artifact-form error message specification with differentiated behavior per brief
- D4 — Changed title from "becomes redundant" to "simplified to exact-only" with clarifying note
- Scope OUT — Expanded fuzzy.py retention rationale (compress.py separate concern)
- Affected Functions table — `_resolve_trigger()` "After" column references D3 for error differentiation

## Positive Observations

- Function-level detail with line numbers gives implementer precise targets
- Sequencing rationale (validator before resolver) is well-reasoned and explicitly justified
- Scope boundaries are comprehensive — OUT items enumerated with reasons, preventing scope creep
- Recall entries integrated naturally (D3 references "when cli error messages are llm-consumed", D6 references "when writing memory-index trigger phrases")
- Test changes specify exact test names with concrete rewrite direction (not just "update tests")
- D6 pre-flight data check prevents the common failure of code-first-data-later

## Recommendations

- Line numbers (125-146, 149-165, etc.) will shift if other changes land first. Implementer should use function names as primary locators, line numbers as hints.
- The recall entry "when design proposes removing functions" applies: `_get_suggestions()` and `_handle_no_match()` are marked for deletion. Implementer should verify all callers before removing (not just the fuzzy path identified here).

---

**Ready for user presentation**: Yes
