# Session: `/when` Memory Recall System — Design Phase B Ready

**Status:** Outline fully updated with architecture decisions from design discussion. Ready for Phase B (user validates outline) → Phase C (full design.md).

## Completed This Session

### Design Discussion — Architecture Decisions
- Extensive discussion resolving all open design questions for `/when` system
- Settled: two-field index format (`/when trigger | extra triggers`), two operators (`/when` + `/how`), direct content output
- Settled: `.section` (heading lookup) and `..file` (file relative to `agents/decisions/`) navigation modes
- Settled: fuzzy matching bridges index density and heading prose clarity — single engine shared by resolver, validator, key compression tool
- Settled: ancestor + sibling navigation links in output footer
- Settled: plain prose triggers (no hyphens), custom ~80 line fzf-style fuzzy engine
- Dropped: file atomization (Read caching research killed rationale), `/what` and `/why` operators, `§` operator, three-field format, batch Read indirection, cross-file explicit relations

### Token Cost Measurement
- Measured all candidate symbols (`..`, `<`, `§`, `@`, `/`, `.`) via Anthropic API: all identical (8 tokens bare, 11 in context)
- Symbol choice is purely usability — `..` for file, `.` for section

### Corpus Analysis
- Delegated to haiku quiet-explore agent: pattern classification, "When" compatibility, H3 uniqueness, collision analysis
- Key findings: 82% noun phrases, 100% H3 uniqueness (no disambiguation needed), 27% incompatible with "When" (→ `/how`), low collision risk
- Report: `plans/when-recall/reports/corpus-analysis.md`

### Outline Update
- Rewrote `plans/when-recall/outline.md` with all settled decisions from discussion
- 9 components: resolver, skill wrappers, index migration, fuzzy engine, validator, key compression tool, consumption header, `/remember` update, fragment promotion rule

## Pending Tasks

- [ ] **Continue `/when` design** — Phase B (user validates outline) → Phase C (full design.md) | `/design plans/when-recall/outline.md`

## Blockers / Gotchas

- `/design` skill has no resume logic — invoke manually from Phase B when continuing, don't re-invoke `/design` (would restart from Phase A)
- Learnings file at 131/80 lines (soft limit exceeded, 0 entries ≥7 days — consolidation deferred)
- Decision file heading renames (~122 headings) are large migration scope — script-assisted but verify no broken @ references
- Invalidated learnings removed this session: "Memory-as-file enables Read caching" (file atomization dropped), updated "Namespace collision" (§ dropped, `.`/`..` used as command syntax)

## Reference Files

- `plans/when-recall/outline.md` — Design outline (updated, ready for Phase B)
- `plans/when-recall/reports/corpus-analysis.md` — Corpus analysis (pattern classification, H3 uniqueness)
- `plans/when-recall/reports/fzf-research.md` — fzf algorithm research + evaluation
- `plans/when-recall/reports/explore-agent-core.md` — Infrastructure exploration
- `plans/when-recall/reports/outline-review.md` — Outline review (stale — pre-discussion, needs re-review after Phase B)
- `plans/memory-index-recall/reports/final-summary.md` — Recall analysis (0% baseline)
- `agent-core/bin/validate-memory-index.py` — Current validator (480 lines, will need update)
- `agents/memory-index.md` — Current index format (~122 entries)
