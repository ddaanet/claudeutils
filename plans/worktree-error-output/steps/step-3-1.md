# Step 3.1

**Plan**: `plans/worktree-error-output/runbook.md`
**Execution Model**: haiku
**Phase**: 3

---

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
