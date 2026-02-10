### Phase 2: Worktree Lifecycle (new, rm)

**Complexity:** Medium
**Cycles:** 7
**Model:** sonnet (implementation)
**Checkpoint:** light
**Files:** `src/claudeutils/worktree/cli.py`, `tests/test_worktree_cli.py`

**Context:** This phase implements the worktree creation and removal operations. The `new` subcommand creates a worktree at `wt/<slug>/` with optional pre-committed focused session, initializes submodules, and branches them. The `rm` subcommand handles cleanup including branch-only scenarios. Key complexity: Cycle 2.5 (--session pre-commit) uses git plumbing with temp index to avoid polluting main index.

**Dependencies:** Phase 0 (CLI foundation, slug derivation)

---

## Cycle 2.1: new subcommand basic flow

**RED: Test behavior before implementation**

Create test `test_worktree_cli.py::test_new_basic_flow`:
- Given: Clean git repo with `.gitignore` containing `wt/` entry
- When: Run `_worktree new test-feature`
- Then: Directory `wt/test-feature/` exists
- Then: Branch `test-feature` exists (not `wt/test-feature`)
- Then: Worktree is checked out to branch `test-feature`
- Then: Command exits 0, stdout contains `wt/test-feature`

**Expected failure:** `_worktree new` subcommand does not exist (Click command not defined).

**GREEN: Implement minimal behavior**

Add `new` subcommand to `cli.py`:
- Click command decorator with `@worktree.command()`
- Parameter: `slug` (string, required)
- Optional: `--base` (default `HEAD`), `--session` (path, optional)
- Behavior: Run `git worktree add wt/{slug} -b {slug} {base}`
- Output: Print `wt/{slug}` to stdout
- Error handling: stderr + exit 1 on git failure

Skip submodule init and environment setup for this cycle (added in subsequent cycles).

---

## Cycle 2.2: new with collision detection

**RED: Test behavior before implementation**

Create test `test_worktree_cli.py::test_new_collision_detection`:
- Given: Existing branch `test-feature` created via `git branch test-feature HEAD`
- When: Run `_worktree new test-feature`
- Then: Exit 1
- Then: stderr contains error message about existing branch
- Then: No `wt/test-feature/` directory created

Create test `test_worktree_cli.py::test_new_directory_collision`:
- Given: Existing directory `wt/test-feature/` (untracked, created via `mkdir -p`)
- When: Run `_worktree new test-feature`
- Then: Exit 1
- Then: stderr contains error message about existing directory
- Then: No new branch created

**Expected failure:** Command proceeds despite collisions, creates worktree or fails with git error (not clean validation message).

**GREEN: Implement minimal behavior**

Add validation to `new` subcommand before `git worktree add`:
- Check: `wt/{slug}/` directory does not exist (use `Path().exists()`)
- Check: Branch `{slug}` does not exist (run `git rev-parse --verify {slug}`, expect exit code != 0)
- On collision: Print descriptive error to stderr, exit 1 before attempting worktree creation

---

## Cycle 2.3: new with submodule initialization

**RED: Test behavior before implementation**

Create test `test_worktree_cli.py::test_new_submodule_init`:
- Given: Repo with submodule `agent-core` initialized in main worktree
- When: Run `_worktree new test-feature`
- Then: Submodule `wt/test-feature/agent-core/` exists and is initialized
- Then: Submodule is at same commit as parent repo's submodule pointer
- Then: Submodule uses local objects from `<project-root>/agent-core` (verify via `.git/objects/info/alternates`)

**Expected failure:** Submodule directory is empty or uninitialized in new worktree.

**GREEN: Implement minimal behavior**

After `git worktree add`, run submodule initialization:
- Get project root: `git rev-parse --show-toplevel`
- Run: `git -C wt/{slug} submodule update --init --reference {project_root}/agent-core`
- `--reference` flag uses local objects as alternates (avoids fetching from remote)
- Error handling: stderr + exit 1 on submodule init failure

---

## Cycle 2.4: new with submodule branching

**RED: Test behavior before implementation**

Create test `test_worktree_cli.py::test_new_submodule_branching`:
- Given: Repo with submodule initialized
- When: Run `_worktree new test-feature`
- Then: Submodule in `wt/test-feature/agent-core/` is on branch `test-feature` (not detached HEAD)
- Then: Branch is new (not existing branch)
- Then: Branch starts at submodule's current commit

**Expected failure:** Submodule remains in detached HEAD state after initialization.

**GREEN: Implement minimal behavior**

After submodule initialization, create and checkout branch in submodule:
- Run: `git -C wt/{slug}/agent-core checkout -b {slug}`
- This creates new branch at current HEAD (the commit from submodule pointer)
- Error handling: stderr + exit 1 on branch creation failure

---

## Cycle 2.5: new with --session pre-commit

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

Add `--session` path handling with git plumbing sequence:
- Create temp index file: `tempfile.NamedTemporaryFile(delete=False, suffix='.index')`
- Hash session file: `git hash-object -w {session_path}` → blob SHA
- Populate temp index from base: `GIT_INDEX_FILE={tmpfile} git read-tree {base}`
- Update temp index: `GIT_INDEX_FILE={tmpfile} git update-index --cacheinfo 100644,{blob},agents/session.md`
- Write tree from temp index: `GIT_INDEX_FILE={tmpfile} git write-tree` → tree SHA
- Create commit: `git commit-tree {tree} -p {base} -m "Focused session for {slug}"` → commit SHA
- Create branch: `git branch {slug} {commit}`
- Create worktree: `git worktree add wt/{slug} {slug}`
- Clean up: Remove temp index file

Environment variable pattern: `subprocess.run(..., env={**os.environ, 'GIT_INDEX_FILE': tmpfile})`

If `--session` not provided, use existing `git worktree add -b` flow from Cycle 2.1.

---

## Cycle 2.6: rm subcommand with worktree removal

**RED: Test behavior before implementation**

Create test `test_worktree_cli.py::test_rm_basic`:
- Given: Worktree created via `_worktree new test-feature`
- When: Run `_worktree rm test-feature`
- Then: Directory `wt/test-feature/` does not exist
- Then: Branch `test-feature` does not exist
- Then: Exit 0
- Then: Success message to stderr

Create test `test_worktree_cli.py::test_rm_dirty_warning`:
- Given: Worktree with uncommitted changes (create file in `wt/test-feature/`)
- When: Run `_worktree rm test-feature`
- Then: Warning to stderr about uncommitted changes
- Then: Worktree and branch still removed (forced)
- Then: Exit 0

**Expected failure:** `_worktree rm` subcommand does not exist.

**GREEN: Implement minimal behavior**

Add `rm` subcommand to `cli.py`:
- Click command decorator with `@worktree.command()`
- Parameter: `slug` (string, required)
- Check if worktree exists: `Path(f'wt/{slug}').exists()`
- If exists:
  - Check for dirty state: `git -C wt/{slug} diff --quiet HEAD` (exit code != 0 means dirty)
  - If dirty: Print warning to stderr (`"Warning: wt/{slug} has uncommitted changes"`)
  - Remove worktree: `git worktree remove --force wt/{slug}`
- Remove branch: `git branch -d {slug}`
  - If unmerged (exit code != 0): Print warning to stderr but don't fail (user choice)
- Print success message to stderr
- Exit 0

---

## Cycle 2.7: rm with branch-only cleanup

**RED: Test behavior before implementation**

Create test `test_worktree_cli.py::test_rm_branch_only`:
- Given: Worktree created via `_worktree new test-feature`, then worktree manually removed via `rm -rf wt/test-feature` (simulating external cleanup)
- Given: Branch `test-feature` still exists (verify with `git branch --list`)
- When: Run `_worktree rm test-feature`
- Then: Exit 0
- Then: Branch `test-feature` removed
- Then: No error about missing worktree directory

**Expected failure:** Command exits 1 when worktree directory missing (fails to handle branch-only scenario).

**GREEN: Implement minimal behavior**

Update `rm` subcommand to handle missing worktree:
- Check if `wt/{slug}/` exists before attempting worktree removal
- If directory does not exist: Skip `git worktree remove` step (no error)
- Always attempt `git branch -d {slug}` (branch cleanup works regardless of worktree state)
- Success message reflects what was cleaned (e.g., "Branch {slug} removed" if worktree already gone)

This makes `rm` idempotent and handles partial cleanup states.
