# Worktree Fixes

## Requirements

### Functional Requirements

**FR-1: Task name constraints**
Task names are prose identifiers (e.g. "Fix session merge"), constrained to be branch-name-suitable. Slug derivation becomes near-identity: lowercase + spaces→hyphens.

Accepted characters: `[a-zA-Z0-9 .\-]`, max 25 characters. No backticks, colons, slashes, or other punctuation in task names. Numbers permitted for collision avoidance (e.g. "Fix session merge 2").

Acceptance criteria:
- `derive_slug()` produces lossless round-trippable slugs (no truncation)
- Remove `max_length` parameter (no truncation needed when names are constrained)
- `focus_session()` pattern matches constrained names without escaping issues
- Validation function exists for task name format checking

**FR-2: Precommit task name validation**
Precommit validates all task names in `agents/session.md` conform to FR-1 constraints.

Acceptance criteria:
- Scans Pending Tasks and Worktree Tasks sections
- Rejects names containing forbidden characters (backticks, colons, slashes, etc.)
- Clear error message identifying the offending task name and character
- Runs as part of `just precommit`

**FR-4: Session merge preserves full task blocks**
`_resolve_session_md_conflict()` extracts full task blocks (task line + indented continuation lines) from worktree side, not just the `- [ ] **` line.

Current bug: set diff of single lines loses metadata sub-bullets. E.g. a worktree-spawned task with 3 continuation lines merges as 1 line.

Acceptance criteria:
- New tasks from worktree side include all indented continuation lines
- Inserted before next `##` section header with proper blank line separation
- Existing task detection still works (match by task name, not full line)

**FR-5: Merge commit always created when merge initiated**
`_phase4_merge_commit_and_precommit` must create the merge commit even when conflict resolution nullifies the diff. Currently, when session.md conflict resolves to no net changes, `git diff --cached --quiet` succeeds → commit skipped → branch left as orphan → `git branch -d` correctly rejects as "not fully merged."

Root cause: skipping merge commit when staged changes are empty. But a merge was initiated — the branch must become an ancestor of HEAD so `git branch -d` succeeds.

Acceptance criteria:
- After `_phase3_merge_parent` initiates a merge, phase 4 always commits (even with empty diff)
- `git branch -d` succeeds in `rm` after merge (branch is reachable from HEAD)
- No behavior change when merge produces real changes (already works)

**FR-6: Automate session.md task movement on worktree create and remove**
`claudeutils _worktree new --task` and `claudeutils _worktree rm` should move tasks between Pending Tasks and Worktree Tasks sections in `agents/session.md` automatically. Currently this is manual agent work in the skill (Mode A step 4, Mode C step 3).

On `new --task`:
- Move task from Pending Tasks to Worktree Tasks with `→ <slug>` marker
- Preserve full task block (task line + continuation lines)

On `rm` (after merge):
- Remove task from Worktree Tasks only if the task was removed (completed or deleted) in the merged worktree's session.md
- If task still exists as pending in the merged content, keep it in Worktree Tasks (or move back to Pending)

Acceptance criteria:
- `new --task` edits session.md in the main repo (not the worktree copy)
- `rm` removes worktree task entry only when task was removed on the merged branch
- `rm` preserves worktree task entry when task still pending in merged content
- Skill Mode A steps 3-4, Mode B step 4, and Mode C step 3 become no-ops (tool handles it)
- Idempotent: re-running doesn't duplicate or corrupt entries

### Out of Scope
- Task name autocomplete or suggestion system
- Worktree parallel group detection (Mode B) changes
- Session merge for learnings.md or jobs.md (already handled)
- Slug format changes beyond removing truncation (hyphens in slugs are fine, constraint is on source task names)

### Dependencies
- FR-2 depends on FR-1 (validation needs format spec)
- FR-4 and FR-5 are independent of FR-1/2
- FR-6 depends on FR-1 (task name format for reliable pattern matching)

### Open Questions
- Q-1: Should `derive_slug` validate task name format and reject invalid names, or is that only precommit's job? (Fail-fast at creation vs catch-at-commit)
