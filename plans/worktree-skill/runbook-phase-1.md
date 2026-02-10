### Phase 1: Simple Subcommands (ls, clean-tree, add-commit)

**Complexity:** Low-Medium
**Model:** sonnet (implementation)
**Checkpoint:** light
**Files:** `src/claudeutils/worktree/cli.py`, `tests/test_worktree_cli.py`

This phase implements three simple subcommands that form the foundation for more complex operations: `ls` for listing worktrees, `clean-tree` for validating repository state, and `add-commit` for atomic stage-and-commit operations. These subcommands are independent and follow similar patterns (git porcelain parsing, filtering logic, idempotent behavior).

---

## Cycle 1.1: ls subcommand structure

**RED Phase:**

Create test `test_ls_empty` in `tests/test_worktree_cli.py`:
- Arrange: Git repo with no worktrees (only main worktree)
- Act: Run `claudeutils _worktree ls`
- Assert:
  - Exit code is 0
  - Output is empty (no worktree lines printed)

Expected failure: `_worktree ls` command doesn't exist yet.

**GREEN Phase:**

Implement `ls` subcommand in `src/claudeutils/worktree/cli.py`:
- Add `@worktree.command()` decorated function for `ls`
- Execute `git worktree list --porcelain` via subprocess
- Parse porcelain output: extract worktree path, branch name
- For each non-main worktree: extract slug from path, emit `<slug>\t<branch>\t<path>` to stdout
- Exit 0 unconditionally

Behavior notes:
- Porcelain format has `worktree <path>` and `branch refs/heads/<name>` lines
- Main worktree (project root) is excluded from output
- Tab-delimited format enables machine parsing by skill

---

## Cycle 1.2: ls with multiple worktrees

**RED Phase:**

Create test `test_ls_multiple_worktrees` in `tests/test_worktree_cli.py`:
- Arrange: Git repo with 2 worktrees created (e.g., `wt/task-a/` on branch `task-a`, `wt/task-b/` on branch `task-b`)
- Act: Run `claudeutils _worktree ls`
- Assert:
  - Exit code is 0
  - Output has exactly 2 lines
  - First line: `task-a\ttask-a\t<absolute-path>/wt/task-a`
  - Second line: `task-b\ttask-b\t<absolute-path>/wt/task-b`

Expected failure: current implementation doesn't correctly parse multiple worktrees or extract slugs from paths.

**GREEN Phase:**

Extend `ls` implementation:
- Parse all worktree entries from porcelain output (loop over `worktree` lines)
- For each worktree path: check if it matches pattern `wt/<slug>/`, extract slug
- Pair slug with branch name extracted from corresponding `branch` line
- Emit one line per worktree (main worktree still excluded)

Behavior notes:
- Porcelain format groups: `worktree`, `HEAD`, `branch`, blank line separator
- Slug extraction: split path on `/`, find `wt` component, take next component
- Absolute paths in output enable direct navigation

---

## Cycle 1.3: clean-tree with clean repo

**RED Phase:**

Create test `test_clean_tree_clean` in `tests/test_worktree_cli.py`:
- Arrange: Git repo with submodule, no uncommitted changes, no untracked files
- Act: Run `claudeutils _worktree clean-tree`
- Assert:
  - Exit code is 0
  - No output to stdout or stderr (silent success)

Expected failure: `_worktree clean-tree` command doesn't exist yet.

**GREEN Phase:**

Implement `clean-tree` subcommand in `src/claudeutils/worktree/cli.py`:
- Add `@worktree.command(name="clean-tree")` decorated function
- Execute `git status --porcelain` for parent repo
- Execute `git -C agent-core status --porcelain` for submodule
- If both outputs are empty: exit 0 silently
- If either has content: print dirty files to stdout, exit 1

Behavior notes:
- Porcelain format: `XY filename` where X=index status, Y=worktree status
- Empty output means clean state (no staged, unstaged, or untracked changes)
- Session file filtering added in next cycle

---

## Cycle 1.4: clean-tree with session files

**RED Phase:**

Create test `test_clean_tree_session_files_exempt` in `tests/test_worktree_cli.py`:
- Arrange: Git repo with modified `agents/session.md`, `agents/jobs.md`, `agents/learnings.md` (all dirty)
- Act: Run `claudeutils _worktree clean-tree`
- Assert:
  - Exit code is 0 (session files are exempt from dirty check)
  - No output (silent success)

Expected failure: current implementation treats session files as dirty, exits 1.

**GREEN Phase:**

Extend `clean-tree` implementation:
- After running `git status --porcelain` for parent and submodule, filter output lines
- Filtering logic: remove lines where filename is `agents/session.md`, `agents/jobs.md`, or `agents/learnings.md`
- Apply same filter to both parent and submodule status outputs
- Exit 0 if filtered output is empty, exit 1 with remaining files otherwise

Behavior notes:
- Porcelain line format: status codes followed by space, then filename
- Exact match on filenames (no partial matches or wildcards)
- Session files are auto-committed during merge ceremony, exempting them here

---

## Cycle 1.5: clean-tree with non-session dirt

**RED Phase:**

Create test `test_clean_tree_dirty_source` in `tests/test_worktree_cli.py`:
- Arrange: Git repo with modified `src/claudeutils/cli.py` (dirty source file)
- Act: Run `claudeutils _worktree clean-tree`
- Assert:
  - Exit code is 1 (dirty tree detected)
  - Stdout contains ` M src/claudeutils/cli.py` (porcelain format line)

Expected failure: current implementation may exit 0 if session files dominate test setup, or may not print remaining files.

**GREEN Phase:**

Verify `clean-tree` behavior:
- After filtering session files, check if remaining porcelain lines exist
- If yes: print all remaining lines to stdout (one line per dirty file, porcelain format preserved)
- Exit 1 with dirty file list
- If no remaining lines: exit 0 silently (already implemented in cycle 1.4)

Behavior notes:
- Output format matches `git status --porcelain` (enables script parsing)
- User sees exactly which files block merge ceremony
- Submodule dirty files also printed with `agent-core/` prefix

---

## Cycle 1.6: add-commit idempotent behavior

**RED Phase:**

Create test `test_add_commit_nothing_staged` in `tests/test_worktree_cli.py`:
- Arrange: Git repo with all changes already committed (clean state)
- Act: Run `claudeutils _worktree add-commit agents/session.md` with message "Update session" piped to stdin
- Assert:
  - Exit code is 0 (idempotent, no error)
  - Stdout is empty (no commit hash, because nothing was committed)

Expected failure: `_worktree add-commit` command doesn't exist yet, or implementation fails when nothing is staged.

**GREEN Phase:**

Implement `add-commit` subcommand in `src/claudeutils/worktree/cli.py`:
- Add `@worktree.command(name="add-commit")` with variadic file arguments
- Execute `git add <files>` for all provided file paths
- Check if anything was staged: `git diff --quiet --cached`
- If nothing staged (exit 0 from diff): exit 0 immediately with no output (idempotent no-op)
- If staged changes exist: read commit message from stdin, execute `git commit -m <message>`, output commit hash to stdout
- Exit 0 on success, exit 1 on error

Behavior notes:
- Message from stdin enables multi-line messages (ceremony uses heredocs)
- Idempotent behavior critical for merge flow (submodule may already be committed)
- Commit hash output enables verification in orchestration
