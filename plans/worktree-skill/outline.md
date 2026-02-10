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

## Error Handling

- Lock file conflicts: built-in wait-1s-and-retry (2 retries max) before failing
- Never agent-initiate lock file removal (existing learning)

## Testing

- Integration-first: pytest with tmp_path creating real git repos + submodules
- No subprocess mocking for behavior validation — only for error injection (lock files, disk errors)
- Shared fixture: base repo + submodule created once, each test gets fresh clone
- Start with simplest non-degenerate happy path, build up
- Autospec on all mocks
- Critical scenarios: submodule merge, conflict resolution + resume, idempotent merge, clean-tree gate
