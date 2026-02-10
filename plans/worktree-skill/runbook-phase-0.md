### Phase 0: CLI Foundation

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
