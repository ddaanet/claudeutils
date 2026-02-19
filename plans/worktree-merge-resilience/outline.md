# Worktree Merge Resilience — Outline

## Approach

Transform `_worktree merge` from an abort-on-conflict pipeline to a state-machine that preserves merge state, reports rich context, and supports idempotent resume.

Core change: replace the sequential Phase 1→2→3→4 call chain with a state-detecting entry point that routes to the appropriate phase based on current git state.

## Key Decisions

**D-1: Exit code 3 for conflict resolution needed.** Keeps 1=error, 2=fatal. Exit 3 means "merge paused — conflicts exist, resolve and re-run." Skill contract (SKILL.md Mode C) updated to handle new code.

**D-2: Phase 2 continues through submodule conflicts.** Submodule conflict leaves MERGE_HEAD in agent-core, continues to Phase 3. Parent merge auto-resolves agent-core pointer to "ours" (already handled). Agent resolves submodule + parent conflicts in one pass.

**D-3: Phase 3 preserves merge state on source conflicts (FR-2, NFR-2).** Remove `git merge --abort` + `git clean -fd` (lines 170-175). After auto-resolving session/learnings/agent-core, remaining conflicts → report + exit 3. Working tree keeps MERGE_HEAD and conflict markers. No code path discards staged auto-resolutions or working tree state.

**D-4: Untracked files — `git add` then retry.** When `git merge` fails because untracked files would be overwritten: parse file list from stderr, `git add` each colliding file, retry merge. Git then handles them as normal merge entries — same content auto-merges, different content produces standard conflict markers handled by the existing pipeline. One code path instead of same-vs-different branching. The file will be tracked post-merge regardless (incoming branch has it tracked).

**D-5: State machine at merge entry.** Detect current state before routing:
- `merged` — slug is ancestor of HEAD → Phase 4 (precommit only)
- `parent_resolved` — MERGE_HEAD exists, no unresolved conflicts → Phase 4
- `parent_conflicts` — MERGE_HEAD exists, unresolved conflicts → report + exit 3
- `submodule_conflicts` — agent-core MERGE_HEAD exists → check resolution, continue or report
- `clean` — no merge in progress → full pipeline (Phase 1→2→3→4)

Re-running Phase 2 when submodule is already merged is a no-op (existing skip logic), so `clean` state after manual submodule resolution correctly resumes.

**D-6: `_git` helper must not raise on conflict.** Phase 2 calls `_git("-C", "agent-core", "merge", ...)` with default `check=True`. Must switch to `check=False` and handle return code explicitly.

**D-7: No data loss invariant (NFR-2).** Cross-cutting: no code path calls `git merge --abort`, `git clean -fd`, or discards staged content. Audit every error/conflict handler. Current `--abort` + `clean -fd` in Phase 3 is the primary violation; Phase 2's uncaught exception is secondary (leaves submodule mid-merge, which is acceptable — data preserved).

**D-8: All output to stdout (C-2).** Single output stream — eliminates `2>&1` at every call site. Exit code (0/1/2/3) carries the semantic signal, not the stream. The only consumer is the worktree skill/agents via Bash tool, which sees combined output regardless. No prompts, no interactive input. File paths in output must be relative to repo root for direct use in `git add <path>`.

## Affected Files

- `src/claudeutils/worktree/merge.py` — all phases, new state detection, new conflict reporting
- `agent-core/skills/worktree/SKILL.md` — Mode C exit code 3 handling
- `tests/test_worktree_merge_*.py` — new tests for each FR, updates to existing tests that assert abort behavior

## Open Questions

**Q-1 (from requirements): Resolved.** Untracked file handling — `git add` + retry (D-4). Stashing is fragile. Content comparison creates two code paths. `git add` converts the special case into the general case (merge conflict), which the pipeline already handles. File becomes tracked — acceptable since incoming branch has it tracked anyway.

**Q-2 (from requirements):** Exit code 3 selected (D-1). Redefining 1 would break the existing skill contract where 1 = investigate error. 3 is a clean new semantic.

## Scope Boundaries

**IN:**
- State detection + idempotent resume (FR-5)
- Submodule conflict pass-through (FR-1)
- Parent merge preservation (FR-2)
- Untracked file collision handling (FR-3)
- Rich conflict output (FR-4)
- Exit code 3 (NFR-1)
- No data loss on any code path (NFR-2)
- SKILL.md update (C-1)
- Non-interactive resolution compatibility (C-2)

**OUT:**
- Automatic source code conflict resolution — only session/learnings/agent-core get auto-resolution
- Changes to `resolve.py` session/learnings strategies
- Changes to `rm.py` or `new.py`
- Interactive conflict resolution

## Phase Typing

- **Phase 1: State detection + idempotent resume (FR-5)** — TDD. State machine logic, multiple code paths.
- **Phase 2: Submodule conflict pass-through (FR-1)** — TDD. Behavioral change to Phase 2.
- **Phase 3: Parent merge preservation + untracked handling (FR-2, FR-3)** — TDD. Core behavioral change + new detection logic.
- **Phase 4: Conflict context output (FR-4)** — TDD. Output contract: conflicted file list with conflict type, per-file diff stats (ours vs theirs), branch divergence summary, actionable hint.
- **Phase 5: Exit code + skill update + stdout unification (NFR-1, C-1, C-2, D-8)** — General. Exit code threading, SKILL.md Mode C update, migrate all `click.echo(..., err=True)` to `click.echo()` (stdout).
