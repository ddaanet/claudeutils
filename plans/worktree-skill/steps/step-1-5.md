# Cycle 1.5

**Plan**: `plans/worktree-skill/runbook.md`
**Execution Model**: haiku
**Phase**: 1
**Report Path**: `plans/worktree-skill/reports/cycle-1-5-notes.md`

---

## Cycle 1.5: new with --session pre-commit

**RED: Test behavior before implementation**

Create test `test_worktree_cli.py::test_new_session_precommit`:
- Given: Focused session file at `tmp/test-session.md` with content `"# Focused Session\n\nTask content"`
- When: Run `_worktree new test-feature --session tmp/test-session.md`
- Then: Worktree `wt/test-feature/` exists on branch `test-feature`
- Then: File `wt/test-feature/agents/session.md` contains focused session content
- Then: Branch has one commit ahead of base (the focused session commit)
- Then: Main worktree index is unmodified (verify via `git diff --cached` output empty in main)
- Then: Commit message is `"Focused session for test-feature"`

**Expected failure:** `--session` flag not implemented, or focused session not committed, or main index polluted.

**GREEN: Implement minimal behavior**

Add `--session` optional parameter that pre-commits focused session.md to branch HEAD.

**Behavior:**
- When `--session` provided: create commit with session.md, then create worktree from that commit
- Session file content becomes `agents/session.md` in new worktree
- Main worktree index must remain unmodified (critical requirement)
- Commit message: "Focused session for {slug}"
- When `--session` not provided: use existing flow from Cycle 1.1 (no pre-commit)

**Approach:**
- Use git plumbing with temp index to avoid polluting main index
- Sequence: hash-object (session) → read-tree (base) → update-index (session) → write-tree → commit-tree → branch → worktree add
- All index operations use temp index via `GIT_INDEX_FILE` environment variable
- Clean up temp index file after branch creation

**Hints:**
- Temp index: `tempfile.NamedTemporaryFile(delete=False, suffix='.index')`
- Environment: `subprocess.run(..., env={**os.environ, 'GIT_INDEX_FILE': tmpfile})`
- Design section "CLI Specification" lines 92-102 provides exact command sequence

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/worktree-skill/reports/cycle-1-5-notes.md

---
