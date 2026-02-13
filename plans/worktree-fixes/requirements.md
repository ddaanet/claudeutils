# Worktree Fixes

## Requirements

### Functional Requirements

**FR-1: Task name constraints**
Task names are prose identifiers (e.g. "Fix session merge"), constrained to be branch-name-suitable. Slug derivation becomes near-identity: lowercase + spaces→hyphens.

Accepted characters: `[a-zA-Z0-9 ]`. No hyphens, backticks, colons, slashes, or other punctuation in task names. Numbers permitted for collision avoidance (e.g. "Fix session merge 2").

Acceptance criteria:
- `derive_slug()` produces lossless round-trippable slugs (no truncation)
- Remove `max_length` parameter (no truncation needed when names are constrained)
- `focus_session()` pattern matches constrained names without escaping issues
- Validation function exists for task name format checking

**FR-2: Precommit task name validation**
Precommit validates all task names in `agents/session.md` conform to FR-1 constraints.

Acceptance criteria:
- Scans Pending Tasks and Worktree Tasks sections
- Rejects names containing forbidden characters (backticks, colons, slashes, hyphens, etc.)
- Clear error message identifying the offending task name and character
- Runs as part of `just precommit`

**FR-3: Migrate existing task names**
Rename all existing task names in `agents/session.md` to conform to FR-1 constraints. One-time migration.

Acceptance criteria:
- All Pending Tasks and Worktree Tasks names pass FR-2 validation after migration
- References in Blockers/Gotchas updated if they mention task names
- Git history references (`git log -S`) remain functional for old names (no rewriting needed — old names exist in history, new names going forward)

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

### Out of Scope
- Task name autocomplete or suggestion system
- Worktree parallel group detection (Mode B) changes
- Session merge for learnings.md or jobs.md (already handled)
- Slug format changes beyond removing truncation (hyphens in slugs are fine, constraint is on source task names)

### Dependencies
- FR-2 depends on FR-1 (validation needs format spec)
- FR-3 depends on FR-2 (migration should pass validation)
- FR-4 and FR-5 are independent of FR-1/2/3

### Open Questions
- Q-1: Should `derive_slug` validate task name format and reject invalid names, or is that only precommit's job? (Fail-fast at creation vs catch-at-commit)
