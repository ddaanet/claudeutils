### Phase 0: CLI Foundation and Simple Subcommands

**Complexity:** Low-Medium
**Model:** sonnet (implementation)
**Checkpoint:** light
**Files:** `src/claudeutils/worktree/__init__.py`, `src/claudeutils/worktree/cli.py`, `tests/test_worktree_cli.py`

This phase establishes the package structure, Click command group, slug derivation utility, and three simple subcommands (ls, clean-tree, add-commit). These form the foundation for more complex operations.

---

## Cycle 0.1: Package Initialization

**Objective:** Establish package structure with empty module and enable import path.

**RED Phase:**
**Test:** `test_package_import`
**Assertions:**
- Importing `from claudeutils.worktree.cli import worktree` raises `ImportError` before package exists
- After package creation, the same import succeeds without error
**Expected failure:** `ImportError: No module named 'claudeutils.worktree'`
**Why it fails:** The `src/claudeutils/worktree/` directory and its module files don't exist yet.
**Verify RED:** `pytest tests/test_worktree_cli.py::test_package_import -v`

---

**GREEN Phase:**
**Implementation:** Create package directory structure with minimal initialization.
**Behavior:**
- Package directory exists at `src/claudeutils/worktree/`
- `__init__.py` is empty per minimal init convention
- `cli.py` exists as an empty module (no content yet)
- Import statement resolves successfully
**Approach:** Create directory structure, add empty files, verify import works.
**Changes:**
- File: `src/claudeutils/worktree/__init__.py`
  Action: Create empty file
  Location hint: New file in new directory
- File: `src/claudeutils/worktree/cli.py`
  Action: Create empty file
  Location hint: New file in same directory
**Verify GREEN:** `pytest tests/test_worktree_cli.py::test_package_import -v`
**Verify no regression:** `just test`

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/worktree-skill/reports/cycle-0-1-notes.md

---

## Cycle 0.2: Click Group Structure

**Objective:** Establish `_worktree` command group with help output.

**RED Phase:**
**Test:** `test_worktree_command_group`
**Assertions:**
- Running `claudeutils _worktree --help` via Click's CliRunner displays usage text
- Help output includes the command name `_worktree`
- Exit code is 0
**Expected failure:** `AttributeError` or import error (no `worktree` Click group exists)
**Why it fails:** The `cli.py` module has no Click command group definition.
**Verify RED:** `pytest tests/test_worktree_cli.py::test_worktree_command_group -v`

---

**GREEN Phase:**
**Implementation:** Define Click command group with basic structure.
**Behavior:**
- Click group named `worktree` responds to `--help`
- Help text displays command group information
- Returns exit code 0 for help invocation
**Approach:** Use Click's `@click.group()` decorator on a function named `worktree`. Add a docstring for help text.
**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Add Click group definition with decorator and docstring
  Location hint: Top level of module after imports
**Verify GREEN:** `pytest tests/test_worktree_cli.py::test_worktree_command_group -v`
**Verify no regression:** `just test`

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/worktree-skill/reports/cycle-0-2-notes.md

---

## Cycle 0.3: Slug Derivation Utility

**Objective:** Convert task names to worktree slugs with deterministic transformation.

**RED Phase:**
**Test:** `test_derive_slug`
**Assertions:**
- `derive_slug("Implement ambient awareness")` returns `"implement-ambient-awareness"`
- `derive_slug("Design runbook identifiers")` returns `"design-runbook-identifiers"`
- `derive_slug("Review agent-core orphaned revisions")` returns `"review-agent-core-orphaned-r"` (truncated at 30 chars)
- `derive_slug("Multiple    spaces   here")` returns `"multiple-spaces-here"` (collapsed)
- `derive_slug("Special!@#$%chars")` returns `"special-chars"` (removed)
**Expected failure:** `AttributeError` or `NameError` (function doesn't exist)
**Why it fails:** No `derive_slug` function is defined in `cli.py`.
**Verify RED:** `pytest tests/test_worktree_cli.py::test_derive_slug -v`

---

**GREEN Phase:**
**Implementation:** Pure function performing string transformation to slug format.
**Behavior:**
- Converts input to lowercase
- Replaces sequences of non-alphanumeric characters with single hyphens
- Strips leading and trailing hyphens
- Truncates to maximum 30 characters
- Strips trailing hyphens after truncation
**Approach:** Use regex substitution with `re.sub(r'[^a-z0-9]+', '-', ...)` pattern. Apply string slicing for truncation.
**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Add `derive_slug(task_name: str, max_length: int = 30) -> str` function
  Location hint: Module level, above Click group (utilities before commands)
**Verify GREEN:** `pytest tests/test_worktree_cli.py::test_derive_slug -v`
**Verify no regression:** `just test`

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/worktree-skill/reports/cycle-0-3-notes.md

---

## Cycle 0.4: ls subcommand structure

**Objective:** Implement `ls` subcommand that lists worktrees with empty output for no worktrees.

**RED Phase:**
**Test:** `test_ls_empty`
**Assertions:**
- Running `claudeutils _worktree ls` in repo with no worktrees exits with code 0
- Output is empty (no worktree lines printed)
**Expected failure:** `AttributeError` or command not found error
**Why it fails:** The `ls` subcommand doesn't exist in the Click group yet.
**Verify RED:** `pytest tests/test_worktree_cli.py::test_ls_empty -v`

---

**GREEN Phase:**
**Implementation:** Add `ls` subcommand with porcelain parsing.
**Behavior:**
- Executes `git worktree list --porcelain` to get structured output
- Parses porcelain format to extract worktree path and branch name
- For non-main worktrees: extracts slug from path, emits tab-delimited line
- Exits 0 unconditionally (empty output for no worktrees is valid)
**Approach:** Use `@worktree.command()` decorator. Parse porcelain format (worktree/branch line pairs). Main worktree (project root) excluded from output. Tab-delimited format enables machine parsing.
**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Add `ls()` function with `@worktree.command()` decorator
  Location hint: After `derive_slug`, before end of file
**Verify GREEN:** `pytest tests/test_worktree_cli.py::test_ls_empty -v`
**Verify no regression:** `just test`

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/worktree-skill/reports/cycle-0-4-notes.md

---

## Cycle 0.5: ls with multiple worktrees

**Objective:** Extend `ls` to parse and output multiple worktrees with slug extraction.

**RED Phase:**
**Test:** `test_ls_multiple_worktrees`
**Assertions:**
- With 2 worktrees (`wt/task-a/` on branch `task-a`, `wt/task-b/` on branch `task-b`), `_worktree ls` outputs exactly 2 lines
- First line matches pattern: `task-a\ttask-a\t<absolute-path>/wt/task-a`
- Second line matches pattern: `task-b\ttask-b\t<absolute-path>/wt/task-b`
- Exit code is 0
**Expected failure:** Current implementation doesn't loop over multiple worktrees or extract slugs correctly
**Why it fails:** Cycle 0.4 implementation may handle empty case only, or slug extraction logic not implemented.
**Verify RED:** `pytest tests/test_worktree_cli.py::test_ls_multiple_worktrees -v`

---

**GREEN Phase:**
**Implementation:** Extend parsing to handle multiple worktrees and extract slugs from paths.
**Behavior:**
- Loops over all `worktree` lines in porcelain output
- For each worktree path matching `wt/<slug>/`, extracts the slug component
- Pairs slug with corresponding branch name from `branch` line
- Emits one tab-delimited line per worktree (format: `<slug>\t<branch>\t<path>`)
**Approach:** Porcelain format groups entries as `worktree`, `HEAD`, `branch`, blank line. Split path on `/`, find `wt` component, take next component as slug. Absolute paths in output enable direct navigation.
**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Extend `ls()` to loop over worktree entries, extract slugs
  Location hint: Inside `ls()` function body
**Verify GREEN:** `pytest tests/test_worktree_cli.py::test_ls_multiple_worktrees -v`
**Verify no regression:** `just test`

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/worktree-skill/reports/cycle-0-5-notes.md

---

## Cycle 0.6: clean-tree with clean repo

**Objective:** Implement `clean-tree` subcommand that validates clean state silently.

**RED Phase:**
**Test:** `test_clean_tree_clean`
**Assertions:**
- Running `claudeutils _worktree clean-tree` in clean repo with submodule exits 0
- No output to stdout or stderr (silent success)
**Expected failure:** `AttributeError` or command not found error
**Why it fails:** The `clean-tree` subcommand doesn't exist in the Click group yet.
**Verify RED:** `pytest tests/test_worktree_cli.py::test_clean_tree_clean -v`

---

**GREEN Phase:**
**Implementation:** Add `clean-tree` subcommand checking parent and submodule status.
**Behavior:**
- Executes `git status --porcelain` for parent repo
- Executes `git -C agent-core status --porcelain` for submodule
- If both outputs are empty: exits 0 silently (clean state)
- If either has content: prints dirty files to stdout, exits 1
**Approach:** Use `@worktree.command(name="clean-tree")` decorator. Porcelain format: `XY filename` where X=index status, Y=worktree status. Empty output = clean state. Session file filtering added in next cycle.
**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Add `clean_tree()` function with `@worktree.command(name="clean-tree")` decorator
  Location hint: After `ls`, before end of file
**Verify GREEN:** `pytest tests/test_worktree_cli.py::test_clean_tree_clean -v`
**Verify no regression:** `just test`

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/worktree-skill/reports/cycle-0-6-notes.md

---

## Cycle 0.7: clean-tree with session files

**Objective:** Extend `clean-tree` to exempt session context files from dirty check.

**RED Phase:**
**Test:** `test_clean_tree_session_files_exempt`
**Assertions:**
- With modified `agents/session.md`, `agents/jobs.md`, `agents/learnings.md`, `_worktree clean-tree` exits 0
- No output to stdout (silent success, session files are exempt)
**Expected failure:** Current implementation treats session files as dirty, exits 1
**Why it fails:** Cycle 0.6 implementation doesn't filter session files, reports any modified file.
**Verify RED:** `pytest tests/test_worktree_cli.py::test_clean_tree_session_files_exempt -v`

---

**GREEN Phase:**
**Implementation:** Add filtering to exclude session context files from status output.
**Behavior:**
- After getting porcelain status for parent and submodule, filters output lines
- Removes lines where filename is `agents/session.md`, `agents/jobs.md`, or `agents/learnings.md`
- Applies same filter to both parent and submodule status
- Exits 0 if filtered output empty, exits 1 with remaining files otherwise
**Approach:** Use exact filename match (no wildcards). Porcelain format: `XY filename` where filename follows space. Session files exempt because they're auto-committed during merge ceremony.
**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Add filtering logic inside `clean_tree()` function
  Location hint: After status command execution, before exit decision
**Verify GREEN:** `pytest tests/test_worktree_cli.py::test_clean_tree_session_files_exempt -v`
**Verify no regression:** `just test`

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/worktree-skill/reports/cycle-0-7-notes.md

---

## Cycle 0.8: clean-tree with non-session dirt

**Objective:** Verify `clean-tree` detects and reports non-session dirty files.

**RED Phase:**
**Test:** `test_clean_tree_dirty_source`
**Assertions:**
- With modified `src/claudeutils/cli.py`, `_worktree clean-tree` exits 1
- Stdout contains porcelain format line: ` M src/claudeutils/cli.py`
**Expected failure:** Current implementation may not print remaining files after filtering
**Why it fails:** Cycle 0.7 may filter and exit, but not print remaining dirty files to stdout before exit 1.
**Verify RED:** `pytest tests/test_worktree_cli.py::test_clean_tree_dirty_source -v`

---

**GREEN Phase:**
**Implementation:** Add output of remaining dirty files after session file filtering.
**Behavior:**
- After filtering session files, checks if remaining porcelain lines exist
- If remaining lines exist: prints all to stdout (one line per file, porcelain format preserved)
- Exits 1 with dirty file list printed
- If no remaining lines: exits 0 silently (already implemented in 0.7)
**Approach:** Output format matches `git status --porcelain` for script parsing. User sees exactly which files block merge ceremony. Submodule files printed with `agent-core/` prefix.
**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Add print statement before exit 1 in `clean_tree()`
  Location hint: After filtering, before exit decision
**Verify GREEN:** `pytest tests/test_worktree_cli.py::test_clean_tree_dirty_source -v`
**Verify no regression:** `just test`

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/worktree-skill/reports/cycle-0-8-notes.md

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
