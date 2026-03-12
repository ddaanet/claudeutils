# Skill Review: proof

**Artifact:** `agent-core/skills/proof/SKILL.md` + `agent-core/skills/proof/references/item-review.md`
**Design context:** `plans/interactive-review/outline.md`
**Date:** 2026-03-12

## Summary

Core loop mechanics are sound. One critical gap (suspend contradicts outline D-6), one major gap (discard planstate), organizational issues in Terminal Actions section.

## Issues

### Critical

- **suspend contradicts outline D-6:** Outline explicitly removed suspend→/design chain ("capture as pending and keep reviewing"). Skill still includes it. Remove.

### Major

- **Terminal Actions conflates terminal and loop actions:** Section contains apply, discard (terminal), revisit, learn (loop actions). revisit self-annotates "not terminal." Restructure.
- **learn duplicated:** Appears under Iteration Guards (line 88) and Terminal Actions (line 109). Remove duplicate.
- **discard has no planstate transition:** Entry writes review-pending. Apply writes reviewed. Discard leaves review-pending dangling.

### Minor

- **Skill in allowed-tools possibly vestigial:** After removing suspend, no path needs Skill tool.
- **revisit return state ambiguous:** SKILL.md says "Returns to iteration" — reference file clearer: "post-iteration state."
- **corrector UNFIXABLE re-enter loop underspecified:** Unclear if full re-iteration or scoped discussion.
- **Reference outline.md granularity improved over outline spec:** Reference uses `### D-N:` (accurate), outline says `### Sub-problem`. Positive deviation.

## Positive

- Verdict mechanics unambiguous, accumulation format concrete
- Implicit discussion well-specified
- Kill sub-actions properly scoped
- Progressive disclosure working (168 + 79 lines)
- Bottom-to-top edit ordering prevents line-shift interference
