# Step 1.3

**Plan**: `plans/handoff-cli-tool/runbook.md`
**Execution Model**: sonnet
**Phase**: 1

---

## Phase Context

Extract git utilities and establish package structure. Foundation for all subcommands.

---

---

## Step 1.3: Add `claudeutils _git status` and `claudeutils _git diff` subcommands

**Objective:** Unified parent + submodule git status/diff view as structured markdown. Consumers: commit skill, commit CLI validation, handoff diagnostics.

**Script Evaluation:** Medium (~80 lines new code + tests)

**Execution Model:** Sonnet

**Prerequisite:** Read `src/claudeutils/git.py` (Step 1.1 output) — uses `_git()` and `discover_submodules()`

**Implementation:**

Create `src/claudeutils/git_cli.py` (CLI commands for the `_git` group):
- `@click.group(name="_git", hidden=True)` group
- `@git_group.command(name="status")` — runs `git status --porcelain` for parent, then for each discovered submodule. Output format:

```markdown
## Parent
<git status --porcelain output or "(clean)">

## Submodule: agent-core
<git -C agent-core status --porcelain output or "(clean)">
```

- `@git_group.command(name="diff")` — same pattern with `git diff` (staged + unstaged). Output format:

```markdown
## Parent
<git diff output or "(no changes)">

## Submodule: agent-core
<git -C agent-core diff output or "(no changes)">
```

Register in main `cli.py`: `from claudeutils.git_cli import git_group` + `cli.add_command(git_group)`

**Tests:** `tests/test_git_cli.py`
- Tests use `tmp_path` to create real git repos with submodules
- `test_git_status_clean_repo`: CliRunner invokes `_git status`, output contains `## Parent` and `(clean)`
- `test_git_status_dirty_repo`: Create dirty file, output contains filename in parent section
- `test_git_status_with_submodule`: Create repo with submodule, output contains `## Submodule:` section
- `test_git_diff_with_changes`: Stage a change, verify diff output appears under correct section

**Expected Outcome:** `claudeutils _git status` and `claudeutils _git diff` produce structured markdown output. Exit 0 always (status is informational).

**Error Conditions:**
- Not in a git repo → `_git()` raises CalledProcessError. Let it propagate (informational command).

**Validation:** `just precommit` — all tests pass.

---

**Phase 1 Checkpoint:** `just precommit` — all existing tests pass, new infrastructure tests pass.
