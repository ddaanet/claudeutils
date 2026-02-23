---
name: worktree-error-output
model: haiku
---

# Worktree Error Output Migration

**Context:** `_worktree` is LLM-native (underscore prefix) but uses stderr for errors. Bash tool error
envelope duplicates stderr on non-zero exit — every error appears twice. `derive_slug` raises
unhandled `ValueError` producing a raw traceback.

**Design:** `plans/worktree-error-output/outline.md`
**Status:** Ready
**Created:** 2026-02-23

---

## Weak Orchestrator Metadata

**Total Steps:** 5 (Cycles 1.1, 2.1; Steps 3.1, 3.2, 3.3)

**Execution Model:**
- Cycles 1.1, 2.1: Haiku (new function + new error path — standard implementation)
- Steps 3.1, 3.2: Haiku (mechanical substitution in single file)
- Step 3.3: Haiku (precommit validation)

**Step Dependencies:** Sequential — 1.1 → 2.1 → 3.1 → 3.2 → 3.3

**Error Escalation:**
- Haiku → Sonnet: RED phase doesn't fail; GREEN breaks unrelated tests; mechanical
  substitution produces syntax error
- Sonnet → User: Design question or regression requiring architectural decision

**Report Locations:** `plans/worktree-error-output/reports/`

**Success Criteria:** All tests pass, `just precommit` clean, no `err=True` remaining in
`src/claudeutils/worktree/cli.py`, `_fail()` defined in cli.py, invalid task names produce
clean one-line error (exit 2) not a traceback.

**Prerequisites:**
- `src/claudeutils/worktree/cli.py` exists (✓ verified)
- `tests/test_worktree_utils.py` exists (✓ verified, 229 lines)
- `tests/test_worktree_new_creation.py` exists (✓ verified, 323 lines)

---

## Common Context

**Requirements:**
- All `_worktree` error output goes to stdout (LLM-native convention — cli.md "When CLI
  Commands Are LLM-Native")
- `_fail(msg, code=1) -> Never` consolidates echo+exit pairs (cli.md "When Writing Error
  Exit Code")
- `derive_slug` ValueError caught in `new()`, produces clean one-line message, exits code 2
- 4 warning-only sites: drop `err=True`, keep as plain `click.echo()` (no exit)

**Scope:**
- IN: `src/claudeutils/worktree/cli.py` — all `err=True` sites, `_fail()` helper, ValueError catch
- OUT: `merge.py`, `merge_state.py`, `resolve.py` (already stdout); user-facing commands

**Project Paths:**
- Target: `src/claudeutils/worktree/cli.py`
- Tests (Phase 1): `tests/test_worktree_utils.py` — add `_fail()` tests at end of file
- Tests (Phase 2): `tests/test_worktree_new_creation.py` — add ValueError test at end of file

**Key implementation facts:**
- Python 3.14 — use `from typing import Never` directly
- `_fail()` is module-level private function in `cli.py`, called from module-level helpers
- Error sites: `click.echo(msg, err=True)` + `raise SystemExit(N)` pattern
- Warning sites: `click.echo(msg, err=True)` with NO following `SystemExit` (same function continues)
- `derive_slug` is called at line 183: `slug = branch or derive_slug(task_name)` inside `new()`

**Verification grep:**
```
grep -n "err=True" src/claudeutils/worktree/cli.py
```

**Stop/Error Conditions (all cycles):**
- RED phase doesn't fail (test passes before implementation) → STOP, the test is vacuous or tests existing behavior — diagnose before implementing
- GREEN breaks unrelated tests → STOP, escalate to sonnet — implementation has side effects
- Syntax error after any edit → STOP, do not commit broken state, escalate to sonnet
- Unexpected exception type raised (not SystemExit) → STOP, implementation incorrect

**Dependencies:** Sequential — Cycle 1.1 → Cycle 2.1 → Step 3.1 → Step 3.2 → Step 3.3. Cycle 2.1 depends on `_fail()` from Cycle 1.1.

---

### Phase 1: `_fail()` helper (type: tdd)

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

## Step 3.1: Convert error+exit sites to `_fail()`

**Objective:** Replace all `click.echo(msg, err=True)` + `raise SystemExit(N)` pairs with
`_fail(msg, N)` in `cli.py`.

**Script Evaluation:** Prose — mechanical substitution requiring careful multi-line matching

**Execution Model:** Haiku

**Prerequisite:** Read `src/claudeutils/worktree/cli.py` in full — identify every
`err=True` + `SystemExit` pair before editing.

**Implementation:**

Grep first to confirm all sites:
```
grep -n "err=True\|SystemExit" src/claudeutils/worktree/cli.py
```

For each error+exit pair (all in `src/claudeutils/worktree/cli.py`):

| Location | Current pattern | Replace with |
|---|---|---|
| `new()` ~L191 | `click.echo(f"Error: existing directory {path}", err=True)` + `raise SystemExit(1)` | `_fail(f"Error: existing directory {path}")` |
| `new()` ~L196 | `click.echo(f"Error: session.md not found at {session_md}", err=True)` + `raise SystemExit(1)` | `_fail(f"Error: session.md not found at {session_md}")` |
| `_guard_branch_removal()` ~L250 | `click.echo(msg, err=True)` + `raise SystemExit(2)` | `_fail(msg, 2)` |
| `_delete_branch()` ~L260 | `click.echo(f"Branch {slug} deletion failed: {r.stderr.strip()}", err=True)` + `raise SystemExit(1)` | `_fail(f"Branch {slug} deletion failed: {r.stderr.strip()}")` |
| `_check_confirm()` ~L267 | multi-line `click.echo(...)` + `raise SystemExit(2)` | `_fail(msg, 2)` — extract string to local var `msg` if multi-line |
| `_check_not_dirty()` ~L280 | multi-line `click.echo(...)` + `raise SystemExit(2)` | `_fail(msg, 2)` |
| `_check_not_dirty()` ~L287 | multi-line `click.echo(...)` + `raise SystemExit(2)` | `_fail(msg, 2)` |

**Note on multi-line echoes:** For the 3 sites with multi-line string arguments to
`click.echo()`, extract the string to a local variable `msg = (...)` before calling `_fail(msg, 2)`.

**Expected Outcome:** All error+exit `err=True` removed. `_fail()` calls in their place.

**Error Conditions:** Syntax error after edit → STOP, escalate to sonnet

**Validation:**
```
grep -n "err=True" src/claudeutils/worktree/cli.py
just test
```
Grep should return only warning-only sites (4 remaining). Tests must pass.

---

## Step 3.2: Drop `err=True` from warning-only sites

**Objective:** Remove `err=True` from the 4 warning sites that do NOT exit — make them plain stdout.

**Script Evaluation:** Direct — simple `err=True` removal from 4 lines

**Execution Model:** Haiku

**Implementation:**

Warning sites in `src/claudeutils/worktree/cli.py` (no `SystemExit` follows):

| Location | Current | Replace with |
|---|---|---|
| `_initialize_environment()` ~L77 | `click.echo(f"Warning: just setup failed: {r.stderr}", err=True)` | `click.echo(f"Warning: just setup failed: {r.stderr}")` |
| `_create_parent_worktree()` ~L110 | `click.echo(f"Warning: branch {slug} exists, ignoring --session", err=True)` | `click.echo(f"Warning: branch {slug} exists, ignoring --session")` |
| `_update_session_and_amend()` ~L309 | `click.echo("Warning: skipping session amend (parent repo dirty)", err=True)` | `click.echo("Warning: skipping session amend (parent repo dirty)")` |
| `rm()` ~L363 | `click.echo(warning, err=True)` | `click.echo(warning)` |

**Expected Outcome:** No `err=True` remaining anywhere in `cli.py`.

**Error Conditions:** None expected — trivial `err=True` removal.

**Validation:**
```
grep "err=True" src/claudeutils/worktree/cli.py
just test
```
Grep must return empty. Tests must pass.

---

## Step 3.3: Precommit validation

**Objective:** Verify full quality gate passes before handoff.

**Script Evaluation:** Direct

**Execution Model:** Haiku

**Implementation:**
```
just precommit
```

If failures:
- Lint/type errors from the new `Never` import or `_fail()` signature → fix in cli.py
- Test failures from the `err=True` changes → check if existing tests assert on `result.output`
  (output captured by CliRunner) vs stderr. Tests asserting `result.output` already pass;
  if any test captured stderr directly (unlikely), update the assertion.

**Expected Outcome:** All checks pass, clean tree ready for commit.

**Error Conditions:** Escalate to sonnet if unexpected failures.

**Validation:** `just precommit` exits 0
