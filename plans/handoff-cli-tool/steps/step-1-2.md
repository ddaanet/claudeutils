# Step 1.2

**Plan**: `plans/handoff-cli-tool/runbook.md`
**Execution Model**: sonnet
**Phase**: 1

---

## Phase Context

Extract git utilities and establish package structure. Foundation for all subcommands.

---

---

## Step 1.2: Create `claudeutils/session/` package structure

**Objective:** Create package skeleton for all three subcommands. Register `_session` group in main CLI.

**Script Evaluation:** Small (~30 lines, mostly `__init__.py` stubs)

**Execution Model:** Sonnet

**Prerequisite:** Read `src/claudeutils/cli.py:145-152` — understand existing `cli.add_command(worktree)` registration pattern to replicate for `_session` group.

**Implementation:**

Create directory structure:
```
src/claudeutils/session/
  __init__.py           (empty)
  cli.py                Click group: `_session`
  handoff/
    __init__.py          (empty)
  commit/
    __init__.py          (empty)
  status/
    __init__.py          (empty)
```

`session/cli.py`:
- Define `@click.group(name="_session", hidden=True)` group
- Add help text: "Session management (internal)"

Main `cli.py` registration:
- `from claudeutils.session.cli import session_group`
- `cli.add_command(session_group)` — same pattern as line 152 (`cli.add_command(worktree)`)

**Expected Outcome:** `claudeutils _session --help` shows group with no subcommands. `claudeutils --help` does NOT show `_session` (hidden).

**Error Conditions:**
- Missing `__init__.py` → import failures

**Validation:** `claudeutils _session --help` succeeds; `just precommit` passes.

---
