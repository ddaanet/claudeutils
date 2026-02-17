# Worktree RM Safety Gate — Requirements

## Context

`claudeutils _worktree rm <slug>` removes worktrees after merge. Current guard checks unmerged commits but lacks dirty-tree checks, force bypass, and proper exit codes. The worktree skill (Mode C) calls rm after merge but can't distinguish guard refusal from other errors.

**Source:** Session task notes, exploration report (`plans/worktree-rm-safety/reports/explore-current-impl.md`).

## Functional Requirements

### FR-1: Dirty tree check (parent + submodule)
Before removal, verify both parent repo and agent-core submodule have clean working trees. Block removal if either is dirty. Currently only warns (non-blocking).

**Acceptance:** `_worktree rm` exits non-zero if parent or submodule has uncommitted changes. Error message identifies which tree is dirty.

### FR-2: Exit code 2 for guard refusal
Guard refusal currently uses `click.Abort` (exit 1). Change to exit 2 so the skill can distinguish guard refusal from merge conflicts (exit 1).

**Acceptance:** Guard refusal exits 2. Skill Mode C handles exit 2 as "guard refused" distinct from exit 1.

### FR-3: `--force` bypass
Add `--force` flag to bypass safety checks (dirty tree, guard). For emergency situations where user needs to force-remove.

**Acceptance:** `claudeutils _worktree rm --force <slug>` bypasses dirty check and guard. Skill passes `--force` when appropriate.

### FR-4: Skill confirmation
Prevent direct CLI removal without skill workflow. The skill should pass a confirmation mechanism (flag or env var) that direct CLI invocation lacks.

**Acceptance:** Direct `claudeutils _worktree rm <slug>` without confirmation prompts or refuses. Skill-invoked rm proceeds without prompt.

### FR-5: No destructive suggestions ✅
CLI output never suggests destructive commands (e.g., `git branch -D`). Already implemented and tested.

## Non-Functional

- Exit code semantics must be consistent: 0 = success, 1 = operational error, 2 = guard/safety refusal
- All new checks need tests (TDD)
- Skill SKILL.md must be updated to pass new flags

## Out of Scope

- Merge command changes
- Worktree creation changes
- Session.md format changes
