# Worktree Merge Resilience

## Requirements

### Functional Requirements

**FR-1: Proceed through submodule conflicts**
Phase 2 (submodule merge) currently raises `CalledProcessError` on conflict, aborting the entire merge pipeline. When submodule merge produces conflicts, the tool should leave the submodule merge in progress (with MERGE_HEAD) and continue to Phase 3 (parent merge) rather than aborting.

Acceptance criteria:
- Submodule conflict in agent-core does not prevent parent merge from starting
- Conflict files are reported to stderr with enough context for the agent to resolve
- After agent resolves submodule conflicts and commits, re-running `_worktree merge` resumes from Phase 3

**FR-2: Leave parent merge in progress on source conflicts**
Phase 3 currently aborts the merge (`git merge --abort; git clean -fd`) when source file conflicts remain after auto-resolving session/learnings/jobs. This destroys the merge state the agent needs to resolve conflicts. Instead, leave the merge in progress (MERGE_HEAD present) so the agent can resolve conflicts in the working tree.

Acceptance criteria:
- After auto-resolving session/learnings/agent-core conflicts, remaining conflicts are reported but merge is NOT aborted
- Working tree contains conflict markers in unresolved files
- Agent can edit conflicted files, `git add` them, then re-run `_worktree merge` to complete
- Exit code distinguishes "conflicts need resolution" from "fatal error"

**FR-3: Handle untracked file collisions**
`git merge` fails before starting when untracked files on main would be overwritten by incoming branch content. Phase 3 should detect this failure mode and either: (a) stash/remove untracked files that match incoming tracked files, or (b) report the collision with actionable guidance.

Acceptance criteria:
- Untracked files that exist identically in the incoming branch are handled automatically (same content → safe to overwrite)
- Untracked files that differ from incoming branch are reported as conflicts (not silently overwritten)
- The merge proceeds after handling, rather than aborting

**FR-4: Provide conflict context in output**
When conflicts occur (submodule or parent), the tool currently outputs minimal information ("Merge aborted: conflicts in X"). Output should include context the agent needs to resolve:

Acceptance criteria:
- Conflicted file list with conflict type (both-modified, delete/modify, etc.)
- For each conflicted file: `git diff --stat` between ours and theirs showing scope of divergence
- Branch divergence summary: commit count since merge-base on each side
- Hint: "Resolve conflicts, `git add`, then re-run `claudeutils _worktree merge <slug>`"

**FR-5: Idempotent resume across all phases**
Re-running `_worktree merge <slug>` after partial completion should detect current state and resume from the appropriate phase. Currently Phase 4 handles resume (detects MERGE_HEAD), but Phases 2 and 3 do not.

Acceptance criteria:
- If submodule already merged (agent-core HEAD matches or is ahead of branch commit): skip Phase 2
- If parent merge is in progress (MERGE_HEAD exists, no conflicts): proceed to Phase 4
- If parent merge is in progress with conflicts: report remaining conflicts, exit with "conflicts need resolution" code
- If merge commit already exists and branch is merged: skip to precommit validation only

### Non-Functional Requirements

**NFR-1: Backward-compatible exit codes**
New exit codes for "conflicts need resolution" must not collide with existing semantics (0=success, 1=error, 2=fatal/safety).

**NFR-2: No data loss on any code path**
No merge code path should discard work. `git merge --abort` + `git clean -fd` (current behavior) destroys staged auto-resolutions and untracked files. All code paths must preserve work-in-progress.

### Constraints

**C-1: Skill contract**
The worktree skill (SKILL.md Mode C) parses exit codes and stderr. Changes to exit code semantics or output format require corresponding skill updates.

**C-2: Agent capability**
The calling agent (skill-driven or orchestrated) must be able to resolve conflicts using Edit + Bash(`git add`). The tool should not assume interactive resolution.

### Out of Scope

- Interactive conflict resolution UI — agents resolve via Edit tool
- Three-way merge visualization — standard git conflict markers sufficient
- Automatic source code conflict resolution — only session/learnings/jobs get auto-resolution

### Dependencies

- Workwoods branch merge (in progress) — this work touches the same `merge.py` that workwoods refactored (extracted `resolve.py`)
- Error handling design (worktree: `error-handling-design`) — may define error classification that applies here

### Open Questions

- Q-1: Should FR-3 (untracked file handling) stash files, or `git add` them before merging so git can do a proper three-way merge?
- Q-2: What exit code for "conflicts need resolution"? Current 1 means error, 2 means fatal. Could use 3, or redefine 1 to include "actionable conflicts" since the agent's response is the same (read stderr, act).

### References

- `src/claudeutils/worktree/merge.py` — current merge implementation (4 phases)
- `src/claudeutils/worktree/resolve.py` — workwoods refactored resolution strategies (on `design-workwoods` branch)
- `agent-core/skills/worktree/SKILL.md` — Mode C skill contract (exit code parsing)
- This session's merge attempt — FR-1 through FR-4 directly observed
