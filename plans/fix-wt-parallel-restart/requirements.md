# Fix wt parallel restart disqualification

## Requirements

### Functional Requirements

**FR-1: Remove restart disqualification from worktree skill Mode B**
In `agent-core/skills/worktree/SKILL.md` Mode B step 2, remove the "Restart requirement check" bullet that disqualifies tasks with restart flag from parallel grouping. Update the group selection line from "all four criteria" to "all three criteria."

Acceptance criteria:
- Mode B step 2 has exactly three criteria: plan directory independence, logical dependencies, model tier compatibility
- No mention of restart as a disqualification factor in Mode B
- Step 3 error message no longer references "restart requirements"

**FR-2: Remove restart from execute-rule parallel task detection**
In `agent-core/fragments/execute-rule.md` parallel task detection section, remove "No restart requirement" from the criteria list.

Acceptance criteria:
- Parallel task detection lists exactly three criteria: no shared plan directory, no logical dependency, compatible model tier
- Tasks with restart flag are eligible for parallel grouping via `wt`

### Constraints

**C-1: Worktrees inherently satisfy restart**
The restart flag means "session restart required for structural changes to load at startup." Worktree creation satisfies this — `cd <path> && claude` starts a fresh session. This is the reasoning for the change, not an implementation constraint.

**C-2: Edit source files only**
`.claude/skills/worktree/SKILL.md` is a symlink to `agent-core/skills/worktree/SKILL.md`. Edit the source (`agent-core/`), not the symlink target.

### Out of Scope

- Merge-time interaction between structural changes — already handled by merge ceremony (conflict detection, precommit validation)
- Dependency analysis for tasks touching same files — already handled by criteria 1-2 (plan directory independence, logical dependencies)
- Changes to Mode A (single task) or Mode C (merge ceremony)
