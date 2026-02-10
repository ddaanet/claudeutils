# Cycle 3.11

**Plan**: `plans/worktree-skill/runbook.md`
**Execution Model**: haiku
**Phase**: 3
**Report Path**: `plans/worktree-skill/reports/cycle-3-11-notes.md`

---

## Cycle 3.11: Take-ours strategy

**RED — Behavioral Verification:**

Create test fixture for source code merge conflict between main and worktree branches. Setup a diverged state where both branches modify same source file at same location. Test that `resolve_source_conflicts()` defaults to `--ours` version for all non-session conflict files.

Expected behavior: Each conflicted source file resolved with `git checkout --ours <file>`, then staged with `git add <file>`. Function returns list of resolved files (exact file paths depend on test fixture — verify list contains all conflicted files excluding session context patterns).

Test verifies:
- Conflict markers present before resolution (`grep -q "^<<<<<<< HEAD" <file>`)
- After resolution, working tree version matches `git show :2:<file>` (ours side)
- File is staged (`git diff --cached --name-only` includes file)
- No conflict markers remain in working tree

Setup requires real git repos with actual merge conflicts (not mocked):
1. Create base repo with initial source file content
2. Branch to worktree branch, modify source file (add function A)
3. Return to main branch, modify same location (add function B)
4. Attempt merge → conflict state
5. Extract conflict list via `git diff --name-only --diff-filter=U`
6. Invoke `resolve_source_conflicts(conflict_list, exclude_patterns=["agents/session.md", "agents/jobs.md", "agents/learnings.md"])`

**GREEN — Behavioral Description:**

Implement `resolve_source_conflicts()` in `conflicts.py`. Function takes conflict list and exclude patterns, filters to source files only (excluding session context files), then applies take-ours resolution.

Behavior hints:
- Filter conflict list against exclude patterns (deterministic, not fuzzy matching)
- For each source file in filtered list, run subprocess commands: `git checkout --ours <file>` followed by `git add <file>`
- Capture any git command failures and propagate errors
- Return list of successfully resolved files
- Function is deterministic (no agent judgment), relies on mechanical git operations

Implementation approach: subprocess wrappers for git checkout and git add, error handling for missing files or git failures, return resolved paths for caller verification.

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/worktree-skill/reports/cycle-3-11-notes.md

---
