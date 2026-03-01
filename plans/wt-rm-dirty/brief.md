# Brief: _worktree rm dirty-state warning after merge

## Observed Behavior

`claudeutils _worktree merge runbook-recall-expansion` completed successfully (exit 0, "Precommit passed"). Immediately after, `claudeutils _worktree rm runbook-recall-expansion` emitted:

```
Warning: skipping session amend (parent repo dirty)
```

`git status --porcelain` after rm showed:

```
M  agents/session.md
 M plans/runbook-recall-expansion/lifecycle.md
```

- `session.md`: staged change (worktree task entry removed by rm)
- `lifecycle.md`: unstaged change ("delivered" line added by rm)

## Merge Commits

| Commit | Description | Parents |
|--------|-------------|---------|
| `5a0f6c91` | Merge agent-core from runbook-recall-expansion | (submodule merge) |
| `1d4a059c` | Merge runbook-recall-expansion | `5a0f6c91` + `e0c64ac7` |
| `3de87159` | Manual cleanup commit (session.md + lifecycle.md) | `1d4a059c` |

The `3de87159` commit was created manually in the session because the rm command skipped amend.

## Code Path (from exploration)

**Warning emitted at:** `src/claudeutils/worktree/cli.py`, `_update_session_and_amend()` ~line 310

```python
parent_status = _git("status", "--porcelain", check=False)
other_dirty = [
    line for line in parent_status.strip().split("\n")
    if line and not line.endswith("agents/session.md")
]
if other_dirty:
    click.echo("Warning: skipping session amend (parent repo dirty)")
    return False
```

The function:
1. Calls `remove_worktree_task()` on session.md (stages session.md change)
2. Checks `_is_merge_of(slug)` — confirms HEAD is merge commit of this slug
3. Runs `git status --porcelain` and filters out session.md
4. If ANY other dirty file exists → warning + bail

## Diagnostic Question

What made `lifecycle.md` dirty between merge completing (exit 0) and rm running? Two hypotheses:
- Merge phase 4 doesn't stage/commit lifecycle.md changes
- The rm command itself writes lifecycle.md before the dirty check (ordering bug — writes then checks)

The rm function calls `_update_session_and_amend()` which checks `_is_merge_of(slug)` before the dirty check. But lifecycle.md modification could happen elsewhere in the rm flow before `_update_session_and_amend` is called. Trace the rm() call sequence to find where lifecycle.md is written relative to the dirty check.
