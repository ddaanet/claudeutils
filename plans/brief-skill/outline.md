# Brief Skill: Outline

## Approach

Create a lightweight skill for cross-tree async context transfer. One session writes essential context (scope changes, design decisions, discussion conclusions) to a file that the target worktree agent reads on task pickup.

**Pattern:** "brief" — noun ("write a brief") and verb ("brief the worktree"). Edify semantics.

## Producer: `agent-core/skills/brief/SKILL.md`

Skill invoked as `/brief <slug-or-plan-name>`. Process:
1. Resolve argument to plan directory (check `plans/<arg>/` or match worktree slug via session.md)
2. Compose brief from current conversation context
3. Append timestamped H2 entry to `plans/<plan>/brief.md` (create if needed)
4. No auto-commit — included in next `hc`

Brief format: `## YYYY-MM-DD: <topic>\n<dense context>`

Append-only — multiple briefs accumulate as separate H2 entries.

Follows when/how skill pattern: ~20 lines body, user-invocable, minimal allowed-tools (Read, Write, Edit).

## Consumer: execute-rule.md task pickup

Add 2-3 lines to "Task Pickup: Context Recovery" section in `agent-core/fragments/execute-rule.md`:
- After running task-context.sh, check for `plans/<plan>/brief.md`
- In main tree: direct Read
- In worktrees: `git show main:plans/<plan>/brief.md 2>/dev/null` (plan dir may only exist on main)

No changes to task-context.sh — the agent handles brief discovery from the instructions.

## Scope

**IN:** SKILL.md (producer), execute-rule.md update (consumer documentation), `just sync-to-parent` for discovery
**OUT:** No CLI tool, no agent, no hook, no script changes

## Key Decisions

- **Location:** `plans/<plan>/brief.md` alongside other plan artifacts (not separate namespace)
- **Accumulation:** Append-only with timestamped H2 entries (not overwrite)
- **Consumer integration:** Documentation in execute-rule.md (not script modification)
- **Discovery:** Auto-discovered via `just sync-to-parent` symlinking to `.claude/skills/`
