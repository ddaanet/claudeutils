# Session Handoff: 2026-01-30

**Status:** Feedback-fixes executed; submodule safety hook added

## Completed This Session

**Feedback-fixes execution:**
- Applied all changes from `plans/feedback-fixes/design.md`
- tdd-task.md: Moved log entry to Step 5 (before commit), removed orphaned Post-Refactoring section, renumbered steps 1-7, added token-efficient bash blocks, simplified sanity check
- Handoff skill: Added section constraints (5 allowed sections), design decisions → learnings guidance, anti-pattern for "commit this" tasks
- good-handoff.md: Removed pre-migration `## Recent Learnings` section (lines 57-77)
- .gitignore: Added `*.local.*` pattern
- Git cleanup: `git rm --cached` for .local.md files (staged for commit)
- agent-core hooks: Restructured hooks.json with matcher entries, created submodule-safety.py PreToolUse hook

**Submodule safety hook:**
- Warns when git operations in project root reference submodule paths
- Warns when inside submodule (reminds to cd back)
- Recommends subshell pattern: `(cd submodule && git ...)` to preserve cwd
- Non-blocking warnings only (doesn't prevent operations)

## Pending Tasks

- [ ] **Execute recovery** — `/plan-tdd` on `plans/claude-tools-recovery/design.md`
- [ ] **Run /remember** — learnings.md at 131 lines (soft limit 80)
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
- New submodule-safety hook warns about common cwd mistakes

## Reference Files

- `plans/feedback-fixes/design.md` — executed this session
- `plans/claude-tools-recovery/design.md` — 4 phases (R0-R4), pending execution
- `agent-core/hooks/submodule-safety.py` — new PreToolUse hook script

---
*Handoff by Sonnet. Feedback-fixes applied; ready for commit.*
