# Outline Review: UserPromptSubmit Topic Injection

**Artifact**: plans/userpromptsubmit-topic/outline.md
**Date**: 2026-02-28
**Mode**: review + fix-all (PDR criteria)

## Summary

The outline is well-structured with 10 explicit decisions, each with clear rationale. All functional requirements trace to outline sections with complete coverage. Three issues required correction: a cache location contradiction with FR-4, an overstated hook refactor claim that misrepresented the existing control flow, and missing explicit traceability tags.

**Overall Assessment**: Ready

## Requirements Traceability

| Requirement | Outline Section | Coverage | Notes |
|-------------|-----------------|----------|-------|
| FR-1 | D-2 (inverted index) | Complete | Keyword table from memory-index via parsed entries |
| FR-2 | D-1 (scoring formula) | Complete | Entry coverage formula with threshold |
| FR-3 | D-5 (resolution), D-7 (dual-channel) | Complete | Resolve via resolver, inject via additionalContext |
| FR-4 | D-4 (cache strategy), D-2 | Complete | $TMPDIR cache with mtime invalidation |
| FR-5 | D-3 (tier placement) | Complete | Insert into existing accumulate pattern |
| FR-6 | D-6 (token budget) | Complete | Entry count cap, highest-scored wins |
| FR-7 | D-7 (dual-channel) | Complete | systemMessage with trigger lines + line count |
| NFR-1 | D-4 (cache strategy) | Complete | 5s timeout referenced, cache avoids re-parsing |
| NFR-2 | D-3 (tier placement), Risks | Complete | Integration tests before/after; no existing behavior changed |
| C-1 | D-3, Architecture | Complete | Single hook script, new tier in existing file |
| C-2 | D-7 | Complete | additionalContext + systemMessage channels |
| C-3 | D-6, D-10 | Complete | Threshold deferred to calibration, declared-ungrounded |

**Traceability Assessment**: All requirements covered. Tags added to decision headings for explicit traceability.

## Review Findings

### Critical Issues

1. **Cache location contradicts FR-4**
   - Location: D-4 heading and first bullet
   - Problem: D-4 specified `tmp/topic-index-{hash}.json` (project-local), but FR-4 acceptance criteria requires "$TMPDIR (sandbox-compatible)." The existing continuation registry also uses `$TMPDIR`. Project-local `tmp/` is for ephemeral dev artifacts, not hook runtime caches.
   - Fix: Changed cache path to `$TMPDIR/topic-index-{hash}.json`, added note about consistency with continuation registry pattern, referenced `get_cache_path()`/`get_cached_registry()`.
   - **Status**: FIXED

### Major Issues

1. **Overstated hook control flow refactor**
   - Location: D-3 "implementation consequence" and Risks last bullet
   - Problem: D-3 claimed "hook control flow refactored from early-return to accumulate-and-return" and "no tier blocks topic injection." Verified against actual hook code: Tier 1 already early-returns (correct — `s`, `x` need no context). Tier 2/2.5 already use `context_parts`/`system_parts` accumulate pattern. The claimed refactor overstates the change and could mislead implementation into unnecessarily restructuring the hook.
   - Fix: Rewrote D-3 to accurately describe insertion into existing accumulate pattern. Clarified Tier 1 early-return is preserved. Changed Risks bullet to reflect actual integration scope.
   - **Status**: FIXED

2. **D-3 "additive with ALL tiers" misleading**
   - Location: D-3 heading
   - Problem: Claiming additivity with Tier 1 is technically vacuous (stopwords remove all keywords) but architecturally misleading — Tier 1 early-returns before topic code runs. The design must be clear about what "additive" means in context of existing control flow.
   - Fix: Changed heading to "additive with Tier 2, 2.5, and 3." Added explicit note that Tier 1 early-returns before topic injection and this is correct behavior.
   - **Status**: FIXED

### Minor Issues

1. **Missing explicit requirement tags on decisions**
   - Location: D-1 through D-7 headings
   - Problem: Decisions referenced requirements implicitly but lacked FR-N/NFR-N/C-N tags. PDR traceability requires explicit mapping.
   - Fix: Added bracketed tags to each decision heading (e.g., `[FR-2]`, `[FR-5, NFR-2, C-1]`).
   - **Status**: FIXED

2. **NFR-2 not explicitly addressed**
   - Location: D-3
   - Problem: NFR-2 ("no degradation of existing hook behavior") was addressed implicitly through integration test mention in Risks, but not tagged or explicitly called out in D-3 where it most applies.
   - Fix: Added NFR-2 tag to D-3 heading.
   - **Status**: FIXED

3. **Missing context budget risk from recall entries**
   - Location: Risks section
   - Problem: Recall artifact entry "too many rules in context — adherence degrades >200 rules, ~150 budget" directly relates to FR-6 rationale but wasn't surfaced as a risk. D-6 caps entry count but resolved sections vary in length — the token-level impact is uncontrolled.
   - Fix: Added "Context budget pressure" risk with recall reference and monitoring mitigation.
   - **Status**: FIXED

4. **Scope boundary FR-5 description stale**
   - Location: Scope Boundaries, IN list, FR-5 line
   - Problem: Referenced "accumulate-and-return refactor" which no longer reflects the corrected D-3 approach.
   - Fix: Changed to "insert into existing accumulate pattern."
   - **Status**: FIXED

## Fixes Applied

- D-1 heading — added `[FR-2]` tag
- D-2 heading — added `[FR-1, FR-4]` tag; removed hardcoded "347" count
- D-3 heading — changed to "additive with Tier 2, 2.5, and 3 [FR-5, NFR-2, C-1]"
- D-3 body — rewrote to describe insertion into existing accumulate pattern, not a full refactor; clarified Tier 1 early-return preserved
- D-4 heading — changed to "$TMPDIR" from "project-local tmp"; added `[FR-4, NFR-1]`
- D-4 cache path — changed to `$TMPDIR/topic-index-{hash}.json`; added consistency note with continuation registry
- D-5 heading — added `[FR-3]`
- D-6 heading — added `[FR-6, C-3]`
- D-7 heading — added `[FR-3, FR-7, C-2]`
- Scope Boundaries IN, FR-5 line — corrected description
- Risks — added "Context budget pressure" risk with recall reference
- Risks — corrected last bullet from "refactor across all tiers" to "inserting into existing accumulate pattern"

## Positive Observations

- All 10 decisions include clear rationale with trade-off documentation
- Q-1 and Q-2 from requirements resolved with explicit DROPPED/additive decisions (D-8, D-9)
- Scoring algorithm grounded via separate report rather than assumed (D-1 + grounding reference)
- D-10 calibration approach is honest about ungrounded parameters and provides a concrete calibration method
- Scope boundaries enumerate IN and OUT with FR-N tags and parenthetical justifications for OUT items
- Affected Files section cleanly separates new, modified, and read-only dependencies

## Recommendations

- During design elaboration, specify the exact insertion point in the hook (line-level) — between Tier 2.5 guards and the `if directive_matches and context_parts:` output assembly
- Consider whether `score_relevance()` should be called directly (coupling to session_id parameter) or whether the formula should be extracted into a shared utility
- The `resolve()` function uses fuzzy matching which adds latency — measure per-call cost during implementation to validate the 5s budget with 3 sequential resolve calls

---

**Ready for user presentation**: Yes
