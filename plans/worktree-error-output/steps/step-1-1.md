# Cycle 1.1

**Plan**: `plans/worktree-error-output/runbook.md`
**Execution Model**: haiku
**Phase**: 1

---

## Cycle 1.1: Implement `_fail()` helper

**RED Phase:**

**Test file:** `tests/test_worktree_utils.py` — append at end of file

**Test:** `test_fail_writes_to_stdout`
**Imports needed:** `import pytest` (already present), `from claudeutils.worktree.cli import _fail`

**Assertions:**
- `_fail("error message", 1)` raises `SystemExit` with `.code == 1`
- The message `"error message"` appears in captured stdout (capsys)
- captured stderr is empty string `""`

**Test:** `test_fail_default_code`
**Assertions:**
- `_fail("msg")` (no code arg) raises `SystemExit` with `.code == 1`

**Test:** `test_fail_custom_code`
**Assertions:**
- `_fail("validation error", 2)` raises `SystemExit` with `.code == 2`

**Expected failure:** `ImportError: cannot import name '_fail' from 'claudeutils.worktree.cli'`

**Why it fails:** `_fail` doesn't exist yet in cli.py

**Verify RED:**
```
pytest tests/test_worktree_utils.py::test_fail_writes_to_stdout tests/test_worktree_utils.py::test_fail_default_code tests/test_worktree_utils.py::test_fail_custom_code -v
```

---

**GREEN Phase:**

**Implementation:** Add `_fail()` helper to `cli.py` — module-level private function after imports

**Behavior:**
- Prints `msg` to stdout (not stderr) via `click.echo(msg)` — no `err=True`
- Raises `SystemExit(code)`
- Return type `Never` — control flow terminates unconditionally

**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Add `from typing import Never` to the imports block (after existing stdlib imports)
  Location hint: After `from pathlib import Path` line

- File: `src/claudeutils/worktree/cli.py`
  Action: Add `_fail()` function definition after the imports block, before `derive_slug`
  Location hint: After the `from claudeutils.worktree.session import ...` import block, before `def derive_slug`

**Verify GREEN:**
```
pytest tests/test_worktree_utils.py::test_fail_writes_to_stdout tests/test_worktree_utils.py::test_fail_default_code tests/test_worktree_utils.py::test_fail_custom_code -v
```
**Verify no regression:**
```
just test
```

---

### Phase 2: ValueError catch in `new()` (type: tdd)
