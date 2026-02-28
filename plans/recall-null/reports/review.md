# Review: recall-null implementation

**Scope**: Phase 1 (null mode CLI + tests) and Phase 2 (D+B gate language propagation to 5 skill files)
**Baseline**: d24b2e6448a07aa1c001a7021afa287417a6c74d
**Date**: 2026-02-28T00:00:00
**Mode**: review + fix

## Summary

Both phases are correctly implemented. Phase 1 null filtering is behaviorally correct — strips operator prefix, compares bare trigger to "null", filters before resolution, returns early when all queries are null. Phase 2 D+B gate language is consistently propagated across all 4 pipeline skills. Two minor prose inconsistencies found and fixed.

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

None.

### Major Issues

None.

### Minor Issues

1. **Tier 1 "No artifact" bullet has parenthetical missing from Tier 2**
   - Location: `agent-core/skills/runbook/SKILL.md` — Tier 1 recall context, "No artifact" bullet
   - Note: Tier 1 says `**No artifact** (moderate path skipped design)` but Tier 2 omits the parenthetical. Both tiers can arrive via the moderate path that skips design. Inconsistent framing creates ambiguity about when Tier 2's "No artifact" path applies.
   - **Status**: FIXED

2. **`test_null_mixed_with_real_queries` assertion is fragile**
   - Location: `tests/test_when_null.py:40`
   - Note: `assert "null" not in result.output.lower().replace("when writing mock tests", "")` replaces the trigger phrase to avoid false positives, but legitimate resolved content could contain the word "null". A content-anchored assertion ("output contains only expected section, not null as resolution output") would be more robust. The fix adds a positive-form assertion: assert the output equals the expected resolved section only.
   - **Status**: FIXED

## Fixes Applied

- `agent-core/skills/runbook/SKILL.md:137` — Added "(moderate path skipped design)" parenthetical to Tier 2 "No artifact" bullet to match Tier 1 framing
- `tests/test_when_null.py:40` — Replaced fragile negative assertion with explicit check that output matches expected content and does not contain a standalone "null" line

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|---------|
| Phase 1: null exits silently (exit 0, empty output) | Satisfied | `cli.py:79-81` — filter + early return; `test_when_null.py:10-15` |
| Phase 1: null mixed with real queries filters nulls | Satisfied | `cli.py:79` list comprehension filters before resolve; `test_when_null.py:18-40` |
| Phase 1: operator-prefixed null filtered ("when null") | Satisfied | `_strip_operator` returns "null" for "when null"; `test_when_null.py:43-48` |
| Phase 2: D+B gate language — /requirements Recall Pass | Satisfied | Gate anchor note added at `requirements/SKILL.md:40` |
| Phase 2: D+B gate language — /requirements null artifact format | Satisfied | Null artifact paragraph added at `requirements/SKILL.md:63` |
| Phase 2: Post-explore gate — /requirements | Satisfied | Post-Explore Recall Gate section added at `requirements/SKILL.md:102` |
| Phase 2: D+B gate language — /design null artifact format | Satisfied | Null artifact paragraph added to A.1 at `design/SKILL.md:209` |
| Phase 2: /design A.2.5 already canonical (no-op) | Satisfied | A.2.5 unchanged in diff — verified current state matches canonical pattern |
| Phase 2: D+B gate language — /runbook Tier 1 | Satisfied | Three-path D+B structure at `runbook/SKILL.md:116-121` |
| Phase 2: D+B gate language — /runbook Tier 2 | Satisfied | Three-path D+B structure at `runbook/SKILL.md:134-139` |
| Phase 2: D+B gate language — tier3 Phase 0.5 step 1 | Satisfied | Both-paths language at `tier3-planning-process.md:22-25` |
| Phase 2: Post-explore gate — tier3 Phase 0.5 step 4 | Satisfied | Post-explore gate added as step 4 at `tier3-planning-process.md:44-50` |
| Phase 2: D+B gate language — /inline 2.3 | Satisfied | Three-path D+B structure at `inline/SKILL.md:68-79` |
| Canonical null artifact format: `null — no relevant entries found` | Satisfied | Both /requirements and /design use exact string |

---

## Positive Observations

- Null filtering is placed correctly: after `_collect_queries` (captures stdin too), before `_resolve_queries`. Operator stripping reuses existing `_strip_operator` — no new logic paths.
- Comment in cli.py explains the "why" (D+B gate anchor), not just the "what" — appropriate for a non-obvious reserved value.
- D+B three-path structure is consistent across all three modified skills (Tier 1, Tier 2, /inline) — same bullet format, same null anchor language.
- Test isolation in `test_null_mixed_with_real_queries` correctly sets up a minimal fixture (memory-index + one decision file) without requiring the real project filesystem.
- Null artifact language is identical between /requirements and /design — copy-consistent, no drift.
