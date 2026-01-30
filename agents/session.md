# Session Handoff: 2026-01-30

**Status:** Feedback review design complete, fixes pending execution

## Completed This Session

**Previous session work (committed 140ff8f agent-core, 2fe5743 parent):**
- Skill improvements: 10 files modified per `plans/skill-improvements/design.md`
- Hookify rules created (but .local.md files wrongly committed — need git rm)
- opus-design-question skill created

**This session — feedback review and design:**
- Created `plans/feedback-fixes/design.md` — comprehensive fixes for last commit
- Issues identified in: tdd-task.md (5 fixes), handoff skill (5 fixes), session.md structure, git cleanup
- Investigated @ references (not supported in skills/agents, only CLAUDE.md)
- Found root cause of "New Learnings" in session.md: `good-handoff.md` line 58 has pre-migration `## Recent Learnings` example
- Investigated PostToolUse cwd hooks: cannot modify cwd, PreToolUse warn is best option
- User removed hookify .local.md files from disk (still tracked in git)

## Pending Tasks

- [ ] **Execute feedback-fixes** — `plans/feedback-fixes/design.md` (direct execution, no orchestration)
  - tdd-task.md: reorder steps, remove orphaned section, bash style fixes
  - Handoff skill: section constraints, remove stale example, design decisions guidance
  - Session/learnings: structure fixes
  - Git: `git rm --cached` .local.md files, add `*.local.*` to .gitignore
  - Hook: submodule safety PreToolUse script
- [ ] **Execute recovery** — `/plan-tdd` on `plans/claude-tools-recovery/design.md`
- [ ] **Run /remember** — learnings.md at ~110 lines after this handoff (soft limit 80)
- [ ] **Discuss** — Tool batching: contextual block with contract (batch-level hook rules)

## Blockers / Gotchas

**Python 3.14 Incompatibility:**
- litellm dependency uvloop doesn't support Python 3.14 yet
- Solution: `uv tool install --python 3.13 'litellm[proxy]'`

**Mock Patching Pattern:**
- Patch at usage location, not definition location
- Example: `patch("claudeutils.account.state.subprocess.run")`

**Bash cwd behavior:**
- Main interactive agent: cwd persists between Bash calls
- Sub-agents (Task tool): cwd does NOT persist
- CLAUDE.md absolute path guidance targets sub-agents

**Hookify .local.md files still tracked in git:**
- User deleted from disk, need `git rm --cached` to remove from index
- Add `*.local.*` to .gitignore before recreating any local files

## Reference Files

- `plans/feedback-fixes/design.md` — all fixes with rationale, ready for execution
- `plans/skill-improvements/design.md` — previous session's changes (applied, committed)
- `plans/claude-tools-recovery/design.md` — 4 phases (R0-R4), pending execution
- `agent-core/skills/handoff/examples/good-handoff.md:58` — pre-migration artifact causing learnings section

---
*Handoff by Opus. Design session complete — feedback-fixes design ready for execution.*
