# Session Handoff: 2026-01-30

**Status:** Feedback-fixes design reviewed and patched, ready for execution

## Completed This Session

**Previous session work (committed 140ff8f agent-core, 2fe5743 parent):**
- Skill improvements: 10 files modified per `plans/skill-improvements/design.md`
- Hookify rules created (but .local.md files wrongly committed — need git rm)
- opus-design-question skill created

**Previous session — feedback review and design:**
- Created `plans/feedback-fixes/design.md` — comprehensive fixes for last commit
- Issues identified in: tdd-task.md (5 fixes), handoff skill (5 fixes), session.md structure, git cleanup
- Found root cause of "New Learnings" in session.md: `good-handoff.md` line 58 has pre-migration `## Recent Learnings` example

**This session — design review and patch:**
- Reviewed design.md for consistency and executability by sonnet agent
- Found §3 (session.md) and §4 (learnings.md) already applied by prior handoff — marked ALREADY APPLIED
- Added `## Next Steps` as 5th allowed session.md section (was missing from §2b, §2d, D3)
- Verified hooks.json format: agent-core uses settings format (not plugin format) — §6 is correct
- Loaded hook-development skill to confirm format; `"hooks"` sub-array + `"type": "command"` needed for matcher entries
- Removed session.md and learnings.md from execution file list

## Pending Tasks

- [ ] **Execute feedback-fixes** — `plans/feedback-fixes/design.md` (direct execution, no orchestration)
  - tdd-task.md: reorder steps, remove orphaned section, bash style fixes
  - Handoff skill: section constraints, remove stale example, design decisions guidance
  - Git: `git rm --cached` .local.md files, add `*.local.*` to .gitignore
  - Hook: submodule safety PreToolUse script
- [ ] **Execute recovery** — `/plan-tdd` on `plans/claude-tools-recovery/design.md`
- [ ] **Run /remember** — learnings.md at ~130 lines (soft limit 80)
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

- `plans/feedback-fixes/design.md` — patched design, ready for execution
- `plans/skill-improvements/design.md` — previous session's changes (applied, committed)
- `plans/claude-tools-recovery/design.md` — 4 phases (R0-R4), pending execution
- `agent-core/skills/handoff/examples/good-handoff.md:58` — pre-migration artifact causing learnings section

---
*Handoff by Opus. Design review complete — feedback-fixes patched and ready for execution.*
