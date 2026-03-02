# Brief: Fix wt parallel restart disqualification

## Problem

Worktree skill Mode B (parallel group detection) disqualifies tasks with `restart` flag from parallel grouping. This is a false constraint.

## Reasoning

The `restart` flag means "session restart required for structural changes to load at startup" (hooks, agents, plugins, MCP config). Worktree creation inherently satisfies this — `cd <path> && claude` starts a fresh session where all startup-loaded files are read from scratch.

The four parallel group criteria:
1. Plan directory independence — real dependency signal
2. Logical dependencies — real dependency signal
3. Model tier compatibility — real constraint
4. **Restart requirement — false constraint** (worktrees already guarantee fresh sessions)

Merge-time interaction between structural changes is already handled by the merge ceremony (conflict detection, precommit validation). The dependency analysis (criteria 1-2) catches tasks touching the same files.

## Fix

Source file: `agent-core/skills/worktree/SKILL.md` (`.claude/skills/worktree/SKILL.md` is symlink)

In Mode B step 2, remove the restart requirement check bullet:
- Delete: "**Restart requirement check:** Check restart flag for each task. Any task marked 'Restart: yes' disqualifies from parallel grouping."
- Update: "Select the **largest independent group** satisfying all four criteria" → "all three criteria"

In the execute-rule.md parallel task detection section, same fix — remove restart requirement from the parallel detection criteria if it references it there.

## Origin

Discussion in ups-topic-injection worktree, 2026-03-01. `wt` (Mode B) rejected a valid parallel group (Fix UPS topic findings + Review TDD dispatch) because Review TDD dispatch had restart flag.
