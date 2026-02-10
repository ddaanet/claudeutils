# Cycle 0.9

**Plan**: `plans/worktree-skill/runbook.md`
**Execution Model**: haiku
**Phase**: 0
**Report Path**: `plans/worktree-skill/reports/cycle-0-9-notes.md`

---

## Cycle 0.9: add-commit idempotent behavior

**Objective:** Implement `add-commit` subcommand with idempotent no-op when nothing staged.

**RED Phase:**
**Test:** `test_add_commit_nothing_staged`
**Assertions:**
- In clean repo, `claudeutils _worktree add-commit agents/session.md` with message from stdin exits 0
- Stdout is empty (no commit hash output because nothing was staged/committed)
**Expected failure:** `AttributeError` or command not found, or implementation fails with "nothing to commit" error
**Why it fails:** The `add-commit` subcommand doesn't exist yet, or no idempotent check.
**Verify RED:** `pytest tests/test_worktree_cli.py::test_add_commit_nothing_staged -v`

---

**GREEN Phase:**
**Implementation:** Add `add-commit` subcommand with idempotent staging check.
**Behavior:**
- Executes `git add <files>` for all provided file paths
- Checks if anything was staged using `git diff --quiet --cached`
- If nothing staged: exits 0 immediately with no output (idempotent no-op)
- If staged changes exist: reads commit message from stdin, commits, outputs commit hash to stdout
- Exits 0 on success, exits 1 on error
**Approach:** Use `@worktree.command(name="add-commit")` with variadic file arguments. Message from stdin enables multi-line messages (ceremony uses heredocs). Idempotent behavior critical for merge flow.
**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Add `add_commit()` function with `@worktree.command(name="add-commit")` decorator
  Location hint: After `clean_tree`, before end of file
**Verify GREEN:** `pytest tests/test_worktree_cli.py::test_add_commit_nothing_staged -v`
**Verify no regression:** `just test`

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/worktree-skill/reports/cycle-0-9-notes.md

### Phase 1: Worktree Lifecycle (new, rm)

**Complexity:** Medium
**Cycles:** 7
**Model:** sonnet (implementation)
**Checkpoint:** light
**Files:** `src/claudeutils/worktree/cli.py`, `tests/test_worktree_cli.py`

**Context:** This phase implements the worktree creation and removal operations. The `new` subcommand creates a worktree at `wt/<slug>/` with optional pre-committed focused session, initializes submodules, and branches them. The `rm` subcommand handles cleanup including branch-only scenarios. Key complexity: Cycle 1.5 (--session pre-commit) uses git plumbing with temp index to avoid polluting main index.

**Dependencies:** Phase 0 (CLI foundation, slug derivation)

---
