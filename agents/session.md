# Session: Worktree — README update

**Status:** Complete.

## Completed This Session

- **Update README.md** — Full rewrite from 261-line stale CLI-only doc to 215-line README covering both agent framework and CLI
  - Researched documentation skills ecosystem (Anthropic doc-coauthoring, ComposioHQ content-research-writer, readme-ai). Stole reader-testing pattern only
  - Reader-tested via fresh sub-agent (9 predicted questions), fixed gaps: motivation opener, PyPI note, session data source, compose config example, statusline as hook, markdown in-place behavior
  - Agent Framework section: structured workflow pipeline and memory management as key value props (user direction)
  - CLI Commands section: all 13 public commands documented (was 7)
  - Dropped: Data Model, Implementation Notes, project structure tree, agent-internal documentation links
  - Style matched to user's writing corpus (`tmp/STYLE_CORPUS.md`)
  - Current installation note: submodule + symlinks via `just sync-to-parent`, converting to plugin

## Pending Tasks

- [ ] **Write agent-core README** — Create README.md for agent-core submodule | sonnet
  - Research findings: `plans/reports/readme-skill-research.md`
  - Reuse: reader-testing pattern, style corpus, motivation-first opener
  - Style corpus: `tmp/STYLE_CORPUS.md`
  - Scope: agent-core as standalone — workflow, memory management, skills, agents, fragments, hooks
  - Context: `plans/plugin-migration/design.md` for future plugin framing (edify-plugin)

## Reference Files

- `plans/reports/readme-skill-research.md` — documentation skill research findings
- `tmp/STYLE_CORPUS.md` — writing style corpus for voice matching
- `plans/plugin-migration/design.md` — informed agent framework framing (edify-plugin future state)
