# Worktree Skill — Design Outline

## Approach

Single `/worktree` skill in `agent-core/skills/worktree/` with a `claudeutils _worktree` internal CLI subcommand handling all git mechanics. Skill SKILL.md orchestrates session.md manipulation, ceremony, and parallel detection. CLI handles deterministic operations. Clean room design. Full TDD discipline.

Absorbs wt-merge-skill plan.

## Key Decisions

- Single skill with subcommand dispatch (new/rm/merge/ls)
- `claudeutils _worktree <subcommand>` — single CLI entry point, Python, TDD
- Branch naming: slug directly (no `wt/` prefix)
- Directory convention: `wt/<slug>/` inside project root
- Design principle: any agent workflow needing >1 shell command → script it
- Hybrid boundary: CLI tailored to skill workflow, not generic git wrappers
- Idempotent merge: stops at conflict/precommit failure, resumes after resolution
- Reuse focus-session.py for session extraction
- Delete justfile wt-* recipes

## CLI Subcommands

- `_worktree new <slug> [--base HEAD] [--session <path>]`
- `_worktree rm <slug>`
- `_worktree merge <slug>` — combined submodule+parent merge, idempotent
- `_worktree ls`
- `_worktree clean-tree` — report status for tree + submodules, fail if not clean
- `_worktree add-commit <files...>` — one-shot stage+commit, stdin commit message

## Skill Orchestration (SKILL.md)

- Slug derivation from task name
- Session.md task movement (Pending → Worktree Tasks)
- Focused session extraction (focus-session.py)
- Parallel group detection (prose, not scripted)
- Handoff/commit ceremony before merge
- Error communication and conflict resolution guidance

## Scope

**In:** CLI subcommand (TDD), SKILL.md, execute-rule.md Mode 5 update, delete justfile recipes, update handoff template, end-to-end tests (submodule merging), absorb wt-merge-skill

**Out:** Parallel detection scripting, focus-session.py changes, stale worktree cleanup

## Submodule Merge Resolution

The `merge` subcommand must handle diverged submodule commits:

**Problem:** Worktree's agent-core may have commits not reachable from main repo's agent-core. Git's `submodule update --init` fetches from remote, which fails if commits were never pushed. Merge strategy `ort` reports "commits don't follow merge-base" and leaves CONFLICT marker.

**Resolution sequence (deterministic, scriptable):**
1. Before merge: fetch worktree's submodule objects into local submodule (`git -C agent-core fetch <worktree-gitdir-path> <commit>`)
2. The gitdir path for worktree submodules: `.git/worktrees/<worktree-name>/modules/<submodule-name>`
3. Inside submodule: `git merge --no-edit <worktree-branch>` (merges both sides)
4. Stage updated submodule: `git add agent-core`
5. Commit submodule merge before or as part of main merge

**Ancestry check:** `git -C agent-core merge-base --is-ancestor <worktree-commit> <local-commit>` — if true, local already includes worktree changes (fast-forward case, no merge needed). If false or if worktree commit not found locally, fetch + merge required.

**Post-merge verification:** Both original pointers must be ancestors of new submodule HEAD.

## Session File Conflict Resolution

Merge conflicts in session context files (session.md, learnings.md, jobs.md) follow deterministic patterns:

- **session.md:** Keep ours as base, but **extract new pending tasks from worktree side first**. Worktree may have accumulated tasks during its lifetime (e.g., "Execute plugin migration" task created during worktree work). Blind `--ours` loses these. Strategy: parse worktree-side Pending Tasks, diff against main-side, append new ones to main session.md after merge.
- **learnings.md:** Keep both sides. Append-only file — remove conflict markers, preserve all content from both branches. Both sides add at the end, so conflict is always "both added here."
- **jobs.md:** Keep ours, then apply worktree-side status updates if any plan status advanced.

These are non-cognitive operations — script them in the CLI, don't delegate to agents.

**Task extraction algorithm (session.md merge):**
1. Parse worktree session.md Pending Tasks section (regex: `^- \[ \] \*\*(.+?)\*\*`)
2. Parse main session.md Pending Tasks section (same regex)
3. New tasks = worktree tasks not in main (match on task name)
4. Append new tasks to main session.md Pending Tasks section
5. Remove worktree task entry from Worktree Tasks section (task is now merged back)

## Error Handling

- Lock file conflicts: built-in wait-1s-and-retry (2 retries max) before failing
- Never agent-initiate lock file removal (existing learning)
- Failed merge debris: after merge abort, check for untracked files materialized from source branch (`git clean -fd -- <dirs>`)
- Submodule object not found: fetch from worktree gitdir before retrying merge

## Testing

- Integration-first: pytest with tmp_path creating real git repos + submodules
- No subprocess mocking for behavior validation — only for error injection (lock files, disk errors)
- Shared fixture: base repo + submodule created once, each test gets fresh clone
- Start with simplest non-degenerate happy path, build up
- Autospec on all mocks
- Critical scenarios: submodule merge (diverged commits), submodule merge (fast-forward), session file conflict resolution (learnings keep-both, session keep-ours), conflict resolution + resume, idempotent merge, clean-tree gate, merge debris cleanup after abort
