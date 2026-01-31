# Session Handoff: 2026-01-31

**Status:** Tail-call skill composition pattern implemented. Ready for commit.

## Completed This Session

**Tail-call pattern for skill composition:**
- Implemented skill chaining via tail-calls: plan-* → `/handoff --commit` → `/commit` → display next task (or `/next`)
- Key insight: skills terminate when invoking another skill — this is a feature for final-action invocation (tail-call), not a bug
- Two composition primitives: tail calls (sync chaining within session), pending tasks (async continuation across sessions)
- Modified 6 files: plan-adhoc/SKILL.md, plan-tdd/SKILL.md, handoff/SKILL.md, commit/SKILL.md, workflows-terminology.md, learnings.md
- First attempted inlining git/session.md logic — user identified tail-call pattern as cleaner solution
- Vet review: no critical issues, applied minor fixes (universal post-commit behavior clarification)
- Review report: tmp/vet-tail-call-skills.md

**Specific changes per file:**
- `agent-core/skills/plan-adhoc/SKILL.md` — Point 4.1: auto prepare-runbook.py, pbcopy, tail-call `/handoff --commit`; added Skill to allowed-tools
- `agent-core/skills/plan-tdd/SKILL.md` — Phase 5 steps 5-7: same pattern; updated CRITICAL block and Integration Notes
- `agent-core/skills/handoff/SKILL.md` — Added `--commit` flag, Tail-Call section, allowed-tools (Read, Write, Edit, Bash, Skill)
- `agent-core/skills/commit/SKILL.md` — Added "Post-Commit: Display Next Task" section; tail-calls `/next` if no pending tasks; added Read+Skill to allowed-tools
- `agent-core/fragments/workflows-terminology.md` — Updated both workflow routes to show tail-call chain
- `agents/learnings.md` — Updated two entries: "Don't compose skills" and "Skills cannot invoke other skills" to document tail-call exception

## Pending Tasks

- [x] **Run /remember** — Process learnings from sessions (learnings.md at ~160 lines, soft limit 80)
- [ ] **Search for configuration fix to make heredoc work in sandbox**
- [ ] **Design solution for ambient awareness of consolidated learnings**
- [ ] **Add specific "go read the docs" checkpoints in design and plan skills**
- [ ] **Design runbook identifier solution** — /design plans/runbook-identifiers/problem.md (semantic IDs vs relaxed validation vs auto-numbering)
- [ ] **Create design-vet-agent** — Opus agent for design document review (deferred to opus session)
- [ ] **Add execution metadata to step files** — Step files declare dependencies and execution mode
- [ ] **Orchestrator scope consolidation** — Update orchestrate skill to delegate checkpoint phases (Fix + Vet + Functional) instead of manual invocation

## Blockers / Gotchas

**Vet minor item deferred — OPTIONAL:**
- Mock assertion in test_account_keychain.py:143 could be more specific (assert_called_once_with vs assert_called_once)
- Fix opportunistically when touching that test file

**Tail-call pattern is untested in live workflow:**
- Pattern is documented but hasn't been exercised end-to-end (plan-* → handoff --commit → commit → next)
- First real test will be next time /plan-tdd or /plan-adhoc runs to completion
- Watch for: skill termination timing, session.md state after handoff, clipboard content

## Reference Files

- **tmp/vet-tail-call-skills.md** — Vet review of tail-call pattern changes

## Next Steps

**Immediate:**
- Run /remember to consolidate learnings.md (~160 lines, soft limit 80) — overdue

**Upcoming:**
- Design runbook identifier solution (semantic IDs vs relaxed validation)
- Create design-vet-agent (opus session)

---
*Handoff by Opus. Tail-call skill composition pattern: plan-* → /handoff --commit → /commit → next. Learnings.md overdue for /remember (~160 lines).*
