# Session Handoff: 2026-02-24

**Status:** `/recall` skill created with 5-mode taxonomy. brainstorm-name agent fixed. Ready to commit.

## Completed This Session

**Recall pass pipeline (prior sessions, carried forward):**
- `plans/recall-pass/requirements.md` — 10 FRs, 3 NFRs, 5 constraints
- `plans/recall-pass/outline.md` — 10 key decisions, all open questions resolved
- 4 pipeline skill files edited with recall artifact generation, augmentation, injection, and review recall (47 insertions across design, runbook, orchestrate, deliverable-review skills)

**`/recall` skill — interactive recall pass:**
- Created `agent-core/skills/recall/SKILL.md` — manual recall for interactive sessions
- Naming: 5 brainstorm rounds with opus brainstorm-name agent → `/recall` selected (transparent, self-documenting, ecosystem identity)
- 5-mode taxonomy designed through discussion:
  - default (section-level, 1-2 passes), deep (aggressive saturation, 4 passes), broad (whole-file Read), all (deep+broad), everything (full corpus)
- Broad mode uses direct Read tool (not when-resolve.py) — file-level loading doesn't benefit from section resolution overhead
- Tail-recursive design: skill self-invokes until zero new entries found (mechanical exit condition). Defeats agent loop short-circuiting — skill continuation drives iteration, not prompt instructions.
- Symlinked via `just sync-to-parent`

**brainstorm-name agent fix:**
- Fixed YAML frontmatter: added `description: |` block scalar (without it, `model`/`color`/`tools` fields were consumed as description text)
- Added `# Artifact Naming Specialist` title heading

**Research artifact:**
- `plans/reports/recall-context-optimization-test.md` — test protocol for Read tool context deduplication behavior (4 tests: whole-file dedup, range accumulation, range→whole interaction, whole→range interaction)

**Key design decisions:**
- Tail-recursive skill with mechanical exit defeats LLM loop short-circuiting ("do X until Y" collapses to single execution; skill self-invocation forces actual iteration)
- Broad mode: direct Read, no line cap enforcement (precommit handles it)
- "Skip already-loaded" only applies to files previously Read whole (verifiable from prior output summaries); section-level partial loads don't suppress whole-file reads
- Future: rename `when-resolve.py` → `claudeutils _recall` (scoped to plugin migration, not this task)

## Pending Tasks

- [x] **Recall pass requirements** — implemented via Tier 2 delegation
- [ ] **Sync-to-parent sandbox documentation** — update references to document required sandbox bypass | haiku
- [ ] **Rename when-resolve.py to claudeutils _recall** — consolidate into CLI, remove `..file` syntax | sonnet
- [>] **Read tool context optimization test** — run `plans/reports/recall-context-optimization-test.md` protocol in fresh session, results inform `/recall` skip-tracking logic | sonnet

## Blockers / Gotchas

**Never run `git merge` without sandbox bypass:**
- `git merge` without `dangerouslyDisableSandbox: true` partially checks out files, hits sandbox, leaves 80+ orphaned untracked files

**`just sync-to-parent` requires sandbox bypass:**
- Recipe removes and recreates symlinks in `.claude/` — sandbox blocks `rm` on those paths

## Next Steps

Run context optimization test in fresh session — read `plans/reports/recall-context-optimization-test.md` for protocol.

## Reference Files

- `agent-core/skills/recall/SKILL.md` — interactive recall skill (5 modes)
- `agent-core/agents/brainstorm-name.md` — fixed YAML frontmatter
- `plans/reports/recall-context-optimization-test.md` — Read deduplication test protocol
- `plans/recall-pass/outline.md` — pipeline recall pass design (10 key decisions)
