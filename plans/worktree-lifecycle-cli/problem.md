# Problem: Worktree Lifecycle CLI

Umbrella plan for worktree CLI improvements. Consolidates:

- `wt-exit-ceremony` — exit ceremony for worktree sessions
- `wt-rm-task-cleanup` — task entry cleanup on worktree removal
- `worktree-ad-hoc-task` — ad-hoc task creation within worktrees
- Worktree CLI UX improvements
- `--base` submodule bug fix

## Investigation Scope

- Exit ceremony: what state transitions and side effects should occur when leaving a worktree session
- Task cleanup: how `_worktree rm` should handle session.md task entries (currently strips marker but leaves entry)
- Ad-hoc tasks: how to create tasks scoped to a worktree without main session.md
- CLI UX: command discoverability, help text, error messages
- `--base` submodule: `_worktree new --base` fails when submodule ref differs between branches
