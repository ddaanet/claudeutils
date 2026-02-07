# Session: Worktree — Fix agent-core justfile links

**Status:** Focused worktree for parallel execution.

## Pending Tasks

- [ ] **Fix agent-core justfile to link all agents and skills** — Missing at least remember-task and memory-refactor

## Blockers / Gotchas

**Sandbox exemption needed:** `just sync-to-parent` requires `dangerouslyDisableSandbox: true` (creates/updates symlinks in `.claude/agents/`, `.claude/skills/`).

## Reference Files

- **agent-core/justfile** — sync-to-parent recipe
- **agent-core/agents/** — Agent definitions to link
- **agent-core/skills/** — Skill definitions to link
- **.claude/agents/** — Symlink target directory
- **.claude/skills/** — Symlink target directory

## Next Steps

Audit agent-core/{agents,skills}/ directories and compare against .claude/{agents,skills}/ to identify missing links.

---
*Focused worktree for agent-core justfile link fixes.*
