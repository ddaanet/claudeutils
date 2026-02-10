### Phase 1: Worktree Lifecycle (new, rm)

**Complexity:** Medium
**Cycles:** 7
**Model:** sonnet (implementation)
**Checkpoint:** light
**Files:** `src/claudeutils/worktree/cli.py`, `tests/test_worktree_cli.py`

**Context:** This phase implements the worktree creation and removal operations. The `new` subcommand creates a worktree at `wt/<slug>/` with optional pre-committed focused session, initializes submodules, and branches them. The `rm` subcommand handles cleanup including branch-only scenarios. Key complexity: Cycle 1.5 (--session pre-commit) uses git plumbing with temp index to avoid polluting main index.

**Dependencies:** Phase 0 (CLI foundation, slug derivation)

---

## Cycle 1.1: new subcommand basic flow

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

Create `new` subcommand in `cli.py` that creates a worktree with branch.

**Behavior:**
- Accept slug as required argument, optional `--base` and `--session` flags
- Create worktree at `wt/{slug}/` on new branch `{slug}` from base commit
- Print worktree path to stdout on success
- Report errors to stderr and exit 1 on failure

**Hints:**
- Use Click's `@worktree.command()` decorator pattern
- Git command: `git worktree add wt/{slug} -b {slug} {base}`
- Skip submodule init for this cycle (added in 1.3-1.4)

---

## Cycle 1.2: new with collision detection

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

Add collision detection to `new` subcommand before creating worktree.

**Behavior:**
- Validate no existing `wt/{slug}/` directory
- Validate no existing `{slug}` branch
- Report specific error (directory or branch collision) to stderr and exit 1 if collision found
- Only proceed to worktree creation if both checks pass

**Hints:**
- Check directory: `Path('wt/{slug}').exists()`
- Check branch: `git rev-parse --verify {slug}` (exit code != 0 means branch doesn't exist)

---

## Cycle 1.3: new with submodule initialization

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

## Cycle 1.4: new with submodule branching

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

## Cycle 1.6: rm subcommand with worktree removal

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

Create `rm` subcommand that removes worktree and branch with safety warnings.

**Behavior:**
- Remove worktree directory (if exists) with force flag
- Remove branch (always attempt, even if worktree already gone)
- Warn to stderr if worktree has uncommitted changes (but proceed with removal)
- Warn to stderr if branch is unmerged (but don't fail command)
- Report success to stderr, exit 0

**Approach:**
- Check worktree existence before attempting removal
- Use `--force` for worktree removal (handles submodule and uncommitted changes)
- Use `-d` (not `-D`) for branch removal (preserves unmerged branch warning)
- Detect dirty state before removal for warning message

**Hints:**
- Worktree check: `Path(f'wt/{slug}').exists()`
- Dirty check: `git -C wt/{slug} diff --quiet HEAD` (exit code indicates state)
- Worktree removal: `git worktree remove --force wt/{slug}`
- Branch removal: `git branch -d {slug}` (warns but doesn't block on unmerged)

---

## Cycle 1.7: rm with branch-only cleanup

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

Make `rm` subcommand handle branch-only cleanup (worktree already removed externally).

**Behavior:**
- Skip worktree removal step if directory doesn't exist (no error)
- Always attempt branch removal (works whether worktree exists or not)
- Success message reflects actual cleanup performed
- Exit 0 in all cases (idempotent)

**Approach:**
- Check directory existence before worktree removal
- Branch removal is independent of worktree state
- Adjust output message based on what was actually cleaned

**Why:** Makes `rm` idempotent and resilient to partial cleanup states (e.g., user manually deleted worktree directory but branch remains).
