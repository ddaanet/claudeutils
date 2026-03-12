# Brief: Interactive Review — User Feedback

## Origin

Dogfooding session (2026-03-12). Applied the interactive review process (as described in its own outline) to review the outline itself. Surfaced presentation, process, and flow gaps that neither the author nor the outline-corrector caught.

## Feedback

### Presentation ergonomics

- **Blockquote rendering is dim.** Item content displayed as `> quote` renders in low-contrast text. Use plain text for item content.
- **Tables are grid-heavy.** TOC as markdown table — grid characters dominate the content. Use numbered lists instead.
- **Missing orientation.** Jumped straight to Item 1 without context. Reviewer needs: preamble (what's being reviewed, how many items, overall summary), then TOC with per-item title + short summary.
- **Checkpoint after orientation.** After presenting preamble + TOC, pause for user feedback before first item. Reviewer may want to reorder, skip sections, or adjust scope based on the overview.

### Research gap

- No external research conducted (A.3-4 skipped entirely).
- Verdict vocabulary (approve/revise/kill/discuss/absorb/skip) invented from first principles. Not validated against structured inspection literature (Fagan, IEEE 1028) or existing tool UX (GitHub PR review, Gerrit, Phabricator).
- Loop structure similarly ungrounded. 50 years of inspection methodology exists.
- Current design may be fine, over-engineered (6 verdicts vs GitHub's 3), or missing important categories. Can't tell without research.

### Process findings

- Outline-corrector verified FR traceability and structural completeness — both passed. But corrector cannot catch UX/ergonomics gaps or grounding absence. Dogfooding caught what automated review couldn't.
- The "testing approach" section (manual walkthrough) is doing real work, not ceremony — this session proved it.

## Implication

Outline should be rewritten from scratch after:
1. Research on structured inspection methods and item-level review UX in existing tools
2. Incorporating the presentation feedback above
3. Adding an orientation/checkpoint step before item iteration

The current outline.md and classification.md can be deleted — they're pre-research artifacts.

## References

- `agent-core/skills/proof/SKILL.md` — existing proof skill (extension target)
- `plans/interactive-review/requirements.md` — FRs unchanged, still valid
- `plans/interactive-review/reports/outline-review.md` — corrector review of pre-research outline (audit trail)
