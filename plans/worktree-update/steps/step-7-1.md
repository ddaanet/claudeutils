# Cycle 7.1

**Plan**: `plans/worktree-update/runbook.md`
**Execution Model**: haiku
**Phase**: 7

---

## Cycle 7.1: Phase 1 pre-checks — OURS clean tree (session exempt)

**Objective:** Verify main repo and submodule are clean before merge, with session file exemption.

**Prerequisite:** Read justfile `wt-merge` recipe lines 200-250 — understand 4-phase ceremony structure and clean tree enforcement.

**RED Phase:**

**Test:** `test_merge_ours_clean_tree`
**Assertions:**
- Command: `claudeutils _worktree merge <slug>` (new command, doesn't exist yet)
- When main repo has uncommitted changes in source files: exit 1 with message "Clean tree required for merge (main)"
- When main repo has uncommitted changes in `agents/session.md`: merge proceeds (session exempt)
- When main repo has uncommitted changes in `agents/learnings.md`: merge proceeds (learnings exempt)
- When agent-core submodule has uncommitted changes: exit 1 with message "Clean tree required for merge (main submodule)"
- Both parent and submodule checked (not just parent)

**Expected failure:** NameError: command `merge` not defined, or no clean tree enforcement

**Why it fails:** Command doesn't exist yet

**Verify RED:** `pytest tests/test_worktree_cli.py::test_merge_ours_clean_tree -v`

---

**GREEN Phase:**

**Implementation:** Create `merge` command with OURS clean tree validation

**Behavior:**
- New Click command: `@click.command()` with slug argument
- Check main repo: run `git status --porcelain --untracked-files=no`
- Filter output: exclude lines matching `agents/session.md` and `agents/learnings.md`
- If filtered output non-empty: exit 1 with "Clean tree required for merge (main)"
- Check submodule: run `git -C agent-core status --porcelain --untracked-files=no`
- If output non-empty: exit 1 with "Clean tree required for merge (main submodule)"

**Approach:** New command function, subprocess status checks, filtered validation, early exit on dirty

**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Add new `merge` command function with Click decorators
  Location hint: After `rm` command definition
- File: `src/claudeutils/worktree/cli.py`
  Action: Implement OURS clean tree check with session exemption
  Location hint: Early in function, use subprocess and filtering
- File: `src/claudeutils/worktree/cli.py`
  Action: Implement submodule clean tree check (strict, no exemptions)
  Location hint: After main repo check

**Verify GREEN:** `pytest tests/test_worktree_cli.py::test_merge_ours_clean_tree -v`
- Must pass

**Verify no regression:** `pytest tests/test_worktree_rm.py -v`
- All Phase 6 tests still pass

---
