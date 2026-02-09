# Session: `/when` Memory Recall System — Design In Progress

**Status:** Design Phase A complete (research + outline). Outline needs update with architectural evolution from discussion before Phase B.

## Completed This Session

### Design Discussion + Architecture Evolution
- Analyzed 0% recall root cause: passive catalog format, agents don't form retrieval intentions
- Opus brainstorm for prefix naming → selected `when` (most natural conditional, no collision)
- Evolved from passive format → `/when` skill as recursive knowledge navigator
- Format evolution through discussion:
  1. `when <trigger> — <rule>` (passive format change)
  2. `/when <trigger> | <rule>` (skill invocation)
  3. `/when <trigger> | <header-title> | <description>` (three-field, validator-friendly)
  4. **Final:** Memory-as-file + `@uniquefuzzy` + two-field index (see Architecture below)

### Architecture Decisions
- **`§` navigation operator** — replaces `.`/`..` prefix (avoids collision with structural section `.` notation in decision files)
- **Memory-as-file** — each decision becomes individual file, enables `@file` Read caching
- **`@uniquefuzzy` frontmatter** — shortest meaningful unique key per memory file, used for matching
- **Resolver-only script** — `/when` outputs `@file` references, agent batch-Reads (cached)
- **`/when §`** — outputs list of `@file` references for section/file-level navigation
- **Two-field index** — `/when <uniquefuzzy> | <description>` (header title lives in file, not index)

### Design Phase A Artifacts
- Exploration report: `plans/when-recall/reports/explore-agent-core.md`
- Outline: `plans/when-recall/outline.md` (reviewed, but needs update with latest architecture)
- Outline review: `plans/when-recall/reports/outline-review.md`

## Pending Tasks

- [ ] **Research fzf algorithm** — Research fzf fuzzy matching algorithm, discuss using as fuzzy find engine for `/when` | sonnet
- [ ] **Update outline with architecture evolution** — Apply individual-files, `§` operator, `@uniquefuzzy`, two-field format, resolver-only changes to `plans/when-recall/outline.md`
- [ ] **Continue `/when` design** — Phase B (user validates outline) → Phase C (full design.md) | `/design plans/when-recall/outline.md`

## Blockers / Gotchas

- Outline currently reflects three-field format from mid-discussion; needs update with final architecture (individual files, `§`, `@uniquefuzzy`, two-field) before Phase B
- Learnings file at 121/80 lines (soft limit exceeded, no entries ≥7 days yet — consolidation deferred)
- File atomization (169 individual files) significantly increases migration scope vs format-only change

## Reference Files

- `plans/when-recall/outline.md` — Design outline (needs update)
- `plans/when-recall/reports/explore-agent-core.md` — Infrastructure exploration
- `plans/when-recall/reports/outline-review.md` — Outline review
- `plans/memory-index-recall/reports/final-summary.md` — Recall analysis (0% baseline)
- `agent-core/bin/validate-memory-index.py` — Current validator (480 lines, will need update)
- `agents/memory-index.md` — Current index format (~169 entries)
