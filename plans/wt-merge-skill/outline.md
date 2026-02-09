

This discussion has produced a design outline for the wt-merge skill. The key decisions:

- **Clean tree gate:** Fail on non-session-context dirty files. Session context (session.md, jobs.md, learnings.md) allowed dirty — handoff handles them.
- **Full ceremony pre-merge:** `/handoff, /commit` via continuation chain — no degraded bookkeeping commits.
- **`--commit` flag obsolete:** Continuation passing replaces the tail-call hack with explicit skill chaining.
- **Auto-resolve session conflicts:** Deterministic merge (keep both sides) for session context files. Escalate non-session conflicts.
- **Post-merge cleanup:** Remove worktree task from session.md, amend merge commit, `just wt-rm`.
- **Dependency:** Blocked on continuation-passing design.

Two pending tasks captured:
- **Explore removing bash tool git prompt noise** (spun off to `wt/bash-git-prompt`)
- **Package worktree handling as skill, add git clean tree check before merge** (this discussion is the design seed)
