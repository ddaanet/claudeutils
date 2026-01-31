# Session Handoff: 2026-01-31

**Status:** Ambient awareness design complete. RCA on opus-design-question visibility done with 4-layer fix. Uncommitted changes ready.

## Completed This Session

**Ambient awareness design — `plans/ambient-awareness/design.md`:**
- Three-part solution: consolidation changelog + remember skill process fix + orphan audit
- Changelog: rolling 20-entry log at `agent-core/fragments/CHANGELOG.md`, `@`-imported in CLAUDE.md
- Remember skill: append-only changelog entry after consolidation, scripted trim via `just trim-changelog`
- Orphan audit: 3 deletions (AGENTS-framework, roles-rules-skills, tool-preferences, hashtags), 3 new `.claude/rules/` entries
- Vetted by opus — applied all HIGH + MEDIUM fixes (commit-delegation preserved, multi-project deployment notes, entry counting spec)
- Key design decision: append-only + scripted trim chosen over git-derived changelog (skill has best context for descriptions; git-derived has "when to generate" problem)

**RCA: Orchestrator uses AskUserQuestion instead of /opus-design-question:**
- Root cause: zero contextual reminders about the skill exist outside the skill itself. No CLAUDE.md reference, no design skill mention, no path-triggered rule
- Fix: 4-layer defense in depth (see `tmp/claude/rca-opus-design-question.md` for full report)
  - New fragment: `agent-core/fragments/design-decisions.md` — design decision escalation rule
  - Updated: `CLAUDE.md` — added `@agent-core/fragments/design-decisions.md`
  - Updated: `agent-core/skills/design/SKILL.md` — added escalation reminder in Step 1
  - New rule: `.claude/rules/design-work.md` — path-triggered on `plans/*/design.md`
  - Updated: `agent-core/skills/opus-design-question/SKILL.md` — directive description with "REQUIRED"

**Uncommitted changes:**
- `CLAUDE.md` — +2 lines (design-decisions fragment `@`-ref)
- `agent-core/` — new fragment, updated design skill, updated opus-design-question skill
- `.claude/rules/design-work.md` — new file
- `plans/ambient-awareness/design.md` — new design document

## Pending Tasks

- [ ] **Implement ambient awareness** — `/plan-adhoc plans/ambient-awareness/design.md` (oneshot workflow)
- [ ] **Add specific "go read the docs" checkpoints in design and plan skills** — partially addressed by design-work.md rule, but design doc calls for more checkpoints
- [ ] **Design runbook identifier solution** — `/design plans/runbook-identifiers/problem.md` (semantic IDs vs relaxed validation vs auto-numbering)
- [ ] **Create design-vet-agent** — Opus agent for design document review (deferred to opus session)
- [ ] **Add execution metadata to step files** — Step files declare dependencies and execution mode
- [ ] **Orchestrator scope consolidation** — Update orchestrate skill to delegate checkpoint phases (Fix + Vet + Functional) instead of manual invocation

## Blockers / Gotchas

**Vet minor item deferred — OPTIONAL:**
- Mock assertion in test_account_keychain.py:143 could be more specific (assert_called_once_with vs assert_called_once)
- Fix opportunistically when touching that test file

**Tail-call pattern is untested in live workflow:**
- Pattern is documented but hasn't been exercised end-to-end (plan-* → handoff --commit → commit → next)
- Watch for: skill termination timing, session.md state after handoff, clipboard content

**pytest-md has other uncommitted changes:**
- README.md, dev/architecture.md, session.md, tests/test_output_expectations.py also modified
- Only .envrc symlink change is from previous session

**agent-core submodule changes span two sessions:**
- Previous session: configs/claude-env.sh (new), templates/dotenvrc (simplified)
- This session: fragments/design-decisions.md (new), skills/design/SKILL.md (updated), skills/opus-design-question/SKILL.md (updated)
- Commit agent-core submodule with all changes, then claudeutils with submodule ref + own changes

## Next Steps

Commit agent-core first (spans two sessions of changes), then claudeutils (CLAUDE.md, .claude/rules/design-work.md, plans/ambient-awareness/, agent-core ref). Then implement ambient awareness via `/plan-adhoc`.

---
*Handoff by Opus. Ambient awareness design + RCA on opus-design-question visibility.*
