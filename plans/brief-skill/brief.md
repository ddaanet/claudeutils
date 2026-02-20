# Brief: Brief Skill

## 2026-02-20: Pattern definition and design decisions

### The pattern

Cross-tree async context transfer. One session has context (scope changes, design decisions, discussion conclusions) that affects a task in another worktree. Direct edits waste context (require reading remote files). Instead: write a file the worktree agent reads on pickup.

**Name:** "brief" — to brief someone is to edify them with essential context before action. Works as noun ("write a brief") and verb ("brief the worktree").

### Producer: `/brief <slug>` skill

- ~20 lines of SKILL.md
- Args: worktree slug or plan name
- Agent composes content from conversation context
- Writes to `plans/<plan-name>/brief.md`
- Append-only with timestamped H2 entries (multiple briefs accumulate)
- No auto-commit (part of next `hc`)
- No CLI tool, no agent, no hook

### Consumer: startup check

- Worktree agent checks plan directory for `brief.md` on task pickup
- Integration point: `task-context.sh` or focused session template in `_worktree new`
- `git show main:plans/<plan>/brief.md 2>/dev/null` when plan dir only exists on main

### Location rationale

Briefs live in plan directory (`plans/<plan>/brief.md`) alongside requirements.md, design.md, outline.md — same family of context artifacts. No separate `plans/briefs/` namespace.

### What it's NOT

- Not a CLI tool (no parsing, no logic)
- Not an agent (no autonomous behavior)
- Not a hook (no event trigger)
- Not requirements/design — too simple for that ceremony
