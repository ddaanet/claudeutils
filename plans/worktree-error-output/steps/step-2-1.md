# Cycle 2.1

**Plan**: `plans/worktree-error-output/runbook.md`
**Execution Model**: haiku
**Phase**: 2

---

## Cycle 2.1: Catch `derive_slug` ValueError in `new()`

**Depends on:** Cycle 1.1 (requires `_fail()`)

**RED Phase:**

**Test file:** `tests/test_worktree_new_creation.py` — append at end of file

**Test:** `test_new_invalid_task_name_clean_error`
**Setup:** init_repo fixture (copy pattern from existing tests: `repo_path = tmp_path / "repo"`, `repo_path.mkdir()`, `monkeypatch.chdir(repo_path)`, `init_repo(repo_path)`)
**Invocation:** `CliRunner().invoke(worktree, ["new", "task_with_underscore"])`

**Assertions:**
- `result.exit_code == 2`
- `"forbidden character '_'" in result.output` (the validate_task_name_format error message)
- `"Traceback" not in result.output` (no raw Python traceback)
- `"ValueError" not in result.output` (no raw exception type)

**Expected failure:** Currently `derive_slug("task_with_underscore")` raises unhandled
`ValueError("forbidden character '_' in task name ...")`. CliRunner catches it and sets
exit_code=1 with the full traceback in output.

**Why it fails:** No try/except around `derive_slug(task_name)` in `new()`

**Verify RED:**
```
pytest tests/test_worktree_new_creation.py::test_new_invalid_task_name_clean_error -v
```

---

**GREEN Phase:**

**Implementation:** Wrap `derive_slug(task_name)` call in try/except ValueError in `new()`

**Behavior:**
- `ValueError` from `derive_slug` caught before it propagates
- Error message from the exception displayed via `_fail(str(e), code=2)`
- Exit code 2 (validation failure, matching outline Key Decision 2)
- Clean output: one line, no traceback

**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: In `new()` function, wrap `slug = branch or derive_slug(task_name)` (line ~183)
    in try/except ValueError that calls `_fail(str(e), code=2)`
  Location hint: `if task_name:` block, currently `slug = branch or derive_slug(task_name)`

**Verify GREEN:**
```
pytest tests/test_worktree_new_creation.py::test_new_invalid_task_name_clean_error -v
```
**Verify no regression:**
```
just test
```

---

### Phase 3: Drop `err=True` from all sites (type: general)
