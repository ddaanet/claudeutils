# Session: Worktree — README update

**Status:** In progress.

## Completed This Session

- **Update README.md** — Full rewrite from 261-line stale CLI-only doc to 215-line README covering both agent framework and CLI
  - Researched documentation skills ecosystem (Anthropic doc-coauthoring, ComposioHQ content-research-writer, readme-ai). Stole reader-testing pattern only
  - Reader-tested via fresh sub-agent (9 predicted questions), fixed gaps: motivation opener, PyPI note, session data source, compose config example, statusline as hook, markdown in-place behavior
  - Agent Framework section: structured workflow pipeline and memory management as key value props (user direction)
  - CLI Commands section: all 13 public commands documented (was 7)
  - Dropped: Data Model, Implementation Notes, project structure tree, agent-internal documentation links
  - Style matched to user's writing corpus (`tmp/STYLE_CORPUS.md`)
  - Current installation note: submodule + symlinks via `just sync-to-parent`, converting to plugin
- **Write agent-core README** — Full rewrite from 116-line stale scaffold to 273-line comprehensive documentation (b44e6ff, 6174382)
  - Motivation-first opener: drift problem → pipeline + memory solution
  - All components enumerated: 18 skills, 14 agents, 23 fragments, 4 hooks, 12 scripts (7 utility + 5 validators)
  - Reader-tested (10 questions), fixed 5 gaps: prerequisites, memory file location, skill/agent distinction, CLAUDE.md template reference, hook configuration note
  - Vet-reviewed: 2 minor fixes (validators expanded from inline list to table format)
  - Style matched to parent README and `tmp/STYLE_CORPUS.md` corpus
  - Reused patterns from parent README session: reader-testing, style corpus, motivation opener

## Pending Tasks

- [ ] **Create documentation writing skill** — Formalize the README writing process as a reusable skill | sonnet
  - Pattern extracted from two README sessions: explore → write → reader-test → fix gaps → vet
  - Key techniques: motivation-first opener, style corpus matching, fresh-agent reader testing
  - Research: `plans/reports/readme-skill-research.md` (doc-coauthoring reader-test, style corpus)
  - Scope: `agent-core/skills/doc-writing/SKILL.md` — covers project documentation (READMEs, guides)

## Reference Files

- `plans/reports/readme-skill-research.md` — documentation skill research findings
- `tmp/STYLE_CORPUS.md` — writing style corpus for voice matching
- `plans/plugin-migration/design.md` — informed agent framework framing (edify-plugin future state)
- `tmp/vet-readme-report.md` — vet review report for agent-core README
