# Session: `/when` Memory Recall System — Design In Progress

**Status:** Design Phase A complete + fzf research done. Outline needs update with architecture evolution + fzf findings before Phase B.

## Completed This Session

### fzf Algorithm Research
- Researched fzf's modified Smith-Waterman algorithm: scoring constants, V1/V2 variants, bonus system
- Evaluated Python implementations: pfzy (pure Python fzy port, MIT), RapidFuzz (C++, Levenshtein family), thefuzz (legacy)
- Recommendation: fzf-style scoring (pfzy or custom ~80 lines) as primary engine, word-overlap as tiebreaker
- Key finding: fzf boundary bonuses align well with hyphenated uniquefuzzy keys, but short keys reduce score discrimination
- Report: `plans/when-recall/reports/fzf-research.md`

### Prior Session: Architecture Evolution (committed 95dd6ed)
- 0% recall root cause analysis → passive catalog format
- Architecture decisions: `§` operator, memory-as-file, `@uniquefuzzy`, resolver-only, two-field index
- Design Phase A artifacts: outline, exploration report, outline review

## Pending Tasks

- [ ] **Update outline with architecture evolution** — Apply individual-files, `§` operator, `@uniquefuzzy`, two-field format, resolver-only changes + fzf research findings to `plans/when-recall/outline.md`
- [ ] **Continue `/when` design** — Phase B (user validates outline) → Phase C (full design.md) | `/design plans/when-recall/outline.md`

## Blockers / Gotchas

- Outline reflects three-field format from mid-discussion; needs update with final architecture (individual files, `§`, `@uniquefuzzy`, two-field) AND fzf matching engine decision before Phase B
- Learnings file at 121/80 lines (soft limit exceeded, no entries ≥7 days yet — consolidation deferred)
- File atomization (169 individual files) significantly increases migration scope vs format-only change

## Reference Files

- `plans/when-recall/outline.md` — Design outline (needs update)
- `plans/when-recall/reports/fzf-research.md` — fzf algorithm research + evaluation
- `plans/when-recall/reports/explore-agent-core.md` — Infrastructure exploration
- `plans/when-recall/reports/outline-review.md` — Outline review
- `plans/memory-index-recall/reports/final-summary.md` — Recall analysis (0% baseline)
- `agent-core/bin/validate-memory-index.py` — Current validator (480 lines, will need update)
- `agents/memory-index.md` — Current index format (~169 entries)
